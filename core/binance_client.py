# core/binance_client.py
import os
from binance.client import Client

def get_client():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    if not api_key or not api_secret:
        raise RuntimeError("API keys not found in environment variables")

    client = Client(api_key, api_secret)
    return client
