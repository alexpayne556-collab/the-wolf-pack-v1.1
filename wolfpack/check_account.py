#!/usr/bin/env python3
"""
Quick check of Alpaca account status
"""

import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

# Load env
load_dotenv()

# Connect
client = TradingClient(
    os.getenv('ALPACA_PAPER_KEY_ID'),
    os.getenv('ALPACA_PAPER_SECRET_KEY'),
    paper=True
)

# Get account
account = client.get_account()

print("\n🐺 ALPACA PAPER ACCOUNT")
print("="*70)
print(f"Status: {account.status}")
print(f"Equity: ${float(account.equity):,.2f}")
print(f"Cash: ${float(account.cash):,.2f}")
print(f"Buying Power: ${float(account.buying_power):,.2f}")

# Get positions
positions = client.get_all_positions()
print(f"\n📊 POSITIONS ({len(positions)} total)")
print("="*70)

if positions:
    for p in positions:
        pnl = float(p.unrealized_plpc) * 100
        print(f"{p.symbol}: {p.qty} shares @ ${float(p.avg_entry_price):.2f}")
        print(f"   Current: ${float(p.current_price):.2f}")
        print(f"   Value: ${float(p.market_value):,.2f}")
        print(f"   P/L: {pnl:+.2f}%\n")
else:
    print("No positions yet")

# Get orders
orders = client.get_orders()
print(f"\n📋 ORDERS ({len(orders)} total)")
print("="*70)

if orders:
    for o in orders:
        print(f"{o.symbol}: {o.side} {o.qty} shares")
        print(f"   Status: {o.status}")
        print(f"   Type: {o.type}")
        print(f"   Submitted: {o.submitted_at}")
        if o.filled_at:
            print(f"   Filled: {o.filled_at} @ ${o.filled_avg_price}")
        print()
else:
    print("No orders")

print("="*70)
