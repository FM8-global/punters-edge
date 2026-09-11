#!/bin/bash
# PunterEdge Deployment Script for PythonAnywhere
# Usage: bash deploy.sh
# This script handles: git pull + app reload automatically

set -e

USERNAME="fm8global"
DOMAIN="fm8global.pythonanywhere.com"
APP_DIR="$HOME/punters-edge"
TOKEN="86efc473848720d3d4714c8015a484326ba503c3"

echo "🚀 PunterEdge Deployment"
echo "========================"

# Step 1: Pull latest code
echo "📥 Pulling latest code from GitHub..."
cd "$APP_DIR"
git pull origin main
echo "✅ Code updated"

# Step 2: Try API reload (might not work, but worth trying)
echo "♻️  Attempting to reload via PythonAnywhere API..."
RELOAD_RESPONSE=$(curl -s -X POST \
  "https://www.pythonanywhere.com/api/user/$USERNAME/webapps/$DOMAIN/reload/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$RELOAD_RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ App reloaded successfully via API"
else
    echo "⚠️  API reload failed (code: $HTTP_CODE)"
    echo ""
    echo "📋 Fallback: Touch WSGI file to trigger reload"
    echo "Run this in PythonAnywhere bash console:"
    echo ""
    echo "  touch ~/.pythonanywhere/${USERNAME}_pythonanywhere_com_wsgi.py"
    echo ""
    echo "Or reload from Web tab in PythonAnywhere dashboard"
fi

echo ""
echo "✅ Deployment script complete"
echo "Visit: https://$DOMAIN to verify changes"
