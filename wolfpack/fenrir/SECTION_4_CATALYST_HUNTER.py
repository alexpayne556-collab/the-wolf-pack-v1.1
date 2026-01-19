# ============================================================================
# 🐺 FENRIR V2 - COLAB SECTION 4: CATALYST HUNTER
# ============================================================================
# For every mover found, automatically fetch news/catalyst
# NO CATALYST = NO TRADE - this is the filter
# ============================================================================

import requests
import time
import pandas as pd

# ============================================================================
# NEWS FETCHER (Free APIs)
# ============================================================================

def get_news_finnhub(ticker, api_key=None):
    """Fetch news from Finnhub (free tier: 60 calls/min)"""
    if not api_key:
        return []
    
    from datetime import datetime, timedelta
    end = datetime.now()
    start = end - timedelta(days=3)
    
    url = f"https://finnhub.io/api/v1/company-news"
    params = {
        'symbol': ticker,
        'from': start.strftime('%Y-%m-%d'),
        'to': end.strftime('%Y-%m-%d'),
        'token': api_key
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        news = resp.json()
        return [{'headline': n.get('headline', ''), 'source': n.get('source', '')} 
                for n in news[:5]]
    except:
        return []


def get_news_yahoo(ticker):
    """Fetch news from Yahoo Finance (no API key needed)"""
    import yfinance as yf
    
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        if news:
            return [{'headline': n.get('title', ''), 'source': n.get('publisher', '')} 
                    for n in news[:5]]
    except:
        pass
    return []


def get_catalyst(ticker, finnhub_key=None):
    """Get news catalyst for a ticker"""
    
    # Try Yahoo first (free, no limits)
    news = get_news_yahoo(ticker)
    
    # Try Finnhub if we have a key and Yahoo failed
    if not news and finnhub_key:
        news = get_news_finnhub(ticker, finnhub_key)
        time.sleep(1)  # Rate limit
    
    if news:
        # Return top headlines
        headlines = [n['headline'] for n in news if n['headline']]
        return headlines[:3]
    
    return []


# ============================================================================
# PROCESS ALL MOVERS
# ============================================================================

def analyze_movers(movers_df, finnhub_key=None):
    """
    For each mover, fetch catalyst and classify
    
    Returns DataFrame with catalyst info added
    """
    
    print("🐺 Fenrir researching catalysts...\n")
    
    results = []
    
    for idx, row in movers_df.iterrows():
        ticker = row['ticker']
        
        print(f"   Checking {ticker}...")
        
        # Get news
        headlines = get_catalyst(ticker, finnhub_key)
        
        # Classify
        if headlines:
            catalyst = headlines[0][:100]  # First headline, truncated
            has_catalyst = True
        else:
            catalyst = "NO NEWS FOUND"
            has_catalyst = False
        
        results.append({
            'ticker': ticker,
            'price': row['price'],
            'change_pct': row['change_pct'],
            'volume_ratio': row['volume_ratio'],
            'catalyst': catalyst,
            'has_catalyst': has_catalyst,
            'all_headlines': headlines,
        })
    
    df = pd.DataFrame(results)
    return df


# ============================================================================
# RUN CATALYST ANALYSIS
# ============================================================================

# Load movers from Section 3
movers_df = pd.read_csv('todays_movers.csv')

# Optional: Add your Finnhub API key for better news coverage
# Get free key at: https://finnhub.io/register
FINNHUB_KEY = None  # Replace with your key: "your_key_here"

# Analyze all movers
analyzed_df = analyze_movers(movers_df, FINNHUB_KEY)

# Split into quality vs garbage
quality_plays = analyzed_df[analyzed_df['has_catalyst'] == True].copy()
no_catalyst = analyzed_df[analyzed_df['has_catalyst'] == False].copy()

print("\n" + "="*60)
print("🎯 QUALITY SETUPS (Have real catalyst):")
print("="*60)
for idx, row in quality_plays.iterrows():
    direction = "🟢" if row['change_pct'] > 0 else "🔴"
    print(f"\n{direction} {row['ticker']} | ${row['price']} | {row['change_pct']:+.1f}% | {row['volume_ratio']:.1f}x vol")
    print(f"   Catalyst: {row['catalyst']}")

print("\n" + "="*60)
print("🗑️ SKIP THESE (No catalyst found):")
print("="*60)
for idx, row in no_catalyst.iterrows():
    print(f"   {row['ticker']} - {row['change_pct']:+.1f}% - NO NEWS = NO TRADE")

# Save for next section
quality_plays.to_csv('quality_setups.csv', index=False)

print(f"\n✅ Section 4 Complete")
print(f"🐺 {len(quality_plays)} quality setups, {len(no_catalyst)} rejected (no catalyst)")
