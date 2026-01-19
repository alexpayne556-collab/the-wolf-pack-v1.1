#!/usr/bin/env python3
"""Quick test of IBRX catalyst detection"""

from market_data import get_stock_data
from news_fetcher import get_company_news
from sec_fetcher import get_8k_filings, get_insider_trades
import config

print("\n🐺 Testing IBRX Catalyst Detection\n")
print("=" * 60)

# Get market data
print("\n1. MARKET DATA:")
data = get_stock_data('IBRX')
if data:
    print(f"   Price: ${data['price']:.2f}")
    print(f"   Move: {data['change_pct']:+.2f}%")
    print(f"   Volume: {data['volume_ratio']:.1f}x average")
else:
    print("   ❌ Failed to fetch")

# Get news
print("\n2. NEWS (last 24 hours):")
news = get_company_news('IBRX', days=1)
if news:
    print(f"   Found {len(news)} articles:")
    for item in news[:3]:
        print(f"   • {item['headline']}")
        print(f"     Source: {item['source']}")
else:
    print("   No news found")

# Get SEC filings
print("\n3. SEC FILINGS:")
filings_8k = get_8k_filings('IBRX', count=5)
if filings_8k:
    print(f"   Found {len(filings_8k)} 8-K filings:")
    for filing in filings_8k:
        print(f"   • {filing.get('form', '8-K')}: {filing.get('description', 'N/A')[:60]}")
else:
    print("   No 8-Ks found")

insider = get_insider_trades('IBRX', days=30)
if insider:
    print(f"   Found {len(insider)} insider trades")
else:
    print("   No insider trades")

print("\n" + "=" * 60)
print("\n✅ Catalyst detection test complete\n")
