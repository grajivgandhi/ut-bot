import pandas as pd
import ta


def ut_bot(df: pd.DataFrame, key: float, atr_period: int, src: pd.Series):
    """UT Bot core logic: ATR trailing stop + EMA(1) crossover."""
    atr = ta.volatility.average_true_range(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=atr_period
    )
    nLoss = atr * key

    trail = [src.iloc[0] - nLoss.iloc[0]]
    for i in range(1, len(src)):
        prev = trail[-1]
        s = src.iloc[i]
        sp = src.iloc[i - 1]
        nl = nLoss.iloc[i]

        if s > prev and sp > prev:
            trail.append(max(prev, s - nl))
        elif s < prev and sp < prev:
            trail.append(min(prev, s + nl))
        else:
            trail.append(s - nl if s > prev else s + nl)

    trail = pd.Series(trail, index=df.index)
    ema1 = src.ewm(span=1, adjust=False).mean()

    long_signal = (ema1.shift(1) <= trail.shift(1)) & (ema1 > trail)
    short_signal = (ema1.shift(1) >= trail.shift(1)) & (ema1 < trail)

    return long_signal, short_signal, trail
