#!/bin/bash

# Navigate to the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Set PYTHONPATH to include the current directory so python can find modules
export PYTHONPATH=$PYTHONPATH:$DIR

# Set WEB_APP_URL if it's provided as an environment variable (from parent script)
if [ -n "$WEB_APP_URL" ]; then
    export WEB_APP_URL
fi

# Start the Telegram bot in the background, redirecting output to a log file
echo "Starting Telegram bot in background..."
nohup ./venv/bin/python3 -u telegram_bot.py > ../bot_final.log 2>&1 &

echo "Telegram bot started."