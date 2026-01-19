from supabase import create_client, Client
import os
from typing import Optional, Dict, List
import json


class Database:
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_KEY", "")
        
        if not supabase_url or not supabase_key:
            # For development, use placeholder values
            print("Warning: SUPABASE_URL and SUPABASE_KEY not set. Using mock mode.")
            self.client = None
            self.mock_mode = True
        else:
            self.client: Client = create_client(supabase_url, supabase_key)
            self.mock_mode = False
    
    def create_session(self) -> str:
        """Create a new conversation session"""
        import uuid
        session_id = str(uuid.uuid4())
        
        if self.mock_mode:
            # Store in memory for testing
            if not hasattr(self, '_sessions'):
                self._sessions = {}
            self._sessions[session_id] = {
                "session_id": session_id,
                "program": None,
                "beneficiary_name": None,
                "beneficiary_age": None,
                "assistance_request": None,
                "messages": []
            }
            return session_id
        
        try:
            # Insert new session into Supabase
            result = self.client.table("conversations").insert({
                "session_id": session_id,
                "program": None,
                "beneficiary_name": None,
                "beneficiary_age": None,
                "assistance_request": None,
                "messages": []
            }).execute()
            return session_id
        except Exception as e:
            print(f"Error creating session: {e}")
            return session_id
    
    def save_conversation(
        self,
        session_id: str,
        program: Optional[str],
        beneficiary_name: Optional[str],
        beneficiary_age: Optional[int],
        assistance_request: Optional[str],
        messages: List[Dict]
    ):
        """Save conversation state to database"""
        if self.mock_mode:
            if hasattr(self, '_sessions') and session_id in self._sessions:
                self._sessions[session_id].update({
                    "program": program,
                    "beneficiary_name": beneficiary_name,
                    "beneficiary_age": beneficiary_age,
                    "assistance_request": assistance_request,
                    "messages": messages
                })
            return
        
        try:
            # Update conversation in Supabase
            self.client.table("conversations").update({
                "program": program,
                "beneficiary_name": beneficiary_name,
                "beneficiary_age": beneficiary_age,
                "assistance_request": assistance_request,
                "messages": json.dumps(messages)
            }).eq("session_id", session_id).execute()
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    def load_conversation_state(self, session_id: str) -> Optional[Dict]:
        """Load conversation state from database"""
        if self.mock_mode:
            if hasattr(self, '_sessions') and session_id in self._sessions:
                return self._sessions[session_id]
            return None
        
        try:
            result = self.client.table("conversations").select("*").eq(
                "session_id", session_id
            ).execute()
            
            if result.data:
                row = result.data[0]
                messages = row.get("messages", [])
                if isinstance(messages, str):
                    messages = json.loads(messages)
                
                return {
                    "messages": messages,
                    "session_id": session_id,
                    "program": row.get("program"),
                    "beneficiary_name": row.get("beneficiary_name"),
                    "beneficiary_age": row.get("beneficiary_age"),
                    "assistance_request": row.get("assistance_request"),
                    "current_node": "start"
                }
        except Exception as e:
            print(f"Error loading conversation state: {e}")
        
        return None



