#!/usr/bin/env python3
"""
🌙 NIGHT RESEARCH MODE - PREPARE FOR TOMORROW'S PREMARKET

This script runs overnight to:
1. Research all FDA calendar plays for this week
2. Scan for after-hours movers
3. Check insider buying activity across watchlist
4. Build tomorrow's priority watchlist
5. Generate a MORNING BRIEFING for when you wake up

RUN THIS TONIGHT - Wake up to a complete briefing!
"""

import os
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv('../../.env')

import requests
import json
from datetime import datetime, timedelta
import time

# Try to import yfinance
try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False
    print("⚠️ yfinance not available")

# API Keys
FINNHUB_KEY = os.environ.get('FINNHUB_API_KEY', '')
NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY', '')
POLYGON_KEY = os.environ.get('POLYGON_API_KEY', '')
ALPHAVANTAGE_KEY = os.environ.get('ALPHAVANTAGE_API_KEY', '')

# Output paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'wolf_brain')
os.makedirs(DATA_DIR, exist_ok=True)

# FDA Calendar - Upcoming catalysts
FDA_CALENDAR = {
    'AQST': {'date': '2026-01-31', 'drug': 'Libervant', 'indication': 'Seizures', 'notes': 'PDUFA'},
    'IRON': {'date': '2026-01-31', 'drug': 'Ferric Maltol', 'indication': 'Iron Deficiency', 'notes': 'NDA decision'},
    'VKTX': {'date': '2026-02-21', 'drug': 'VK2735', 'indication': 'Obesity', 'notes': 'Phase 2 data'},
    'SRPT': {'date': '2026-Q1', 'drug': 'SRP-9001', 'indication': 'DMD Gene Therapy', 'notes': 'Label expansion'},
    'MDGL': {'date': '2026-Q1', 'drug': 'Resmetirom', 'indication': 'NASH', 'notes': 'Commercial launch data'},
    'IONS': {'date': '2026-02-15', 'drug': 'Donidalorsen', 'indication': 'HAE', 'notes': 'Phase 3 readout'},
    'MRNA': {'date': '2026-Q1', 'drug': 'mRNA-1283', 'indication': 'COVID Next-Gen', 'notes': 'Approval expected'},
    'BBIO': {'date': '2026-02-28', 'drug': 'Acoramidis', 'indication': 'ATTR-CM', 'notes': 'EU approval'},
}

# Core watchlist for research
WATCHLIST = [
    # FDA Plays
    'AQST', 'IRON', 'VKTX', 'SRPT', 'MDGL', 'IONS', 'BBIO',
    # Low float biotech
    'SAVA', 'IMVT', 'NVAX', 'MRNA', 'BNTX',
    # Current positions
    'NTLA', 'UUUU', 'VRCA', 'LUNR', 'INTC',
    # Hot sectors
    'PLTR', 'IONQ', 'RGTI', 'SMR', 'OKLO',
    # Meme/momentum
    'GME', 'AMC', 'MARA', 'RIOT',
]

def get_news(ticker):
    """Get news from all sources"""
    news = []
    
    # Finnhub
    if FINNHUB_KEY:
        try:
            url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={(datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')}&to={datetime.now().strftime('%Y-%m-%d')}&token={FINNHUB_KEY}"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                for item in r.json()[:5]:
                    news.append({
                        'headline': item.get('headline', ''),
                        'source': 'Finnhub',
                        'time': datetime.fromtimestamp(item.get('datetime', 0)).strftime('%Y-%m-%d %H:%M') if item.get('datetime') else ''
                    })
        except:
            pass
    
    # Polygon
    if POLYGON_KEY and len(news) < 5:
        try:
            url = f"https://api.polygon.io/v2/reference/news?ticker={ticker}&limit=5&apiKey={POLYGON_KEY}"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                for item in r.json().get('results', []):
                    news.append({
                        'headline': item.get('title', ''),
                        'source': 'Polygon',
                        'time': item.get('published_utc', '')[:16] if item.get('published_utc') else ''
                    })
        except:
            pass
    
    return news[:7]

def get_insider_activity(ticker):
    """Get insider buying/selling"""
    if not FINNHUB_KEY:
        return None
    
    try:
        url = f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={ticker}&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            txns = r.json().get('data', [])
            buys = sum(1 for t in txns if t.get('transactionCode') == 'P')
            sells = sum(1 for t in txns if t.get('transactionCode') == 'S')
            return {'buys': buys, 'sells': sells, 'net': 'BUYING' if buys > sells else 'SELLING' if sells > buys else 'NEUTRAL'}
    except:
        pass
    return None

def get_price_data(ticker):
    """Get price data from yfinance"""
    if not YF_AVAILABLE:
        return None
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='5d')
        if hist.empty:
            return None
        
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
        change = (current - prev) / prev * 100
        
        info = stock.info
        
        return {
            'price': float(current),
            'change': float(change),
            'volume': int(hist['Volume'].iloc[-1]),
            'avg_volume': int(hist['Volume'].mean()),
            'rel_volume': float(hist['Volume'].iloc[-1] / hist['Volume'].mean()) if hist['Volume'].mean() > 0 else 1,
            'float': info.get('floatShares', 0),
            'short_pct': info.get('shortPercentOfFloat', 0) * 100 if info.get('shortPercentOfFloat') else 0,
        }
    except Exception as e:
        return None

def get_fundamentals(ticker):
    """Get fundamentals from Alpha Vantage"""
    if not ALPHAVANTAGE_KEY:
        return None
    
    try:
        url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHAVANTAGE_KEY}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if 'Symbol' in data:
                return {
                    'pe': data.get('PERatio', 'N/A'),
                    'target': data.get('AnalystTargetPrice', 'N/A'),
                    'sector': data.get('Sector', 'N/A'),
                }
    except:
        pass
    return None

def main():
    print("=" * 70)
    print("NIGHT RESEARCH MODE - PREPARING FOR TOMORROW")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    briefing = []
    briefing.append("=" * 70)
    briefing.append(f"🌅 WOLF PACK MORNING BRIEFING - {(datetime.now() + timedelta(days=1)).strftime('%A, %B %d, %Y')}")
    briefing.append("=" * 70)
    briefing.append("")
    
    # SECTION 1: FDA CALENDAR
    briefing.append("📅 FDA CATALYST CALENDAR (This Week)")
    briefing.append("-" * 50)
    
    today = datetime.now()
    week_end = today + timedelta(days=7)
    
    for ticker, info in FDA_CALENDAR.items():
        try:
            if 'Q' in info['date']:
                briefing.append(f"  {ticker}: {info['drug']} - {info['indication']} ({info['date']})")
            else:
                fda_date = datetime.strptime(info['date'], '%Y-%m-%d')
                days_until = (fda_date - today).days
                if days_until <= 14:
                    urgency = "🔥🔥🔥" if days_until <= 3 else "🔥🔥" if days_until <= 7 else "🔥"
                    briefing.append(f"  {urgency} {ticker}: {info['drug']} - {info['indication']}")
                    briefing.append(f"      Date: {info['date']} ({days_until} days) | {info['notes']}")
        except:
            pass
    
    briefing.append("")
    
    # SECTION 2: RESEARCH EACH TICKER
    briefing.append("📊 WATCHLIST RESEARCH")
    briefing.append("-" * 50)
    
    research_results = []
    
    for i, ticker in enumerate(WATCHLIST):
        print(f"Researching {ticker} ({i+1}/{len(WATCHLIST)})...")
        
        result = {'ticker': ticker}
        
        # Get price data
        price_data = get_price_data(ticker)
        if price_data:
            result['price'] = price_data
        
        # Get news
        news = get_news(ticker)
        result['news'] = news
        
        # Get insider activity
        insider = get_insider_activity(ticker)
        if insider:
            result['insider'] = insider
        
        # Rate limit
        time.sleep(0.3)
        
        research_results.append(result)
        
        # Brief summary
        if price_data:
            change_emoji = "🟢" if price_data['change'] > 0 else "🔴"
            vol_emoji = "📈" if price_data['rel_volume'] > 1.5 else ""
            insider_emoji = "💰" if insider and insider['net'] == 'BUYING' else ""
            
            briefing.append(f"  {change_emoji} {ticker}: ${price_data['price']:.2f} ({price_data['change']:+.1f}%) {vol_emoji}{insider_emoji}")
            
            if price_data['rel_volume'] > 2:
                briefing.append(f"      ⚠️  HIGH VOLUME: {price_data['rel_volume']:.1f}x avg")
            
            if insider and insider['net'] == 'BUYING':
                briefing.append(f"      💰 INSIDER BUYING: {insider['buys']} buys vs {insider['sells']} sells")
            
            if news:
                briefing.append(f"      📰 Latest: {news[0]['headline'][:60]}...")
        
        time.sleep(0.2)
    
    briefing.append("")
    
    # SECTION 3: TOP MOVERS
    briefing.append("🚀 TOP MOVERS (Sort by Change)")
    briefing.append("-" * 50)
    
    movers = [r for r in research_results if r.get('price')]
    movers.sort(key=lambda x: x['price']['change'], reverse=True)
    
    briefing.append("  GAINERS:")
    for m in movers[:5]:
        if m['price']['change'] > 0:
            briefing.append(f"    🟢 {m['ticker']}: +{m['price']['change']:.1f}%")
    
    briefing.append("  LOSERS:")
    for m in movers[-5:]:
        if m['price']['change'] < 0:
            briefing.append(f"    🔴 {m['ticker']}: {m['price']['change']:.1f}%")
    
    briefing.append("")
    
    # SECTION 4: HIGH VOLUME ALERTS
    briefing.append("📈 HIGH VOLUME ALERTS (>1.5x avg)")
    briefing.append("-" * 50)
    
    high_vol = [r for r in research_results if r.get('price') and r['price']['rel_volume'] > 1.5]
    high_vol.sort(key=lambda x: x['price']['rel_volume'], reverse=True)
    
    for h in high_vol[:10]:
        briefing.append(f"  ⚡ {h['ticker']}: {h['price']['rel_volume']:.1f}x volume | {h['price']['change']:+.1f}%")
    
    if not high_vol:
        briefing.append("  No unusual volume detected")
    
    briefing.append("")
    
    # SECTION 5: INSIDER ACTIVITY
    briefing.append("💰 INSIDER ACTIVITY SUMMARY")
    briefing.append("-" * 50)
    
    buyers = [r for r in research_results if r.get('insider') and r['insider']['net'] == 'BUYING']
    sellers = [r for r in research_results if r.get('insider') and r['insider']['net'] == 'SELLING']
    
    if buyers:
        briefing.append("  INSIDER BUYING:")
        for b in buyers:
            briefing.append(f"    💚 {b['ticker']}: {b['insider']['buys']} buys")
    
    if sellers:
        briefing.append("  INSIDER SELLING:")
        for s in sellers[:5]:
            briefing.append(f"    🔴 {s['ticker']}: {s['insider']['sells']} sells")
    
    briefing.append("")
    
    # SECTION 6: TOMORROW'S PRIORITY WATCHLIST
    briefing.append("🎯 TOMORROW'S PRIORITY WATCHLIST")
    briefing.append("-" * 50)
    
    # Score each ticker
    scored = []
    for r in research_results:
        score = 0
        reasons = []
        
        # FDA catalyst soon
        if r['ticker'] in FDA_CALENDAR:
            score += 30
            reasons.append("FDA catalyst")
        
        # High volume
        if r.get('price') and r['price']['rel_volume'] > 1.5:
            score += 20
            reasons.append(f"{r['price']['rel_volume']:.1f}x vol")
        
        # Insider buying
        if r.get('insider') and r['insider']['net'] == 'BUYING':
            score += 25
            reasons.append("insider buying")
        
        # Recent news
        if r.get('news') and len(r['news']) > 2:
            score += 10
            reasons.append("news flow")
        
        # Momentum
        if r.get('price') and r['price']['change'] > 3:
            score += 15
            reasons.append(f"+{r['price']['change']:.1f}%")
        
        if score > 0:
            scored.append({'ticker': r['ticker'], 'score': score, 'reasons': reasons, 'data': r})
    
    scored.sort(key=lambda x: x['score'], reverse=True)
    
    for i, s in enumerate(scored[:10], 1):
        price_str = f"${s['data']['price']['price']:.2f}" if s['data'].get('price') else "N/A"
        briefing.append(f"  {i}. {s['ticker']} (Score: {s['score']}) - {price_str}")
        briefing.append(f"     Reasons: {', '.join(s['reasons'])}")
    
    briefing.append("")
    briefing.append("=" * 70)
    briefing.append(f"🐺 Research completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    briefing.append("=" * 70)
    
    # Save briefing
    briefing_text = "\n".join(briefing)
    
    briefing_path = os.path.join(DATA_DIR, 'MORNING_BRIEFING.txt')
    with open(briefing_path, 'w', encoding='utf-8') as f:
        f.write(briefing_text)
    
    print()
    print("Briefing generated - check MORNING_BRIEFING.txt")
    print(f"Saved to: {briefing_path}")
    
    # Also save raw research data
    research_path = os.path.join(DATA_DIR, 'night_research.json')
    with open(research_path, 'w', encoding='utf-8') as f:
        json.dump(research_results, f, indent=2, default=str)
    
    print(f"Research data saved to: {research_path}")
    print()
    print("Night research complete! Get some sleep - the brain will wake at 4 AM!")

if __name__ == '__main__':
    main()
