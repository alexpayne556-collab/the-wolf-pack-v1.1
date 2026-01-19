# ============================================================================
# 🐺 FENRIR V2 - COLAB SECTION 3: MARKET-WIDE SCANNER
# ============================================================================
# This scans the ENTIRE market for movers, not just a watchlist
# Fenrir hunts - he doesn't wait for you to bring names
# ============================================================================

import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# GET ALL TRADEABLE STOCKS
# ============================================================================

def get_all_tickers():
    """Get list of all US stocks from major exchanges"""
    
    # We'll use a pre-built list of liquid stocks
    # These are stocks with enough volume to actually trade
    
    # Method 1: Use yfinance screener (basic)
    # Method 2: Pull from a ticker list
    
    # For speed, we'll scan the most liquid ~3000 stocks
    # This covers everything that actually moves with volume
    
    import requests
    
    # NASDAQ traded list
    url = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/nasdaq/nasdaq_tickers.txt"
    try:
        nasdaq = requests.get(url, timeout=10).text.strip().split('\n')
    except:
        nasdaq = []
    
    # NYSE traded list  
    url = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/nyse/nyse_tickers.txt"
    try:
        nyse = requests.get(url, timeout=10).text.strip().split('\n')
    except:
        nyse = []
    
    # Combine and clean
    all_tickers = list(set(nasdaq + nyse))
    
    # Filter out weird tickers (warrants, units, etc)
    clean_tickers = [t for t in all_tickers if t.isalpha() and len(t) <= 5]
    
    print(f"📊 Loaded {len(clean_tickers)} tickers to scan")
    return clean_tickers


# ============================================================================
# FAST SCANNER - PARALLEL PROCESSING
# ============================================================================

def scan_ticker(ticker):
    """Scan a single ticker for today's move"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        
        if len(hist) < 2:
            return None
        
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        change_pct = ((current - prev) / prev) * 100
        
        # Volume check
        avg_vol = hist['Volume'].iloc[:-1].mean()
        today_vol = hist['Volume'].iloc[-1]
        vol_ratio = today_vol / avg_vol if avg_vol > 0 else 0
        
        return {
            'ticker': ticker,
            'price': round(current, 2),
            'change_pct': round(change_pct, 2),
            'volume_ratio': round(vol_ratio, 2),
            'volume': int(today_vol),
        }
    except:
        return None


def scan_market(min_change=5.0, min_volume_ratio=1.5, max_price=50.0, min_price=1.0, max_workers=50):
    """
    Scan entire market for movers
    
    Args:
        min_change: Minimum % move to flag (default 5%)
        min_volume_ratio: Minimum volume vs average (default 1.5x)
        max_price: Max price to consider (default $50)
        min_price: Min price to consider (default $1)
        max_workers: Parallel threads (default 50)
    
    Returns:
        DataFrame of movers sorted by change %
    """
    
    print("🐺 Fenrir scanning market...")
    
    tickers = get_all_tickers()
    movers = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_ticker, t): t for t in tickers}
        
        done = 0
        for future in as_completed(futures):
            done += 1
            if done % 500 == 0:
                print(f"   Scanned {done}/{len(tickers)}...")
            
            result = future.result()
            if result is None:
                continue
            
            # Apply filters
            if abs(result['change_pct']) < min_change:
                continue
            if result['volume_ratio'] < min_volume_ratio:
                continue
            if result['price'] > max_price or result['price'] < min_price:
                continue
            
            movers.append(result)
    
    # Sort by change %
    df = pd.DataFrame(movers)
    if len(df) > 0:
        df = df.sort_values('change_pct', ascending=False)
    
    print(f"\n✅ Scan complete - Found {len(df)} movers")
    return df


# ============================================================================
# RUN SCAN
# ============================================================================

# Scan for movers: 5%+ move, 1.5x volume, $1-50 price range
movers_df = scan_market(min_change=5.0, min_volume_ratio=1.5, max_price=50, min_price=1)

print("\n📈 TODAY'S MOVERS (5%+ move, volume confirmed, $1-50):\n")
print(movers_df.to_string(index=False))

# Save for next section
movers_df.to_csv('todays_movers.csv', index=False)

print("\n✅ Section 3 Complete - Market scanned")
print(f"🐺 Found {len(movers_df)} potential targets")
