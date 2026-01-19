#!/usr/bin/env python3
"""
Daily SEC filing collector
Pulls 8-K and Form 4 filings, categorizes events, stores in database
Run after market close (5 PM ET)
"""

import sqlite3
import urllib.request
import xml.etree.ElementTree as ET
import re
import yfinance as yf
from datetime import datetime, timedelta
import time

DB_PATH = 'wolf_pack_events.db'

# Event classification keywords
KEYWORDS = {
    'contract': ['contract', 'award', 'agreement', 'order'],
    'partnership': ['partnership', 'collaboration', 'joint venture', 'alliance'],
    'fda': ['FDA', 'approval', 'trial', 'drug', 'Phase'],
    'earnings': ['earnings', 'quarter', 'revenue', 'results'],
    'offering': ['offering', 'shares', 'dilution', 'shelf', 'ATM'],
    'analyst': ['upgrade', 'downgrade', 'price target', 'initiated'],
    'acquisition': ['acquisition', 'acquire', 'merger', 'M&A'],
}

def fetch_sec_filings(form_type='8-K', count=100):
    """Fetch SEC filings from EDGAR RSS feed"""
    
    url = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type={form_type}&company=&dateb=&owner=include&count={count}&output=atom'
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Wolf Pack Research/1.0'})
        response = urllib.request.urlopen(req, timeout=15)
        data = response.read().decode('utf-8')
        
        root = ET.fromstring(data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        filings = []
        entries = root.findall('atom:entry', ns)
        
        for entry in entries:
            title = entry.find('atom:title', ns).text
            link = entry.find('atom:link', ns).get('href') if entry.find('atom:link', ns) is not None else ''
            updated = entry.find('atom:updated', ns).text if entry.find('atom:updated', ns) is not None else ''
            
            # Parse ticker from title
            # Format: "8-K - COMPANY NAME (TICKER)"
            ticker_match = re.search(r'\(([A-Z]+)\)', title)
            if ticker_match:
                ticker = ticker_match.group(1)
                company = title.split(' - ')[1].split(' (')[0] if ' - ' in title else ''
                
                filings.append({
                    'ticker': ticker,
                    'company': company,
                    'headline': title,
                    'url': link,
                    'date': updated,
                    'form_type': form_type
                })
        
        return filings
    
    except Exception as e:
        print(f"❌ Error fetching {form_type} filings: {e}")
        return []

def classify_event(headline, form_type):
    """Classify event type based on headline keywords"""
    
    headline_lower = headline.lower()
    
    # Form 4 gets special handling
    if form_type == '4':
        if 'purchase' in headline_lower or 'buy' in headline_lower:
            return 'insider_buy'
        elif 'sale' in headline_lower or 'sell' in headline_lower:
            return 'insider_sell'
        else:
            return 'insider_transaction'
    
    # Check keywords for 8-K
    for event_type, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in headline_lower:
                return event_type
    
    return 'other'

def get_stock_data(ticker):
    """Get current price, volume, market cap for ticker"""
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo')
        info = stock.info
        
        if len(hist) < 2:
            return None
        
        current_price = hist['Close'].iloc[-1]
        current_volume = hist['Volume'].iloc[-1]
        avg_volume = hist['Volume'].iloc[-20:].mean() if len(hist) >= 20 else hist['Volume'].mean()
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        market_cap = info.get('marketCap', 0)
        
        return {
            'price': current_price,
            'volume': int(current_volume),
            'avg_volume': int(avg_volume),
            'volume_ratio': volume_ratio,
            'market_cap': market_cap
        }
    
    except Exception as e:
        print(f"  ⚠️  Could not fetch data for {ticker}: {e}")
        return None

def store_event(conn, event_data):
    """Store event in database"""
    
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO events 
        (ticker, event_date, event_type, headline, filing_url, 
         market_cap_at_event, price_at_event, volume_at_event, 
         avg_volume_20d, volume_ratio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_data['ticker'],
            event_data['event_date'],
            event_data['event_type'],
            event_data['headline'],
            event_data['filing_url'],
            event_data['market_cap'],
            event_data['price'],
            event_data['volume'],
            event_data['avg_volume'],
            event_data['volume_ratio']
        ))
        
        conn.commit()
        return cursor.rowcount > 0
    
    except Exception as e:
        print(f"  ❌ Error storing event: {e}")
        return False

def collect_daily_events():
    """Main collection function"""
    
    print("\n" + "🐺"*30)
    print("WOLF PACK NEWS TRACKER - DAILY COLLECTION")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🐺"*30 + "\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    events_stored = 0
    
    # Collect 8-K filings
    print("📄 Fetching 8-K filings...")
    filings_8k = fetch_sec_filings('8-K', count=100)
    print(f"   Found {len(filings_8k)} 8-K filings\n")
    
    # Collect Form 4 filings
    print("📄 Fetching Form 4 filings...")
    filings_4 = fetch_sec_filings('4', count=50)
    print(f"   Found {len(filings_4)} Form 4 filings\n")
    
    all_filings = filings_8k + filings_4
    
    print(f"Processing {len(all_filings)} total filings...\n")
    
    for filing in all_filings:
        ticker = filing['ticker']
        event_type = classify_event(filing['headline'], filing['form_type'])
        
        # Get stock data
        stock_data = get_stock_data(ticker)
        
        if stock_data is None:
            continue
        
        # Prepare event data
        event_data = {
            'ticker': ticker,
            'event_date': datetime.now(),
            'event_type': event_type,
            'headline': filing['headline'][:500],  # Truncate long headlines
            'filing_url': filing['url'],
            'market_cap': stock_data['market_cap'],
            'price': stock_data['price'],
            'volume': stock_data['volume'],
            'avg_volume': stock_data['avg_volume'],
            'volume_ratio': stock_data['volume_ratio']
        }
        
        # Store in database
        if store_event(conn, event_data):
            events_stored += 1
            print(f"✅ {ticker:6} | {event_type:15} | ${stock_data['price']:.2f} | {stock_data['volume_ratio']:.1f}x vol")
        
        # Rate limit
        time.sleep(0.5)
    
    conn.close()
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total filings: {len(all_filings)}")
    print(f"   Events stored: {events_stored}")
    print(f"\n🐺 Collection complete - LLHR\n")

if __name__ == '__main__':
    collect_daily_events()
