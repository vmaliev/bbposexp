# 🤖 Telegram Bot Quick Start

## 1️⃣ Get Your Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the prompts to create your bot
4. **Copy the token** (looks like: `123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

## 2️⃣ Add Token to .env File

Open your `.env` file and add:
```bash
TELEGRAM_BOT_TOKEN=your_token_here
```

## 3️⃣ Start the Bot

```bash
./start_telegram_bot.sh
```

Or manually:
```bash
./venv/bin/python3 telegram_bot.py
```

## 4️⃣ Use Your Bot

1. Find your bot in Telegram (search for the username you created)
2. Click **Start** or send `/start`
3. Use the interactive buttons or commands:
   - `/list` - List positions
   - `/orders` - List orders
   - `/analyze` - AI analysis
   - `/help` - Help

## 📋 Current Configuration

Your `.env` file should have:
- ✅ `BYBIT_API_KEY` - Your Bybit API key
- ✅ `BYBIT_API_SECRET` - Your Bybit API secret
- ✅ `BYBIT_BASE_URL` - Currently set to demo: `https://api-demo.bybit.com`
- ✅ `GEMINI_API_KEY` - For AI analysis
- ⚠️ `TELEGRAM_BOT_TOKEN` - **You need to add this!**

## 🔧 Troubleshooting

**Bot doesn't start?**
- Check that `TELEGRAM_BOT_TOKEN` is set in `.env`
- Verify the token is correct (no extra spaces)

**Bot doesn't respond?**
- Make sure the bot is running
- Check you've sent `/start` to the bot first

**Can't fetch positions?**
- Verify your Bybit API credentials
- Check that you're using the correct API URL

## 📚 More Info

See `TELEGRAM_BOT_GUIDE.md` for detailed setup instructions and features.

---

**Need help?** Check the logs when running the bot for error messages.
