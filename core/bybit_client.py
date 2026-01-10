import os
import logging
import ccxt


class BybitWrapper:
    def __init__(self, api_key, api_secret, testnet: bool = False):
        opts = {
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'future', 'adjustForTimeDifference': True}
        }
        if testnet:
            # Use Bybit testnet endpoint
            opts['urls'] = {'api': 'https://api-testnet.bybit.com'}
        self.exchange = ccxt.bybit(opts)

    def _to_ccxt_symbol(self, symbol: str) -> str:
        # Convert Binance-style SYMBOL like 'SOLUSDT' to 'SOL/USDT'
        if symbol.endswith('USDT'):
            return symbol[:-4] + '/USDT'
        if '/' not in symbol:
            # best-effort fallback
            return symbol
        return symbol

    def futures_create_order(self, symbol, side, type, quantity=None, stopPrice=None, closePosition=False, reduceOnly=False):
        sym = self._to_ccxt_symbol(symbol)
        side_s = side.lower() if isinstance(side, str) else side

        params = {}
        try:
            if type in ("MARKET", "FUTURE_ORDER_TYPE_MARKET"):
                return self.exchange.create_order(sym, 'market', side_s, quantity, None, params)

            # TAKE_PROFIT_MARKET handling: create a market order with stop params
            if type == "TAKE_PROFIT_MARKET" or type == "TAKE_PROFIT_MARKET":
                if stopPrice is not None:
                    params.update({'stopPrice': stopPrice, 'stop': True, 'reduce_only': True})
                # bybit/ccxt sometimes requires amount; using quantity or 0 to create a trigger
                amt = quantity or 0
                return self.exchange.create_order(sym, 'market', side_s, amt, None, params)

            # fallback to market
            return self.exchange.create_order(sym, 'market', side_s, quantity, None, params)
        except Exception as e:
            logging.info("Bybit create_order error: %s", e)
            raise

    def futures_symbol_ticker(self, symbol):
        sym = self._to_ccxt_symbol(symbol)
        t = self.exchange.fetch_ticker(sym)
        return {'price': str(t.get('last') or t.get('close') or 0)}

    def futures_exchange_info(self):
        markets = self.exchange.fetch_markets()
        symbols = []
        for m in markets:
            s = m.get('symbol')
            if not s:
                continue
            s_noslash = s.replace('/', '')
            precision = m.get('precision', {}) or {}
            price_prec = precision.get('price', 4)
            amount_prec = precision.get('amount', 3)
            tick = float(10 ** (-price_prec))
            step = float(10 ** (-amount_prec))
            symbols.append({
                'symbol': s_noslash,
                'filters': [
                    {'filterType': 'PRICE_FILTER', 'tickSize': str(tick)},
                    {'filterType': 'LOT_SIZE', 'stepSize': str(step), 'minQty': str(m.get('limits', {}).get('amount', {}).get('min', 0))}
                ]
            })
        return {'symbols': symbols}

    def futures_account_balance(self):
        bal = self.exchange.fetch_balance()
        res = []
        total = bal.get('total', {}) or {}
        for asset, amount in total.items():
            res.append({'asset': asset, 'balance': amount})
        return res

    def futures_change_leverage(self, symbol: str, leverage: int):
        try:
            # ccxt provides set_leverage in some implementations
            return self.exchange.set_leverage(leverage, self._to_ccxt_symbol(symbol))
        except Exception as e:
            logging.info("set_leverage not supported or failed: %s", e)
            return {}


def get_client():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    if not api_key or not api_secret:
        raise RuntimeError("API keys not found in environment variables")
    testnet_flag = os.getenv("BYBIT_TESTNET") or os.getenv("TESTNET") or os.getenv("BYBIT_DEMO")
    testnet = str(testnet_flag).lower() in ("1", "true", "yes", "y", "on")
    return BybitWrapper(api_key, api_secret, testnet=testnet)
