#!/bin/bash

# AI Risk Scenario Generator - Development Startup Script

set -e

echo "🚀 Starting AI Risk Scenario Generator Development Environment"

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Start infrastructure
echo "🐳 Starting local infrastructure..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose -f docker-compose.dev.yml ps

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing root dependencies..."
    npm install
fi

if [ ! -d "apps/frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd apps/frontend && npm install && cd ../..
fi

if [ ! -d "apps/backend/node_modules" ]; then
    echo "📦 Installing backend dependencies..."
    cd apps/backend && npm install && cd ../..
fi

if [ ! -d "apps/workers/.venv" ]; then
    echo "📦 Setting up Python virtual environment..."
    cd apps/workers
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cd ../..
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

echo "✅ Development environment setup complete!"
echo ""
echo "🌐 Access URLs:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:3001/api/docs"
echo "  Workers:   http://localhost:8000/docs"
echo "  Grafana:   http://localhost:3002 (admin/admin123)"
echo "  Prometheus: http://localhost:9090"
echo ""
echo "🚀 To start the development servers:"
echo "  npm run dev"
echo ""
echo "🛑 To stop infrastructure:"
echo "  docker-compose -f docker-compose.dev.yml down"
