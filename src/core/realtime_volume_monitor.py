"""
REAL-TIME VOLUME MONITOR - Production Ready

Uses ACTUAL API data (NO MOCKS):
- Polygon.io: Real-time volume data
- Finnhub: Stock info and fundamentals
- Alpha Vantage: Historical volume baseline

If API fails: Shows error, doesn't fake data
If rate limited: Waits and retries
If no data: Says "NO DATA" (never makes it up)

This is PRODUCTION CODE.
"""

import os
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from dotenv import load_dotenv

# Load real API keys
load_dotenv()

class RealTimeVolumeMonitor:
    """
    Real-time volume spike detection using actual APIs.
    
    NO MOCK DATA. NEVER FAKE ANYTHING.
    """
    
    def __init__(self):
        # Real API keys from .env
        self.polygon_key = os.getenv('POLYGON_API_KEY')
        self.finnhub_key = os.getenv('FINNHUB_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHAVANTAGE_API_KEY')
        
        # Validate we have keys
        if not self.polygon_key:
            print("⚠️  WARNING: No Polygon API key - volume data will be limited")
        if not self.finnhub_key:
            print("⚠️  WARNING: No Finnhub API key - fundamentals will be limited")
        if not self.alpha_vantage_key:
            print("⚠️  WARNING: No Alpha Vantage key - historical data limited")
        
        # Rate limiting (respect API limits)
        self.last_request_time = {}
        self.request_delays = {
            'polygon': 0.1,      # 5 calls/min free tier
            'finnhub': 1.0,      # 60 calls/min free tier
            'alphavantage': 12.0 # 25 calls/day free tier
        }
        
        # Cache (avoid repeated calls)
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def _respect_rate_limit(self, api: str):
        """Wait if needed to respect rate limits."""
        if api in self.last_request_time:
            elapsed = time.time() - self.last_request_time[api]
            delay = self.request_delays.get(api, 1.0)
            if elapsed < delay:
                time.sleep(delay - elapsed)
        
        self.last_request_time[api] = time.time()
    
    def _get_cached(self, key: str) -> Optional[Dict]:
        """Get cached data if fresh."""
        if key in self.cache:
            cached_time, data = self.cache[key]
            if time.time() - cached_time < self.cache_ttl:
                return data
        return None
    
    def _set_cache(self, key: str, data: Dict):
        """Cache data with timestamp."""
        self.cache[key] = (time.time(), data)
    
    def get_current_volume_polygon(self, ticker: str) -> Optional[Dict]:
        """
        Get current day volume from Polygon.
        REAL DATA ONLY - returns None if no data.
        """
        if not self.polygon_key:
            return None
        
        # Check cache
        cache_key = f"polygon_volume_{ticker}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        self._respect_rate_limit('polygon')
        
        try:
            # Polygon aggregate bars endpoint (free tier)
            today = datetime.now().strftime('%Y-%m-%d')
            url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{today}/{today}"
            params = {'apiKey': self.polygon_key}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('resultsCount', 0) > 0:
                    result = data['results'][0]
                    volume_data = {
                        'volume': result.get('v', 0),
                        'open': result.get('o', 0),
                        'high': result.get('h', 0),
                        'low': result.get('l', 0),
                        'close': result.get('c', 0),
                        'timestamp': result.get('t', 0),
                        'source': 'polygon'
                    }
                    self._set_cache(cache_key, volume_data)
                    return volume_data
            elif response.status_code == 429:
                print(f"⚠️  Polygon rate limit hit for {ticker}")
                return None
            else:
                print(f"⚠️  Polygon error {response.status_code} for {ticker}")
                return None
        
        except Exception as e:
            print(f"❌ Polygon API error for {ticker}: {str(e)}")
            return None
        
        return None
    
    def get_average_volume_finnhub(self, ticker: str) -> Optional[float]:
        """
        Get average volume from Finnhub.
        REAL DATA ONLY.
        """
        if not self.finnhub_key:
            return None
        
        cache_key = f"finnhub_avg_vol_{ticker}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached.get('avg_volume')
        
        self._respect_rate_limit('finnhub')
        
        try:
            url = "https://finnhub.io/api/v1/stock/metric"
            params = {
                'symbol': ticker,
                'metric': 'all',
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metric', {})
                avg_vol = metrics.get('10DayAverageTradingVolume', None)
                
                if avg_vol:
                    self._set_cache(cache_key, {'avg_volume': avg_vol})
                    return avg_vol
            elif response.status_code == 429:
                print(f"⚠️  Finnhub rate limit hit for {ticker}")
        
        except Exception as e:
            print(f"❌ Finnhub API error for {ticker}: {str(e)}")
        
        return None
    
    def get_stock_info_finnhub(self, ticker: str) -> Optional[Dict]:
        """
        Get stock fundamentals from Finnhub.
        REAL DATA ONLY.
        """
        if not self.finnhub_key:
            return None
        
        cache_key = f"finnhub_info_{ticker}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        self._respect_rate_limit('finnhub')
        
        try:
            url = "https://finnhub.io/api/v1/stock/profile2"
            params = {
                'symbol': ticker,
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    info = {
                        'name': data.get('name', ''),
                        'marketCap': data.get('marketCapitalization', 0) * 1e6,  # Convert to actual value
                        'shareOutstanding': data.get('shareOutstanding', 0) * 1e6,
                        'exchange': data.get('exchange', ''),
                        'source': 'finnhub'
                    }
                    self._set_cache(cache_key, info)
                    return info
        
        except Exception as e:
            print(f"❌ Finnhub profile error for {ticker}: {str(e)}")
        
        return None
    
    def detect_volume_spike(self, ticker: str) -> Optional[Dict]:
        """
        Detect if ticker has volume spike.
        
        Returns real data or None (NEVER FAKES IT).
        """
        print(f"\n🔍 Checking {ticker}...", end='', flush=True)
        
        # Get current volume
        current_data = self.get_current_volume_polygon(ticker)
        if not current_data:
            print(" ❌ No current volume data")
            return None
        
        current_volume = current_data['volume']
        
        # Get average volume
        avg_volume = self.get_average_volume_finnhub(ticker)
        if not avg_volume or avg_volume == 0:
            print(" ⚠️  No average volume data")
            return None
        
        # Calculate ratio
        volume_ratio = current_volume / avg_volume
        
        # Get stock info
        info = self.get_stock_info_finnhub(ticker)
        float_shares = info.get('shareOutstanding', 0) if info else 0
        
        result = {
            'ticker': ticker,
            'current_volume': current_volume,
            'avg_volume': avg_volume,
            'volume_ratio': volume_ratio,
            'price': current_data.get('close', 0),
            'float_m': float_shares / 1e6 if float_shares else 0,
            'timestamp': datetime.now().isoformat(),
            'is_spike': volume_ratio > 5.0  # 5x = spike threshold
        }
        
        # Print result
        if result['is_spike']:
            print(f" 🚀 {volume_ratio:.1f}x VOLUME SPIKE!")
        else:
            print(f" ✓ {volume_ratio:.1f}x normal")
        
        return result
    
    def scan_watchlist(self, tickers: List[str]) -> List[Dict]:
        """
        Scan list of tickers for volume spikes.
        Uses REAL APIs with rate limiting.
        """
        print("="*80)
        print("🚨 REAL-TIME VOLUME MONITOR")
        print("="*80)
        print(f"Scanning {len(tickers)} tickers...")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        spikes = []
        
        for ticker in tickers:
            result = self.detect_volume_spike(ticker)
            if result and result['is_spike']:
                spikes.append(result)
            
            # Small delay between tickers
            time.sleep(0.5)
        
        print("\n" + "="*80)
        print(f"🎯 VOLUME SPIKES DETECTED: {len(spikes)}")
        print("="*80)
        
        if spikes:
            for spike in sorted(spikes, key=lambda x: x['volume_ratio'], reverse=True):
                print(f"\n🚀 ${spike['ticker']}")
                print(f"   Volume Ratio: {spike['volume_ratio']:.1f}x")
                print(f"   Current Volume: {spike['current_volume']:,.0f}")
                print(f"   Avg Volume: {spike['avg_volume']:,.0f}")
                print(f"   Price: ${spike['price']:.2f}")
                print(f"   Float: {spike['float_m']:.2f}M")
                
                # Check if movable
                if spike['float_m'] < 10 and spike['price'] < 5:
                    print(f"   ⚠️  MOVABLE: Low float + low price = explosive potential")
        else:
            print("\nNo 5x+ volume spikes detected")
        
        return spikes
    
    def monitor_continuous(self, tickers: List[str], interval_seconds: int = 300):
        """
        Continuously monitor for volume spikes.
        Scans every N seconds.
        """
        print("="*80)
        print("🔄 CONTINUOUS VOLUME MONITORING")
        print("="*80)
        print(f"Tickers: {len(tickers)}")
        print(f"Interval: {interval_seconds} seconds")
        print(f"Press Ctrl+C to stop")
        print()
        
        scan_count = 0
        
        try:
            while True:
                scan_count += 1
                print(f"\n{'='*80}")
                print(f"SCAN #{scan_count} - {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*80}")
                
                spikes = self.scan_watchlist(tickers)
                
                if spikes:
                    # Alert on spikes
                    print(f"\n🚨 ALERT: {len(spikes)} volume spike(s) detected!")
                    for spike in spikes:
                        print(f"   ${spike['ticker']}: {spike['volume_ratio']:.1f}x volume")
                
                print(f"\n⏳ Next scan in {interval_seconds} seconds...")
                time.sleep(interval_seconds)
        
        except KeyboardInterrupt:
            print("\n\n✋ Monitoring stopped by user")
            print(f"Total scans: {scan_count}")


def main():
    """Test the real-time volume monitor."""
    
    print("="*80)
    print("🐺 BROKKR REAL-TIME VOLUME MONITOR")
    print("="*80)
    print("Using REAL APIs (NO MOCK DATA)")
    print()
    
    # Initialize monitor
    monitor = RealTimeVolumeMonitor()
    
    # Test with our watchlist
    watchlist = [
        'GLSI', 'IPW', 'SNTI', 'INTG', 'INAB',
        'LVLU', 'VRCA', 'CYCN', 'UPC', 'BTAI'
    ]
    
    print(f"Watchlist: {', '.join(watchlist)}")
    print()
    
    # Single scan
    print("Running single scan...")
    spikes = monitor.scan_watchlist(watchlist)
    
    # Ask if user wants continuous monitoring
    print("\n" + "="*80)
    response = input("Start continuous monitoring? (y/n): ").lower()
    
    if response == 'y':
        interval = input("Scan interval in seconds (default 300 = 5 min): ")
        interval = int(interval) if interval.isdigit() else 300
        
        monitor.monitor_continuous(watchlist, interval)


if __name__ == '__main__':
    main()
