"""Lightweight demo script for Bybit testnet connectivity.

Usage: set env vars `API_KEY`, `API_SECRET` and `BYBIT_TESTNET=1`, then run:
    python -m core.bybit_demo

By default this only fetches ticker + balances. To place a sample market order on testnet,
set `BYBIT_PLACE_ORDER=1` (use with extreme caution).
"""
import os
import logging
from config import settings

from core.bybit_client import get_client


def run_demo():
    logging.basicConfig(level=logging.INFO)
    try:
        client = get_client()
    except Exception as e:
        print("Could not create client:", e)
        return

    sym = settings.SYMBOLS[0] if getattr(settings, 'SYMBOLS', None) else 'SOLUSDT'
    print(f"Using symbol: {sym}")

    try:
        ticker = client.futures_symbol_ticker(sym)
        print("Ticker:", ticker)
    except Exception as e:
        print("Ticker fetch failed:", e)

    try:
        bals = client.futures_account_balance()
        print("Balances (subset):", [b for b in bals if b.get('asset') in ('USDT', 'BTC', 'ETH')][:5])
    except Exception as e:
        print("Balance fetch failed:", e)

    place = os.getenv('BYBIT_PLACE_ORDER')
    if str(place).lower() in ('1', 'true', 'yes'):
        print("Placing a small market BUY order as demo (testnet)...")
        try:
            # WARNING: only for testnet. Using qty=0 may be rejected; require user to set BYBIT_DEMO_QTY.
            qty = float(os.getenv('BYBIT_DEMO_QTY') or 0)
            if qty <= 0:
                print('Set BYBIT_DEMO_QTY to a positive number to place an order. Skipping.')
                return
            resp = client.futures_create_order(symbol=sym, side='BUY', type='MARKET', quantity=qty)
            print('Order response:', resp)
        except Exception as e:
            print('Order failed:', e)


if __name__ == '__main__':
    run_demo()
