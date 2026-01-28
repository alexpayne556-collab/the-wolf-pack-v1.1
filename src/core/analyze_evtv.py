"""
EVTV Analysis - When did +3,300% move start?
What signals existed BEFORE the run?
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def analyze_evtv():
    print("="*80)
    print("EVTV (+3,300%) - TIMING ANALYSIS")
    print("="*80)
    
    ticker = yf.Ticker('EVTV')
    
    # Get 1 year history
    hist = ticker.history(period='1y')
    
    if hist.empty:
        print("❌ No data available for EVTV")
        return
    
    print("\n📊 PRICE ACTION (Last 60 days):")
    print(hist[['Open', 'High', 'Low', 'Close', 'Volume']].tail(60).to_string())
    
    # Get stock info
    info = ticker.info
    
    print("\n" + "="*80)
    print("EVTV CURRENT FUNDAMENTALS:")
    print("="*80)
    
    float_shares = info.get('floatShares', 0)
    shares_out = info.get('sharesOutstanding', 0)
    
    print(f"\n🎯 SETUP FACTORS:")
    print(f"   Float: {float_shares/1e6:.2f}M")
    print(f"   Shares Out: {shares_out/1e6:.2f}M")
    print(f"   Insider Ownership: {info.get('heldPercentInsiders', 0)*100:.1f}%")
    print(f"   Institutional: {info.get('heldPercentInstitutions', 0)*100:.1f}%")
    
    print(f"\n📊 SQUEEZE POTENTIAL:")
    print(f"   Short Interest: {info.get('shortPercentOfFloat', 0)*100:.1f}%")
    print(f"   Short Ratio: {info.get('shortRatio', 0):.2f} days")
    
    print(f"\n💰 VALUATION:")
    print(f"   Current Price: ${info.get('currentPrice', info.get('regularMarketPrice', 0)):.2f}")
    print(f"   Market Cap: ${info.get('marketCap', 0)/1e6:.2f}M")
    
    # Find the move
    print("\n" + "="*80)
    print("FINDING THE +3,300% MOVE:")
    print("="*80)
    
    # Calculate daily returns
    hist['Returns'] = hist['Close'].pct_change() * 100
    
    # Find biggest single-day moves
    print("\n🚀 BIGGEST SINGLE-DAY MOVES:")
    biggest_days = hist.nlargest(10, 'Returns')[['Close', 'Returns', 'Volume']]
    print(biggest_days.to_string())
    
    # Find the bottom and peak
    bottom_price = hist['Close'].min()
    bottom_date = hist['Close'].idxmin()
    peak_price = hist['Close'].max()
    peak_date = hist['Close'].idxmax()
    
    total_move = ((peak_price - bottom_price) / bottom_price) * 100
    
    print("\n" + "="*80)
    print("THE COMPLETE MOVE:")
    print("="*80)
    print(f"   Bottom: ${bottom_price:.2f} on {bottom_date.strftime('%Y-%m-%d')}")
    print(f"   Peak: ${peak_price:.2f} on {peak_date.strftime('%Y-%m-%d')}")
    print(f"   Total Move: +{total_move:.1f}%")
    print(f"   Duration: {(peak_date - bottom_date).days} days")
    
    # What was setup BEFORE move?
    if bottom_date in hist.index:
        print("\n" + "="*80)
        print(f"SETUP AT BOTTOM ({bottom_date.strftime('%Y-%m-%d')}):")
        print("="*80)
        print(f"   Price: ${bottom_price:.2f}")
        print(f"   Volume: {hist.loc[bottom_date, 'Volume']:,.0f}")
        print(f"   Float: {float_shares/1e6:.2f}M (same as now)")
        print(f"   Insider: {info.get('heldPercentInsiders', 0)*100:.1f}% (likely same)")
    
    # Score it with our system
    print("\n" + "="*80)
    print("WOULD OUR SYSTEM CATCH IT?")
    print("="*80)
    
    # Float score
    float_m = float_shares / 1e6
    if float_m < 1:
        float_score = 20
    elif float_m < 5:
        float_score = 16
    elif float_m < 10:
        float_score = 12
    elif float_m < 50:
        float_score = 8
    else:
        float_score = 0
    
    # Insider score
    insider_pct = info.get('heldPercentInsiders', 0) * 100
    if insider_pct > 50:
        insider_score = 10
    elif insider_pct > 20:
        insider_score = 8
    else:
        insider_score = 0
    
    # Short score
    short_pct = info.get('shortPercentOfFloat', 0) * 100
    if short_pct > 30:
        short_score = 10
    elif short_pct > 20:
        short_score = 8
    elif short_pct > 10:
        short_score = 6
    else:
        short_score = 0
    
    total_score = float_score + insider_score + short_score
    
    print(f"\n🎯 SETUP SCORE (BEFORE move):")
    print(f"   Float: {float_score}/20 pts ({float_m:.1f}M)")
    print(f"   Insider: {insider_score}/20 pts ({insider_pct:.1f}%)")
    print(f"   Short: {short_score}/10 pts ({short_pct:.1f}%)")
    print(f"   Catalyst: ???/10 pts (need to research trigger)")
    print(f"   TOTAL (partial): {total_score}/70 pts")
    
    if total_score >= 35:
        print(f"\n   ✅ YES - Would score TIER 2 or higher")
    elif total_score >= 20:
        print(f"\n   ⚠️  MAYBE - Would make TIER 3 watchlist")
    else:
        print(f"\n   ❌ NO - Score too low")


if __name__ == '__main__':
    analyze_evtv()
