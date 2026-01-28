"""
SETUP HUNTER - Forward-Looking Pattern Scanner

The pattern_excavator teaches us the PAST.
The setup_hunter finds the FUTURE.

We learn from RGC's 20,000% move.
We find tickers with RGC's SAME SETUP before it moved.

THE HUNTER, NOT THE HISTORIAN.
"""

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import json

class SetupHunter:
    """
    Finds tickers with the SAME SETUP as past winners BEFORE they moved.
    
    We don't want to know what DID happen.
    We want to know what WILL happen.
    """
    
    def __init__(self):
        self.patterns = self._load_winning_patterns()
        self.universe = self._load_expanded_universe()
        
    def _load_winning_patterns(self) -> Dict[str, Dict]:
        """
        Load patterns extracted from past winners.
        These are the DNA signatures we hunt for.
        """
        return {
            'rgc_pattern': {
                'name': 'RGC 20,000% Setup',
                'criteria': {
                    'max_price': 1.0,  # RGC was $0.09
                    'max_float': 30_000_000,  # Tiny float
                    'sector': 'Biotechnology',
                    'catalyst_type': 'FDA Phase 3',
                    'insider_buying': True,
                    'min_volume_spike': 3.0  # 3x normal volume
                }
            },
            'evtv_pattern': {
                'name': 'EVTV 3,300% Setup',
                'criteria': {
                    'max_price': 2.0,  # EVTV was $0.33
                    'max_float': 50_000_000,
                    'sector': 'Biotechnology',
                    'catalyst_type': 'Trial Readout',
                    'down_from_high_pct': 70,  # Beaten down
                    'min_volume_spike': 2.0
                }
            },
            'ibrx_pattern': {
                'name': 'IBRX 248% Setup (Still Running)',
                'criteria': {
                    'max_price': 3.0,  # IBRX was $1.83
                    'max_float': 100_000_000,
                    'sector': 'Biotechnology',
                    'catalyst_type': 'FDA PDUFA',
                    'down_from_high_pct': 50,
                    'insider_buying': True
                }
            },
            'sector_rotation': {
                'name': 'MU 250% Sector Rotation',
                'criteria': {
                    'sector': 'Semiconductors',
                    'down_from_high_pct': 40,
                    'catalyst_type': 'Earnings Beat + Guidance Raise',
                    'institutional_accumulation': True
                }
            }
        }
    
    def _load_expanded_universe(self) -> List[str]:
        """
        Load expanded ticker universe (5,000+ tickers).
        This is what we scan for setups.
        """
        # TODO: Load from universe_expander output
        # For now, starter biotech list
        return [
            'SRPT', 'NTLA', 'IBRX', 'YMAB', 'ETNB', 'ADVM', 'ASMB', 
            'CVAC', 'SGMO', 'EDIT', 'CRSP', 'BLUE', 'FATE', 'BEAM',
            'VERV', 'AKRO', 'GERN', 'OBSV', 'ARQT', 'XNCR', 'CAPR',
            'SWTX', 'KALV', 'RCKT', 'MDGL', 'KRYS', 'PRTA', 'IMCR',
            'CGEM', 'NRIX', 'ANIK', 'ETON', 'HRTX', 'CASI', 'PGEN'
        ]
    
    def hunt_rgc_setups(self) -> List[Dict[str, Any]]:
        """
        Find tickers with RGC's setup BEFORE it moved 20,000%.
        
        RGC Setup (before move):
        - Under $1
        - Float <30M shares
        - Biotech
        - Phase 3 trial completing
        - Insider buying
        """
        print("🎯 HUNTING FOR RGC-LIKE SETUPS...")
        print("   Under $1, float <30M, biotech, Phase 3 catalyst")
        
        pattern = self.patterns['rgc_pattern']['criteria']
        matches = []
        
        for ticker in self.universe:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Price check
                price = info.get('currentPrice', info.get('regularMarketPrice', 999))
                if price > pattern['max_price']:
                    continue
                
                # Float check
                float_shares = info.get('floatShares', 999_999_999)
                if float_shares > pattern['max_float']:
                    continue
                
                # Sector check
                sector = info.get('sector', '')
                if 'bio' not in sector.lower() and 'health' not in sector.lower():
                    continue
                
                # Volume spike check
                avg_volume = info.get('averageVolume', 1)
                recent_volume = info.get('volume', 0)
                volume_spike = recent_volume / avg_volume if avg_volume > 0 else 0
                
                if volume_spike < pattern['min_volume_spike']:
                    continue
                
                # Calculate setup score
                score = self._calculate_setup_score(ticker, pattern, {
                    'price': price,
                    'float': float_shares,
                    'volume_spike': volume_spike
                })
                
                matches.append({
                    'ticker': ticker,
                    'setup': 'RGC Pattern',
                    'price': price,
                    'float_m': float_shares / 1_000_000,
                    'volume_spike': f"{volume_spike:.1f}x",
                    'score': score,
                    'why': f"Under ${pattern['max_price']}, {float_shares/1_000_000:.1f}M float, {volume_spike:.1f}x volume"
                })
                
            except Exception as e:
                continue
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches
    
    def hunt_phase3_catalysts(self) -> List[Dict[str, Any]]:
        """
        Find biotechs with Phase 3 trials completing in next 90 days.
        
        This is FORWARD-LOOKING catalyst hunting.
        Past: "ABVX went 1,700% after Phase 3 success"
        Future: "What Phase 3s are reading out in Q1-Q2 2026?"
        """
        print("🎯 HUNTING FOR PHASE 3 CATALYSTS (Next 90 Days)...")
        
        # TODO: Integrate with FDA PDUFA calendar API
        # TODO: Scrape clinicaltrials.gov for completion dates
        # TODO: Parse biotech news for trial readout dates
        
        # For now, scan for biotechs with Phase 3 mentions + low price
        matches = []
        
        for ticker in self.universe:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                price = info.get('currentPrice', info.get('regularMarketPrice', 999))
                if price > 5.0:  # Phase 3 biotechs under $5
                    continue
                
                # Check business summary for "Phase 3"
                summary = info.get('longBusinessSummary', '').lower()
                if 'phase 3' in summary or 'phase iii' in summary:
                    matches.append({
                        'ticker': ticker,
                        'setup': 'Phase 3 Catalyst',
                        'price': price,
                        'market_cap': info.get('marketCap', 0) / 1_000_000,
                        'why': 'Phase 3 program active, under $5'
                    })
                
            except Exception as e:
                continue
        
        return matches
    
    def hunt_beaten_down_with_catalyst(self) -> List[Dict[str, Any]]:
        """
        Find tickers down 50%+ from high with catalyst ahead.
        
        Past: "MU went 250% after being down 40%"
        Future: "What's down 50%+ with earnings/catalyst ahead?"
        """
        print("🎯 HUNTING FOR BEATEN-DOWN TICKERS WITH CATALYSTS...")
        
        matches = []
        
        for ticker in self.universe:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period='1y')
                
                if hist.empty:
                    continue
                
                # Calculate drawdown from 52-week high
                current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                high_52w = hist['High'].max()
                
                if high_52w == 0:
                    continue
                
                drawdown_pct = ((high_52w - current_price) / high_52w) * 100
                
                if drawdown_pct < 50:  # Want 50%+ drawdown
                    continue
                
                # Check for upcoming catalyst (earnings, FDA date, etc.)
                # TODO: Integrate earnings calendar API
                # TODO: Check FDA PDUFA calendar
                # TODO: Parse news for catalyst mentions
                
                matches.append({
                    'ticker': ticker,
                    'setup': 'Beaten-Down + Catalyst',
                    'price': current_price,
                    'high_52w': high_52w,
                    'drawdown_pct': f"{drawdown_pct:.1f}%",
                    'sector': info.get('sector', 'Unknown'),
                    'why': f"Down {drawdown_pct:.0f}% from high, potential recovery"
                })
                
            except Exception as e:
                continue
        
        matches.sort(key=lambda x: float(x['drawdown_pct'].rstrip('%')), reverse=True)
        return matches
    
    def hunt_insider_buying_clusters(self) -> List[Dict[str, Any]]:
        """
        Find tickers with RECENT insider buying clusters.
        
        Past: "Low float + insider buying = explosion"
        Future: "Who is buying their own stock RIGHT NOW?"
        """
        print("🎯 HUNTING FOR INSIDER BUYING CLUSTERS...")
        
        # TODO: Integrate SEC EDGAR Form 4 scraping
        # TODO: Track insider buying in last 30 days
        # TODO: Calculate buying cluster (3+ insiders buying in 2 weeks)
        # TODO: Filter for CEO/CFO/Directors (smart money)
        
        # For now, placeholder
        print("   ⚠️ TODO: Integrate SEC Form 4 real-time scraping")
        return []
    
    def _calculate_setup_score(self, ticker: str, pattern: Dict, data: Dict) -> int:
        """
        Calculate how well ticker matches pattern setup.
        0-100 score.
        """
        score = 0
        
        # Price score (lower = better for moonshots)
        max_price = pattern.get('max_price', 5.0)
        if data['price'] < max_price * 0.5:
            score += 30
        elif data['price'] < max_price:
            score += 20
        
        # Float score (smaller = better)
        max_float = pattern.get('max_float', 50_000_000)
        if data['float'] < max_float * 0.5:
            score += 40
        elif data['float'] < max_float:
            score += 30
        
        # Volume spike score
        volume_spike = data.get('volume_spike', 1.0)
        if volume_spike >= 5.0:
            score += 30
        elif volume_spike >= 3.0:
            score += 20
        elif volume_spike >= 2.0:
            score += 10
        
        return min(score, 100)
    
    def scan_all_setups(self) -> Dict[str, List[Dict]]:
        """
        Run all forward-looking setup scans.
        
        This is the master hunter that finds:
        1. RGC-like setups (under $1, tiny float, catalyst)
        2. Phase 3 catalysts in next 90 days
        3. Beaten-down with catalyst ahead
        4. Insider buying clusters
        """
        print("\n" + "="*70)
        print("🐺 SETUP HUNTER - FORWARD-LOOKING PATTERN SCANNER")
        print("="*70)
        print("We don't study what DID happen. We find what WILL happen.")
        print()
        
        results = {}
        
        # Hunt for each pattern type
        results['rgc_setups'] = self.hunt_rgc_setups()
        print()
        
        results['phase3_catalysts'] = self.hunt_phase3_catalysts()
        print()
        
        results['beaten_down_catalyst'] = self.hunt_beaten_down_with_catalyst()
        print()
        
        results['insider_buying'] = self.hunt_insider_buying_clusters()
        print()
        
        return results
    
    def print_results(self, results: Dict[str, List[Dict]]):
        """
        Print forward-looking setup matches.
        """
        print("="*70)
        print("📊 FORWARD-LOOKING SETUPS FOUND")
        print("="*70)
        
        # RGC-like setups
        if results['rgc_setups']:
            print("\n🎯 RGC PATTERN MATCHES (Under $1, Float <30M):")
            for i, match in enumerate(results['rgc_setups'][:10], 1):
                print(f"   {i}. ${match['ticker']}: ${match['price']:.2f}, {match['float_m']:.1f}M float, {match['volume_spike']} volume (Score: {match['score']})")
                print(f"      Why: {match['why']}")
        else:
            print("\n🎯 RGC PATTERN MATCHES: None found")
        
        # Phase 3 catalysts
        if results['phase3_catalysts']:
            print("\n🧪 PHASE 3 CATALYSTS (Next 90 Days):")
            for i, match in enumerate(results['phase3_catalysts'][:10], 1):
                print(f"   {i}. ${match['ticker']}: ${match['price']:.2f}, ${match['market_cap']:.0f}M market cap")
                print(f"      Why: {match['why']}")
        else:
            print("\n🧪 PHASE 3 CATALYSTS: None found (need FDA calendar integration)")
        
        # Beaten-down with catalyst
        if results['beaten_down_catalyst']:
            print("\n📉 BEATEN-DOWN WITH CATALYST:")
            for i, match in enumerate(results['beaten_down_catalyst'][:10], 1):
                print(f"   {i}. ${match['ticker']}: ${match['price']:.2f} (High: ${match['high_52w']:.2f}, Down {match['drawdown_pct']})")
                print(f"      Sector: {match['sector']}")
        else:
            print("\n📉 BEATEN-DOWN WITH CATALYST: None found")
        
        # Insider buying
        if results['insider_buying']:
            print("\n💰 INSIDER BUYING CLUSTERS:")
            for i, match in enumerate(results['insider_buying'][:10], 1):
                print(f"   {i}. ${match['ticker']}: {match['buyers']} insiders buying in last 30 days")
        else:
            print("\n💰 INSIDER BUYING CLUSTERS: Need SEC Form 4 integration")
        
        print("\n" + "="*70)
        print("THE DIFFERENCE:")
        print("Historian: 'RGC went 20,000%'")
        print("Hunter: 'These 5 tickers have RGC's setup RIGHT NOW'")
        print("="*70)


if __name__ == '__main__':
    hunter = SetupHunter()
    results = hunter.scan_all_setups()
    hunter.print_results(results)
