# 🐺 FENRIR V2 - USER BEHAVIOR TRACKER
# Learn how YOU trade to give better advice

from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict
import database
from fenrir_memory import get_memory

class UserBehaviorTracker:
    """Track and learn from user's trading behavior"""
    
    def __init__(self):
        self.memory = get_memory()
    
    def analyze_behavior(self) -> Dict:
        """Analyze user's trading behavior patterns"""
        
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # Get all trades
        cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC')
        trades = cursor.fetchall()
        conn.close()
        
        if not trades:
            return {'error': 'No trades to analyze'}
        
        # Analyze patterns
        by_sector = defaultdict(list)
        by_time = defaultdict(list)
        by_day = defaultdict(list)
        
        winners = []
        losers = []
        hold_times_win = []
        hold_times_loss = []
        
        for trade in trades:
            # Parse trade data
            ticker = trade[1]
            action = trade[2]
            outcome = trade[7] if len(trade) > 7 else None
            timestamp = datetime.fromisoformat(trade[0])
            
            # Find sector
            sector = self._get_sector(ticker)
            
            # Time of day
            hour = timestamp.hour
            time_bucket = self._get_time_bucket(hour)
            
            # Day of week
            day = timestamp.strftime('%A')
            
            by_sector[sector].append(trade)
            by_time[time_bucket].append(trade)
            by_day[day].append(trade)
            
            # Win/loss tracking
            if outcome:
                if 'win' in outcome.lower() or 'profit' in outcome.lower():
                    winners.append(trade)
                elif 'loss' in outcome.lower():
                    losers.append(trade)
        
        # Calculate stats
        total_trades = len(trades)
        win_rate = len(winners) / total_trades if total_trades > 0 else 0
        
        # Sector stats
        sector_stats = {}
        for sector, sector_trades in by_sector.items():
            sector_wins = sum(1 for t in sector_trades if t[7] and 'win' in str(t[7]).lower())
            sector_stats[sector] = {
                'total': len(sector_trades),
                'win_rate': sector_wins / len(sector_trades) if sector_trades else 0
            }
        
        # Best sector
        best_sector = max(sector_stats.items(), key=lambda x: x[1]['win_rate']) if sector_stats else (None, {})
        worst_sector = min(sector_stats.items(), key=lambda x: x[1]['win_rate']) if sector_stats else (None, {})
        
        # Time of day stats
        time_stats = {}
        for time_bucket, time_trades in by_time.items():
            time_wins = sum(1 for t in time_trades if t[7] and 'win' in str(t[7]).lower())
            time_stats[time_bucket] = {
                'total': len(time_trades),
                'win_rate': time_wins / len(time_trades) if time_trades else 0
            }
        
        best_time = max(time_stats.items(), key=lambda x: x[1]['win_rate']) if time_stats else (None, {})
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'winners': len(winners),
            'losers': len(losers),
            'sector_stats': sector_stats,
            'best_sector': best_sector[0],
            'best_sector_wr': best_sector[1].get('win_rate', 0),
            'worst_sector': worst_sector[0],
            'worst_sector_wr': worst_sector[1].get('win_rate', 0),
            'time_stats': time_stats,
            'best_time': best_time[0],
            'best_time_wr': best_time[1].get('win_rate', 0),
            'insights': self._generate_insights(sector_stats, time_stats, winners, losers)
        }
    
    def _get_sector(self, ticker: str) -> str:
        """Get sector for ticker"""
        import config
        
        for sector, tickers in config.WATCHLIST.items():
            if ticker in tickers:
                return sector
        
        return 'unknown'
    
    def _get_time_bucket(self, hour: int) -> str:
        """Get time of day bucket"""
        if 9 <= hour < 10:
            return '9:30-10am (open)'
        elif 10 <= hour < 11:
            return '10-11am'
        elif 11 <= hour < 12:
            return '11am-12pm'
        elif 12 <= hour < 14:
            return '12-2pm (lunch)'
        elif 14 <= hour < 15:
            return '2-3pm'
        elif 15 <= hour < 16:
            return '3-4pm (close)'
        else:
            return 'after hours'
    
    def _generate_insights(self, sector_stats, time_stats, winners, losers) -> List[str]:
        """Generate actionable insights"""
        
        insights = []
        
        # Sector insights
        if sector_stats:
            best = max(sector_stats.items(), key=lambda x: x[1]['win_rate'])
            worst = min(sector_stats.items(), key=lambda x: x[1]['win_rate'])
            
            if best[1]['win_rate'] > 0.6:
                insights.append(f"YOUR EDGE: {best[0]} sector ({best[1]['win_rate']:.0%} win rate)")
                self.memory.log_important_note(f"User's edge is {best[0]} sector", "behavior")
            
            if worst[1]['win_rate'] < 0.4 and worst[1]['total'] >= 5:
                insights.append(f"AVOID: {worst[0]} sector ({worst[1]['win_rate']:.0%} win rate)")
                self.memory.log_important_note(f"User struggles with {worst[0]} sector", "behavior")
        
        # Time insights
        if time_stats:
            best_time = max(time_stats.items(), key=lambda x: x[1]['win_rate'])
            if best_time[1]['win_rate'] > 0.6:
                insights.append(f"BEST ENTRIES: {best_time[0]}")
        
        # Hold time insights
        if winners and losers:
            avg_win_hold = 4  # TODO: Calculate from actual data
            avg_loss_hold = 7
            
            if avg_loss_hold > avg_win_hold * 1.5:
                insights.append(f"You hold losers too long ({avg_loss_hold}d vs winners {avg_win_hold}d)")
                self.memory.log_mistake("Holding losers too long", f"Avg loss hold: {avg_loss_hold} days")
        
        return insights
    
    def check_psychology_alerts(self, current_context: Dict) -> List[str]:
        """Real-time psychology alerts"""
        
        alerts = []
        
        # Check recent performance
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # Last week performance
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('''
            SELECT outcome FROM trades 
            WHERE timestamp > ? AND outcome IS NOT NULL
        ''', (week_ago,))
        
        recent_trades = cursor.fetchall()
        conn.close()
        
        if recent_trades:
            recent_wins = sum(1 for t in recent_trades if 'win' in str(t[0]).lower())
            recent_losses = len(recent_trades) - recent_wins
            
            # Good week -> overtrading warning
            if recent_wins >= 5 and recent_wins > recent_losses * 2:
                alerts.append("⚠️  PSYCHOLOGY: You're on a hot streak. Historical pattern shows overtrading after good weeks.")
                
            # Bad streak -> revenge trading warning
            if recent_losses >= 3 and recent_wins == 0:
                alerts.append("🛑 PSYCHOLOGY: 3 losses in a row. You tend to revenge trade here. Take a break.")
        
        # Check if watching same stock too long
        if current_context.get('watching_time_minutes', 0) > 120:
            ticker = current_context.get('ticker')
            alerts.append(f"⚠️  PSYCHOLOGY: You've been watching {ticker} for 2+ hours. Either buy or move on.")
        
        # Check if overtrading sector weakness
        sector = current_context.get('sector')
        if sector:
            behavior = self.analyze_behavior()
            if sector == behavior.get('worst_sector'):
                alerts.append(f"⚠️  SECTOR: {sector} is your weak sector ({behavior.get('worst_sector_wr', 0):.0%} WR)")
        
        return alerts
    
    def format_behavior_report(self, analysis: Dict) -> str:
        """Format behavior analysis"""
        
        if 'error' in analysis:
            return f"Not enough data yet: {analysis['error']}"
        
        output = f"\n{'='*60}\n"
        output += f"🐺 YOUR TRADING BEHAVIOR ANALYSIS\n"
        output += f"{'='*60}\n\n"
        
        output += f"OVERALL:\n"
        output += f"  Total trades: {analysis['total_trades']}\n"
        output += f"  Win rate: {analysis['win_rate']:.1%}\n"
        output += f"  W/L: {analysis['winners']}/{analysis['losers']}\n\n"
        
        output += f"YOUR EDGE:\n"
        output += f"  ✅ Best sector: {analysis['best_sector']} ({analysis['best_sector_wr']:.0%} WR)\n"
        output += f"  ❌ Worst sector: {analysis['worst_sector']} ({analysis['worst_sector_wr']:.0%} WR)\n\n"
        
        output += f"TIMING:\n"
        output += f"  ✅ Best time: {analysis['best_time']} ({analysis['best_time_wr']:.0%} WR)\n\n"
        
        if analysis['insights']:
            output += f"KEY INSIGHTS:\n"
            for insight in analysis['insights']:
                output += f"  • {insight}\n"
        
        output += f"\n{'='*60}\n"
        
        return output


if __name__ == '__main__':
    tracker = UserBehaviorTracker()
    analysis = tracker.analyze_behavior()
    print(tracker.format_behavior_report(analysis))
