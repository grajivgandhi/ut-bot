def get_position(client, symbol):
    """Return (side, qty): side in {'LONG','SHORT','FLAT'} for a symbol."""
    pos_info = client.futures_position_information(symbol=symbol)
    for p in pos_info:
        amt = float(p.get("positionAmt", 0.0))
        if amt > 0:
            return "LONG", amt
        elif amt < 0:
            return "SHORT", abs(amt)
    return "FLAT", 0.0
