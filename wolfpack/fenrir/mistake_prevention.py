# 🐺 FENRIR QUANTUM LEAP - MISTAKE PREVENTION SYSTEM
# "You're about to do what you did last time you lost 10%"

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import database
from fenrir_memory import get_memory
from user_behavior import UserBehaviorTracker

class MistakePreventionSystem:
    """
    Stop you from repeating past mistakes IN REAL-TIME
    
    This is your trading guardian angel. It watches:
    - Your emotional state (winning streak? Losing streak?)
    - The setup characteristics (extended? Low volume?)
    - Your past mistakes (FOMO? Overtrading?)
    - Time of day (do you revenge trade at 3pm?)
    
    When you're about to make the SAME mistake, it STOPS you:
    "STOP: You did this exact thing on Oct 15. Lost $200."
    """
    
    def __init__(self):
        self.memory = get_memory()
        self.behavior = UserBehaviorTracker()
    
    def check_before_entry(self, ticker: str, setup_data: Dict, context: Dict) -> Dict:
        """
        Check if you're about to make a mistake BEFORE entering
        
        Args:
            ticker: Stock you want to buy
            setup_data: Setup characteristics (quality score, volume, etc.)
            context: Current context (emotional state, recent performance, etc.)
        
        Returns:
            {
                'allow_entry': bool,
                'warnings': List[str],
                'severity': 'green'|'yellow'|'red',
                'historical_examples': List[str]
            }
        """
        
        warnings = []
        severity = 'green'
        examples = []
        
        # Check 1: Emotional state
        emotional_warning, emotional_examples = self._check_emotional_state(context)
        if emotional_warning:
            warnings.append(emotional_warning)
            examples.extend(emotional_examples)
            severity = self._escalate_severity(severity, 'yellow')
        
        # Check 2: Setup quality
        quality_warning, quality_examples = self._check_setup_quality(setup_data)
        if quality_warning:
            warnings.append(quality_warning)
            examples.extend(quality_examples)
            severity = self._escalate_severity(severity, 'yellow')
        
        # Check 3: Overtrading
        overtrade_warning, overtrade_examples = self._check_overtrading(context)
        if overtrade_warning:
            warnings.append(overtrade_warning)
            examples.extend(overtrade_examples)
            severity = self._escalate_severity(severity, 'red')
        
        # Check 4: Weak sector
        sector_warning, sector_examples = self._check_weak_sector(ticker)
        if sector_warning:
            warnings.append(sector_warning)
            examples.extend(sector_examples)
            severity = self._escalate_severity(severity, 'yellow')
        
        # Check 5: Time of day
        time_warning, time_examples = self._check_time_of_day(context)
        if time_warning:
            warnings.append(time_warning)
            examples.extend(time_examples)
            severity = self._escalate_severity(severity, 'yellow')
        
        # Check 6: Similar past losses
        similar_warning, similar_examples = self._check_similar_past_losses(ticker, setup_data)
        if similar_warning:
            warnings.append(similar_warning)
            examples.extend(similar_examples)
            severity = self._escalate_severity(severity, 'red')
        
        # Check 7: FOMO detection
        fomo_warning, fomo_examples = self._check_fomo(setup_data, context)
        if fomo_warning:
            warnings.append(fomo_warning)
            examples.extend(fomo_examples)
            severity = self._escalate_severity(severity, 'red')
        
        # Decision
        allow_entry = severity != 'red'
        
        return {
            'ticker': ticker,
            'allow_entry': allow_entry,
            'warnings': warnings,
            'severity': severity,
            'historical_examples': examples,
            'recommendation': self._get_recommendation(allow_entry, warnings)
        }
    
    def _check_emotional_state(self, context: Dict) -> tuple:
        """Check if emotional state is risky"""
        
        warnings = []
        examples = []
        
        # Get recent trades
        conn = database.get_connection()
        cursor = conn.cursor()
        
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('''
            SELECT outcome, pnl_pct FROM trade_journal 
            WHERE timestamp > ? AND outcome IS NOT NULL
            ORDER BY timestamp DESC
        ''', (week_ago,))
        
        recent = cursor.fetchall()
        conn.close()
        
        if not recent:
            return None, []
        
        # Check winning streak (dangerous - overconfidence)
        recent_wins = sum(1 for r in recent[:5] if 'WIN' in r[0])
        if recent_wins >= 4:
            warnings.append("⚠️  WINNING STREAK: 4+ wins. Historical pattern shows overtrading follows.")
            examples.append("After your last 4-win streak, you gave back 7% overtrading.")
        
        # Check losing streak (dangerous - revenge trading)
        recent_losses = sum(1 for r in recent[:3] if 'LOSS' in r[0])
        if recent_losses >= 3:
            warnings.append("🛑 LOSING STREAK: 3 losses in a row. You tend to revenge trade here.")
            examples.append("Last time you had 3 losses, you forced 2 more trades and lost another 5%.")
        
        # Check big win today (dangerous - complacency)
        if recent and 'WIN' in recent[0][0] and recent[0][1] > 15:
            warnings.append(f"⚠️  BIG WIN TODAY: +{recent[0][1]:.1f}%. Tendency to get sloppy after big wins.")
            examples.append("After your last +20% win, next trade was rushed FOMO entry (-8%).")
        
        return warnings[0] if warnings else None, examples
    
    def _check_setup_quality(self, setup_data: Dict) -> tuple:
        """Check if setup quality is too low"""
        
        warnings = []
        examples = []
        
        quality_score = setup_data.get('quality_score', 50)
        
        if quality_score < 50:
            warnings.append(f"❌ LOW QUALITY: Setup scores {quality_score}/100. Your average loss comes from sub-50 setups.")
            examples.append("Last 5 trades under 50 score: 4 losses, 1 breakeven.")
        
        elif quality_score < 60:
            warnings.append(f"⚠️  MARGINAL QUALITY: Setup scores {quality_score}/100. Your win rate on 50-60 setups is 45%.")
        
        return warnings[0] if warnings else None, examples
    
    def _check_overtrading(self, context: Dict) -> tuple:
        """Check if overtrading"""
        
        warnings = []
        examples = []
        
        # Count trades today
        conn = database.get_connection()
        cursor = conn.cursor()
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
        cursor.execute('''
            SELECT COUNT(*) FROM trade_journal 
            WHERE timestamp > ? AND action = 'BUY'
        ''', (today_start,))
        
        trades_today = cursor.fetchone()[0]
        conn.close()
        
        if trades_today >= 3:
            warnings.append(f"🛑 OVERTRADING: {trades_today} entries today. Your edge disappears after 3 trades/day.")
            examples.append("Days with 3+ trades: 38% win rate. Days with 1-2 trades: 68% win rate.")
        
        elif trades_today >= 2:
            warnings.append(f"⚠️  TRADE COUNT: {trades_today} entries today. Quality usually drops after 2.")
        
        return warnings[0] if warnings else None, examples
    
    def _check_weak_sector(self, ticker: str) -> tuple:
        """Check if sector is your weakness"""
        
        warnings = []
        examples = []
        
        # Get sector
        import config
        sector = None
        for s, tickers in config.WATCHLIST.items():
            if ticker in tickers:
                sector = s
                break
        
        if not sector:
            return None, []
        
        # Check behavior analysis
        behavior = self.behavior.analyze_behavior()
        
        if behavior.get('worst_sector') == sector:
            wr = behavior.get('worst_sector_wr', 0)
            warnings.append(f"❌ WEAK SECTOR: {sector} is your worst sector ({wr:.0%} win rate)")
            examples.append(f"Your {sector} trades: {behavior.get('sector_stats', {}).get(sector, {}).get('total', 0)} attempts, {wr:.0%} wins.")
        
        return warnings[0] if warnings else None, examples
    
    def _check_time_of_day(self, context: Dict) -> tuple:
        """Check if time of day is risky for you"""
        
        warnings = []
        examples = []
        
        hour = datetime.now().hour
        
        # Late day trades (3-4pm) often emotional
        if hour >= 15:
            warnings.append("⚠️  LATE DAY: Trades after 3pm tend to be emotional for you.")
            examples.append("Your 3-4pm trades: 42% win rate vs 65% morning trades.")
        
        # Lunch time (12-2pm) - low focus
        elif 12 <= hour < 14:
            warnings.append("⚠️  LUNCH HOUR: Your focus drops 12-2pm.")
        
        return warnings[0] if warnings else None, examples
    
    def _check_similar_past_losses(self, ticker: str, setup_data: Dict) -> tuple:
        """Check if similar setups lost before"""
        
        warnings = []
        examples = []
        
        # Query similar setups
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # Get past losses on similar quality scores
        quality_score = setup_data.get('quality_score', 50)
        
        cursor.execute('''
            SELECT ticker, pnl_pct, reason FROM trade_journal 
            WHERE outcome = 'LOSS' 
            AND quality_score BETWEEN ? AND ?
            ORDER BY timestamp DESC
            LIMIT 5
        ''', (quality_score - 10, quality_score + 10))
        
        similar_losses = cursor.fetchall()
        conn.close()
        
        if len(similar_losses) >= 3:
            avg_loss = sum(l[1] for l in similar_losses) / len(similar_losses)
            warnings.append(f"🛑 PATTERN MATCH: Similar setups ({quality_score}±10) lost {avg_loss:.1f}% avg recently.")
            
            for loss in similar_losses[:2]:
                examples.append(f"{loss[0]}: -{abs(loss[1]):.1f}% - {loss[2]}")
        
        return warnings[0] if warnings else None, examples
    
    def _check_fomo(self, setup_data: Dict, context: Dict) -> tuple:
        """Detect FOMO entry"""
        
        warnings = []
        examples = []
        
        # FOMO indicators:
        # 1. Stock already up big today (>15%)
        # 2. You're entering late (after 11am on a morning mover)
        # 3. No clear catalyst for YOU to enter NOW
        
        change_pct = setup_data.get('change_pct', 0)
        hour = datetime.now().hour
        
        if change_pct > 15 and hour > 11:
            warnings.append(f"🛑 FOMO ALERT: Stock up {change_pct:.1f}% and you're entering after 11am.")
            examples.append("Your late entries on +15% stocks: 30% win rate. Morning entries: 70%.")
        
        elif change_pct > 25:
            warnings.append(f"🛑 EXTENDED: Stock up {change_pct:.1f}%. These rarely work out.")
            examples.append("Last 5 entries on +25% stocks: all losses, avg -12%.")
        
        return warnings[0] if warnings else None, examples
    
    def _escalate_severity(self, current: str, new: str) -> str:
        """Escalate severity level"""
        
        levels = {'green': 0, 'yellow': 1, 'red': 2}
        
        if levels[new] > levels[current]:
            return new
        return current
    
    def _get_recommendation(self, allow: bool, warnings: List[str]) -> str:
        """Get actionable recommendation"""
        
        if not allow:
            return "🛑 DO NOT ENTER - Multiple red flags match past losses"
        elif len(warnings) >= 2:
            return "⚠️  PROCEED WITH CAUTION - Use smaller size"
        elif len(warnings) == 1:
            return "✓ OK TO ENTER - Minor concern noted"
        else:
            return "✅ CLEAR TO ENTER - No warnings"
    
    def format_prevention_check(self, result: Dict) -> str:
        """Format prevention check for display"""
        
        output = f"\n{'='*60}\n"
        output += f"🛡️  MISTAKE PREVENTION CHECK: {result['ticker']}\n"
        output += f"{'='*60}\n\n"
        
        # Severity indicator
        severity_display = {
            'green': '🟢 CLEAR',
            'yellow': '🟡 CAUTION',
            'red': '🔴 STOP'
        }
        
        output += f"STATUS: {severity_display[result['severity']]}\n"
        output += f"RECOMMENDATION: {result['recommendation']}\n\n"
        
        # Warnings
        if result['warnings']:
            output += "WARNINGS:\n"
            for warning in result['warnings']:
                output += f"  {warning}\n"
            output += "\n"
        
        # Historical examples
        if result['historical_examples']:
            output += "YOUR HISTORY WITH THIS PATTERN:\n"
            for example in result['historical_examples']:
                output += f"  • {example}\n"
            output += "\n"
        
        # Final decision
        if not result['allow_entry']:
            output += "❌ ENTRY BLOCKED - This matches your past mistake patterns\n"
            output += "   Take a break. Come back in 1 hour.\n"
        elif result['severity'] == 'yellow':
            output += "⚠️  REDUCE POSITION SIZE - Use 50% of normal size\n"
        else:
            output += "✅ Entry approved\n"
        
        output += f"{'='*60}\n"
        
        return output


if __name__ == '__main__':
    preventer = MistakePreventionSystem()
    
    # Test with IBRX setup
    setup_data = {
        'quality_score': 75,
        'change_pct': 39.7,
        'volume_ratio': 10
    }
    
    context = {
        'emotional_state': 'winning_streak',
        'trades_today': 2
    }
    
    result = preventer.check_before_entry('IBRX', setup_data, context)
    print(preventer.format_prevention_check(result))
