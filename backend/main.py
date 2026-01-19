from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from conversation_flow import ConversationFlow
from database import Database
import os

app = FastAPI(title="Zero Hunger Assistant API")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize conversation flow and database
conversation_flow = ConversationFlow()
db = Database()


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """
    Main chat endpoint that processes user messages and returns AI responses.
    """
    try:
        # Get or create session ID
        session_id = chat_message.session_id
        if not session_id:
            session_id = db.create_session()
        
        # Process message through LangGraph conversation flow
        response = await conversation_flow.process_message(
            message=chat_message.message,
            session_id=session_id
        )
        
        return ChatResponse(
            response=response["message"],
            session_id=session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)



