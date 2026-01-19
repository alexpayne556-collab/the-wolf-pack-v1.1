#!/usr/bin/env python3
"""
Wolf Pack V2 - Catalyst Fetcher
Auto-fetches news and SEC filings when moves are detected
"""

import requests
from datetime import datetime, timedelta
import time
from config import FINNHUB_API_KEY, SEC_EDGAR_BASE_URL
from wolfpack_db_v2 import store_catalyst

class CatalystFetcher:
    """Fetches and stores catalysts for stock moves"""
    
    def __init__(self):
        self.finnhub_base = "https://finnhub.io/api/v1"
        self.sec_base = "https://data.sec.gov/submissions"
    
    def fetch_news(self, ticker, hours_back=24):
        """Fetch recent news from Finnhub"""
        
        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(hours=hours_back)
            
            url = f"{self.finnhub_base}/company-news"
            params = {
                'symbol': ticker,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'token': FINNHUB_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                news_items = response.json()
                
                # Filter to most recent and relevant
                recent_news = []
                for item in news_items[:5]:  # Top 5 most recent
                    recent_news.append({
                        'headline': item.get('headline', ''),
                        'summary': item.get('summary', ''),
                        'source': item.get('source', ''),
                        'url': item.get('url', ''),
                        'timestamp': datetime.fromtimestamp(item.get('datetime', 0))
                    })
                
                return recent_news
            
            else:
                print(f"  ⚠️  Finnhub API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"  ❌ Error fetching news: {e}")
            return []
    
    def fetch_sec_filings(self, ticker):
        """Fetch recent SEC filings"""
        
        try:
            # Note: SEC requires User-Agent header
            headers = {
                'User-Agent': 'WolfPack Trading System contact@trading.com'
            }
            
            # Get CIK for ticker (simplified - in production use mapping file)
            # For now, try direct ticker lookup
            
            # Search for recent filings
            url = f"{self.sec_base}/CIK{ticker}.json"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract recent filings (8-K, 10-Q, 10-K, etc.)
                filings = []
                recent_filings = data.get('filings', {}).get('recent', {})
                
                if recent_filings:
                    forms = recent_filings.get('form', [])
                    dates = recent_filings.get('filingDate', [])
                    accessions = recent_filings.get('accessionNumber', [])
                    
                    for i in range(min(5, len(forms))):  # Latest 5
                        filings.append({
                            'form_type': forms[i],
                            'filing_date': dates[i],
                            'accession': accessions[i],
                            'url': f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type={forms[i]}&dateb=&owner=exclude&count=10"
                        })
                
                return filings
            
            else:
                # SEC API can be strict - don't error out, just return empty
                return []
                
        except Exception as e:
            print(f"  ⚠️  SEC fetch issue: {e}")
            return []
    
    def analyze_timing(self, move_timestamp, catalysts):
        """Analyze timing correlation between catalyst and move"""
        
        best_match = None
        min_time_diff = float('inf')
        
        for catalyst in catalysts:
            catalyst_time = catalyst.get('timestamp')
            if catalyst_time:
                time_diff = abs((move_timestamp - catalyst_time).total_seconds() / 60)  # Minutes
                
                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    best_match = catalyst
        
        return best_match, min_time_diff

def fetch_catalysts(ticker, move_timestamp, move_pct):
    """Main function to fetch all catalysts for a move"""
    
    fetcher = CatalystFetcher()
    
    # Fetch news (last 24 hours)
    news = fetcher.fetch_news(ticker, hours_back=24)
    
    # Fetch SEC filings (today)
    filings = fetcher.fetch_sec_filings(ticker)
    
    # Determine most likely catalyst
    catalyst_info = {
        'ticker': ticker,
        'move_timestamp': move_timestamp,
        'move_pct': move_pct,
        'news_count': len(news),
        'filing_count': len(filings),
        'news_items': news,
        'filings': filings,
        'catalyst_type': 'unknown',
        'confidence': 0.3,
        'summary': ''
    }
    
    # Analyze what we found
    if news and filings:
        catalyst_info['catalyst_type'] = 'news_and_filing'
        catalyst_info['confidence'] = 0.9
        catalyst_info['summary'] = f"{len(news)} news + {len(filings)} SEC filings"
    elif news:
        catalyst_info['catalyst_type'] = 'news'
        catalyst_info['confidence'] = 0.7
        catalyst_info['summary'] = f"{len(news)} news items: {news[0]['headline'][:50]}..."
    elif filings:
        catalyst_info['catalyst_type'] = 'sec_filing'
        catalyst_info['confidence'] = 0.8
        catalyst_info['summary'] = f"SEC {filings[0]['form_type']} filed {filings[0]['filing_date']}"
    else:
        catalyst_info['summary'] = "No catalyst found - manual check needed"
    
    # Store in database
    store_catalyst(catalyst_info)
    
    return catalyst_info

if __name__ == '__main__':
    # Test fetcher
    print("\n🧪 Testing Catalyst Fetcher\n")
    
    test_ticker = "AAPL"
    print(f"Fetching catalysts for {test_ticker}...")
    
    result = fetch_catalysts(
        ticker=test_ticker,
        move_timestamp=datetime.now(),
        move_pct=3.5
    )
    
    print(f"\n✅ Result:")
    print(f"  Type: {result['catalyst_type']}")
    print(f"  Confidence: {result['confidence']:.0%}")
    print(f"  Summary: {result['summary']}")
    print(f"  News: {len(result['news_items'])} items")
    print(f"  Filings: {len(result['filings'])} items")
