# Zero Hunger Assistant - Backend

FastAPI backend with LangGraph conversation flow for the Zero Hunger Assistant.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

3. Configure environment variables in `.env`:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
   - `WEBHOOK_URL`: URL to send beneficiary data

## Database Schema

Create the following table in Supabase:

```sql
CREATE TABLE conversations (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    program TEXT,
    beneficiary_name TEXT,
    beneficiary_age INTEGER,
    assistance_request TEXT,
    messages JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Running the Server

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /chat
Send a user message and receive AI response.

**Request:**
```json
{
  "message": "I need emergency food assistance",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "Thank you for reaching out...",
  "session_id": "session-uuid"
}
```

### GET /health
Health check endpoint.



