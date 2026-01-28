"""
RGC SETUP SCANNER - Find Ultra-Low Float Bombs

THE RGC TRUTH:
- Float: 802K shares (0.8M)
- CEO ownership: 86%
- CEO bought 652K shares at $9.50 (Form 4)
- Stock went 235% THAT DAY
- Then ran to $83 (another 500%)

THE DATA WAS PUBLIC. WE JUST WEREN'T LOOKING.

NOW WE'RE LOOKING.
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time

class RGCSetupScanner:
    """
    Finds ultra-low float setups with RGC's DNA.
    
    RGC Setup:
    - Float < 2M shares
    - Insider ownership > 50%
    - Recent insider buying (Form 4)
    - Price < $10
    
    These are the bombs waiting for a trigger.
    """
    
    def __init__(self, expanded=False):
        if expanded:
            # EXPANDED: Catch MORE opportunities
            self.rgc_criteria = {
                'max_float': 10_000_000,     # Under 10M shares (was 2M)
                'min_insider_pct': 20,       # >20% insider ownership (was 50%)
                'max_price': 10.0,           # Under $10
                'min_volume': 50_000,        # Some liquidity
            }
        else:
            # STRICT: True RGC unicorns
            self.rgc_criteria = {
                'max_float': 2_000_000,      # Under 2M shares
                'min_insider_pct': 50,       # >50% insider ownership
                'max_price': 10.0,           # Under $10
                'min_volume': 50_000,        # Some liquidity
            }
        
    def get_scanning_universe(self) -> List[str]:
        """
        Get universe of small caps to scan.
        Focus on: biotechs, micro-caps, recent IPOs.
        """
        # Start with known small biotechs
        universe = [
            # Biotechs
            'SRPT', 'NTLA', 'IBRX', 'ETNB', 'ADVM', 'ASMB', 'CVAC', 'SGMO',
            'EDIT', 'CRSP', 'FATE', 'BEAM', 'VERV', 'AKRO', 'GERN', 'OBSV',
            'ARQT', 'XNCR', 'CAPR', 'SWTX', 'KALV', 'RCKT', 'MDGL', 'KRYS',
            'PRTA', 'IMCR', 'CGEM', 'NRIX', 'ANIK', 'ETON', 'HRTX', 'CASI',
            'PGEN', 'RLAY', 'ALEC', 'AVTX', 'BBIO', 'BDTX', 'BTAI', 'CABA',
            'CCCC', 'CERE', 'CHRS', 'CLOV', 'CNTX', 'COYA', 'CTMX', 'CVLT',
            'CYCN', 'DERM', 'ELVN', 'ENSC', 'EVLO', 'FDMT', 'FGEN', 'FHTX',
            'FWBI', 'GHSI', 'GMAB', 'GNPX', 'GOSS', 'GRPH', 'GTBP', 'HARP',
            'HGEN', 'HLTH', 'HOOK', 'IBIO', 'IGMS', 'IKNA', 'INAB', 'INZY',
            'IONS', 'ITCI', 'ITOS', 'JANX', 'KALA', 'KDNY', 'KYMR', 'LCTX',
            'LEGN', 'LENZ', 'LQDA', 'LRMR', 'LYRA', 'MASS', 'MCRB', 'MEIP',
            'MNOV', 'MRNA', 'MRSN', 'MRTX', 'MRUS', 'MYNZ', 'NAMS', 'NBSE',
            'NBTX', 'NCNA', 'NKTX', 'NMTC', 'NRIX', 'NSTG', 'NTLA', 'NTRB',
            'NUVB', 'NVAX', 'NVCR', 'NVRO', 'NWBO', 'OCGN', 'OCUL', 'OPCH',
            'ORIC', 'ORTX', 'OSPN', 'PBYI', 'PCVX', 'PEPG', 'PHIO', 'PIRS',
            'PLRX', 'PMVP', 'PNTH', 'PRAX', 'PRVB', 'PTCT', 'PTGX', 'PTON',
            'PULM', 'QDEL', 'QLGN', 'QNCX', 'QURE', 'RAPT', 'RCKT', 'REPL',
            'RGNX', 'RNA', 'RNAZ', 'RPTX', 'RSVR', 'RYTM', 'SAGE', 'SANA',
            'SANM', 'SAVA', 'SBPH', 'SDGR', 'SEEL', 'SELB', 'SEVN', 'SGTX',
            'SLNO', 'SMMT', 'SNAL', 'SNCE', 'SNTI', 'SOPH', 'SPRY', 'SRRK',
            'STRO', 'SYRS', 'TALO', 'TARS', 'TBPH', 'TCRT', 'TERN', 'TFFP',
            'TGTX', 'TLIS', 'TLSA', 'TMBR', 'TMCI', 'TORL', 'TPTX', 'TRDA',
            'TRVN', 'TYRA', 'UFCS', 'VNDA', 'VKTX', 'VLON', 'VRCA', 'VRDN',
            'VRNA', 'VRTX', 'VTNR', 'VTVT', 'VXRT', 'WAGON', 'WEAV', 'WORX',
            'XBIT', 'XENE', 'XERS', 'XFOR', 'XLRN', 'XNCR', 'XOMA', 'XRTX',
            'XTLB', 'YMAB', 'YMTX', 'YTHX', 'ZCMD', 'ZDGE', 'ZLAB', 'ZNTL',
            'ZURA', 'ZVRA', 'ZYXI'
        ]
        
        return universe
    
    def scan_for_rgc_setups(self) -> List[Dict[str, Any]]:
        """
        Scan for tickers with RGC's setup RIGHT NOW.
        
        Criteria:
        1. Float < 2M shares
        2. Insider ownership > 50%
        3. Price < $10
        4. Some volume (not dead)
        """
        print("="*80)
        print("🎯 RGC SETUP SCANNER - FINDING ULTRA-LOW FLOAT BOMBS")
        print("="*80)
        print(f"Criteria: Float < {self.rgc_criteria['max_float']/1_000_000:.1f}M, Insider > {self.rgc_criteria['min_insider_pct']}%, Price < ${self.rgc_criteria['max_price']}")
        print()
        
        universe = self.get_scanning_universe()
        matches = []
        
        for i, ticker in enumerate(universe, 1):
            try:
                print(f"[{i}/{len(universe)}] Scanning ${ticker}...", end=' ')
                
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Get key metrics
                price = info.get('currentPrice', info.get('regularMarketPrice', 999))
                float_shares = info.get('floatShares', 999_999_999)
                insider_pct = info.get('heldPercentInsiders', 0) * 100
                volume = info.get('volume', 0)
                market_cap = info.get('marketCap', 0)
                
                # Price check
                if price > self.rgc_criteria['max_price']:
                    print(f"❌ Price ${price:.2f} too high")
                    continue
                
                # Float check (THE CRITICAL ONE)
                if float_shares > self.rgc_criteria['max_float']:
                    print(f"❌ Float {float_shares/1_000_000:.1f}M too high")
                    continue
                
                # Insider ownership check
                if insider_pct < self.rgc_criteria['min_insider_pct']:
                    print(f"❌ Insider {insider_pct:.1f}% too low")
                    continue
                
                # Volume check (needs some liquidity)
                if volume < self.rgc_criteria['min_volume']:
                    print(f"❌ Volume {volume:,} too low")
                    continue
                
                # Calculate RGC similarity score
                score = self._calculate_rgc_similarity(float_shares, insider_pct, price, volume)
                
                print(f"✅ MATCH! Score: {score}/100")
                
                matches.append({
                    'ticker': ticker,
                    'price': price,
                    'float_m': float_shares / 1_000_000,
                    'float_shares': float_shares,
                    'insider_pct': insider_pct,
                    'volume': volume,
                    'market_cap_m': market_cap / 1_000_000,
                    'score': score,
                    'why': self._explain_match(float_shares, insider_pct, price)
                })
                
            except Exception as e:
                print(f"⚠️ Error: {str(e)[:50]}")
                continue
            
            # Rate limit
            time.sleep(0.5)
        
        # Sort by score (highest = most like RGC)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches
    
    def _calculate_rgc_similarity(self, float_shares: int, insider_pct: float, 
                                   price: float, volume: int) -> int:
        """
        Calculate how similar this setup is to RGC's setup.
        
        RGC baseline:
        - Float: 802K (0.8M)
        - Insider: 86%
        - Price: ~$9.50 before trigger
        
        Score 0-100.
        """
        score = 0
        
        # Float score (smaller = better, 50 points max)
        # RGC was 802K
        if float_shares < 1_000_000:  # Under 1M like RGC
            score += 50
        elif float_shares < 1_500_000:  # Under 1.5M
            score += 40
        elif float_shares < 2_000_000:  # Under 2M
            score += 30
        
        # Insider ownership score (30 points max)
        # RGC was 86%
        if insider_pct > 80:
            score += 30
        elif insider_pct > 70:
            score += 25
        elif insider_pct > 60:
            score += 20
        elif insider_pct > 50:
            score += 15
        
        # Price score (10 points max)
        # Lower price = more room to run
        if price < 5:
            score += 10
        elif price < 10:
            score += 5
        
        # Volume score (10 points max)
        # Need enough liquidity to trade
        if volume > 200_000:
            score += 10
        elif volume > 100_000:
            score += 5
        
        return min(score, 100)
    
    def _explain_match(self, float_shares: int, insider_pct: float, price: float) -> str:
        """
        Explain why this matches RGC setup.
        """
        float_m = float_shares / 1_000_000
        
        if float_shares < 1_000_000 and insider_pct > 80:
            return f"ULTRA-LOW float {float_m:.2f}M, insiders control {insider_pct:.1f}% - RGC-like bomb"
        elif float_shares < 1_500_000 and insider_pct > 70:
            return f"Tiny float {float_m:.2f}M, {insider_pct:.1f}% insider - explosive setup"
        else:
            return f"Low float {float_m:.2f}M, {insider_pct:.1f}% insider - waiting for trigger"
    
    def check_recent_form4s(self, ticker: str) -> Dict[str, Any]:
        """
        Check for recent Form 4 insider buying.
        
        This is the TRIGGER we watch for.
        When CEO buys on ultra-low float = RGC replay.
        
        TODO: Integrate with SEC EDGAR API for real-time alerts.
        For now, use OpenInsider.
        """
        print(f"\n🔍 Checking Form 4s for ${ticker}...")
        
        # TODO: Scrape OpenInsider or use SEC EDGAR API
        # For now, placeholder
        print("   ⚠️ TODO: Integrate real-time Form 4 scraping")
        
        return {
            'recent_buying': False,
            'buyers': [],
            'shares_bought': 0,
            'pct_of_float': 0
        }
    
    def print_results(self, matches: List[Dict[str, Any]]):
        """
        Print RGC setup matches.
        """
        print("\n" + "="*80)
        print("📊 RGC SETUPS FOUND - ULTRA-LOW FLOAT BOMBS")
        print("="*80)
        
        if not matches:
            print("\n❌ No matches found with current criteria.")
            print("   Try expanding to float < 5M or insider > 40%")
            return
        
        print(f"\n✅ Found {len(matches)} tickers with RGC-like setup:\n")
        
        for i, m in enumerate(matches, 1):
            print(f"{i}. ${m['ticker']}")
            print(f"   Price: ${m['price']:.2f}")
            print(f"   Float: {m['float_m']:.2f}M shares ({m['float_shares']:,})")
            print(f"   Insider: {m['insider_pct']:.1f}%")
            print(f"   Volume: {m['volume']:,}")
            print(f"   Market Cap: ${m['market_cap_m']:.1f}M")
            print(f"   RGC Similarity: {m['score']}/100")
            print(f"   Why: {m['why']}")
            print()
        
        print("="*80)
        print("🎯 THE RGC TRUTH:")
        print("   SETUP: Visible in data (float, insider %)")
        print("   TRIGGER: Form 4 filing (CEO buying)")
        print("   EXPLOSION: Math (removed % of float)")
        print()
        print("   These tickers have the SETUP.")
        print("   Now we WATCH for the TRIGGER (Form 4).")
        print("="*80)
        
        # Save to file
        df = pd.DataFrame(matches)
        df.to_csv('rgc_setups_current.csv', index=False)
        print(f"\n💾 Saved to: rgc_setups_current.csv")


if __name__ == '__main__':
    import sys
    
    # Check if --expanded flag
    expanded = '--expanded' in sys.argv
    
    if expanded:
        print("\n🎯 RUNNING WITH EXPANDED CRITERIA")
        print("   Float < 10M (vs 2M)")
        print("   Insider > 20% (vs 50%)")
        print("   Price < $10\n")
    
    scanner = RGCSetupScanner(expanded=expanded)
    matches = scanner.scan_for_rgc_setups()
    scanner.print_results(matches)
