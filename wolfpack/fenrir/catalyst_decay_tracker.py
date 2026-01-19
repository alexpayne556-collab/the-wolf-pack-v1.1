# 🐺 FENRIR QUANTUM LEAP - CATALYST DECAY TRACKER
# "This catalyst loses 70% of its power by day 3"

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import database
from collections import defaultdict

class CatalystDecayTracker:
    """
    Track how long catalysts stay powerful
    
    NOT all catalysts are equal:
    - FDA approval: Strong day 1-2, dead by day 5
    - Earnings beat: Strong day 1, fades by day 3
    - Buyout rumor: Can last weeks
    - 13D filing: Explosive day 1, watch day 2-3 carefully
    - Contract win: Gradual build over days
    
    This learns YOUR patterns: when do you take profits? When does the edge disappear?
    """
    
    def __init__(self):
        self.conn = database.get_connection()
    
    def track_catalyst_lifecycle(self, ticker: str, catalyst_type: str, catalyst_date: datetime) -> Dict:
        """
        Track how a catalyst's power decays over time
        
        Returns:
            - Peak power day (which day saw biggest move)
            - Decay rate (how fast it fades)
            - Life expectancy (how many days it lasts)
            - Warning signs (volume fade, price stall)
        """
        
        import yfinance as yf
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get 15 days after catalyst
            end_date = catalyst_date + timedelta(days=15)
            hist = stock.history(start=catalyst_date, end=end_date)
            
            if hist.empty:
                return {'error': 'No data available'}
            
            # Analyze each day
            days_analysis = []
            base_price = hist['Close'].iloc[0]
            base_volume = hist['Volume'].iloc[0]
            
            peak_day = 0
            peak_gain = 0
            
            for i in range(min(15, len(hist))):
                day_data = hist.iloc[i]
                
                gain_pct = ((day_data['Close'] - base_price) / base_price) * 100
                volume_ratio = day_data['Volume'] / base_volume if base_volume > 0 else 1
                
                days_analysis.append({
                    'day': i,
                    'date': day_data.name.strftime('%Y-%m-%d'),
                    'gain_pct': gain_pct,
                    'volume_ratio': volume_ratio,
                    'high': day_data['High'],
                    'low': day_data['Low']
                })
                
                if gain_pct > peak_gain:
                    peak_gain = gain_pct
                    peak_day = i
            
            # Calculate decay metrics
            decay_rate = self._calculate_decay_rate(days_analysis)
            life_expectancy = self._estimate_life_expectancy(days_analysis)
            warning_signs = self._detect_warning_signs(days_analysis)
            
            return {
                'ticker': ticker,
                'catalyst_type': catalyst_type,
                'peak_day': peak_day,
                'peak_gain_pct': peak_gain,
                'decay_rate': decay_rate,
                'life_expectancy_days': life_expectancy,
                'warning_signs': warning_signs,
                'daily_breakdown': days_analysis
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_decay_rate(self, days: List[Dict]) -> str:
        """Calculate how fast the catalyst power fades"""
        
        if len(days) < 3:
            return 'unknown'
        
        # Compare peak to day 3, day 5, day 10
        peak_gain = max(d['gain_pct'] for d in days[:5])
        
        day3_gain = days[2]['gain_pct'] if len(days) > 2 else 0
        day5_gain = days[4]['gain_pct'] if len(days) > 4 else 0
        
        # Calculate retention rate
        if peak_gain > 0:
            day3_retention = (day3_gain / peak_gain) * 100
            day5_retention = (day5_gain / peak_gain) * 100 if len(days) > 4 else 0
        else:
            day3_retention = 100
            day5_retention = 100
        
        if day3_retention < 30:
            return 'fast_decay'  # Loses 70%+ by day 3
        elif day3_retention < 60:
            return 'moderate_decay'  # Loses 40-70% by day 3
        else:
            return 'slow_decay'  # Retains 60%+ by day 3
    
    def _estimate_life_expectancy(self, days: List[Dict]) -> int:
        """Estimate how many days the catalyst stays powerful"""
        
        if not days:
            return 0
        
        peak_gain = max(d['gain_pct'] for d in days)
        
        if peak_gain <= 0:
            return 0
        
        # Find when it falls below 20% of peak
        threshold = peak_gain * 0.2
        
        for i, day in enumerate(days):
            if day['gain_pct'] < threshold:
                return i
        
        return len(days)  # Still going strong
    
    def _detect_warning_signs(self, days: List[Dict]) -> List[str]:
        """Detect warning signs that catalyst is dying"""
        
        warnings = []
        
        if len(days) < 3:
            return warnings
        
        # Volume fade
        recent_vol = sum(d['volume_ratio'] for d in days[-3:]) / 3
        early_vol = sum(d['volume_ratio'] for d in days[:3]) / 3
        
        if recent_vol < early_vol * 0.5:
            warnings.append('VOLUME_FADE: Volume dropped 50%+')
        
        # Price stalling
        recent_gains = [d['gain_pct'] for d in days[-3:]]
        if max(recent_gains) - min(recent_gains) < 3:
            warnings.append('PRICE_STALL: Consolidating tight')
        
        # Lower highs
        if len(days) >= 5:
            highs = [d['gain_pct'] for d in days[-5:]]
            if all(highs[i] < highs[i-1] for i in range(1, len(highs))):
                warnings.append('LOWER_HIGHS: Momentum fading')
        
        # Gap down
        for i in range(1, len(days)):
            prev_close = days[i-1]['gain_pct']
            curr_low = days[i]['low']
            
            # If today's low is significantly below yesterday's close
            if len(days) > i:
                pass  # Simplified check
        
        return warnings
    
    def get_historical_patterns(self, catalyst_type: str) -> Dict:
        """
        Get historical patterns for this catalyst type
        
        Returns average lifecycle metrics from past trades
        """
        
        cursor = self.conn.cursor()
        
        # Get past trades with this catalyst type
        cursor.execute('''
            SELECT ticker, timestamp FROM trade_journal
            WHERE setup_type = ? AND action = 'BUY'
            ORDER BY timestamp DESC
            LIMIT 20
        ''', (catalyst_type,))
        
        trades = cursor.fetchall()
        
        if not trades:
            return {
                'catalyst_type': catalyst_type,
                'sample_size': 0,
                'avg_peak_day': None,
                'avg_life_expectancy': None,
                'typical_decay': 'unknown'
            }
        
        # Analyze each historical trade
        lifecycles = []
        
        for ticker, timestamp in trades:
            catalyst_date = datetime.fromisoformat(timestamp)
            lifecycle = self.track_catalyst_lifecycle(ticker, catalyst_type, catalyst_date)
            
            if 'error' not in lifecycle:
                lifecycles.append(lifecycle)
        
        # Calculate averages
        if lifecycles:
            avg_peak_day = sum(l['peak_day'] for l in lifecycles) / len(lifecycles)
            avg_life = sum(l['life_expectancy_days'] for l in lifecycles) / len(lifecycles)
            
            # Most common decay pattern
            decay_patterns = [l['decay_rate'] for l in lifecycles]
            typical_decay = max(set(decay_patterns), key=decay_patterns.count)
        else:
            avg_peak_day = None
            avg_life = None
            typical_decay = 'unknown'
        
        return {
            'catalyst_type': catalyst_type,
            'sample_size': len(lifecycles),
            'avg_peak_day': avg_peak_day,
            'avg_life_expectancy': avg_life,
            'typical_decay': typical_decay,
            'examples': lifecycles[:3]
        }
    
    def should_trim_position(self, ticker: str, catalyst_type: str, days_since_catalyst: int) -> Dict:
        """
        Determine if you should trim based on catalyst decay
        
        Returns recommendation with reasoning
        """
        
        # Get historical pattern for this catalyst type
        pattern = self.get_historical_patterns(catalyst_type)
        
        if pattern['sample_size'] == 0:
            return {
                'recommendation': 'HOLD',
                'confidence': 'low',
                'reason': 'No historical data for this catalyst type'
            }
        
        avg_peak = pattern['avg_peak_day']
        avg_life = pattern['avg_life_expectancy']
        
        # Decision logic
        if days_since_catalyst > avg_life:
            return {
                'recommendation': 'TRIM',
                'confidence': 'high',
                'reason': f'Day {days_since_catalyst} exceeds typical {catalyst_type} life ({avg_life:.0f} days)',
                'historical_pattern': f'This catalyst type typically peaks day {avg_peak:.0f}, dies by day {avg_life:.0f}'
            }
        
        elif days_since_catalyst >= avg_peak * 1.5:
            return {
                'recommendation': 'TRIM 50%',
                'confidence': 'medium',
                'reason': f'Day {days_since_catalyst} is {1.5:.1f}x past typical peak (day {avg_peak:.0f})',
                'historical_pattern': f'Historical peak day: {avg_peak:.0f}. You\'re in the decay zone.'
            }
        
        elif days_since_catalyst <= avg_peak:
            return {
                'recommendation': 'HOLD',
                'confidence': 'high',
                'reason': f'Still within typical peak window (day {avg_peak:.0f})',
                'historical_pattern': f'This catalyst usually peaks around day {avg_peak:.0f}'
            }
        
        else:
            return {
                'recommendation': 'WATCH CLOSELY',
                'confidence': 'medium',
                'reason': f'Approaching typical decay zone (day {avg_life:.0f})',
                'historical_pattern': f'Peak was day {avg_peak:.0f}, life expectancy {avg_life:.0f} days'
            }
    
    def format_decay_analysis(self, lifecycle: Dict) -> str:
        """Format lifecycle analysis for display"""
        
        if 'error' in lifecycle:
            return f"\nError: {lifecycle['error']}\n"
        
        output = f"\n{'='*60}\n"
        output += f"⏱️  CATALYST DECAY ANALYSIS: {lifecycle['ticker']}\n"
        output += f"{'='*60}\n\n"
        
        output += f"Catalyst Type: {lifecycle['catalyst_type']}\n"
        output += f"Peak Power: Day {lifecycle['peak_day']} (+{lifecycle['peak_gain_pct']:.1f}%)\n"
        output += f"Decay Rate: {lifecycle['decay_rate'].upper().replace('_', ' ')}\n"
        output += f"Life Expectancy: {lifecycle['life_expectancy_days']} days\n\n"
        
        # Warning signs
        if lifecycle['warning_signs']:
            output += "⚠️  WARNING SIGNS:\n"
            for warning in lifecycle['warning_signs']:
                output += f"  • {warning}\n"
            output += "\n"
        
        # Day-by-day breakdown (first 7 days)
        output += "DAY-BY-DAY BREAKDOWN:\n"
        for day in lifecycle['daily_breakdown'][:7]:
            volume_indicator = "🔥" if day['volume_ratio'] > 2 else "📊" if day['volume_ratio'] > 1 else "📉"
            output += f"  Day {day['day']}: {day['gain_pct']:+.1f}% | {volume_indicator} {day['volume_ratio']:.1f}x vol\n"
        
        output += f"\n{'='*60}\n"
        
        return output


if __name__ == '__main__':
    tracker = CatalystDecayTracker()
    
    # Analyze IBRX catalyst lifecycle
    catalyst_date = datetime(2026, 1, 6)  # Assume catalyst was Jan 6
    lifecycle = tracker.track_catalyst_lifecycle('IBRX', 'dual_catalyst', catalyst_date)
    
    print(tracker.format_decay_analysis(lifecycle))
    
    # Check if should trim
    decision = tracker.should_trim_position('IBRX', 'dual_catalyst', days_since_catalyst=10)
    print(f"\nTRIM DECISION: {decision['recommendation']}")
    print(f"Confidence: {decision['confidence']}")
    print(f"Reason: {decision['reason']}")
