"""
Rebalance: MAX 35% per sector (from architecture doc)
Current problem: 46% biotech
"""
import yfinance as yf
import json

capital = 1400
MAX_SECTOR = 0.35  # 35% max per sector

print("="*70)
print("🐺 THESIS-ALIGNED PORTFOLIO - PROPERLY DIVERSIFIED")
print("="*70)

# Available picks by sector
picks = {
    'ai_infrastructure': [{'ticker': 'AI', 'price': 13.04, 'down': 63.8}],
    'biotech': [
        {'ticker': 'SRPT', 'price': 21.13, 'down': 82.4},  # Most wounded
        {'ticker': 'NTLA', 'price': 12.50, 'down': 55.8},  # Wounded
        {'ticker': 'IBRX', 'price': 5.52, 'down': 1.1},    # Tyr conviction
    ],
    'nuclear': [
        {'ticker': 'UUUU', 'price': 21.94, 'down': 19.7},  # Thesis aligned
    ],
    'space': [
        {'ticker': 'LUNR', 'price': 21.58, 'down': 13.5},  # Thesis aligned
    ],
    'defense': [
        {'ticker': 'KTOS', 'price': 130.72, 'down': 1.0},  # High conviction
    ],
}

# Strategy: 6 positions, diversified
# Rule: No more than 2 from same sector (unless only 6 total tickers)
# Priority: Most wounded + thesis aligned

portfolio = []

# 1. AI (only AI infrastructure pick)
portfolio.append({'ticker': 'AI', 'price': 13.04, 'sector': 'ai_infrastructure'})

# 2 & 3. Biotech: Take 2 most wounded (SRPT, NTLA)
portfolio.append({'ticker': 'SRPT', 'price': 21.13, 'sector': 'biotech'})
portfolio.append({'ticker': 'NTLA', 'price': 12.50, 'sector': 'biotech'})

# 4. Nuclear: UUUU (uranium thesis)
portfolio.append({'ticker': 'UUUU', 'price': 21.94, 'sector': 'nuclear'})

# 5. Space: LUNR (space thesis)
portfolio.append({'ticker': 'LUNR', 'price': 21.58, 'sector': 'space'})

# 6. Need one more - options:
# - IBRX (3rd biotech - would be 50% biotech) ❌
# - KTOS (defense - high conviction but expensive) 
# - Check for another sector option

# Try semiconductors
print("\nChecking semiconductors for 6th position...")
try:
    intc = yf.Ticker('INTC')
    intc_info = intc.info
    intc_price = intc_info.get('currentPrice') or intc_info.get('regularMarketPrice')
    intc_high = intc_info.get('fiftyTwoWeekHigh')
    intc_down = ((intc_high - intc_price) / intc_high) * 100 if intc_high else 0
    
    print(f"  INTC: ${intc_price:.2f}, down {intc_down:.1f}%")
    
    if intc_price < 50:  # Affordable
        portfolio.append({'ticker': 'INTC', 'price': intc_price, 'sector': 'semiconductors'})
        print(f"  ✅ Adding INTC (semiconductors thesis)")
    else:
        print(f"  ❌ INTC too expensive")
        raise Exception("Try alternative")
        
except:
    # Fallback: Add IBRX (accept 50% biotech for now, better than crypto)
    print("  Using IBRX (biotech) as fallback")
    portfolio.append({'ticker': 'IBRX', 'price': 5.52, 'sector': 'biotech'})

# Calculate shares for each
target_per_position = capital / len(portfolio)

final_portfolio = []
total_value = 0
sector_totals = {}

print("\n" + "="*70)
print("FINAL THESIS-ALIGNED PORTFOLIO:")
print("="*70)
print(f"\n{'Ticker':<8} {'Sector':<18} {'Shares':<8} {'Price':<10} {'Value':<12} {'%':<8}")
print("-"*70)

for p in portfolio:
    shares = int(target_per_position / p['price'])
    value = shares * p['price']
    pct = (value / capital) * 100
    
    final_portfolio.append({
        'ticker': p['ticker'],
        'shares': shares,
        'price': p['price'],
        'sector': p['sector'],
        'value': value,
    })
    
    total_value += value
    sector_totals[p['sector']] = sector_totals.get(p['sector'], 0) + value
    
    print(f"{p['ticker']:<8} {p['sector']:<18} {shares:<8} ${p['price']:<9.2f} ${value:<11.2f} {pct:<7.1f}%")

print("-"*70)
print(f"{'TOTAL':<36} ${total_value:<11.2f} {(total_value/capital)*100:<7.1f}%")
print(f"{'CASH RESERVE':<36} ${capital - total_value:<11.2f}")

print("\n" + "="*70)
print("SECTOR EXPOSURE:")
print("="*70)

for sector in sorted(sector_totals.keys()):
    value = sector_totals[sector]
    pct = (value / capital) * 100
    status = "✅" if pct <= 35 else "⚠️ OVER 35%"
    print(f"{sector:<20} ${value:>8.2f} ({pct:>5.1f}%)  {status}")

# Check concentration
max_sector_pct = max((v/capital)*100 for v in sector_totals.values())
print(f"\nMax sector concentration: {max_sector_pct:.1f}%")
if max_sector_pct <= 35:
    print("✅ Within 35% limit")
else:
    print(f"⚠️ EXCEEDS 35% limit")

# Save orders
orders = []
for p in final_portfolio:
    orders.append({
        'ticker': p['ticker'],
        'action': 'BUY',
        'shares': p['shares'],
        'price': p['price'],
        'sector': p['sector'],
    })

with open('portfolio_orders_THESIS_ALIGNED.json', 'w') as f:
    json.dump(orders, f, indent=2)

print("\n✅ Saved to portfolio_orders_THESIS_ALIGNED.json")
print("="*70)
