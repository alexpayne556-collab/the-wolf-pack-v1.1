#!/usr/bin/env python3
"""
Fenrir Fast Scanner - Parallel market scanning for NEW opportunities
Finds stocks to REPLACE weak positions
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Top 50 REAL money makers - high volume, real catalysts
SCAN_UNIVERSE = [
    # AI MEGA CAPS
    'NVDA', 'AMD', 'MSFT', 'GOOGL', 'META', 'TSLA', 'AAPL',
    
    # AI PURE PLAYS  
    'PLTR', 'ARM', 'SMCI', 'AVGO',
    
    # QUANTUM
    'IONQ', 'RGTI', 'QBTS',
    
    # SEMICONDUCTORS
    'TSM', 'INTC', 'QCOM', 'AMAT', 'ASML',
    
    # BIOTECH MOMENTUM
    'MRNA', 'BNTX', 'GILD', 'VRTX', 'CRSP',
    
    # DEFENSE
    'LMT', 'RTX', 'NOC', 'AVAV', 'RCAT', 'ASTS',
    
    # URANIUM
    'CCJ', 'DNN', 'NXE', 'UUUU', 'UEC', 'LEU',
    
    # CRYPTO
    'MSTR', 'RIOT', 'MARA', 'COIN', 'CLSK',
    
    # SPACE
    'RKLB', 'LUNR',
    
    # CLOUD/CYBER
    'SNOW', 'CRWD', 'NET', 'DDOG'
]


def quick_score(ticker: str) -> Dict:
    """
    Quick momentum score - FAST
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo', timeout=5)
        
        if len(hist) < 5:
            return None
        
        current_price = hist['Close'].iloc[-1]
        price_7d = hist['Close'].iloc[-5] if len(hist) >= 5 else hist['Close'].iloc[0]
        price_30d = hist['Close'].iloc[0]
        
        change_7d = ((current_price - price_7d) / price_7d * 100)
        change_30d = ((current_price - price_30d) / price_30d * 100)
        
        volume = hist['Volume'].mean()
        
        # Momentum score
        score = 0
        
        # 7-day (most important)
        if change_7d > 15:
            score += 3
        elif change_7d > 7:
            score += 2
        elif change_7d > 3:
            score += 1
        elif change_7d < -10:
            score -= 2
        
        # 30-day trend
        if change_30d > 20:
            score += 2
        elif change_30d > 10:
            score += 1
        elif change_30d < -20:
            score -= 2
        
        # Volume (liquidity)
        if volume < 100000:
            score -= 1
        
        return {
            'ticker': ticker,
            'score': score,
            'price': current_price,
            'change_7d': change_7d,
            'change_30d': change_30d,
            'volume': volume
        }
        
    except:
        return None


def scan_parallel() -> List[Dict]:
    """
    Scan market in PARALLEL - 10x faster
    """
    print(f"🔍 Scanning {len(SCAN_UNIVERSE)} tickers in parallel...\n")
    
    results = []
    completed = 0
    total = len(SCAN_UNIVERSE)
    
    # Scan 10 at once
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(quick_score, ticker): ticker 
                           for ticker in SCAN_UNIVERSE}
        
        for future in as_completed(future_to_ticker):
            completed += 1
            if completed % 10 == 0:
                print(f"   Progress: {completed}/{total}...")
            
            result = future.result()
            if result and result['score'] >= 3:
                results.append(result)
    
    print(f"\n   ✅ Found {len(results)} opportunities\n")
    
    # Sort by score then 7d change
    results.sort(key=lambda x: (x['score'], x['change_7d']), reverse=True)
    
    return results


def categorize(ticker: str) -> str:
    """Sector tag"""
    sectors = {
        'AI/Chips': ['NVDA', 'AMD', 'PLTR', 'ARM', 'SMCI', 'AVGO', 'TSM', 'INTC', 'QCOM', 'AMAT', 'ASML'],
        'Quantum': ['IONQ', 'RGTI', 'QBTS'],
        'Biotech': ['MRNA', 'BNTX', 'GILD', 'VRTX', 'CRSP'],
        'Defense': ['LMT', 'RTX', 'NOC', 'AVAV', 'RCAT', 'ASTS'],
        'Uranium': ['CCJ', 'DNN', 'NXE', 'UUUU', 'UEC', 'LEU'],
        'Crypto': ['MSTR', 'RIOT', 'MARA', 'COIN', 'CLSK'],
        'Space': ['RKLB', 'LUNR'],
        'Cloud': ['SNOW', 'CRWD', 'NET', 'DDOG']
    }
    
    for sector, tickers in sectors.items():
        if ticker in tickers:
            return sector
    return 'Other'


def display_results(results: List[Dict]):
    """Show opportunities by category"""
    if not results:
        print("❌ No strong momentum found right now")
        return
    
    print("=" * 80)
    print("🔥 TOP OPPORTUNITIES - REPLACEMENT CANDIDATES")
    print("=" * 80)
    
    # Group by score
    running_hot = [r for r in results if r['score'] >= 5]
    strong = [r for r in results if 3 <= r['score'] < 5]
    
    if running_hot:
        print("\n🔥 RUNNING HOT (Score ≥5) - BUY NOW:")
        for r in running_hot[:10]:
            sector = categorize(r['ticker'])
            print(f"   {r['ticker']:6} ${r['price']:8.2f} | 7d: {r['change_7d']:+6.1f}% | 30d: {r['change_30d']:+6.1f}% | {sector}")
    
    if strong:
        print("\n📈 STRONG MOMENTUM (Score 3-4) - WATCH:")
        for r in strong[:10]:
            sector = categorize(r['ticker'])
            print(f"   {r['ticker']:6} ${r['price']:8.2f} | 7d: {r['change_7d']:+6.1f}% | 30d: {r['change_30d']:+6.1f}% | {sector}")
    
    print("\n" + "=" * 80)
    print("💡 WHAT TO DO:")
    print("   1. Research top scorers (check thesis, catalysts)")
    print("   2. Compare to your weak positions")
    print("   3. Consider: Sell weak → Buy running")
    print("=" * 80)


if __name__ == "__main__":
    print("\n🐺 FENRIR FAST SCANNER - Parallel Mode")
    print("=" * 80)
    print("Finding REPLACEMENTS for weak positions...")
    print("=" * 80 + "\n")
    
    start = datetime.now()
    results = scan_parallel()
    elapsed = (datetime.now() - start).total_seconds()
    
    display_results(results)
    
    print(f"\n⚡ Scanned {len(SCAN_UNIVERSE)} tickers in {elapsed:.1f} seconds")
    print()
