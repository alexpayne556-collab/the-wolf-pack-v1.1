#!/usr/bin/env python
# Quick test of scanner
import time
from full_scanner import full_market_scan

print("Starting full market scan...")
start = time.time()
movers = full_market_scan()
elapsed = time.time() - start

print(f"\nScan took {elapsed:.1f} seconds")
print(f"Found {len(movers)} movers\n")

print("Top 10 movers:")
for m in movers[:10]:
    print(f"  {m['ticker']}: ${m['price']:.2f} ({m['change_pct']:+.1f}%) vol {m['volume_ratio']:.1f}x")
