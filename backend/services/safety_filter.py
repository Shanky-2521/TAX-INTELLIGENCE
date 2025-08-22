"""
Safety Filter Service for Tax Intelligence
Implements content moderation and PII detection
"""

import re
import structlog
from typing import List, Dict, Tuple, Optional
import hashlib

logger = structlog.get_logger()


class SafetyFilter:
    """
    Service for filtering unsafe content and detecting PII in user inputs and AI responses
    """
    
    def __init__(self):
        self.pii_patterns = self._load_pii_patterns()
        self.unsafe_patterns = self._load_unsafe_patterns()
        self.tax_related_keywords = self._load_tax_keywords()
    
    def _load_pii_patterns(self) -> Dict[str, re.Pattern]:
        """Load regex patterns for detecting PII"""
        return {
            'ssn': re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
            'ssn_full': re.compile(r'\b\d{9}\b'),
            'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            'bank_account': re.compile(r'\b\d{8,17}\b'),
            'address_pattern': re.compile(r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b', re.IGNORECASE),
            'zip_code': re.compile(r'\b\d{5}(?:-\d{4})?\b'),
            'date_of_birth': re.compile(r'\b(?:0[1-9]|1[0-2])[/-](?:0[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b'),
            'ein': re.compile(r'\b\d{2}-?\d{7}\b')  # Employer Identification Number
        }
    
    def _load_unsafe_patterns(self) -> Dict[str, re.Pattern]:
        """Load patterns for detecting unsafe content"""
        return {
            'tax_evasion': re.compile(r'\b(?:hide|conceal|evade|avoid paying|not report|under report|cash only|off the books)\s+(?:income|taxes|earnings)\b', re.IGNORECASE),
            'illegal_advice': re.compile(r'\b(?:illegal|fraudulent|fake|false)\s+(?:deduction|credit|return|claim)\b', re.IGNORECASE),
            'aggressive_language': re.compile(r'\b(?:damn|hell|stupid|idiot|moron|scam|rip-?off)\b', re.IGNORECASE),
            'non_tax_requests': re.compile(r'\b(?:medical|legal|investment|relationship|personal)\s+advice\b', re.IGNORECASE),
            'specific_advice': re.compile(r'\b(?:should I|tell me exactly|what should|give me specific)\b', re.IGNORECASE)
        }
    
    def _load_tax_keywords(self) -> List[str]:
        """Load tax-related keywords to validate topic relevance"""
        return [
            'eitc', 'earned income tax credit', 'tax credit', 'refund', 'irs', 'taxes',
            'income', 'filing', 'deduction', 'w-2', '1040', 'adjusted gross income',
            'qualifying child', 'dependent', 'tax return', 'withholding', 'standard deduction',
            'itemized deduction', 'tax liability', 'tax year', 'publication 596'
        ]
    
    def is_safe_input(self, text: str) -> bool:
        """
        Check if user input is safe and appropriate
        
        Args:
            text: User input text to check
            
        Returns:
            True if input is safe, False otherwise
        """
        try:
            # Check for PII
            pii_detected = self.detect_pii(text)
            if pii_detected['has_pii']:
                logger.warning("PII detected in user input", 
                              pii_types=list(pii_detected['pii_types'].keys()))
                return False
            
            # Check for unsafe content
            unsafe_content = self.detect_unsafe_content(text)
            if unsafe_content['is_unsafe']:
                logger.warning("Unsafe content detected in user input",
                              unsafe_types=list(unsafe_content['unsafe_types'].keys()))
                return False
            
            # Check if content is tax-related
            if not self.is_tax_related(text):
                logger.info("Non-tax related query detected")
                # Allow non-tax queries but flag them
                return True
            
            return True
            
        except Exception as e:
            logger.error("Error in safety filter", error=str(e))
            # Err on the side of caution
            return False
    
    def is_safe_output(self, text: str) -> bool:
        """
        Check if AI-generated output is safe and appropriate
        
        Args:
            text: AI response text to check
            
        Returns:
            True if output is safe, False otherwise
        """
        try:
            # Check for PII in response
            pii_detected = self.detect_pii(text)
            if pii_detected['has_pii']:
                logger.warning("PII detected in AI response",
                              pii_types=list(pii_detected['pii_types'].keys()))
                return False
            
            # Check for inappropriate advice
            if self._contains_specific_tax_advice(text):
                logger.warning("Specific tax advice detected in AI response")
                return False
            
            # Check for disclaimers
            if not self._has_appropriate_disclaimers(text):
                logger.info("AI response missing appropriate disclaimers")
                # Don't block, but log for review
            
            return True
            
        except Exception as e:
            logger.error("Error in output safety filter", error=str(e))
            return False
    
    def detect_pii(self, text: str) -> Dict:
        """
        Detect personally identifiable information in text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with PII detection results
        """
        pii_found = {}
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(text)
            if matches:
                # Hash the matches for logging without exposing actual PII
                hashed_matches = [hashlib.sha256(match.encode()).hexdigest()[:8] for match in matches]
                pii_found[pii_type] = {
                    'count': len(matches),
                    'hashed_values': hashed_matches
                }
        
        return {
            'has_pii': bool(pii_found),
            'pii_types': pii_found,
            'total_pii_items': sum(item['count'] for item in pii_found.values())
        }
    
    def detect_unsafe_content(self, text: str) -> Dict:
        """
        Detect unsafe or inappropriate content
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with unsafe content detection results
        """
        unsafe_found = {}
        
        for unsafe_type, pattern in self.unsafe_patterns.items():
            matches = pattern.findall(text)
            if matches:
                unsafe_found[unsafe_type] = {
                    'count': len(matches),
                    'matches': matches[:3]  # Limit to first 3 matches for logging
                }
        
        return {
            'is_unsafe': bool(unsafe_found),
            'unsafe_types': unsafe_found,
            'total_unsafe_items': sum(item['count'] for item in unsafe_found.values())
        }
    
    def is_tax_related(self, text: str) -> bool:
        """
        Check if text is related to tax topics
        
        Args:
            text: Text to analyze
            
        Returns:
            True if text appears to be tax-related
        """
        text_lower = text.lower()
        
        # Check for tax keywords
        tax_keyword_count = sum(1 for keyword in self.tax_related_keywords 
                               if keyword in text_lower)
        
        # Consider it tax-related if it has at least one tax keyword
        # or if it's a general greeting/question
        general_patterns = ['hello', 'hi', 'help', 'question', 'how', 'what', 'can you']
        is_general = any(pattern in text_lower for pattern in general_patterns)
        
        return tax_keyword_count > 0 or is_general
    
    def _contains_specific_tax_advice(self, text: str) -> bool:
        """Check if response contains specific tax advice that should be avoided"""
        specific_advice_patterns = [
            r'\byou should claim\b',
            r'\byou should deduct\b',
            r'\byou should file\b',
            r'\byou are eligible for exactly\b',
            r'\byour tax liability is\b',
            r'\byou owe \$\d+\b',
            r'\byou will receive \$\d+\b'
        ]
        
        text_lower = text.lower()
        for pattern in specific_advice_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _has_appropriate_disclaimers(self, text: str) -> bool:
        """Check if response has appropriate disclaimers"""
        disclaimer_patterns = [
            r'consult.*tax professional',
            r'this is.*estimate',
            r'general.*information',
            r'not.*substitute.*professional advice',
            r'irs publication',
            r'verify.*current.*information'
        ]
        
        text_lower = text.lower()
        disclaimer_count = sum(1 for pattern in disclaimer_patterns 
                             if re.search(pattern, text_lower))
        
        # Should have at least one disclaimer for longer responses
        return disclaimer_count > 0 or len(text.split()) < 50
    
    def sanitize_text(self, text: str) -> str:
        """
        Remove or mask PII from text
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text with PII removed/masked
        """
        sanitized = text
        
        # Replace PII with masked versions
        sanitized = self.pii_patterns['ssn'].sub('XXX-XX-XXXX', sanitized)
        sanitized = self.pii_patterns['phone'].sub('XXX-XXX-XXXX', sanitized)
        sanitized = self.pii_patterns['email'].sub('[EMAIL]', sanitized)
        sanitized = self.pii_patterns['credit_card'].sub('XXXX-XXXX-XXXX-XXXX', sanitized)
        sanitized = self.pii_patterns['bank_account'].sub('[ACCOUNT_NUMBER]', sanitized)
        sanitized = self.pii_patterns['address_pattern'].sub('[ADDRESS]', sanitized)
        sanitized = self.pii_patterns['zip_code'].sub('XXXXX', sanitized)
        sanitized = self.pii_patterns['date_of_birth'].sub('XX/XX/XXXX', sanitized)
        sanitized = self.pii_patterns['ein'].sub('XX-XXXXXXX', sanitized)
        
        return sanitized
    
    def get_safety_report(self, text: str) -> Dict:
        """
        Generate comprehensive safety report for text
        
        Args:
            text: Text to analyze
            
        Returns:
            Comprehensive safety analysis report
        """
        return {
            'text_length': len(text),
            'word_count': len(text.split()),
            'pii_analysis': self.detect_pii(text),
            'unsafe_content_analysis': self.detect_unsafe_content(text),
            'is_tax_related': self.is_tax_related(text),
            'is_safe_input': self.is_safe_input(text),
            'sanitized_text': self.sanitize_text(text),
            'timestamp': structlog.get_logger().info("Safety report generated")
        }
