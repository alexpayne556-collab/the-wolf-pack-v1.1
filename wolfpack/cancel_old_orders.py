"""
Cancel the old fantasy portfolio orders (378 MARA, 480 PLTR, 26 NVDA, 73 MRNA, 25 CRWD, 250 MU)
Keep the 6 REAL orders (7 RGTI, 14 CLSK, 17 MARA, 56 HIVE, 15 NTLA, 15 AI)
"""
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderStatus, QueryOrderStatus

# Load env
load_dotenv()

# Connect to Alpaca
client = TradingClient(
    os.getenv('ALPACA_PAPER_KEY_ID'),
    os.getenv('ALPACA_PAPER_SECRET_KEY'),
    paper=True
)

print("=" * 70)
print("🐺 CANCELLING OLD FANTASY ORDERS")
print("=" * 70)

# Get all open orders
orders = client.get_orders(filter=GetOrdersRequest(status=QueryOrderStatus.OPEN))

# Fantasy orders to cancel (old 7:29 PM orders + the 250 MU from Jan 18)
fantasy_signatures = [
    ("MARA", 378),  # Fantasy
    ("PLTR", 480),  # Fantasy
    ("NVDA", 26),   # Fantasy
    ("MRNA", 73),   # Fantasy
    ("CRWD", 25),   # Fantasy
    ("MU", 250),    # Old order from Jan 18
]

# Real orders to KEEP (7:53 PM orders)
real_signatures = [
    ("RGTI", 7),
    ("CLSK", 14),
    ("MARA", 17),   # ← Note: MARA 17 is REAL, MARA 378 is FANTASY
    ("HIVE", 56),
    ("NTLA", 15),
    ("AI", 15),
]

cancelled = 0
kept = 0

for order in orders:
    symbol = order.symbol
    qty = int(order.qty)
    order_id = order.id
    
    # Check if this is a fantasy order
    is_fantasy = (symbol, qty) in fantasy_signatures
    is_real = (symbol, qty) in real_signatures
    
    if is_fantasy:
        print(f"\n❌ CANCELLING: {symbol} {qty} shares (fantasy order)")
        try:
            client.cancel_order_by_id(order_id)
            print(f"   ✅ Cancelled: {order_id}")
            cancelled += 1
        except Exception as e:
            print(f"   ⚠️ Failed: {e}")
    elif is_real:
        print(f"\n✅ KEEPING: {symbol} {qty} shares (REAL $1,400 order)")
        kept += 1
    else:
        print(f"\n⚠️ UNKNOWN: {symbol} {qty} shares - check manually")

print("\n" + "=" * 70)
print(f"✅ Cancelled: {cancelled} fantasy orders")
print(f"✅ Kept: {kept} real orders")
print("=" * 70)
print("\nRun check_account.py to verify only 6 orders remain")
