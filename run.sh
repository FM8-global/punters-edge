#!/bin/bash

set -e

echo "🏇 PunterEdge - Starting services..."
echo "====================================\n"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Start backend in background
echo -e "${BLUE}Starting Backend (http://localhost:8000)...${NC}"
cd backend
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
python main.py &
BACKEND_PID=$!
cd ..

sleep 2

# Start frontend in background
echo -e "${BLUE}Starting Frontend (http://localhost:3000)...${NC}"
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo -e "\n${GREEN}✅ Services started!${NC}"
echo -e "\n${BLUE}Backend:  http://localhost:8000${NC}"
echo -e "${BLUE}Frontend: http://localhost:3000${NC}"
echo -e "${BLUE}API Docs: http://localhost:8000/docs${NC}"

# Cleanup on exit
trap "echo '\\nShutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true" EXIT

# Wait for processes
wait
