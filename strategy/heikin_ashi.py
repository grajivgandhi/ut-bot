import pandas as pd


def heikin(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Heikin Ashi candles and add ha_open/ha_close columns."""
    ha = df.copy()

    ha_close = (df["open"] + df["high"] + df["low"] + df["close"]) / 4.0

    ha_open = ha_close.copy()
    ha_open.iloc[0] = (df["open"].iloc[0] + df["close"].iloc[0]) / 2.0

    for i in range(1, len(df)):
        ha_open.iloc[i] = (ha_open.iloc[i - 1] + ha_close.iloc[i - 1]) / 2.0

    ha["ha_close"] = ha_close
    ha["ha_open"] = ha_open
    return ha
