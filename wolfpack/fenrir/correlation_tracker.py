# 🐺 FENRIR V2 - CORRELATION TRACKER  
# Find stocks that move together

from typing import Dict, List
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import config

class CorrelationTracker:
    """Track which stocks move together"""
    
    def __init__(self):
        self.correlation_cache = {}
        self.lookback_days = 30
    
    def get_correlation(self, ticker1: str, ticker2: str) -> float:
        """Calculate correlation between two tickers"""
        
        try:
            # Download data for both
            end = datetime.now()
            start = end - timedelta(days=self.lookback_days)
            
            data1 = yf.download(ticker1, start=start, end=end, progress=False)
            data2 = yf.download(ticker2, start=start, end=end, progress=False)
            
            if len(data1) < 10 or len(data2) < 10:
                return 0.0
            
            # Calculate returns
            returns1 = data1['Close'].pct_change().dropna()
            returns2 = data2['Close'].pct_change().dropna()
            
            # Align dates
            aligned = pd.concat([returns1, returns2], axis=1, join='inner')
            aligned.columns = [ticker1, ticker2]
            
            # Correlation
            corr = aligned.corr().iloc[0, 1]
            
            return float(corr) if not pd.isna(corr) else 0.0
            
        except Exception as e:
            print(f"Error calculating correlation: {e}")
            return 0.0
    
    def find_correlated_stocks(self, ticker: str, min_correlation: float = 0.6) -> List[Dict]:
        """Find stocks that move with this ticker"""
        
        print(f"Finding stocks correlated with {ticker}...")
        
        correlated = []
        
        # Check against watchlist
        for other_ticker in config.ALL_WATCHLIST:
            if other_ticker == ticker:
                continue
            
            corr = self.get_correlation(ticker, other_ticker)
            
            if abs(corr) >= min_correlation:
                correlated.append({
                    'ticker': other_ticker,
                    'correlation': corr,
                    'type': 'POSITIVE' if corr > 0 else 'NEGATIVE',
                })
        
        # Sort by absolute correlation
        correlated.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        return correlated
    
    def format_correlation_report(self, ticker: str, correlated: List[Dict]) -> str:
        """Format correlation report"""
        
        if not correlated:
            return f"\n🐺 No strong correlations found for {ticker}\n"
        
        output = "\n" + "=" * 60 + "\n"
        output += f"🐺 STOCKS THAT MOVE WITH {ticker}\n"
        output += "=" * 60 + "\n\n"
        
        output += "POSITIVE CORRELATIONS (move together):\n"
        positive = [c for c in correlated if c['correlation'] > 0]
        for c in positive[:5]:
            output += f"  {c['ticker']}: {c['correlation']:.2f}\n"
        
        output += "\nNEGATIVE CORRELATIONS (move opposite):\n"
        negative = [c for c in correlated if c['correlation'] < 0]
        for c in negative[:5]:
            output += f"  {c['ticker']}: {c['correlation']:.2f}\n"
        
        output += "\n💡 USE THIS:\n"
        output += f"  When {ticker} runs, watch: {', '.join([c['ticker'] for c in positive[:3]])}\n"
        output += f"  When {ticker} drops, these may rise: {', '.join([c['ticker'] for c in negative[:3]])}\n"
        
        output += "\n" + "=" * 60 + "\n"
        
        return output
    
    def get_sector_sympathy_plays(self, ticker: str) -> List[str]:
        """Find sympathy plays in same sector"""
        
        # Find ticker's sector
        ticker_sector = None
        for sector, tickers in config.WATCHLIST.items():
            if ticker in tickers:
                ticker_sector = sector
                break
        
        if not ticker_sector:
            return []
        
        # Return other stocks in same sector
        sympathy = [t for t in config.WATCHLIST[ticker_sector] if t != ticker]
        
        return sympathy


def when_this_moves_watch(ticker: str) -> str:
    """Quick lookup: when ticker moves, what else to watch"""
    
    tracker = CorrelationTracker()
    
    # Get sector plays
    sympathy = tracker.get_sector_sympathy_plays(ticker)
    
    output = f"\n🐺 WHEN {ticker} MOVES, WATCH:\n\n"
    
    if sympathy:
        output += "SECTOR SYMPATHY:\n"
        output += f"  {', '.join(sympathy[:5])}\n\n"
    
    output += "💡 TIP: If catalyst is sector-wide, these move too\n"
    
    return output


# Test
if __name__ == '__main__':
    print("\n🐺 Testing Correlation Tracker\n")
    
    # Quick sector sympathy test
    print(when_this_moves_watch('MU'))
    print(when_this_moves_watch('KTOS'))
    
    # Full correlation analysis (slow - commented out for quick test)
    # tracker = CorrelationTracker()
    # correlated = tracker.find_correlated_stocks('MU', min_correlation=0.6)
    # print(tracker.format_correlation_report('MU', correlated))
