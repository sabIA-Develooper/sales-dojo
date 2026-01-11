-- ============================================
-- Sales AI Dojo - Database Initialization
-- ============================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create uuid extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: Tables will be created by Alembic migrations
-- This file only enables required extensions
