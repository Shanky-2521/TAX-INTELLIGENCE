"""
EITC Calculator Service
Implements IRS EITC calculation rules based on Publication 596
"""

import structlog
from typing import Dict, List, Optional
from datetime import datetime

logger = structlog.get_logger()


class EITCCalculator:
    """
    Calculator for Earned Income Tax Credit based on IRS rules
    """
    
    def __init__(self, tax_year: int = 2023):
        self.tax_year = tax_year
        self.eitc_tables = self._load_eitc_tables()
    
    def _load_eitc_tables(self) -> Dict:
        """
        Load EITC income limits and credit amounts for the tax year
        Based on IRS Publication 596 for 2023
        """
        if self.tax_year == 2023:
            return {
                'income_limits': {
                    'single': {
                        0: {'earned': 17640, 'agi': 17640},  # No qualifying children
                        1: {'earned': 46560, 'agi': 46560},  # 1 qualifying child
                        2: {'earned': 52918, 'agi': 52918},  # 2 qualifying children
                        3: {'earned': 56838, 'agi': 56838}   # 3+ qualifying children
                    },
                    'married_joint': {
                        0: {'earned': 23260, 'agi': 23260},
                        1: {'earned': 52180, 'agi': 52180},
                        2: {'earned': 58538, 'agi': 58538},
                        3: {'earned': 62458, 'agi': 62458}
                    }
                },
                'max_credits': {
                    0: 600,    # No qualifying children
                    1: 3995,   # 1 qualifying child
                    2: 6604,   # 2 qualifying children
                    3: 7430    # 3+ qualifying children
                },
                'phase_in_rates': {
                    0: 0.0765,  # 7.65%
                    1: 0.34,    # 34%
                    2: 0.40,    # 40%
                    3: 0.45     # 45%
                },
                'phase_out_rates': {
                    0: 0.0765,  # 7.65%
                    1: 0.1598,  # 15.98%
                    2: 0.2106,  # 21.06%
                    3: 0.2106   # 21.06%
                },
                'phase_out_start': {
                    'single': {
                        0: 9800,
                        1: 11750,
                        2: 11750,
                        3: 11750
                    },
                    'married_joint': {
                        0: 15420,
                        1: 17370,
                        2: 17370,
                        3: 17370
                    }
                },
                'investment_income_limit': 11000,
                'minimum_age_no_children': 25,
                'maximum_age_no_children': 64
            }
        else:
            # For other years, would need to implement or load different tables
            raise ValueError(f"EITC tables not available for tax year {self.tax_year}")
    
    def calculate(self, filing_status: str, adjusted_gross_income: float, 
                 earned_income: float, investment_income: float = 0,
                 qualifying_children: int = 0, children_ages: List[int] = None,
                 taxpayer_age: int = None, spouse_age: int = None) -> Dict:
        """
        Calculate EITC eligibility and credit amount
        
        Args:
            filing_status: 'single', 'married_joint', 'married_separate', 'head_of_household'
            adjusted_gross_income: AGI from tax return
            earned_income: Earned income (wages, self-employment, etc.)
            investment_income: Investment income amount
            qualifying_children: Number of qualifying children
            children_ages: List of children's ages (for validation)
            taxpayer_age: Age of primary taxpayer
            spouse_age: Age of spouse (if married filing jointly)
        
        Returns:
            Dictionary with eligibility status, credit amount, and explanation
        """
        try:
            logger.info("Starting EITC calculation",
                       filing_status=filing_status,
                       agi=adjusted_gross_income,
                       earned_income=earned_income,
                       children=qualifying_children)
            
            result = {
                'eligible': False,
                'credit_amount': 0,
                'explanation': [],
                'requirements_met': {},
                'tax_year': self.tax_year
            }
            
            # Normalize filing status
            filing_status_normalized = self._normalize_filing_status(filing_status)
            
            # Check basic eligibility requirements
            eligibility_checks = self._check_eligibility(
                filing_status_normalized, adjusted_gross_income, earned_income,
                investment_income, qualifying_children, taxpayer_age, spouse_age
            )
            
            result['requirements_met'] = eligibility_checks
            
            # If not eligible, return early
            if not all(eligibility_checks.values()):
                result['explanation'] = self._generate_ineligibility_explanation(eligibility_checks)
                return result
            
            # Calculate credit amount
            credit_amount = self._calculate_credit_amount(
                filing_status_normalized, adjusted_gross_income, earned_income, qualifying_children
            )
            
            result['eligible'] = True
            result['credit_amount'] = credit_amount
            result['explanation'] = self._generate_eligibility_explanation(
                credit_amount, qualifying_children, filing_status_normalized
            )
            
            logger.info("EITC calculation completed",
                       eligible=result['eligible'],
                       credit_amount=credit_amount)
            
            return result
            
        except Exception as e:
            logger.error("Error in EITC calculation", error=str(e))
            return {
                'eligible': False,
                'credit_amount': 0,
                'explanation': ['An error occurred during calculation. Please verify your inputs.'],
                'error': str(e)
            }
    
    def _normalize_filing_status(self, filing_status: str) -> str:
        """Normalize filing status to match our tables"""
        status_map = {
            'single': 'single',
            'married_joint': 'married_joint',
            'married_filing_jointly': 'married_joint',
            'married_separate': 'single',  # Use single limits for married filing separately
            'married_filing_separately': 'single',
            'head_of_household': 'single'  # Use single limits for head of household
        }
        return status_map.get(filing_status.lower(), 'single')
    
    def _check_eligibility(self, filing_status: str, agi: float, earned_income: float,
                          investment_income: float, qualifying_children: int,
                          taxpayer_age: int = None, spouse_age: int = None) -> Dict[str, bool]:
        """Check all EITC eligibility requirements"""
        
        checks = {}
        tables = self.eitc_tables
        
        # Investment income limit
        checks['investment_income_ok'] = investment_income <= tables['investment_income_limit']
        
        # Income limits
        children_key = min(qualifying_children, 3)  # Max 3 for table lookup
        income_limits = tables['income_limits'][filing_status][children_key]
        
        checks['agi_within_limits'] = agi <= income_limits['agi']
        checks['earned_income_within_limits'] = earned_income <= income_limits['earned']
        
        # Age requirements for taxpayers with no qualifying children
        if qualifying_children == 0:
            min_age = tables['minimum_age_no_children']
            max_age = tables['maximum_age_no_children']
            
            if filing_status == 'married_joint':
                # For married filing jointly, at least one spouse must meet age requirement
                taxpayer_age_ok = taxpayer_age and min_age <= taxpayer_age <= max_age
                spouse_age_ok = spouse_age and min_age <= spouse_age <= max_age
                checks['age_requirement_met'] = taxpayer_age_ok or spouse_age_ok
            else:
                checks['age_requirement_met'] = (taxpayer_age and 
                                               min_age <= taxpayer_age <= max_age)
        else:
            checks['age_requirement_met'] = True  # Not applicable with qualifying children
        
        # Must have earned income
        checks['has_earned_income'] = earned_income > 0
        
        return checks
    
    def _calculate_credit_amount(self, filing_status: str, agi: float, 
                               earned_income: float, qualifying_children: int) -> float:
        """Calculate the actual EITC amount"""
        
        tables = self.eitc_tables
        children_key = min(qualifying_children, 3)
        
        # Use the lesser of AGI or earned income for calculation
        income_for_calculation = min(agi, earned_income)
        
        # Get rates and limits
        phase_in_rate = tables['phase_in_rates'][children_key]
        phase_out_rate = tables['phase_out_rates'][children_key]
        max_credit = tables['max_credits'][children_key]
        phase_out_start = tables['phase_out_start'][filing_status][children_key]
        
        # Phase-in calculation
        phase_in_credit = income_for_calculation * phase_in_rate
        credit_amount = min(phase_in_credit, max_credit)
        
        # Phase-out calculation
        if income_for_calculation > phase_out_start:
            phase_out_amount = (income_for_calculation - phase_out_start) * phase_out_rate
            credit_amount = max(0, credit_amount - phase_out_amount)
        
        return round(credit_amount, 2)
    
    def _generate_eligibility_explanation(self, credit_amount: float, 
                                        qualifying_children: int, filing_status: str) -> List[str]:
        """Generate explanation for eligible taxpayers"""
        explanation = [
            f"You are eligible for the Earned Income Tax Credit!",
            f"Your estimated EITC amount is ${credit_amount:,.2f}",
            f"This calculation is based on {qualifying_children} qualifying child(ren)" if qualifying_children > 0 
            else "This calculation is for taxpayers with no qualifying children"
        ]
        
        explanation.append(
            "Please note: This is an estimate. Your actual credit may vary based on "
            "other factors not included in this calculation."
        )
        
        return explanation
    
    def _generate_ineligibility_explanation(self, checks: Dict[str, bool]) -> List[str]:
        """Generate explanation for ineligible taxpayers"""
        explanation = ["You do not appear to be eligible for the EITC based on the following:"]
        
        if not checks.get('investment_income_ok', True):
            explanation.append(f"• Investment income exceeds ${self.eitc_tables['investment_income_limit']:,}")
        
        if not checks.get('agi_within_limits', True):
            explanation.append("• Adjusted gross income exceeds EITC limits")
        
        if not checks.get('earned_income_within_limits', True):
            explanation.append("• Earned income exceeds EITC limits")
        
        if not checks.get('age_requirement_met', True):
            explanation.append("• Age requirements not met (must be 25-64 with no qualifying children)")
        
        if not checks.get('has_earned_income', True):
            explanation.append("• Must have earned income to qualify for EITC")
        
        explanation.append("Please consult IRS Publication 596 or a tax professional for more information.")
        
        return explanation
