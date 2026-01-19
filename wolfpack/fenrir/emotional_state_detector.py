# 🐺 FENRIR QUANTUM LEVEL 2 - EMOTIONAL STATE DETECTOR
# "I can tell you're tilting - typing speed is 2x normal"

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import database
from collections import deque
import numpy as np

class EmotionalStateDetector:
    """
    Detect YOUR emotional state from behavioral patterns
    
    Not just "you lost money" - detect TILT from subtle signals:
    
    SIGNALS TRACKED:
    1. Typing speed (tilting = faster, manic typing)
    2. Command frequency (tilting = checking portfolio every 30 sec)
    3. Query patterns (tilting = "why is X down?" repeated queries)
    4. Time between trades (tilting = rapid fire entries)
    5. Note quality (tilting = shorter, emotional notes)
    6. Trading hours (tilting = trading after your "stop time")
    7. Symbol switching (tilting = jumping between many tickers)
    
    EMOTIONAL STATES DETECTED:
    - CALM: Normal behavior, trading edge intact
    - ANXIOUS: Checking too frequently, but not acting yet
    - TILTING: Making emotional decisions, losing edge
    - RAGE: Full tilt, revenge trading mode
    - GREEDY: Overconfident after wins, taking too much risk
    - FEARFUL: Paralyzed, can't pull trigger on good setups
    
    Example: "🚨 TILT DETECTED:
             - Checking portfolio 8 times in 10 min (normal: 2x/hour)
             - Query speed: 2.3x faster than baseline
             - Symbol switching: 12 tickers in 20 min (normal: 3)
             - Time: 3:47pm (past your 3pm cutoff)
             DIAGNOSIS: RAGE state after losses
             ACTION: Close laptop immediately. Walk away for 24 hours."
    """
    
    def __init__(self):
        self.conn = database.get_connection()
        self.interaction_history = deque(maxlen=100)  # Last 100 interactions
        self.baseline_metrics = self._calculate_baseline()
    
    def record_interaction(self, interaction_type: str, data: Dict):
        """
        Record user interaction for pattern analysis
        
        Types: 'query', 'trade', 'note', 'check_portfolio', 'check_position'
        """
        
        self.interaction_history.append({
            'timestamp': datetime.now(),
            'type': interaction_type,
            'data': data
        })
    
    def detect_emotional_state(self) -> Dict:
        """
        Analyze recent behavior to detect emotional state
        
        Returns:
            state: 'calm'|'anxious'|'tilting'|'rage'|'greedy'|'fearful'
            confidence: 0-1
            signals: List of detected signals
            severity: 1-10
            recommendations: List of actions
        """
        
        if len(self.interaction_history) < 5:
            return {
                'state': 'calm',
                'confidence': 0.5,
                'signals': [],
                'severity': 0,
                'recommendations': ['Insufficient data for analysis']
            }
        
        # Analyze various behavioral signals
        signals = []
        severity_scores = []
        
        # Signal 1: Check frequency
        check_freq_signal = self._analyze_check_frequency()
        if check_freq_signal:
            signals.append(check_freq_signal)
            severity_scores.append(check_freq_signal['severity'])
        
        # Signal 2: Query patterns
        query_pattern_signal = self._analyze_query_patterns()
        if query_pattern_signal:
            signals.append(query_pattern_signal)
            severity_scores.append(query_pattern_signal['severity'])
        
        # Signal 3: Trade timing
        trade_timing_signal = self._analyze_trade_timing()
        if trade_timing_signal:
            signals.append(trade_timing_signal)
            severity_scores.append(trade_timing_signal['severity'])
        
        # Signal 4: Symbol switching
        symbol_switching_signal = self._analyze_symbol_switching()
        if symbol_switching_signal:
            signals.append(symbol_switching_signal)
            severity_scores.append(symbol_switching_signal['severity'])
        
        # Signal 5: Trading hours violation
        hours_signal = self._analyze_trading_hours()
        if hours_signal:
            signals.append(hours_signal)
            severity_scores.append(hours_signal['severity'])
        
        # Signal 6: Recent P&L context
        pnl_signal = self._analyze_pnl_context()
        if pnl_signal:
            signals.append(pnl_signal)
            severity_scores.append(pnl_signal['severity'])
        
        # Determine overall emotional state
        if not severity_scores:
            state = 'calm'
            severity = 0
            confidence = 0.7
        else:
            avg_severity = np.mean(severity_scores)
            severity = int(avg_severity)
            
            if avg_severity >= 8:
                state = 'rage'
                confidence = 0.9
            elif avg_severity >= 6:
                state = 'tilting'
                confidence = 0.85
            elif avg_severity >= 4:
                state = 'anxious'
                confidence = 0.75
            elif avg_severity <= 2 and any('greedy' in s['description'].lower() for s in signals):
                state = 'greedy'
                confidence = 0.8
            elif avg_severity <= 3 and any('fearful' in s['description'].lower() for s in signals):
                state = 'fearful'
                confidence = 0.75
            else:
                state = 'calm'
                confidence = 0.7
        
        # Generate recommendations
        recommendations = self._generate_recommendations(state, severity, signals)
        
        return {
            'state': state,
            'confidence': confidence,
            'signals': signals,
            'severity': severity,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_baseline(self) -> Dict:
        """Calculate baseline behavior metrics from history"""
        
        # Simplified - would calculate from long-term history
        return {
            'avg_checks_per_hour': 2.5,
            'avg_queries_per_hour': 4.0,
            'avg_trades_per_day': 2.0,
            'avg_symbols_per_day': 5.0,
            'normal_trading_end_hour': 15  # 3pm
        }
    
    def _analyze_check_frequency(self) -> Optional[Dict]:
        """Analyze how often checking portfolio/positions"""
        
        recent_checks = [i for i in self.interaction_history 
                        if i['type'] in ['check_portfolio', 'check_position']
                        and (datetime.now() - i['timestamp']).total_seconds() < 3600]
        
        checks_per_hour = len(recent_checks)
        baseline = self.baseline_metrics['avg_checks_per_hour']
        
        if checks_per_hour > baseline * 3:
            return {
                'signal': 'excessive_checking',
                'description': f"Checking portfolio {checks_per_hour} times/hour (normal: {baseline:.1f})",
                'severity': min(10, int((checks_per_hour / baseline) * 3)),
                'interpretation': 'High anxiety or obsessive monitoring'
            }
        
        return None
    
    def _analyze_query_patterns(self) -> Optional[Dict]:
        """Analyze query patterns for emotional indicators"""
        
        recent_queries = [i for i in self.interaction_history 
                         if i['type'] == 'query'
                         and (datetime.now() - i['timestamp']).total_seconds() < 1800]
        
        if len(recent_queries) < 3:
            return None
        
        # Check for repeated queries (obsessive)
        queries_text = [q['data'].get('text', '').lower() for q in recent_queries]
        
        # Emotional keywords
        anxious_keywords = ['why', 'down', 'dropping', 'losing', 'wrong']
        greedy_keywords = ['up', 'more', 'higher', 'gain']
        
        anxious_count = sum(1 for q in queries_text if any(kw in q for kw in anxious_keywords))
        greedy_count = sum(1 for q in queries_text if any(kw in q for kw in greedy_keywords))
        
        # Query speed
        if len(recent_queries) >= 2:
            time_diffs = []
            for i in range(1, len(recent_queries)):
                diff = (recent_queries[i]['timestamp'] - recent_queries[i-1]['timestamp']).total_seconds()
                time_diffs.append(diff)
            
            avg_time_between = np.mean(time_diffs) if time_diffs else 300
            
            if avg_time_between < 30:  # Queries every 30 seconds
                return {
                    'signal': 'rapid_queries',
                    'description': f"Queries every {avg_time_between:.0f} seconds (manic behavior)",
                    'severity': 8,
                    'interpretation': 'Anxious or tilting - obsessive behavior'
                }
        
        if anxious_count >= 3:
            return {
                'signal': 'anxious_queries',
                'description': f"{anxious_count} anxious queries in 30 min ('why down?', 'losing')",
                'severity': 7,
                'interpretation': 'High anxiety about losses'
            }
        
        return None
    
    def _analyze_trade_timing(self) -> Optional[Dict]:
        """Analyze time between trades"""
        
        cursor = self.conn.cursor()
        
        # Get today's trades
        today_start = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
        cursor.execute('''
            SELECT timestamp FROM trade_journal
            WHERE timestamp > ? AND action = 'BUY'
            ORDER BY timestamp
        ''', (today_start,))
        
        trades = cursor.fetchall()
        
        if len(trades) < 2:
            return None
        
        # Calculate time between trades
        trade_times = [datetime.fromisoformat(t[0]) for t in trades]
        time_diffs = []
        
        for i in range(1, len(trade_times)):
            diff_minutes = (trade_times[i] - trade_times[i-1]).total_seconds() / 60
            time_diffs.append(diff_minutes)
        
        avg_time_between = np.mean(time_diffs)
        
        # Rapid fire trades = tilting
        if avg_time_between < 15:  # Less than 15 min between trades
            return {
                'signal': 'rapid_fire_trades',
                'description': f"Trades every {avg_time_between:.0f} min (rapid fire)",
                'severity': 9,
                'interpretation': 'Revenge trading or overtrading'
            }
        
        return None
    
    def _analyze_symbol_switching(self) -> Optional[Dict]:
        """Analyze how many different symbols being checked"""
        
        recent_interactions = [i for i in self.interaction_history
                             if (datetime.now() - i['timestamp']).total_seconds() < 1200]  # Last 20 min
        
        symbols = set()
        for interaction in recent_interactions:
            if 'ticker' in interaction['data']:
                symbols.add(interaction['data']['ticker'])
            elif 'symbol' in interaction['data']:
                symbols.add(interaction['data']['symbol'])
        
        symbol_count = len(symbols)
        
        if symbol_count > 8:  # More than 8 symbols in 20 min
            return {
                'signal': 'excessive_symbol_switching',
                'description': f"Checking {symbol_count} different symbols in 20 min",
                'severity': 7,
                'interpretation': 'Scattered focus, chasing, FOMO'
            }
        
        return None
    
    def _analyze_trading_hours(self) -> Optional[Dict]:
        """Check if trading outside normal hours"""
        
        hour = datetime.now().hour
        normal_end = self.baseline_metrics['normal_trading_end_hour']
        
        # Check if there are trades after normal hours
        cursor = self.conn.cursor()
        today_start = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
        
        cursor.execute('''
            SELECT timestamp FROM trade_journal
            WHERE timestamp > ? AND action = 'BUY'
        ''', (today_start,))
        
        trades = cursor.fetchall()
        
        late_trades = []
        for trade in trades:
            trade_time = datetime.fromisoformat(trade[0])
            if trade_time.hour >= normal_end:
                late_trades.append(trade_time)
        
        if late_trades:
            return {
                'signal': 'trading_after_hours',
                'description': f"{len(late_trades)} trades after {normal_end}:00 (your cutoff)",
                'severity': 8,
                'interpretation': 'Emotional trading, ignoring rules'
            }
        
        # Current check
        if hour >= normal_end and len([i for i in self.interaction_history 
                                      if (datetime.now() - i['timestamp']).total_seconds() < 300]) > 0:
            return {
                'signal': 'active_after_hours',
                'description': f"Still active at {hour}:00 (cutoff: {normal_end}:00)",
                'severity': 6,
                'interpretation': 'Unable to disconnect, potential overtrading'
            }
        
        return None
    
    def _analyze_pnl_context(self) -> Optional[Dict]:
        """Analyze recent P&L for emotional context"""
        
        cursor = self.conn.cursor()
        today_start = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
        
        cursor.execute('''
            SELECT pnl_pct, outcome FROM trade_journal
            WHERE timestamp > ? AND outcome IS NOT NULL
            ORDER BY timestamp DESC
        ''', (today_start,))
        
        trades = cursor.fetchall()
        
        if not trades:
            return None
        
        # Recent losses = potential rage/revenge
        recent_losses = sum(1 for t in trades[:3] if t[1] == 'LOSS')
        
        if recent_losses >= 2:
            total_loss = sum(t[0] for t in trades[:3] if t[1] == 'LOSS')
            return {
                'signal': 'consecutive_losses',
                'description': f"{recent_losses} losses in a row ({total_loss:.1f}% total)",
                'severity': 8,
                'interpretation': 'High risk of revenge trading'
            }
        
        # Recent wins = potential greed
        recent_wins = sum(1 for t in trades[:3] if t[1] == 'WIN')
        
        if recent_wins >= 3:
            total_gain = sum(t[0] for t in trades[:3] if t[1] == 'WIN')
            return {
                'signal': 'winning_streak',
                'description': f"{recent_wins} wins in a row (+{total_gain:.1f}% total)",
                'severity': 5,
                'interpretation': 'Potential overconfidence/greed'
            }
        
        return None
    
    def _generate_recommendations(self, state: str, severity: int, signals: List[Dict]) -> List[str]:
        """Generate recommendations based on emotional state"""
        
        recommendations = []
        
        if state == 'rage':
            recommendations = [
                "🛑 STOP TRADING IMMEDIATELY",
                "Close laptop. Leave room. Don't look at markets.",
                "Take 24 hour break MINIMUM",
                "Your emotional state will cost you money",
                "The market will be here tomorrow"
            ]
        
        elif state == 'tilting':
            recommendations = [
                "⚠️  REDUCE POSITION SIZES by 75%",
                "Take 2 hour break - walk, gym, anything else",
                "Do NOT enter new positions",
                "Review trades tomorrow when calm",
                "Your decision-making is compromised"
            ]
        
        elif state == 'anxious':
            recommendations = [
                "⚠️  REDUCE POSITION SIZES by 50%",
                "Stop checking portfolio every 5 min",
                "Set alerts instead of watching",
                "Take 30 min break",
                "Anxiety leads to panic sells"
            ]
        
        elif state == 'greedy':
            recommendations = [
                "⚠️  TRIM WINNERS - Take some profit",
                "You're getting overconfident",
                "Reduce position sizes by 25%",
                "Winning streaks often end badly",
                "Protect your gains"
            ]
        
        elif state == 'fearful':
            recommendations = [
                "You're overthinking good setups",
                "Trust your analysis",
                "Start with smaller size to build confidence",
                "Review your winning trades",
                "Fear costs as much as greed"
            ]
        
        else:  # calm
            recommendations = [
                "✅ Emotional state is healthy",
                "Continue trading normally",
                "Your decision-making is sound"
            ]
        
        return recommendations
    
    def format_emotional_analysis(self, result: Dict) -> str:
        """Format emotional state analysis"""
        
        output = f"\n{'='*60}\n"
        output += f"🧠 EMOTIONAL STATE DETECTOR\n"
        output += f"{'='*60}\n\n"
        
        # State display
        state_emoji = {
            'calm': '🟢 CALM',
            'anxious': '🟡 ANXIOUS',
            'tilting': '🟠 TILTING',
            'rage': '🔴 RAGE',
            'greedy': '🟡 GREEDY',
            'fearful': '🔵 FEARFUL'
        }
        
        output += f"CURRENT STATE: {state_emoji.get(result['state'], result['state'].upper())}\n"
        output += f"Confidence: {result['confidence']*100:.0f}%\n"
        output += f"Severity: {result['severity']}/10\n\n"
        
        # Signals detected
        if result['signals']:
            output += "🚨 SIGNALS DETECTED:\n"
            for signal in result['signals']:
                output += f"\n  • {signal['signal'].upper().replace('_', ' ')}\n"
                output += f"    {signal['description']}\n"
                output += f"    Severity: {signal['severity']}/10\n"
                output += f"    Means: {signal['interpretation']}\n"
        else:
            output += "✅ No concerning signals detected\n"
        
        output += "\n"
        
        # Recommendations
        output += "💡 RECOMMENDATIONS:\n"
        for rec in result['recommendations']:
            output += f"  {rec}\n"
        
        output += f"\n{'='*60}\n"
        
        return output


if __name__ == '__main__':
    detector = EmotionalStateDetector()
    
    # Simulate tilting behavior
    for i in range(10):
        detector.record_interaction('check_portfolio', {})
        detector.record_interaction('query', {'text': 'why is IBRX down?'})
    
    result = detector.detect_emotional_state()
    print(detector.format_emotional_analysis(result))
