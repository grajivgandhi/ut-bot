import pandas as pd


def get_klines_df(client, symbol, interval, limit=300):
    """Fetch futures klines and return as a cleaned pandas DataFrame."""
    raw = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(raw, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades",
        "taker_base", "taker_quote", "ignore"
    ])
    for col in ["open", "high", "low", "close", "volume", "quote_volume", "taker_base", "taker_quote"]:
        df[col] = df[col].astype(float)
    return df
