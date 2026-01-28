# 🐺 FENRIR V2 - SETUP QUALITY SCORER
# Score every setup 1-100 to prioritize what to look at

from datetime import datetime, timedelta
from typing import Dict, List
import yfinance as yf
import config
try:
    from fenrir.fenrir_memory import get_memory
except ImportError:
    # Graceful fallback if memory module not available
    def get_memory():
        return None

class SetupScorer:
    """Score trading setups on quality 1-100"""
    
    def __init__(self):
        memory = get_memory()
        self.memory = memory if memory else {'stocks': {}}
    
    def score_setup(self, ticker: str, data: Dict) -> Dict:
        """
        Score a setup on multiple factors
        
        Returns:
            {
                'ticker': str,
                'score': int (1-100),
                'factors': dict of individual scores,
                'reasoning': str
            }
        """
        
        scores = {}
        reasoning = []
        
        # Factor 1: Catalyst Strength (0-30 points)
        catalyst_score, catalyst_reason = self._score_catalyst(ticker, data)
        scores['catalyst'] = catalyst_score
        reasoning.append(catalyst_reason)
        
        # Factor 2: Volume Confirmation (0-20 points)
        vol_score, vol_reason = self._score_volume(data)
        scores['volume'] = vol_score
        reasoning.append(vol_reason)
        
        # Factor 3: Price Range Sweet Spot (0-15 points)
        price_score, price_reason = self._score_price_range(data)
        scores['price_range'] = price_score
        reasoning.append(price_reason)
        
        # Factor 4: Days Into Run (0-20 points, negative if extended)
        days_score, days_reason = self._score_run_age(ticker, data)
        scores['run_age'] = days_score
        reasoning.append(days_reason)
        
        # Factor 5: Sector Momentum (0-10 points)
        sector_score, sector_reason = self._score_sector(ticker)
        scores['sector'] = sector_score
        reasoning.append(sector_reason)
        
        # Factor 6: Historical Pattern Match (0-15 points)
        pattern_score, pattern_reason = self._score_pattern_match(ticker)
        scores['pattern'] = pattern_score
        reasoning.append(pattern_reason)
        
        # Factor 7: Extension Risk (-20 to 0 points)
        extension_score, extension_reason = self._score_extension(data)
        scores['extension'] = extension_score
        reasoning.append(extension_reason)
        
        # Factor 8: Our Edge (0-10 points if it's our strong sector)
        edge_score, edge_reason = self._score_our_edge(ticker)
        scores['our_edge'] = edge_score
        reasoning.append(edge_reason)
        
        # Total score
        total = sum(scores.values())
        total = max(0, min(100, total))  # Clamp to 0-100
        
        return {
            'ticker': ticker,
            'score': int(total),
            'factors': scores,
            'reasoning': ' | '.join([r for r in reasoning if r]),
            'grade': self._score_to_grade(total)
        }
    
    def _score_catalyst(self, ticker: str, data: Dict) -> tuple:
        """Score catalyst strength"""
        # Check memory for known catalysts
        stock_history = None
        if isinstance(self.memory, dict):
            stock_history = self.memory.get('stocks', {}).get(ticker)
        elif hasattr(self.memory, 'get_stock_history'):
            stock_history = self.memory.get_stock_history(ticker)
        
        if data.get('has_earnings'):
            return (30, "Strong catalyst: earnings beat")
        elif data.get('has_news'):
            return (20, "Catalyst: fresh news")
        elif stock_history:
            return (15, "Known runner")
        else:
            return (5, "No clear catalyst")
    
    def _score_volume(self, data: Dict) -> tuple:
        """Score volume confirmation"""
        vol_ratio = data.get('volume_ratio', 1)
        
        if vol_ratio >= 3:
            return (20, f"Excellent volume: {vol_ratio:.1f}x")
        elif vol_ratio >= 2:
            return (15, f"Good volume: {vol_ratio:.1f}x")
        elif vol_ratio >= 1.5:
            return (10, f"Decent volume: {vol_ratio:.1f}x")
        else:
            return (0, f"Weak volume: {vol_ratio:.1f}x")
    
    def _score_price_range(self, data: Dict) -> tuple:
        """Score price range - $2-50 is sweet spot"""
        price = data.get('price', 0)
        
        if 2 <= price <= 50:
            return (15, f"Sweet spot: ${price:.2f}")
        elif 50 < price <= 100:
            return (10, f"Higher price: ${price:.2f}")
        elif price < 2:
            return (5, f"Low price: ${price:.2f}")
        else:
            return (0, f"Too expensive: ${price:.2f}")
    
    def _score_run_age(self, ticker: str, data: Dict) -> tuple:
        """Score days into run - early is good, extended is bad"""
        # TODO: Track run start date properly
        # For now, estimate from recent data
        
        change = data.get('change_pct', 0)
        
        if abs(change) >= 15:
            return (20, "Day 1-2 of run")
        elif abs(change) >= 8:
            return (15, "Day 3-5 of run")
        elif abs(change) >= 5:
            return (5, "Day 6-8 of run")
        else:
            return (-10, "Extended/fading")
    
    def _score_sector(self, ticker: str) -> tuple:
        """Score sector momentum"""
        # Find ticker's sector
        sector = None
        watchlist = getattr(config, 'WATCHLIST', {})
        for s, tickers in watchlist.items():
            if ticker in tickers:
                sector = s
                break
        
        if not sector:
            return (0, "")
        
        # Defense and AI are hot sectors
        if sector in ['defense', 'ai_semis']:
            return (10, f"{sector} sector hot")
        else:
            return (5, f"{sector} sector")
    
    def _score_pattern_match(self, ticker: str) -> tuple:
        """Score if similar setups worked before"""
        stock_history = self.memory.get_stock_history(ticker)
        
        if stock_history:
            successes = [h for h in stock_history if 'ran' in h.get('outcome', '').lower()]
            if successes:
                return (15, f"Pattern match: ran before")
        
        return (0, "")
    
    def _score_extension(self, data: Dict) -> tuple:
        """Penalty for being extended"""
        # Check if up huge over short period
        # TODO: Track 5-day performance
        
        change = data.get('change_pct', 0)
        
        if abs(change) >= 50:
            return (-20, "WARNING: Extended +50%")
        elif abs(change) >= 30:
            return (-10, "Extended +30%")
        else:
            return (0, "")
    
    def _score_our_edge(self, ticker: str) -> tuple:
        """Bonus if it's our strong sector"""
        
        # Check memory for our edge
        if isinstance(self.memory, dict):
            notes = self.memory.get('edge')
        elif hasattr(self.memory, 'recall'):
            notes = self.memory.recall('edge')
        else:
            notes = None
        
        holdings = getattr(config, 'HOLDINGS', {})
        if ticker in holdings:
            # We know this stock
            sector = holdings[ticker].get('sector', '')
            if 'defense' in sector.lower():
                return (10, "OUR EDGE: defense")
        
        return (0, "")
    
    def _score_to_grade(self, score: int) -> str:
        """Convert score to grade"""
        if score >= 85:
            return "A+ EXCEPTIONAL"
        elif score >= 75:
            return "A EXCELLENT"
        elif score >= 65:
            return "B GOOD"
        elif score >= 50:
            return "C AVERAGE"
        elif score >= 35:
            return "D WEAK"
        else:
            return "F AVOID"
    
    def score_multiple(self, setups: List[Dict]) -> List[Dict]:
        """Score multiple setups and sort by quality"""
        
        scored = []
        for setup in setups:
            score_result = self.score_setup(setup['ticker'], setup)
            scored.append({**setup, **score_result})
        
        # Sort by score
        scored.sort(key=lambda x: x['score'], reverse=True)
        
        return scored
    
    def format_score_report(self, score_result: Dict) -> str:
        """Format score for display"""
        
        output = f"\n{'='*60}\n"
        output += f"🐺 SETUP QUALITY: {score_result['ticker']}\n"
        output += f"{'='*60}\n\n"
        
        output += f"SCORE: {score_result['score']}/100 ({score_result['grade']})\n\n"
        
        output += "FACTORS:\n"
        for factor, score in score_result['factors'].items():
            emoji = "✅" if score > 0 else "⚠️" if score == 0 else "❌"
            output += f"  {emoji} {factor}: {score:+d}\n"
        
        output += f"\nREASONING:\n  {score_result['reasoning']}\n"
        
        output += f"\n{'='*60}\n"
        
        return output


if __name__ == '__main__':
    scorer = SetupScorer()
    
    # Test on IBRX
    test_data = {
        'price': 5.52,
        'change_pct': 39.7,
        'volume_ratio': 3.5,
        'has_earnings': True,
        'has_news': True
    }
    
    result = scorer.score_setup('IBRX', test_data)
    print(scorer.format_score_report(result))
