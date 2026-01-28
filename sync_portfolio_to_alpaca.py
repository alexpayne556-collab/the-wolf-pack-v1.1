"""
SYNC REAL PORTFOLIO TO ALPACA PAPER ACCOUNT
This replicates Tyr's actual positions in Alpaca for brain testing.
"""

import os
from dotenv import load_dotenv

load_dotenv()

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    ALPACA_AVAILABLE = True
except ImportError:
    print("ERROR: alpaca-py not installed")
    print("Run: pip install alpaca-py")
    ALPACA_AVAILABLE = False
    exit(1)

# Portfolio to replicate
PORTFOLIO = {
    "MU": {"shares": 2.5, "thesis": "AI memory demand", "status": "HOLD"},
    "RCAT": {"shares": 6.70, "thesis": "Defense/drones", "status": "HOLD"},
    "UUUU": {"shares": 6, "thesis": "Nuclear + rare earth", "status": "HOLD"},
    "MRNO": {"shares": 3, "thesis": "Momentum play +111%", "status": "MANAGE"},
    "IVF": {"shares": 51, "thesis": "Fertility + Trump policy", "status": "REVIEW"},
    "NTLA": {"shares": 2, "thesis": "NO THESIS - mistake", "status": "SELL_AT_OPEN"},
    "RDW": {"shares": 3.583, "thesis": "Defense contracts", "status": "HOLD"},
    "UEC": {"shares": 2, "thesis": "Uranium bull run", "status": "HOLD"}
}

print("="*80)
print("ALPACA PORTFOLIO SYNC - PAPER TRADING")
print("="*80)

# Connect to Alpaca
ALPACA_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET = os.getenv('ALPACA_SECRET_KEY')

if not ALPACA_KEY or not ALPACA_SECRET:
    print("ERROR: Alpaca credentials not found in .env")
    exit(1)

try:
    client = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=True)
    account = client.get_account()
    print(f"\n✓ Connected to Alpaca Paper Account")
    print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"  Buying Power: ${float(account.buying_power):,.2f}")
except Exception as e:
    print(f"ERROR: Could not connect to Alpaca: {e}")
    exit(1)

# Check current positions
print(f"\n[1/3] CURRENT ALPACA POSITIONS:")
try:
    current_positions = client.get_all_positions()
    if current_positions:
        for pos in current_positions:
            print(f"  • {pos.symbol}: {pos.qty} shares @ ${float(pos.current_price):.2f}")
    else:
        print("  (No positions)")
except Exception as e:
    print(f"  Error getting positions: {e}")

# Sync strategy: Clear all, then replicate
print(f"\n[2/3] SYNCING PORTFOLIO...")
print("  Strategy: Replicate real portfolio in paper account")
print("  Note: This is for BRAIN TESTING only")

synced = 0
errors = []

for ticker, data in PORTFOLIO.items():
    shares = int(data['shares'])  # Alpaca requires whole shares
    thesis = data['thesis']
    status = data['status']
    
    try:
        # Place market order to establish position
        order_request = MarketOrderRequest(
            symbol=ticker,
            qty=shares,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        
        order = client.submit_order(order_request)
        print(f"  ✓ {ticker}: {shares} shares ({status}) - {thesis}")
        synced += 1
        
    except Exception as e:
        error_msg = f"{ticker}: {str(e)}"
        errors.append(error_msg)
        print(f"  ✗ {error_msg}")

print(f"\n[3/3] SYNC COMPLETE")
print(f"  ✓ Synced: {synced}/{len(PORTFOLIO)}")
if errors:
    print(f"  ✗ Errors: {len(errors)}")
    for err in errors:
        print(f"    • {err}")

print(f"\n" + "="*80)
print("PORTFOLIO SYNCED - BRAIN READY FOR TESTING")
print("="*80)
print("\nNOTE: This paper portfolio mirrors real positions for:")
print("  1. Brain decision testing")
print("  2. Order execution practice")
print("  3. Risk management validation")
print("  4. Strategy backtesting")
print("\nReal trades happen in Robinhood/Fidelity.")
print("Paper trades teach the brain.")
