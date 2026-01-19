# 🐺 FENRIR V2 - NEWS FETCHER
# Fetch recent news via Finnhub API

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import FINNHUB_API_KEY


def get_company_news(ticker: str, days: int = 3) -> List[Dict]:
    """Fetch recent news for a ticker from Finnhub"""
    if not FINNHUB_API_KEY:
        print("Warning: FINNHUB_API_KEY not set in .env")
        return []
    
    end = datetime.now()
    start = end - timedelta(days=days)
    
    url = "https://finnhub.io/api/v1/company-news"
    params = {
        'symbol': ticker,
        'from': start.strftime('%Y-%m-%d'),
        'to': end.strftime('%Y-%m-%d'),
        'token': FINNHUB_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        news = response.json()
        
        # Return formatted news items
        return [{
            'headline': item.get('headline', ''),
            'summary': item.get('summary', '')[:200] + '...' if item.get('summary') else '',
            'source': item.get('source', ''),
            'datetime': datetime.fromtimestamp(item['datetime']).strftime('%Y-%m-%d %H:%M'),
            'url': item.get('url', ''),
            'category': item.get('category', ''),
        } for item in news[:10]]  # Top 10 articles
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []


def get_market_news(category: str = 'general') -> List[Dict]:
    """Fetch general market news
    
    Categories: general, forex, crypto, merger
    """
    if not FINNHUB_API_KEY:
        return []
    
    url = "https://finnhub.io/api/v1/news"
    params = {
        'category': category,
        'token': FINNHUB_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        news = response.json()
        
        return [{
            'headline': item.get('headline', ''),
            'summary': item.get('summary', '')[:200] + '...' if item.get('summary') else '',
            'source': item.get('source', ''),
            'datetime': datetime.fromtimestamp(item['datetime']).strftime('%Y-%m-%d %H:%M'),
            'url': item.get('url', ''),
        } for item in news[:10]]
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching market news: {e}")
        return []


def get_basic_financials(ticker: str) -> Optional[Dict]:
    """Get basic financial metrics from Finnhub"""
    if not FINNHUB_API_KEY:
        return None
    
    url = "https://finnhub.io/api/v1/stock/metric"
    params = {
        'symbol': ticker,
        'metric': 'all',
        'token': FINNHUB_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        metrics = data.get('metric', {})
        return {
            'pe_ratio': metrics.get('peBasicExclExtraTTM'),
            'pb_ratio': metrics.get('pbQuarterly'),
            'ps_ratio': metrics.get('psTTM'),
            'market_cap': metrics.get('marketCapitalization'),
            'beta': metrics.get('beta'),
            '52w_high': metrics.get('52WeekHigh'),
            '52w_low': metrics.get('52WeekLow'),
            'avg_volume_10d': metrics.get('10DayAverageTradingVolume'),
            'dividend_yield': metrics.get('dividendYieldIndicatedAnnual'),
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching financials for {ticker}: {e}")
        return None


def get_earnings_calendar(ticker: str) -> Optional[Dict]:
    """Get upcoming earnings date"""
    if not FINNHUB_API_KEY:
        return None
    
    url = "https://finnhub.io/api/v1/calendar/earnings"
    params = {
        'symbol': ticker,
        'token': FINNHUB_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        earnings = data.get('earningsCalendar', [])
        if earnings:
            next_earning = earnings[0]
            return {
                'date': next_earning.get('date'),
                'eps_estimate': next_earning.get('epsEstimate'),
                'revenue_estimate': next_earning.get('revenueEstimate'),
                'hour': next_earning.get('hour'),  # 'bmo' (before market open) or 'amc' (after market close)
            }
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching earnings for {ticker}: {e}")
        return None


def format_news_for_context(news_list: List[Dict]) -> str:
    """Format news list as a string for LLM context"""
    if not news_list:
        return "No recent news found."
    
    lines = []
    for item in news_list[:5]:  # Top 5 for context
        lines.append(f"[{item['datetime']}] {item['headline']}")
        if item.get('source'):
            lines[-1] += f" ({item['source']})"
    
    return "\n".join(lines)


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    print("Testing Finnhub news fetcher...")
    
    # Test company news
    print("\n--- IBRX News ---")
    news = get_company_news("IBRX", days=7)
    for item in news[:3]:
        print(f"  [{item['datetime']}] {item['headline']}")
    
    # Test market news
    print("\n--- Market News ---")
    market = get_market_news('general')
    for item in market[:3]:
        print(f"  {item['headline'][:60]}...")
    
    # Test financials
    print("\n--- IBRX Financials ---")
    fins = get_basic_financials("IBRX")
    if fins:
        for k, v in fins.items():
            if v is not None:
                print(f"  {k}: {v}")
