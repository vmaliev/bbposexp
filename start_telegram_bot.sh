#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Start the web server in the background
echo "Starting web server..."
./venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Start the Telegram bot in the foreground
echo "Starting Telegram bot..."
./venv/bin/python3 telegram_bot.py

# Clean up the server process when the bot is stopped
kill $SERVER_PID