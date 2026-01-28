"""
MULTI-STRATEGY SYSTEM - EXPANDING THE WOLF PACK BRAIN
Built: January 20, 2026

Philosophy:
- ADD strategies, NEVER replace existing ones
- Each strategy is independent module (plugin architecture)
- System learns which strategies work for YOU
- Bot adapts to your trading style over time

Current Strategies (Built):
1. FLAT-TO-BOOM (Jan 20): 3-6 month consolidation + insider + catalyst
2. CONVERGENCE SCORING (Jan 19): 70-point weighted multi-factor

New Strategies to Add:
3. SUPPLY SHOCK: RGC-style float destruction detection
4. BREAKOUT CONFIRMATION: Livermore pivotal points with volume
5. BOTTOMING REVERSAL: Capitulation + insider buying at lows
6. ACTIVIST ENTRY: 13D/13G filings on quality names
7. SECTOR ROTATION: Hot sector + undervalued name catching up
8. SQUEEZE SETUP: High short interest + catalyst + tight float

Architecture:
- Each strategy = separate class inheriting from BaseStrategy
- Strategy returns: signal (BUY/PASS), confidence (0-100), reason
- System combines ALL strategies → weighted decision
- Learning engine tracks: which strategies YOU follow, which work
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import yfinance as yf
import json
from pathlib import Path


class BaseStrategy(ABC):
    """
    Base class for ALL trading strategies
    All new strategies inherit from this
    """
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight  # Can be adjusted by learning engine
        self.enabled = True
        
    @abstractmethod
    def analyze(self, ticker: str, data: Dict) -> Dict:
        """
        Analyze ticker and return signal
        
        Returns:
            {
                'signal': 'BUY' | 'HOLD' | 'PASS',
                'confidence': 0-100,
                'reason': str,
                'entry_price': float,
                'stop_loss': float,
                'targets': [float, float, float],
                'strategy_specific': {}  # Additional data
            }
        """
        pass
    
    def get_performance_stats(self) -> Dict:
        """Get this strategy's historical performance"""
        # Will be tracked by learning engine
        return {}


class SupplyShockStrategy(BaseStrategy):
    """
    Strategy 3: SUPPLY SHOCK Detection
    Based on RGC analysis (20,000% move from supply destruction)
    
    Pattern:
    - Ultra-low float (<5M, ideally <2M)
    - High insider ownership (>50% locked)
    - NEW insider buying (Form 4 signal) - THIS IS KEY
    - Removes significant % of remaining float
    - Price compressed (not already running)
    
    The Math:
    If CEO owns 86% and buys another 10% of float → only 4% left trading
    Any institutional demand → supply/demand imbalance → price explosion
    
    This is PHYSICS, not speculation.
    """
    
    def __init__(self):
        super().__init__("SUPPLY_SHOCK", weight=1.5)  # High weight (validated)
        self.float_max = 5_000_000  # 5M max
        self.insider_min = 0.50  # 50% min locked
        self.new_buy_min = 50000  # $50K min new buy
        
    def analyze(self, ticker: str, data: Dict) -> Dict:
        """Detect supply shock setup"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get float and insider data
            float_shares = info.get('floatShares', 0)
            insider_pct = info.get('heldPercentInsiders', 0) * 100
            
            # Check basic requirements
            if float_shares > self.float_max:
                return self._no_signal("Float too large")
            
            if insider_pct < self.insider_min * 100:
                return self._no_signal("Insider ownership too low")
            
            # Calculate tradeable float
            total_shares = info.get('sharesOutstanding', float_shares)
            locked_shares = total_shares * (insider_pct / 100)
            tradeable_float = total_shares - locked_shares
            
            # Check for NEW insider buying (would come from data param)
            recent_buys = data.get('insider_buys', [])
            significant_buys = [b for b in recent_buys if b.get('value', 0) >= self.new_buy_min]
            
            if not significant_buys:
                return self._no_signal("No recent insider buying")
            
            # Calculate % of float being removed
            total_buy_value = sum(b.get('value', 0) for b in significant_buys)
            current_price = info.get('currentPrice', 0)
            
            if current_price == 0:
                return self._no_signal("Price data unavailable")
            
            shares_bought = total_buy_value / current_price
            float_removal_pct = (shares_bought / tradeable_float) * 100 if tradeable_float > 0 else 0
            
            # Score based on float removal %
            if float_removal_pct > 20:  # Removing >20% of tradeable float
                confidence = 95
                reason = f"🚨 SUPPLY SHOCK: {float_removal_pct:.1f}% of tradeable float removed"
            elif float_removal_pct > 10:
                confidence = 85
                reason = f"⚠️ Supply squeeze: {float_removal_pct:.1f}% float removed"
            elif float_removal_pct > 5:
                confidence = 70
                reason = f"Supply tightening: {float_removal_pct:.1f}% float removed"
            else:
                return self._no_signal(f"Only {float_removal_pct:.1f}% float removal")
            
            # Calculate targets based on float reduction
            multiplier = 1 + (float_removal_pct / 10)  # Each 10% removal = 2x potential
            
            return {
                'signal': 'BUY',
                'confidence': confidence,
                'reason': reason,
                'entry_price': current_price,
                'stop_loss': current_price * 0.85,  # 15% stop
                'targets': [
                    current_price * multiplier * 0.5,  # Conservative
                    current_price * multiplier * 1.0,  # Expected
                    current_price * multiplier * 2.0   # Explosive
                ],
                'strategy_specific': {
                    'float_shares': float_shares,
                    'tradeable_float': tradeable_float,
                    'insider_pct': insider_pct,
                    'float_removal_pct': float_removal_pct,
                    'significant_buys': significant_buys
                }
            }
            
        except Exception as e:
            return self._no_signal(f"Error: {str(e)}")
    
    def _no_signal(self, reason: str) -> Dict:
        """Return no signal"""
        return {
            'signal': 'PASS',
            'confidence': 0,
            'reason': reason,
            'entry_price': 0,
            'stop_loss': 0,
            'targets': [0, 0, 0],
            'strategy_specific': {}
        }


class BreakoutConfirmationStrategy(BaseStrategy):
    """
    Strategy 4: BREAKOUT CONFIRMATION
    Livermore pivotal points + Day 2 follow-through
    
    Pattern:
    - Consolidation period (20+ days)
    - Breakout on volume (3x+ average)
    - Day 2 confirmation (closes above Day 1 high)
    - Retest of breakout level holds
    
    Entry: On Day 2 confirmation or retest hold
    """
    
    def __init__(self):
        super().__init__("BREAKOUT_CONFIRMATION", weight=1.2)
        self.consolidation_days = 20
        self.volume_multiplier = 3.0
        
    def analyze(self, ticker: str, data: Dict) -> Dict:
        """Detect confirmed breakout"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="3mo")
            
            if len(hist) < self.consolidation_days:
                return self._no_signal("Insufficient data")
            
            # Find consolidation range
            lookback_data = hist.iloc[-self.consolidation_days-5:-5]  # Exclude last 5 days
            consolidation_high = lookback_data['High'].max()
            consolidation_low = lookback_data['Low'].min()
            consolidation_range = consolidation_high - consolidation_low
            
            # Check if recent breakout above consolidation
            recent = hist.iloc[-5:]
            current_price = hist['Close'].iloc[-1]
            
            breakout_bar = None
            for i in range(len(recent)):
                if recent['High'].iloc[i] > consolidation_high:
                    breakout_bar = i
                    break
            
            if breakout_bar is None:
                return self._no_signal("No breakout detected")
            
            # Check volume confirmation
            breakout_volume = recent['Volume'].iloc[breakout_bar]
            avg_volume = lookback_data['Volume'].mean()
            volume_ratio = breakout_volume / avg_volume if avg_volume > 0 else 0
            
            if volume_ratio < self.volume_multiplier:
                return self._no_signal(f"Volume too low ({volume_ratio:.1f}x)")
            
            # Check Day 2 confirmation (if applicable)
            days_since_breakout = len(recent) - breakout_bar - 1
            
            if days_since_breakout >= 1:
                day2_close = recent['Close'].iloc[breakout_bar + 1]
                breakout_high = recent['High'].iloc[breakout_bar]
                
                confirmed = day2_close > breakout_high
                
                if confirmed:
                    confidence = 90
                    reason = f"✅ Breakout CONFIRMED: Day 2 above Day 1 high ({volume_ratio:.1f}x volume)"
                else:
                    confidence = 60
                    reason = f"⚠️ Breakout unconfirmed: Day 2 below Day 1 high"
            else:
                confidence = 75
                reason = f"🔄 Breakout detected: Waiting Day 2 confirmation ({volume_ratio:.1f}x volume)"
            
            # Calculate targets
            range_height = consolidation_range
            measured_move = current_price + range_height
            
            return {
                'signal': 'BUY' if confidence >= 75 else 'HOLD',
                'confidence': confidence,
                'reason': reason,
                'entry_price': current_price,
                'stop_loss': consolidation_high * 0.97,  # Just below breakout
                'targets': [
                    current_price + (range_height * 0.5),
                    measured_move,
                    measured_move * 1.5
                ],
                'strategy_specific': {
                    'consolidation_high': consolidation_high,
                    'consolidation_low': consolidation_low,
                    'volume_ratio': volume_ratio,
                    'days_since_breakout': days_since_breakout
                }
            }
            
        except Exception as e:
            return self._no_signal(f"Error: {str(e)}")
    
    def _no_signal(self, reason: str) -> Dict:
        return {
            'signal': 'PASS',
            'confidence': 0,
            'reason': reason,
            'entry_price': 0,
            'stop_loss': 0,
            'targets': [0, 0, 0],
            'strategy_specific': {}
        }


class BottomingReversalStrategy(BaseStrategy):
    """
    Strategy 5: BOTTOMING REVERSAL
    Capitulation + insider buying at lows
    
    Pattern:
    - Stock down 50%+ from highs
    - Volume capitulation (10x+ spike on down day)
    - Insider buying AT THE LOWS (Form 4 signal)
    - Price stabilizes above capitulation low
    
    Entry: After low holds for 3+ days with insider confirmation
    """
    
    def __init__(self):
        super().__init__("BOTTOMING_REVERSAL", weight=1.3)
        self.drawdown_min = 0.50  # 50% down from highs
        self.volume_spike_min = 10.0  # 10x volume
        self.insider_buy_min = 50000
        
    def analyze(self, ticker: str, data: Dict) -> Dict:
        """Detect bottoming reversal"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")
            
            if len(hist) < 60:
                return self._no_signal("Insufficient data")
            
            # Check drawdown from highs
            high_52w = hist['High'].max()
            current = hist['Close'].iloc[-1]
            drawdown = (high_52w - current) / high_52w
            
            if drawdown < self.drawdown_min:
                return self._no_signal(f"Only {drawdown*100:.0f}% down (need >{self.drawdown_min*100:.0f}%)")
            
            # Find capitulation bar (highest volume in last 30 days)
            last_30 = hist.iloc[-30:]
            cap_idx = last_30['Volume'].idxmax()
            cap_volume = last_30.loc[cap_idx, 'Volume']
            cap_price = last_30.loc[cap_idx, 'Low']
            
            avg_volume = hist['Volume'].mean()
            volume_ratio = cap_volume / avg_volume if avg_volume > 0 else 0
            
            if volume_ratio < self.volume_spike_min:
                return self._no_signal(f"No capitulation ({volume_ratio:.1f}x volume)")
            
            # Check if price holding above capitulation low
            days_since_cap = len(last_30) - last_30.index.get_loc(cap_idx) - 1
            lows_after_cap = hist.iloc[-days_since_cap:]['Low']
            
            if days_since_cap < 3:
                return self._no_signal("Too soon after capitulation")
            
            if lows_after_cap.min() < cap_price * 0.95:
                return self._no_signal("Price broke below capitulation low")
            
            # Check for insider buying AT THE LOWS
            insider_buys = data.get('insider_buys', [])
            recent_significant = [
                b for b in insider_buys 
                if b.get('value', 0) >= self.insider_buy_min
                and (datetime.now() - datetime.fromisoformat(b.get('date', '2020-01-01'))).days <= 30
            ]
            
            if not recent_significant:
                return self._no_signal("No insider buying at lows")
            
            # Calculate confidence
            confidence = min(95, 60 + (volume_ratio / 2) + (drawdown * 50))
            
            reason = f"🔄 BOTTOMING: {drawdown*100:.0f}% down, {volume_ratio:.0f}x capitulation, insider buying"
            
            # Targets based on retracement
            target_50pct = cap_price + (high_52w - cap_price) * 0.50
            target_618pct = cap_price + (high_52w - cap_price) * 0.618
            target_high = high_52w
            
            return {
                'signal': 'BUY',
                'confidence': confidence,
                'reason': reason,
                'entry_price': current,
                'stop_loss': cap_price * 0.95,  # Just below capitulation
                'targets': [target_50pct, target_618pct, target_high],
                'strategy_specific': {
                    'high_52w': high_52w,
                    'capitulation_price': cap_price,
                    'drawdown_pct': drawdown * 100,
                    'volume_ratio': volume_ratio,
                    'days_since_cap': days_since_cap,
                    'insider_buys': recent_significant
                }
            }
            
        except Exception as e:
            return self._no_signal(f"Error: {str(e)}")
    
    def _no_signal(self, reason: str) -> Dict:
        return {
            'signal': 'PASS',
            'confidence': 0,
            'reason': reason,
            'entry_price': 0,
            'stop_loss': 0,
            'targets': [0, 0, 0],
            'strategy_specific': {}
        }


# Export all strategies
ALL_STRATEGIES = [
    SupplyShockStrategy,
    BreakoutConfirmationStrategy,
    BottomingReversalStrategy
]
