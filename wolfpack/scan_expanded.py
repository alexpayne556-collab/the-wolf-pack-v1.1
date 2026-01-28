"""
Expand the scan - check MORE tickers in approved sectors
Criteria might be too strict. Let's see what's CLOSE to wounded prey.
"""
import yfinance as yf

print("="*80)
print("🐺 EXPANDED THESIS-ALIGNED SCAN")
print("="*80)

# Expanded universe - more tickers in approved sectors
EXPANDED_UNIVERSE = {
    'defense': ['KTOS', 'LMT', 'RTX', 'NOC', 'LHX', 'HII', 'AVAV', 'TXT', 'GD', 'BA'],
    'space': ['RKLB', 'LUNR', 'ASTS', 'PL', 'SPCE'],
    'nuclear': ['UUUU', 'UEC', 'DNN', 'UROY', 'CCJ', 'LEU', 'NXE'],
    'biotech': ['IBRX', 'NTLA', 'CRSP', 'MRNA', 'VRTX', 'SRPT', 'IONS', 'ARWR', 'EDIT', 'BEAM', 'VERV', 'BLUE', 'SANA'],
    'semiconductors': ['MU', 'AMD', 'INTC', 'QCOM', 'MRVL', 'ON', 'MPWR'],
    'ai_infrastructure': ['AI', 'PLTR', 'SNOW', 'DDOG', 'PATH', 'S'],
}

all_tickers = []
ticker_sectors = {}
for sector, tickers in EXPANDED_UNIVERSE.items():
    all_tickers.extend(tickers)
    for t in tickers:
        ticker_sectors[t] = sector

print(f"\nScanning {len(all_tickers)} tickers...")
print()

candidates = []

for symbol in all_tickers:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period='1mo')
        
        current = info.get('currentPrice') or info.get('regularMarketPrice')
        high_52 = info.get('fiftyTwoWeekHigh')
        low_52 = info.get('fiftyTwoWeekLow')
        mcap = info.get('marketCap', 0)
        avg_vol = info.get('averageVolume10days', 0)
        
        if not current or not high_52:
            continue
        
        pct_down = ((high_52 - current) / high_52) * 100
        pct_from_low = ((current - low_52) / low_52) * 100 if low_52 else 0
        
        # RELAXED criteria - just show what's available
        if pct_down >= 25 and 1 <= current <= 100 and avg_vol >= 300_000:
            
            # Get recent momentum
            five_day_change = 0
            if len(hist) >= 6:
                five_days_ago = hist['Close'].iloc[-6]
                five_day_change = ((current - five_days_ago) / five_days_ago) * 100
            
            candidates.append({
                'symbol': symbol,
                'sector': ticker_sectors[symbol],
                'current': current,
                'high_52': high_52,
                'pct_down': pct_down,
                'pct_from_low': pct_from_low,
                'five_day': five_day_change,
                'mcap_b': mcap / 1_000_000_000 if mcap else 0,
                'vol_m': avg_vol / 1_000_000,
            })
            
    except Exception as e:
        continue

candidates.sort(key=lambda x: x['pct_down'], reverse=True)

print("="*90)
print(f"THESIS-ALIGNED CANDIDATES (ANY down 25%+)")
print("="*90)
print(f"\n{'Ticker':<8} {'Sector':<16} {'Price':<8} {'Down%':<8} {'OffLow%':<10} {'5D%':<8} {'MCap':<8}")
print("-"*90)

for c in candidates[:20]:
    print(f"{c['symbol']:<8} {c['sector']:<16} ${c['current']:<7.2f} {c['pct_down']:<7.1f}% {c['pct_from_low']:<9.1f}% {c['five_day']:+7.1f}% ${c['mcap_b']:<7.2f}B")

print("\n" + "="*90)
print("\nTOP PICKS FOR $1,400 PORTFOLIO (checking affordability):")
print("-"*90)

# Filter for affordable + decent setup
affordable = [c for c in candidates if 2 <= c['current'] <= 40 and c['pct_down'] >= 30 and c['pct_from_low'] >= 10]

if affordable:
    print(f"\n{'Ticker':<8} {'Sector':<16} {'Price':<8} {'Down%':<8} {'Status':<20}")
    print("-"*90)
    for a in affordable[:10]:
        status = "BOUNCING" if a['five_day'] > 5 else "FLAT" if a['five_day'] > -2 else "STILL FALLING"
        print(f"{a['symbol']:<8} {a['sector']:<16} ${a['current']:<7.2f} {a['pct_down']:<7.1f}% {status:<20}")
else:
    print("\n⚠️ Market might not have many wounded prey right now")
    print("Consider: Lower the 'down%' threshold OR wait for better setups")

print("\n" + "="*90)
