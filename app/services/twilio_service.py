"""Twilio service for WhatsApp messaging."""
from typing import Optional
from twilio.rest import Client
from twilio.request_validator import RequestValidator

from app.config import settings
from app.utils.logger import app_logger


class TwilioService:
    """Service for Twilio WhatsApp messaging."""
    
    def __init__(self):
        """Initialize Twilio client."""
        self.client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.from_number = settings.twilio_whatsapp_number
        self.validator = RequestValidator(settings.twilio_auth_token)
    
    def send_message(self, to_number: str, message: str) -> bool:
        """
        Send WhatsApp message via Twilio.
        
        Args:
            to_number: Recipient WhatsApp number (format: whatsapp:+1234567890)
            message: Message text to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure number has whatsapp: prefix
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            app_logger.info(f"Sent message to {to_number}: SID {message_obj.sid}")
            return True
            
        except Exception as e:
            app_logger.error(f"Error sending message to {to_number}: {e}")
            return False
    
    def validate_webhook(
        self,
        url: str,
        params: dict,
        signature: str
    ) -> bool:
        """
        Validate Twilio webhook signature.
        
        Args:
            url: Full webhook URL
            params: Request parameters
            signature: X-Twilio-Signature header
            
        Returns:
            True if valid, False otherwise
        """
        try:
            return self.validator.validate(url, params, signature)
        except Exception as e:
            app_logger.error(f"Error validating webhook: {e}")
            return False
    
    def format_whatsapp_message(self, text: str) -> str:
        """
        Format message for optimal WhatsApp display.
        
        Args:
            text: Raw message text
            
        Returns:
            Formatted message
        """
        # Ensure proper line breaks and spacing
        formatted = text.strip()
        
        # Replace multiple newlines with double newline for better spacing
        formatted = "\n\n".join([p.strip() for p in formatted.split("\n\n") if p.strip()])
        
        return formatted


# Global instance
twilio_service = TwilioService()
