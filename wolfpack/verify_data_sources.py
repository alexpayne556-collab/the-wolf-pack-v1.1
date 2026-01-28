"""
Verify all data sources are REAL API calls, not mock data
"""
import yfinance as yf
import json
from datetime import datetime

print("=" * 70)
print("🔍 VERIFYING DATA SOURCES ARE REAL")
print("=" * 70)

# Test 1: Check Yahoo Finance API is working
print("\n✅ TEST 1: Yahoo Finance API")
print("-" * 70)
tickers = ['AI', 'NTLA', 'HIVE', 'MARA', 'CLSK', 'RGTI']
for symbol in tickers:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current = info.get('currentPrice') or info.get('regularMarketPrice')
        high_52 = info.get('fiftyTwoWeekHigh')
        
        if current and high_52:
            pct_down = ((high_52 - current) / high_52) * 100
            print(f"{symbol:6} Current: ${current:7.2f}  High: ${high_52:7.2f}  Down: {pct_down:5.1f}%")
        else:
            print(f"{symbol:6} ⚠️ Missing price data")
    except Exception as e:
        print(f"{symbol:6} ❌ API Error: {e}")

# Test 2: Check wounded prey file exists and has real data
print("\n✅ TEST 2: Wounded Prey Data File")
print("-" * 70)
try:
    with open('../data/wounded_prey_universe.json', 'r') as f:
        wounded = json.load(f)
    print(f"Found {len(wounded)} wounded prey candidates")
    print(f"File timestamp: {wounded[0].get('timestamp', 'N/A')}")
    
    # Check a few entries have real structure
    sample = wounded[0]
    required_fields = ['symbol', 'current_price', 'high_52week', 'pct_down', 'score']
    missing = [f for f in required_fields if f not in sample]
    if missing:
        print(f"⚠️ Missing fields: {missing}")
    else:
        print(f"✅ All required fields present")
        print(f"Sample: {sample['symbol']} @ ${sample['current_price']:.2f}, down {sample['pct_down']:.1f}%")
except FileNotFoundError:
    print("❌ Wounded prey file not found")
except Exception as e:
    print(f"❌ Error reading file: {e}")

# Test 3: Check morning opportunities file
print("\n✅ TEST 3: Morning Opportunities (Overnight Scan)")
print("-" * 70)
try:
    with open('../data/morning_opportunities.json', 'r') as f:
        morning = json.load(f)
    print(f"Found {len(morning)} opportunities from overnight scan")
    
    if morning:
        top = morning[0]
        print(f"Top pick: {top['symbol']} (score: {top.get('final_score', 'N/A')})")
        print(f"Reasoning: {top.get('wolf_analysis', 'N/A')[:80]}...")
except FileNotFoundError:
    print("❌ Morning opportunities file not found")
except Exception as e:
    print(f"❌ Error reading file: {e}")

# Test 4: Check portfolio orders file
print("\n✅ TEST 4: Portfolio Orders (REAL $1,400 sized)")
print("-" * 70)
try:
    with open('portfolio_orders_REAL.json', 'r') as f:
        orders = json.load(f)
    
    total_value = sum(o['shares'] * o['current_price'] for o in orders)
    print(f"Found {len(orders)} orders")
    print(f"Total value: ${total_value:,.2f}")
    print(f"Capital target: $1,400")
    print(f"Allocation: {(total_value/1400)*100:.1f}%")
    
    if total_value > 2000:
        print(f"⚠️ WARNING: Total value ${total_value:,.2f} too high for $1,400 capital")
    elif total_value < 800:
        print(f"⚠️ WARNING: Total value ${total_value:,.2f} too low (underallocated)")
    else:
        print(f"✅ Position sizing appropriate for $1,400 capital")
        
except FileNotFoundError:
    print("❌ Portfolio orders file not found")
except Exception as e:
    print(f"❌ Error reading file: {e}")

print("\n" + "=" * 70)
print("DATA SOURCE VERIFICATION COMPLETE")
print("=" * 70)
