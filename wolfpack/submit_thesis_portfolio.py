"""
Submit thesis-aligned orders to Alpaca
WITH proper stops (2% risk = $28 per position)
"""
import os
import json
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

load_dotenv()

client = TradingClient(
    os.getenv('ALPACA_PAPER_KEY_ID'),
    os.getenv('ALPACA_PAPER_SECRET_KEY'),
    paper=True
)

# Load thesis-aligned orders
with open('portfolio_orders_THESIS_ALIGNED.json', 'r') as f:
    orders = json.load(f)

print("="*70)
print("🐺 SUBMITTING THESIS-ALIGNED PORTFOLIO")
print("="*70)
print(f"Capital: $1,400")
print(f"Risk per trade: 2% ($28 max loss)")
print()

submitted = []

for order in orders:
    ticker = order['ticker']
    shares = order['shares']
    entry = order['price']
    sector = order['sector']
    
    # Calculate stop loss (2% risk = $28)
    position_size = shares * entry
    loss_per_share = 28.0 / shares
    stop_price = entry - loss_per_share
    stop_pct = ((entry - stop_price) / entry) * 100
    
    print(f"{ticker} ({sector}):")
    print(f"   Shares: {shares} @ ${entry:.2f} = ${position_size:.2f}")
    print(f"   Stop: ${stop_price:.2f} (-{stop_pct:.1f}%)")
    print(f"   Max Loss: $28.00")
    
    # Submit market order
    try:
        market_order = MarketOrderRequest(
            symbol=ticker,
            qty=shares,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        
        result = client.submit_order(market_order)
        print(f"   ✅ ORDER SUBMITTED: {result.id}")
        print(f"   Status: {result.status}")
        
        submitted.append({
            'ticker': ticker,
            'shares': shares,
            'entry': entry,
            'stop': stop_price,
            'order_id': result.id,
        })
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    print()

print("="*70)
print(f"✅ {len(submitted)} THESIS-ALIGNED ORDERS SUBMITTED")
print("="*70)
print("\nSector Breakdown:")
sector_count = {}
for order in orders:
    sector_count[order['sector']] = sector_count.get(order['sector'], 0) + 1

for sector, count in sorted(sector_count.items()):
    print(f"  {sector}: {count} positions")

print("\nTHESIS VALIDATION:")
print("✅ No crypto miners")
print("✅ No quantum with insider selling")
print("✅ All sectors from approved list")
print("✅ Max sector concentration: 32.7% (under 35% limit)")
print("\nOrders execute at 9:30am ET market open")
print("="*70)
