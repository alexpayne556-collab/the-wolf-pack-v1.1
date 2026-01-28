"""
Cancel the crypto miners - they violate thesis
Keep only: AI, NTLA (and check RGTI insiders)
"""
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus

load_dotenv()

client = TradingClient(
    os.getenv('ALPACA_PAPER_KEY_ID'),
    os.getenv('ALPACA_PAPER_SECRET_KEY'),
    paper=True
)

print("="*70)
print("🐺 CANCELLING CRYPTO MINERS - THESIS VIOLATION")
print("="*70)

# Crypto miners to cancel (violate thesis)
crypto_miners = [
    ("HIVE", 56),   # Bitcoin mining
    ("MARA", 17),   # Bitcoin mining
    ("CLSK", 14),   # Bitcoin mining
]

# Keep these (thesis aligned)
keep = [
    ("AI", 15),     # AI infrastructure
    ("NTLA", 15),   # Biotech
    ("RGTI", 7),    # Quantum (checking insiders)
]

orders = client.get_orders(filter=GetOrdersRequest(status=QueryOrderStatus.OPEN))

cancelled = 0
kept = 0

for order in orders:
    symbol = order.symbol
    qty = int(order.qty)
    order_id = order.id
    
    is_crypto = (symbol, qty) in crypto_miners
    is_keep = (symbol, qty) in keep
    
    if is_crypto:
        print(f"\n❌ CANCELLING: {symbol} {qty} shares (Bitcoin miner - thesis violation)")
        try:
            client.cancel_order_by_id(order_id)
            print(f"   ✅ Cancelled: {order_id}")
            cancelled += 1
        except Exception as e:
            print(f"   ⚠️ Failed: {e}")
    elif is_keep:
        print(f"\n✅ KEEPING: {symbol} {qty} shares (thesis aligned)")
        kept += 1

print("\n" + "="*70)
print(f"✅ Cancelled: {cancelled} crypto miners")
print(f"✅ Kept: {kept} thesis-aligned positions")
print("="*70)
print("\nNow need to find 3 replacement wounded prey from approved sectors:")
print("- Defense (KTOS, etc)")
print("- Nuclear (UUUU, UEC)")
print("- Space (LUNR, RKLB)")
print("- More biotech")
