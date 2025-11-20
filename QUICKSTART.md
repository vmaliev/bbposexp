# Quick Start Guide

## 🚀 Run the Bot

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Set your API credentials
export BYBIT_API_KEY="your_key_here"
export BYBIT_API_SECRET="your_secret_here"

# 3. (Optional) Add OpenAI for AI analysis
export OPENAI_API_KEY="your_openai_key"

# 4. Run analysis
python bot.py analyze
```

## 📝 First Time Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Then edit .env with your credentials
```

## 🔑 Get Bybit API Keys

1. Go to https://www.bybit.com
2. Account & Security → API Management
3. Create API key with **Read** permissions only
4. Save your key and secret

## 💡 Tips

- **Read-only API key is sufficient** - no trading permissions needed
- **OpenAI is optional** - bot works with rule-based analysis too
- **Use testnet first** - set `BYBIT_BASE_URL=https://api-testnet.bybit.com`
- **Virtual environment** - always activate before running

## 📊 What You'll Get

- Portfolio summary (long/short exposure, bias)
- Risk analysis per position (leverage, liquidation distance)
- Cluster distribution (BTC, ETH, L2, Meme, AI)
- Actionable suggestions (urgent, recommended, optional)

## ❓ Troubleshooting

**"Configuration Error: BYBIT_API_KEY not set"**
→ Export your environment variables first

**"No module named 'requests'"**
→ Activate virtual environment: `source venv/bin/activate`

**"Invalid API key"**
→ Check your credentials and API permissions

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.
