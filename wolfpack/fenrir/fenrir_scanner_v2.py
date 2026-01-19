#!/usr/bin/env python3
"""
Fenrir Scanner V2 - Find SETUPS not RESULTS
Fixed to stop encouraging chasing extended stocks
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Top tickers - high volume, real catalysts
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


def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    if len(prices) < period + 1:
        return None
    
    deltas = prices.diff()
    gain = deltas.where(deltas > 0, 0)
    loss = -deltas.where(deltas < 0, 0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1] if not rsi.empty else None


def analyze_ticker(ticker: str) -> Optional[Dict]:
    """
    Deep analysis - Find SETUPS not RESULTS
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get 1 year for 52-week high/low and moving averages
        hist = stock.history(period='1y', timeout=5)
        
        if len(hist) < 30:
            return None
        
        # Current metrics
        current_price = hist['Close'].iloc[-1]
        price_7d = hist['Close'].iloc[-5] if len(hist) >= 5 else hist['Close'].iloc[0]
        price_30d = hist['Close'].iloc[-21] if len(hist) >= 21 else hist['Close'].iloc[0]
        
        # % changes
        change_7d = ((current_price - price_7d) / price_7d * 100)
        change_30d = ((current_price - price_30d) / price_30d * 100)
        
        # 52-week range
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()
        distance_from_high = ((current_price - high_52w) / high_52w * 100)
        distance_from_low = ((current_price - low_52w) / low_52w * 100)
        
        # Moving averages
        ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else None
        ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else None
        ma_200 = hist['Close'].rolling(window=200).mean().iloc[-1] if len(hist) >= 200 else None
        
        # RSI
        rsi = calculate_rsi(hist['Close'])
        
        # Volume
        volume = hist['Volume'].iloc[-1]
        avg_volume = hist['Volume'].mean()
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1
        
        # === CRITICAL: FILTER OUT EXTENDED STOCKS ===
        # If stock already ran hard AND overbought, it's TOO LATE
        if change_30d > 30 and rsi and rsi > 70:
            signal_type = "TOO_LATE"
            reasoning = f"Extended: +{change_30d:.1f}% in 30d with RSI {rsi:.0f} (overbought). Move already happened."
            setup_score = 0
            return {
                'ticker': ticker,
                'signal_type': signal_type,
                'setup_score': setup_score,
                'price': current_price,
                'change_7d': change_7d,
                'change_30d': change_30d,
                'distance_from_high': distance_from_high,
                'rsi': rsi,
                'reasoning': reasoning
            }
        
        # === TREND POSITION DETECTION ===
        trend_position = "UNKNOWN"
        
        if ma_200 and current_price > ma_200:
            # In uptrend
            if distance_from_high > -10:
                trend_position = "LATE"  # Near highs, could be extended
            elif distance_from_high > -25:
                trend_position = "MIDDLE"  # Room to run
            else:
                trend_position = "EARLY"  # Beaten down but trend up
        else:
            trend_position = "DOWNTREND"
        
        # === SETUP DETECTION ===
        signal_type = "AVOID"
        reasoning = ""
        setup_score = 0
        
        # Pattern 1: PULLBACK IN UPTREND (Highest probability)
        if (trend_position in ["EARLY", "MIDDLE"] and 
            change_7d < -5 and change_7d > -20 and  # Pullback but not breaking down
            change_30d > 10 and  # Still in uptrend
            rsi and rsi < 60):  # Not overbought
            
            signal_type = "SETUP_PULLBACK"
            reasoning = f"Pullback in uptrend: {change_7d:.1f}% (7d) but {change_30d:.1f}% (30d) trend intact. RSI {rsi:.0f}."
            setup_score = 70
            
            # Bonus for volume confirmation
            if volume_ratio < 0.7:  # Low volume on pullback = healthy
                setup_score += 10
                reasoning += " Low volume pullback (healthy)."
        
        # Pattern 2: WOUNDED PREY (Core strategy)
        elif (distance_from_high < -30 and  # Down 30%+ from highs
              ma_200 and current_price > ma_200 and  # But above 200 DMA (trend intact)
              change_7d > 0):  # Starting to bounce
            
            signal_type = "SETUP_WOUNDED"
            reasoning = f"Wounded prey: {distance_from_high:.1f}% from highs but above 200 DMA. Starting bounce."
            setup_score = 65
        
        # Pattern 3: BREAKOUT SETUP (At resistance)
        elif (ma_50 and current_price > ma_50 and
              distance_from_high > -15 and distance_from_high < -5 and  # Near highs but not at
              volume_ratio > 1.5):  # Volume increasing
            
            signal_type = "SETUP_BREAKOUT"
            reasoning = f"Near resistance with volume. {distance_from_high:.1f}% from highs, volume {volume_ratio:.1f}x."
            setup_score = 60
        
        # Pattern 4: STRONG MOMENTUM EARLY (Just started)
        elif (change_7d > 10 and change_30d < 20 and  # Strong week, not extended month
              rsi and rsi < 65):  # Not overbought yet
            
            signal_type = "SETUP_MOMENTUM"
            reasoning = f"Early momentum: +{change_7d:.1f}% (7d) but only +{change_30d:.1f}% (30d). RSI {rsi:.0f}."
            setup_score = 55
        
        # === KEY LEVELS ===
        # Support: Recent swing low or 50 DMA
        support_level = None
        if ma_50:
            support_level = min(ma_50, hist['Low'].iloc[-20:].min())
        
        # Resistance: Recent swing high
        resistance_level = hist['High'].iloc[-20:].max()
        
        # Stop loss: Below support
        stop_loss = support_level * 0.97 if support_level else current_price * 0.85
        
        return {
            'ticker': ticker,
            'signal_type': signal_type,
            'setup_score': setup_score,
            'price': current_price,
            'change_7d': change_7d,
            'change_30d': change_30d,
            'distance_from_high': distance_from_high,
            'distance_from_low': distance_from_low,
            'rsi': rsi,
            'ma_20': ma_20,
            'ma_50': ma_50,
            'ma_200': ma_200,
            'volume_ratio': volume_ratio,
            'trend_position': trend_position,
            'support_level': support_level,
            'resistance_level': resistance_level,
            'stop_loss': stop_loss,
            'reasoning': reasoning
        }
        
    except Exception as e:
        return None


def scan_parallel() -> List[Dict]:
    """
    Scan market in PARALLEL - find setups
    """
    print(f"🔍 Scanning {len(SCAN_UNIVERSE)} tickers for SETUPS (not results)...\n")
    
    results = []
    completed = 0
    total = len(SCAN_UNIVERSE)
    
    # Scan 10 at once
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(analyze_ticker, ticker): ticker 
                           for ticker in SCAN_UNIVERSE}
        
        for future in as_completed(future_to_ticker):
            completed += 1
            if completed % 10 == 0:
                print(f"   Progress: {completed}/{total}...")
            
            result = future.result()
            if result and result['setup_score'] > 0:
                results.append(result)
    
    print(f"\n   ✅ Found {len(results)} setups\n")
    
    # Sort by setup score
    results.sort(key=lambda x: x['setup_score'], reverse=True)
    
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
    """Show SETUPS with full context"""
    if not results:
        print("❌ No setups found right now (market extended)")
        return
    
    print("=" * 90)
    print("🎯 POTENTIAL SETUPS - POSITIONED BEFORE THE MOVE")
    print("=" * 90)
    
    # Group by signal type
    pullbacks = [r for r in results if r['signal_type'] == 'SETUP_PULLBACK']
    wounded = [r for r in results if r['signal_type'] == 'SETUP_WOUNDED']
    breakouts = [r for r in results if r['signal_type'] == 'SETUP_BREAKOUT']
    momentum = [r for r in results if r['signal_type'] == 'SETUP_MOMENTUM']
    
    if pullbacks:
        print("\n🔄 PULLBACK IN UPTREND (Highest probability):")
        for r in pullbacks[:5]:
            sector = categorize(r['ticker'])
            print(f"\n   {r['ticker']} - ${r['price']:.2f} ({sector})")
            print(f"   Score: {r['setup_score']}/100")
            print(f"   {r['reasoning']}")
            print(f"   Entry: ${r['price']:.2f} | Stop: ${r['stop_loss']:.2f} ({((r['stop_loss']/r['price']-1)*100):.1f}%)")
            if r['resistance_level']:
                print(f"   Target: ${r['resistance_level']:.2f} ({((r['resistance_level']/r['price']-1)*100):.1f}%)")
    
    if wounded:
        print("\n🦌 WOUNDED PREY (Core strategy):")
        for r in wounded[:5]:
            sector = categorize(r['ticker'])
            print(f"\n   {r['ticker']} - ${r['price']:.2f} ({sector})")
            print(f"   Score: {r['setup_score']}/100")
            print(f"   {r['reasoning']}")
            print(f"   Entry: ${r['price']:.2f} | Stop: ${r['stop_loss']:.2f}")
    
    if breakouts:
        print("\n📈 BREAKOUT SETUPS:")
        for r in breakouts[:5]:
            sector = categorize(r['ticker'])
            print(f"\n   {r['ticker']} - ${r['price']:.2f} ({sector})")
            print(f"   Score: {r['setup_score']}/100")
            print(f"   {r['reasoning']}")
    
    if momentum:
        print("\n⚡ EARLY MOMENTUM:")
        for r in momentum[:5]:
            sector = categorize(r['ticker'])
            print(f"\n   {r['ticker']} - ${r['price']:.2f} ({sector})")
            print(f"   Score: {r['setup_score']}/100")
            print(f"   {r['reasoning']}")
    
    print("\n" + "=" * 90)
    print("💡 WHAT TO DO:")
    print("   1. Research top setups (check catalysts, insider activity)")
    print("   2. These are EARLY - not chasing what already ran")
    print("   3. Stop loss levels provided (know your risk)")
    print("=" * 90)


if __name__ == "__main__":
    print("\n🐺 FENRIR SCANNER V2 - SETUPS NOT RESULTS")
    print("=" * 90)
    print("Finding opportunities BEFORE they run (not after)...")
    print("=" * 90 + "\n")
    
    start = datetime.now()
    results = scan_parallel()
    elapsed = (datetime.now() - start).total_seconds()
    
    display_results(results)
    
    print(f"\n⚡ Scanned {len(SCAN_UNIVERSE)} tickers in {elapsed:.1f} seconds")
