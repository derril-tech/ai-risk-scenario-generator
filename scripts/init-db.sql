-- Initialize AI Risk Scenario Generator Database

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS scenarios;
CREATE SCHEMA IF NOT EXISTS simulations;
CREATE SCHEMA IF NOT EXISTS ingestion;
CREATE SCHEMA IF NOT EXISTS reports;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    org_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create scenarios table (already defined in entity, but ensuring it exists)
CREATE TABLE IF NOT EXISTS scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL CHECK (type IN ('financial', 'supply_chain', 'cyber', 'operational')),
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed', 'archived')),
    assumptions JSONB DEFAULT '{}',
    narrative JSONB DEFAULT '{}',
    org_id UUID REFERENCES organizations(id),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create simulations table
CREATE TABLE IF NOT EXISTS simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES scenarios(id) ON DELETE CASCADE,
    runs INTEGER NOT NULL,
    seed INTEGER,
    results JSONB DEFAULT '{}',
    distribution JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create data_sources table
CREATE TABLE IF NOT EXISTS data_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    connection_config JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'inactive',
    last_sync TIMESTAMP,
    records_ingested INTEGER DEFAULT 0,
    org_id UUID REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create assets table for ingested data
CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    value DECIMAL(15,2),
    metadata JSONB DEFAULT '{}',
    embedding vector(1536), -- OpenAI embedding dimension
    data_source_id UUID REFERENCES data_sources(id),
    org_id UUID REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES scenarios(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    format VARCHAR(20) NOT NULL CHECK (format IN ('pdf', 'json', 'csv')),
    sections JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'generating' CHECK (status IN ('generating', 'completed', 'failed')),
    file_path VARCHAR(500),
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_scenarios_org_id ON scenarios(org_id);
CREATE INDEX IF NOT EXISTS idx_scenarios_type ON scenarios(type);
CREATE INDEX IF NOT EXISTS idx_scenarios_status ON scenarios(status);
CREATE INDEX IF NOT EXISTS idx_simulations_scenario_id ON simulations(scenario_id);
CREATE INDEX IF NOT EXISTS idx_assets_org_id ON assets(org_id);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type);
CREATE INDEX IF NOT EXISTS idx_assets_embedding ON assets USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_reports_scenario_id ON reports(scenario_id);

-- Insert sample organization
INSERT INTO organizations (id, name, domain) 
VALUES ('00000000-0000-0000-0000-000000000001', 'Demo Organization', 'demo.com')
ON CONFLICT DO NOTHING;

-- Insert sample user
INSERT INTO users (id, email, password_hash, name, role, org_id)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'admin@demo.com',
    '$2b$10$rQZ8qNqZ8qNqZ8qNqZ8qNOe', -- placeholder hash
    'Demo Admin',
    'admin',
    '00000000-0000-0000-0000-000000000001'
) ON CONFLICT DO NOTHING;
