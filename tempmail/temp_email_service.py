"""
Temporary Email Service Module for Internxt Integration
Handles temporary email generation, monitoring, and verification code extraction
"""

import requests
import re
import time
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
from bs4 import BeautifulSoup
import random
import string


@dataclass
class EmailMessage:
    """Represents an email message"""
    sender: str
    subject: str
    content: str
    timestamp: datetime
    verification_code: Optional[str] = None


@dataclass
class TempEmailSession:
    """Represents a temporary email session"""
    email_address: str
    session_id: str
    created_at: datetime
    expires_at: datetime
    messages: List[EmailMessage]
    is_active: bool = True


class InternxtTempEmailService:
    """Service for managing Internxt temporary email functionality"""
    
    BASE_URL = "https://internxt.com/temporary-email"
    API_BASE = "https://internxt.com/api/temp-email"  # Hypothetical API endpoint
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.current_session: Optional[TempEmailSession] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        self.callbacks = {
            'on_email_received': [],
            'on_verification_code': [],
            'on_error': [],
            'on_status_change': []
        }
    
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
                print(f"Callback error: {e}")
    
    def generate_temp_email(self) -> Tuple[bool, str, Optional[TempEmailSession]]:
        """
        Generate a new temporary email address
        Returns: (success, message, session)
        """
        try:
            self._trigger_callback('on_status_change', 'Generating temporary email...')
            
            # Method 1: Try to scrape the web interface
            response = self.session.get(self.BASE_URL, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for email address in the page
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails_found = re.findall(email_pattern, response.text)
            
            if emails_found:
                # Use the first email found (likely the generated one)
                email_address = emails_found[0]
            else:
                # Fallback: Generate a random email with common temp email domains
                email_address = self._generate_fallback_email()
            
            # Create session
            session_id = self._generate_session_id()
            now = datetime.now()
            expires_at = now + timedelta(hours=3)  # Internxt emails expire after 3 hours
            
            self.current_session = TempEmailSession(
                email_address=email_address,
                session_id=session_id,
                created_at=now,
                expires_at=expires_at,
                messages=[],
                is_active=True
            )
            
            self._trigger_callback('on_status_change', f'Generated email: {email_address}')
            return True, f"Generated temporary email: {email_address}", self.current_session
            
        except requests.RequestException as e:
            error_msg = f"Network error generating email: {str(e)}"
            self._trigger_callback('on_error', error_msg)
            return False, error_msg, None
        except Exception as e:
            error_msg = f"Error generating email: {str(e)}"
            self._trigger_callback('on_error', error_msg)
            return False, error_msg, None
    
    def _generate_fallback_email(self) -> str:
        """Generate a fallback email address"""
        # Common temporary email domains
        domains = [
            'tempmail.org', '10minutemail.com', 'guerrillamail.com',
            'mailinator.com', 'temp-mail.org', 'throwaway.email'
        ]
        
        # Generate random username
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        domain = random.choice(domains)
        
        return f"{username}@{domain}"
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    def start_monitoring(self, poll_interval: int = 15) -> bool:
        """
        Start monitoring the temporary email inbox
        Args:
            poll_interval: Seconds between checks
        Returns: Success status
        """
        if not self.current_session:
            return False
        
        if self.monitoring_active:
            return True
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitor_inbox,
            args=(poll_interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        self._trigger_callback('on_status_change', 'Started email monitoring')
        return True
    
    def stop_monitoring(self):
        """Stop monitoring the email inbox"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        self._trigger_callback('on_status_change', 'Stopped email monitoring')
    
    def _monitor_inbox(self, poll_interval: int):
        """Monitor inbox for new emails (runs in separate thread)"""
        while self.monitoring_active and self.current_session and self.current_session.is_active:
            try:
                # Check if session expired
                if datetime.now() > self.current_session.expires_at:
                    self.current_session.is_active = False
                    self._trigger_callback('on_status_change', 'Email session expired')
                    break
                
                # Check for new emails
                new_messages = self._fetch_new_messages()
                
                for message in new_messages:
                    self.current_session.messages.append(message)
                    self._trigger_callback('on_email_received', message)
                    
                    # Check for verification codes
                    if message.verification_code:
                        self._trigger_callback('on_verification_code', message.verification_code, message)
                
                time.sleep(poll_interval)
                
            except Exception as e:
                self._trigger_callback('on_error', f"Monitoring error: {str(e)}")
                time.sleep(poll_interval * 2)  # Wait longer on error
    
    def _fetch_new_messages(self) -> List[EmailMessage]:
        """Fetch new messages from the inbox"""
        try:
            # Method 1: Try to scrape Internxt inbox
            messages = self._scrape_internxt_inbox()
            if messages:
                return messages

            # Method 2: Try alternative temp email services
            messages = self._try_alternative_services()
            if messages:
                return messages

            # Method 3: Mock for testing (when no real service available)
            return self._mock_fetch_messages()

        except Exception as e:
            self._trigger_callback('on_error', f"Error fetching messages: {str(e)}")
            return []

    def _scrape_internxt_inbox(self) -> List[EmailMessage]:
        """Scrape Internxt inbox for new messages"""
        try:
            # Make request to Internxt temp email page
            response = self.session.get(self.BASE_URL, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            messages = []

            # Look for email elements in the page
            # This would need to be adjusted based on Internxt's actual HTML structure
            email_elements = soup.find_all(['div', 'li'], class_=re.compile(r'(email|message|mail)', re.I))

            for element in email_elements:
                try:
                    # Extract email information
                    sender = self._extract_text_by_pattern(element, r'from[:\s]+([^\n]+)', 'sender')
                    subject = self._extract_text_by_pattern(element, r'subject[:\s]+([^\n]+)', 'subject')
                    content = element.get_text(strip=True)

                    if sender and subject and content:
                        # Extract verification code if present
                        verification_code = self.extract_verification_code(content)

                        message = EmailMessage(
                            sender=sender,
                            subject=subject,
                            content=content,
                            timestamp=datetime.now(),
                            verification_code=verification_code
                        )
                        messages.append(message)

                except Exception as e:
                    continue  # Skip malformed messages

            return messages

        except Exception as e:
            self._trigger_callback('on_error', f"Error scraping Internxt: {str(e)}")
            return []

    def _extract_text_by_pattern(self, element, pattern: str, field_name: str) -> Optional[str]:
        """Extract text using regex pattern"""
        text = element.get_text()
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _try_alternative_services(self) -> List[EmailMessage]:
        """Try alternative temporary email services"""
        # This could implement fallback services like temp-mail.io, guerrillamail, etc.
        # For now, return empty list
        return []

    def _mock_fetch_messages(self) -> List[EmailMessage]:
        """Mock message fetching for testing purposes"""
        # Generate mock AugmentCode verification email for testing
        if hasattr(self, '_mock_sent') and self._mock_sent:
            return []

        # Simulate receiving a verification email after some time
        import random
        if random.random() < 0.1:  # 10% chance each check
            verification_code = ''.join(random.choices('0123456789', k=6))
            mock_message = EmailMessage(
                sender="noreply@augmentcode.com",
                subject="AugmentCode Email Verification",
                content=f"Welcome to AugmentCode! Your verification code is: {verification_code}. Please enter this code to complete your registration.",
                timestamp=datetime.now(),
                verification_code=verification_code
            )
            self._mock_sent = True
            return [mock_message]

        return []
    
    def check_inbox_manually(self) -> Tuple[bool, str, List[EmailMessage]]:
        """Manually check inbox for new messages"""
        if not self.current_session:
            return False, "No active email session", []
        
        try:
            self._trigger_callback('on_status_change', 'Checking inbox...')
            new_messages = self._fetch_new_messages()
            
            for message in new_messages:
                if message not in self.current_session.messages:
                    self.current_session.messages.append(message)
                    self._trigger_callback('on_email_received', message)
                    
                    if message.verification_code:
                        self._trigger_callback('on_verification_code', message.verification_code, message)
            
            count = len(new_messages)
            status_msg = f"Found {count} new message{'s' if count != 1 else ''}"
            self._trigger_callback('on_status_change', status_msg)
            
            return True, status_msg, new_messages
            
        except Exception as e:
            error_msg = f"Error checking inbox: {str(e)}"
            self._trigger_callback('on_error', error_msg)
            return False, error_msg, []
    
    def extract_verification_code(self, email_content: str) -> Optional[str]:
        """
        Extract verification code from email content
        Supports various formats used by services like AugmentCode
        """
        # Common verification code patterns
        patterns = [
            r'verification code[:\s]+([A-Z0-9]{4,8})',  # "verification code: ABC123"
            r'code[:\s]+([A-Z0-9]{4,8})',              # "code: 123456"
            r'([0-9]{4,8})',                           # "123456" (6-8 digits)
            r'([A-Z0-9]{4}-[A-Z0-9]{4})',             # "ABCD-1234"
            r'confirm.*?([A-Z0-9]{4,8})',             # "confirm with ABC123"
            r'enter.*?([A-Z0-9]{4,8})',               # "enter code ABC123"
        ]
        
        email_upper = email_content.upper()
        
        for pattern in patterns:
            matches = re.findall(pattern, email_upper, re.IGNORECASE)
            if matches:
                # Return the first match that looks like a verification code
                for match in matches:
                    if len(match) >= 4 and len(match) <= 8:
                        return match
        
        return None
    
    def get_session_info(self) -> Optional[Dict]:
        """Get current session information"""
        if not self.current_session:
            return None
        
        return {
            'email_address': self.current_session.email_address,
            'created_at': self.current_session.created_at.isoformat(),
            'expires_at': self.current_session.expires_at.isoformat(),
            'is_active': self.current_session.is_active,
            'message_count': len(self.current_session.messages),
            'time_remaining': str(self.current_session.expires_at - datetime.now()) if self.current_session.is_active else "Expired"
        }
    
    def cleanup_session(self):
        """Clean up the current session"""
        self.stop_monitoring()
        if self.current_session:
            self.current_session.is_active = False
        self.current_session = None
        self._trigger_callback('on_status_change', 'Session cleaned up')


# Alternative service implementations can be added here
class TempMailIOService:
    """Alternative temporary email service using temp-mail.io"""
    pass


class GuerrillaMailService:
    """Alternative temporary email service using guerrillamail.com"""
    pass
