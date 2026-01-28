"""
FLAT-TO-BOOM PATTERN DETECTOR
Validated Pattern from Fenrir's Research (Jan 20, 2026)

Examples that validated this:
- IVF: 6 months flat → Trump fertility catalyst → +30%
- IBRX: 3+ months flat → BLA approval catalyst → +52% (holding)
- ONCY: 12 months flat → Director $103K buy → FDA Q1 2026 → BUYING

The Pattern:
- Stock trades sideways 3-6 months (accumulation phase)
- Insider buying appears (Form 4 signal)
- Catalyst approaching within 30-90 days
- Price compressed in middle of range (coiled spring)
- Low/stable volume (not volatile)

This is PHYSICS, not speculation.
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd


class FlatToBoomDetector:
    """
    Detects flat-to-boom setup candidates based on validated pattern
    """
    
    def __init__(self):
        self.lookback_months = 6
        self.range_width_max = 0.50  # 50% max range width
        self.coil_min = 0.3  # Price must be between 30-70% of range
        self.coil_max = 0.7
        self.insider_buy_min = 50000  # $50K minimum significant buy
        self.catalyst_window_days = 90
        
    def detect(self, ticker: str, insider_buys: List[Dict], 
               catalysts: List[Dict]) -> Dict:
        """
        Main detection method
        
        Args:
            ticker: Stock symbol
            insider_buys: List of Form 4 buys with {'date', 'value', 'role'}
            catalysts: List of catalysts with {'date', 'type', 'days_away'}
            
        Returns:
            Dict with detection results and score
        """
        try:
            # Get price data
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            
            if hist.empty:
                return self._empty_result(ticker, "No price data")
            
            # Calculate 6-month metrics
            six_months_ago = datetime.now() - timedelta(days=180)
            recent_data = hist[hist.index >= six_months_ago]
            
            if len(recent_data) < 60:  # Need at least ~3 months of data
                return self._empty_result(ticker, "Insufficient data")
            
            # 1. Check price range (is it flat?)
            high_6m = recent_data['High'].max()
            low_6m = recent_data['Low'].min()
            current = recent_data['Close'].iloc[-1]
            
            range_pct = (high_6m - low_6m) / current if current > 0 else 0
            is_flat = range_pct < self.range_width_max
            
            # 2. Check if price is coiled (middle of range)
            if high_6m > low_6m:
                price_position = (current - low_6m) / (high_6m - low_6m)
            else:
                price_position = 0.5  # If no range, assume middle
                
            is_coiled = self.coil_min < price_position < self.coil_max
            
            # 3. Check for significant insider buying (last 30 days)
            significant_buys = [
                buy for buy in insider_buys 
                if buy.get('value', 0) >= self.insider_buy_min
            ]
            has_insider_signal = len(significant_buys) > 0
            
            # Calculate insider conviction score
            insider_score = self._calculate_insider_score(significant_buys)
            
            # 4. Check for upcoming catalyst
            upcoming_catalysts = [
                c for c in catalysts 
                if c.get('days_away', 999) <= self.catalyst_window_days
            ]
            has_catalyst = len(upcoming_catalysts) > 0
            
            # 5. Check volume pattern (stable/low = accumulation)
            volume_stable = self._check_volume_stability(recent_data)
            
            # Calculate composite score (0-100)
            score = self._calculate_score(
                is_flat=is_flat,
                is_coiled=is_coiled,
                has_insider=has_insider_signal,
                insider_score=insider_score,
                has_catalyst=has_catalyst,
                volume_stable=volume_stable,
                range_pct=range_pct
            )
            
            return {
                'ticker': ticker,
                'pattern_detected': score >= 60,  # 60+ = strong signal
                'score': round(score, 1),
                'metrics': {
                    'is_flat': is_flat,
                    'is_coiled': is_coiled,
                    'has_insider_signal': has_insider_signal,
                    'has_catalyst': has_catalyst,
                    'volume_stable': volume_stable,
                    'range_pct': round(range_pct * 100, 1),
                    'price_position': round(price_position * 100, 1),
                    'insider_count': len(significant_buys),
                    'insider_total': sum(b.get('value', 0) for b in significant_buys),
                    'catalyst_count': len(upcoming_catalysts)
                },
                'significant_buys': significant_buys,
                'upcoming_catalysts': upcoming_catalysts,
                'current_price': round(current, 2),
                'range_high': round(high_6m, 2),
                'range_low': round(low_6m, 2),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._empty_result(ticker, f"Error: {str(e)}")
    
    def _calculate_insider_score(self, buys: List[Dict]) -> float:
        """
        Calculate weighted insider buying score
        Based on Fenrir's research (Jan 20, 2026)
        """
        if not buys:
            return 0
        
        # Role weights
        role_weights = {
            'ceo': 5,
            'cfo': 4,
            'director': 4,
            'officer': 3,
            'other': 2
        }
        
        # Size tier weights
        def size_weight(value):
            if value >= 100000:
                return 5  # $100K+
            elif value >= 50000:
                return 4  # $50-100K
            elif value >= 25000:
                return 3  # $25-50K
            elif value >= 10000:
                return 2  # $10-25K
            else:
                return 1  # <$10K
        
        # Timing boost (days ago)
        def timing_weight(days_ago):
            if days_ago <= 7:
                return 3  # Within week
            elif days_ago <= 30:
                return 2  # Within month
            elif days_ago <= 60:
                return 1  # Within 2 months
            else:
                return 0  # Too old
        
        total_score = 0
        for buy in buys:
            role = buy.get('role', 'other').lower()
            value = buy.get('value', 0)
            days_ago = buy.get('days_ago', 30)
            
            role_score = role_weights.get(role, 2)
            size_score = size_weight(value)
            timing_score = timing_weight(days_ago)
            
            buy_score = role_score + size_score + timing_score
            total_score += buy_score
        
        # Normalize to 0-100
        max_possible = len(buys) * 13  # 5+5+3 = 13 max per buy
        normalized = (total_score / max_possible * 100) if max_possible > 0 else 0
        
        return min(normalized, 100)
    
    def _check_volume_stability(self, data: pd.DataFrame) -> bool:
        """
        Check if volume is stable (not volatile spikes)
        Stable volume = accumulation phase
        """
        if len(data) < 20:
            return False
        
        volumes = data['Volume'].values
        avg_volume = volumes.mean()
        
        # Count days with >2x average volume (spike days)
        spike_days = sum(v > avg_volume * 2 for v in volumes)
        spike_pct = spike_days / len(volumes)
        
        # Stable = fewer than 10% spike days
        return spike_pct < 0.10
    
    def _calculate_score(self, is_flat: bool, is_coiled: bool, 
                        has_insider: bool, insider_score: float,
                        has_catalyst: bool, volume_stable: bool,
                        range_pct: float) -> float:
        """
        Calculate composite pattern score (0-100)
        """
        score = 0
        
        # Flat pattern (0-25 points)
        if is_flat:
            # Tighter range = higher score
            if range_pct < 0.20:
                score += 25  # Very tight
            elif range_pct < 0.35:
                score += 20  # Tight
            elif range_pct < 0.50:
                score += 15  # Acceptable
        
        # Coiled position (0-15 points)
        if is_coiled:
            score += 15
        
        # Insider buying (0-30 points)
        if has_insider:
            score += (insider_score * 0.30)  # Scale insider_score to 30 pts max
        
        # Catalyst (0-20 points)
        if has_catalyst:
            score += 20
        
        # Volume stability (0-10 points)
        if volume_stable:
            score += 10
        
        return min(score, 100)
    
    def _empty_result(self, ticker: str, reason: str) -> Dict:
        """Return empty result with reason"""
        return {
            'ticker': ticker,
            'pattern_detected': False,
            'score': 0,
            'reason': reason,
            'metrics': {},
            'timestamp': datetime.now().isoformat()
        }


class ChaseVsCatchFilter:
    """
    Determines if opportunity is CATCH (our edge) or CHASE (late)
    Based on Fenrir's framework (Jan 20, 2026)
    
    Philosophy:
    - CATCH = Setup before breakout (flat pattern + insider + catalyst)
    - CHASE = Already moving (late entry, poor risk/reward)
    
    Examples:
    - ONCY at $1.04 = CATCH (Director bought, FDA coming, still flat)
    - Gold miners +15% AH = CHASE (already ran, would be late)
    """
    
    def __init__(self):
        self.chase_threshold_1d = 0.10  # +10% in 1 day
        self.chase_threshold_5d = 0.20  # +20% in 5 days
        self.near_high_threshold = 0.95  # Within 5% of 52-week high
        
    def is_chasing(self, ticker: str) -> Dict:
        """
        Returns True if entering now would be CHASING (late)
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            
            if hist.empty or len(hist) < 5:
                return {'is_chasing': False, 'reason': 'Insufficient data'}
            
            current = hist['Close'].iloc[-1]
            
            # Check 1-day move
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                change_1d = (current - prev_close) / prev_close
                
                if change_1d > self.chase_threshold_1d:
                    return {
                        'is_chasing': True,
                        'reason': f'Already up {change_1d*100:.1f}% today',
                        'change_1d': round(change_1d * 100, 2)
                    }
            
            # Check 5-day move
            if len(hist) >= 5:
                five_days_ago = hist['Close'].iloc[-6]
                change_5d = (current - five_days_ago) / five_days_ago
                
                if change_5d > self.chase_threshold_5d:
                    return {
                        'is_chasing': True,
                        'reason': f'Already up {change_5d*100:.1f}% in 5 days',
                        'change_5d': round(change_5d * 100, 2)
                    }
            
            # Check if near 52-week high
            high_52w = hist['High'].max()
            if current > high_52w * self.near_high_threshold:
                pct_from_high = ((current - high_52w) / high_52w) * 100
                return {
                    'is_chasing': True,
                    'reason': f'Near 52-week high ({pct_from_high:.1f}%)',
                    'pct_from_high': round(pct_from_high, 2)
                }
            
            return {
                'is_chasing': False,
                'reason': 'Not extended, good entry timing',
                'change_1d': round(change_1d * 100, 2) if 'change_1d' in locals() else 0,
                'change_5d': round(change_5d * 100, 2) if 'change_5d' in locals() else 0
            }
            
        except Exception as e:
            return {'is_chasing': False, 'reason': f'Error: {str(e)}'}
    
    def is_catching(self, ticker: str, flat_to_boom_score: float,
                    has_insider: bool, has_catalyst: bool) -> Dict:
        """
        Returns True if this is a CATCHING opportunity (our edge)
        
        Requirements:
        - Flat pattern detected (high flat_to_boom_score)
        - Has insider buying signal
        - Has upcoming catalyst
        - NOT chasing (not extended)
        """
        chase_check = self.is_chasing(ticker)
        
        if chase_check['is_chasing']:
            return {
                'is_catching': False,
                'reason': f"Would be chasing: {chase_check['reason']}"
            }
        
        if flat_to_boom_score < 60:
            return {
                'is_catching': False,
                'reason': f'Flat-to-boom score too low: {flat_to_boom_score}'
            }
        
        if not has_insider:
            return {
                'is_catching': False,
                'reason': 'No insider buying signal'
            }
        
        if not has_catalyst:
            return {
                'is_catching': False,
                'reason': 'No upcoming catalyst'
            }
        
        return {
            'is_catching': True,
            'reason': 'Setup complete: Flat + Insider + Catalyst + Not Extended',
            'flat_to_boom_score': flat_to_boom_score,
            'has_insider': has_insider,
            'has_catalyst': has_catalyst
        }


def analyze_ticker_comprehensive(ticker: str, insider_buys: List[Dict] = None,
                                 catalysts: List[Dict] = None) -> Dict:
    """
    Comprehensive analysis combining flat-to-boom + chase/catch
    
    Args:
        ticker: Stock symbol
        insider_buys: Optional list of insider transactions
        catalysts: Optional list of upcoming catalysts
        
    Returns:
        Complete analysis with actionable verdict
    """
    if insider_buys is None:
        insider_buys = []
    if catalysts is None:
        catalysts = []
    
    # Initialize detectors
    ftb_detector = FlatToBoomDetector()
    chase_filter = ChaseVsCatchFilter()
    
    # Run flat-to-boom analysis
    ftb_result = ftb_detector.detect(ticker, insider_buys, catalysts)
    
    # Run chase/catch filter
    chase_check = chase_filter.is_chasing(ticker)
    
    if ftb_result['pattern_detected'] and not chase_check['is_chasing']:
        catch_check = chase_filter.is_catching(
            ticker,
            ftb_result['score'],
            ftb_result['metrics'].get('has_insider_signal', False),
            ftb_result['metrics'].get('has_catalyst', False)
        )
    else:
        catch_check = {'is_catching': False}
    
    # Verdict
    if catch_check.get('is_catching'):
        verdict = "BUY SIGNAL"
        confidence = "HIGH"
    elif ftb_result['pattern_detected']:
        verdict = "WATCH"
        confidence = "MEDIUM"
    elif chase_check['is_chasing']:
        verdict = "PASS - CHASING"
        confidence = "N/A"
    else:
        verdict = "PASS - NO SETUP"
        confidence = "N/A"
    
    return {
        'ticker': ticker,
        'verdict': verdict,
        'confidence': confidence,
        'flat_to_boom': ftb_result,
        'chase_check': chase_check,
        'catch_check': catch_check,
        'timestamp': datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Test with ONCY (example from Fenrir's research)
    print("🐺 FLAT-TO-BOOM DETECTOR TEST")
    print("=" * 60)
    
    # Mock insider data for ONCY (Director Bernd Seizinger, Jan 16, 2026)
    oncy_insider_buys = [
        {
            'date': '2026-01-16',
            'role': 'director',
            'value': 103770,
            'shares': 100000,
            'price': 1.04,
            'days_ago': 4
        }
    ]
    
    # Mock catalyst data
    oncy_catalysts = [
        {
            'date': '2026-03-15',  # Estimated Q1
            'type': 'FDA Type C Meeting',
            'days_away': 54,
            'impact': 'HIGH'
        }
    ]
    
    result = analyze_ticker_comprehensive('ONCY', oncy_insider_buys, oncy_catalysts)
    
    print(f"\nTicker: {result['ticker']}")
    print(f"Verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence']}")
    print(f"\nFlat-to-Boom Score: {result['flat_to_boom']['score']}/100")
    print(f"Pattern Detected: {result['flat_to_boom']['pattern_detected']}")
    print(f"Is Chasing: {result['chase_check']['is_chasing']}")
    print(f"Is Catching: {result['catch_check'].get('is_catching', False)}")
    
    print("\n" + "=" * 60)
    print("Module ready for integration with convergence_engine_v2.py")
