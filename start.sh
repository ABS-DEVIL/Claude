#!/bin/bash

# ABS Stream Fucker - Start Script

echo "🔥 Starting ABS Stream Fucker... 🔥"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env from .env.example"
    exit 1
fi

# Load environment variables
export $(cat .env | xargs)

# Create downloads directory
mkdir -p downloads

# Start MongoDB (if not using Docker)
# mongod --dbpath ./data/db &

# Start Bot in background
echo "🤖 Starting Telegram Bot..."
python -m bot.main &
BOT_PID=$!

# Wait a bit for bot to start
sleep 3

# Start Web Server
echo "🌐 Starting Web Server..."
uvicorn web.app:app --host 0.0.0.0 --port ${WEB_PORT:-8000} &
WEB_PID=$!

echo ""
echo "✅ Bot started! PID: $BOT_PID"
echo "✅ Web server started! PID: $WEB_PID"
echo ""
echo "📺 Web UI: http://localhost:${WEB_PORT:-8000}"
echo "🤖 Bot: @${BOT_TOKEN%%:*}_bot"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for interrupt
trap "kill $BOT_PID $WEB_PID; exit" INT
wait
