
from binance.enums import SIDE_BUY, SIDE_SELL, FUTURE_ORDER_TYPE_MARKET
import math


def _get_price_tick(client, symbol: str) -> float:
    """Return the tick size (price filter) for a symbol or 0.01 as fallback."""
    try:
        info = client.futures_exchange_info()
        for s in info.get("symbols", []):
            if s.get("symbol") == symbol:
                for f in s.get("filters", []):
                    if f.get("filterType") == "PRICE_FILTER":
                        return float(f.get("tickSize", 0.01))
    except Exception:
        pass
    return 0.01


def _round_price(price: float, tick: float, direction: str = "nearest") -> float:
    if tick <= 0:
        return price
    q = price / tick
    if direction == "up":
        q = math.ceil(q)
    elif direction == "down":
        q = math.floor(q)
    else:
        q = round(q)
    return q * tick


def open_long(client, symbol, qty, balance, tp_pct: float = 0.05):
    """Open a market long and place a take-profit that targets `tp_pct` of account balance.

    - qty: contract quantity (in base units)
    - balance: USDT account balance (float)
    - tp_pct: target profit as fraction of balance (default 0.05 = 5%)
    """
    # place market entry
    resp = client.futures_create_order(
        symbol=symbol,
        side=SIDE_BUY,
        type=FUTURE_ORDER_TYPE_MARKET,
        quantity=qty
    )

    # approximate entry price with latest ticker (market fill price may vary)
    try:
        entry_price = float(client.futures_symbol_ticker(symbol=symbol)["price"])
    except Exception:
        entry_price = None

    # place take-profit market order to close position when profit target hit
    try:
        if entry_price and qty > 0 and balance > 0:
            target_profit = float(balance) * float(tp_pct)
            # For linear perpetuals: profit = (tp_price - entry_price) * qty
            tp_price = entry_price + (target_profit / qty)

            tick = _get_price_tick(client, symbol)
            tp_price = _round_price(tp_price, tick, direction="up")

            # place TAKE_PROFIT_MARKET to close the position
            client.futures_create_order(
                symbol=symbol,
                side=SIDE_SELL,
                type="TAKE_PROFIT_MARKET",
                stopPrice=str(tp_price),
                closePosition=True
            )
    except Exception:
        pass

    return resp


def open_short(client, symbol, qty, balance, tp_pct: float = 0.05):
    """Open a market short and place a take-profit that targets `tp_pct` of account balance."""
    resp = client.futures_create_order(
        symbol=symbol,
        side=SIDE_SELL,
        type=FUTURE_ORDER_TYPE_MARKET,
        quantity=qty
    )

    try:
        entry_price = float(client.futures_symbol_ticker(symbol=symbol)["price"])
    except Exception:
        entry_price = None

    try:
        if entry_price and qty > 0 and balance > 0:
            target_profit = float(balance) * float(tp_pct)
            tp_price = entry_price - (target_profit / qty)
            tick = _get_price_tick(client, symbol)
            tp_price = _round_price(tp_price, tick, direction="down")

            client.futures_create_order(
                symbol=symbol,
                side=SIDE_BUY,
                type="TAKE_PROFIT_MARKET",
                stopPrice=str(tp_price),
                closePosition=True
            )
    except Exception:
        pass

    return resp


def close_all(client, symbol, side, qty):
    """Close position on a symbol by side with reduceOnly market order."""
    if qty <= 0:
        return None
    if side == "LONG":
        order_side = SIDE_SELL
    elif side == "SHORT":
        order_side = SIDE_BUY
    else:
        return None
    return client.futures_create_order(
        symbol=symbol,
        side=order_side,
        type=FUTURE_ORDER_TYPE_MARKET,
        quantity=qty,
        reduceOnly=True
    )
