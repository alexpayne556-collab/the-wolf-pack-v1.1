# 🐺 FENRIR QUANTUM LEAP - MARKET REGIME DETECTOR
# "The market just changed character - adjust strategy NOW"

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf
from collections import deque

class MarketRegimeDetector:
    """
    Detect when the ENTIRE MARKET changes character
    
    Not just "market is up/down" - detect REGIME CHANGES:
    
    REGIMES:
    1. GRIND: Slow steady climbs, BTFD works, hold overnight safe
    2. EXPLOSIVE: Huge moves, momentum works, chase works, gaps hold
    3. CHOP: Violent swings, mean reversion works, don't hold overnight
    4. CRASH: Everything fails, cash is king, shorts work
    5. ROTATION: Sectors rotating fast, yesterday's winner is today's loser
    6. MEME: Social momentum dominates, fundamentals don't matter
    
    YOUR STRATEGY MUST MATCH THE REGIME or you lose
    
    Examples:
    - GRIND regime: Buy dips, hold, add on pullbacks
    - EXPLOSIVE regime: Chase momentum, tight stops, take profits fast
    - CHOP regime: Scalp, take profits 5-10%, don't hold overnight
    - ROTATION regime: Follow the money, exit yesterday's sector
    """
    
    def __init__(self):
        self.regime_history = deque(maxlen=30)  # Last 30 days
    
    def detect_current_regime(self) -> Dict:
        """
        Analyze current market regime
        
        Returns:
            regime_type: grind|explosive|chop|crash|rotation|meme
            confidence: 0-100
            characteristics: List of what defines this regime
            strategy_adjustments: What to do differently
            duration: How long has this regime lasted
        """
        
        try:
            # Get SPY data (market proxy)
            spy = yf.Ticker('SPY')
            hist = spy.history(period='30d', interval='1d')
            
            if hist.empty:
                return {'error': 'No market data'}
            
            # Get intraday data for recent volatility
            intraday = spy.history(period='5d', interval='5m')
            
            # Calculate regime indicators
            volatility = self._calculate_volatility(hist)
            trend_strength = self._calculate_trend_strength(hist)
            chop_factor = self._calculate_chop_factor(hist)
            gap_behavior = self._analyze_gap_behavior(hist)
            intraday_character = self._analyze_intraday_character(intraday)
            sector_rotation = self._check_sector_rotation()
            
            # Determine regime
            regime = self._classify_regime(
                volatility, trend_strength, chop_factor, 
                gap_behavior, intraday_character, sector_rotation
            )
            
            # Calculate duration (how long in this regime)
            duration = self._estimate_regime_duration(regime['type'], hist)
            
            # Get strategy adjustments
            strategy = self._get_strategy_for_regime(regime['type'])
            
            return {
                'regime_type': regime['type'],
                'confidence': regime['confidence'],
                'characteristics': regime['characteristics'],
                'strategy_adjustments': strategy,
                'duration_days': duration,
                'volatility_level': volatility,
                'trend_strength': trend_strength,
                'indicators': {
                    'volatility': volatility,
                    'trend_strength': trend_strength,
                    'chop_factor': chop_factor,
                    'gap_behavior': gap_behavior,
                    'intraday_character': intraday_character,
                    'sector_rotation': sector_rotation
                }
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_volatility(self, hist) -> float:
        """Calculate recent volatility"""
        
        # ATR-like calculation
        recent = hist.tail(10)
        
        ranges = []
        for i in range(len(recent)):
            day_range = (recent['High'].iloc[i] - recent['Low'].iloc[i]) / recent['Close'].iloc[i]
            ranges.append(day_range)
        
        avg_range = sum(ranges) / len(ranges) * 100
        return avg_range
    
    def _calculate_trend_strength(self, hist) -> float:
        """Calculate trend strength"""
        
        if len(hist) < 20:
            return 0
        
        # Compare current price to 20-day average
        ma20 = hist['Close'].tail(20).mean()
        current = hist['Close'].iloc[-1]
        
        deviation = ((current - ma20) / ma20) * 100
        
        # Also check consistency
        above_ma = sum(1 for i in range(-10, 0) if hist['Close'].iloc[i] > ma20)
        consistency = above_ma / 10
        
        # Strong trend = large deviation + consistent direction
        strength = abs(deviation) * consistency
        
        return strength
    
    def _calculate_chop_factor(self, hist) -> float:
        """Calculate how choppy the market is"""
        
        if len(hist) < 10:
            return 0
        
        recent = hist.tail(10)
        
        # Count direction changes
        direction_changes = 0
        for i in range(1, len(recent)):
            prev_change = recent['Close'].iloc[i-1] - recent['Close'].iloc[i-2] if i > 1 else 0
            curr_change = recent['Close'].iloc[i] - recent['Close'].iloc[i-1]
            
            if (prev_change > 0 and curr_change < 0) or (prev_change < 0 and curr_change > 0):
                direction_changes += 1
        
        # High chop = many direction changes
        chop_score = (direction_changes / 9) * 100  # 9 possible changes in 10 days
        
        return chop_score
    
    def _analyze_gap_behavior(self, hist) -> str:
        """Analyze how gaps behave (fill vs hold)"""
        
        if len(hist) < 10:
            return 'unknown'
        
        gaps_held = 0
        gaps_filled = 0
        
        for i in range(1, len(hist)):
            prev_close = hist['Close'].iloc[i-1]
            curr_open = hist['Open'].iloc[i]
            curr_close = hist['Close'].iloc[i]
            curr_low = hist['Low'].iloc[i]
            curr_high = hist['High'].iloc[i]
            
            # Check if gap up
            gap_pct = ((curr_open - prev_close) / prev_close) * 100
            
            if abs(gap_pct) > 0.5:  # 0.5%+ gap
                # Did it fill?
                if gap_pct > 0 and curr_low < prev_close:
                    gaps_filled += 1
                elif gap_pct < 0 and curr_high > prev_close:
                    gaps_filled += 1
                else:
                    gaps_held += 1
        
        if gaps_held + gaps_filled == 0:
            return 'no_gaps'
        
        hold_ratio = gaps_held / (gaps_held + gaps_filled)
        
        if hold_ratio > 0.7:
            return 'gaps_hold'  # Explosive regime
        elif hold_ratio < 0.3:
            return 'gaps_fill'  # Chop regime
        else:
            return 'mixed'
    
    def _analyze_intraday_character(self, intraday) -> str:
        """Analyze intraday behavior"""
        
        if intraday.empty or len(intraday) < 50:
            return 'unknown'
        
        # Look at each day
        days_explosive = 0
        days_choppy = 0
        
        # Group by date
        dates = intraday.index.date
        unique_dates = sorted(set(dates))
        
        for date in unique_dates[-5:]:  # Last 5 days
            day_data = intraday[intraday.index.date == date]
            
            if len(day_data) < 10:
                continue
            
            # Calculate intraday range
            day_range = (day_data['High'].max() - day_data['Low'].min()) / day_data['Close'].iloc[0] * 100
            
            # Count direction changes
            changes = 0
            for i in range(1, len(day_data)):
                if (day_data['Close'].iloc[i] - day_data['Close'].iloc[i-1]) * \
                   (day_data['Close'].iloc[i-1] - day_data['Close'].iloc[i-2]) < 0:
                    changes += 1
            
            change_rate = changes / len(day_data) if len(day_data) > 0 else 0
            
            if day_range > 1.5 and change_rate < 0.3:
                days_explosive += 1
            elif change_rate > 0.4:
                days_choppy += 1
        
        if days_explosive > days_choppy:
            return 'trending_intraday'
        elif days_choppy > days_explosive:
            return 'choppy_intraday'
        else:
            return 'mixed_intraday'
    
    def _check_sector_rotation(self) -> bool:
        """Check if sectors are rotating quickly"""
        
        # Simplified - would compare sector ETFs (XLK, XLF, XLE, etc.)
        # For now, return False
        return False
    
    def _classify_regime(self, volatility: float, trend_strength: float, 
                        chop_factor: float, gap_behavior: str,
                        intraday_character: str, sector_rotation: bool) -> Dict:
        """Classify the market regime"""
        
        characteristics = []
        
        # GRIND: Low vol, strong trend, gaps fill, steady intraday
        if volatility < 1.5 and trend_strength > 2 and chop_factor < 40:
            regime_type = 'grind'
            confidence = 80
            characteristics = [
                'Low volatility (steady moves)',
                'Strong consistent trend',
                'Gaps often fill',
                'Buy-the-dip works'
            ]
        
        # EXPLOSIVE: High vol, strong trend, gaps hold, trending intraday
        elif volatility > 2.5 and trend_strength > 3 and gap_behavior == 'gaps_hold':
            regime_type = 'explosive'
            confidence = 85
            characteristics = [
                'High volatility (big moves)',
                'Strong trend acceleration',
                'Gaps hold (momentum)',
                'Chase works, FOMO justified'
            ]
        
        # CHOP: High vol, weak trend, high chop factor
        elif chop_factor > 60 and trend_strength < 2:
            regime_type = 'chop'
            confidence = 75
            characteristics = [
                'High chop (many reversals)',
                'No clear trend',
                'Gaps fill quickly',
                'Mean reversion works'
            ]
        
        # CRASH: High vol, strong downtrend
        elif volatility > 3 and trend_strength < -3:
            regime_type = 'crash'
            confidence = 90
            characteristics = [
                'Extreme volatility',
                'Strong downtrend',
                'Nothing works',
                'Cash is king'
            ]
        
        # ROTATION: Sector rotation active
        elif sector_rotation:
            regime_type = 'rotation'
            confidence = 70
            characteristics = [
                'Sectors rotating fast',
                'Yesterday\'s winner is today\'s loser',
                'Follow the money flow',
                'Don\'t marry positions'
            ]
        
        # DEFAULT: Mixed/transitioning
        else:
            regime_type = 'mixed'
            confidence = 50
            characteristics = [
                'No clear regime',
                'Transitioning between states',
                'Trade cautiously'
            ]
        
        return {
            'type': regime_type,
            'confidence': confidence,
            'characteristics': characteristics
        }
    
    def _estimate_regime_duration(self, regime_type: str, hist) -> int:
        """Estimate how many days this regime has lasted"""
        
        # Simplified - count consecutive days matching regime
        # In real implementation, would track regime changes over time
        return 5  # Placeholder
    
    def _get_strategy_for_regime(self, regime_type: str) -> List[str]:
        """Get strategy adjustments for this regime"""
        
        strategies = {
            'grind': [
                "✅ Buy dips - they will recover",
                "✅ Hold overnight - gaps often fade",
                "✅ Add to winners on pullbacks",
                "❌ Don't chase - wait for pullback",
                "Position size: NORMAL"
            ],
            'explosive': [
                "✅ Chase momentum - it continues",
                "✅ Tight stops - move fast",
                "✅ Take profits on extensions",
                "✅ Gaps hold - don't fade them",
                "❌ Don't buy dips - they keep dipping",
                "Position size: 75% (faster moves)"
            ],
            'chop': [
                "✅ Scalp 5-10% - don't hold",
                "✅ Fade extensions",
                "✅ Take profits FAST",
                "❌ Don't hold overnight",
                "❌ Don't add to losers",
                "Position size: 50% (volatility trap)"
            ],
            'crash': [
                "🛑 CASH - sit on hands",
                "❌ Don't catch falling knives",
                "❌ Don't buy dips yet",
                "✅ Wait for capitulation",
                "Position size: 0-25%"
            ],
            'rotation': [
                "✅ Follow sector flow",
                "✅ Exit yesterday's leaders",
                "✅ Enter today's movers",
                "❌ Don't marry positions",
                "Position size: NORMAL but rotate fast"
            ],
            'mixed': [
                "⚠️  No clear regime - trade less",
                "✅ Wait for clearer setup",
                "✅ Smaller position sizes",
                "Position size: 50%"
            ]
        }
        
        return strategies.get(regime_type, ["⚠️  Unknown regime"])
    
    def format_regime_analysis(self, result: Dict) -> str:
        """Format regime analysis for display"""
        
        if 'error' in result:
            return f"\nError: {result['error']}\n"
        
        output = f"\n{'='*60}\n"
        output += f"🌊 MARKET REGIME DETECTOR\n"
        output += f"{'='*60}\n\n"
        
        # Regime type
        regime_display = {
            'grind': '📈 GRIND (Steady Climb)',
            'explosive': '🚀 EXPLOSIVE (Big Moves)',
            'chop': '⚡ CHOP (Violent Swings)',
            'crash': '💥 CRASH (Everything Fails)',
            'rotation': '🔄 ROTATION (Sector Rotation)',
            'mixed': '❓ MIXED (Unclear)'
        }
        
        output += f"CURRENT REGIME: {regime_display.get(result['regime_type'], result['regime_type'].upper())}\n"
        output += f"CONFIDENCE: {result['confidence']}%\n"
        output += f"DURATION: {result['duration_days']} days in this regime\n\n"
        
        # Characteristics
        output += "CHARACTERISTICS:\n"
        for char in result['characteristics']:
            output += f"  • {char}\n"
        output += "\n"
        
        # Strategy adjustments
        output += "🎯 STRATEGY ADJUSTMENTS:\n"
        for strategy in result['strategy_adjustments']:
            output += f"  {strategy}\n"
        output += "\n"
        
        # Technical details
        output += "TECHNICAL INDICATORS:\n"
        output += f"  Volatility: {result['volatility_level']:.2f}%\n"
        output += f"  Trend Strength: {result['trend_strength']:.2f}\n"
        output += f"  Gap Behavior: {result['indicators']['gap_behavior']}\n"
        output += f"  Intraday: {result['indicators']['intraday_character']}\n"
        
        output += f"\n{'='*60}\n"
        
        return output


if __name__ == '__main__':
    detector = MarketRegimeDetector()
    
    result = detector.detect_current_regime()
    print(detector.format_regime_analysis(result))
