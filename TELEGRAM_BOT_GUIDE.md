# Telegram Bot Setup Guide 🤖

This guide will help you set up and run the Telegram bot for your Bybit Position Analysis Bot.

## Prerequisites ✅

1. Python 3.7+ installed
2. Virtual environment set up (from main README)
3. Bybit API credentials configured
4. A Telegram account

## Step 1: Create a Telegram Bot 🆕

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** with BotFather
3. **Send the command**: `/newbot`
4. **Choose a name** for your bot (e.g., "My Bybit Analysis Bot")
5. **Choose a username** for your bot (must end in 'bot', e.g., "mybybit_analysis_bot")
6. **Copy the token** that BotFather gives you (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Configure the Bot Token 🔑

Add your Telegram bot token to the `.env` file:

```bash
# Open .env file
nano .env

# Add this line (replace with your actual token)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

Your `.env` file should now look like this:

```bash
# Bybit API Credentials (Required)
BYBIT_API_KEY=your_api_key_here
BYBIT_API_SECRET=your_api_secret_here

# Bybit API Base URL
BYBIT_BASE_URL=https://api-demo.bybit.com

# Gemini API Key
GEMINI_API_KEY=your_gemini_key_here

# Telegram Bot Token
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

## Step 3: Run the Telegram Bot 🚀

```bash
# Activate virtual environment
source venv/bin/activate

# Or use the full path
./venv/bin/python3 telegram_bot.py
```

You should see:
```
INFO - Starting Telegram bot...
```

## Step 4: Use the Bot 📱

1. **Find your bot** in Telegram (search for the username you created)
2. **Start the bot** by clicking "Start" or sending `/start`
3. **Use the interactive menu** or commands:

### Available Commands:

- `/start` - Start the bot and show interactive menu
- `/list` - List all open positions
- `/orders` - List all open orders (limit, SL, TP)
- `/analyze` - Analyze positions with AI insights
- `/help` - Show help message

### Interactive Buttons:

The bot provides an easy-to-use button interface:
- 📊 **List Positions** - View all your open positions
- 📋 **List Orders** - View all your open orders
- 🔍 **Analyze** - Get AI-powered analysis and suggestions
- ❓ **Help** - Show help information

## Features 🌟

### Position Listing
- Real-time position data from Bybit
- Entry price, mark price, and leverage
- Unrealized PnL for each position
- Total portfolio value and PnL

### Order Tracking
- All open limit orders
- Stop-loss and take-profit orders
- Order details (price, quantity, type)

### AI Analysis
- Portfolio risk assessment
- High-risk position alerts
- Actionable suggestions (urgent, recommended, optional)
- Exposure and bias analysis

## Security Tips 🔒

1. **Keep your bot token private** - Never share it publicly
2. **Use read-only API keys** - Your Bybit API keys should only have read permissions
3. **Restrict bot access** - Only you should have access to your bot
4. **Monitor usage** - Check who's using your bot regularly

## Troubleshooting 🔧

### Bot doesn't respond
- Check that the bot is running (`./venv/bin/python3 telegram_bot.py`)
- Verify your `TELEGRAM_BOT_TOKEN` is correct in `.env`
- Make sure you've started the bot with `/start` in Telegram

### "Configuration error: BYBIT_API_KEY environment variable is not set"
- Ensure your `.env` file has all required variables
- Check that you're running the bot from the correct directory

### "Error fetching positions"
- Verify your Bybit API credentials are correct
- Check that the API key has read permissions
- Ensure you're using the correct `BYBIT_BASE_URL` (mainnet/testnet/demo)

### Bot stops after some time
- Use a process manager like `systemd`, `supervisor`, or `pm2` for production
- Or run in a `screen` or `tmux` session

## Running in Background 🔄

### Using screen (simple method):

```bash
# Install screen if not available
sudo apt-get install screen

# Create a new screen session
screen -S telegram_bot

# Run the bot
./venv/bin/python3 telegram_bot.py

# Detach from screen: Press Ctrl+A, then D
# Reattach to screen: screen -r telegram_bot
```

### Using systemd (production method):

Create a service file `/etc/systemd/system/bybit-telegram-bot.service`:

```ini
[Unit]
Description=Bybit Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/bbposexp
Environment="PATH=/path/to/bbposexp/venv/bin"
ExecStart=/path/to/bbposexp/venv/bin/python3 telegram_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable bybit-telegram-bot
sudo systemctl start bybit-telegram-bot
sudo systemctl status bybit-telegram-bot
```

## Example Usage 📸

### Starting the bot:
```
User: /start
Bot: 👋 Welcome @username!

🤖 Bybit Position Analysis Bot

I can help you monitor and analyze your Bybit positions.

[📊 List Positions] [📋 List Orders]
[🔍 Analyze] [❓ Help]
```

### Listing positions:
```
User: /list
Bot: 📡 Fetching positions from Bybit...

📋 Bybit Positions List
==================================================

✅ Found 5 open position(s)

📈 BTCUSDT (Buy)
  Size: 0.0020 | Entry: $96,845.23
  Mark: $83,724.48 | Lev: 3.0x
  🔴 PnL: $-26.24

...

💰 Total Value: $1,176.37 USDT
💰 Total PnL: $-121.59 USDT
```

### Analyzing positions:
```
User: /analyze
Bot: 🔍 Analyzing positions...

🔍 Position Analysis
==================================================

📊 Portfolio Summary
Long Exposure: $650.00
Short Exposure: $526.37
Net Exposure: $123.63
Total PnL: $-121.59
Bias: LONG
Positions: 44

⚠️ High Risk Positions (2)
• ZKUSDT (Buy)
  Lev: 10.0x | Liq: 13.36%

💡 Suggestions

🔴 URGENT:
• Reduce leverage on high-risk positions
• Add collateral to positions near liquidation

🟡 RECOMMENDED:
• Diversify portfolio across different clusters
• Set stop-loss orders for protection
```

## Support 💬

For issues or questions:
1. Check this guide and the main README
2. Verify all configuration settings
3. Check the bot logs for error messages

---

**Happy Trading! 📈**
