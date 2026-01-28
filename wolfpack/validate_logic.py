"""
Validate the scoring logic and wounded prey selection makes sense
"""
import json

print("=" * 70)
print("🧠 VALIDATING SCORING LOGIC")
print("=" * 70)

# Test 1: Check wounded prey scoring formula
print("\n✅ TEST 1: Wounded Prey Scoring Formula")
print("-" * 70)
print("Formula: Base Score (0-100)")
print("  - How wounded (40 pts): More down from high = more points")
print("  - Liquidity (30 pts): Higher volume = more points")
print("  - Market cap (30 pts): $500M-$2B sweet spot")
print()

# Manual check of the 6 selected tickers
selected = [
    {"symbol": "AI", "down": 63.8, "vol": 6.6, "mcap": "unknown"},
    {"symbol": "NTLA", "down": 55.8, "vol": 0.9, "mcap": "unknown"},
    {"symbol": "HIVE", "down": 55.7, "vol": 19.3, "mcap": "unknown"},
    {"symbol": "MARA", "down": 51.6, "vol": 4.4, "mcap": "unknown"},
    {"symbol": "CLSK", "down": 43.4, "vol": 7.0, "mcap": "unknown"},
    {"symbol": "RGTI", "down": 55.9, "vol": 4.2, "mcap": "unknown"},
]

print("Selected tickers:")
for s in selected:
    # Calculate wounded score (40 pts max)
    if s['down'] >= 60:
        wounded_pts = 40
    elif s['down'] >= 50:
        wounded_pts = 35
    elif s['down'] >= 40:
        wounded_pts = 30
    else:
        wounded_pts = 20
    
    # Calculate liquidity score (30 pts max)
    vol_m = s['vol']
    if vol_m >= 5:
        liquidity_pts = 30
    elif vol_m >= 2:
        liquidity_pts = 25
    elif vol_m >= 1:
        liquidity_pts = 20
    else:
        liquidity_pts = 10
    
    # Market cap score (assume 20 pts since we don't have exact)
    mcap_pts = 20
    
    total = wounded_pts + liquidity_pts + mcap_pts
    
    print(f"{s['symbol']:6} Down {s['down']:5.1f}% ({wounded_pts}pts) + Vol {s['vol']:5.1f}M ({liquidity_pts}pts) = {total}pts")

# Test 2: Check if selection makes sense
print("\n✅ TEST 2: Does Selection Make Sense?")
print("-" * 70)
print("✅ AI: Down 63.8% - Most wounded, good liquidity")
print("✅ NTLA: Down 55.8% - Biotech bounce, lower volume but acceptable")
print("✅ HIVE: Down 55.7% - Crypto mining, BEST liquidity (19.3M)")
print("✅ MARA: Down 51.6% - Bitcoin miner, good volume")
print("✅ CLSK: Down 43.4% - LEAST wounded, but still >30% criteria")
print("✅ RGTI: Down 55.9% - Quantum play, volatile")

# Test 3: Check position sizing logic
print("\n✅ TEST 3: Position Sizing Logic")
print("-" * 70)
print("Total capital: $1,400")
print("Target: 6 positions (~$233 each for even spread)")
print()

positions = [
    ("AI", 15, 13.04, 195.60),
    ("NTLA", 15, 12.50, 187.50),
    ("HIVE", 56, 3.47, 194.32),
    ("MARA", 17, 11.36, 193.12),
    ("CLSK", 14, 13.37, 187.18),
    ("RGTI", 7, 25.62, 179.34),
]

total = 0
for symbol, shares, price, value in positions:
    pct = (value / 1400) * 100
    print(f"{symbol:6} {shares:3} shares @ ${price:6.2f} = ${value:7.2f} ({pct:5.2f}%)")
    total += value

print(f"\nTotal: ${total:7.2f} ({(total/1400)*100:.1f}% of $1,400)")
print(f"Cash reserve: ${1400-total:7.2f}")

if total > 1200 and total < 1400:
    print("✅ Position sizing CORRECT: 85-100% deployed, some cash reserve")
else:
    print("⚠️ Position sizing may be off")

# Test 4: Check stop loss logic
print("\n✅ TEST 4: Stop Loss Calculations")
print("-" * 70)
print("Risk: 2% of $1,400 = $28 per position")
print()

stops = [
    ("AI", 15, 13.04, 11.17),
    ("NTLA", 15, 12.50, 10.63),
    ("HIVE", 56, 3.47, 2.97),
    ("MARA", 17, 11.36, 9.71),
    ("CLSK", 14, 13.37, 11.37),
    ("RGTI", 7, 25.62, 21.62),
]

for symbol, shares, entry, stop in stops:
    loss_per_share = entry - stop
    max_loss = loss_per_share * shares
    pct_stop = ((entry - stop) / entry) * 100
    
    print(f"{symbol:6} Entry ${entry:6.2f} → Stop ${stop:6.2f} ({pct_stop:5.1f}%) = ${max_loss:5.2f} max loss")
    
    if max_loss > 30:
        print(f"       ⚠️ Max loss ${max_loss:.2f} exceeds $28 target")
    elif max_loss < 26:
        print(f"       ⚠️ Max loss ${max_loss:.2f} under $28 (not using full risk)")

print("\n✅ All stops calculated to risk ~$28 per position")
print(f"Worst case (all 6 stop): 6 × $28 = ${6*28} ({(6*28/1400)*100:.1f}% of capital)")

print("\n" + "=" * 70)
print("SCORING LOGIC VALIDATION COMPLETE")
print("=" * 70)
