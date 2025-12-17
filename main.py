# main.py
# Multi-symbol UT Bot futures bot (1m, compounding, SOL/BTC/ETH by default)

import time
import logging

from config.settings import *
from config.secrets import API_KEY, API_SECRET

from core.binance_client import get_client
from core.data_loader import get_klines_df
from core.position_manager import get_position
from core.trade_executor import open_long, open_short, close_all

from strategy.signals import compute_signals
from utils.logger import setup_logger
from utils.helpers import round_step


def get_client_wrapped():
    client = get_client()
    try:
        client.session.keep_alive = True
    except Exception:
        pass
    try:
        client._request_params = {"timeout": 30}
    except Exception:
        pass
    return client


def get_usdt_balance(client) -> float:
    for _ in range(5):
        try:
            bals = client.futures_account_balance()
            for b in bals:
                if b.get("asset") == "USDT":
                    return float(b.get("balance", 0.0))
        except Exception as e:
            logging.info("Balance retry: %s", e)
            time.sleep(1)
    return 0.0


def get_price(client, symbol: str) -> float:
    for _ in range(6):
        try:
            t = client.futures_symbol_ticker(symbol=symbol)
            return float(t["price"])
        except Exception as e:
            logging.info("Price retry: %s", e)
            time.sleep(1)
    raise RuntimeError("Failed to fetch price")


def get_symbol_filters(client, symbol: str) -> dict:
    info = client.futures_exchange_info()
    for s in info.get("symbols", []):
        if s.get("symbol") == symbol:
            return s
    raise RuntimeError(f"Symbol info for {symbol} not found")


def safe_calculate_qty(client, symbol: str, leverage: int) -> float:
    balance = get_usdt_balance(client)
    if balance <= 0:
        return 0.0

    price = get_price(client, symbol)

    max_by_margin = (balance * leverage) / price
    max_by_margin *= 0.97  # safety margin

    sf = get_symbol_filters(client, symbol)
    step = 0.001
    min_qty = 0.0
    min_notional = 5.0

    for f in sf.get("filters", []):
        if f.get("filterType") == "LOT_SIZE":
            step = float(f.get("stepSize", step))
            min_qty = float(f.get("minQty", min_qty))
        if f.get("filterType") in ("MIN_NOTIONAL", "NOTIONAL"):
            v = f.get("minNotional") or f.get("notional") or None
            if v:
                try:
                    min_notional = float(v)
                except Exception:
                    pass

    qty = round_step(max_by_margin, step)

    if qty * price < min_notional:
        qty = round_step(min_notional / price + 1e-12, step)

    if qty < min_qty:
        qty = min_qty

    if qty > max_by_margin:
        qty = round_step(max_by_margin, step)

    if qty < min_qty or qty <= 0:
        return 0.0

    return float(qty)


def fetch_klines_with_retry(client, symbol, interval, limit=300, retries=6):
    for i in range(retries):
        try:
            return get_klines_df(client, symbol, interval, limit=limit)
        except Exception as e:
            logging.info("[%s] Klines fetch failed (attempt %d/%d): %s", symbol, i + 1, retries, e)
            time.sleep(min(2 + i * 1, 6))
    raise RuntimeError(f"Failed to fetch klines for {symbol} after retries")


def set_leverage_safe(client, symbol: str):
    try:
        r = client.futures_change_leverage(symbol=symbol, leverage=LEVERAGE)
        logging.info("[%s] Leverage set: %s", symbol, r)
    except Exception as e:
        logging.info("[%s] Could not set leverage: %s", symbol, e)


def trade_symbol(client, symbol, last_bar_time_map):
    """Handle one symbol: fetch candles, compute signal, manage position and orders."""
    try:
        df = fetch_klines_with_retry(client, symbol, INTERVAL, limit=300, retries=6)
    except Exception as e:
        logging.info("[%s] Critical: failed to fetch klines: %s", symbol, e)
        return last_bar_time_map.get(symbol)

    if len(df) < 60:
        logging.info("[%s] Waiting for more historic candles...", symbol)
        return last_bar_time_map.get(symbol)

    closed_time = df["open_time"].iloc[-2]
    if last_bar_time_map.get(symbol) == closed_time:
        return last_bar_time_map.get(symbol)

    # new bar
    last_bar_time_map[symbol] = closed_time

    try:
        long_signal, short_signal = compute_signals(df)
    except Exception as e:
        logging.info("[%s] Signal computation error: %s", symbol, e)
        return last_bar_time_map.get(symbol)

    try:
        pos_side, pos_qty = get_position(client, symbol)
    except Exception as e:
        logging.info("[%s] Position fetch error: %s", symbol, e)
        pos_side, pos_qty = "FLAT", 0.0

    try:
        balance = get_usdt_balance(client)
    except Exception:
        balance = 0.0

    try:
        price = get_price(client, symbol)
    except Exception as e:
        logging.info("[%s] Price fetch error: %s", symbol, e)
        price = None

    logging.info(
        "[%s] [BAR CLOSED] price=%s pos=%s long=%s short=%s balance=%.6f",
        symbol, price, pos_side, long_signal, short_signal, balance
    )

    # Long logic
    if long_signal:
        logging.info("[%s] Long signal detected", symbol)
        if pos_side == "SHORT" and pos_qty > 0:
            logging.info("[%s] Closing existing SHORT first (qty=%s)", symbol, pos_qty)
            try:
                close_all(client, symbol, pos_side, pos_qty)
            except Exception as e:
                logging.info("[%s] Error closing short: %s", symbol, e)
                time.sleep(1)
                try:
                    close_all(client, symbol, pos_side, pos_qty)
                except Exception as e2:
                    logging.info("[%s] Second close attempt failed: %s", symbol, e2)
                    return last_bar_time_map.get(symbol)
            time.sleep(1.2)

        qty = safe_calculate_qty(client, symbol, LEVERAGE)
        if qty <= 0:
            logging.info("[%s] Calculated qty zero or below min -> skipping LONG", symbol)
        else:
            logging.info("[%s] Opening LONG qty=%.6f", symbol, qty)
            try:
                open_long(client, symbol, qty, balance, TAKE_PROFIT_PCT)
            except Exception as e:
                logging.info("[%s] Error opening long: %s", symbol, e)

    # Short logic
    if short_signal:
        logging.info("[%s] Short signal detected", symbol)
        if pos_side == "LONG" and pos_qty > 0:
            logging.info("[%s] Closing existing LONG first (qty=%s)", symbol, pos_qty)
            try:
                close_all(client, symbol, pos_side, pos_qty)
            except Exception as e:
                logging.info("[%s] Error closing long: %s", symbol, e)
                time.sleep(1)
                try:
                    close_all(client, symbol, pos_side, pos_qty)
                except Exception as e2:
                    logging.info("[%s] Second close attempt failed: %s", symbol, e2)
                    return last_bar_time_map.get(symbol)
            time.sleep(1.2)

        qty = safe_calculate_qty(client, symbol, LEVERAGE)
        if qty <= 0:
            logging.info("[%s] Calculated qty zero or below min -> skipping SHORT", symbol)
        else:
            logging.info("[%s] Opening SHORT qty=%.6f", symbol, qty)
            try:
                open_short(client, symbol, qty, balance, TAKE_PROFIT_PCT)
            except Exception as e:
                logging.info("[%s] Error opening short: %s", symbol, e)

    return last_bar_time_map.get(symbol)


def main():
    setup_logger()
    logging.info("Starting bot_02 - multi-symbol UT Bot (%s) - Compounding Mode", INTERVAL)
    logging.info("Symbols: %s", SYMBOLS)

    client = get_client_wrapped()

    # set leverage per symbol
    for sym in SYMBOLS:
        set_leverage_safe(client, sym)

    last_bar_time_map = {}

    while True:
        try:
            for sym in SYMBOLS:
                last_bar_time_map.setdefault(sym, None)
                last_bar_time_map[sym] = trade_symbol(client, sym, last_bar_time_map)
        except Exception as err:
            logging.info("❗ Main loop error: %s", err)
            time.sleep(5)
            continue

        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
