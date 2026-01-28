"""
Build thesis-aligned portfolio with $1,400
Current: AI, NTLA, RGTI
Need: 3 more positions (total 6)
Available: SRPT (biotech)
"""
import yfinance as yf
import json

print("="*70)
print("🐺 BUILDING THESIS-ALIGNED PORTFOLIO")
print("="*70)

# What we already have
current_positions = [
    {'ticker': 'AI', 'sector': 'ai_infrastructure', 'shares': 15, 'price': 13.04},
    {'ticker': 'NTLA', 'sector': 'biotech', 'shares': 15, 'price': 12.50},
    {'ticker': 'RGTI', 'sector': 'quantum', 'shares': 7, 'price': 25.62},  # Check this
]

# Thesis-aligned wounded prey
new_candidates = [
    'SRPT',  # Biotech, down 82%
    'UUUU',  # Nuclear, down 20% (not quite wounded but thesis aligned)
    'KTOS',  # Defense, down 1% (not wounded but HIGH conviction thesis)
    'LUNR',  # Space, down 13.5%
]

print("\nCURRENT POSITIONS (kept from cancelled orders):")
for p in current_positions:
    value = p['shares'] * p['price']
    print(f"  {p['ticker']}: {p['shares']} @ ${p['price']:.2f} = ${value:.2f}")

current_value = sum(p['shares'] * p['price'] for p in current_positions)
print(f"\nCurrent total: ${current_value:.2f}")

print("\n" + "="*70)
print("CHECKING NEW CANDIDATES:")
print("="*70)

candidates = []
for symbol in new_candidates:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current = info.get('currentPrice') or info.get('regularMarketPrice')
        high_52 = info.get('fiftyTwoWeekHigh')
        
        if current and high_52:
            pct_down = ((high_52 - current) / high_52) * 100
            candidates.append({
                'ticker': symbol,
                'price': current,
                'pct_down': pct_down,
            })
            print(f"  {symbol}: ${current:.2f} (down {pct_down:.1f}%)")
    except:
        continue

# Build 6-position portfolio
print("\n" + "="*70)
print("PROPOSED 6-POSITION PORTFOLIO:")
print("="*70)

capital = 1400
target_position = capital / 6  # ~$233 each

portfolio = []

# Keep AI and NTLA (thesis aligned)
portfolio.append({'ticker': 'AI', 'shares': 15, 'price': 13.04, 'sector': 'ai_infrastructure'})
portfolio.append({'ticker': 'NTLA', 'shares': 15, 'price': 12.50, 'sector': 'biotech'})

# Add SRPT (biotech, most wounded)
srpt_price = next(c['price'] for c in candidates if c['ticker'] == 'SRPT')
srpt_shares = int(target_position / srpt_price)
portfolio.append({'ticker': 'SRPT', 'shares': srpt_shares, 'price': srpt_price, 'sector': 'biotech'})

# Question: Keep RGTI? Check if insiders sold
print("\n⚠️ RGTI (Quantum): Checking if we should keep...")
print("  Architecture says: 'Only with insider buying. RGTI insiders SOLD.'")
print("  Decision: DROP RGTI - violates thesis (insiders sold)")

# Add 3 more thesis-aligned
# Priority: Diversify sectors (not all biotech)

# UUUU (nuclear - thesis aligned even if not deep wounded)
uuuu_price = next(c['price'] for c in candidates if c['ticker'] == 'UUUU')
uuuu_shares = int(target_position / uuuu_price)
portfolio.append({'ticker': 'UUUU', 'shares': uuuu_shares, 'price': uuuu_price, 'sector': 'nuclear'})

# KTOS or LUNR? Both thesis aligned
# KTOS: Defense, high conviction, not wounded
# LUNR: Space, thesis aligned, down 13.5%

lunr_price = next(c['price'] for c in candidates if c['ticker'] == 'LUNR')
lunr_shares = int(target_position / lunr_price)
portfolio.append({'ticker': 'LUNR', 'shares': lunr_shares, 'price': lunr_price, 'sector': 'space'})

# 6th position: Need one more
# Options: KTOS (defense), IBRX (biotech - Tyr's conviction), or another nuclear
# Let's check IBRX

try:
    ibrx = yf.Ticker('IBRX')
    ibrx_info = ibrx.info
    ibrx_price = ibrx_info.get('currentPrice') or ibrx_info.get('regularMarketPrice')
    ibrx_shares = int(target_position / ibrx_price)
    portfolio.append({'ticker': 'IBRX', 'shares': ibrx_shares, 'price': ibrx_price, 'sector': 'biotech'})
    print(f"  Adding IBRX @ ${ibrx_price:.2f}")
except:
    # Fallback to KTOS if IBRX fails
    print("  IBRX failed, using KTOS instead")
    ktos_price = 28.50  # Approximate
    ktos_shares = int(target_position / ktos_price)
    portfolio.append({'ticker': 'KTOS', 'shares': ktos_shares, 'price': ktos_price, 'sector': 'defense'})

print("\n" + "="*70)
print("FINAL PORTFOLIO:")
print("="*70)

total = 0
sector_exposure = {}

for p in portfolio:
    value = p['shares'] * p['price']
    pct = (value / capital) * 100
    total += value
    sector_exposure[p['sector']] = sector_exposure.get(p['sector'], 0) + value
    print(f"{p['ticker']:<8} {p['shares']:>3} @ ${p['price']:>7.2f} = ${value:>7.2f} ({pct:>5.1f}%)  [{p['sector']}]")

print(f"\nTotal: ${total:.2f} ({(total/capital)*100:.1f}% deployed)")
print(f"Cash: ${capital - total:.2f}")

print("\nSector Diversification:")
for sector, value in sorted(sector_exposure.items(), key=lambda x: x[1], reverse=True):
    pct = (value / capital) * 100
    print(f"  {sector}: ${value:.2f} ({pct:.1f}%)")

# Save to JSON
orders = []
for p in portfolio:
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
