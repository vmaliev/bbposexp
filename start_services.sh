#!/bin/bash
export $(grep -v '^#' ../.env | xargs)
export WEB_APP_URL="https://bedff81a7361.ngrok-free.app"

echo "Starting Server..."
nohup ./venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 60 > server.log 2>&1 &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"

echo "Starting Bot..."
nohup ./venv/bin/python3 telegram_bot.py > bot.log 2>&1 &
BOT_PID=$!
echo "Bot PID: $BOT_PID"

echo "Services started."