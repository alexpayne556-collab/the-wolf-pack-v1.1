# 🐺 FENRIR V2 - CATALYST CALENDAR
# Track upcoming events that could move stocks

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf
import config

class CatalystCalendar:
    """Track upcoming catalysts"""
    
    def __init__(self):
        self.calendar = {}  # ticker -> list of events
    
    def get_earnings_date(self, ticker: str) -> Optional[str]:
        """Get next earnings date for ticker"""
        
        try:
            stock = yf.Ticker(ticker)
            
            # Try to get earnings calendar
            calendar = stock.calendar
            
            if calendar is not None and 'Earnings Date' in calendar:
                earnings = calendar['Earnings Date']
                
                if isinstance(earnings, str):
                    return earnings
                elif hasattr(earnings, 'iloc'):
                    # It's a Series, get first value
                    return earnings.iloc[0].strftime('%Y-%m-%d') if len(earnings) > 0 else None
            
            return None
            
        except Exception as e:
            return None
    
    def get_ex_dividend_date(self, ticker: str) -> Optional[Dict]:
        """Get ex-dividend date"""
        
        try:
            stock = yf.Ticker(ticker)
            
            info = stock.info
            ex_date = info.get('exDividendDate')
            dividend = info.get('dividendRate')
            
            if ex_date and dividend:
                # Convert timestamp to date
                ex_date_str = datetime.fromtimestamp(ex_date).strftime('%Y-%m-%d')
                
                return {
                    'ex_date': ex_date_str,
                    'dividend': dividend,
                }
            
            return None
            
        except Exception:
            return None
    
    def scan_upcoming_catalysts(self, tickers: List[str], days_ahead: int = 14) -> Dict:
        """Scan for catalysts in next N days"""
        
        print(f"🐺 Scanning {len(tickers)} tickers for upcoming catalysts...")
        
        catalysts = {
            'earnings': [],
            'dividends': [],
        }
        
        cutoff = datetime.now() + timedelta(days=days_ahead)
        
        for ticker in tickers:
            # Earnings
            earnings_date = self.get_earnings_date(ticker)
            if earnings_date:
                try:
                    date_obj = datetime.strptime(earnings_date, '%Y-%m-%d')
                    if date_obj <= cutoff:
                        days_away = (date_obj - datetime.now()).days
                        catalysts['earnings'].append({
                            'ticker': ticker,
                            'date': earnings_date,
                            'days_away': days_away,
                        })
                except:
                    pass
            
            # Dividends
            div_info = self.get_ex_dividend_date(ticker)
            if div_info:
                try:
                    date_obj = datetime.strptime(div_info['ex_date'], '%Y-%m-%d')
                    if date_obj <= cutoff:
                        days_away = (date_obj - datetime.now()).days
                        catalysts['dividends'].append({
                            'ticker': ticker,
                            'date': div_info['ex_date'],
                            'dividend': div_info['dividend'],
                            'days_away': days_away,
                        })
                except:
                    pass
        
        # Sort by date
        catalysts['earnings'].sort(key=lambda x: x['days_away'])
        catalysts['dividends'].sort(key=lambda x: x['days_away'])
        
        return catalysts
    
    def format_calendar(self, catalysts: Dict) -> str:
        """Format catalyst calendar for display"""
        
        output = "\n" + "=" * 60 + "\n"
        output += "🐺 CATALYST CALENDAR - Next 2 Weeks\n"
        output += "=" * 60 + "\n\n"
        
        # Earnings
        if catalysts['earnings']:
            output += "📊 EARNINGS:\n"
            for e in catalysts['earnings']:
                when = "TODAY" if e['days_away'] == 0 else f"{e['days_away']}d away"
                output += f"  {e['ticker']}: {e['date']} ({when})\n"
            output += "\n"
        else:
            output += "📊 EARNINGS: None scheduled\n\n"
        
        # Dividends
        if catalysts['dividends']:
            output += "💰 EX-DIVIDEND:\n"
            for d in catalysts['dividends']:
                when = "TODAY" if d['days_away'] == 0 else f"{d['days_away']}d away"
                output += f"  {d['ticker']}: {d['date']} (${d['dividend']:.2f}) ({when})\n"
            output += "\n"
        else:
            output += "💰 EX-DIVIDEND: None scheduled\n\n"
        
        output += "💡 TIP: Volatility increases around earnings\n"
        output += "=" * 60 + "\n"
        
        return output
    
    def get_this_week_catalysts(self, tickers: List[str]) -> str:
        """Quick: What's happening THIS WEEK?"""
        
        catalysts = self.scan_upcoming_catalysts(tickers, days_ahead=7)
        
        this_week = []
        
        for e in catalysts['earnings']:
            if e['days_away'] <= 7:
                this_week.append(f"📊 {e['ticker']} earnings in {e['days_away']}d")
        
        for d in catalysts['dividends']:
            if d['days_away'] <= 7:
                this_week.append(f"💰 {d['ticker']} ex-div in {d['days_away']}d")
        
        if not this_week:
            return "\n✅ No catalysts this week\n"
        
        output = "\n🐺 THIS WEEK:\n"
        for item in this_week:
            output += f"  {item}\n"
        output += "\n"
        
        return output


def quick_catalyst_check(tickers: List[str] = None) -> str:
    """Quick catalyst check on holdings"""
    
    if tickers is None:
        tickers = list(config.HOLDINGS.keys())
    
    calendar = CatalystCalendar()
    catalysts = calendar.scan_upcoming_catalysts(tickers, days_ahead=14)
    
    return calendar.format_calendar(catalysts)


# Test
if __name__ == '__main__':
    print("\n🐺 Testing Catalyst Calendar\n")
    
    calendar = CatalystCalendar()
    
    # Test on holdings
    holdings = list(config.HOLDINGS.keys())
    
    print("Scanning for catalysts...")
    catalysts = calendar.scan_upcoming_catalysts(holdings, days_ahead=14)
    
    print(calendar.format_calendar(catalysts))
    
    print(calendar.get_this_week_catalysts(holdings))
