# 🐺 FENRIR V2 - PREMARKET TRACKER
# Track gaps and detect reversals at open

from datetime import datetime, time
from typing import Dict, Optional
import yfinance as yf
import database

class PremarketTracker:
    """Track pre-market gaps and detect reversals"""
    
    def __init__(self):
        self.premarket_start = time(4, 0)   # 4:00 AM ET
        self.market_open = time(9, 30)      # 9:30 AM ET
        self.premarket_data = {}  # ticker -> snapshot
    
    def snapshot_premarket(self, ticker: str) -> Optional[Dict]:
        """Take snapshot of pre-market price and direction"""
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get current price (pre-market if available)
            current = stock.info.get('regularMarketPrice') or stock.info.get('currentPrice')
            prev_close = stock.info.get('previousClose')
            
            if not current or not prev_close:
                return None
            
            gap_pct = ((current - prev_close) / prev_close) * 100
            
            snapshot = {
                'ticker': ticker,
                'timestamp': datetime.now().isoformat(),
                'premarket_price': current,
                'prev_close': prev_close,
                'gap_pct': gap_pct,
                'direction': 'UP' if gap_pct > 0 else 'DOWN',
            }
            
            # Cache it
            self.premarket_data[ticker] = snapshot
            
            return snapshot
            
        except Exception as e:
            print(f"Error snapshot {ticker}: {e}")
            return None
    
    def check_for_reversal(self, ticker: str) -> Optional[Dict]:
        """
        Check if stock reversed from pre-market
        
        Returns reversal data if detected, None otherwise
        """
        
        # Need pre-market snapshot
        if ticker not in self.premarket_data:
            return None
        
        pm_snapshot = self.premarket_data[ticker]
        
        try:
            # Get current price
            stock = yf.Ticker(ticker)
            current = stock.info.get('regularMarketPrice') or stock.info.get('currentPrice')
            
            if not current:
                return None
            
            pm_price = pm_snapshot['premarket_price']
            prev_close = pm_snapshot['prev_close']
            
            # Calculate changes
            pm_vs_close = ((pm_price - prev_close) / prev_close) * 100
            current_vs_close = ((current - prev_close) / prev_close) * 100
            
            # Detect reversal
            reversal = None
            
            if pm_vs_close < -2 and current_vs_close > 0:
                # Was red pre-market, now green
                reversal = 'RED_TO_GREEN'
            elif pm_vs_close > 2 and current_vs_close < 0:
                # Was green pre-market, now red
                reversal = 'GREEN_TO_RED'
            
            if reversal:
                return {
                    'ticker': ticker,
                    'reversal_type': reversal,
                    'premarket_pct': pm_vs_close,
                    'current_pct': current_vs_close,
                    'reversal_magnitude': abs(current_vs_close - pm_vs_close),
                    'timestamp': datetime.now().isoformat(),
                }
            
        except Exception as e:
            print(f"Error checking reversal {ticker}: {e}")
        
        return None
    
    def scan_for_gaps(self, tickers: list, min_gap_pct: float = 3.0) -> list:
        """Scan multiple tickers for pre-market gaps"""
        
        gaps = []
        
        for ticker in tickers:
            snapshot = self.snapshot_premarket(ticker)
            if snapshot and abs(snapshot['gap_pct']) >= min_gap_pct:
                gaps.append(snapshot)
        
        # Sort by gap size
        gaps.sort(key=lambda x: abs(x['gap_pct']), reverse=True)
        
        return gaps
    
    def format_gap_report(self, gaps: list) -> str:
        """Format pre-market gap report"""
        
        if not gaps:
            return "\n🐺 No significant pre-market gaps\n"
        
        output = "\n" + "=" * 60 + "\n"
        output += f"🐺 PRE-MARKET GAPS - {len(gaps)} found\n"
        output += "=" * 60 + "\n\n"
        
        for gap in gaps[:10]:
            emoji = "🟢" if gap['gap_pct'] > 0 else "🔴"
            output += f"{emoji} {gap['ticker']}: ${gap['premarket_price']:.2f} ({gap['gap_pct']:+.1f}%)\n"
            output += f"   Previous close: ${gap['prev_close']:.2f}\n\n"
        
        output += "⚠️  WATCH FOR REVERSALS AT OPEN\n"
        output += "=" * 60 + "\n"
        
        return output


def log_premarket_snapshot(ticker: str, snapshot: Dict):
    """Save pre-market snapshot to database"""
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO daily_summary (date, ticker, open, close, change_pct, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(date, ticker) DO UPDATE SET
            notes = 'PM: ' || excluded.close || ' (' || excluded.change_pct || '%)'
    ''', (
        snapshot['timestamp'][:10],
        ticker,
        snapshot['premarket_price'],
        snapshot['prev_close'],
        snapshot['gap_pct'],
        f"Pre-market gap {snapshot['gap_pct']:+.1f}%"
    ))
    
    conn.commit()
    conn.close()


# Test
if __name__ == '__main__':
    import config
    
    print("\n🐺 Testing Pre-Market Tracker\n")
    
    tracker = PremarketTracker()
    
    # Test 1: Snapshot holdings
    print("Taking pre-market snapshots of holdings...")
    for ticker in config.HOLDINGS.keys():
        snap = tracker.snapshot_premarket(ticker)
        if snap:
            print(f"  {ticker}: ${snap['premarket_price']:.2f} ({snap['gap_pct']:+.1f}%)")
    
    print("\n🐺 Pre-market tracker ready\n")
