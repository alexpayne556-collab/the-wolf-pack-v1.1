"""
BIOTECH MOONSHOT SCANNER
Find the next RGC (+20,000%) or EVTV (+3,300%) BEFORE they run

WHAT WE'RE LOOKING FOR:
- Biotech/bioscience under $5
- Low float (<50M shares)
- FDA catalyst coming (PDUFA, trial data, BLA)
- Volume starting to spike
- Not already up 200%+

THE PATTERN:
RGC: Low float + regulatory catalyst → 207x
EVTV: AI merger news + government contracts → 33x
IBRX: BLA filing + Saudi approval → 2.5x (still running)

THIS IS HOW WE CATCH THEM EARLY.
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
import json

class BiotechMoonshotScanner:
    """
    Hunt for 10x-100x potential biotech plays BEFORE they run
    """
    
    def __init__(self):
        self.results = []
        
        # Moonshot criteria (different from wounded prey)
        self.criteria = {
            'max_price': 5.0,           # Under $5 = room to run
            'max_float': 50_000_000,    # Low float = explosive moves
            'min_volume': 200_000,      # Need liquidity to enter/exit
            'sectors': ['Biotechnology', 'Healthcare', 'Bioscience'],
        }
    
    def scan_biotech_universe(self) -> List[Dict]:
        """
        Scan ALL biotech stocks under $5 with low float
        """
        print("🔍 SCANNING BIOTECH UNIVERSE FOR MOONSHOTS...")
        
        # Expanded biotech ticker list (need to build comprehensive one)
        biotech_tickers = self._get_biotech_tickers()
        
        candidates = []
        
        for ticker in biotech_tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                price = info.get('currentPrice') or info.get('regularMarketPrice', 999)
                float_shares = info.get('floatShares', 999_999_999)
                avg_volume = info.get('averageVolume10days', 0)
                market_cap = info.get('marketCap', 0)
                
                # Check criteria
                if (price <= self.criteria['max_price'] and 
                    float_shares <= self.criteria['max_float'] and
                    avg_volume >= self.criteria['min_volume']):
                    
                    # Get recent volume spike
                    hist = stock.history(period='5d')
                    if len(hist) >= 2:
                        recent_vol = hist['Volume'].iloc[-1]
                        avg_vol_5d = hist['Volume'].mean()
                        vol_ratio = recent_vol / avg_vol_5d if avg_vol_5d > 0 else 1
                    else:
                        vol_ratio = 1
                    
                    candidates.append({
                        'ticker': ticker,
                        'price': price,
                        'float_m': float_shares / 1_000_000,
                        'volume': avg_volume,
                        'vol_spike': vol_ratio,
                        'mcap_m': market_cap / 1_000_000,
                        'name': info.get('longName', ticker),
                    })
                    
            except Exception as e:
                continue
        
        # Sort by float (smallest first) and volume spike
        candidates.sort(key=lambda x: (x['float_m'], -x['vol_spike']))
        
        self.results = candidates
        return candidates
    
    def check_fda_catalysts(self, tickers: List[str]) -> Dict:
        """
        Check for upcoming FDA catalysts (PDUFA dates, trial readouts)
        
        Real moonshots have BINARY EVENTS ahead
        """
        print("\n📅 CHECKING FDA CATALYST CALENDAR...")
        
        # Note: Need to integrate with FDA calendar API or scrape biopharmcatalyst
        # For now, return structure
        
        catalysts = {}
        
        # TODO: Integrate FDA calendar data
        # Sources:
        # - biopharmcatalyst.com/calendars/fda-calendar
        # - fdatracker.com
        # - SEC filings (8-K for trial results)
        
        return catalysts
    
    def check_insider_activity(self, ticker: str) -> Dict:
        """
        Check recent insider buying (Form 4 filings)
        
        Insiders buying before catalyst = they know something
        """
        # TODO: Integrate SEC EDGAR Form 4 scraping
        # Cluster buying = strong signal
        
        return {}
    
    def calculate_moonshot_score(self, ticker_data: Dict) -> int:
        """
        Score moonshot potential (0-100)
        
        Factors:
        - Low float (smaller = better)
        - Volume spike (bigger = something happening)
        - Price under $3 (more room to run)
        - FDA catalyst ahead (binary event)
        - Insider buying (smart money knows)
        """
        score = 0
        
        # Float score (40 points max)
        float_m = ticker_data['float_m']
        if float_m < 10:
            score += 40
        elif float_m < 20:
            score += 30
        elif float_m < 30:
            score += 20
        elif float_m < 50:
            score += 10
        
        # Volume spike score (30 points max)
        vol_spike = ticker_data['vol_spike']
        if vol_spike >= 5:
            score += 30
        elif vol_spike >= 3:
            score += 20
        elif vol_spike >= 2:
            score += 10
        
        # Price score (20 points max) - lower = more room
        price = ticker_data['price']
        if price < 1:
            score += 20
        elif price < 2:
            score += 15
        elif price < 3:
            score += 10
        elif price < 5:
            score += 5
        
        # TODO: Add catalyst score (10 points)
        # TODO: Add insider score (10 points)
        
        return min(score, 100)
    
    def _get_biotech_tickers(self) -> List[str]:
        """
        Get comprehensive list of biotech tickers
        
        TODO: Expand this massively
        - Scrape NASDAQ biotech list
        - Get from finviz screener
        - Build from SEC filings
        """
        
        # Starter list (need to expand to 1000+)
        return [
            # Current holdings
            'IBRX', 'NTLA', 'SRPT',
            
            # Known biotechs
            'BTAI', 'ADVM', 'SNGX', 'CHRS', 'ALLO', 'FDMT',
            'CRSP', 'EDIT', 'BEAM', 'VERV', 'BLUE', 'SANA',
            'MRNA', 'VRTX', 'IONS', 'ARWR',
            'VNDA', 'DNLI', 'OCGN', 'VXRT', 'ATOS',
            
            # Need 1000+ more
        ]
    
    def generate_report(self) -> str:
        """
        Generate moonshot hunting report
        """
        if not self.results:
            return "No scans run yet"
        
        report = []
        report.append("="*80)
        report.append("🚀 BIOTECH MOONSHOT SCANNER RESULTS")
        report.append("="*80)
        report.append(f"\nScanned: {len(self.results)} candidates")
        report.append(f"Criteria: Under ${self.criteria['max_price']}, Float <{self.criteria['max_float']/1_000_000}M")
        report.append("\nTOP 20 MOONSHOT CANDIDATES:")
        report.append("-"*80)
        report.append(f"{'Ticker':<8} {'Price':<8} {'Float':<12} {'VolSpike':<10} {'Score':<8} {'Name':<30}")
        report.append("-"*80)
        
        for candidate in self.results[:20]:
            score = self.calculate_moonshot_score(candidate)
            candidate['score'] = score
            
            report.append(
                f"{candidate['ticker']:<8} "
                f"${candidate['price']:<7.2f} "
                f"{candidate['float_m']:<11.1f}M "
                f"{candidate['vol_spike']:<9.1f}x "
                f"{score:<8} "
                f"{candidate['name'][:30]:<30}"
            )
        
        # Sort by score for top picks
        self.results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        report.append("\n" + "="*80)
        report.append("🎯 TOP 5 HIGHEST CONVICTION:")
        report.append("="*80)
        
        for i, candidate in enumerate(self.results[:5], 1):
            report.append(f"\n{i}. {candidate['ticker']} - ${candidate['price']:.2f}")
            report.append(f"   Float: {candidate['float_m']:.1f}M shares")
            report.append(f"   Volume spike: {candidate['vol_spike']:.1f}x")
            report.append(f"   Score: {candidate.get('score', 0)}/100")
            report.append(f"   Name: {candidate['name']}")
        
        report.append("\n" + "="*80)
        report.append("⚠️  NEXT STEPS:")
        report.append("="*80)
        report.append("1. Check FDA catalyst calendar for PDUFA dates")
        report.append("2. Review insider buying (Form 4 filings)")
        report.append("3. Look for Phase 3 trial data readouts")
        report.append("4. Watch for volume continuing to spike")
        report.append("5. Enter small positions EARLY, not after 50% run")
        report.append("\n" + "="*80)
        
        return "\n".join(report)

if __name__ == "__main__":
    scanner = BiotechMoonshotScanner()
    
    # Run scan
    print("🐺 HUNTING FOR BIOTECH MOONSHOTS...")
    candidates = scanner.scan_biotech_universe()
    
    # Generate report
    report = scanner.generate_report()
    print(report)
    
    # Save results
    with open('../../data/biotech_moonshots.json', 'w') as f:
        json.dump(scanner.results, f, indent=2)
    
    print("\n✅ Results saved to data/biotech_moonshots.json")
