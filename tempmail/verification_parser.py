"""
Advanced Verification Code Parser
Specialized for extracting verification codes from various email services
"""

import re
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class VerificationMatch:
    """Represents a found verification code with metadata"""
    code: str
    confidence: float  # 0.0 to 1.0
    pattern_type: str
    context: str  # Surrounding text
    position: int  # Position in text


class AdvancedVerificationParser:
    """Advanced parser for extracting verification codes from emails"""
    
    def __init__(self):
        # Define patterns with confidence scores
        self.patterns = [
            # High confidence patterns (exact matches)
            {
                'pattern': r'verification code[:\s]+([A-Z0-9]{4,8})',
                'confidence': 0.95,
                'type': 'verification_code_explicit',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'your code[:\s]+([A-Z0-9]{4,8})',
                'confidence': 0.95,
                'type': 'your_code_explicit',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'enter[:\s]+([A-Z0-9]{4,8})',
                'confidence': 0.90,
                'type': 'enter_code',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'confirm.*?code[:\s]+([A-Z0-9]{4,8})',
                'confidence': 0.90,
                'type': 'confirm_code',
                'flags': re.IGNORECASE
            },
            
            # Medium confidence patterns
            {
                'pattern': r'code[:\s]+([A-Z0-9]{4,8})',
                'confidence': 0.80,
                'type': 'code_generic',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'([0-9]{6})',  # 6-digit numbers (common for 2FA)
                'confidence': 0.75,
                'type': 'six_digit_number',
                'flags': 0
            },
            {
                'pattern': r'([A-Z0-9]{4}-[A-Z0-9]{4})',  # Format: ABCD-1234
                'confidence': 0.85,
                'type': 'hyphenated_code',
                'flags': 0
            },
            {
                'pattern': r'([A-Z]{2}[0-9]{4})',  # Format: AB1234
                'confidence': 0.70,
                'type': 'alpha_numeric_6',
                'flags': 0
            },
            
            # Lower confidence patterns (broader matches)
            {
                'pattern': r'([0-9]{4,8})',  # 4-8 digit numbers
                'confidence': 0.60,
                'type': 'numeric_code',
                'flags': 0
            },
            {
                'pattern': r'([A-Z0-9]{4,8})',  # 4-8 alphanumeric
                'confidence': 0.50,
                'type': 'alphanumeric_code',
                'flags': 0
            }
        ]
        
        # Service-specific patterns
        self.service_patterns = {
            'augmentcode': [
                r'augmentcode.*?verification.*?([A-Z0-9]{4,8})',
                r'augment.*?code[:\s]+([A-Z0-9]{4,8})',
                r'welcome.*?augment.*?([0-9]{6})'
            ],
            'github': [
                r'github.*?verification.*?([0-9]{6})',
                r'github.*?code[:\s]+([0-9]{6})'
            ],
            'google': [
                r'google.*?verification.*?([0-9]{6})',
                r'g-[0-9]{6}'
            ]
        }
        
        # Context keywords that increase confidence
        self.positive_keywords = [
            'verification', 'verify', 'confirm', 'authenticate', 'code',
            'login', 'signin', 'register', 'signup', 'account', 'security'
        ]
        
        # Context keywords that decrease confidence
        self.negative_keywords = [
            'invoice', 'receipt', 'order', 'tracking', 'phone', 'address',
            'zip', 'postal', 'reference', 'transaction'
        ]
    
    def extract_verification_codes(self, email_content: str, sender: str = "") -> List[VerificationMatch]:
        """
        Extract all potential verification codes from email content
        Returns list of matches sorted by confidence
        """
        matches = []
        email_lower = email_content.lower()
        
        # Try service-specific patterns first
        service_matches = self._extract_service_specific(email_content, sender)
        matches.extend(service_matches)
        
        # Try general patterns
        for pattern_info in self.patterns:
            pattern_matches = self._find_pattern_matches(
                email_content, 
                pattern_info['pattern'],
                pattern_info['confidence'],
                pattern_info['type'],
                pattern_info.get('flags', 0)
            )
            matches.extend(pattern_matches)
        
        # Remove duplicates and adjust confidence based on context
        unique_matches = self._deduplicate_and_score(matches, email_content)
        
        # Sort by confidence (highest first)
        unique_matches.sort(key=lambda x: x.confidence, reverse=True)
        
        return unique_matches
    
    def _extract_service_specific(self, content: str, sender: str) -> List[VerificationMatch]:
        """Extract codes using service-specific patterns"""
        matches = []
        sender_lower = sender.lower()
        
        # Determine service from sender
        service = None
        if 'augment' in sender_lower:
            service = 'augmentcode'
        elif 'github' in sender_lower:
            service = 'github'
        elif 'google' in sender_lower or 'gmail' in sender_lower:
            service = 'google'
        
        if service and service in self.service_patterns:
            for pattern in self.service_patterns[service]:
                pattern_matches = self._find_pattern_matches(
                    content, pattern, 0.95, f'{service}_specific', re.IGNORECASE
                )
                matches.extend(pattern_matches)
        
        return matches
    
    def _find_pattern_matches(self, content: str, pattern: str, base_confidence: float, 
                            pattern_type: str, flags: int = 0) -> List[VerificationMatch]:
        """Find all matches for a specific pattern"""
        matches = []
        
        try:
            for match in re.finditer(pattern, content, flags):
                code = match.group(1) if match.groups() else match.group(0)
                
                # Skip if code doesn't look valid
                if not self._is_valid_code(code):
                    continue
                
                # Get context around the match
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end]
                
                verification_match = VerificationMatch(
                    code=code,
                    confidence=base_confidence,
                    pattern_type=pattern_type,
                    context=context,
                    position=match.start()
                )
                
                matches.append(verification_match)
                
        except re.error:
            pass  # Skip invalid regex patterns
        
        return matches
    
    def _is_valid_code(self, code: str) -> bool:
        """Check if a code looks like a valid verification code"""
        # Basic validation rules
        if len(code) < 4 or len(code) > 8:
            return False
        
        # Skip codes that are all the same character
        if len(set(code)) == 1:
            return False
        
        # Skip codes that look like years, phone numbers, etc.
        if code.isdigit():
            num = int(code)
            if 1900 <= num <= 2100:  # Likely a year
                return False
            if len(code) == 10:  # Likely a phone number
                return False
        
        return True
    
    def _deduplicate_and_score(self, matches: List[VerificationMatch], 
                              email_content: str) -> List[VerificationMatch]:
        """Remove duplicates and adjust confidence based on context"""
        # Group by code
        code_groups = {}
        for match in matches:
            if match.code not in code_groups:
                code_groups[match.code] = []
            code_groups[match.code].append(match)
        
        unique_matches = []
        email_lower = email_content.lower()
        
        for code, group in code_groups.items():
            # Take the match with highest confidence
            best_match = max(group, key=lambda x: x.confidence)
            
            # Adjust confidence based on context
            context_lower = best_match.context.lower()
            
            # Boost confidence for positive keywords
            positive_boost = sum(0.05 for keyword in self.positive_keywords 
                               if keyword in context_lower)
            
            # Reduce confidence for negative keywords
            negative_penalty = sum(0.1 for keyword in self.negative_keywords 
                                 if keyword in context_lower)
            
            # Adjust confidence
            adjusted_confidence = min(1.0, best_match.confidence + positive_boost - negative_penalty)
            
            best_match.confidence = adjusted_confidence
            unique_matches.append(best_match)
        
        return unique_matches
    
    def get_best_verification_code(self, email_content: str, sender: str = "") -> Optional[str]:
        """
        Get the most likely verification code from email content
        Returns the code with highest confidence, or None if no good matches
        """
        matches = self.extract_verification_codes(email_content, sender)
        
        if not matches:
            return None
        
        # Return the highest confidence match if it's above threshold
        best_match = matches[0]
        if best_match.confidence >= 0.6:  # Minimum confidence threshold
            return best_match.code
        
        return None
    
    def analyze_email_for_codes(self, email_content: str, sender: str = "") -> Dict:
        """
        Comprehensive analysis of email for verification codes
        Returns detailed analysis including all potential codes
        """
        matches = self.extract_verification_codes(email_content, sender)
        
        analysis = {
            'has_verification_code': len(matches) > 0,
            'best_code': matches[0].code if matches else None,
            'best_confidence': matches[0].confidence if matches else 0.0,
            'all_matches': [
                {
                    'code': match.code,
                    'confidence': match.confidence,
                    'type': match.pattern_type,
                    'context': match.context[:100] + '...' if len(match.context) > 100 else match.context
                }
                for match in matches
            ],
            'total_matches': len(matches),
            'high_confidence_matches': len([m for m in matches if m.confidence >= 0.8])
        }
        
        return analysis
