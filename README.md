# Bybit Position Analysis Bot 🤖

A Python CLI tool that analyzes your Bybit USDT perpetual futures positions, computes comprehensive risk metrics, and provides AI-enhanced actionable insights.

## Features ✨

- **Real-time Position Fetching**: Connects to Bybit v5 API with signed authentication
- **Comprehensive Risk Analysis**:
  - Liquidation distance calculation
  - Leverage risk scoring (safe/medium/high)
  - PnL status per position
  - Exposure analysis
  - Symbol clustering (BTC, ETH, L2, Meme, AI)
- **Portfolio Metrics**:
  - Long/short exposure breakdown
  - Portfolio bias detection
  - Cluster concentration analysis
  - Risk scoring
- **AI-Enhanced Suggestions**: Optional OpenAI integration for intelligent recommendations
- **Clean Console Output**: Color-coded risk levels and formatted reports

## Installation 📦

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure API credentials**:

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```bash
BYBIT_API_KEY=your_actual_api_key
BYBIT_API_SECRET=your_actual_api_secret
OPENAI_API_KEY=your_openai_key_optional
```

5. **Load environment variables**:
```bash
# On macOS/Linux
source .env

# Or export manually
export BYBIT_API_KEY="your_key"
export BYBIT_API_SECRET="your_secret"
```


## Usage 🚀

### Activate Virtual Environment

Before running the bot, activate your virtual environment:
```bash
source venv/bin/activate  # On macOS/Linux
# On Windows: venv\Scripts\activate
```

### Analyze Positions

```bash
python bot.py analyze
```


This will:
1. Fetch all your open USDT perpetual positions from Bybit
2. Compute risk metrics for each position
3. Analyze portfolio-level metrics
4. Generate AI-enhanced suggestions (if OpenAI configured)
5. Display a comprehensive report

### Example Output

```
🤖 Bybit Position Analysis Bot
============================================================
✅ OpenAI API configured - AI analysis enabled

📡 Fetching positions from Bybit...
✅ Found 5 open position(s)
🔍 Analyzing positions...
🧠 Generating suggestions...

============================================================
                    PORTFOLIO SUMMARY
============================================================

Long Exposure:  $12,450.00 USDT
Short Exposure: $8,320.00 USDT
Net Exposure:   $4,130.00 USDT
Total PnL:      $342.50 USDT
Bias:           LONG
Total Positions: 5

Cluster Distribution:
  BTC      35.20%
  ETH      28.10%
  L2       22.40%
  MEME     14.30%

============================================================
                     POSITION RISKS
============================================================

🔴 [HIGH RISK] BTCUSDT (LONG)
  Size: 0.5000 | Entry: $42,150.00 | Mark: $43,200.00
  Leverage: 12.5x | Liq Price: $39,800.00
  Distance to Liquidation: 7.87%
  PnL: +$525.00 (profit)
  Exposure: $21,600.00 USDT | Cluster: BTC
  ⚠️  HIGH RISK: High leverage + close to liquidation!

🟡 [MEDIUM RISK] ETHUSDT (SHORT)
  Size: 5.0000 | Entry: $2,250.00 | Mark: $2,180.00
  Leverage: 8.0x | Liq Price: $2,420.00
  Distance to Liquidation: 11.01%
  PnL: +$350.00 (profit)
  Exposure: $10,900.00 USDT | Cluster: ETH

============================================================
                 ACTIONABLE SUGGESTIONS
============================================================

🔴 URGENT:
  - Add collateral or reduce BTCUSDT LONG position (7.87% from liquidation)
  - Reduce leverage on BTCUSDT (currently 12.5x)

🟡 RECOMMENDED:
  - Consider taking partial profits on 3 profitable position(s)
  - Diversify away from BTC cluster (35.2% of portfolio)

🟢 OPTIONAL:
  - Set tighter stop losses on high-leverage positions
  - Review losing positions for potential exit

============================================================
✅ Analysis complete!
============================================================
```

## Bybit API Requirements 🔑

### API Permissions Needed

When creating your Bybit API key, ensure you enable:
- ✅ **Read** permission for Position data
- ❌ **No trading permissions required** (read-only is safe)

### Getting API Credentials

1. Log in to [Bybit](https://www.bybit.com)
2. Go to **Account & Security** → **API Management**
3. Create a new API key
4. Enable **Read** permissions for positions
5. Save your API key and secret securely

### Testnet Support

To use Bybit testnet for testing:
```bash
export BYBIT_BASE_URL="https://api-testnet.bybit.com"
```

## Configuration Options ⚙️

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BYBIT_API_KEY` | ✅ Yes | Your Bybit API key |
| `BYBIT_API_SECRET` | ✅ Yes | Your Bybit API secret |
| `BYBIT_BASE_URL` | ❌ No | API base URL (default: mainnet) |
| `OPENAI_API_KEY` | ❌ No | OpenAI key for AI analysis |

### AI Analysis

- **With OpenAI**: Provides intelligent, context-aware suggestions using GPT-4
- **Without OpenAI**: Uses rule-based analysis with predefined risk criteria

Both modes are fully functional - AI just provides more nuanced insights.

## Architecture 🏗️

```
bot.py              # CLI entrypoint and orchestration
├── config.py       # Environment variable management
├── bybit_api.py    # Bybit v5 API client (signed requests)
├── analyzer.py     # Risk analysis engine
└── ai_analysis.py  # AI/rule-based suggestions
```

### Analysis Logic

**Position Metrics**:
- `liquidation_distance_pct` = `|mark_price - liq_price| / mark_price × 100`
- `leverage_risk` = safe (<5x), medium (5-10x), high (>10x)
- `exposure` = `|size × mark_price|` in USDT
- `cluster` = Symbol categorization

**Portfolio Metrics**:
- Long/short exposure totals
- Bias calculation (60/40 threshold)
- Cluster concentration
- Risk scoring

## Troubleshooting 🔧

### "Configuration Error: BYBIT_API_KEY environment variable is not set"

Make sure you've exported your environment variables:
```bash
export BYBIT_API_KEY="your_key"
export BYBIT_API_SECRET="your_secret"
```

### "Bybit API error: Invalid API key"

- Verify your API key and secret are correct
- Check that the API key has read permissions for positions
- Ensure you're using the correct base URL (mainnet vs testnet)

### "API request failed: Connection timeout"

- Check your internet connection
- Verify Bybit API is accessible from your location
- Try increasing timeout in `bybit_api.py` if needed

### No positions found

- Ensure you have open USDT perpetual positions on Bybit
- Verify the API key has access to your trading account
- Check you're using the correct account (main vs sub-account)

## Security Notes 🔒

- **Never commit** your `.env` file or expose API credentials
- Use **read-only** API keys when possible
- Store credentials securely
- Rotate API keys periodically
- Use testnet for initial testing

## Dependencies 📚

- Python 3.7+
- `requests` - HTTP library for API calls

That's it! Minimal dependencies for maximum reliability.

## License

MIT License - feel free to modify and use as needed.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your API credentials and permissions
3. Review Bybit API documentation: https://bybit-exchange.github.io/docs/v5/intro

---

**Happy Trading! 📈**
