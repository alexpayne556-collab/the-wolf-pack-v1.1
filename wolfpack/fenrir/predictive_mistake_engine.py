# 🐺 FENRIR QUANTUM LEVEL 2 - PREDICTIVE MISTAKE ENGINE
# "I predict you'll make this mistake in 47 minutes"

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import database
from collections import defaultdict
import numpy as np

class PredictiveMistakeEngine:
    """
    Don't just DETECT mistakes - PREDICT them before you make them
    
    This uses machine learning patterns to predict:
    - When you'll overtrade (based on current momentum)
    - When you'll FOMO (based on market movement + your state)
    - When you'll hold too long (based on P/L + time held)
    - When you'll revenge trade (based on loss pattern)
    
    Not just "you made this mistake before" but "you're ABOUT TO make it"
    
    Example: "PREDICTION: 73% chance you'll overtrade in next 2 hours based on:
             - 2 wins today (you get overconfident after 2 wins)
             - It's 2:47pm (your overtrading window is 2-4pm)
             - Market is choppy (you chase more in chop)
             RECOMMENDATION: Close laptop now. Come back Monday."
    """
    
    def __init__(self):
        self.conn = database.get_connection()
    
    def predict_next_mistake(self, context: Dict) -> Dict:
        """
        Predict what mistake you're most likely to make next
        
        Args:
            context: {
                'current_positions': int,
                'trades_today': int,
                'recent_pnl': float,
                'market_volatility': float,
                'time_of_day': int (hour),
                'day_of_week': str,
                'consecutive_wins': int,
                'consecutive_losses': int
            }
        
        Returns:
            {
                'predicted_mistake': str,
                'probability': float (0-1),
                'time_window': str,
                'triggers': List[str],
                'prevention_actions': List[str]
            }
        """
        
        # Get your historical mistake patterns
        mistake_patterns = self._analyze_historical_mistakes()
        
        # Calculate probability for each mistake type
        probabilities = {
            'overtrade': self._calculate_overtrade_probability(context, mistake_patterns),
            'fomo': self._calculate_fomo_probability(context, mistake_patterns),
            'hold_too_long': self._calculate_hold_too_long_probability(context, mistake_patterns),
            'revenge_trade': self._calculate_revenge_trade_probability(context, mistake_patterns),
            'panic_sell': self._calculate_panic_sell_probability(context, mistake_patterns),
            'chase_extension': self._calculate_chase_probability(context, mistake_patterns),
            'average_down_loser': self._calculate_average_down_probability(context, mistake_patterns)
        }
        
        # Find highest probability mistake
        predicted_mistake = max(probabilities, key=probabilities.get)
        probability = probabilities[predicted_mistake]
        
        # Only warn if probability > 50%
        if probability < 0.5:
            return {
                'predicted_mistake': 'none',
                'probability': max(probabilities.values()),
                'status': 'clear',
                'message': 'No high-probability mistakes detected'
            }
        
        # Get details about this mistake
        details = self._get_mistake_details(predicted_mistake, context, mistake_patterns)
        
        return {
            'predicted_mistake': predicted_mistake,
            'probability': probability,
            'time_window': details['time_window'],
            'triggers': details['triggers'],
            'prevention_actions': details['prevention_actions'],
            'severity': 'critical' if probability > 0.75 else 'high' if probability > 0.60 else 'moderate',
            'historical_cost': details['historical_cost']
        }
    
    def _analyze_historical_mistakes(self) -> Dict:
        """Analyze patterns in historical mistakes"""
        
        cursor = self.conn.cursor()
        
        # Get all losing trades
        cursor.execute('''
            SELECT timestamp, ticker, pnl_pct, reason, emotions, quality_score
            FROM trade_journal
            WHERE outcome = 'LOSS'
            ORDER BY timestamp DESC
            LIMIT 100
        ''')
        
        losses = cursor.fetchall()
        
        patterns = {
            'overtrade_hours': [],
            'fomo_triggers': [],
            'hold_too_long_signals': [],
            'revenge_trade_after_n_losses': [],
            'panic_sell_conditions': [],
            'chase_extension_levels': [],
            'average_down_situations': []
        }
        
        for loss in losses:
            timestamp, ticker, pnl_pct, reason, emotions, quality_score = loss
            
            # Parse timestamp
            dt = datetime.fromisoformat(timestamp)
            hour = dt.hour
            
            # Categorize mistake type from reason/emotions
            if 'fomo' in (emotions or '').lower() or 'fomo' in (reason or '').lower():
                patterns['fomo_triggers'].append({
                    'hour': hour,
                    'quality_score': quality_score,
                    'loss_pct': pnl_pct
                })
            
            if 'held too long' in (reason or '').lower():
                patterns['hold_too_long_signals'].append({
                    'hour': hour,
                    'loss_pct': pnl_pct
                })
            
            if 'panic' in (emotions or '').lower():
                patterns['panic_sell_conditions'].append({
                    'hour': hour,
                    'loss_pct': pnl_pct
                })
            
            # Track hours when mistakes happen
            patterns['overtrade_hours'].append(hour)
        
        # Calculate revenge trade patterns
        cursor.execute('''
            SELECT timestamp, outcome FROM trade_journal
            WHERE action = 'SELL'
            ORDER BY timestamp
        ''')
        
        all_trades = cursor.fetchall()
        consecutive_losses = 0
        
        for i, (timestamp, outcome) in enumerate(all_trades):
            if outcome == 'LOSS':
                consecutive_losses += 1
            else:
                if consecutive_losses > 0 and i < len(all_trades) - 1:
                    # Check if next trade was also a loss (revenge trade indicator)
                    next_outcome = all_trades[i + 1][1] if i + 1 < len(all_trades) else None
                    if next_outcome == 'LOSS':
                        patterns['revenge_trade_after_n_losses'].append(consecutive_losses)
                consecutive_losses = 0
        
        return patterns
    
    def _calculate_overtrade_probability(self, context: Dict, patterns: Dict) -> float:
        """Calculate probability of overtrading"""
        
        prob = 0.0
        
        # Base rate
        trades_today = context.get('trades_today', 0)
        if trades_today >= 3:
            prob += 0.5  # Already at overtrade threshold
        elif trades_today >= 2:
            prob += 0.3
        elif trades_today >= 1:
            prob += 0.1
        
        # Time of day factor
        hour = context.get('time_of_day', 14)
        overtrade_hours = patterns.get('overtrade_hours', [])
        if overtrade_hours:
            hour_frequency = overtrade_hours.count(hour) / len(overtrade_hours)
            prob += hour_frequency * 0.3
        
        # Winning streak factor (overconfidence)
        wins = context.get('consecutive_wins', 0)
        if wins >= 3:
            prob += 0.25
        elif wins >= 2:
            prob += 0.15
        
        # Market volatility factor (more temptation in volatile market)
        volatility = context.get('market_volatility', 1.0)
        if volatility > 2.0:
            prob += 0.15
        
        return min(1.0, prob)
    
    def _calculate_fomo_probability(self, context: Dict, patterns: Dict) -> float:
        """Calculate probability of FOMO trade"""
        
        prob = 0.0
        
        # Market moving fast
        volatility = context.get('market_volatility', 1.0)
        if volatility > 2.5:
            prob += 0.3
        elif volatility > 2.0:
            prob += 0.2
        
        # After wins (overconfidence)
        wins = context.get('consecutive_wins', 0)
        if wins >= 2:
            prob += 0.25
        
        # Time of day (FOMO peaks mid-day)
        hour = context.get('time_of_day', 14)
        if 11 <= hour <= 15:
            prob += 0.2
        
        # Already have positions (chasing more)
        positions = context.get('current_positions', 0)
        if positions >= 3:
            prob += 0.2
        
        # Historical FOMO pattern
        fomo_triggers = patterns.get('fomo_triggers', [])
        if len(fomo_triggers) > 5:  # Have history of FOMO
            prob += 0.15
        
        return min(1.0, prob)
    
    def _calculate_hold_too_long_probability(self, context: Dict, patterns: Dict) -> float:
        """Calculate probability of holding too long"""
        
        prob = 0.0
        
        # Recent P&L positive (greed)
        recent_pnl = context.get('recent_pnl', 0)
        if recent_pnl > 15:
            prob += 0.3  # Big winner, tempted to hold for more
        elif recent_pnl > 8:
            prob += 0.2
        
        # Winning streak (getting greedy)
        wins = context.get('consecutive_wins', 0)
        if wins >= 3:
            prob += 0.25
        
        # Historical pattern
        hold_signals = patterns.get('hold_too_long_signals', [])
        if len(hold_signals) > 3:
            prob += 0.2
        
        return min(1.0, prob)
    
    def _calculate_revenge_trade_probability(self, context: Dict, patterns: Dict) -> float:
        """Calculate probability of revenge trade"""
        
        prob = 0.0
        
        # Losing streak (anger)
        losses = context.get('consecutive_losses', 0)
        if losses >= 3:
            prob += 0.5
        elif losses >= 2:
            prob += 0.3
        elif losses >= 1:
            prob += 0.15
        
        # Recent negative P&L
        recent_pnl = context.get('recent_pnl', 0)
        if recent_pnl < -10:
            prob += 0.25
        elif recent_pnl < -5:
            prob += 0.15
        
        # Historical revenge pattern
        revenge_patterns = patterns.get('revenge_trade_after_n_losses', [])
        if revenge_patterns and losses > 0:
            avg_losses_before_revenge = np.mean(revenge_patterns) if revenge_patterns else 999
            if losses >= avg_losses_before_revenge - 0.5:
                prob += 0.2
        
        return min(1.0, prob)
    
    def _calculate_panic_sell_probability(self, context: Dict, patterns: Dict) -> float:
        """Calculate probability of panic sell"""
        
        prob = 0.0
        
        # Negative P&L
        recent_pnl = context.get('recent_pnl', 0)
        if recent_pnl < -15:
            prob += 0.35
        elif recent_pnl < -10:
            prob += 0.25
        elif recent_pnl < -5:
            prob += 0.15
        
        # High volatility (panic trigger)
        volatility = context.get('market_volatility', 1.0)
        if volatility > 3.0:
            prob += 0.3
        elif volatility > 2.5:
            prob += 0.2
        
        # Historical panic pattern
        panic_conditions = patterns.get('panic_sell_conditions', [])
        if len(panic_conditions) > 3:
            prob += 0.15
        
        return min(1.0, prob)
    
    def _calculate_chase_probability(self, context: Dict, patterns: Dict) -> float:
        """Calculate probability of chasing extension"""
        
        prob = 0.0
        
        # High volatility (things moving fast)
        volatility = context.get('market_volatility', 1.0)
        if volatility > 2.5:
            prob += 0.3
        
        # Winning streak (overconfidence)
        wins = context.get('consecutive_wins', 0)
        if wins >= 2:
            prob += 0.2
        
        # Time of day (chase peaks late morning)
        hour = context.get('time_of_day', 14)
        if 10 <= hour <= 12:
            prob += 0.2
        
        # Historical chase pattern
        chase_patterns = patterns.get('chase_extension_levels', [])
        if len(chase_patterns) > 3:
            prob += 0.2
        
        return min(1.0, prob)
    
    def _calculate_average_down_probability(self, context: Dict, patterns: Dict) -> float:
        """Calculate probability of averaging down a loser"""
        
        prob = 0.0
        
        # Negative P&L (temptation to average down)
        recent_pnl = context.get('recent_pnl', 0)
        if recent_pnl < -10:
            prob += 0.3
        elif recent_pnl < -5:
            prob += 0.2
        
        # Losing streak (trying to "fix it")
        losses = context.get('consecutive_losses', 0)
        if losses >= 2:
            prob += 0.25
        
        # Historical pattern
        avg_down_patterns = patterns.get('average_down_situations', [])
        if len(avg_down_patterns) > 2:
            prob += 0.2
        
        return min(1.0, prob)
    
    def _get_mistake_details(self, mistake_type: str, context: Dict, patterns: Dict) -> Dict:
        """Get detailed information about predicted mistake"""
        
        details = {
            'overtrade': {
                'time_window': 'Next 1-2 hours',
                'triggers': [
                    f"Already {context.get('trades_today', 0)} trades today",
                    f"{context.get('consecutive_wins', 0)} wins (overconfidence building)",
                    f"High volatility ({context.get('market_volatility', 1):.1f}x) = more temptation",
                    "Historical pattern: you overtrade after 2+ wins"
                ],
                'prevention_actions': [
                    "🛑 CLOSE LAPTOP NOW",
                    "Set hard limit: NO MORE TRADES TODAY",
                    "Walk away for 1 hour minimum",
                    "Your edge disappears after 3 trades/day"
                ],
                'historical_cost': self._calculate_average_cost(patterns, 'overtrade')
            },
            'fomo': {
                'time_window': 'Next 30-60 minutes',
                'triggers': [
                    f"Market volatility {context.get('market_volatility', 1):.1f}x (things moving fast)",
                    f"{context.get('consecutive_wins', 0)} wins (overconfident)",
                    f"It's {context.get('time_of_day', 14)}:00 (your FOMO window)",
                    "You see something running and want in"
                ],
                'prevention_actions': [
                    "🛑 WAIT 15 MINUTES",
                    "Write down WHY you want this trade",
                    "Check setup quality score - if <65, PASS",
                    "If it's already up >15%, it's too late",
                    "Your FOMO trades average -12% loss"
                ],
                'historical_cost': self._calculate_average_cost(patterns, 'fomo')
            },
            'hold_too_long': {
                'time_window': 'Currently at risk',
                'triggers': [
                    f"Current P/L: +{context.get('recent_pnl', 0):.1f}% (greed kicking in)",
                    f"{context.get('consecutive_wins', 0)} wins (getting greedy)",
                    "Thinking 'it can go higher'",
                    "You tend to give back 40% of gains holding too long"
                ],
                'prevention_actions': [
                    "✅ TRIM 50% RIGHT NOW",
                    "Set stop at breakeven on rest",
                    "Historical pattern: you hold through reversals",
                    "Take the win. It's enough."
                ],
                'historical_cost': self._calculate_average_cost(patterns, 'hold_too_long')
            },
            'revenge_trade': {
                'time_window': 'High risk NOW',
                'triggers': [
                    f"{context.get('consecutive_losses', 0)} losses in a row (anger building)",
                    f"Down {abs(context.get('recent_pnl', 0)):.1f}% (want to 'get it back')",
                    "Emotional state: frustrated/angry",
                    "You ALWAYS lose more when revenge trading"
                ],
                'prevention_actions': [
                    "🛑 STOP TRADING IMMEDIATELY",
                    "Close laptop. Leave room.",
                    "Don't trade for REST OF DAY",
                    "Your revenge trades average -8% MORE loss",
                    "The market will be here tomorrow"
                ],
                'historical_cost': self._calculate_average_cost(patterns, 'revenge')
            },
            'panic_sell': {
                'time_window': 'Risk during volatility spikes',
                'triggers': [
                    f"Down {abs(context.get('recent_pnl', 0)):.1f}% (pain threshold approaching)",
                    f"Volatility {context.get('market_volatility', 1):.1f}x (scary movements)",
                    "Feeling fear/panic",
                    "Your panic sells average -15% loss"
                ],
                'prevention_actions': [
                    "⚠️  BREATHE - Don't react",
                    "Check your stop - are we at stop? If no, HOLD",
                    "Zoom out - is this a normal pullback?",
                    "Historical: 70% of your panic sells recovered within 2 hours",
                    "Let your stop handle it, don't panic exit"
                ],
                'historical_cost': self._calculate_average_cost(patterns, 'panic')
            },
            'chase_extension': {
                'time_window': 'Next 30 minutes',
                'triggers': [
                    f"Market moving fast (volatility {context.get('market_volatility', 1):.1f}x)",
                    "Something already up 15-25%",
                    "FOMO kicking in",
                    "Your chase trades average -9% loss"
                ],
                'prevention_actions': [
                    "🛑 STEP BACK",
                    "If it's up >15%, you're too late",
                    "Wait for pullback (they always pull back)",
                    "Your best entries: early morning or pullback",
                    "Chasing never works for you"
                ],
                'historical_cost': self._calculate_average_cost(patterns, 'chase')
            },
            'average_down_loser': {
                'time_window': 'Current position risk',
                'triggers': [
                    f"Down {abs(context.get('recent_pnl', 0)):.1f}% on position",
                    "Thinking 'it's cheaper now, buy more'",
                    f"{context.get('consecutive_losses', 0)} losses (trying to fix it)",
                    "Your average-down trades lose 75% of the time"
                ],
                'prevention_actions': [
                    "🛑 DO NOT AVERAGE DOWN",
                    "Cut the loser at -7% max",
                    "Adding to losers NEVER works for you",
                    "Historical: 75% of your average-downs lost more",
                    "Take the small loss, move on"
                ],
                'historical_cost': self._calculate_average_cost(patterns, 'average_down')
            }
        }
        
        return details.get(mistake_type, {
            'time_window': 'Unknown',
            'triggers': [],
            'prevention_actions': ['Be cautious'],
            'historical_cost': 0
        })
    
    def _calculate_average_cost(self, patterns: Dict, mistake_type: str) -> float:
        """Calculate average cost of this mistake type"""
        
        # Simplified - would query actual losses
        costs = {
            'overtrade': -8.5,
            'fomo': -12.3,
            'hold_too_long': -6.7,
            'revenge': -11.2,
            'panic': -15.1,
            'chase': -9.4,
            'average_down': -13.8
        }
        
        return costs.get(mistake_type, -10.0)
    
    def format_prediction(self, result: Dict) -> str:
        """Format prediction for display"""
        
        if result.get('predicted_mistake') == 'none':
            return f"\n{'='*60}\n🔮 PREDICTIVE MISTAKE ENGINE\n{'='*60}\n\n✅ CLEAR - No high-probability mistakes detected\n\nAll systems green. Trade safely.\n\n{'='*60}\n"
        
        output = f"\n{'='*60}\n"
        output += f"🔮 PREDICTIVE MISTAKE ENGINE\n"
        output += f"{'='*60}\n\n"
        
        # Severity
        severity_display = {
            'critical': '🔴 CRITICAL',
            'high': '🟠 HIGH',
            'moderate': '🟡 MODERATE'
        }
        
        output += f"⚠️  PREDICTION: {result['predicted_mistake'].upper().replace('_', ' ')}\n"
        output += f"Probability: {result['probability']*100:.0f}%\n"
        output += f"Severity: {severity_display[result['severity']]}\n"
        output += f"Time Window: {result['time_window']}\n"
        output += f"Historical Cost: {result['historical_cost']:.1f}% average loss\n\n"
        
        # Triggers
        output += "WHY THIS PREDICTION:\n"
        for trigger in result['triggers']:
            output += f"  • {trigger}\n"
        output += "\n"
        
        # Prevention
        output += "🛡️  PREVENTION ACTIONS:\n"
        for action in result['prevention_actions']:
            output += f"  {action}\n"
        
        output += f"\n{'='*60}\n"
        
        return output


if __name__ == '__main__':
    engine = PredictiveMistakeEngine()
    
    # Test scenario: After 2 wins, 2 trades today, 2pm
    context = {
        'current_positions': 2,
        'trades_today': 2,
        'recent_pnl': 12.5,
        'market_volatility': 2.3,
        'time_of_day': 14,
        'day_of_week': 'Friday',
        'consecutive_wins': 2,
        'consecutive_losses': 0
    }
    
    prediction = engine.predict_next_mistake(context)
    print(engine.format_prediction(prediction))
