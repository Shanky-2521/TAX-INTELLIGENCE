"""
Unit tests for EITC Calculator Service
"""

import pytest
from backend.services.eitc_calculator import EITCCalculator


class TestEITCCalculator:
    """Test cases for EITC Calculator"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.calculator = EITCCalculator(tax_year=2023)
    
    def test_calculator_initialization(self):
        """Test calculator initializes correctly"""
        assert self.calculator.tax_year == 2023
        assert self.calculator.eitc_tables is not None
        assert 'income_limits' in self.calculator.eitc_tables
        assert 'max_credits' in self.calculator.eitc_tables
    
    def test_single_no_children_eligible(self):
        """Test single filer with no children - eligible case"""
        result = self.calculator.calculate(
            filing_status='single',
            adjusted_gross_income=15000,
            earned_income=15000,
            investment_income=0,
            qualifying_children=0,
            taxpayer_age=30
        )
        
        assert result['eligible'] is True
        assert result['credit_amount'] > 0
        assert result['tax_year'] == 2023
    
    def test_single_no_children_too_young(self):
        """Test single filer with no children - too young"""
        result = self.calculator.calculate(
            filing_status='single',
            adjusted_gross_income=15000,
            earned_income=15000,
            investment_income=0,
            qualifying_children=0,
            taxpayer_age=20
        )
        
        assert result['eligible'] is False
        assert 'age requirements' in ' '.join(result['explanation']).lower()
    
    def test_single_with_children_eligible(self):
        """Test single filer with qualifying children"""
        result = self.calculator.calculate(
            filing_status='single',
            adjusted_gross_income=25000,
            earned_income=25000,
            investment_income=0,
            qualifying_children=2
        )
        
        assert result['eligible'] is True
        assert result['credit_amount'] > 0
    
    def test_income_too_high(self):
        """Test case where income exceeds EITC limits"""
        result = self.calculator.calculate(
            filing_status='single',
            adjusted_gross_income=60000,
            earned_income=60000,
            investment_income=0,
            qualifying_children=1
        )
        
        assert result['eligible'] is False
        assert 'income exceeds' in ' '.join(result['explanation']).lower()
    
    def test_investment_income_too_high(self):
        """Test case where investment income exceeds limit"""
        result = self.calculator.calculate(
            filing_status='single',
            adjusted_gross_income=25000,
            earned_income=25000,
            investment_income=15000,
            qualifying_children=1
        )
        
        assert result['eligible'] is False
        assert 'investment income' in ' '.join(result['explanation']).lower()
    
    def test_married_filing_jointly(self):
        """Test married filing jointly calculation"""
        result = self.calculator.calculate(
            filing_status='married_joint',
            adjusted_gross_income=35000,
            earned_income=35000,
            investment_income=0,
            qualifying_children=1
        )
        
        assert result['eligible'] is True
        assert result['credit_amount'] > 0
    
    def test_get_income_limits(self):
        """Test income limits retrieval"""
        limits = self.calculator.get_income_limits('single', 1)
        
        assert 'earned_income_limit' in limits
        assert 'agi_limit' in limits
        assert 'max_credit_amount' in limits
        assert limits['earned_income_limit'] > 0
    
    def test_estimate_credit_by_income(self):
        """Test credit estimation for multiple income levels"""
        income_levels = [10000, 20000, 30000, 40000]
        results = self.calculator.estimate_credit_by_income('single', 1, income_levels)
        
        assert len(results) == len(income_levels)
        for result in results:
            assert 'income' in result
            assert 'credit_amount' in result
            assert 'eligible' in result
    
    def test_filing_status_normalization(self):
        """Test filing status normalization"""
        # Test various filing status inputs
        assert self.calculator._normalize_filing_status('single') == 'single'
        assert self.calculator._normalize_filing_status('married_filing_jointly') == 'married_joint'
        assert self.calculator._normalize_filing_status('head_of_household') == 'single'
        assert self.calculator._normalize_filing_status('married_separate') == 'single'
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test with negative income
        result = self.calculator.calculate(
            filing_status='single',
            adjusted_gross_income=-1000,
            earned_income=15000,
            investment_income=0,
            qualifying_children=0,
            taxpayer_age=30
        )
        
        # Should handle gracefully
        assert 'error' in result or result['eligible'] is False


if __name__ == '__main__':
    pytest.main([__file__])
