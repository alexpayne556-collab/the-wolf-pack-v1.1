# 🐺 FENRIR V2 - MARKET DATA
# Real-time price and volume data via yfinance

import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, List, Dict

def get_stock_data(ticker: str) -> Optional[Dict]:
    """Get current price, today's move, and volume for a stock"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        
        if len(hist) < 2:
            return None
        
        current = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        change_pct = ((current - prev_close) / prev_close) * 100
        
        # Volume analysis
        avg_volume = hist['Volume'].iloc[:-1].mean()
        today_volume = hist['Volume'].iloc[-1]
        volume_ratio = today_volume / avg_volume if avg_volume > 0 else 1
        
        # 52 week high/low
        hist_1y = stock.history(period="1y")
        high_52w = hist_1y['High'].max() if len(hist_1y) > 0 else current
        low_52w = hist_1y['Low'].min() if len(hist_1y) > 0 else current
        
        return {
            'ticker': ticker,
            'price': round(current, 2),
            'change_pct': round(change_pct, 2),
            'prev_close': round(prev_close, 2),
            'volume': int(today_volume),
            'avg_volume': int(avg_volume),
            'volume_ratio': round(volume_ratio, 2),
            'high_52w': round(high_52w, 2),
            'low_52w': round(low_52w, 2),
            'from_high': round(((current - high_52w) / high_52w) * 100, 2),
            'from_low': round(((current - low_52w) / low_52w) * 100, 2),
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None


def get_multi_stock_data(tickers: List[str]) -> Dict[str, Dict]:
    """Get data for multiple tickers"""
    results = {}
    for ticker in tickers:
        data = get_stock_data(ticker)
        if data:
            results[ticker] = data
    return results


def scan_movers(tickers: List[str], threshold: float = 5.0) -> List[Dict]:
    """Scan a list of tickers for big movers (up OR down)"""
    movers = []
    for ticker in tickers:
        data = get_stock_data(ticker)
        if data and abs(data['change_pct']) >= threshold:
            movers.append(data)
    
    return sorted(movers, key=lambda x: abs(x['change_pct']), reverse=True)


def scan_volume_spikes(tickers: List[str], threshold: float = 2.0) -> List[Dict]:
    """Scan for unusual volume"""
    spikes = []
    for ticker in tickers:
        data = get_stock_data(ticker)
        if data and data['volume_ratio'] >= threshold:
            spikes.append(data)
    
    return sorted(spikes, key=lambda x: x['volume_ratio'], reverse=True)


def scan_near_lows(tickers: List[str], threshold: float = 20.0) -> List[Dict]:
    """Find stocks near 52-week lows (wounded prey)"""
    near_lows = []
    for ticker in tickers:
        data = get_stock_data(ticker)
        if data and data['from_low'] <= threshold:
            near_lows.append(data)
    
    return sorted(near_lows, key=lambda x: x['from_low'])


def scan_near_highs(tickers: List[str], threshold: float = 10.0) -> List[Dict]:
    """Find stocks near 52-week highs (momentum)"""
    near_highs = []
    for ticker in tickers:
        data = get_stock_data(ticker)
        if data and abs(data['from_high']) <= threshold:
            near_highs.append(data)
    
    return sorted(near_highs, key=lambda x: data['from_high'], reverse=True)


def get_sector_performance(watchlist_dict: Dict[str, List[str]]) -> Dict[str, float]:
    """Calculate average performance by sector"""
    sector_perf = {}
    
    for sector, tickers in watchlist_dict.items():
        changes = []
        for ticker in tickers:
            data = get_stock_data(ticker)
            if data:
                changes.append(data['change_pct'])
        
        if changes:
            sector_perf[sector] = round(sum(changes) / len(changes), 2)
    
    return dict(sorted(sector_perf.items(), key=lambda x: x[1], reverse=True))


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    # Test single stock
    print("Testing IBRX:")
    data = get_stock_data("IBRX")
    if data:
        for k, v in data.items():
            print(f"  {k}: {v}")
    
    # Test movers scan
    print("\nScanning for movers...")
    test_tickers = ['IBRX', 'KTOS', 'MU', 'NVDA', 'AAPL']
    movers = scan_movers(test_tickers, threshold=1.0)
    for m in movers:
        print(f"  {m['ticker']}: {m['change_pct']:+.2f}%")
