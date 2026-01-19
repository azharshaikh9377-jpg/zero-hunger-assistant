# Setup Guide - Zero Hunger Assistant

This guide will help you set up and run the Zero Hunger Assistant system.

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- Supabase account (free tier works)
- Webhook URL (optional, for testing use https://webhook.site or similar)

## Step 1: Supabase Setup

1. Go to [Supabase](https://supabase.com) and create a new project
2. Wait for the project to be provisioned
3. Go to the SQL Editor in your Supabase dashboard
4. Run the SQL from `backend/supabase_schema.sql`:
   ```sql
   CREATE TABLE IF NOT EXISTS conversations (
       id BIGSERIAL PRIMARY KEY,
       session_id TEXT UNIQUE NOT NULL,
       program TEXT CHECK (program IN ('emergency_food_aid', 'nutrition_support', 'general_food_access')),
       beneficiary_name TEXT,
       beneficiary_age INTEGER,
       assistance_request TEXT,
       messages JSONB DEFAULT '[]'::jsonb,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   
   CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
   CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
   ```
5. Get your Supabase credentials:
   - Go to Project Settings > API
   - Copy your "Project URL" (SUPABASE_URL)
   - Copy your "anon public" key (SUPABASE_KEY)

## Step 2: Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd zero-hunger-assistant/backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```
   
   Activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory:
   ```bash
   # On Windows (PowerShell)
   Copy-Item .env.example .env
   
   # On Mac/Linux
   cp .env.example .env
   ```

5. Edit the `.env` file and add your credentials:
   ```env
   SUPABASE_URL
   SUPABASE_KEY=your-anon-key-here
   WEBHOOK_URL=https://webhook.site/your-unique-url
   ```

   For testing webhooks, you can use [webhook.site](https://webhook.site) to get a unique URL.

6. Start the backend server:
   ```bash
   python main.py
   ```

   Or with auto-reload:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

   The backend should now be running at `http://localhost:8000`

## Step 3: Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd zero-hunger-assistant/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. (Optional) Create a `.env` file if you need to change the API URL:
   ```bash
   # Windows (PowerShell)
   Copy-Item .env.example .env
   
   # Mac/Linux
   cp .env.example .env
   ```

   Edit `.env` if your backend runs on a different port:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend should now be running at `http://localhost:5173`

## Step 4: Testing

1. Open your browser and go to `http://localhost:5173`

2. Try a conversation like:
   - User: "I need emergency food assistance"
   - Assistant will ask for name
   - User: "My name is John Doe"
   - Assistant will ask for age
   - User: "I'm 35 years old"
   - Assistant will ask about the request
   - User: "I lost my home in a flood and have no food"
   - Assistant will confirm and trigger the webhook

3. Check your webhook URL to verify the data was sent:
   ```json
   {
     "beneficiary_name": "John Doe",
     "beneficiary_age": 35,
     "assistance_request": "I lost my home in a flood and have no food",
     "program": "emergency_food_aid"
   }
   ```

4. Check your Supabase database to see the stored conversation data

## Troubleshooting

### Backend Issues

- **Import errors**: Make sure you've activated your virtual environment and installed all requirements
- **Supabase connection errors**: Verify your SUPABASE_URL and SUPABASE_KEY are correct
- **Port already in use**: Change the port in `main.py` or stop the process using port 8000

### Frontend Issues

- **Cannot connect to backend**: Check that the backend is running and verify the API URL in `.env`
- **CORS errors**: Make sure the backend CORS middleware includes your frontend URL

### Database Issues

- **Table doesn't exist**: Make sure you ran the SQL schema in Supabase
- **Permission errors**: Check that your Supabase key has the correct permissions

## Production Deployment

For production deployment:

1. Set proper environment variables (never commit `.env` files)
2. Use a production-grade ASGI server like Gunicorn with Uvicorn workers
3. Configure proper CORS origins
4. Use environment-specific Supabase credentials
5. Set up proper webhook authentication if needed
6. Configure HTTPS for both frontend and backend

## Support

For issues or questions, refer to the main README.md file.



