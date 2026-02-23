"""
Notification Service
Sends alerts via WhatsApp, SMS, or Email when users ask questions
"""

import logging
import os
from datetime import datetime
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class NotificationService:
    """Send notifications via multiple channels"""
    
    def __init__(self):
        # Email settings (using SendGrid or similar)
        self.email_api_key = os.getenv("SENDGRID_API_KEY")
        self.email_from = os.getenv("NOTIFICATION_EMAIL_FROM", "noreply@gitagpt.com")
        self.email_to = os.getenv("NOTIFICATION_EMAIL_TO")
        
        # SMS settings (using Twilio)
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from = os.getenv("TWILIO_FROM_NUMBER")
        self.twilio_to = os.getenv("TWILIO_TO_NUMBER")
        
        # WhatsApp settings (using Twilio WhatsApp)
        self.whatsapp_from = os.getenv("WHATSAPP_FROM_NUMBER")  # Format: whatsapp:+14155238886
        self.whatsapp_to = os.getenv("WHATSAPP_TO_NUMBER")      # Format: whatsapp:+15551234567
        
        # Slack webhook (alternative)
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        
        # Discord webhook (alternative)
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        
        # Notification settings
        self.enabled = os.getenv("NOTIFICATIONS_ENABLED", "false").lower() == "true"
        self.channels = os.getenv("NOTIFICATION_CHANNELS", "email").split(",")  # email,sms,whatsapp,slack
    
    def send_question_alert(
        self,
        question: str,
        user_info: Optional[dict] = None,
        timestamp: Optional[str] = None
    ) -> dict:
        """
        Send notification when a user asks a question
        
        Args:
            question: The user's question
            user_info: Optional user information (IP, location, etc.)
            timestamp: Optional timestamp
            
        Returns:
            Dictionary with notification results
        """
        if not self.enabled:
            logger.info("Notifications disabled")
            return {"enabled": False}
        
        timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results = {}
        
        # Prepare message
        message = self._format_message(question, user_info, timestamp)
        short_message = self._format_short_message(question, timestamp)
        
        # Send via configured channels
        for channel in self.channels:
            channel = channel.strip().lower()
            
            if channel == "email":
                results["email"] = self._send_email(message)
            elif channel == "sms":
                results["sms"] = self._send_sms(short_message)
            elif channel == "whatsapp":
                results["whatsapp"] = self._send_whatsapp(message)
            elif channel == "slack":
                results["slack"] = self._send_slack(message)
            elif channel == "discord":
                results["discord"] = self._send_discord(message)
        
        return results
    
    def _format_message(self, question: str, user_info: Optional[dict], timestamp: str) -> str:
        """Format detailed notification message"""
        message = f"🔔 New Question Alert\n\n"
        message += f"⏰ Time: {timestamp}\n"
        message += f"❓ Question: {question}\n"
        
        if user_info:
            if user_info.get("ip"):
                message += f"🌐 IP: {user_info['ip']}\n"
            if user_info.get("location"):
                message += f"📍 Location: {user_info['location']}\n"
            if user_info.get("user_agent"):
                message += f"💻 Device: {user_info['user_agent'][:50]}...\n"
        
        message += f"\n🔗 View in dashboard: https://your-dashboard-url.com"
        return message
    
    def _format_short_message(self, question: str, timestamp: str) -> str:
        """Format short message for SMS"""
        # SMS has 160 character limit
        question_short = question[:80] + "..." if len(question) > 80 else question
        return f"New Q ({timestamp}): {question_short}"
    
    def _send_email(self, message: str) -> bool:
        """Send email notification using SendGrid"""
        if not self.email_api_key or not self.email_to:
            logger.warning("Email not configured")
            return False
        
        try:
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {self.email_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "personalizations": [{
                    "to": [{"email": self.email_to}],
                    "subject": "🔔 New Bhagavad Gita Question"
                }],
                "from": {"email": self.email_from},
                "content": [{
                    "type": "text/plain",
                    "value": message
                }]
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 202:
                logger.info("Email notification sent successfully")
                return True
            else:
                logger.error(f"Email failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Email error: {e}")
            return False
    
    def _send_sms(self, message: str) -> bool:
        """Send SMS notification using Twilio"""
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_from, self.twilio_to]):
            logger.warning("SMS not configured")
            return False
        
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
            
            response = requests.post(
                url,
                auth=(self.twilio_account_sid, self.twilio_auth_token),
                data={
                    "From": self.twilio_from,
                    "To": self.twilio_to,
                    "Body": message
                },
                timeout=10
            )
            
            if response.status_code == 201:
                logger.info("SMS notification sent successfully")
                return True
            else:
                logger.error(f"SMS failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"SMS error: {e}")
            return False
    
    def _send_whatsapp(self, message: str) -> bool:
        """Send WhatsApp notification using Twilio"""
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.whatsapp_from, self.whatsapp_to]):
            logger.warning("WhatsApp not configured")
            return False
        
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
            
            response = requests.post(
                url,
                auth=(self.twilio_account_sid, self.twilio_auth_token),
                data={
                    "From": self.whatsapp_from,
                    "To": self.whatsapp_to,
                    "Body": message
                },
                timeout=10
            )
            
            if response.status_code == 201:
                logger.info("WhatsApp notification sent successfully")
                return True
            else:
                logger.error(f"WhatsApp failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"WhatsApp error: {e}")
            return False
    
    def _send_slack(self, message: str) -> bool:
        """Send Slack notification"""
        if not self.slack_webhook_url:
            logger.warning("Slack not configured")
            return False
        
        try:
            response = requests.post(
                self.slack_webhook_url,
                json={"text": message},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Slack notification sent successfully")
                return True
            else:
                logger.error(f"Slack failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Slack error: {e}")
            return False
    
    def _send_discord(self, message: str) -> bool:
        """Send Discord notification"""
        if not self.discord_webhook_url:
            logger.warning("Discord not configured")
            return False
        
        try:
            response = requests.post(
                self.discord_webhook_url,
                json={"content": message},
                timeout=10
            )
            
            if response.status_code == 204:
                logger.info("Discord notification sent successfully")
                return True
            else:
                logger.error(f"Discord failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Discord error: {e}")
            return False
    
    def send_daily_summary(self, stats: dict) -> dict:
        """
        Send daily summary of questions
        
        Args:
            stats: Dictionary with daily statistics
            
        Returns:
            Notification results
        """
        message = f"📊 Daily Summary - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        message += f"Total Questions: {stats.get('total_questions', 0)}\n"
        message += f"Unique Users: {stats.get('unique_users', 0)}\n"
        message += f"Avg Response Time: {stats.get('avg_response_time', 0):.2f}ms\n"
        message += f"Top Question: {stats.get('top_question', 'N/A')}\n"
        
        results = {}
        if "email" in self.channels:
            results["email"] = self._send_email(message)
        
        return results
