"""
REAL Temporary Email Service Implementation
Uses actual temporary email providers to generate real, functional email addresses
"""

import time
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Import the temp-mails library for real email services
try:
    from temp_mails import (
        Mail_tm, Tempmail_lol, Tenminemail_com, Dropmail_me,
        Yopmail_com, Mailinator_com, Emailondeck_com
    )
    TEMP_MAILS_AVAILABLE = True
except ImportError:
    TEMP_MAILS_AVAILABLE = False
    print("⚠️ temp-mails library not available. Install with: pip install temp-mails")


@dataclass
class RealEmailMessage:
    """Represents a real email message from temporary email services"""
    sender: str
    subject: str
    content: str
    timestamp: datetime
    message_id: str
    verification_code: Optional[str] = None


@dataclass
class RealEmailSession:
    """Represents a real temporary email session"""
    email_address: str
    service_name: str
    service_instance: Any
    created_at: datetime
    expires_at: datetime
    messages: List[RealEmailMessage]
    is_active: bool = True


class RealTempEmailService:
    """Real temporary email service using actual providers"""
    
    def __init__(self):
        self.current_session: Optional[RealEmailSession] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        self.callbacks = {
            'on_email_received': [],
            'on_verification_code': [],
            'on_error': [],
            'on_status_change': []
        }
        
        # Available services with their typical domains (in order of preference)
        self.available_services = [
            {
                'name': 'Mail.tm',
                'class': Mail_tm,
                'typical_domains': ['punkproof.com'],
                'reliability': 'high',
                'description': 'Reliable service with consistent domains'
            },
            {
                'name': 'TempMail.lol',
                'class': Tempmail_lol,
                'typical_domains': ['jailbreakeverything.com'],
                'reliability': 'high',
                'description': 'Fast service with unique domains'
            },
            {
                'name': '10MinuteMail',
                'class': Tenminemail_com,
                'typical_domains': ['hosliy.com'],
                'reliability': 'medium',
                'description': '10-minute expiry service'
            },
            {
                'name': 'DropMail',
                'class': Dropmail_me,
                'typical_domains': ['dropmail.me'],
                'reliability': 'medium',
                'description': 'Simple temporary email service'
            },
            {
                'name': 'YopMail',
                'class': Yopmail_com,
                'typical_domains': ['cobal.infos.st'],
                'reliability': 'medium',
                'description': 'European temporary email service'
            },
            {
                'name': 'Mailinator',
                'class': Mailinator_com,
                'typical_domains': ['mailinator.com'],
                'reliability': 'high',
                'description': 'Well-known temporary email service'
            },
            {
                'name': 'EmailOnDeck',
                'class': Emailondeck_com,
                'typical_domains': ['blouseness.com'],
                'reliability': 'medium',
                'description': 'Alternative temporary email provider'
            }
        ]
        
        self.logger = logging.getLogger(__name__)
    
    def add_callback(self, event_type: str, callback):
        """Add callback for events"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    def _trigger_callback(self, event_type: str, *args, **kwargs):
        """Trigger callbacks for an event"""
        for callback in self.callbacks.get(event_type, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")
    
    def generate_real_email(self, preferred_domain: str = None) -> Tuple[bool, str, Optional[RealEmailSession]]:
        """
        Generate a REAL temporary email address using actual services
        Args:
            preferred_domain: Optional preferred domain (e.g., 'mailinator.com')
        Returns: (success, message, session)
        """
        if not TEMP_MAILS_AVAILABLE:
            return False, "temp-mails library not installed. Run: pip install temp-mails", None

        self._trigger_callback('on_status_change', 'Generating real temporary email...')

        # Sort services by preference (preferred domain first, then by reliability)
        sorted_services = self._sort_services_by_preference(preferred_domain)

        # Try each service until one works
        for service_info in sorted_services:
            service_name = service_info['name']
            service_class = service_info['class']
            typical_domains = service_info['typical_domains']

            try:
                self._trigger_callback('on_status_change', f'Trying {service_name} (domains: {", ".join(typical_domains)})...')

                # Create service instance
                service_instance = service_class()

                # Get the real email address
                email_address = service_instance.email

                if email_address and '@' in email_address:
                    domain = email_address.split('@')[1]

                    # Create enhanced session with domain info
                    now = datetime.now()
                    expires_at = now + timedelta(hours=1)  # Most services expire in 1 hour

                    self.current_session = RealEmailSession(
                        email_address=email_address,
                        service_name=service_name,
                        service_instance=service_instance,
                        created_at=now,
                        expires_at=expires_at,
                        messages=[],
                        is_active=True
                    )

                    # Add domain and service info to session
                    self.current_session.domain = domain
                    self.current_session.service_info = service_info

                    success_msg = f"✅ Generated REAL email: {email_address} (via {service_name}, domain: {domain})"
                    self._trigger_callback('on_status_change', success_msg)
                    return True, success_msg, self.current_session

            except Exception as e:
                self.logger.warning(f"Failed to use {service_name}: {str(e)}")
                self._trigger_callback('on_status_change', f'❌ {service_name} failed: {str(e)}')
                continue

        # If all services failed
        error_msg = "❌ All temporary email services failed. Please try again later."
        self._trigger_callback('on_error', error_msg)
        return False, error_msg, None

    def _sort_services_by_preference(self, preferred_domain: str = None) -> List[Dict]:
        """Sort services by preference (preferred domain first, then reliability)"""
        services = self.available_services.copy()

        if preferred_domain:
            # Move services with preferred domain to front
            preferred_services = []
            other_services = []

            for service in services:
                if preferred_domain in service['typical_domains']:
                    preferred_services.append(service)
                else:
                    other_services.append(service)

            # Sort by reliability within each group
            preferred_services.sort(key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x['reliability'], 2))
            other_services.sort(key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x['reliability'], 2))

            return preferred_services + other_services
        else:
            # Sort by reliability only
            services.sort(key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x['reliability'], 2))
            return services
    
    def start_real_monitoring(self, poll_interval: int = 10) -> bool:
        """
        Start monitoring the REAL temporary email inbox
        Args:
            poll_interval: Seconds between checks (default 10 for real emails)
        Returns: Success status
        """
        if not self.current_session:
            return False
        
        if self.monitoring_active:
            return True
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitor_real_inbox,
            args=(poll_interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        self._trigger_callback('on_status_change', f'🟢 Started REAL email monitoring ({self.current_session.service_name})')
        return True
    
    def stop_real_monitoring(self):
        """Stop monitoring the real email inbox"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        self._trigger_callback('on_status_change', '🔴 Stopped real email monitoring')
    
    def _monitor_real_inbox(self, poll_interval: int):
        """Monitor real inbox for new emails (runs in separate thread)"""
        while self.monitoring_active and self.current_session and self.current_session.is_active:
            try:
                # Check if session expired
                if datetime.now() > self.current_session.expires_at:
                    self.current_session.is_active = False
                    self._trigger_callback('on_status_change', '⏰ Email session expired')
                    break
                
                # Check for new real emails
                new_messages = self._fetch_real_messages()
                
                for message in new_messages:
                    # Avoid duplicates
                    if not any(m.message_id == message.message_id for m in self.current_session.messages):
                        self.current_session.messages.append(message)
                        self._trigger_callback('on_email_received', message)
                        
                        # Check for verification codes
                        if message.verification_code:
                            self._trigger_callback('on_verification_code', message.verification_code, message)
                
                time.sleep(poll_interval)
                
            except Exception as e:
                self._trigger_callback('on_error', f"Real monitoring error: {str(e)}")
                time.sleep(poll_interval * 2)  # Wait longer on error
    
    def _fetch_real_messages(self) -> List[RealEmailMessage]:
        """Fetch new messages from the REAL inbox"""
        if not self.current_session or not self.current_session.service_instance:
            return []
        
        try:
            service = self.current_session.service_instance
            
            # Get inbox from the real service
            inbox = service.get_inbox()
            
            if not inbox:
                return []
            
            messages = []
            for email_data in inbox:
                try:
                    # Extract email information (format varies by service)
                    message_id = str(email_data.get('id', email_data.get('mail_id', len(messages))))
                    sender = email_data.get('from', email_data.get('sender', 'Unknown'))
                    subject = email_data.get('subject', 'No Subject')
                    
                    # Get email content
                    content = ""
                    try:
                        if hasattr(service, 'get_mail_content'):
                            # Use correct parameter name: mail_id (not message_id)
                            content_data = service.get_mail_content(mail_id=message_id)
                            if isinstance(content_data, dict):
                                content = content_data.get('content', content_data.get('body', str(content_data)))
                            else:
                                content = str(content_data)
                        else:
                            content = email_data.get('content', email_data.get('body', str(email_data)))

                        # Convert HTML to plain text if needed
                        content = self._html_to_text(content)

                    except Exception as e:
                        # If content extraction fails, try to get it from email_data directly
                        content = email_data.get('content', email_data.get('body', email_data.get('text', str(email_data))))
                        if content:
                            content = self._html_to_text(content)
                        if not content or len(content) < 10:
                            content = f"Content extraction failed: {str(e)}"
                    
                    # Extract verification code
                    verification_code = self._extract_verification_code(content)
                    
                    # Create message
                    message = RealEmailMessage(
                        sender=sender,
                        subject=subject,
                        content=content,
                        timestamp=datetime.now(),
                        message_id=message_id,
                        verification_code=verification_code
                    )
                    
                    messages.append(message)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing email: {str(e)}")
                    continue
            
            return messages
            
        except Exception as e:
            self._trigger_callback('on_error', f"Error fetching real messages: {str(e)}")
            return []
    
    def check_real_inbox_manually(self) -> Tuple[bool, str, List[RealEmailMessage]]:
        """Manually check REAL inbox for new messages"""
        if not self.current_session:
            return False, "No active email session", []
        
        try:
            self._trigger_callback('on_status_change', 'Checking real inbox...')
            new_messages = self._fetch_real_messages()
            
            # Add new messages to session
            for message in new_messages:
                if not any(m.message_id == message.message_id for m in self.current_session.messages):
                    self.current_session.messages.append(message)
                    self._trigger_callback('on_email_received', message)
                    
                    if message.verification_code:
                        self._trigger_callback('on_verification_code', message.verification_code, message)
            
            count = len([m for m in new_messages if not any(existing.message_id == m.message_id for existing in self.current_session.messages[:-len(new_messages)])])
            status_msg = f"📬 Found {count} new real message{'s' if count != 1 else ''}"
            self._trigger_callback('on_status_change', status_msg)
            
            return True, status_msg, new_messages
            
        except Exception as e:
            error_msg = f"Error checking real inbox: {str(e)}"
            self._trigger_callback('on_error', error_msg)
            return False, error_msg, []
    
    def _extract_verification_code(self, email_content: str) -> Optional[str]:
        """Extract verification code from real email content with enhanced patterns"""
        import re

        if not email_content:
            return None

        # Clean the content for better matching
        content = email_content.strip()

        # Priority patterns - most specific first
        priority_patterns = [
            # HTML patterns (for emails with HTML formatting) - more flexible
            r'your verification code is[:\s]*<[^>]*>([A-Z0-9]{4,8})<',  # "Your verification code is: <b>066533</b>"
            r'verification code is[:\s]*<[^>]*>([A-Z0-9]{4,8})<',       # "verification code is: <b>066533</b>"
            r'code is[:\s]*<[^>]*>([A-Z0-9]{4,8})<',                   # "code is: <b>066533</b>"

            # Nested HTML patterns (for complex HTML structures)
            r'code[:\s]*<[^>]*><[^>]*>([A-Z0-9]{4,8})<',               # "Code: <span><b>XY123Z</b></span>"
            r'verification[:\s]*<[^>]*><[^>]*>([A-Z0-9]{4,8})<',       # Nested verification patterns

            # Exact "Your verification code is:" patterns (highest priority)
            r'your verification code is[:\s]+([A-Z0-9]{4,8})',
            r'verification code is[:\s]+([A-Z0-9]{4,8})',
            r'your code is[:\s]+([A-Z0-9]{4,8})',

            # Common verification patterns
            r'verification code[:\s]+([A-Z0-9]{4,8})',
            r'your verification code[:\s]+([A-Z0-9]{4,8})',
            r'your code[:\s]+([A-Z0-9]{4,8})',
            r'enter code[:\s]+([A-Z0-9]{4,8})',
            r'use code[:\s]+([A-Z0-9]{4,8})',
            r'confirm.*?code[:\s]+([A-Z0-9]{4,8})',

            # Service-specific patterns
            r'augmentcode.*?code[:\s]+([A-Z0-9]{4,8})',
            r'github.*?code[:\s]+([A-Z0-9]{4,8})',

            # Generic code patterns (lower priority to avoid false positives)
            r'([A-Z0-9]{4}-[A-Z0-9]{4})',  # Hyphenated codes
        ]

        # Fallback patterns for standalone numbers
        fallback_patterns = [
            r'([0-9]{6})',      # 6-digit numbers (most common)
            r'([0-9]{4,8})',    # 4-8 digit numbers
            r'([A-Z0-9]{4,8})', # 4-8 alphanumeric
        ]

        # If content is HTML, also try extracting from plain text version
        plain_text_content = None
        if '<' in content and '>' in content:  # Likely HTML
            plain_text_content = self._html_to_text(content)

        # Try priority patterns on both HTML and plain text
        for pattern in priority_patterns:
            # Try on original content first
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                for match in matches:
                    if self._is_valid_verification_code(match):
                        return match.upper()

            # If HTML, also try on plain text version
            if plain_text_content:
                matches = re.findall(pattern, plain_text_content, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if self._is_valid_verification_code(match):
                            return match.upper()

        # If no priority patterns match, try fallback patterns
        # But only if the content seems to be about verification
        verification_keywords = ['verification', 'verify', 'code', 'confirm', 'authenticate']
        content_lower = content.lower()
        plain_text_lower = plain_text_content.lower() if plain_text_content else ""

        if any(keyword in content_lower or keyword in plain_text_lower for keyword in verification_keywords):
            for pattern in fallback_patterns:
                # Try on plain text first (more reliable for fallback patterns)
                if plain_text_content:
                    matches = re.findall(pattern, plain_text_content, re.IGNORECASE)
                    if matches:
                        for match in matches:
                            if self._is_valid_verification_code(match):
                                return match.upper()

                # Then try on original content
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if self._is_valid_verification_code(match):
                            return match.upper()

        return None

    def _is_valid_verification_code(self, code: str) -> bool:
        """Validate if a string looks like a verification code"""
        if not code or len(code) < 4 or len(code) > 8:
            return False

        # Skip obvious non-codes
        if code.isdigit():
            num = int(code)
            # Skip years, common numbers, etc.
            if 1900 <= num <= 2100:  # Years
                return False
            if num in [1234, 0000, 9999, 1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888]:  # Common patterns
                return False

        # Skip codes that are all the same character
        if len(set(code)) == 1:
            return False

        # Skip codes that look like phone numbers or IDs
        if len(code) == 10 and code.isdigit():
            return False

        return True

    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text"""
        if not html_content:
            return ""

        # Check if content is HTML
        if not ('<html' in html_content.lower() or '<div' in html_content.lower() or '<p' in html_content.lower()):
            return html_content  # Already plain text

        try:
            # Try using BeautifulSoup if available
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                # Extract text and clean it up
                text = soup.get_text()
                # Clean up whitespace
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                return '\n'.join(lines)
            except ImportError:
                # Fallback: simple HTML tag removal
                import re
                # Remove HTML tags
                text = re.sub(r'<[^>]+>', '', html_content)
                # Decode HTML entities
                text = text.replace('&nbsp;', ' ')
                text = text.replace('&amp;', '&')
                text = text.replace('&lt;', '<')
                text = text.replace('&gt;', '>')
                text = text.replace('&quot;', '"')
                # Clean up whitespace
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                return '\n'.join(lines)
        except Exception:
            # If all else fails, return original content
            return html_content
    
    def get_real_session_info(self) -> Optional[Dict]:
        """Get current real session information"""
        if not self.current_session:
            return None
        
        return {
            'email_address': self.current_session.email_address,
            'service_name': self.current_session.service_name,
            'created_at': self.current_session.created_at.isoformat(),
            'expires_at': self.current_session.expires_at.isoformat(),
            'is_active': self.current_session.is_active,
            'message_count': len(self.current_session.messages),
            'time_remaining': str(self.current_session.expires_at - datetime.now()) if self.current_session.is_active else "Expired",
            'is_real': True
        }
    
    def cleanup_real_session(self):
        """Clean up the current real session"""
        self.stop_real_monitoring()
        if self.current_session:
            self.current_session.is_active = False
        self.current_session = None
        self._trigger_callback('on_status_change', 'Real session cleaned up')

    def get_available_domains(self) -> List[str]:
        """Get list of all available email domains"""
        domains = []
        for service in self.available_services:
            domains.extend(service['typical_domains'])
        return list(set(domains))  # Remove duplicates

    def get_available_services(self) -> List[Dict]:
        """Get list of all available services with their information"""
        return [
            {
                'name': service['name'],
                'domains': service['typical_domains'],
                'reliability': service['reliability'],
                'description': service['description']
            }
            for service in self.available_services
        ]

    def generate_email_with_domain(self, preferred_domain: str) -> Tuple[bool, str, Optional[RealEmailSession]]:
        """Generate email with specific domain preference"""
        return self.generate_real_email(preferred_domain=preferred_domain)

    def get_service_stats(self) -> Dict:
        """Get statistics about available services"""
        total_services = len(self.available_services)
        total_domains = len(self.get_available_domains())
        high_reliability = len([s for s in self.available_services if s['reliability'] == 'high'])

        return {
            'total_services': total_services,
            'total_domains': total_domains,
            'high_reliability_services': high_reliability,
            'available_domains': self.get_available_domains(),
            'services': self.get_available_services()
        }
    
    def wait_for_verification_email(self, timeout: int = 120) -> Optional[RealEmailMessage]:
        """
        Wait for a verification email to arrive (blocking)
        Args:
            timeout: Maximum seconds to wait
        Returns: The verification email message or None
        """
        if not self.current_session:
            return None
        
        service = self.current_session.service_instance
        
        try:
            # Use the service's built-in wait function if available
            if hasattr(service, 'wait_for_new_email'):
                self._trigger_callback('on_status_change', f'⏳ Waiting for verification email (up to {timeout}s)...')
                
                email_data = service.wait_for_new_email(timeout=timeout)
                
                if email_data:
                    # Process the received email
                    message_id = str(email_data.get('id', email_data.get('mail_id', 'new')))
                    sender = email_data.get('from', email_data.get('sender', 'Unknown'))
                    subject = email_data.get('subject', 'No Subject')
                    
                    # Get content
                    content = ""
                    try:
                        if hasattr(service, 'get_mail_content'):
                            # Use correct parameter name: mail_id (not message_id)
                            content_data = service.get_mail_content(mail_id=message_id)
                            content = str(content_data)
                        else:
                            content = str(email_data)

                        # Convert HTML to plain text if needed
                        content = self._html_to_text(content)

                    except Exception as e:
                        content = email_data.get('content', email_data.get('body', str(email_data)))
                        if content:
                            content = self._html_to_text(content)
                    
                    # Extract verification code
                    verification_code = self._extract_verification_code(content)
                    
                    message = RealEmailMessage(
                        sender=sender,
                        subject=subject,
                        content=content,
                        timestamp=datetime.now(),
                        message_id=message_id,
                        verification_code=verification_code
                    )
                    
                    # Add to session
                    self.current_session.messages.append(message)
                    
                    # Trigger callbacks
                    self._trigger_callback('on_email_received', message)
                    if verification_code:
                        self._trigger_callback('on_verification_code', verification_code, message)
                    
                    return message
                
            return None
            
        except Exception as e:
            self._trigger_callback('on_error', f"Error waiting for email: {str(e)}")
            return None
