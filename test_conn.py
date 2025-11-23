import os
import sys
from config import Config
import bybit_api

try:
    print("Testing Bybit connection...")
    if bybit_api.test_connection():
        print("Connection successful!")
        balance = bybit_api.get_wallet_balance()
        print(f"Balance: {balance}")
    else:
        print("Connection failed!")
except Exception as e:
    print(f"Error: {e}")
