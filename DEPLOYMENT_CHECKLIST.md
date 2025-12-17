# Heroku Deployment Checklist

## Pre-Deployment ✅

- [x] Bot code syntax verified (no errors)
- [x] All dependencies in requirements.txt
  - python-binance
  - pandas
  - numpy
  - ta
- [x] Dockerfile ready for containerization
- [x] Procfile configured (worker: python main.py)
- [x] runtime.txt set to python-3.10.12
- [x] config/secrets.py reads from environment variables
- [x] .gitignore prevents committing secrets

## Deployment Steps ✅

### 1. GitHub Setup
- [ ] Create GitHub account (github.com)
- [ ] Create new repository "ut-bot"
- [ ] Push code to GitHub main branch

### 2. Heroku Setup
- [ ] Install Heroku CLI (https://devcenter.heroku.com/articles/heroku-cli)
- [ ] Create Heroku account (heroku.com)
- [ ] Login: `heroku login`
- [ ] Create app: `heroku create your-app-name`

### 3. Environment Variables
- [ ] Generate NEW Binance API keys (NOT the old exposed ones!)
  - Go to Binance > Account > API Management
  - Delete old keys first
  - Create new keys with:
    - Futures trading enabled
    - Read-only: OFF (need to place orders)
    - Withdrawal: OFF (security)
    - IP Restriction: Optional (leave empty for testing)
- [ ] Set keys in Heroku:
  ```bash
  heroku config:set API_KEY=your_new_key
  heroku config:set API_SECRET=your_new_secret
  ```

### 4. Deploy Code
- [ ] Connect GitHub to Heroku (or use git push)
- [ ] Deploy: `git push heroku main`
- [ ] Watch logs: `heroku logs --tail`

### 5. Start Bot
- [ ] Start worker: `heroku ps:scale worker=1`
- [ ] Verify running: `heroku ps`
- [ ] Should show: `worker.1 up`

## Post-Deployment ✅

### Monitoring
- [ ] Check logs daily: `heroku logs --tail`
- [ ] Monitor trade execution
- [ ] Verify no API errors
- [ ] Check Binance account for orders

### Security
- [ ] ✅ Deleted old API keys from Binance
- [ ] ✅ New API keys have minimal permissions
- [ ] ✅ Never committed secrets to Git
- [ ] ✅ All sensitive data in Heroku Config Vars
- [ ] IP restrictions set on Binance API (optional)

### Testing
- [ ] Bot connects to Binance API
- [ ] Fetches candles successfully
- [ ] Computes signals correctly
- [ ] Places test orders (if capital available)
- [ ] Take-profit orders work

## Troubleshooting Quick Guide

| Issue | Solution |
|-------|----------|
| Bot won't start | Check logs: `heroku logs --tail` |
| API key error | Verify key in `heroku config` |
| No orders placed | Check balance > 0 USDT |
| Bot crashes | Increase dyno memory (paid) |
| Need to update code | `git push heroku main` |

## Cost Estimate

| Item | Cost |
|------|------|
| Heroku Eco Dyno | $7/month |
| Binance API | Free |
| **Total** | **$7/month** |

## Important Reminders

⚠️ **Security Critical**
- Your old API keys (from screenshots in code) are exposed!
- IMMEDIATELY deactivate them on Binance
- Generate new keys
- Use new keys with Heroku

⚠️ **Trading Risk**
- High leverage (10x) = high risk
- Start with small capital ($100-500)
- Test thoroughly before scaling
- Monitor daily

✅ **Daily Maintenance**
- Check logs: `heroku logs --tail`
- Verify Binance account for trades
- Monitor balance changes
- Watch for errors

## Commands Reference

```bash
# Deploy/update
git push heroku main

# Logs
heroku logs --tail              # Live logs
heroku logs --num=100           # Last 100 lines
heroku logs --grep ERROR        # Errors only

# Status
heroku ps                        # Check if running
heroku config                    # View env vars

# Control
heroku ps:scale worker=1         # Start bot
heroku ps:scale worker=0         # Stop bot
heroku restart                   # Restart bot

# Help
heroku help
heroku help deploy
```

## Success Indicators

✅ Bot is running when:
- `heroku ps` shows `worker.1 up`
- `heroku logs --tail` shows "Starting bot_02 - multi-symbol UT Bot (30m) - Compounding Mode"
- No API errors in logs
- Binance shows new orders appearing

---

**Status**: Ready to deploy to Heroku! 🚀
