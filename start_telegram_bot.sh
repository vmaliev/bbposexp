#!/bin/bash
# Start the Telegram bot

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment and run the bot
cd "$DIR"
./venv/bin/python3 telegram_bot.py
