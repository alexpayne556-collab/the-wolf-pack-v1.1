#!/usr/bin/env python3
"""
Validate Scanner V2 - Are the setups ACTUALLY good?
"""

import yfinance as yf
from datetime import datetime, timedelta

# Setups the scanner found today
SETUPS_FOUND = [
    {'ticker': 'RGTI', 'type': 'WOUNDED_PREY', 'price': 25.62, 'stop': 20.88},
    {'ticker': 'QBTS', 'type': 'WOUNDED_PREY', 'price': 28.83, 'stop': 23.49},
    {'ticker': 'CLSK', 'type': 'WOUNDED_PREY', 'price': 13.37, 'stop': 9.68},
    {'ticker': 'AMD', 'type': 'EARLY_MOMENTUM', 'price': 231.83, 'stop': None},
]

# Stocks that SHOULD be filtered as TOO_LATE
SHOULD_BE_FILTERED = [
    'MRNA',  # Was +23.6% (7d), +37.1% (30d) in old scanner
    'ASTS',  # Was +17.7% (7d), +87.1% (30d) 
    'RIOT',  # Was +17.0% (7d), +48.5% (30d)
]

def check_setup_quality(setup):
    """Did this setup work out?"""
    try:
        ticker = setup['ticker']
        stock = yf.Ticker(ticker)
        
        # Get recent history
        hist = stock.history(period='5d')
        
        if len(hist) < 2:
            return None
        
        current = hist['Close'].iloc[-1]
        entry = setup['price']
        
        # Calculate from entry to now
        change = ((current - entry) / entry * 100)
        
        # Check if stop would have been hit
        lowest = hist['Low'].min()
        stop_hit = False
        if setup['stop']:
            stop_hit = lowest < setup['stop']
        
        return {
            'ticker': ticker,
            'type': setup['type'],
            'entry': entry,
            'current': current,
            'change': change,
            'stop': setup['stop'],
            'stop_hit': stop_hit,
            'status': 'WINNER' if change > 0 and not stop_hit else 'LOSER' if stop_hit else 'PENDING'
        }
    except:
        return None


def test_too_late_filter():
    """Are extended stocks correctly filtered?"""
    print("\n" + "="*80)
    print("TEST 2: TOO_LATE FILTER - Is it working?")
    print("="*80 + "\n")
    
    for ticker in SHOULD_BE_FILTERED:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1mo')
            
            if len(hist) < 21:
                continue
            
            current = hist['Close'].iloc[-1]
            price_30d = hist['Close'].iloc[0]
            change_30d = ((current - price_30d) / price_30d * 100)
            
            # Calculate RSI
            closes = hist['Close']
            deltas = closes.diff()
            gain = deltas.where(deltas > 0, 0)
            loss = -deltas.where(deltas < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            rsi = (100 - (100 / (1 + rs))).iloc[-1]
            
            should_filter = change_30d > 30 and rsi > 70
            
            print(f"{ticker}:")
            print(f"  30d change: {change_30d:+.1f}%")
            print(f"  RSI: {rsi:.0f}")
            print(f"  Should be filtered: {should_filter}")
            print(f"  {'✅ CORRECT - TOO LATE' if should_filter else '⚠️ MIGHT STILL BE GOOD'}\n")
            
        except:
            continue


def test_stop_losses():
    """Are stop losses realistic?"""
    print("\n" + "="*80)
    print("TEST 3: STOP LOSSES - Are they protecting capital?")
    print("="*80 + "\n")
    
    for setup in SETUPS_FOUND:
        if not setup['stop']:
            continue
        
        ticker = setup['ticker']
        entry = setup['price']
        stop = setup['stop']
        risk_pct = ((stop - entry) / entry * 100)
        
        print(f"{ticker}:")
        print(f"  Entry: ${entry:.2f}")
        print(f"  Stop: ${stop:.2f}")
        print(f"  Risk: {risk_pct:.1f}%")
        
        # Is risk reasonable? (10-20% is typical)
        if risk_pct < -25:
            print(f"  ⚠️ STOP TOO WIDE - Risk is {risk_pct:.1f}%")
        elif risk_pct > -5:
            print(f"  ⚠️ STOP TOO TIGHT - Risk only {risk_pct:.1f}%")
        else:
            print(f"  ✅ REASONABLE - {risk_pct:.1f}% risk")
        print()


if __name__ == "__main__":
    print("\n🐺 SCANNER VALIDATION - Does it ACTUALLY work?")
    print("="*80 + "\n")
    
    print("TEST 1: SETUP QUALITY - Did these work out?")
    print("="*80 + "\n")
    
    results = []
    for setup in SETUPS_FOUND:
        result = check_setup_quality(setup)
        if result:
            results.append(result)
    
    for r in results:
        print(f"{r['ticker']} ({r['type']}):")
        print(f"  Entry: ${r['entry']:.2f}")
        print(f"  Current: ${r['current']:.2f}")
        print(f"  Change: {r['change']:+.1f}%")
        if r['stop']:
            print(f"  Stop hit: {'YES ❌' if r['stop_hit'] else 'NO ✅'}")
        print(f"  Status: {r['status']}")
        print()
    
    # Summary
    winners = len([r for r in results if r['status'] == 'WINNER'])
    losers = len([r for r in results if r['status'] == 'LOSER'])
    pending = len([r for r in results if r['status'] == 'PENDING'])
    
    print(f"SUMMARY: {winners} winners, {losers} losers, {pending} pending")
    print(f"Win rate: {(winners / len(results) * 100) if results else 0:.0f}%")
    
    # Test TOO_LATE filter
    test_too_late_filter()
    
    # Test stop losses
    test_stop_losses()
    
    print("\n" + "="*80)
    print("FINAL VERDICT:")
    print("="*80)
    print("\n⚠️ IMPORTANT: This is just 1 day of data.")
    print("Need to track for 1-2 weeks to see if setups CONSISTENTLY work.")
    print("\nQuestions for Tyr:")
    print("1. Do these setups FEEL right to you?")
    print("2. Would you actually trade them?")
    print("3. Are the stop losses too tight/wide?")
    print("="*80 + "\n")
