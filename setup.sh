#!/bin/bash

set -e

echo "🏇 PunterEdge Setup"
echo "==================\n"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

echo "✅ Python and Node.js found"

# Backend setup
echo "\n📦 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
pip install -r requirements.txt

if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Created .env file. Please edit and add your PuntersEdge API key:"
    echo "    Edit: backend/.env"
fi

cd ..

# Frontend setup
echo "\n📦 Setting up frontend..."
cd frontend
if [ ! -d node_modules ]; then
    npm install
fi
cd ..

echo "\n✅ Setup complete!"
echo "\nNext steps:"
echo "1. Add your PuntersEdge API key to backend/.env"
echo "2. Run: ./run.sh"
echo "\nOr run components individually:"
echo "  Backend:  cd backend && python main.py"
echo "  CLI:      cd cli && python main.py today-bets --api-key YOUR_KEY"
echo "  Frontend: cd frontend && npm start"
