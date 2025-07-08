#!/bin/bash

# Start the Protein Intake Agent application
echo "🚀 Starting Protein Intake Agent..."

# Check if .env file exists
if [ ! -f "./backend/.env" ]; then
    echo "⚠️  .env file not found in backend directory"
    echo "📝 Please copy .env.example to .env and configure your API keys"
    echo "   cd backend && cp .env.example .env"
    exit 1
fi

# Load environment variables
source ./backend/.env

# Check if required environment variables are set
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OPENAI_API_KEY not configured in backend/.env"
    echo "📝 Please set your OpenAI API key in backend/.env"
    exit 1
fi

echo "✅ Environment configured"

# Start services with Docker Compose
echo "🐳 Starting services with Docker Compose..."
docker-compose up --build

echo "🎉 Protein Intake Agent started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"