"""
CONVERGENCE ENGINE V2 - WEIGHTED Multi-Factor Scoring

KEY LESSON FROM RGC:
Volume/momentum spike AFTER move starts (reactive)
Float/insider exist BEFORE trigger (predictive)

SETUP factors (exist before trigger) = HIGH WEIGHT
REACTIVE factors (confirm move started) = LOW WEIGHT

WEIGHTED SCORING (70 points max):
- Float: 20 pts (28.6%) - SETUP - DOUBLED
- Insider: 20 pts (28.6%) - SETUP - DOUBLED
- Catalyst: 10 pts (14.3%) - SETUP
- Short: 10 pts (14.3%) - SETUP
- Volume: 5 pts (7.1%) - REACTIVE - HALVED
- Momentum: 5 pts (7.1%) - REACTIVE - HALVED

Tier 1 (50-70 pts): HIGHEST CONVICTION
Tier 2 (35-49 pts): STRONG
Tier 3 (20-34 pts): WATCHLIST
Tier 4 (<20 pts): PASS

FLAT-TO-BOOM INTEGRATION (Jan 20, 2026):
Added pattern detector for 3-6 month flat setups with insider buying.
Validated examples: IVF (+30%), IBRX (+52%), ONCY (Director $103K buy)
"""

import yfinance as yf
from typing import List, Dict, Any
from datetime import datetime, timedelta
from flat_to_boom_detector import FlatToBoomDetector, ChaseVsCatchFilter, analyze_ticker_comprehensive

class ConvergenceEngine:
    
    def __init__(self):
        self.master_watchlist = self._load_watchlist()
        self.ftb_detector = FlatToBoomDetector()
        self.chase_filter = ChaseVsCatchFilter()
        
    def _load_watchlist(self) -> List[str]:
        """Load all tickers to score - EXPANDED to 100+ universe"""
        try:
            # Import expanded universe
            import sys
            import os
            sys.path.insert(0, os.path.dirname(__file__))
            from ticker_universe import MASTER_UNIVERSE
            return MASTER_UNIVERSE
        except ImportError:
            # Fallback to original small list if import fails
            tier1 = ['GLSI', 'BTAI', 'PMCB', 'COSM', 'IMNM']
            tier2 = ['HIMS', 'SOUN', 'NVAX', 'SMR', 'BBAI']
            tier3 = ['INTG', 'IPW', 'LVLU', 'UPC']
            tier4 = ['VNDA', 'OCUL', 'RZLT', 'PLX', 'RLMD']
            scanner_finds = ['SNTI', 'VRCA', 'INAB', 'CYCN', 'ONCY']
            
            all_tickers = tier1 + tier2 + tier3 + tier4 + scanner_finds
            return list(set(all_tickers))
    
    def score_float(self, ticker: str) -> dict:
        """
        Score float (20 points max) - DOUBLED WEIGHT
        
        SETUP FACTOR: Float exists before trigger
        
        <1M = 20 pts (RGC-level rare)
        1-5M = 16 pts (explosive)
        5-10M = 12 pts (volatile)
        10-50M = 8 pts (movable)
        50-100M = 4 pts (heavy)
        >100M = 0 pts (tanker)
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            shares_out = info.get('sharesOutstanding', 0)
            float_shares = info.get('floatShares', shares_out)
            
            if float_shares == 0:
                return {'score': 0, 'reason': 'No float data', 'float_m': 0}
            
            float_m = float_shares / 1_000_000
            
            if float_m < 1:
                score = 20
                reason = f"{float_m:.1f}M float - RGC-level RARE"
            elif float_m < 5:
                score = 16
                reason = f"{float_m:.1f}M float - explosive"
            elif float_m < 10:
                score = 12
                reason = f"{float_m:.1f}M float - volatile"
            elif float_m < 50:
                score = 8
                reason = f"{float_m:.1f}M float - movable"
            elif float_m < 100:
                score = 4
                reason = f"{float_m:.1f}M float - heavy"
            else:
                score = 0
                reason = f"{float_m:.1f}M float - tanker"
            
            return {
                'score': score,
                'reason': reason,
                'float_m': float_m
            }
        except Exception as e:
            return {'score': 0, 'reason': 'Data error', 'float_m': 0}
    
    def score_insider_ownership(self, ticker: str) -> dict:
        """
        Score insider ownership (20 points max) - DOUBLED WEIGHT
        
        SETUP FACTOR: Insider ownership exists before trigger
        
        >50% + recent buying = 20 pts (locked up + conviction)
        30-50% + recent buying = 16 pts (strong + buying)
        20-30% + recent buying = 12 pts (solid + buying)
        >50% ownership alone = 10 pts (locked up, waiting for catalyst)
        >20% ownership alone = 8 pts (decent)
        <20% = 0 pts (weak)
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            insider_pct = info.get('heldPercentInsiders', 0) * 100
            
            # Known insider buying from research
            buying_clusters = {
                'GLSI': True,  # CEO $340K+ cluster
                'PMCB': True,  # CEO + Director $128K
                'COSM': True,  # CEO $400K+ monthly
                'IMNM': True,  # CEO $1M+
                'RZLT': True,  # Known cluster
                'PLX': True,   # Known cluster
                'RLMD': True,  # Known cluster
                'SNTI': True,  # 56.8% insider
            }
            
            has_buying = buying_clusters.get(ticker, False)
            
            if insider_pct > 50 and has_buying:
                score = 20
                reason = f"{insider_pct:.1f}% insider + CEO buying - CONVICTION"
            elif insider_pct > 30 and has_buying:
                score = 16
                reason = f"{insider_pct:.1f}% insider + buying - strong"
            elif insider_pct > 20 and has_buying:
                score = 12
                reason = f"{insider_pct:.1f}% insider + buying - solid"
            elif insider_pct > 50:
                score = 10
                reason = f"{insider_pct:.1f}% insider (locked, waiting)"
            elif insider_pct > 20:
                score = 8
                reason = f"{insider_pct:.1f}% insider - decent"
            else:
                score = 0
                reason = f"{insider_pct:.1f}% insider - weak"
            
            return {
                'score': score,
                'reason': reason,
                'insider_pct': insider_pct
            }
        except Exception as e:
            return {'score': 0, 'reason': 'Data error', 'insider_pct': 0}
    
    def score_short_interest(self, ticker: str) -> dict:
        """
        Score short interest (10 points max)
        
        >30% = 10 pts (extreme squeeze)
        20-30% = 8 pts (high squeeze)
        10-20% = 6 pts (moderate)
        5-10% = 4 pts (light)
        <5% = 0 pts (no squeeze)
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            short_pct = info.get('shortPercentOfFloat', 0) * 100
            
            if short_pct > 30:
                score = 10
                reason = f"{short_pct:.1f}% short - EXTREME squeeze"
            elif short_pct > 20:
                score = 8
                reason = f"{short_pct:.1f}% short - high squeeze"
            elif short_pct > 10:
                score = 6
                reason = f"{short_pct:.1f}% short - moderate"
            elif short_pct > 5:
                score = 4
                reason = f"{short_pct:.1f}% short - light"
            else:
                score = 0
                reason = f"{short_pct:.1f}% short - no squeeze"
            
            return {
                'score': score,
                'reason': reason,
                'short_pct': short_pct
            }
        except Exception as e:
            return {'score': 0, 'reason': 'Data error', 'short_pct': 0}
    
    def score_catalyst(self, ticker: str) -> dict:
        """
        Score catalyst (10 points max)
        
        PDUFA <30 days = 10 pts (imminent binary)
        PDUFA 30-90 days = 8 pts (near-term)
        Phase 3 data = 7 pts (high impact)
        sNDA filing = 6 pts (approval path)
        Phase 2 data = 4 pts (earlier)
        No catalyst = 0 pts
        """
        # Known catalysts from research
        catalysts = {
            'OCUL': {'type': 'PDUFA', 'date': '2026-01-28'},
            'VNDA': {'type': 'PDUFA', 'date': '2026-02-21'},
            'BTAI': {'type': 'sNDA', 'date': '2026-03-31'},
            'GLSI': {'type': 'Phase 3', 'date': '2026-03-31'},
            'PMCB': {'type': 'Phase 3', 'date': '2026-06-30'},
            'RZLT': {'type': 'Phase 3', 'date': '2026-06-30'},
        }
        
        if ticker not in catalysts:
            return {'score': 0, 'reason': 'No known catalyst'}
        
        cat = catalysts[ticker]
        cat_date = datetime.strptime(cat['date'], '%Y-%m-%d')
        days_until = (cat_date - datetime.now()).days
        
        if cat['type'] == 'PDUFA':
            if days_until < 30:
                score = 10
                reason = f"PDUFA {cat['date']} - IMMINENT ({days_until}d)"
            else:
                score = 8
                reason = f"PDUFA {cat['date']} ({days_until}d)"
        elif cat['type'] == 'Phase 3':
            score = 7
            reason = f"Phase 3 data {cat['date']} ({days_until}d)"
        elif cat['type'] == 'sNDA':
            score = 6
            reason = f"sNDA {cat['date']} ({days_until}d)"
        else:
            score = 4
            reason = f"{cat['type']} {cat['date']}"
        
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
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1mo')
            
            if hist.empty or len(hist) < 10:
                return {'score': 0, 'reason': 'No data', 'volume_ratio': 0}
            
            avg_vol = hist['Volume'][:-1].mean()
            recent_vol = hist['Volume'].iloc[-1]
            
            if avg_vol == 0:
                return {'score': 0, 'reason': 'No volume', 'volume_ratio': 0}
            
            ratio = recent_vol / avg_vol
            
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
                reason = f"{ratio:.1f}x volume - elevated"
            else:
                score = 0
                reason = f"{ratio:.1f}x volume - normal"
            
            return {
                'score': score,
                'reason': reason,
                'volume_ratio': ratio
            }
        except Exception as e:
            return {'score': 0, 'reason': 'Data error', 'volume_ratio': 0}
    
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
        except Exception as e:
            return {'score': 0, 'reason': 'Data error', 'momentum_pct': 0}
    
    def score_ticker(self, ticker: str) -> dict:
        """
        Score a single ticker across all dimensions.
        Now includes flat-to-boom pattern detection.
        """
        print(f"[Scoring] ${ticker}...", end='', flush=True)
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            
            # Score all dimensions
            float_score = self.score_float(ticker)
            insider_score = self.score_insider_ownership(ticker)
            short_score = self.score_short_interest(ticker)
            catalyst_score = self.score_catalyst(ticker)
            volume_score = self.score_volume(ticker)
            momentum_score = self.score_momentum(ticker)
            
            # Total score (70 max)
            total_score = (
                float_score['score'] +
                insider_score['score'] +
                short_score['score'] +
                catalyst_score['score'] +
                volume_score['score'] +
                momentum_score['score']
            )
            
            # FLAT-TO-BOOM PATTERN CHECK
            # Build insider data from our known buys
            insider_buys = []
            if insider_score.get('insider_pct', 0) > 20:
                # Use existing known buying clusters
                buying_clusters = {
                    'GLSI': [{'role': 'ceo', 'value': 340000, 'days_ago': 7}],
                    'PMCB': [{'role': 'ceo', 'value': 88000, 'days_ago': 15}, 
                             {'role': 'director', 'value': 10000, 'days_ago': 13}],
                    'COSM': [{'role': 'ceo', 'value': 400000, 'days_ago': 30}],
                    'ONCY': [{'role': 'director', 'value': 103770, 'days_ago': 4}],
                }
                insider_buys = buying_clusters.get(ticker, [])
            
            # Build catalyst data
            catalysts = []
            if catalyst_score['score'] > 0:
                known_catalysts = {
                    'OCUL': [{'date': '2026-01-28', 'type': 'PDUFA', 'days_away': 8}],
                    'VNDA': [{'date': '2026-02-21', 'type': 'PDUFA', 'days_away': 32}],
                    'BTAI': [{'date': '2026-03-31', 'type': 'sNDA', 'days_away': 70}],
                    'GLSI': [{'date': '2026-03-31', 'type': 'Phase 3', 'days_away': 70}],
                    'ONCY': [{'date': '2026-03-15', 'type': 'FDA Type C', 'days_away': 54}],
                }
                catalysts = known_catalysts.get(ticker, [])
            
            # Run flat-to-boom detection
            ftb_result = self.ftb_detector.detect(ticker, insider_buys, catalysts)
            
            # Run chase/catch filter
            chase_check = self.chase_filter.is_chasing(ticker)
            
            # Determine if this is a CATCHING opportunity
            is_catching = False
            if ftb_result.get('pattern_detected') and not chase_check.get('is_chasing'):
                catch_check = self.chase_filter.is_catching(
                    ticker,
                    ftb_result['score'],
                    ftb_result['metrics'].get('has_insider_signal', False),
                    ftb_result['metrics'].get('has_catalyst', False)
                )
                is_catching = catch_check.get('is_catching', False)
            
            # Tier classification (with flat-to-boom boost)
            if is_catching:
                tier = "TIER 1 - FLAT-TO-BOOM SETUP ⚡"
            elif total_score >= 50:
                tier = "TIER 1 - HIGHEST CONVICTION"
            elif total_score >= 35:
                tier = "TIER 2 - STRONG"
            elif total_score >= 20:
                tier = "TIER 3 - WATCHLIST"
            else:
                tier = "TIER 4 - PASS"
            
            if chase_check.get('is_chasing'):
                tier += " (⚠️ CHASING - PASS)"
            
            print(f" ✅ {total_score}/70 pts ({tier})")
            
            return {
                'ticker': ticker,
                'price': price,
                'total_score': total_score,
                'tier': tier,
                'float': float_score,
                'insider': insider_score,
                'short': short_score,
                'catalyst': catalyst_score,
                'volume': volume_score,
                'momentum': momentum_score,
                'flat_to_boom': ftb_result,
                'chase_check': chase_check,
                'is_catching': is_catching
            }
        except Exception as e:
            print(f" ❌ Error: {str(e)}")
            return {
                'ticker': ticker,
                'total_score': 0,
                'tier': "ERROR",
                'error': str(e)
            }
    
    def scan_all(self) -> List[dict]:
        """
        Score all watchlist tickers.
        """
        print("\n" + "="*80)
        print("🎯 CONVERGENCE ENGINE V2 - WEIGHTED MULTI-FACTOR SCORING")
        print("="*80)
        print(f"Scanning {len(self.master_watchlist)} tickers...")
        print("\nWEIGHTED SCORING (70 pts max):")
        print("  🎯 SETUP (Predictive): Float 20pts + Insider 20pts + Catalyst 10pts + Short 10pts = 60pts (85.7%)")
        print("  ⚪ REACTIVE (Confirmatory): Volume 5pts + Momentum 5pts = 10pts (14.3%)")
        print()
        
        results = []
        for ticker in sorted(self.master_watchlist):
            result = self.score_ticker(ticker)
            results.append(result)
        
        # Sort by total score descending
        results.sort(key=lambda x: x['total_score'], reverse=True)
        
        return results
    
    def print_results(self, results: List[dict]):
        """
        Print top results with details including flat-to-boom analysis.
        """
        print("\n" + "="*80)
        print("📊 TOP 10 TICKERS")
        print("="*80)
        
        for i, r in enumerate(results[:10], 1):
            print(f"\n{i}. ${r['ticker']}: {r['total_score']}/70 pts - {r['tier']}")
            print(f"   Price: ${r['price']:.2f}")
            print(f"   🎯 Float: {r['float']['score']}/20 - {r['float']['reason']}")
            print(f"   🎯 Insider: {r['insider']['score']}/20 - {r['insider']['reason']}")
            print(f"   📊 Short: {r['short']['score']}/10 - {r['short']['reason']}")
            print(f"   📊 Catalyst: {r['catalyst']['score']}/10 - {r['catalyst']['reason']}")
            print(f"   ⚪ Volume: {r['volume']['score']}/5 - {r['volume']['reason']}")
            print(f"   ⚪ Momentum: {r['momentum']['score']}/5 - {r['momentum']['reason']}")
            
            # Add flat-to-boom analysis
            if r.get('flat_to_boom'):
                ftb = r['flat_to_boom']
                if ftb.get('pattern_detected'):
                    print(f"   ⚡ FLAT-TO-BOOM: {ftb['score']:.1f}/100")
                    metrics = ftb.get('metrics', {})
                    if metrics.get('is_flat'):
                        print(f"      ✓ Flat pattern ({metrics.get('range_pct', 0):.1f}% range)")
                    if metrics.get('is_coiled'):
                        print(f"      ✓ Coiled ({metrics.get('price_position', 0):.1f}% of range)")
                    if metrics.get('has_insider_signal'):
                        print(f"      ✓ Insider buying ({metrics.get('insider_count', 0)} transactions)")
                    if metrics.get('has_catalyst'):
                        print(f"      ✓ Catalyst ({metrics.get('catalyst_count', 0)} upcoming)")
                    if r.get('is_catching'):
                        print(f"      🎯 VERDICT: CATCH (Entry opportunity)")
                    elif r.get('chase_check', {}).get('is_chasing'):
                        print(f"      ⚠️  VERDICT: CHASE (Too late)")
        
        # Distribution stats
        catching = len([r for r in results if r.get('is_catching')])
        tier1 = len([r for r in results if r['total_score'] >= 50])
        tier2 = len([r for r in results if 35 <= r['total_score'] < 50])
        tier3 = len([r for r in results if 20 <= r['total_score'] < 35])
        tier4 = len([r for r in results if r['total_score'] < 20])
        chasing = len([r for r in results if r.get('chase_check', {}).get('is_chasing')])
        
        print("\n" + "="*80)
        print("📈 DISTRIBUTION")
        print("="*80)
        print(f"⚡ Flat-to-Boom Setups: {catching} tickers - CATCH OPPORTUNITY")
        print(f"Tier 1 (50-70 pts): {tier1} tickers - HIGHEST CONVICTION")
        print(f"Tier 2 (35-49 pts): {tier2} tickers - STRONG")
        print(f"Tier 3 (20-34 pts): {tier3} tickers - WATCHLIST")
        print(f"Tier 4 (<20 pts): {tier4} tickers - PASS")
        print(f"⚠️  Chasing: {chasing} tickers - TOO LATE")


if __name__ == '__main__':
    engine = ConvergenceEngine()
    results = engine.scan_all()
    engine.print_results(results)
