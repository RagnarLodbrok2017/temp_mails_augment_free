"""
Error handling and resilience utilities for temporary email services
"""

import time
import logging
from typing import Callable, Any, Optional
from functools import wraps
import requests


class EmailServiceError(Exception):
    """Base exception for email service errors"""
    pass


class NetworkError(EmailServiceError):
    """Network-related errors"""
    pass


class ServiceUnavailableError(EmailServiceError):
    """Service temporarily unavailable"""
    pass


class SessionExpiredError(EmailServiceError):
    """Email session has expired"""
    pass


class RetryHandler:
    """Handles retry logic with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry and exponential backoff"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except requests.RequestException as e:
                last_exception = NetworkError(f"Network error: {str(e)}")
                if attempt == self.max_retries:
                    break
                
                # Calculate delay with exponential backoff
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                time.sleep(delay)
            except Exception as e:
                last_exception = EmailServiceError(f"Service error: {str(e)}")
                if attempt == self.max_retries:
                    break
                
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                time.sleep(delay)
        
        raise last_exception


def with_error_handling(retry_count: int = 3):
    """Decorator for adding error handling to methods"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_handler = RetryHandler(max_retries=retry_count)
            try:
                return retry_handler.retry_with_backoff(func, *args, **kwargs)
            except EmailServiceError:
                raise
            except Exception as e:
                raise EmailServiceError(f"Unexpected error in {func.__name__}: {str(e)}")
        return wrapper
    return decorator


class ServiceHealthChecker:
    """Monitors service health and availability"""
    
    def __init__(self):
        self.last_check = 0
        self.check_interval = 300  # 5 minutes
        self.service_status = {}
    
    def is_service_healthy(self, service_url: str) -> bool:
        """Check if a service is healthy"""
        current_time = time.time()
        
        # Use cached result if recent
        if (service_url in self.service_status and 
            current_time - self.last_check < self.check_interval):
            return self.service_status[service_url]
        
        try:
            response = requests.head(service_url, timeout=10)
            is_healthy = response.status_code < 500
            self.service_status[service_url] = is_healthy
            self.last_check = current_time
            return is_healthy
        except requests.RequestException:
            self.service_status[service_url] = False
            self.last_check = current_time
            return False


class FallbackManager:
    """Manages fallback services when primary service fails"""
    
    def __init__(self):
        self.fallback_services = [
            {
                'name': 'temp-mail.io',
                'url': 'https://temp-mail.io',
                'priority': 1
            },
            {
                'name': 'guerrillamail.com',
                'url': 'https://guerrillamail.com',
                'priority': 2
            },
            {
                'name': '10minutemail.com',
                'url': 'https://10minutemail.com',
                'priority': 3
            }
        ]
        self.health_checker = ServiceHealthChecker()
    
    def get_available_service(self) -> Optional[dict]:
        """Get the best available fallback service"""
        # Sort by priority
        sorted_services = sorted(self.fallback_services, key=lambda x: x['priority'])
        
        for service in sorted_services:
            if self.health_checker.is_service_healthy(service['url']):
                return service
        
        return None


# Setup logging for the email service
def setup_logging():
    """Setup logging for email service operations"""
    logger = logging.getLogger('tempmail')
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


# Global logger instance
logger = setup_logging()
