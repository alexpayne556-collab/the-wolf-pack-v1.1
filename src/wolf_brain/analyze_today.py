#!/usr/bin/env python3
"""Quick analysis of today's movers"""

from strategies.compression_breakout import CompressionBreakoutStrategy
import yfinance as yf

strategy = CompressionBreakoutStrategy()

# Today's movers
movers = ['ONCY', 'MNMD', 'TNXP', 'RXRX']

for ticker in movers:
    print('='*60)
    print(f'ANALYZING {ticker}')
    print('='*60)
    
    # Check compression
    comp = strategy.check_compression(ticker)
    if comp:
        print(f"Compression Score: {comp['compression_score']}/100")
        print(f"Range before today: {comp['range_pct']:.1f}%")
        print(f"Flat days: {comp['flat_days']}")
        print(f"Volume declining: {comp['vol_declining']}")
        print(f"Was COMPRESSED: {'YES!' if comp['is_compressed'] else 'No'}")
    
    # Get news
    print()
    print("Recent News:")
    try:
        stock = yf.Ticker(ticker)
        news = stock.news[:3] if hasattr(stock, 'news') else []
        for n in news:
            title = n.get('title', 'N/A')[:70]
            print(f"  - {title}...")
    except Exception as e:
        print(f"  No news: {e}")
    
    print()
