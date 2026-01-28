#!/usr/bin/env python3
"""
SIMPLE ALPACA TRADE SYNC - Automated version
Imports your Alpaca trade history with smart defaults
"""

import os
import sys
from pathlib import Path

# Load .env from root
root_env = Path(__file__).parent.parent / '.env'
if root_env.exists():
    from dotenv import load_dotenv
    load_dotenv(root_env)

# Change to services directory to use alpaca_trade_sync
os.chdir(Path(__file__).parent / 'services')
sys.path.insert(0, str(Path(__file__).parent))

from services.alpaca_trade_sync import AlpacaTradeSync

print("=" * 70)
print("🐺 ALPACA TRADE SYNC - AUTOMATED VERSION")
print("=" * 70)
print("\nImporting from PAPER account (last 90 days)...")
print()

# Initialize sync (paper trading by default)
sync = AlpacaTradeSync(paper_trading=True)

# Run sync with defaults
result = sync.sync_all(days_back=90)

if result['success']:
    print("\n" + "=" * 70)
    print("✅ SYNC COMPLETE!")
    print("=" * 70)
    print(f"\n📊 Results:")
    print(f"   Orders fetched: {result['orders_fetched']}")
    print(f"   Trades matched: {result['trades_matched']}")
    print(f"   Trades imported: {result['trades_imported']}")
    
    if result.get('patterns'):
        patterns = result['patterns']
        print(f"\n💡 YOUR TRADING PATTERNS:")
        print(f"   Win Rate: {patterns.get('win_rate', 'N/A')}")
        print(f"   Avg Winner: {patterns.get('avg_winner', 'N/A')}")
        print(f"   Avg Loser: {patterns.get('avg_loser', 'N/A')}")
        print(f"   Avg Hold Time: {patterns.get('avg_hold_time', 'N/A')}")
        
        best_tickers = patterns.get('best_tickers', [])
        if best_tickers:
            print(f"\n   Your Best Tickers:")
            for ticker_data in best_tickers[:3]:
                print(f"   • {ticker_data}")
    
    print("\n" + "=" * 70)
    print("🐺 THE WOLF NOW KNOWS YOUR STYLE FROM DAY 1!")
    print("=" * 70)
else:
    print("\n❌ Sync failed. Check error messages above.")
