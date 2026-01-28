"""
Quick check on TYR'S CORE HOLDINGS + close alternatives
Focus on what Tyr actually tracks
"""
import yfinance as yf

print("="*70)
print("🐺 CHECKING TYR'S UNIVERSE")
print("="*70)

# Tyr's actual watchlist from Leonard File
CORE_UNIVERSE = {
    'defense': ['KTOS'],
    'space': ['RKLB', 'LUNR'],
    'nuclear': ['UUUU', 'UEC', 'DNN'],
    'biotech': ['IBRX', 'NTLA', 'SRPT'],
    'semiconductors': ['MU', 'INTC'],
    'ai_infrastructure': ['AI'],
}

all_tickers = []
for tickers in CORE_UNIVERSE.values():
    all_tickers.extend(tickers)

print(f"\nChecking {len(all_tickers)} core tickers...\n")

results = []

for symbol in all_tickers:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        current = info.get('currentPrice') or info.get('regularMarketPrice')
        high_52 = info.get('fiftyTwoWeekHigh')
        
        if not current or not high_52:
            continue
        
        pct_down = ((high_52 - current) / high_52) * 100
        
        # Find sector
        sector = next(s for s, tickers in CORE_UNIVERSE.items() if symbol in tickers)
        
        results.append({
            'symbol': symbol,
            'sector': sector,
            'price': current,
            'down': pct_down,
            'wounded': pct_down >= 30,
        })
        
    except:
        continue

print(f"{'Ticker':<8} {'Sector':<16} {'Price':<10} {'Down%':<10} {'Wounded?':<10}")
print("-"*70)

for r in sorted(results, key=lambda x: x['down'], reverse=True):
    wounded_mark = "✅ YES" if r['wounded'] else ""
    print(f"{r['symbol']:<8} {r['sector']:<16} ${r['price']:<9.2f} {r['down']:<9.1f}% {wounded_mark:<10}")

wounded_count = sum(1 for r in results if r['wounded'])
print("\n" + "="*70)
print(f"WOUNDED PREY AVAILABLE: {wounded_count}")
print("="*70)

if wounded_count >= 3:
    print("\n✅ Have enough thesis-aligned wounded prey for portfolio")
    wounded_list = [r for r in results if r['wounded']]
    print("\nTop picks:")
    for w in sorted(wounded_list, key=lambda x: x['down'], reverse=True)[:6]:
        shares = int(200 / w['price'])  # ~$200 position
        print(f"  {w['symbol']}: {shares} shares @ ${w['price']:.2f} = ${shares * w['price']:.2f}")
else:
    print(f"\n⚠️ Only {wounded_count} wounded prey in Tyr's universe")
    print("Options:")
    print("1. Use the wounded prey we have")
    print("2. Lower 'wounded' threshold to 25%")
    print("3. Wait for better setups")
