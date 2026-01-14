#!/bin/bash

# muuh WhatsApp Chatbot - Quick Start Setup Script

echo "================================================"
echo "  muuh WhatsApp Recruiting Chatbot - Setup"
echo "================================================"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python $python_version detected"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
echo "   ✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "   ✅ Dependencies installed"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "   ✅ .env file created"
    echo ""
    echo "   ⚠️  IMPORTANT: Edit .env and add your API credentials!"
    echo "   You need:"
    echo "   - OPENAI_API_KEY (from platform.openai.com)"
    echo "   - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Initialize database
echo "🗄️  Initializing database..."
python scripts/setup_db.py
echo ""

# Success message
echo "================================================"
echo "  ✅ Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API credentials"
echo "2. Run: python scripts/test_conversation.py (test locally)"
echo "3. Run: python -m uvicorn app.main:app --reload (start server)"
echo ""
echo "For deployment, see: DEPLOYMENT.md"
echo ""
