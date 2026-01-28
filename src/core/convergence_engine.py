"""
CONVERGENCE ENGINE - Multi-Factor Scoring System

THE CONCEPT:
One advantage = good
Multiple advantages = GREAT
ALL advantages converging = MOONSHOT

Example:
GLSI hits 4/6 scanners = 37/40 score
CYCN hits 2/6 scanners = 10/40 score

The system finds where MULTIPLE signals converge on the SAME ticker.
"""

import yfinance as yf
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd

class ConvergenceEngine:
    """
    Combines ALL scanner signals into unified scoring.
    
    6 Scoring Dimensions:
    1. Float Score (10 pts): Smaller = better
    2. Short Score (10 pts): Higher short = squeeze potential
    3. Insider Score (10 pts): Recent buying = conviction
    4. Catalyst Score (10 pts): Binary event proximity
    5. Volume Score (10 pts): Explosion = attention
    6. Momentum Score (10 pts): Recent price action
    
    MAX SCORE: 60 points
    Tier 1 (45-60 pts): Triple/Quad threat - HIGHEST CONVICTION
    Tier 2 (30-44 pts): Dual threat - STRONG
    Tier 3 (15-29 pts): Single advantage - MONITOR
    """
    
    def __init__(self):
        self.master_watchlist = self._load_watchlist()
        
    def _load_watchlist(self) -> List[str]:
        """Load all tickers to score"""
        # Manual research finds
        tier1 = ['GLSI', 'BTAI', 'PMCB', 'COSM', 'IMNM']
        tier2 = ['HIMS', 'SOUN', 'NVAX', 'SMR', 'BBAI']
        tier3 = ['INTG', 'IPW', 'LVLU', 'UPC']
        tier4 = ['VNDA', 'OCUL', 'RZLT', 'PLX', 'RLMD']
        
        # Our scanner finds
        our_finds = ['SNTI', 'VRCA', 'INAB', 'CYCN']
        
        # Current portfolio
        portfolio = ['AI', 'SRPT', 'NTLA', 'UUUU', 'LUNR', 'INTC']
        
        return tier1 + tier2 + tier3 + tier4 + our_finds + portfolio
    
    def score_float(self, ticker: str, info: Dict) -> Dict[str, Any]:
        """
        Score 1: Float (20 points max) - DOUBLED WEIGHT
        
        SETUP FACTOR: Predicts explosive potential
        
        <1M shares = 20 pts (RGC-level rare)
        1-5M = 16 pts (very small)
        5-10M = 12 pts (small)
        10-50M = 8 pts (moderate)
        50-100M = 4 pts (larger)
        >100M = 0 pts (too big)
        """
        float_shares = info.get('floatShares', 999_999_999)
        float_m = float_shares / 1_000_000
        
        if float_shares < 1_000_000:
            score = 20
            reason = f"{float_shares/1000:.0f}K float - RGC-level rare"
        elif float_shares < 5_000_000:
            score = 16
            reason = f"{float_m:.1f}M float - very small"
        elif float_shares < 10_000_000:
            score = 12
            reason = f"{float_m:.1f}M float - small"
        elif float_shares < 50_000_000:
            score = 8
            reason = f"{float_m:.1f}M float - moderate"
        elif float_shares < 100_000_000:
            score = 4
            reason = f"{float_m:.1f}M float - larger"
        else:
            score = 0
            reason = f"{float_m:.0f}M float - too big"
        
        return {
            'score': score,
            'reason': reason,
            'float_m': float_m
        }
    
    def score_short_interest(self, ticker: str, info: Dict) -> Dict[str, Any]:
        """
        Score 2: Short Interest (10 points max)
        
        >30% = 10 pts (massive squeeze potential)
        20-30% = 8 pts (high squeeze)
        10-20% = 6 pts (moderate squeeze)
        5-10% = 4 pts (some squeeze)
        <5% = 0 pts (no squeeze setup)
        """
        short_pct = info.get('shortPercentOfFloat', 0) * 100
        
        if short_pct > 30:
            score = 10
            reason = f"{short_pct:.1f}% short - massive squeeze potential"
        elif short_pct > 20:
            score = 8
            reason = f"{short_pct:.1f}% short - high squeeze"
        elif short_pct > 10:
            score = 6
            reason = f"{short_pct:.1f}% short - moderate"
        elif short_pct > 5:
            score = 4
            reason = f"{short_pct:.1f}% short - some potential"
        else:
            score = 0
            reason = f"{short_pct:.1f}% short - low"
        
        return {
            'score': score,
            'reason': reason,
            'short_pct': short_pct
        }
    
    def score_insider_ownership(self, ticker: str, info: Dict) -> Dict[str, Any]:
        """
        Score 3: Insider Ownership (20 points max) - DOUBLED WEIGHT
        
        SETUP FACTOR: Predicts conviction and control
        
        >50% + recent buying = 20 pts (RGC-level control)
        30-50% + buying = 16 pts (high insider conviction)
        20-30% + buying = 12 pts (good insider)
        >50% no buying = 10 pts (high ownership, monitoring)
        >20% no buying = 8 pts (monitoring)
        <20% = 0 pts (no insider signal)
        
        TODO: Integrate OpenInsider for "recent buying" detection
        """
        insider_pct = info.get('heldPercentInsiders', 0) * 100
        
        # Known insider buying from research
        recent_buyers = {
            'GLSI': 'CEO $340K+',
            'PMCB': 'CEO + Director $128K',
            'COSM': 'CEO $400K+ monthly',
            'IMNM': 'CEO $1M+',
            'RZLT': 'CEO + CFO',
            'PLX': 'CEO $101K',
            'RLMD': 'CEO + CFO $161K'
        }
        
        has_recent_buying = ticker in recent_buyers
        
        if insider_pct > 50 and has_recent_buying:
            score = 20
            reason = f"{insider_pct:.1f}% insider + {recent_buyers.get(ticker, 'buying')}"
        elif insider_pct > 30 and has_recent_buying:
            score = 16
            reason = f"{insider_pct:.1f}% insider + buying"
        elif insider_pct > 20 and has_recent_buying:
            score = 12
            reason = f"{insider_pct:.1f}% insider + buying"
        elif insider_pct > 50:
            score = 10
            reason = f"{insider_pct:.1f}% insider, no recent buying (RGC-level ownership)"
        elif insider_pct > 20:
            score = 8
            reason = f"{insider_pct:.1f}% insider, no recent buying"
        else:
            score = 0
            reason = f"{insider_pct:.1f}% insider - low"
        
        return {
            'score': score,
            'reason': reason,
            'insider_pct': insider_pct,
            'recent_buying': recent_buyers.get(ticker)
        }
    
    def score_catalyst(self, ticker: str, info: Dict) -> Dict[str, Any]:
        """
        Score 4: Catalyst (10 points max)
        
        FDA PDUFA <30 days = 10 pts (imminent binary)
        FDA PDUFA 30-90 days = 8 pts (near-term)
        Phase 3 readout scheduled = 7 pts
        sNDA/BLA filing = 6 pts
        Phase 2 data = 4 pts
        No catalyst = 0 pts
        """
        # Known catalysts from research
        catalysts = {
            'OCUL': {'type': 'PDUFA', 'date': '2026-01-28', 'days': 9},
            'VNDA': {'type': 'PDUFA', 'date': '2026-02-21', 'days': 33},
            'BTAI': {'type': 'sNDA filing', 'date': '2026-03-31', 'days': 71},
            'GLSI': {'type': 'Phase 3', 'date': 'Q1 2026', 'days': 60},
            'RZLT': {'type': 'Data readout', 'date': '2026-06-30', 'days': 162}
        }
        
        if ticker in catalysts:
            cat = catalysts[ticker]
            days = cat['days']
            
            if days < 30:
                score = 10
                reason = f"{cat['type']} in {days} days - IMMINENT"
            elif days < 90:
                score = 8
                reason = f"{cat['type']} in {days} days - near-term"
            else:
                score = 6
                reason = f"{cat['type']} {cat['date']}"
        else:
            score = 0
            reason = "No known catalyst"
        
        return {
            'score': score,
            'reason': reason
        }
    
    def score_volume(self, ticker: str) -> dict:
        """
        Score volume spike (5 points max) - HALVED WEIGHT
        
        REACTIVE FACTOR: Confirms move already started
        
        >10x avg = 5 pts (explosion - you're late)
        5-10x = 4 pts (major spike)
        3-5x = 3 pts (spike)
        2-3x = 2 pts (elevated)
        <2x = 0 pts (normal)
        """
        avg_volume = info.get('averageVolume', 1)
        current_volume = info.get('volume', 0)
        
        if avg_volume > 0:
            ratio = current_volume / avg_volume
        else:
            ratio = 1.0
        
        if ratio > 10:
            score = 5
            reason = f"{ratio:.1f}x volume - EXPLOSION (late)"
        elif ratio > 5:
            score = 4
            reason = f"{ratio:.1f}x volume - major spike"
        elif ratio > 3:
            score = 3
            reason = f"{ratio:.1f}x volume - spike"
        elif ratio > 2:
            score = 2
            reason = f"{ratio:.1f}x volume - major spike"
        elif ratio > 3:
            score = 6
            reason = f"{ratio:.1f}x volume - spike"
        elif ratio > 2:
            score = 4
            reason = f"{ratio:.1f}x volume - elevated"
        else:
            score = 0
            reason = f"{ratio:.1f}x volume - normal"
        
        return {
            'score': score,
            'reason': reason,
            'volume_ratio': ratio
        }
    
    def score_momentum(self, ticker: str) -> dict:
        """
        Score momentum (5 points max) - HALVED WEIGHT
        
        REACTIVE FACTOR: Confirms move already started
        
        +20%+ in 5 days = 5 pts (running - you're late)
        +10-20% = 4 pts (strong)
        +5-10% = 3 pts (positive)
        0-5% = 2 pts (stable)
        Negative = 0 pts (weak)
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1mo')
        except Exception as e:
            return {'score': 0, 'reason': 'Data error', 'momentum_pct': 0}
        
        if hist.empty or len(hist) < 5:
            return {'score': 0, 'reason': 'No data', 'momentum_pct': 0}
        
        price_5d_ago = hist['Close'].iloc[-5]
        current_price = hist['Close'].iloc[-1]
        
        momentum_pct = ((current_price - price_5d_ago) / price_5d_ago) * 100
        
        if momentum_pct > 20:
            score = 5
            reason = f"+{momentum_pct:.1f}% in 5d - RUNNING (late)"
        elif momentum_pct > 10:
            score = 4
            reason = f"+{momentum_pct:.1f}% in 5d - strong"
        elif momentum_pct > 5:
            score = 3
            reason = f"+{momentum_pct:.1f}% in 5d - positive"
        elif momentum_pct > 0:
            score = 2
            reason = f"+{momentum_pct:.1f}% in 5d - stable"
        else:
            score = 0
            reason = f"{momentum_pct:.1f}% in 5d - weak"
        
        return {
            'score': score,
            'reason': reason,
            'momentum_pct': momentum_pct
        }
    
    def score_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Score ticker across ALL 6 dimensions.
        Return comprehensive multi-factor score.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period='1mo')
            
            # Score all dimensions
            float_score = self.score_float(ticker, info)
            short_score = self.score_short_interest(ticker, info)
            insider_score = self.score_insider_ownership(ticker, info)
            catalyst_score = self.score_catalyst(ticker, info)
            volume_score = self.score_volume(ticker, info)
            momentum_score = self.score_momentum(ticker, info, hist)
            
            # Total score
            total = (
                float_score['score'] +
                short_score['score'] +
                insider_score['score'] +
                catalyst_score['score'] +
                volume_score['score'] +
                momentum_score['score']
            )
            
            # Price
            price = info.get('cur (out of 70 pts now)
            if total >= 50:
                tier = 'TIER 1 - QUAD THREAT'
            elif total >= 35:
                tier = 'TIER 2 - TRIPLE THREAT'
            elif total >= 20:
                tier = 'TIER 2 - TRIPLE THREAT'
            elif total >= 15:
                tier = 'TIER 3 - DUAL THREAT'
            else:
                tier = 'TIER 4 - SINGLE ADVANTAGE'
            
            return {
                'ticker': ticker,
                'price': price,
                'total_score': total,
                'max_score': 70,
                'tier': tier,
                'scores': {
                    'float': float_score,
                    'short': short_score,
                    'insider': insider_score,
                    'catalyst': catalyst_score,
                    'volume': volume_score,
                    'momentum': momentum_score
                }
            }
            
        except Exception as e:
            return {
                'ticker': ticker,
                'error': str(e),
                'total_score': 0
            }
    
    def scan_all(self) -> List[Dict]:
        """
        Score ALL tickers in watchlist.
        Return sorted by total score (highest = best).
        """
        print("="*80)
        print("🎯 CONVERGENCE ENGINE - WEIGHTED MULTI-FACTOR SCORING")
        print("="*80)
        print("SETUP (predict): Float (20), Insider (20), Catalyst (10), Short (10)")
        print("REACTIVE (confirm): Volume (5), Momentum (5)")
        print(f"MAX SCORE: 70 points | Scanning {len(self.master_watchlist)} tickers...\n")
        
        results = []
        
        for i, ticker in enumerate(self.master_watchlist, 1):
            print(f"[{i}/{len(self.master_watchlist)}] Scoring ${ticker}...", end=' ')
            
            result = self.score_ticker(ticker)
            
            if 'error' in result:
                print(f"❌ Error")
            else:7
                print(f"✅ Score: {result['total_score']}/60 ({result['tier']})")
            
            results.append(result)
        
        # Sort by total score
        results.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        
        return results
    
    def print_results(self, results: List[Dict]):
        """
        Print comprehensive multi-factor results.
        """
        print("\n" + "="*80)
        print("📊 CONVERGENCE RESULTS - RANKED BY TOTAL SCORE")
        print("="*80)
        
        # Filter out errors
        valid = [r for r in results if 'error' not in r]
        
        print(f"\n🏆 TOP 10 - HIGHEST MULTI-FACTOR CONVICTION:\n")
        
        for i, result in enumerate(valid[:10], 1):
            scores = result['scores']
            
            print(f"{i}. ${result['ticker']}: {result['total_score']}/70 pts - {result['tier']}")
            print(f"   Price: ${result['price']:.2f}")
            print(f"   🎯 Float: {scores['float']['score']}/20 - {scores['float']['reason']}")
            print(f"   🎯 Insider: {scores['insider']['score']}/20 - {scores['insider']['reason']}")
            print(f"   📊 Catalyst: {scores['catalyst']['score']}/10 - {scores['catalyst']['reason']}")
            print(f"   📊 Short: {scores['short']['score']}/10 - {scores['short']['reason']}")
            print(f"   ⚪ Volume: {scores['volume']['score']}/5 - {scores['volume']['reason']}")
            print(f"   ⚪ Momentum: {scores['momentum']['score']}/5 - {scores['momentum']['reason']}")
            print()
        
        # Stats50])
        tier2 = len([r for r in valid if 35 <= r['total_score'] < 50])
        tier3 = len([r for r in valid if 20 <= r['total_score'] < 35])
        
        print("="*80)
        print("📈 DISTRIBUTION:")
        print(f"   Tier 1 (50-70 pts): {tier1} tickers - QUAD THREAT")
        print(f"   Tier 2 (35-49 pts): {tier2} tickers - TRIPLE THREAT")
        print(f"   Tier 3 (20-34 pts): {tier3} tickers - DUAL THREAT")
        print("="*80)
        print("\n🎯 THE WEIGHTED LOGIC:")
        print("   SETUP (float + insider) = What makes it EXPLOSIVE")
        print("   REACTIVE (volume + momentum) = Tells you you're LATE")
        print("   We catch BEFORE the spike, not after
        print("   ALL advantages converging = MOONSHOT")
        print("="*80)


if __name__ == '__main__':
    engine = ConvergenceEngine()
    results = engine.scan_all()
    engine.print_results(results)
