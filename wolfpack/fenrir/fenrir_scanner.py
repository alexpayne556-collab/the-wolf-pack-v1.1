#!/usr/bin/env python3
"""
Fenrir Scanner - Find NEW opportunities in the market
Scans popular tickers, applies same health + thesis logic
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict
import sys

# Universe of tickers to scan (high volume, REAL money makers)
SCAN_UNIVERSE = [
    # AI/Tech MEGA CAPS
    'NVDA', 'AMD', 'MSFT', 'GOOGL', 'META', 'TSLA', 'AAPL', 'AMZN', 'NFLX',
    
    # AI/CHIPS PURE PLAYS
    'PLTR', 'AVGO', 'ARM', 'SMCI', 'IONQ', 'RGTI', 'QBTS', 'QUBT',
    
    # SEMICONDUCTORS
    'TSM', 'INTC', 'QCOM', 'AMAT', 'LRCX', 'KLAC', 'ASML', 'NVDL',
    
    # BIOTECH RUNNERS
    'MRNA', 'BNTX', 'GILD', 'REGN', 'VRTX', 'CRSP', 'EDIT', 'BEAM', 'NTLA',
    'SRRK', 'LEGN', 'ARVN', 'BLUE', 'FATE',
    
    # DEFENSE/AEROSPACE
    'LMT', 'RTX', 'NOC', 'GD', 'BA', 'AVAV', 'RCAT', 'ASTS',
    
    # URANIUM/NUCLEAR
    'CCJ', 'DNN', 'NXE', 'UUUU', 'UEC', 'URNM', 'URA', 'LEU', 'BWXT',
    
    # CRYPTO PLAYS
    'MSTR', 'RIOT', 'MARA', 'COIN', 'HOOD', 'CLSK', 'CIFR', 'BTBT', 'HUT',
    
    # EV/BATTERY
    'RIVN', 'LCID', 'CHPT', 'BLNK', 'ALB', 'LAC',
    
    # SPACE/SATELLITE  
    'RKLB', 'SPCE', 'LUNR', 'PL',
    
    # GROWTH/MOMENTUM
    'SHOP', 'SQ', 'RBLX', 'SNAP', 'DKNG', 'ABNB', 'UBER', 'LYFT',
    'APP', 'SNOW', 'NET', 'DDOG', 'ZS', 'CRWD', 'S', 'MDB',
    
    # ENERGY/OIL
    'XOM', 'CVX', 'COP', 'SLB', 'HAL', 'OXY',
    
    # SMALL CAP MOMENTUM
    'CELH', 'CVNA', 'W', 'UPST', 'SOFI', 'OPEN', 'AFRM',
    
    # CHINA TECH
    'BABA', 'PDD', 'JD', 'BIDU', 'NIO', 'XPEV', 'LI',
    
    # PHARMA CATALYSTS
    'PFE', 'ABBV', 'LLY', 'NVO', 'BMY', 'MRK', 'JNJ'
]

def quick_score(ticker: str) -> Dict:
    """
    Quick health score for a ticker
    Returns: {'ticker', 'score', 'price', 'change_7d', 'change_30d', 'volume'}
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo', timeout=3)  # 3 second timeout
        
        if len(hist) < 5:
            return None
        
        current_price = hist['Close'].iloc[-1]
        price_7d_ago = hist['Close'].iloc[-5] if len(hist) >= 5 else hist['Close'].iloc[0]
        price_30d_ago = hist['Close'].iloc[0]
        
        change_7d = ((current_price - price_7d_ago) / price_7d_ago * 100)
        change_30d = ((current_price - price_30d_ago) / price_30d_ago * 100)
        
        avg_volume = hist['Volume'].mean()
        
        # Simple momentum score
        score = 0
        
        # 7-day momentum (most important)
        if change_7d > 15:
            score += 3
        elif change_7d > 7:
            score += 2
        elif change_7d > 3:
            score += 1
        elif change_7d < -10:
            score -= 2
        elif change_7d < -5:
            score -= 1
        
        # 30-day trend
        if change_30d > 20:
            score += 2
        elif change_30d > 10:
            score += 1
        elif change_30d < -20:
            score -= 2
        
        # Volume check (liquidity)
        if avg_volume < 100000:
            score -= 1  # Too illiquid
        
        return {
            'ticker': ticker,
            'score': score,
            'price': current_price,
            'change_7d': change_7d,
            'change_30d': change_30d,
            'volume': avg_volume
        }
        
    except Exception as e:
        return None


def scan_market() -> List[Dict]:
    """
    Scan the universe for opportunities - FAST batch mode
    """
    print("🔍 Scanning market for opportunities...")
    print(f"   Checking {len(SCAN_UNIVERSE)} tickers...\n")
    
    results = []
    total = len(SCAN_UNIVERSE)
    
    # Process in smaller batches to show progress
    batch_size = 20
    for batch_start in range(0, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        batch = SCAN_UNIVERSE[batch_start:batch_end]
        
        print(f"   Progress: {batch_start}/{total}...")
        
        for ticker in batch:
            try:
                result = quick_score(ticker)
                if result and result['score'] >= 3:  # Only keep promising ones
                    results.append(result)
            except:
                pass  # Skip failures silently
    
    print(f"   ✅ Found {len(results)} opportunities\n")
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results


def categorize_by_sector(ticker: str) -> str:
    """Quick sector categorization"""
    
    ai_tech = ['NVDA', 'AMD', 'PLTR', 'MSFT', 'GOOGL', 'META', 'AVGO', 'TSM', 'INTC', 'QCOM', 
               'AMAT', 'LRCX', 'KLAC', 'ARM', 'SMCI', 'IONQ', 'RGTI', 'QBTS', 'QUBT', 
               'AAPL', 'AMZN', 'ASML', 'NVDL']
    biotech = ['MRNA', 'BNTX', 'GILD', 'REGN', 'VRTX', 'CRSP', 'EDIT', 'IBRX', 'BEAM', 
               'NTLA', 'SRRK', 'LEGN', 'ARVN', 'BLUE', 'FATE']
    defense = ['LMT', 'RTX', 'NOC', 'GD', 'BA', 'AVAV', 'RCAT', 'KTOS', 'ASTS']
    uranium = ['CCJ', 'DNN', 'NXE', 'URNM', 'URA', 'UUUU', 'UEC', 'LEU', 'BWXT']
    crypto = ['MSTR', 'RIOT', 'MARA', 'COIN', 'HOOD', 'CLSK', 'CIFR', 'BTBT', 'HUT']
    space = ['RKLB', 'SPCE', 'LUNR', 'PL']
    ev = ['TSLA', 'RIVN', 'LCID', 'CHPT', 'BLNK', 'ALB', 'LAC']
    fintech = ['SQ', 'SOFI', 'AFRM', 'UPST']
    cloud = ['SNOW', 'NET', 'DDOG', 'ZS', 'CRWD', 'S', 'MDB']
    
    if ticker in ai_tech:
        return 'AI/Chips'
    elif ticker in biotech:
        return 'Biotech'
    elif ticker in defense:
        return 'Defense'
    elif ticker in uranium:
        return 'Uranium'
    elif ticker in crypto:
        return 'Crypto'
    elif ticker in space:
        return 'Space'
    elif ticker in ev:
        return 'EV/Battery'
    elif ticker in fintech:
        return 'Fintech'
    elif ticker in cloud:
        return 'Cloud/Cyber'
    else:
        return 'Growth'


def find_opportunities():
    """Main scanner function"""
    results = scan_market()
    
    if not results:
        print("❌ No strong opportunities found right now")
        return
    
    print("=" * 70)
    print("🔥 TOP OPPORTUNITIES (Score ≥3)")
    print("=" * 70)
    
    for r in results[:15]:  # Top 15
        sector = categorize_by_sector(r['ticker'])
        
        # Status emoji
        if r['score'] >= 5:
            status = "🔥 RUNNING HOT"
        elif r['score'] >= 3:
            status = "📈 MOMENTUM"
        else:
            status = "🟢 EMERGING"
        
        print(f"\n{r['ticker']:6} | Score: {r['score']:+2d} | ${r['price']:.2f} | {sector}")
        print(f"       7d: {r['change_7d']:+6.1f}% | 30d: {r['change_30d']:+6.1f}% | {status}")
    
    print("\n" + "=" * 70)
    print("📊 BREAKDOWN:")
    
    hot = [r for r in results if r['score'] >= 5]
    momentum = [r for r in results if 3 <= r['score'] < 5]
    
    if hot:
        print(f"\n🔥 RUNNING HOT ({len(hot)}): {', '.join([r['ticker'] for r in hot[:10]])}")
    if momentum:
        print(f"📈 MOMENTUM ({len(momentum)}): {', '.join([r['ticker'] for r in momentum[:10]])}")
    
    print("\n" + "=" * 70)
    print("\nℹ️  This scans momentum only. For deep thesis analysis,")
    print("   research the top scorers manually or use fenrir_chat.py")
    print("=" * 70)


if __name__ == "__main__":
    print("\n🐺 FENRIR MARKET SCANNER")
    print("=" * 70)
    print("Finding NEW opportunities you don't own yet...")
    print("=" * 70 + "\n")
    
    find_opportunities()
    
    print("\n")
