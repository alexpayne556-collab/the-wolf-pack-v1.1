#!/usr/bin/env python3
"""
EXECUTE WITH STOPS - Real $1,400 Portfolio
SUBMITS ORDERS NOW - They execute at market open
"""

import os
import json
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

load_dotenv()

# Connect to Alpaca
client = TradingClient(
    os.getenv('ALPACA_PAPER_KEY_ID'),
    os.getenv('ALPACA_PAPER_SECRET_KEY'),
    paper=True
)

# Load orders
with open('wolfpack/portfolio_orders_REAL.json', 'r') as f:
    orders = json.load(f)

print("="*70)
print("🐺 EXECUTING 6 TRADES WITH STOP LOSSES")
print("="*70)
print(f"Capital: $1,400")
print(f"Risk per trade: 2% ($28 max loss)")
print()

# Calculate stops and execute
for order in orders:
    ticker = order['ticker']
    shares = order['shares']
    entry = order['price']
    
    # Calculate stop loss (2% risk = $28)
    # $28 loss / shares = loss per share
    # entry - loss_per_share = stop price
    position_size = shares * entry
    loss_per_share = 28.0 / shares
    stop_price = entry - loss_per_share
    stop_pct = (stop_price / entry - 1) * 100
    
    print(f"{ticker}:")
    print(f"   Shares: {shares} @ ${entry:.2f} = ${position_size:.2f}")
    print(f"   Stop: ${stop_price:.2f} ({stop_pct:.1f}%)")
    print(f"   Max Loss: ${28:.2f}")
    
    # EXECUTE FOR REAL
    try:
        # Bracket order with stop loss
        market_order = MarketOrderRequest(
            symbol=ticker,
            qty=shares,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
            order_class=OrderClass.BRACKET,
            stop_loss=StopLossRequest(stop_price=stop_price)
        )
        
        result = client.submit_order(market_order)
        print(f"   ✅ ORDER SUBMITTED: {result.id}")
        print(f"   Status: {result.status}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    # EXECUTE FOR REAL
    try:
        # Submit bracket order with stop loss
        market_order = MarketOrderRequest(
            symbol=ticker,
            qty=shares,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        
        result = client.submit_order(market_order)
        print(f"   ✅ ORDER SUBMITTED: {result.id}")
        print(f"   Status: {result.status}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    print()

print("="*70)
print("✅ ORDERS SUBMITTED TO ALPACA PAPER")
print("They will execute at market open tomorrow (9:30am ET)")
print()
print("Check status: python wolfpack/check_account.py")
print("="*70)
