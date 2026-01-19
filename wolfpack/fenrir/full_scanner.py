# 🐺 FENRIR V2 - FULL MARKET SCANNER
# Scan entire tradeable universe for movers

import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
import config

# Cache for tradeable tickers (update daily)
_TICKER_CACHE = None
_CACHE_DATE = None

def get_all_tradeable_tickers() -> List[str]:
    """
    Get ~8,000 tradeable US stocks from NASDAQ FTP
    Caches result for the day
    """
    
    global _TICKER_CACHE, _CACHE_DATE
    
    from datetime import date
    today = date.today()
    
    # Return cached if same day
    if _TICKER_CACHE and _CACHE_DATE == today:
        return _TICKER_CACHE
    
    try:
        # NASDAQ FTP has complete list
        nasdaq_url = 'ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt'
        other_url = 'ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt'
        
        nasdaq = pd.read_csv(nasdaq_url, sep='|')
        other = pd.read_csv(other_url, sep='|')
        
        # Filter to common stocks only (not ETFs)
        nasdaq_tickers = nasdaq[nasdaq['ETF'] == 'N']['Symbol'].tolist()
        other_tickers = other[other['ETF'] == 'N']['ACT Symbol'].tolist()
        
        all_tickers = list(set(nasdaq_tickers + other_tickers))
        
        # Remove test symbols and special characters - handle numeric values
        all_tickers = [str(t) for t in all_tickers if isinstance(t, str) and t.isalpha() and len(t) <= 5]
        
        # Cache it
        _TICKER_CACHE = all_tickers
        _CACHE_DATE = today
        
        print(f"Loaded {len(all_tickers)} tradeable tickers")
        return all_tickers
        
    except Exception as e:
        print(f"Error loading tickers from NASDAQ: {e}")
        # Fallback to watchlist if FTP fails
        return config.ALL_WATCHLIST


def scan_single_ticker(ticker: str) -> Optional[Dict]:
    """
    Check one ticker - return if it's a mover
    
    Returns None if not a mover or error
    """
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='5d')
        
        if len(hist) < 2:
            return None
        
        # Get today's data
        price = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        change = ((price - prev) / prev) * 100
        
        # Calculate volume ratio
        avg_vol = hist['Volume'].iloc[:-1].mean()
        today_vol = hist['Volume'].iloc[-1]
        vol_ratio = today_vol / avg_vol if avg_vol > 0 else 0
        
        # Apply filters
        if (abs(change) >= config.FULL_SCAN_MIN_CHANGE and 
            vol_ratio >= config.FULL_SCAN_MIN_VOLUME_RATIO and 
            config.FULL_SCAN_MIN_PRICE <= price <= config.FULL_SCAN_MAX_PRICE and
            avg_vol >= config.FULL_SCAN_MIN_AVG_VOLUME):
            
            return {
                'ticker': ticker,
                'price': float(price),
                'change_pct': float(change),  # Consistent key name
                'change': float(change),  # Keep for backwards compatibility
                'volume_ratio': float(vol_ratio),  # Consistent key name
                'vol_ratio': float(vol_ratio),  # Keep for backwards compatibility
                'avg_volume': int(avg_vol),
            }
            
    except Exception:
        pass
    
    return None


def full_market_scan() -> List[Dict]:
    """
    Scan entire market in parallel
    
    Returns top 50 movers sorted by move size
    """
    
    if not config.FULL_SCAN_ENABLED:
        print("Full market scan disabled in config")
        return []
    
    tickers = get_all_tradeable_tickers()
    print(f"🐺 Scanning {len(tickers)} tickers with {config.FULL_SCAN_MAX_WORKERS} workers...")
    
    movers = []
    completed = 0
    
    # Use thread pool for parallel scanning
    with ThreadPoolExecutor(max_workers=config.FULL_SCAN_MAX_WORKERS) as executor:
        futures = {executor.submit(scan_single_ticker, t): t for t in tickers}
        
        for future in as_completed(futures):
            completed += 1
            if completed % 500 == 0:
                print(f"Progress: {completed}/{len(tickers)} ({len(movers)} movers found)")
            
            result = future.result()
            if result:
                movers.append(result)
    
    # Sort by absolute move size
    movers = sorted(movers, key=lambda x: abs(x['change']), reverse=True)
    
    print(f"✅ Scan complete: Found {len(movers)} movers")
    return movers[:50]  # Top 50 only


def quick_watchlist_scan(tickers: List[str]) -> List[Dict]:
    """
    Quick scan of just watchlist tickers (faster than full scan)
    """
    
    print(f"🐺 Quick scan: {len(tickers)} tickers...")
    
    movers = []
    
    # Use smaller thread pool for watchlist
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(scan_single_ticker, t): t for t in tickers}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                movers.append(result)
    
    # Sort by move size
    movers = sorted(movers, key=lambda x: abs(x['change']), reverse=True)
    
    return movers


def format_scan_results(movers: List[Dict], we_own: List[str]) -> str:
    """Format scan results for display"""
    
    output = "\n" + "=" * 60 + "\n"
    output += f"MARKET SCAN - {len(movers)} MOVERS FOUND\n"
    output += "=" * 60 + "\n\n"
    
    if not movers:
        output += "No significant movers right now.\n"
        return output
    
    # Check if we own any
    owned_movers = [m for m in movers if m['ticker'] in we_own]
    if owned_movers:
        output += "🚨 POSITIONS MOVING:\n"
        for m in owned_movers:
            output += f"  {m['ticker']}: ${m['price']:.2f} ({m['change']:+.1f}%) - {m['vol_ratio']:.1f}x vol\n"
        output += "\n"
    
    # Top 10 movers
    output += "🔥 TOP 10 MOVERS:\n"
    for i, m in enumerate(movers[:10], 1):
        emoji = "⭐" if m['ticker'] in we_own else ""
        output += f"{i}. {m['ticker']}{emoji}: ${m['price']:.2f} ({m['change']:+.1f}%) - {m['vol_ratio']:.1f}x vol\n"
    
    output += "\n" + "=" * 60 + "\n"
    
    return output


# Test function
if __name__ == '__main__':
    print("\n🐺 Testing Full Market Scanner\n")
    
    # Test 1: Get ticker list
    print("Test 1: Loading ticker universe...")
    tickers = get_all_tradeable_tickers()
    print(f"✅ Loaded {len(tickers)} tickers\n")
    
    # Test 2: Quick scan of watchlist only
    print("Test 2: Quick watchlist scan...")
    movers = quick_watchlist_scan(config.ALL_WATCHLIST[:20])  # Just first 20 for speed
    print(format_scan_results(movers, list(config.HOLDINGS.keys())))
    
    print("\n🐺 Scanner test complete!\n")
