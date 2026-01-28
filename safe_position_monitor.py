"""
SAFE POSITION MONITOR - Won't Crash Your Computer
==================================================
Monitors ONLY your 9 positions, not all 205 tickers.

Features:
- Rate-limited API calls
- Memory-efficient
- Runs continuously without crashing
- Alerts on volume spikes
- Integrates with thinking engine

Safety:
- Only checks 9 tickers (your positions)
- 5-minute intervals (not constant)
- Proper rate limiting
- Error handling
"""

import os
import sys
import time
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_fetcher import DataFetcher
from alerter import Alerter
from fenrir_thinking_engine import FenrirThinkingEngine


class SafePositionMonitor:
    """Monitor YOUR positions only - safe and efficient"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.alerter = Alerter()
        self.brain = FenrirThinkingEngine()
        
        # Database connection (Integration 3)
        self.db_path = "wolfpack.db"
        self._init_database()
        
        # Load your positions from brain config
        self.positions = self._load_positions()
        
        print(f"🐺 Safe Position Monitor Initialized")
        print(f"   Monitoring {len(self.positions)} positions")
        print(f"   Check interval: 5 minutes")
        print(f"   Rate limited: ✅")
        print(f"   Memory efficient: ✅")
        print(f"   Brain integration: ✅")
        print(f"   Database logging: ✅")
    
    def _load_positions(self):
        """Load your current positions from brain config"""
        try:
            with open('brain_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            watchlists = config.get('watchlists', {})
            my_positions = watchlists.get('MY_POSITIONS', {})
            
            # Extract tickers
            if isinstance(my_positions, dict) and 'tickers' in my_positions:
                return list(my_positions['tickers'].keys())
            elif isinstance(my_positions, dict):
                # Filter out metadata keys
                return [k for k in my_positions.keys() 
                       if k not in ['description', 'monitoring_frequency', 'priority']]
            else:
                # Fallback - hardcode your 9 positions
                return ["MU", "RCAT", "UUUU", "MRNO", "IVF", "NTLA", "RDW", "UEC", "IBRX"]
        
        except Exception as e:
            print(f"⚠️  Could not load positions from config: {e}")
            # Fallback
            return ["MU", "RCAT", "UUUU", "MRNO", "IVF", "NTLA", "RDW", "UEC", "IBRX"]
    
    def _init_database(self):
        """Initialize database tables if they don't exist (Integration 3)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Price history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    change REAL,
                    change_pct REAL,
                    volume INTEGER,
                    source TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Brain thoughts table (already exists but ensure it's there)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS brain_thoughts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT,
                    thought_type TEXT,
                    reasoning TEXT,
                    confidence REAL,
                    action TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Database initialization error: {e}")
    
    def _log_quote_to_db(self, quote: dict):
        """Log quote to database (Integration 3)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO price_history (symbol, price, change, change_pct, volume, source, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                quote['ticker'],
                quote['price'],
                quote.get('change', 0),
                quote['change_pct'],
                quote.get('volume', 0),
                quote.get('source', 'finnhub'),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Database logging error: {e}")
    
    def _log_thought_to_db(self, thought: dict):
        """Log brain thought to database (Integration 3)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO brain_thoughts (ticker, thought_type, reasoning, confidence, action, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                thought['ticker'],
                thought['thought_type'],
                thought['reasoning'],
                thought['confidence'],
                thought['action'],
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Thought logging error: {e}")
    
    def check_position(self, ticker: str) -> dict:
        """Check one position with full analysis"""
        
        # Get quote
        quote = self.data_fetcher.get_quote(ticker)
        if not quote:
            return {'ticker': ticker, 'status': 'failed'}
        
        # Get volume analysis
        volume_data = self.data_fetcher.get_volume_analysis(ticker)
        
        result = {
            'ticker': ticker,
            'price': quote['price'],
            'change_pct': quote['change_pct'],
            'volume': quote['volume'],
            'status': 'ok'
        }
        
        # Check for volume spike
        if volume_data and volume_data['is_spike']:
            result['volume_spike'] = True
            result['volume_ratio'] = volume_data['volume_ratio']
            
            # Get news to understand WHY
            news = self.data_fetcher.get_news(ticker, limit=3)
            result['recent_news'] = news
        else:
            result['volume_spike'] = False
        
        return result
    
    def monitor_loop(self, interval_minutes: int = 5, max_iterations: int = None):
        """
        Main monitoring loop - SAFE, won't crash
        
        Args:
            interval_minutes: Minutes between checks (default 5)
            max_iterations: Stop after N iterations (None = infinite)
        """
        iteration = 0
        
        print(f"\n{'='*70}")
        print(f"🐺 WOLF PACK POSITION MONITOR - ACTIVE")
        print(f"{'='*70}")
        print(f"Monitoring: {', '.join(self.positions)}")
        print(f"Interval: Every {interval_minutes} minutes")
        print(f"Press Ctrl+C to stop")
        print(f"{'='*70}\n")
        
        try:
            while True:
                iteration += 1
                
                if max_iterations and iteration > max_iterations:
                    print(f"\n✅ Completed {max_iterations} iterations")
                    break
                
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scan #{iteration}")
                print("-" * 70)
                
                # Check market status first
                market_status = self.data_fetcher.check_market_status()
                print(f"Market: {market_status['session'].upper()}")
                
                # Check each position
                for i, ticker in enumerate(self.positions, 1):
                    print(f"\n  [{i}/{len(self.positions)}] Checking {ticker}...", end=" ")
                    
                    try:
                        result = self.check_position(ticker)
                        
                        if result['status'] == 'failed':
                            print("❌ Failed")
                            continue
                        
                        # Display result
                        print(f"${result['price']:.2f} ({result['change_pct']:+.1f}%)", end="")
                        
                        # Check for alerts
                        if result.get('volume_spike'):
                            print(f" 🔥 VOLUME SPIKE {result['volume_ratio']:.1f}x")
                            
                            # INTEGRATION 1: Ask brain to think about it
                            print(f"      🧠 Consulting brain...")
                            thought = self.brain.think_about_volume_spike(
                                ticker=ticker,
                                volume_ratio=result['volume_ratio'],
                                price_change=result['change_pct'],
                                news=result.get('recent_news')
                            )
                            
                            # INTEGRATION 3: Log thought to database
                            self._log_thought_to_db(thought)
                            
                            # Alert via Discord WITH brain's reasoning
                            self.alerter.alert_brain_thought(
                                thought_type='volume_spike',
                                trigger=f"{ticker} volume {result['volume_ratio']:.1f}x",
                                reasoning=thought['reasoning'],
                                confidence=thought['confidence'],
                                action=thought['action']
                            )
                            
                            print(f"      💡 Brain: {thought['action']}")
                            print(f"      📊 Confidence: {thought['confidence']}%")
                            
                            # Check if there's news
                            if result.get('recent_news'):
                                print(f"      📰 Latest: {result['recent_news'][0]['headline'][:60]}...")
                        else:
                            print(f" ✅ Normal")
                        
                        # INTEGRATION 3: Log all quotes to database
                        self._log_quote_to_db(result)
                        
                        # Polite delay between tickers
                        time.sleep(1)
                    
                    except Exception as e:
                        print(f"❌ Error: {e}")
                
                print(f"\n{'='*70}")
                print(f"Scan #{iteration} complete. Next scan in {interval_minutes} minutes.")
                print(f"{'='*70}")
                
                # Wait before next iteration
                time.sleep(interval_minutes * 60)
        
        except KeyboardInterrupt:
            print(f"\n\n🛑 Monitor stopped by user")
            print(f"Completed {iteration} scans")
    
    def scan_once(self):
        """Run one scan and exit - good for testing"""
        print(f"\n{'='*70}")
        print(f"🐺 SINGLE POSITION SCAN")
        print(f"{'='*70}\n")
        
        results = []
        
        for i, ticker in enumerate(self.positions, 1):
            print(f"[{i}/{len(self.positions)}] {ticker}...", end=" ")
            
            result = self.check_position(ticker)
            results.append(result)
            
            if result['status'] == 'ok':
                spike_text = f"🔥 {result['volume_ratio']:.1f}x" if result.get('volume_spike') else "✅"
                print(f"${result['price']:.2f} ({result['change_pct']:+.1f}%) {spike_text}")
                
                # INTEGRATION 3: Log to database
                self._log_quote_to_db(result)
                
                # If volume spike, get brain analysis
                if result.get('volume_spike'):
                    thought = self.brain.think_about_volume_spike(
                        ticker=ticker,
                        volume_ratio=result['volume_ratio'],
                        price_change=result['change_pct'],
                        news=result.get('recent_news')
                    )
                    self._log_thought_to_db(thought)
                    print(f"    🧠 {thought['action']} (confidence: {thought['confidence']}%)")
            else:
                print("❌ Failed")
            
            time.sleep(1)  # Polite delay
        
        print(f"\n{'='*70}")
        print(f"✅ Scan Complete")
        
        # Summary
        spikes = [r for r in results if r.get('volume_spike')]
        if spikes:
            print(f"\n🔥 Volume Spikes Detected: {len(spikes)}")
            for r in spikes:
                print(f"   • {r['ticker']}: {r['volume_ratio']:.1f}x avg volume")
        else:
            print(f"\n✅ No volume spikes detected")
        
        print(f"{'='*70}\n")
        
        return results


def main():
    """Main entry point"""
    
    # Check if we should run once or continuously
    import sys
    
    monitor = SafePositionMonitor()
    
    if '--once' in sys.argv or '-1' in sys.argv:
        # Single scan
        monitor.scan_once()
    elif '--test' in sys.argv:
        # Test mode - 3 iterations, 1 minute intervals
        print("\n⚙️  TEST MODE: 3 scans, 1 minute intervals\n")
        monitor.monitor_loop(interval_minutes=1, max_iterations=3)
    else:
        # Continuous monitoring
        monitor.monitor_loop(interval_minutes=5)


if __name__ == "__main__":
    main()
