from binance.client import Client
from config.secrets import API_KEY, API_SECRET


def get_client():
    """Return a Binance client using API keys from config.secrets."""
    client = Client(API_KEY, API_SECRET)
    return client
