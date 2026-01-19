#!/usr/bin/env python3
"""
TEST ALPACA CONNECTION
Quick test to verify Alpaca paper trading is working
"""

import os
import sys
from pathlib import Path

# Load environment variables from ROOT .env (not wolfpack/.env)
# This ensures we use the correct API keys
root_env = Path(__file__).parent.parent / '.env'
if root_env.exists():
    from dotenv import load_dotenv
    load_dotenv(root_env)
    print(f"Loaded .env from: {root_env}")
else:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded .env from default location")

from datetime import datetime

print("=" * 60)
print("🐺 WOLF PACK - ALPACA CONNECTION TEST")
print("=" * 60)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Check for alpaca-py
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
    from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
    print("✅ alpaca-py installed and imported")
except ImportError as e:
    print(f"❌ alpaca-py NOT installed: {e}")
    print("Run: pip install alpaca-py")
    sys.exit(1)

# Get API keys from .env
api_key = os.getenv('ALPACA_API_KEY')
api_secret = os.getenv('ALPACA_SECRET_KEY')  # Note: Some .env files use ALPACA_API_SECRET
if not api_secret:
    api_secret = os.getenv('ALPACA_API_SECRET')  # Try alternate name
base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')

print(f"\n📋 Configuration:")
print(f"   API Key: {api_key[:8]}..." if api_key else "   API Key: ❌ NOT FOUND")
print(f"   Secret: {api_secret[:8]}..." if api_secret else "   Secret: ❌ NOT FOUND")
print(f"   Base URL: {base_url}")

if not api_key or not api_secret:
    print("\n❌ API keys not found in .env file!")
    print("Required environment variables:")
    print("   ALPACA_API_KEY=your_key_here")
    print("   ALPACA_API_SECRET=your_secret_here")
    sys.exit(1)

# Test connection
print(f"\n🔌 Connecting to Alpaca...")
try:
    client = TradingClient(api_key, api_secret, paper=True)
    account = client.get_account()
    print("✅ Connected successfully!")
    
    print(f"\n📊 ACCOUNT STATUS:")
    print(f"   Account Number: {account.account_number}")
    print(f"   Status: {account.status}")
    print(f"   Currency: {account.currency}")
    print(f"   Buying Power: ${float(account.buying_power):,.2f}")
    print(f"   Cash: ${float(account.cash):,.2f}")
    print(f"   Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"   Equity: ${float(account.equity):,.2f}")
    print(f"   Pattern Day Trader: {account.pattern_day_trader}")
    print(f"   Trading Blocked: {account.trading_blocked}")
    print(f"   Account Blocked: {account.account_blocked}")
    
    # Get positions
    print(f"\n📈 CURRENT POSITIONS:")
    positions = client.get_all_positions()
    if positions:
        for pos in positions:
            print(f"   {pos.symbol}: {pos.qty} shares @ ${float(pos.avg_entry_price):.2f} (P&L: ${float(pos.unrealized_pl):.2f})")
    else:
        print("   No open positions")
    
    # Get recent orders
    print(f"\n📋 RECENT ORDERS:")
    try:
        request_params = GetOrdersRequest(status=QueryOrderStatus.ALL, limit=5)
        orders = client.get_orders(filter=request_params)
        if orders:
            for order in orders:
                print(f"   {order.symbol}: {order.side} {order.qty} @ {order.type} - Status: {order.status}")
        else:
            print("   No recent orders")
    except Exception as e:
        print(f"   Could not fetch orders: {e}")
    
    # Calculate risk parameters
    equity = float(account.equity)
    max_risk_per_trade = equity * 0.02  # 2% rule
    
    print(f"\n⚠️ RISK PARAMETERS (Based on Current Equity):")
    print(f"   Max Risk Per Trade (2%): ${max_risk_per_trade:,.2f}")
    print(f"   Max Position Size (20%): ${equity * 0.20:,.2f}")
    print(f"   Available for Trading: ${float(account.buying_power):,.2f}")
    
    print(f"\n" + "=" * 60)
    print("✅ ALPACA PAPER TRADING IS READY!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Connection FAILED: {e}")
    print("\nTroubleshooting:")
    print("1. Check API keys are correct")
    print("2. Ensure you're using paper trading keys (not live)")
    print("3. Check if your Alpaca account is active")
    sys.exit(1)
