# 🐺 FENRIR V2 - SEC FETCHER
# Fetch SEC filings from EDGAR

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time


# SEC requires a user agent
HEADERS = {
    'User-Agent': 'Fenrir Trading Bot contact@example.com',
    'Accept-Encoding': 'gzip, deflate',
}


def get_cik_from_ticker(ticker: str) -> Optional[str]:
    """Get CIK number from ticker symbol"""
    url = "https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        'action': 'getcompany',
        'CIK': ticker,
        'type': '8-K',
        'dateb': '',
        'owner': 'include',
        'count': '1',
        'output': 'atom'
    }
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        # Extract CIK from response (basic parsing)
        if 'CIK=' in response.text:
            start = response.text.find('CIK=') + 4
            end = response.text.find('&', start)
            if end == -1:
                end = response.text.find('"', start)
            return response.text[start:end].zfill(10)
    except Exception as e:
        print(f"Error getting CIK for {ticker}: {e}")
    
    return None


def get_recent_filings(ticker: str, filing_type: str = '8-K', count: int = 10) -> List[Dict]:
    """Get recent SEC filings for a ticker
    
    Filing types:
    - 8-K: Material events (contracts, acquisitions, management changes)
    - 10-K: Annual report
    - 10-Q: Quarterly report
    - 4: Insider trading
    """
    
    # Use SEC full-text search API
    url = "https://efts.sec.gov/LATEST/search-index"
    params = {
        'q': f'"{ticker}"',
        'dateRange': 'custom',
        'startdt': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'enddt': datetime.now().strftime('%Y-%m-%d'),
        'forms': filing_type,
        'from': 0,
        'size': count,
    }
    
    try:
        # Alternative: Use the company filings endpoint
        search_url = f"https://www.sec.gov/cgi-bin/browse-edgar"
        search_params = {
            'action': 'getcompany',
            'CIK': ticker,
            'type': filing_type,
            'dateb': '',
            'owner': 'include',
            'count': str(count),
            'output': 'atom'
        }
        
        response = requests.get(search_url, params=search_params, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            return []
        
        # Parse the ATOM feed (basic parsing)
        filings = []
        content = response.text
        
        # Find all entries
        entries = content.split('<entry>')
        for entry in entries[1:]:  # Skip first split (before first entry)
            filing = {}
            
            # Extract title
            if '<title>' in entry:
                start = entry.find('<title>') + 7
                end = entry.find('</title>', start)
                filing['title'] = entry[start:end].strip()
            
            # Extract link
            if 'href="' in entry:
                start = entry.find('href="') + 6
                end = entry.find('"', start)
                filing['url'] = entry[start:end]
            
            # Extract date
            if '<updated>' in entry:
                start = entry.find('<updated>') + 9
                end = entry.find('</updated>', start)
                filing['date'] = entry[start:end][:10]  # Just the date part
            
            # Extract summary
            if '<summary' in entry:
                start = entry.find('>', entry.find('<summary')) + 1
                end = entry.find('</summary>', start)
                summary = entry[start:end].strip()
                # Clean HTML
                summary = summary.replace('&lt;', '<').replace('&gt;', '>')
                summary = summary.replace('<b>', '').replace('</b>', '')
                filing['summary'] = summary[:300] + '...' if len(summary) > 300 else summary
            
            if filing.get('title'):
                filings.append(filing)
        
        return filings
        
    except Exception as e:
        print(f"Error fetching SEC filings for {ticker}: {e}")
        return []


def get_insider_trades(ticker: str, days: int = 30) -> List[Dict]:
    """Get recent Form 4 insider trading filings"""
    filings = get_recent_filings(ticker, filing_type='4', count=20)
    
    insider_trades = []
    for f in filings:
        # Parse Form 4 for buy/sell info
        trade = {
            'date': f.get('date'),
            'title': f.get('title'),
            'url': f.get('url'),
            'summary': f.get('summary', ''),
        }
        
        # Try to determine if it's a buy or sell from title/summary
        text = (f.get('title', '') + ' ' + f.get('summary', '')).lower()
        if 'acquisition' in text or 'purchase' in text:
            trade['type'] = 'BUY'
        elif 'disposition' in text or 'sale' in text:
            trade['type'] = 'SELL'
        else:
            trade['type'] = 'UNKNOWN'
        
        insider_trades.append(trade)
    
    return insider_trades


def get_8k_filings(ticker: str, count: int = 5) -> List[Dict]:
    """Get recent 8-K filings (material events)"""
    return get_recent_filings(ticker, filing_type='8-K', count=count)


def format_filings_for_context(filings: List[Dict]) -> str:
    """Format filings as string for LLM context"""
    if not filings:
        return "No recent SEC filings found."
    
    lines = []
    for f in filings[:5]:
        line = f"[{f.get('date', 'N/A')}] {f.get('title', 'No title')}"
        lines.append(line)
    
    return "\n".join(lines)


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    print("Testing SEC fetcher...")
    
    # Add delay to respect rate limits
    ticker = "IBRX"
    
    print(f"\n--- {ticker} 8-K Filings ---")
    filings_8k = get_8k_filings(ticker)
    for f in filings_8k:
        print(f"  [{f.get('date')}] {f.get('title', '')[:60]}")
    
    time.sleep(0.5)  # Rate limit
    
    print(f"\n--- {ticker} Insider Trades ---")
    insider = get_insider_trades(ticker)
    for t in insider[:5]:
        print(f"  [{t.get('date')}] {t.get('type')}: {t.get('title', '')[:50]}")
