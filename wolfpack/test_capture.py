#!/usr/bin/env python3
"""
Quick test to show what data gets captured for 3 stocks
"""

import sys
import sqlite3
from wolfpack_recorder import get_stock_data
from config import DB_PATH, TICKER_TO_SECTOR

# Test on 3 of your holdings
test_tickers = ['MU', 'KTOS', 'BBAI']

print("\n🐺 TESTING WOLF PACK DATA CAPTURE 🐺\n")
print("=" * 80)

for ticker in test_tickers:
    sector = TICKER_TO_SECTOR[ticker]
    print(f"\n📊 {ticker} ({sector})")
    print("-" * 80)
    
    record = get_stock_data(ticker, sector)
    
    if record:
        print(f"✅ DATA CAPTURED:")
        print(f"\n💰 PRICE ACTION:")
        print(f"   Open:  ${record['open']:.2f}")
        print(f"   High:  ${record['high']:.2f}")
        print(f"   Low:   ${record['low']:.2f}")
        print(f"   Close: ${record['close']:.2f}")
        print(f"   Daily Return: {record['daily_return_pct']:+.2f}%")
        print(f"   Intraday Range: {record['intraday_range_pct']:.2f}%")
        print(f"   Gap: {record['gap_pct']:+.2f}%")
        
        print(f"\n📊 VOLUME:")
        print(f"   Today: {record['volume']:,}")
        print(f"   20-Day Avg: {record['avg_volume_20d']:,}")
        print(f"   Volume Ratio: {record['volume_ratio']:.2f}x")
        print(f"   Dollar Volume: ${record['dollar_volume']:,.0f}")
        
        print(f"\n📈 POSITION:")
        print(f"   From 52W High: {record['dist_52w_high_pct']:+.1f}%")
        print(f"   From 52W Low: {record['dist_52w_low_pct']:+.1f}%")
        print(f"   5-Day Return: {record['return_5d']:+.1f}%")
        print(f"   20-Day Return: {record['return_20d']:+.1f}%")
        print(f"   60-Day Return: {record['return_60d']:+.1f}%")
        
        print(f"\n🔥 MOMENTUM:")
        print(f"   Consecutive Green: {record['consecutive_green']} days")
        print(f"   Consecutive Red: {record['consecutive_red']} days")
        print(f"   Big Move? {record['is_big_move']} ({record['move_direction']} {record['move_size']}%)")
        
        print(f"\n📉 TECHNICALS:")
        print(f"   SMA-20: ${record['sma_20']:.2f} (Above: {record['above_sma_20']})")
        print(f"   SMA-50: ${record['sma_50']:.2f} (Above: {record['above_sma_50']})")
        print(f"   SMA-200: ${record['sma_200']:.2f} (Above: {record['above_sma_200']})")
        print(f"   RSI-14: {record['rsi_14']:.1f}")
        
    else:
        print("❌ Failed to get data")
    
    print("=" * 80)

print(f"\n\n🧠 THIS DATA × 99 STOCKS × EVERY DAY = YOUR TRADING INTELLIGENCE")
print(f"📊 Database: {DB_PATH}")
print("\n🐺 LLHR\n")
