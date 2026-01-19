# zero-hunger-assistant
# 🥗 Zero Hunger Assistant
An AI-powered full-stack platform helping users access food assistance programs.

## 🔗 Live Application
**[CLICK HERE TO VIEW THE LIVE PROJECT](PASTE_YOUR_RENDER_FRONTEND_LINK_HERE)**
*(Note: Please allow 30-60 seconds for the free server to wake up on the first load.)*

## 🛠️ Tech Stack
- **Frontend:** React.js + Vite (Deployed on Render Static Site)
- **Backend:** Python + FastAPI + LangGraph (Deployed on Render Web Service)
- **Database:** Supabase (PostgreSQL)
- **AI Logic:** LangChain State Management

## 🏗️ Architecture
The project is split into two independent services to ensure scalability:
1.  **Backend API:** Handles AI processing, Supabase queries, and LangGraph logic.
2.  **Frontend UI:** A modern, responsive chat interface that communicates with the API via environment variables.

## 🚀 Local Development
If you wish to run this project locally:

### 1. Backend
- Navigate to `/backend`
- Create a virtual environment: `python -m venv venv`
- Install dependencies: `pip install -r requirements.txt`
- Run: `python main.py`

### 2. Frontend
- Navigate to `/frontend`
- Install dependencies: `npm install`
- Run: `npm run dev`

## ⚙️ Deployment Details
- **Environment Variables:** The frontend uses `VITE_API_URL` to dynamically connect to the hosted FastAPI service.
- **CORS:** The backend is configured to allow cross-origin requests for secure web access.
-
