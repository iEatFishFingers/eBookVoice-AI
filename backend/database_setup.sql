-- Supabase Database Setup for eBookVoice-AI
-- Run this SQL in your Supabase SQL Editor

-- Users table: Core identity and profile
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_id VARCHAR(255) UNIQUE NOT NULL,  -- External identity reference
    email VARCHAR(255) UNIQUE NOT NULL,      -- Business key for user lookup
    name VARCHAR(255) NOT NULL,
    picture_url TEXT,
    subscription_type VARCHAR(50) DEFAULT 'free',  -- Future monetization
    storage_used_bytes BIGINT DEFAULT 0,    -- Track usage for quotas
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Audiobooks table: User's converted audiobooks
CREATE TABLE IF NOT EXISTS audiobooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,  -- Data integrity
    title VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    storage_key VARCHAR(500) NOT NULL,      -- R2/S3 object key
    file_size BIGINT NOT NULL,              -- For quota management
    duration_seconds INTEGER,               -- For UI progress bars
    status VARCHAR(50) DEFAULT 'processing', -- State machine for conversion
    metadata JSONB,                         -- Flexible schema for TTS settings
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    -- Database-level constraints for data quality
    CONSTRAINT positive_file_size CHECK (file_size > 0),
    CONSTRAINT valid_status CHECK (status IN ('processing', 'completed', 'failed', 'deleted'))
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_audiobooks_user_id ON audiobooks(user_id);
CREATE INDEX IF NOT EXISTS idx_audiobooks_status ON audiobooks(status);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);

-- Row-Level Security (RLS) - enterprise security pattern
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE audiobooks ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can only access their own profile" ON users;
DROP POLICY IF EXISTS "Users can only access their own audiobooks" ON audiobooks;

-- Users can only see their own data
CREATE POLICY "Users can only access their own profile" 
    ON users FOR ALL 
    USING (auth.jwt() ->> 'sub' = google_id);

CREATE POLICY "Users can only access their own audiobooks" 
    ON audiobooks FOR ALL 
    USING (
        user_id IN (
            SELECT id FROM users WHERE google_id = auth.jwt() ->> 'sub'
        )
    );

-- Grant necessary permissions
GRANT ALL ON users TO authenticated;
GRANT ALL ON audiobooks TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;

-- Insert a test user (optional - remove in production)
INSERT INTO users (google_id, email, name, picture_url) 
VALUES ('test-user-123', 'test@example.com', 'Test User', 'https://example.com/avatar.jpg')
ON CONFLICT (google_id) DO NOTHING;