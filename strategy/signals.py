from config.settings import USE_HEIKIN_ASHI, KEY_VALUE, ATR_PERIOD
from strategy.heikin_ashi import heikin
from strategy.ut_bot import ut_bot


def compute_signals(df):
    """Return (long_signal, short_signal) bools for the previous closed bar."""
    if USE_HEIKIN_ASHI:
        ha = heikin(df)
        src = ha["ha_close"]
    else:
        src = df["close"]

    long_series, short_series, _ = ut_bot(df, KEY_VALUE, ATR_PERIOD, src)

    # use second last (closed) candle
    ls = bool(long_series.iloc[-2])
    ss = bool(short_series.iloc[-2])
    return ls, ss
