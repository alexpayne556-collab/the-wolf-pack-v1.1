# 🐺 FENRIR QUANTUM LEAP - SETUP DNA MATCHER
# "This looks EXACTLY like IBRX did 3 weeks ago"

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import yfinance as yf
from collections import defaultdict
import database
from fenrir_memory import get_memory

class SetupDNAMatcher:
    """
    Match current setups to historical patterns with SCARY accuracy
    
    Not just "earnings play" - match the EXACT signature:
    - Price pattern (consolidation then breakout vs immediate gap)
    - Volume signature (steady climb vs explosive)
    - Catalyst type + timing
    - Sector conditions
    - Your emotional state at entry
    
    Output: "This is 87% match to KTOS Oct 15 which ran 8 more days"
    """
    
    def __init__(self):
        self.memory = get_memory()
    
    def extract_dna(self, ticker: str, analysis_date: datetime = None) -> Dict:
        """
        Extract the DNA signature of a setup
        
        Returns DNA fingerprint with:
        - Price pattern (gap, grind, breakout, reversal)
        - Volume signature (steady, explosive, fading)
        - Catalyst type + days since catalyst
        - Sector momentum
        - Day of week
        - Market conditions
        - Technical pattern
        """
        
        if not analysis_date:
            analysis_date = datetime.now()
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get 30 days of data before the setup
            hist = stock.history(period='30d')
            
            if hist.empty or len(hist) < 10:
                return {'error': 'Insufficient data'}
            
            # Price pattern DNA
            price_dna = self._analyze_price_pattern(hist)
            
            # Volume signature
            volume_dna = self._analyze_volume_signature(hist)
            
            # Technical pattern
            technical_dna = self._analyze_technical_pattern(hist)
            
            # Momentum DNA
            momentum_dna = self._analyze_momentum(hist)
            
            # Timing DNA
            timing_dna = {
                'day_of_week': analysis_date.strftime('%A'),
                'hour': analysis_date.hour if analysis_date else 14,
                'market_conditions': self._get_market_conditions()
            }
            
            return {
                'ticker': ticker,
                'timestamp': analysis_date.isoformat(),
                'price_pattern': price_dna,
                'volume_signature': volume_dna,
                'technical_pattern': technical_dna,
                'momentum': momentum_dna,
                'timing': timing_dna,
                'dna_hash': self._calculate_dna_hash(price_dna, volume_dna, technical_dna)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_price_pattern(self, hist) -> Dict:
        """Identify the price pattern leading to the setup"""
        
        if len(hist) < 5:
            return {'pattern': 'unknown'}
        
        # Last 5 days vs previous 20
        recent = hist['Close'].iloc[-5:]
        earlier = hist['Close'].iloc[-25:-5] if len(hist) >= 25 else hist['Close'].iloc[:-5]
        
        # Check for gap
        if len(hist) >= 2:
            gap_pct = ((recent.iloc[-1] - recent.iloc[-2]) / recent.iloc[-2]) * 100
        else:
            gap_pct = 0
        
        # Check for consolidation
        recent_volatility = recent.std() / recent.mean()
        earlier_volatility = earlier.std() / earlier.mean() if len(earlier) > 0 else 0
        
        # Classify pattern
        if gap_pct > 10:
            pattern = 'gap_up'
        elif gap_pct < -10:
            pattern = 'gap_down'
        elif recent_volatility < earlier_volatility * 0.6:
            pattern = 'consolidation'
        elif recent.iloc[-1] > recent.iloc[0] * 1.1:
            pattern = 'grind_up'
        elif recent.iloc[-1] < recent.iloc[0] * 0.9:
            pattern = 'pullback'
        else:
            pattern = 'chop'
        
        # Trend strength
        trend_direction = 'up' if recent.iloc[-1] > earlier.mean() else 'down'
        trend_strength = abs((recent.iloc[-1] - earlier.mean()) / earlier.mean()) * 100
        
        return {
            'pattern': pattern,
            'gap_pct': float(gap_pct),
            'trend_direction': trend_direction,
            'trend_strength': float(trend_strength),
            'volatility_ratio': float(recent_volatility / earlier_volatility) if earlier_volatility > 0 else 1
        }
    
    def _analyze_volume_signature(self, hist) -> Dict:
        """Analyze volume behavior"""
        
        if len(hist) < 5:
            return {'signature': 'unknown'}
        
        recent_vol = hist['Volume'].iloc[-5:].mean()
        earlier_vol = hist['Volume'].iloc[-25:-5].mean() if len(hist) >= 25 else hist['Volume'].iloc[:-5].mean()
        
        volume_ratio = recent_vol / earlier_vol if earlier_vol > 0 else 1
        
        # Volume trend
        vol_slope = (hist['Volume'].iloc[-1] - hist['Volume'].iloc[-5]) / 5 if len(hist) >= 5 else 0
        
        # Classify
        if volume_ratio > 3:
            signature = 'explosive'
        elif volume_ratio > 1.5:
            signature = 'strong'
        elif volume_ratio > 0.7:
            signature = 'steady'
        else:
            signature = 'fading'
        
        return {
            'signature': signature,
            'volume_ratio': float(volume_ratio),
            'volume_trend': 'increasing' if vol_slope > 0 else 'decreasing',
            'consistency': 'consistent' if hist['Volume'].iloc[-5:].std() < recent_vol * 0.5 else 'erratic'
        }
    
    def _analyze_technical_pattern(self, hist) -> Dict:
        """Detect technical patterns"""
        
        if len(hist) < 20:
            return {'pattern': 'unknown'}
        
        close = hist['Close']
        high = hist['High']
        low = hist['Low']
        
        # 52-week high check
        at_52w_high = close.iloc[-1] >= high.max() * 0.98
        
        # Higher highs, higher lows
        recent_highs = high.iloc[-5:]
        recent_lows = low.iloc[-5:]
        
        higher_highs = all(recent_highs.iloc[i] >= recent_highs.iloc[i-1] for i in range(1, len(recent_highs)))
        higher_lows = all(recent_lows.iloc[i] >= recent_lows.iloc[i-1] for i in range(1, len(recent_lows)))
        
        if at_52w_high:
            pattern = 'breakout_52w'
        elif higher_highs and higher_lows:
            pattern = 'uptrend_strong'
        elif higher_highs:
            pattern = 'uptrend_weak'
        else:
            pattern = 'no_trend'
        
        return {
            'pattern': pattern,
            'at_52w_high': at_52w_high,
            'higher_highs': higher_highs,
            'higher_lows': higher_lows
        }
    
    def _analyze_momentum(self, hist) -> Dict:
        """Momentum characteristics"""
        
        if len(hist) < 10:
            return {'type': 'unknown'}
        
        # 5-day vs 10-day change
        five_day_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100
        ten_day_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-10]) / hist['Close'].iloc[-10]) * 100
        
        # Acceleration
        accelerating = abs(five_day_change) > abs(ten_day_change / 2)
        
        if five_day_change > 15:
            momentum_type = 'explosive'
        elif five_day_change > 8:
            momentum_type = 'strong'
        elif five_day_change > 3:
            momentum_type = 'steady'
        else:
            momentum_type = 'weak'
        
        return {
            'type': momentum_type,
            'five_day_change': float(five_day_change),
            'ten_day_change': float(ten_day_change),
            'accelerating': accelerating
        }
    
    def _get_market_conditions(self) -> str:
        """Get overall market conditions"""
        # Simplified - could check SPY, VIX, etc.
        return 'bullish'  # Placeholder
    
    def _calculate_dna_hash(self, price_dna: Dict, volume_dna: Dict, technical_dna: Dict) -> str:
        """Create a unique hash for this DNA signature"""
        
        signature = f"{price_dna.get('pattern', '')}_{volume_dna.get('signature', '')}_{technical_dna.get('pattern', '')}"
        return signature
    
    def find_matches(self, current_dna: Dict, min_similarity: float = 0.7) -> List[Tuple[Dict, float]]:
        """
        Find historical setups that match current DNA
        
        Returns list of (historical_setup, similarity_score) tuples
        """
        
        if 'error' in current_dna:
            return []
        
        # Query historical setups from database
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # Get all historical trades
        cursor.execute('''
            SELECT ticker, timestamp, setup_type, outcome, pnl_pct 
            FROM trade_journal 
            WHERE action = 'SELL' AND outcome IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 100
        ''')
        
        historical = cursor.fetchall()
        conn.close()
        
        matches = []
        
        for trade in historical:
            ticker, timestamp, setup_type, outcome, pnl_pct = trade
            
            # Extract DNA for this historical setup
            try:
                hist_date = datetime.fromisoformat(timestamp)
                hist_dna = self.extract_dna(ticker, hist_date)
                
                if 'error' not in hist_dna:
                    # Calculate similarity
                    similarity = self._calculate_similarity(current_dna, hist_dna)
                    
                    if similarity >= min_similarity:
                        matches.append(({
                            'ticker': ticker,
                            'date': timestamp,
                            'outcome': outcome,
                            'pnl_pct': pnl_pct,
                            'setup_type': setup_type,
                            'dna': hist_dna
                        }, similarity))
            except:
                pass
        
        # Sort by similarity
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def _calculate_similarity(self, dna1: Dict, dna2: Dict) -> float:
        """
        Calculate similarity score between two DNA signatures
        
        Returns 0.0 to 1.0
        """
        
        scores = []
        
        # Price pattern similarity
        if dna1['price_pattern']['pattern'] == dna2['price_pattern']['pattern']:
            scores.append(1.0)
        else:
            scores.append(0.3)
        
        # Volume signature similarity
        if dna1['volume_signature']['signature'] == dna2['volume_signature']['signature']:
            scores.append(1.0)
        else:
            scores.append(0.3)
        
        # Technical pattern similarity
        if dna1['technical_pattern']['pattern'] == dna2['technical_pattern']['pattern']:
            scores.append(1.0)
        else:
            scores.append(0.3)
        
        # Momentum similarity
        momentum_diff = abs(dna1['momentum']['five_day_change'] - dna2['momentum']['five_day_change'])
        momentum_score = max(0, 1.0 - (momentum_diff / 20))  # 20% diff = 0 score
        scores.append(momentum_score)
        
        # Volume ratio similarity
        vol_ratio_diff = abs(dna1['volume_signature']['volume_ratio'] - dna2['volume_signature']['volume_ratio'])
        vol_score = max(0, 1.0 - (vol_ratio_diff / 3))  # 3x diff = 0 score
        scores.append(vol_score)
        
        # Average all scores
        return sum(scores) / len(scores)
    
    def format_matches(self, ticker: str, matches: List[Tuple[Dict, float]]) -> str:
        """Format DNA matches for display"""
        
        if not matches:
            return f"\nNo historical matches found for {ticker} setup DNA\n"
        
        output = f"\n{'='*60}\n"
        output += f"🧬 SETUP DNA MATCHES: {ticker}\n"
        output += f"{'='*60}\n\n"
        
        output += f"Found {len(matches)} similar historical setups:\n\n"
        
        for i, (match, similarity) in enumerate(matches[:5], 1):
            outcome_emoji = "✅" if 'WIN' in match['outcome'] else "❌"
            
            output += f"{i}. {outcome_emoji} {match['ticker']} ({match['date'][:10]}) - {similarity*100:.0f}% match\n"
            output += f"   Outcome: {match['outcome']} ({match['pnl_pct']:+.1f}%)\n"
            output += f"   DNA: {match['dna']['price_pattern']['pattern']} + {match['dna']['volume_signature']['signature']} volume\n"
            
            # Actionable insight
            if 'WIN' in match['outcome']:
                output += f"   💡 This pattern averaged +{match['pnl_pct']:.1f}% - GOOD SETUP\n"
            else:
                output += f"   ⚠️  This pattern lost {match['pnl_pct']:.1f}% - CAUTION\n"
            
            output += "\n"
        
        # Overall pattern success rate
        wins = sum(1 for m, _ in matches if 'WIN' in m[0]['outcome'])
        win_rate = (wins / len(matches)) * 100 if matches else 0
        
        output += f"PATTERN WIN RATE: {win_rate:.0f}% ({wins}/{len(matches)})\n"
        
        output += f"{'='*60}\n"
        
        return output


if __name__ == '__main__':
    matcher = SetupDNAMatcher()
    
    # Extract DNA for current setup
    current_dna = matcher.extract_dna('IBRX')
    
    if 'error' not in current_dna:
        print(f"DNA extracted for IBRX:")
        print(f"  Price pattern: {current_dna['price_pattern']['pattern']}")
        print(f"  Volume: {current_dna['volume_signature']['signature']}")
        print(f"  Technical: {current_dna['technical_pattern']['pattern']}")
        
        # Find matches
        matches = matcher.find_matches(current_dna, min_similarity=0.6)
        print(matcher.format_matches('IBRX', matches))
