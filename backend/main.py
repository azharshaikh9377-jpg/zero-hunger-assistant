from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from conversation_flow import ConversationFlow
from database import Database
import os

app = FastAPI(title="Zero Hunger Assistant API")

# Define explicitly allowed origins
# REPLACE the render URL with your actual frontend URL from your Render dashboard
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://zero-hunger-web.onrender.com", # Add your actual frontend URL here
]

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Must use specific list, not "*"
    allow_credentials=True,     # Required for session/cookie support
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
        # Note: If an internal 500 error occurs, CORS headers might not be sent.
        # Ensure your API key and DB connection are working correctly.
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # Render uses the PORT environment variable; default to 10000 for Render
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
