import os
from config import settings

def get_client():
    exchange = os.getenv("EXCHANGE") or getattr(settings, 'EXCHANGE', 'binance')
    exchange = exchange.lower()
    if exchange in ("binance",):
        from core.binance_client import get_client as _get
        return _get()
    if exchange in ("bybit",):
        from core.bybit_client import get_client as _get
        return _get()
    raise RuntimeError(f"Unsupported exchange: {exchange}")
