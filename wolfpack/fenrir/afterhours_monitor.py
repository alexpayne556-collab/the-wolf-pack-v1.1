# 🐺 FENRIR V2 - AFTER-HOURS MONITOR
# Track after-hours movement and news

from datetime import datetime, time
from typing import Dict, List, Optional
import yfinance as yf
from news_fetcher import get_company_news
import config
import database

class AfterHoursMonitor:
    """Monitor after-hours activity on positions"""
    
    def __init__(self):
        self.market_close = time(16, 0)  # 4:00 PM ET
        self.ah_end = time(20, 0)        # 8:00 PM ET
        self.ah_threshold = 3.0          # Alert on 3%+ AH moves
        
        self.close_prices = {}  # ticker -> close price
    
    def is_after_hours(self) -> bool:
        """Check if currently after hours"""
        now = datetime.now().time()
        return self.market_close <= now <= self.ah_end
    
    def capture_close_prices(self, tickers: List[str]):
        """Save closing prices for AH comparison"""
        
        print(f"🐺 Capturing close prices for {len(tickers)} positions...")
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1d')
                
                if not hist.empty:
                    close = hist['Close'].iloc[-1]
                    self.close_prices[ticker] = float(close)
                    print(f"  {ticker}: ${close:.2f}")
            except Exception as e:
                print(f"  Error {ticker}: {e}")
    
    def check_after_hours_move(self, ticker: str) -> Optional[Dict]:
        """Check if ticker moved significantly after hours"""
        
        if ticker not in self.close_prices:
            return None
        
        try:
            stock = yf.Ticker(ticker)
            
            # Try to get post-market price
            current = stock.info.get('postMarketPrice') or stock.info.get('regularMarketPrice')
            
            if not current:
                return None
            
            close = self.close_prices[ticker]
            ah_change = ((current - close) / close) * 100
            
            if abs(ah_change) >= self.ah_threshold:
                return {
                    'ticker': ticker,
                    'close': close,
                    'ah_price': current,
                    'ah_change_pct': ah_change,
                    'timestamp': datetime.now().isoformat(),
                    'severity': 'URGENT' if abs(ah_change) >= 5 else 'WARNING',
                }
        except Exception as e:
            print(f"Error checking AH for {ticker}: {e}")
        
        return None
    
    def scan_after_hours(self, tickers: List[str]) -> List[Dict]:
        """Scan all tickers for AH movement"""
        
        movers = []
        
        for ticker in tickers:
            move = self.check_after_hours_move(ticker)
            if move:
                movers.append(move)
        
        # Sort by absolute move
        movers.sort(key=lambda x: abs(x['ah_change_pct']), reverse=True)
        
        return movers
    
    def check_after_hours_news(self, ticker: str) -> List[Dict]:
        """Check for news that dropped after close"""
        
        # Get news from last 4 hours
        news = get_company_news(ticker, days=1)
        
        # Filter to after 4 PM ET
        after_close = []
        cutoff = datetime.now().replace(hour=16, minute=0, second=0)
        
        for item in news:
            try:
                news_time = datetime.fromisoformat(item['datetime'])
                if news_time >= cutoff:
                    after_close.append(item)
            except:
                pass
        
        return after_close
    
    def generate_ah_report(self, tickers: List[str]) -> str:
        """Generate after-hours activity report"""
        
        if not self.is_after_hours():
            return "\n🐺 Market still open - AH monitoring starts at 4 PM\n"
        
        output = "\n" + "=" * 60 + "\n"
        output += "🐺 AFTER-HOURS REPORT\n"
        output += "=" * 60 + "\n\n"
        
        # Price moves
        movers = self.scan_after_hours(tickers)
        
        if movers:
            output += "🚨 AFTER-HOURS MOVERS:\n"
            for move in movers:
                emoji = "🟢" if move['ah_change_pct'] > 0 else "🔴"
                output += f"{emoji} {move['ticker']}: ${move['ah_price']:.2f} ({move['ah_change_pct']:+.1f}% AH)\n"
                output += f"   Close: ${move['close']:.2f}\n"
                
                # Check for news
                news = self.check_after_hours_news(move['ticker'])
                if news:
                    output += f"   📰 {len(news)} news items after close\n"
                    for n in news[:2]:
                        output += f"      • {n['headline'][:60]}\n"
                output += "\n"
        else:
            output += "✅ No significant after-hours moves\n\n"
        
        # News on other positions
        output += "📰 AFTER-HOURS NEWS:\n"
        news_count = 0
        for ticker in tickers:
            if ticker in [m['ticker'] for m in movers]:
                continue  # Already covered above
            
            news = self.check_after_hours_news(ticker)
            if news:
                output += f"  {ticker}: {len(news)} items\n"
                for n in news[:1]:
                    output += f"    • {n['headline'][:60]}\n"
                news_count += 1
        
        if news_count == 0:
            output += "  None\n"
        
        output += "\n" + "=" * 60 + "\n"
        
        return output
    
    def log_ah_move(self, ticker: str, move: Dict):
        """Log after-hours move to database"""
        
        conn = database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (timestamp, ticker, alert_type, price, change_pct, catalyst)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            move['timestamp'],
            ticker,
            'AFTER_HOURS_MOVE',
            move['ah_price'],
            move['ah_change_pct'],
            f"AH: {move['ah_change_pct']:+.1f}% from close"
        ))
        
        conn.commit()
        conn.close()


def quick_ah_check(tickers: List[str] = None) -> str:
    """Quick after-hours check on positions"""
    
    if tickers is None:
        tickers = list(config.HOLDINGS.keys())
    
    monitor = AfterHoursMonitor()
    monitor.capture_close_prices(tickers)
    
    return monitor.generate_ah_report(tickers)


# Test
if __name__ == '__main__':
    print("\n🐺 Testing After-Hours Monitor\n")
    
    monitor = AfterHoursMonitor()
    
    # Test with holdings
    holdings = list(config.HOLDINGS.keys())
    
    print("Capturing close prices...")
    monitor.capture_close_prices(holdings)
    
    print("\nChecking for after-hours moves...")
    print(monitor.generate_ah_report(holdings))
