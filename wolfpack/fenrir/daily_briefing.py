# 🐺 FENRIR V2 - DAILY BRIEFING
# Morning summary - what you need to know before open

from datetime import datetime, time
from typing import Dict, List
import config
from news_fetcher import get_company_news
from premarket_tracker import PremarketTracker
from risk_manager import RiskManager, format_risk_report
import database

class DailyBriefing:
    """Generate morning briefing"""
    
    def __init__(self):
        self.briefing_time = time(6, 0)  # 6:00 AM ET
        self.pm_tracker = PremarketTracker()
        self.risk_mgr = RiskManager()
    
    def generate_briefing(self) -> str:
        """Generate complete morning briefing"""
        
        now = datetime.now()
        
        output = "\n" + "=" * 60 + "\n"
        output += f"🐺 FENRIR DAILY BRIEFING - {now.strftime('%A, %B %d, %Y')}\n"
        output += f"Generated at {now.strftime('%I:%M %p ET')}\n"
        output += "=" * 60 + "\n\n"
        
        # Section 1: Pre-market gaps
        output += "📊 PRE-MARKET GAPS:\n"
        output += self._check_premarket_gaps()
        output += "\n"
        
        # Section 2: Overnight news
        output += "📰 OVERNIGHT NEWS:\n"
        output += self._check_overnight_news()
        output += "\n"
        
        # Section 3: Earnings/catalysts today
        output += "📅 TODAY'S CATALYSTS:\n"
        output += self._check_todays_catalysts()
        output += "\n"
        
        # Section 4: Risk status
        output += "⚠️  RISK STATUS:\n"
        output += self._check_risk_status()
        output += "\n"
        
        # Section 5: Day trades available
        output += "🎯 TRADING CAPACITY:\n"
        output += self._check_day_trades()
        output += "\n"
        
        # Section 6: Action items
        output += "✅ FOCUS TODAY:\n"
        output += self._generate_action_items()
        
        output += "\n" + "=" * 60 + "\n"
        output += "🐺 Good hunting, boss.\n"
        output += "=" * 60 + "\n"
        
        return output
    
    def _check_premarket_gaps(self) -> str:
        """Check for pre-market gaps"""
        
        holdings = list(config.HOLDINGS.keys())
        gaps = self.pm_tracker.scan_for_gaps(holdings, min_gap_pct=2.0)
        
        if not gaps:
            return "  No significant gaps in holdings\n"
        
        output = ""
        for gap in gaps:
            emoji = "🟢" if gap['gap_pct'] > 0 else "🔴"
            output += f"  {emoji} {gap['ticker']}: ${gap['premarket_price']:.2f} ({gap['gap_pct']:+.1f}%)\n"
        
        return output
    
    def _check_overnight_news(self) -> str:
        """Check for news on positions"""
        
        holdings = list(config.HOLDINGS.keys())
        news_found = False
        output = ""
        
        for ticker in holdings:
            news = get_company_news(ticker, days=1)
            
            # Filter to last 12 hours
            recent = [n for n in news if self._is_recent(n.get('datetime', ''))]
            
            if recent:
                news_found = True
                output += f"  {ticker}: {len(recent)} items\n"
                for n in recent[:2]:
                    output += f"    • {n['headline'][:55]}\n"
        
        if not news_found:
            output = "  No major news overnight\n"
        
        return output
    
    def _check_todays_catalysts(self) -> str:
        """Check for earnings or events today"""
        
        # TODO: Pull from earnings calendar
        # For now, placeholder
        return "  No known earnings today\n  (Earnings calendar coming soon)\n"
    
    def _check_risk_status(self) -> str:
        """Quick risk check"""
        
        warnings = self.risk_mgr.check_risks(config.HOLDINGS)
        
        if not warnings:
            return "  ✅ All clear - no risk warnings\n"
        
        output = ""
        for w in warnings:
            output += f"  {w}\n"
        
        return output
    
    def _check_day_trades(self) -> str:
        """Check day trade availability"""
        
        used = self.risk_mgr.get_day_trades_used()
        remaining = self.risk_mgr.pdt_limit - used
        
        if remaining == 0:
            return "  🚨 NO DAY TRADES LEFT - swing only\n"
        elif remaining == 1:
            return f"  ⚠️  {remaining} day trade left - use wisely\n"
        else:
            return f"  ✅ {remaining} day trades available\n"
    
    def _generate_action_items(self) -> str:
        """What to focus on today"""
        
        items = []
        
        # Check for gappers
        gaps = self.pm_tracker.scan_for_gaps(list(config.HOLDINGS.keys()), min_gap_pct=3.0)
        if gaps:
            for gap in gaps[:2]:
                items.append(f"Watch {gap['ticker']} - gapped {gap['gap_pct']:+.1f}%")
        
        # Check for bleeding positions
        # TODO: Query yesterday's closes and compare
        
        # Default items
        if not items:
            items = [
                "Monitor positions for 5%+ moves",
                "Watch for sector momentum",
                "Check volume at 10 AM for direction",
            ]
        
        output = ""
        for i, item in enumerate(items, 1):
            output += f"  {i}. {item}\n"
        
        return output
    
    def _is_recent(self, datetime_str: str, hours: int = 12) -> bool:
        """Check if datetime is within last N hours"""
        
        if not datetime_str:
            return False
        
        try:
            news_time = datetime.fromisoformat(datetime_str)
            cutoff = datetime.now() - timedelta(hours=hours)
            return news_time >= cutoff
        except:
            return False
    
    def save_briefing(self, briefing: str):
        """Save briefing to file"""
        
        filename = f"briefings/briefing_{datetime.now().strftime('%Y%m%d')}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(briefing)
            print(f"💾 Briefing saved to {filename}")
        except:
            pass  # OK if fails


from datetime import timedelta

def morning_briefing() -> str:
    """Quick function to generate briefing"""
    
    briefing = DailyBriefing()
    return briefing.generate_briefing()


# Test
if __name__ == '__main__':
    print("\n🐺 Generating Daily Briefing\n")
    
    print(morning_briefing())
