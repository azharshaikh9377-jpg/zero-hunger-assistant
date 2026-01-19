-- Supabase Database Schema for Zero Hunger Assistant

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

-- Create index on session_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);

