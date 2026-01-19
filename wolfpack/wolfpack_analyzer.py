#!/usr/bin/env python3
"""
Wolf Pack Pattern Analyzer
Find what BIG WINNERS looked like BEFORE they exploded
"""

import sqlite3
import pandas as pd
from datetime import datetime
import argparse

from config import DB_PATH, DEFAULT_WINNER_THRESHOLD, DEFAULT_TIMEFRAME

def analyze_winners(threshold=20.0, timeframe=10):
    """
    Find all stocks that gained threshold%+ over timeframe days.
    Then analyze what they looked like the day BEFORE the run started.
    """
    
    print("\n" + "🔬"*30)
    print("WOLF PACK PATTERN ANALYZER")
    print(f"Analyzing {threshold}%+ winners over {timeframe} days")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔬"*30 + "\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    forward_field = f'forward_{timeframe}d'
    
    # Get all winners
    query = f'''
    SELECT *
    FROM daily_records
    WHERE {forward_field} >= ?
    ORDER BY {forward_field} DESC
    '''
    
    df = pd.read_sql_query(query, conn, params=(threshold,))
    
    if len(df) == 0:
        print(f"❌ No winners found with {threshold}%+ return over {timeframe} days")
        print("   Run the system for more days or lower threshold\n")
        conn.close()
        return
    
    print(f"✅ Found {len(df)} winners\n")
    
    # =============================================================================
    # ANALYSIS 1: Color bias (were they green or red the day before?)
    # =============================================================================
    
    print("="*80)
    print("📊 ANALYSIS 1: COLOR BIAS")
    print("="*80)
    
    green_before = df[df['daily_return_pct'] > 0]
    red_before = df[df['daily_return_pct'] <= 0]
    
    print(f"\nGreen day before explosion: {len(green_before)} ({len(green_before)/len(df)*100:.1f}%)")
    print(f"Red day before explosion:   {len(red_before)} ({len(red_before)/len(df)*100:.1f}%)")
    
    if len(green_before) > 0:
        print(f"\n  Avg return when green before:  {green_before[forward_field].mean():+.1f}%")
        print(f"  Avg daily% day before:         {green_before['daily_return_pct'].mean():+.1f}%")
    
    if len(red_before) > 0:
        print(f"\n  Avg return when red before:    {red_before[forward_field].mean():+.1f}%")
        print(f"  Avg daily% day before:         {red_before['daily_return_pct'].mean():+.1f}%")
    
    # =============================================================================
    # ANALYSIS 2: Volume bias
    # =============================================================================
    
    print("\n" + "="*80)
    print("📊 ANALYSIS 2: VOLUME BIAS")
    print("="*80)
    
    print(f"\nAverage volume ratio: {df['volume_ratio'].mean():.2f}x")
    print(f"Median volume ratio:  {df['volume_ratio'].median():.2f}x")
    
    low_vol = df[df['volume_ratio'] < 1.5]
    med_vol = df[(df['volume_ratio'] >= 1.5) & (df['volume_ratio'] < 3.0)]
    high_vol = df[df['volume_ratio'] >= 3.0]
    
    print(f"\nLow volume (<1.5x):     {len(low_vol)} winners, avg {forward_field}: {low_vol[forward_field].mean() if len(low_vol) > 0 else 0:.1f}%")
    print(f"Medium volume (1.5-3x): {len(med_vol)} winners, avg {forward_field}: {med_vol[forward_field].mean() if len(med_vol) > 0 else 0:.1f}%")
    print(f"High volume (3x+):      {len(high_vol)} winners, avg {forward_field}: {high_vol[forward_field].mean() if len(high_vol) > 0 else 0:.1f}%")
    
    # =============================================================================
    # ANALYSIS 3: Extension bias (60d return)
    # =============================================================================
    
    print("\n" + "="*80)
    print("📊 ANALYSIS 3: EXTENSION BIAS")
    print("="*80)
    
    print(f"\nAverage 60d return before explosion: {df['return_60d'].mean():+.1f}%")
    print(f"Median 60d return before explosion:  {df['return_60d'].median():+.1f}%")
    
    compressed = df[df['return_60d'] < 0]
    neutral = df[(df['return_60d'] >= 0) & (df['return_60d'] < 30)]
    extended = df[df['return_60d'] >= 30]
    
    print(f"\nCompressed (60d <0%):    {len(compressed)} winners, avg {forward_field}: {compressed[forward_field].mean() if len(compressed) > 0 else 0:.1f}%")
    print(f"Neutral (60d 0-30%):     {len(neutral)} winners, avg {forward_field}: {neutral[forward_field].mean() if len(neutral) > 0 else 0:.1f}%")
    print(f"Extended (60d >30%):     {len(extended)} winners, avg {forward_field}: {extended[forward_field].mean() if len(extended) > 0 else 0:.1f}%")
    
    # =============================================================================
    # ANALYSIS 4: Sector distribution
    # =============================================================================
    
    print("\n" + "="*80)
    print("📊 ANALYSIS 4: SECTOR DISTRIBUTION")
    print("="*80 + "\n")
    
    sector_counts = df['sector'].value_counts()
    sector_avg_returns = df.groupby('sector')[forward_field].mean()
    
    for sector in sector_counts.index:
        count = sector_counts[sector]
        avg_ret = sector_avg_returns[sector]
        print(f"{sector:12} | {count:3} winners | Avg return: {avg_ret:+6.1f}%")
    
    # =============================================================================
    # ANALYSIS 5: 52-week high/low positioning
    # =============================================================================
    
    print("\n" + "="*80)
    print("📊 ANALYSIS 5: 52-WEEK POSITIONING")
    print("="*80)
    
    print(f"\nAvg distance from 52w high: {df['dist_52w_high_pct'].mean():+.1f}%")
    print(f"Avg distance from 52w low:  {df['dist_52w_low_pct'].mean():+.1f}%")
    
    near_high = df[df['dist_52w_high_pct'] > -10]
    mid_range = df[(df['dist_52w_high_pct'] <= -10) & (df['dist_52w_high_pct'] > -40)]
    wounded = df[df['dist_52w_high_pct'] <= -40]
    
    print(f"\nNear 52w high (<10% away):  {len(near_high)} winners, avg {forward_field}: {near_high[forward_field].mean() if len(near_high) > 0 else 0:.1f}%")
    print(f"Mid-range (10-40% away):    {len(mid_range)} winners, avg {forward_field}: {mid_range[forward_field].mean() if len(mid_range) > 0 else 0:.1f}%")
    print(f"Wounded (40%+ away):        {len(wounded)} winners, avg {forward_field}: {wounded[forward_field].mean() if len(wounded) > 0 else 0:.1f}%")
    
    # =============================================================================
    # ANALYSIS 6: Red streak before reversal
    # =============================================================================
    
    print("\n" + "="*80)
    print("📊 ANALYSIS 6: RED STREAK BEFORE REVERSAL")
    print("="*80)
    
    with_red_streak = df[df['consecutive_red'] > 0]
    
    if len(with_red_streak) > 0:
        print(f"\n{len(with_red_streak)} winners had red streak before explosion")
        print(f"Average consecutive red days: {with_red_streak['consecutive_red'].mean():.1f}")
        print(f"Max consecutive red days: {with_red_streak['consecutive_red'].max():.0f}")
        print(f"Avg return after red streak: {with_red_streak[forward_field].mean():+.1f}%")
    else:
        print("\nNo winners had red streaks before explosion")
    
    # =============================================================================
    # TOP PERFORMERS
    # =============================================================================
    
    print("\n" + "="*80)
    print("🔥 TOP 10 PERFORMERS")
    print("="*80 + "\n")
    
    top_10 = df.nlargest(10, forward_field)
    
    for _, row in top_10.iterrows():
        print(f"{row['ticker']:6} | {row['sector']:10} | {row['date']} | {forward_field}: {row[forward_field]:+6.1f}% | "
              f"Day before: {row['daily_return_pct']:+5.1f}% | Vol: {row['volume_ratio']:.1f}x | 60d: {row['return_60d']:+5.1f}%")
    
    conn.close()
    
    print("\n🐺 Analysis complete - LLHR\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze what big winners looked like before explosion')
    parser.add_argument('--threshold', type=float, default=DEFAULT_WINNER_THRESHOLD, 
                       help=f'Minimum return %% to qualify as winner (default: {DEFAULT_WINNER_THRESHOLD})')
    parser.add_argument('--timeframe', type=int, default=DEFAULT_TIMEFRAME,
                       help=f'Days forward to check (default: {DEFAULT_TIMEFRAME})')
    
    args = parser.parse_args()
    
    analyze_winners(args.threshold, args.timeframe)
