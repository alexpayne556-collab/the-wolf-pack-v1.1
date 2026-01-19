# 🐺 FENRIR V2 - END OF DAY REPORT
# Auto-generate EOD summary at market close

from datetime import datetime, time
from typing import Dict, List
import config
from market_data import get_stock_data
from news_fetcher import get_company_news
import database

class EODReport:
    """Generate end of day report"""
    
    def __init__(self):
        self.market_close = time(16, 0)  # 4:00 PM ET
    
    def generate_report(self) -> str:
        """Generate complete EOD report"""
        
        now = datetime.now()
        
        output = "\n" + "=" * 60 + "\n"
        output += f"🐺 END OF DAY REPORT - {now.strftime('%A, %B %d, %Y')}\n"
        output += f"Market Close: {now.strftime('%I:%M %p ET')}\n"
        output += "=" * 60 + "\n\n"
        
        # Section 1: Today's P/L
        output += "💰 TODAY'S P/L:\n"
        output += self._calculate_daily_pnl()
        output += "\n"
        
        # Section 2: Movers and why
        output += "📊 WHAT MOVED:\n"
        output += self._summarize_movers()
        output += "\n"
        
        # Section 3: Character changes
        output += "⚡ CHARACTER CHANGES:\n"
        output += self._check_character_changes()
        output += "\n"
        
        # Section 4: After-hours setup
        output += "🌙 AFTER-HOURS WATCH:\n"
        output += self._ah_preview()
        output += "\n"
        
        # Section 5: Tomorrow prep
        output += "🔮 TOMORROW:\n"
        output += self._tomorrow_prep()
        
        output += "\n" + "=" * 60 + "\n"
        output += "🐺 See you tomorrow, boss.\n"
        output += "=" * 60 + "\n"
        
        return output
    
    def _calculate_daily_pnl(self) -> str:
        """Calculate today's P/L per position"""
        
        output = ""
        total_daily_pnl = 0
        
        winners = []
        losers = []
        
        for ticker, holding in config.HOLDINGS.items():
            data = get_stock_data(ticker)
            
            if not data:
                continue
            
            # Today's move on position value
            position_value = holding['shares'] * data['price']
            daily_pnl = position_value * (data['change_pct'] / 100)
            total_daily_pnl += daily_pnl
            
            item = {
                'ticker': ticker,
                'change_pct': data['change_pct'],
                'daily_pnl': daily_pnl,
                'price': data['price'],
            }
            
            if daily_pnl > 0:
                winners.append(item)
            else:
                losers.append(item)
        
        # Sort
        winners.sort(key=lambda x: x['daily_pnl'], reverse=True)
        losers.sort(key=lambda x: x['daily_pnl'])
        
        # Winners
        if winners:
            output += "  🟢 WINNERS:\n"
            for w in winners:
                output += f"    {w['ticker']}: {w['change_pct']:+.1f}% (${w['daily_pnl']:+.2f})\n"
        
        # Losers
        if losers:
            output += "  🔴 LOSERS:\n"
            for l in losers:
                output += f"    {l['ticker']}: {l['change_pct']:+.1f}% (${l['daily_pnl']:+.2f})\n"
        
        output += f"\n  TOTAL TODAY: ${total_daily_pnl:+.2f}\n"
        
        return output
    
    def _summarize_movers(self) -> str:
        """What moved and why"""
        
        output = ""
        
        for ticker in config.HOLDINGS.keys():
            data = get_stock_data(ticker)
            
            if not data or abs(data['change_pct']) < 3:
                continue  # Skip small moves
            
            # Get news
            news = get_company_news(ticker, days=1)
            
            emoji = "🟢" if data['change_pct'] > 0 else "🔴"
            output += f"  {emoji} {ticker}: {data['change_pct']:+.1f}%\n"
            
            if news:
                output += f"     📰 {news[0]['headline'][:50]}\n"
            else:
                output += f"     (No news - sector/momentum?)\n"
        
        if not output:
            output = "  No major moves today (< 3%)\n"
        
        return output
    
    def _check_character_changes(self) -> str:
        """Detect character changes"""
        
        # TODO: Compare to state tracker
        # For now, placeholder
        
        output = "  None detected\n"
        output += "  (Full state tracking coming soon)\n"
        
        return output
    
    def _ah_preview(self) -> str:
        """What to watch after hours"""
        
        output = ""
        
        # Check for earnings releases
        output += "  Earnings after close: Check manually\n"
        output += "  (Earnings calendar integration coming)\n\n"
        
        # Movers to watch AH
        output += "  Watch for AH movement on:\n"
        for ticker in config.HOLDINGS.keys():
            data = get_stock_data(ticker)
            if data and abs(data['change_pct']) >= 5:
                output += f"    {ticker} (moved {data['change_pct']:+.1f}% today)\n"
        
        return output
    
    def _tomorrow_prep(self) -> str:
        """Tomorrow setup"""
        
        output = ""
        
        output += "  Pre-market scan starts 6 AM\n"
        output += "  Check gaps before open\n"
        output += "  Daily briefing at 6 AM\n"
        
        return output
    
    def save_report(self, report: str):
        """Save EOD report to file"""
        
        filename = f"reports/eod_{datetime.now().strftime('%Y%m%d')}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(report)
            print(f"💾 Report saved to {filename}")
        except:
            pass


def generate_eod() -> str:
    """Quick function to generate EOD"""
    
    report = EODReport()
    return report.generate_report()


# Test
if __name__ == '__main__':
    print("\n🐺 Generating End of Day Report\n")
    
    print(generate_eod())
