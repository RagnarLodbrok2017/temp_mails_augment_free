"""
Temporary Email Module for Free AugmentCode
Provides temporary email functionality with verification code extraction
"""

from .temp_email_service import (
    InternxtTempEmailService,
    EmailMessage,
    TempEmailSession,
    TempMailIOService,
    GuerrillaMailService
)

__all__ = [
    'InternxtTempEmailService',
    'EmailMessage', 
    'TempEmailSession',
    'TempMailIOService',
    'GuerrillaMailService'
]
