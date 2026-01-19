from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Literal
import re
from database import Database
from webhook_client import WebhookClient


class ConversationState(TypedDict):
    messages: List[dict]
    session_id: str
    program: Literal["emergency_food_aid", "nutrition_support", "general_food_access", None]
    beneficiary_name: str | None
    beneficiary_age: int | None
    assistance_request: str | None
    current_node: str


class ConversationFlow:
    def __init__(self):
        self.db = Database()
        self.webhook_client = WebhookClient()
        self.build_graph()
    
    def build_graph(self):
        """Build the LangGraph conversation workflow"""
        workflow = StateGraph(ConversationState)
        
        # Add nodes
        workflow.add_node("start", self.start_node)
        workflow.add_node("router", self.router_node)
        workflow.add_node("emergency_food_aid", self.emergency_food_aid_node)
        workflow.add_node("nutrition_support", self.nutrition_support_node)
        workflow.add_node("general_food_access", self.general_food_access_node)
        
        # Add edges
        workflow.set_entry_point("start")
        
        # Conditional: skip router if program is already set
        workflow.add_conditional_edges(
            "start",
            self._should_skip_router_check,
            {
                "router": "router",
                "emergency_food_aid": "emergency_food_aid",
                "nutrition_support": "nutrition_support",
                "general_food_access": "general_food_access",
            }
        )
        
        # Conditional routing from router
        workflow.add_conditional_edges(
            "router",
            self.route_to_program,
            {
                "emergency_food_aid": "emergency_food_aid",
                "nutrition_support": "nutrition_support",
                "general_food_access": "general_food_access",
            }
        )
        
        # All program nodes end after processing one message
        # The next user message will restart the flow
        workflow.add_edge("emergency_food_aid", END)
        workflow.add_edge("nutrition_support", END)
        workflow.add_edge("general_food_access", END)
        
        self.graph = workflow.compile()
    
    def start_node(self, state: ConversationState) -> ConversationState:
        """Initial node that receives user message"""
        state["current_node"] = "start"
        return state
    
    def _should_skip_router_check(self, state: ConversationState) -> str:
        """Check if we should skip router and go directly to program node"""
        program = state.get("program")
        
        if program == "emergency_food_aid":
            return "emergency_food_aid"
        elif program == "nutrition_support":
            return "nutrition_support"
        elif program == "general_food_access":
            return "general_food_access"
        else:
            return "router"
    
    def router_node(self, state: ConversationState) -> ConversationState:
        """Classify user intent into one of three programs"""
        messages = state.get("messages", [])
        if not messages:
            state["program"] = "general_food_access"
            return state
        
        last_message = messages[-1].get("content", "").lower()
        
        # Emergency Food Aid keywords
        emergency_keywords = [
            "no food", "hunger crisis", "starving", "disaster", "displacement",
            "urgent", "immediate", "emergency", "no food available", "crisis"
        ]
        
        # Nutrition Support keywords
        nutrition_keywords = [
            "nutrition", "malnutrition", "child nutrition", "maternal",
            "pregnant", "lactating", "breastfeeding", "dietary", "pregnancy"
        ]
        
        # Check for emergency first (highest priority)
        if any(keyword in last_message for keyword in emergency_keywords):
            state["program"] = "emergency_food_aid"
        elif any(keyword in last_message for keyword in nutrition_keywords):
            state["program"] = "nutrition_support"
        else:
            state["program"] = "general_food_access"
        
        state["current_node"] = "router"
        return state
    
    def route_to_program(self, state: ConversationState) -> str:
        """Route to appropriate program node"""
        program = state.get("program")
        if program == "emergency_food_aid":
            return "emergency_food_aid"
        elif program == "nutrition_support":
            return "nutrition_support"
        else:
            return "general_food_access"
    
    def emergency_food_aid_node(self, state: ConversationState) -> ConversationState:
        """Handle Emergency Food Aid program - collect beneficiary info"""
        return self._collect_beneficiary_info(state, "emergency_food_aid")
    
    def nutrition_support_node(self, state: ConversationState) -> ConversationState:
        """Handle Nutrition Support program - collect beneficiary info"""
        return self._collect_beneficiary_info(state, "nutrition_support")
    
    def general_food_access_node(self, state: ConversationState) -> ConversationState:
        """Handle General Food Access program - collect beneficiary info"""
        return self._collect_beneficiary_info(state, "general_food_access")
    
    def _collect_beneficiary_info(
        self, 
        state: ConversationState, 
        program: str
    ) -> ConversationState:
        """Generic function to collect beneficiary information"""
        messages = state.get("messages", [])
        last_message = messages[-1].get("content", "") if messages else ""
        
        # Extract information from user message
        self._extract_info_from_message(state, last_message)
        
        # Check what's missing and ask for one thing at a time
        missing_info = []
        
        if not state.get("beneficiary_name"):
            missing_info.append("name")
        if state.get("beneficiary_age") is None:
            missing_info.append("age")
        if not state.get("assistance_request"):
            missing_info.append("assistance_request")
        
        # Generate response based on what's missing
        if missing_info:
            # Ask for the first missing piece of information
            response = self._generate_clarification_question(
                missing_info[0], 
                program
            )
        else:
            # All information collected - trigger webhook and prepare completion message
            name = state.get("beneficiary_name")
            age = state.get("beneficiary_age")
            request = state.get("assistance_request")
            
            if name and age is not None and request:
                # Trigger webhook
                self.webhook_client.send_webhook(
                    beneficiary_name=name,
                    beneficiary_age=age,
                    assistance_request=request,
                    program=program
                )
            
            response = self._generate_completion_message(program)
        
        # Add AI response to messages
        state["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        # Update database
        self.db.save_conversation(
            session_id=state["session_id"],
            program=program,
            beneficiary_name=state.get("beneficiary_name"),
            beneficiary_age=state.get("beneficiary_age"),
            assistance_request=state.get("assistance_request"),
            messages=state["messages"]
        )
        
        state["current_node"] = program
        return state
    
    def _extract_info_from_message(self, state: ConversationState, message: str):
        """Extract beneficiary information from user message"""
        message_lower = message.lower()
        
        # Try to extract name (simple heuristic: look for "my name is" or "I'm" patterns)
        if not state.get("beneficiary_name"):
            name_patterns = [
                r"my name is ([A-Za-z\s]+)",
                r"i['']?m ([A-Za-z\s]+)",
                r"name is ([A-Za-z\s]+)",
                r"i am ([A-Za-z\s]+)",
            ]
            for pattern in name_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    state["beneficiary_name"] = match.group(1).strip()
                    break
        
        # Try to extract age
        if state.get("beneficiary_age") is None:
            age_patterns = [
                r"i['']?m (\d+) years? old",
                r"age is (\d+)",
                r"(\d+) years? old",
                r"aged (\d+)",
            ]
            for pattern in age_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    try:
                        state["beneficiary_age"] = int(match.group(1))
                        break
                    except ValueError:
                        pass
        
        # Extract assistance request (if user provides detailed request)
        # Only extract if message is substantial and doesn't match name/age patterns
        if not state.get("assistance_request"):
            name_age_patterns = [
                r"^(my name is|i['']?m|i am|name is)",
                r"^(age is|i['']?m \d+|aged \d+)",
                r"^\d+$",  # Just a number (likely age)
            ]
            is_name_or_age = any(re.match(pattern, message_lower) for pattern in name_age_patterns)
            
            if not is_name_or_age and len(message.strip()) > 15:
                # Substantial message that's not just name/age - treat as assistance request
                state["assistance_request"] = message.strip()
    
    def _generate_clarification_question(self, missing_field: str, program: str) -> str:
        """Generate a clarification question for missing information"""
        program_names = {
            "emergency_food_aid": "Emergency Food Aid",
            "nutrition_support": "Nutrition Support Program",
            "general_food_access": "General Food Access Program"
        }
        
        program_name = program_names.get(program, "Food Assistance")
        
        if missing_field == "name":
            return f"Thank you for reaching out to the {program_name}. To assist you better, may I please have your name?"
        
        elif missing_field == "age":
            return "Could you please share your age? This helps us provide appropriate assistance."
        
        elif missing_field == "assistance_request":
            return "Please tell me more about your food assistance needs. What specific help are you looking for?"
        
        return "I need a bit more information to help you. Could you please provide more details?"
    
    def _generate_completion_message(self, program: str) -> str:
        """Generate completion message when all info is collected"""
        program_names = {
            "emergency_food_aid": "Emergency Food Aid",
            "nutrition_support": "Nutrition Support Program",
            "general_food_access": "General Food Access Program"
        }
        
        program_name = program_names.get(program, "Food Assistance")
        
        return (
            f"Thank you for providing all the necessary information. "
            f"I've registered your request with the {program_name}. "
            f"Your information has been submitted and our team will contact you shortly to assist you further."
        )
    
    
    async def process_message(self, message: str, session_id: str) -> dict:
        """Process a user message through the conversation flow"""
        # Load existing conversation state from database
        state = self.db.load_conversation_state(session_id)
        
        if not state:
            # Initialize new conversation
            state = {
                "messages": [],
                "session_id": session_id,
                "program": None,
                "beneficiary_name": None,
                "beneficiary_age": None,
                "assistance_request": None,
                "current_node": "start"
            }
        
        # Add user message
        state["messages"].append({
            "role": "user",
            "content": message
        })
        
        # Run through graph
        final_state = self.graph.invoke(state)
        
        # Extract last AI message
        messages = final_state.get("messages", [])
        ai_messages = [m for m in messages if m.get("role") == "assistant"]
        last_ai_message = ai_messages[-1]["content"] if ai_messages else "I'm here to help you with food assistance."
        
        return {
            "message": last_ai_message,
            "session_id": session_id,
            "state": final_state
        }

