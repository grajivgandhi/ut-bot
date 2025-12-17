SYMBOLS = ["SOLUSDT"]  # you can edit this list
INTERVAL = "1h"          # Bot timeframe: single interval set to 30 minutes

LEVERAGE = 10            # High risk for small accounts
USE_HEIKIN_ASHI = True   # Use Heikin Ashi as UT Bot source

ATR_PERIOD = 10          # UT Bot ATR period
KEY_VALUE = 1.0          # UT Bot sensitivity (a)

SLEEP_SECONDS = 10        # Loop sleep time in seconds

COMPOUNDING = True       # Use 100% capital each trade (per symbol when signal comes)
MIN_NOTIONAL = None      # Optional override, else Binance filter is used
TAKE_PROFIT_PCT = 0.05   # Fraction of account balance to target as TP per trade (5%)
