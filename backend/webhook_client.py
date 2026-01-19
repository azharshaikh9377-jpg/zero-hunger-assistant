import os
import httpx
from typing import Literal


class WebhookClient:
    def __init__(self):
        """Initialize webhook client"""
        self.webhook_url = os.getenv("WEBHOOK_URL", "")
        
        if not self.webhook_url:
            print("Warning: WEBHOOK_URL not set. Webhooks will not be sent.")
    
    def send_webhook(
        self,
        beneficiary_name: str,
        beneficiary_age: int,
        assistance_request: str,
        program: Literal["emergency_food_aid", "nutrition_support", "general_food_access"]
    ) -> bool:
        """
        Send beneficiary information to webhook endpoint.
        
        Returns True if successful, False otherwise.
        """
        if not self.webhook_url:
            print(f"[MOCK WEBHOOK] Would send: {beneficiary_name}, {beneficiary_age}, {assistance_request}, {program}")
            return False
        
        payload = {
            "beneficiary_name": beneficiary_name,
            "beneficiary_age": beneficiary_age,
            "assistance_request": assistance_request,
            "program": program
        }
        
        try:
            response = httpx.post(
                self.webhook_url,
                json=payload,
                timeout=10.0
            )
            
            if response.status_code == 200:
                print(f"Webhook sent successfully for {beneficiary_name}")
                return True
            else:
                print(f"Webhook failed with status {response.status_code}: {response.text}")
                return False
        
        except Exception as e:
            print(f"Error sending webhook: {e}")
            return False



