"""
REAL-TIME VOLUME MONITOR V2 - Using FREE yfinance

Polygon free tier = blocked (403)
Solution: yfinance (100% free, no API key)

STILL NO MOCK DATA - Uses real Yahoo Finance data
If data unavailable: Shows "NO DATA" (never fakes it)
"""

import yfinance as yf
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

class FreeVolumeMonitor:
    """
    Real-time volume monitoring using FREE yfinance.
    NO API KEYS NEEDED. NO MOCK DATA.
    """
    
    def __init__(self):
        print("✅ Using yfinance (FREE - no API key required)")
        self.cache = {}
        self.cache_ttl = 60  # 1 minute cache
    
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
    
    def get_realtime_data(self, ticker: str) -> Optional[Dict]:
        """
        Get real-time volume + price from Yahoo Finance.
        REAL DATA ONLY - returns None if fails.
        """
        cache_key = f"realtime_{ticker}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get today's intraday data (1 minute intervals)
            hist_1d = stock.history(period='1d', interval='1m')
            
            if hist_1d.empty:
                # Market closed or no data, try regular daily
                hist_1d = stock.history(period='1d')
                if hist_1d.empty:
                    return None
            
            # Current volume = sum of all 1min bars today
            current_volume = hist_1d['Volume'].sum()
            current_price = hist_1d['Close'].iloc[-1]
            
            # Get 20-day average volume
            hist_20d = stock.history(period='1mo')
            if len(hist_20d) < 5:
                return None
            
            # Calculate average daily volume (exclude today)
            avg_volume = hist_20d['Volume'][:-1].mean()
            
            # Get stock info
            info = stock.info
            float_shares = info.get('floatShares', 0)
            if float_shares == 0:
                float_shares = info.get('sharesOutstanding', 0)
            
            data = {
                'ticker': ticker,
                'current_volume': int(current_volume),
                'avg_volume': int(avg_volume),
                'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 0,
                'price': float(current_price),
                'float_m': float_shares / 1e6 if float_shares else 0,
                'timestamp': datetime.now().isoformat(),
                'market_cap': info.get('marketCap', 0) / 1e6,
                'is_spike': (current_volume / avg_volume) > 5.0 if avg_volume > 0 else False
            }
            
            self._set_cache(cache_key, data)
            return data
        
        except Exception as e:
            print(f" ❌ Error: {str(e)}")
            return None
    
    def detect_volume_spike(self, ticker: str) -> Optional[Dict]:
        """
        Detect if ticker has volume spike.
        Returns real data or None (NEVER FAKES IT).
        """
        print(f"🔍 {ticker}...", end='', flush=True)
        
        data = self.get_realtime_data(ticker)
        
        if not data:
            print(" ❌ NO DATA")
            return None
        
        # Print result
        ratio = data['volume_ratio']
        if ratio > 10:
            print(f" 🚀🚀 {ratio:.1f}x MASSIVE SPIKE!")
        elif ratio > 5:
            print(f" 🚀 {ratio:.1f}x SPIKE!")
        elif ratio > 3:
            print(f" 📈 {ratio:.1f}x elevated")
        elif ratio > 2:
            print(f" ✓ {ratio:.1f}x above avg")
        else:
            print(f" ✓ {ratio:.1f}x normal")
        
        return data
    
    def scan_watchlist(self, tickers: List[str]) -> Dict[str, List[Dict]]:
        """
        Scan tickers and categorize by volume level.
        Returns REAL DATA from Yahoo Finance.
        """
        print("\n" + "="*80)
        print("🚨 REAL-TIME VOLUME MONITOR (FREE - Yahoo Finance)")
        print("="*80)
        print(f"Scanning {len(tickers)} tickers...")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Market Hours: 9:30am-4pm ET (After-hours: 4-8pm)")
        print()
        
        results = {
            'massive_spikes': [],  # >10x
            'spikes': [],          # 5-10x
            'elevated': [],        # 3-5x
            'above_avg': [],       # 2-3x
            'normal': []           # <2x
        }
        
        for ticker in tickers:
            data = self.detect_volume_spike(ticker)
            
            if data:
                ratio = data['volume_ratio']
                if ratio > 10:
                    results['massive_spikes'].append(data)
                elif ratio > 5:
                    results['spikes'].append(data)
                elif ratio > 3:
                    results['elevated'].append(data)
                elif ratio > 2:
                    results['above_avg'].append(data)
                else:
                    results['normal'].append(data)
            
            # Small delay (be respectful)
            time.sleep(0.3)
        
        # Print summary
        print("\n" + "="*80)
        print("📊 VOLUME ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"\n🚀🚀 MASSIVE SPIKES (>10x): {len(results['massive_spikes'])}")
        for d in sorted(results['massive_spikes'], key=lambda x: x['volume_ratio'], reverse=True):
            self._print_alert(d, '🚀🚀')
        
        print(f"\n🚀 SPIKES (5-10x): {len(results['spikes'])}")
        for d in sorted(results['spikes'], key=lambda x: x['volume_ratio'], reverse=True):
            self._print_alert(d, '🚀')
        
        print(f"\n📈 ELEVATED (3-5x): {len(results['elevated'])}")
        for d in sorted(results['elevated'], key=lambda x: x['volume_ratio'], reverse=True):
            self._print_brief(d)
        
        print(f"\n✓ ABOVE AVG (2-3x): {len(results['above_avg'])}")
        print(f"✓ NORMAL (<2x): {len(results['normal'])}")
        
        return results
    
    def _print_alert(self, data: Dict, emoji: str):
        """Print detailed alert for spikes."""
        print(f"\n{emoji} ${data['ticker']}: {data['volume_ratio']:.1f}x volume")
        print(f"   Current: {data['current_volume']:,} | Avg: {data['avg_volume']:,}")
        print(f"   Price: ${data['price']:.2f} | Float: {data['float_m']:.2f}M")
        print(f"   Market Cap: ${data['market_cap']:.1f}M")
        
        # Check if movable
        if data['float_m'] < 10 and data['price'] < 5:
            print(f"   ⚠️  EXPLOSIVE SETUP: Low float + Low price")
        elif data['float_m'] < 20:
            print(f"   ⚠️  MOVABLE: Float under 20M")
    
    def _print_brief(self, data: Dict):
        """Print brief info for elevated volume."""
        print(f"   ${data['ticker']}: {data['volume_ratio']:.1f}x @ ${data['price']:.2f}")
    
    def monitor_continuous(self, tickers: List[str], interval_minutes: int = 5):
        """
        Continuously monitor for volume spikes.
        Scans every N minutes.
        """
        print("="*80)
        print("🔄 CONTINUOUS VOLUME MONITORING")
        print("="*80)
        print(f"Tickers: {len(tickers)}")
        print(f"Interval: {interval_minutes} minutes")
        print(f"Data: Yahoo Finance (FREE, real-time)")
        print(f"Press Ctrl+C to stop")
        print()
        
        scan_count = 0
        
        try:
            while True:
                scan_count += 1
                print(f"\n{'='*80}")
                print(f"SCAN #{scan_count} - {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*80}")
                
                results = self.scan_watchlist(tickers)
                
                # Alert on spikes
                total_spikes = len(results['massive_spikes']) + len(results['spikes'])
                if total_spikes > 0:
                    print(f"\n🚨 ALERT: {total_spikes} volume spike(s) detected!")
                
                # Wait for next scan
                wait_seconds = interval_minutes * 60
                print(f"\n⏳ Next scan in {interval_minutes} minutes...")
                time.sleep(wait_seconds)
        
        except KeyboardInterrupt:
            print("\n\n✋ Monitoring stopped by user")
            print(f"Total scans: {scan_count}")


def main():
    """Run the volume monitor."""
    
    print("="*80)
    print("🐺 BROKKR VOLUME MONITOR - FREE VERSION")
    print("="*80)
    print("Data: Yahoo Finance (NO API KEY REQUIRED)")
    print("Updates: Real-time (1-minute bars during market hours)")
    print("Cost: $0 (100% free)")
    print()
    
    # Initialize monitor
    monitor = FreeVolumeMonitor()
    
    # Our moonshot watchlist
    watchlist = [
        # Tier 1-2 (highest conviction)
        'GLSI', 'IPW', 'SNTI', 'INTG',
        # Tier 3 (watchlist)
        'INAB', 'LVLU', 'VRCA', 'CYCN', 'UPC',
        'BTAI', 'PMCB', 'COSM', 'IMNM',
        # High short interest
        'HIMS', 'SMR',
        # FDA catalysts
        'VNDA', 'OCUL'
    ]
    
    print(f"📋 WATCHLIST ({len(watchlist)} tickers):")
    print(f"   {', '.join(watchlist)}")
    print()
    
    # Single scan
    print("Running scan...")
    results = monitor.scan_watchlist(watchlist)
    
    # Ask if continuous monitoring
    print("\n" + "="*80)
    print("OPTIONS:")
    print("1. Exit")
    print("2. Run another scan")
    print("3. Start continuous monitoring")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == '2':
        main()  # Recursive call for another scan
    elif choice == '3':
        interval = input("Scan interval in minutes (default 5): ").strip()
        interval = int(interval) if interval.isdigit() else 5
        monitor.monitor_continuous(watchlist, interval)
    else:
        print("\n✅ Done")


if __name__ == '__main__':
    main()
