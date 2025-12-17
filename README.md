# UT BOT Trading Bot - Cloud Ready

Multi-symbol UT Bot futures trading bot with 1H timeframe, 5% take-profit targeting, and compounding.

## Features
- 1H interval trading (1 hourly candle = 1 signal)
- Automatic 5% account balance take-profit per trade
- Multi-symbol support (configurable)
- Heikin Ashi candle filtering
- Auto-leverage setting
- Error handling & reconnection logic

## Quick Start (Local)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
# Edit config/secrets.py with your Binance Futures API keys

# Run bot
python main.py
```

## Cloud Deployment

See **CLOUD_DEPLOYMENT.md** for detailed instructions on:
- AWS EC2
- Google Cloud Run
- Azure Container Instances
- Heroku
- DigitalOcean

## Configuration (config/settings.py)

```python
SYMBOLS = ["SOLUSDT"]       # Trading pairs
INTERVAL = "30m"            # Candle interval (15m, 30m, 1h, etc)
LEVERAGE = 10               # Futures leverage (high risk!)
TAKE_PROFIT_PCT = 0.05      # 5% profit target per trade
ATR_PERIOD = 10             # UT Bot ATR period
SLEEP_SECONDS = 10          # Loop sleep time
```

## API Keys (config/secrets.py)

```python
API_KEY = "your_binance_futures_api_key"
API_SECRET = "your_binance_futures_api_secret"
```

⚠️ Never commit `config/secrets.py` to Git!

## Docker

```bash
# Build image
docker build -t ut-bot .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f ut-bot
```

## Monitoring

```bash
# View trades
tail -f trades.log

# View errors
docker-compose logs -f ut-bot --tail 100
```

## Strategy

- **Signal**: UT Bot (Chandelier Exit style)
- **Entry**: Market order at signal bar close
- **Exit**: TAKE_PROFIT_MARKET order at calculated TP price
- **TP Calculation**: `TP_price = entry_price ± (balance * 0.05 / qty)`
- **Compounding**: Uses 100% available balance per signal

## Risk Warning

⚠️ This bot trades with high leverage and real money. Test thoroughly before running live. Start with small capital.

## Support

Check logs for errors:
```bash
docker-compose logs -f ut-bot
```

For API issues, verify:
- API keys are correct
- IP is whitelisted on Binance
- Account has futures enabled
- Sufficient balance
