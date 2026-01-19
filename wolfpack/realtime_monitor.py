#!/usr/bin/env python3
"""
Wolf Pack V2 - Real-Time Market Monitor
Runs DURING market hours (9:30 AM - 4:00 PM ET)
Detects moves >3% and triggers immediate investigation
"""

import yfinance as yf
import time
from datetime import datetime, time as dtime
import pytz
from config import ALL_TICKERS, TICKER_TO_SECTOR
from wolfpack_db_v2 import init_v2_database, log_realtime_move, get_recent_moves
from catalyst_fetcher import fetch_catalysts

# Constants
SCAN_INTERVAL_SECONDS = 120  # Check every 2 minutes
MOVE_THRESHOLD = 3.0  # Alert on >3% moves
MARKET_OPEN = dtime(9, 30)   # 9:30 AM ET
MARKET_CLOSE = dtime(16, 0)   # 4:00 PM ET
ET_TIMEZONE = pytz.timezone('America/New_York')

class RealTimeMonitor:
    """Monitors stocks during market hours and triggers alerts"""
    
    def __init__(self):
        self.running = False
        self.last_prices = {}  # Track previous prices
        self.alerted_today = set()  # Don't spam same alert
        
    def is_market_open(self):
        """Check if market is currently open"""
        now = datetime.now(ET_TIMEZONE)
        
        # Check if weekday (Monday=0, Friday=4)
        if now.weekday() > 4:
            return False
        
        current_time = now.time()
        return MARKET_OPEN <= current_time <= MARKET_CLOSE
    
    def get_current_price(self, ticker):
        """Get current/latest price for a ticker"""
        try:
            stock = yf.Ticker(ticker)
            # Get most recent data (1 day, 1 minute intervals)
            hist = stock.history(period='1d', interval='1m')
            
            if len(hist) > 0:
                current_price = hist['Close'].iloc[-1]
                current_volume = hist['Volume'].sum()  # Total volume so far today
                
                # Get yesterday's close for % calculation
                hist_day = stock.history(period='5d')
                if len(hist_day) >= 2:
                    prev_close = hist_day['Close'].iloc[-2]
                else:
                    prev_close = current_price
                
                return {
                    'price': current_price,
                    'prev_close': prev_close,
                    'volume': current_volume,
                    'timestamp': datetime.now(ET_TIMEZONE)
                }
            
            return None
            
        except Exception as e:
            print(f"  ❌ Error getting price for {ticker}: {e}")
            return None
    
    def check_for_moves(self):
        """Check all tickers for significant moves"""
        
        now = datetime.now(ET_TIMEZONE)
        print(f"\n🔍 [{now.strftime('%H:%M:%S')}] Scanning {len(ALL_TICKERS)} stocks...", flush=True)
        
        moves_detected = []
        
        for ticker in ALL_TICKERS:
            data = self.get_current_price(ticker)
            
            if not data:
                continue
            
            price = data['price']
            prev_close = data['prev_close']
            
            # Calculate move %
            move_pct = ((price - prev_close) / prev_close) * 100
            
            # Check if this is a big move
            if abs(move_pct) >= MOVE_THRESHOLD:
                # Avoid duplicate alerts for same move
                alert_key = f"{ticker}_{now.strftime('%Y%m%d')}"
                
                if alert_key not in self.alerted_today:
                    self.alerted_today.add(alert_key)
                    
                    sector = TICKER_TO_SECTOR[ticker]
                    
                    move_info = {
                        'ticker': ticker,
                        'sector': sector,
                        'price': price,
                        'prev_close': prev_close,
                        'move_pct': move_pct,
                        'volume': data['volume'],
                        'timestamp': data['timestamp']
                    }
                    
                    moves_detected.append(move_info)
                    
                    # Log to database immediately
                    log_realtime_move(move_info)
                    
                    # Trigger catalyst investigation
                    self.investigate_move(move_info)
        
        if moves_detected:
            print(f"🚨 DETECTED {len(moves_detected)} BIG MOVES:")
            for move in moves_detected:
                direction = "📈" if move['move_pct'] > 0 else "📉"
                print(f"  {direction} {move['ticker']:6} {move['move_pct']:+.1f}% @ ${move['price']:.2f} ({move['sector']})")
        else:
            print("  ✅ No big moves detected")
    
    def investigate_move(self, move_info):
        """Trigger catalyst investigation for a detected move"""
        
        print(f"\n🔍 INVESTIGATING {move_info['ticker']} {move_info['move_pct']:+.1f}%...")
        
        # Fetch catalysts (news + SEC filings)
        catalysts = fetch_catalysts(
            ticker=move_info['ticker'],
            move_timestamp=move_info['timestamp'],
            move_pct=move_info['move_pct']
        )
        
        if catalysts:
            print(f"  ✅ Catalysts found: {catalysts['summary']}")
        else:
            print(f"  ⚠️  No obvious catalyst - manual check needed")
    
    def run(self):
        """Main monitoring loop"""
        
        print("\n" + "🐺"*40)
        print("WOLF PACK V2 - REAL-TIME MARKET MONITOR")
        print("Monitoring 99 stocks during market hours")
        print("Alert threshold: ±{:.1f}%".format(MOVE_THRESHOLD))
        print("🐺"*40 + "\n")
        
        self.running = True
        
        try:
            while self.running:
                # Check if market is open
                if self.is_market_open():
                    self.check_for_moves()
                    
                    # Wait before next scan
                    print(f"  ⏸️  Waiting {SCAN_INTERVAL_SECONDS}s until next scan...")
                    time.sleep(SCAN_INTERVAL_SECONDS)
                    
                else:
                    now = datetime.now(ET_TIMEZONE)
                    print(f"\n💤 Market closed. Current time: {now.strftime('%H:%M:%S ET')}")
                    print(f"   Market hours: {MARKET_OPEN.strftime('%H:%M')} - {MARKET_CLOSE.strftime('%H:%M')} ET")
                    print(f"   Sleeping for 5 minutes...\n")
                    time.sleep(300)  # Check every 5 minutes if market opens
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Monitor stopped by user")
            self.running = False

if __name__ == '__main__':
    # Initialize V2 database
    init_v2_database()
    
    # Start monitoring
    monitor = RealTimeMonitor()
    monitor.run()
