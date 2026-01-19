#!/usr/bin/env python3
"""
🐺 WOLF PACK MASTER SCANNER 🐺

Run this at these times:
- 4:00 AM - Pre-market scan (gaps overnight)
- 9:25 AM - Pre-open scan (last check before open)
- 4:05 PM - After hours scan (catch earnings movers)
- 8:00 PM - Evening scan (late filings)

This finds:
1. Pre-market gaps
2. After-hours movers  
3. Volume spikes
4. Earnings this week
5. SEC 8-K filings
6. Compressed stocks waking up
"""

import yfinance as yf
import pandas as pd
import numpy as np
import urllib.request
import xml.etree.ElementTree as ET
import re
import json
import time
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================
# CONFIGURATION
# ============================================

# Full universe
SCAN_UNIVERSE = [
    # Core holdings
    'KTOS', 'NTLA', 'MU', 'SLV',
    # Space
    'LUNR', 'RKLB', 'RDW', 'PL', 'ASTS', 'BKSY',
    # Nuclear
    'SMR', 'UEC', 'LEU', 'CCJ', 'DNN', 'UUUU', 'NNE', 'OKLO',
    # Defense
    'RCAT', 'PLTR', 'AVAV',
    # Biotech
    'CRSP', 'BEAM', 'EDIT', 'DNLI', 'MRNA', 'BNTX',
    # AI/Quantum
    'SOUN', 'BBAI', 'IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ',
    # Fintech
    'SOFI', 'AFRM', 'UPST', 'NU', 'HOOD',
    # Energy
    'KULR', 'APLD', 'VST', 'CEG',
    # Hot movers (add any you see in Fidelity)
    'RILY', 'MSGE', 'AMN', 'XPRO', 'FUBO',
    # Crypto
    'MARA', 'RIOT', 'COIN',
    # Materials
    'MP', 'LAC',
    # EV
    'QS', 'RIVN', 'LCID',
    # Healthcare
    'HIMS', 'DOCS',
    # REPEAT RUNNERS (proven movers)
    'BKKT', 'EVTV', 'ATON', 'SIDU',
]

MIN_MOVE_PCT = 5.0
MIN_VOLUME_MULT = 2.5
MAX_PRICE = 50

# ============================================
# SCAN FUNCTIONS
# ============================================

def scan_extended_hours():
    """Scan pre-market and after-hours"""
    print("\n" + "🌙"*20)
    print("EXTENDED HOURS SCAN")
    print("🌙"*20)
    
    movers = []
    
    for ticker in SCAN_UNIVERSE:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            reg_price = info.get('regularMarketPrice', 0)
            post_price = info.get('postMarketPrice', 0)
            pre_price = info.get('preMarketPrice', 0)
            mcap = info.get('marketCap', 0)
            
            if not reg_price:
                continue
            
            # After hours
            if post_price and post_price != reg_price:
                ah_change = ((post_price - reg_price) / reg_price) * 100
                if abs(ah_change) >= MIN_MOVE_PCT:
                    movers.append({
                        'ticker': ticker,
                        'type': 'AFTER_HOURS',
                        'from_price': reg_price,
                        'to_price': post_price,
                        'change': ah_change,
                        'mcap': mcap
                    })
            
            # Pre-market
            if pre_price and pre_price != reg_price:
                pm_change = ((pre_price - reg_price) / reg_price) * 100
                if abs(pm_change) >= MIN_MOVE_PCT:
                    movers.append({
                        'ticker': ticker,
                        'type': 'PRE_MARKET',
                        'from_price': reg_price,
                        'to_price': pre_price,
                        'change': pm_change,
                        'mcap': mcap
                    })
                    
        except:
            continue
    
    movers.sort(key=lambda x: abs(x['change']), reverse=True)
    
    if movers:
        print(f"\n🚨 {len(movers)} EXTENDED HOURS MOVERS:\n")
        for m in movers:
            emoji = "🟢" if m['change'] > 0 else "🔴"
            print(f"{emoji} {m['ticker']} ({m['type']}): ${m['from_price']:.2f} → ${m['to_price']:.2f} ({m['change']:+.1f}%)")
    else:
        print("\nNo significant extended hours moves.")
    
    return movers


def scan_volume_spikes():
    """Find unusual volume"""
    print("\n" + "📊"*20)
    print("VOLUME SPIKE SCAN")
    print("📊"*20)
    
    spikes = []
    
    for ticker in SCAN_UNIVERSE:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1mo')
            
            if len(hist) < 10:
                continue
            
            today_vol = hist['Volume'].iloc[-1]
            avg_vol = hist['Volume'].iloc[:-1].mean()
            
            if avg_vol > 0:
                ratio = today_vol / avg_vol
                if ratio >= MIN_VOLUME_MULT:
                    price = hist['Close'].iloc[-1]
                    day_chg = ((hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]) * 100
                    
                    spikes.append({
                        'ticker': ticker,
                        'price': price,
                        'volume': today_vol,
                        'avg_volume': avg_vol,
                        'ratio': ratio,
                        'day_change': day_chg
                    })
        except:
            continue
    
    spikes.sort(key=lambda x: x['ratio'], reverse=True)
    
    if spikes:
        print(f"\n🔊 {len(spikes)} VOLUME SPIKES:\n")
        for s in spikes[:10]:
            emoji = "🟢" if s['day_change'] > 0 else "🔴"
            in_range = "✓" if s['price'] <= MAX_PRICE else ""
            print(f"{emoji} {s['ticker']}: ${s['price']:.2f} ({s['day_change']:+.1f}%) | Vol: {s['ratio']:.1f}x avg {in_range}")
    else:
        print("\nNo significant volume spikes.")
    
    return spikes


def scan_day_movers():
    """Get biggest movers of the day"""
    print("\n" + "📈"*20)
    print("TODAY'S BIGGEST MOVERS")
    print("📈"*20)
    
    movers = []
    
    for ticker in SCAN_UNIVERSE:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='2d')
            
            if len(hist) < 1:
                continue
            
            price = hist['Close'].iloc[-1]
            day_chg = ((hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]) * 100
            
            movers.append({
                'ticker': ticker,
                'price': price,
                'change': day_chg
            })
        except:
            continue
    
    movers.sort(key=lambda x: abs(x['change']), reverse=True)
    
    print(f"\n📊 TOP 15 MOVERS:\n")
    for m in movers[:15]:
        emoji = "🟢" if m['change'] > 0 else "🔴"
        in_range = "✓ YOUR RANGE" if m['price'] <= MAX_PRICE else ""
        print(f"{emoji} {m['ticker']}: ${m['price']:.2f} ({m['change']:+.1f}%) {in_range}")
    
    return movers


def scan_compressed_waking():
    """Find beaten down stocks showing life"""
    print("\n" + "🎯"*20)
    print("COMPRESSED STOCKS WAKING UP")
    print("🎯"*20)
    
    candidates = []
    
    for ticker in SCAN_UNIVERSE:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='6mo')
            
            if len(hist) < 60:
                continue
            
            price = hist['Close'].iloc[-1]
            high = hist['Close'].max()
            from_high = ((price - high) / high) * 100
            
            # Today's volume vs average
            today_vol = hist['Volume'].iloc[-1]
            avg_vol = hist['Volume'].iloc[-20:].mean()
            vol_ratio = today_vol / avg_vol if avg_vol > 0 else 0
            
            # Today's move
            day_chg = ((hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]) * 100
            
            # Compressed (>30% down) + elevated volume + green today
            if from_high <= -30 and vol_ratio >= 1.5 and day_chg > 0 and price <= MAX_PRICE:
                candidates.append({
                    'ticker': ticker,
                    'price': price,
                    'from_high': from_high,
                    'vol_ratio': vol_ratio,
                    'day_change': day_chg
                })
        except:
            continue
    
    candidates.sort(key=lambda x: x['from_high'])
    
    if candidates:
        print(f"\n🎯 {len(candidates)} COMPRESSED + WAKING UP:\n")
        for c in candidates:
            print(f"  {c['ticker']}: ${c['price']:.2f} | Down {c['from_high']:.0f}% | Today: +{c['day_change']:.1f}% | Vol: {c['vol_ratio']:.1f}x")
    else:
        print("\nNo compressed stocks waking up today.")
    
    return candidates


def scan_earnings():
    """Check earnings calendar"""
    print("\n" + "📅"*20)
    print("EARNINGS CALENDAR")
    print("📅"*20)
    
    earnings = []
    
    for ticker in SCAN_UNIVERSE:
        try:
            stock = yf.Ticker(ticker)
            cal = stock.earnings_dates
            
            if cal is not None and len(cal) > 0:
                now = datetime.now()
                
                for date in cal.index:
                    date_dt = date.to_pydatetime().replace(tzinfo=None)
                    days = (date_dt - now).days
                    
                    if -1 <= days <= 7:
                        earnings.append({
                            'ticker': ticker,
                            'date': date_dt.strftime('%m/%d'),
                            'days': days
                        })
                        break
        except:
            continue
    
    earnings.sort(key=lambda x: x['days'])
    
    if earnings:
        yesterday = [e for e in earnings if e['days'] == -1]
        today = [e for e in earnings if e['days'] == 0]
        tomorrow = [e for e in earnings if e['days'] == 1]
        this_week = [e for e in earnings if 2 <= e['days'] <= 7]
        
        if yesterday:
            print("\n📍 REPORTED YESTERDAY (CHECK AH):")
            for e in yesterday:
                print(f"   ⚠️  {e['ticker']}")
        
        if today:
            print("\n🔴 REPORTING TODAY:")
            for e in today:
                print(f"   🔴 {e['ticker']}")
        
        if tomorrow:
            print("\n🟡 REPORTING TOMORROW:")
            for e in tomorrow:
                print(f"   🟡 {e['ticker']}")
        
        if this_week:
            print("\n🟢 THIS WEEK:")
            for e in this_week:
                print(f"   {e['ticker']} ({e['date']})")
    else:
        print("\nNo earnings this week in watchlist.")
    
    return earnings


def scan_sec_filings():
    """Check SEC 8-K filings"""
    print("\n" + "📄"*20)
    print("SEC 8-K FILINGS (Last 2 Hours)")
    print("📄"*20)
    
    url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&company=&dateb=&owner=include&count=30&output=atom'
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Wolf Pack Scanner alex@example.com'})
        response = urllib.request.urlopen(req, timeout=15)
        data = response.read().decode('utf-8')
        
        root = ET.fromstring(data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        entries = root.findall('atom:entry', ns)
        
        print(f"\n{len(entries)} recent filings:")
        for entry in entries[:15]:
            title = entry.find('atom:title', ns).text
            match = re.search(r'8-K(?:/A)? - (.+?) \((\d+)\)', title)
            if match:
                company = match.group(1).strip()[:40]
                print(f"  • {company}")
                
    except Exception as e:
        print(f"Error: {e}")


def run_master_scan():
    """Run the complete scan"""
    
    print("\n")
    print("🐺" * 35)
    print("        WOLF PACK MASTER SCANNER")
    print(f"        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🐺" * 35)
    
    # Run all scans
    results = {}
    
    results['extended'] = scan_extended_hours()
    results['volume'] = scan_volume_spikes()
    results['movers'] = scan_day_movers()
    results['compressed'] = scan_compressed_waking()
    results['earnings'] = scan_earnings()
    scan_sec_filings()
    
    # Summary
    print("\n")
    print("=" * 60)
    print("📊 SCAN SUMMARY")
    print("=" * 60)
    print(f"  Extended Hours Movers: {len(results['extended'])}")
    print(f"  Volume Spikes: {len(results['volume'])}")
    print(f"  Compressed Waking: {len(results['compressed'])}")
    print(f"  Earnings This Week: {len(results['earnings'])}")
    
    # Action items
    print("\n")
    print("=" * 60)
    print("🎯 ACTION ITEMS")
    print("=" * 60)
    
    actions = []
    
    # High priority: Extended hours + green
    for m in results['extended']:
        if m['change'] > 10:
            actions.append(f"🚨 {m['ticker']} +{m['change']:.0f}% {m['type']} - INVESTIGATE NOW")
    
    # Medium: Volume spike + green
    for v in results['volume'][:5]:
        if v['day_change'] > 5:
            actions.append(f"📊 {v['ticker']} +{v['day_change']:.0f}% on {v['ratio']:.0f}x volume")
    
    # Compressed waking
    for c in results['compressed'][:3]:
        actions.append(f"🎯 {c['ticker']} waking up from -{abs(c['from_high']):.0f}% compression")
    
    # Earnings today
    for e in results['earnings']:
        if e['days'] == 0:
            actions.append(f"📅 {e['ticker']} EARNINGS TODAY - watch AH")
    
    if actions:
        for a in actions:
            print(f"  {a}")
    else:
        print("  No immediate action items.")
    
    print("\n" + "🐺" * 35)
    print("        SCAN COMPLETE - LLHR")
    print("🐺" * 35 + "\n")
    
    return results


if __name__ == "__main__":
    run_master_scan()
