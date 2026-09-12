#!/bin/bash
# Manual PythonAnywhere app reload script
# Run this on PythonAnywhere bash console to pull latest code and reload

echo "🚀 PunterEdge Manual Reload"
echo "==========================="

# Step 1: Navigate to app directory
echo "📂 Navigating to app directory..."
cd ~/punters-edge

# Step 2: Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ Code pulled successfully"
else
    echo "❌ Failed to pull code"
    exit 1
fi

# Step 3: Reload PythonAnywhere app by touching WSGI file
echo "♻️  Reloading app by touching WSGI file..."
touch ~/.pythonanywhere/fm8global_pythonanywhere_com_wsgi.py

if [ $? -eq 0 ]; then
    echo "✅ WSGI file touched - app should reload in a few seconds"
else
    echo "⚠️  Touch failed, trying alternative WSGI path..."
    touch /home/FM8Global/punters-edge/backend/pythonanywhere_wsgi.py
fi

echo ""
echo "✅ Reload script complete!"
echo "Visit https://fm8global.pythonanywhere.com/outcomes to verify the fix"
