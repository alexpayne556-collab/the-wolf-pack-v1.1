"""
Scan for THESIS-ALIGNED wounded prey
Only approved sectors: Defense, Biotech, Nuclear, Space, Semiconductors, AI Infrastructure
"""
import yfinance as yf
from datetime import datetime

print("="*80)
print("🐺 HUNTING FOR THESIS-ALIGNED WOUNDED PREY")
print("="*80)

# Tyr's approved universe (from Leonard File + thesis)
APPROVED_UNIVERSE = {
    'defense': ['KTOS', 'LMT', 'RTX', 'NOC', 'LHX', 'HII', 'AVAV'],
    'space': ['RKLB', 'LUNR', 'ASTS', 'PL'],
    'nuclear': ['UUUU', 'UEC', 'DNN', 'UROY', 'CCJ'],
    'biotech': ['IBRX', 'NTLA', 'CRSP', 'MRNA', 'VRTX', 'SRPT', 'IONS'],
    'semiconductors': ['MU', 'AMD', 'INTC', 'QCOM', 'NVDA', 'ASML'],
    'ai_infrastructure': ['AI', 'PLTR', 'SNOW', 'DDOG'],
}

# Flatten to scan list
all_tickers = []
ticker_sectors = {}
for sector, tickers in APPROVED_UNIVERSE.items():
    all_tickers.extend(tickers)
    for t in tickers:
        ticker_sectors[t] = sector

print(f"\nScanning {len(all_tickers)} thesis-aligned tickers...")
print(f"Sectors: {', '.join(APPROVED_UNIVERSE.keys())}")
print()

wounded = []

for symbol in all_tickers:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        current = info.get('currentPrice') or info.get('regularMarketPrice')
        high_52 = info.get('fiftyTwoWeekHigh')
        low_52 = info.get('fiftyTwoWeekLow')
        mcap = info.get('marketCap', 0)
        avg_vol = info.get('averageVolume10days', 0)
        
        if not current or not high_52:
            continue
        
        # Calculate wounded status
        pct_down = ((high_52 - current) / high_52) * 100
        pct_from_low = ((current - low_52) / low_52) * 100 if low_52 else 0
        
        # THESIS-ALIGNED WOUNDED PREY CRITERIA:
        # 1. Down 30-70% from high (wounded but not dying)
        # 2. Price $2-50 (affordable for $1,400)
        # 3. Volume >500K (liquid)
        # 4. Market cap $200M-$10B (sweet spot)
        # 5. NOT at absolute lows (some bounce already)
        
        if (30 <= pct_down <= 70 and 
            2 <= current <= 50 and 
            avg_vol >= 500_000 and
            200_000_000 <= mcap <= 10_000_000_000 and
            pct_from_low >= 10):  # At least 10% off lows
            
            # Score it
            wounded_score = 40 if pct_down >= 60 else 35 if pct_down >= 50 else 30
            liquidity_score = 30 if avg_vol >= 5_000_000 else 25 if avg_vol >= 2_000_000 else 20 if avg_vol >= 1_000_000 else 10
            mcap_score = 30 if 500_000_000 <= mcap <= 2_000_000_000 else 20
            
            total_score = wounded_score + liquidity_score + mcap_score
            
            wounded.append({
                'symbol': symbol,
                'sector': ticker_sectors[symbol],
                'current': current,
                'high_52': high_52,
                'low_52': low_52,
                'pct_down': pct_down,
                'pct_from_low': pct_from_low,
                'mcap': mcap,
                'avg_vol': avg_vol / 1_000_000,
                'score': total_score,
            })
            
    except Exception as e:
        continue

# Sort by score
wounded.sort(key=lambda x: x['score'], reverse=True)

print("\n" + "="*80)
print(f"FOUND {len(wounded)} THESIS-ALIGNED WOUNDED PREY")
print("="*80)

if wounded:
    print(f"\n{'Ticker':<8} {'Sector':<16} {'Price':<8} {'Down%':<8} {'OffLow%':<10} {'Score':<6}")
    print("-"*80)
    for w in wounded[:15]:  # Top 15
        print(f"{w['symbol']:<8} {w['sector']:<16} ${w['current']:<7.2f} {w['pct_down']:<7.1f}% {w['pct_from_low']:<9.1f}% {w['score']:<6}")

    # Save top candidates
    import json
    with open('../data/thesis_aligned_wounded_prey.json', 'w') as f:
        json.dump(wounded[:15], f, indent=2)
    
    print("\n✅ Saved top 15 to data/thesis_aligned_wounded_prey.json")
else:
    print("\n⚠️ No wounded prey found meeting all criteria")

print("\n" + "="*80)
