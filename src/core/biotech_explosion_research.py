"""
BIOTECH EXPLOSIVE MOVE RESEARCH

Question: How often do biotechs move 200%+ to 20,000%+?
Answer: Let's find out with DATA.
"""

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict

class BiotechExplosionResearch:
    """
    Research: How common are 200%+ biotech moves?
    
    If they're COMMON, we're being too strict.
    If they're RARE, RGC setup is the unicorn.
    """
    
    def __init__(self):
        self.lookback_months = 12
        
    def research_recent_biotech_explosions(self) -> List[Dict]:
        """
        Find all biotechs that moved 200%+ in last 12 months.
        
        THIS TELLS US THE REALITY.
        """
        print("="*80)
        print("🔬 BIOTECH EXPLOSION RESEARCH - LAST 12 MONTHS")
        print("="*80)
        print("Question: How often do biotechs move 200%+ to 20,000%+?")
        print()
        
        # Large universe of biotechs
        biotechs = self._get_biotech_universe()
        
        explosions = []
        
        for i, ticker in enumerate(biotechs, 1):
            try:
                if i % 20 == 0:
                    print(f"[{i}/{len(biotechs)}] Scanned...")
                
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1y')
                
                if hist.empty or len(hist) < 5:
                    continue
                
                # Get low and high over period
                low_12m = hist['Low'].min()
                high_12m = hist['High'].max()
                current = hist['Close'].iloc[-1]
                
                if low_12m == 0:
                    continue
                
                # Calculate move from low to high
                move_pct = ((high_12m - low_12m) / low_12m) * 100
                
                # Only track moves > 100%
                if move_pct > 100:
                    # Find when low and high occurred
                    low_date = hist['Low'].idxmin()
                    high_date = hist['High'].idxmax()
                    
                    # Calculate current position
                    from_high_pct = ((high_12m - current) / high_12m) * 100
                    
                    info = stock.info
                    float_shares = info.get('floatShares', 0)
                    market_cap = info.get('marketCap', 0)
                    
                    explosions.append({
                        'ticker': ticker,
                        'low_12m': low_12m,
                        'high_12m': high_12m,
                        'current': current,
                        'move_pct': move_pct,
                        'from_high_pct': from_high_pct,
                        'low_date': low_date.strftime('%Y-%m-%d'),
                        'high_date': high_date.strftime('%Y-%m-%d'),
                        'float_m': float_shares / 1_000_000 if float_shares else 0,
                        'market_cap_m': market_cap / 1_000_000 if market_cap else 0
                    })
                
            except Exception as e:
                continue
        
        # Sort by move size
        explosions.sort(key=lambda x: x['move_pct'], reverse=True)
        
        return explosions
    
    def _get_biotech_universe(self) -> List[str]:
        """
        Get comprehensive biotech universe.
        """
        return [
            'SRPT', 'NTLA', 'IBRX', 'ETNB', 'ADVM', 'ASMB', 'CVAC', 'SGMO',
            'EDIT', 'CRSP', 'FATE', 'BEAM', 'VERV', 'AKRO', 'GERN', 'OBSV',
            'ARQT', 'XNCR', 'CAPR', 'SWTX', 'KALV', 'RCKT', 'MDGL', 'KRYS',
            'PRTA', 'IMCR', 'CGEM', 'NRIX', 'ANIK', 'ETON', 'HRTX', 'CASI',
            'PGEN', 'RLAY', 'ALEC', 'AVTX', 'BBIO', 'BDTX', 'BTAI', 'CABA',
            'CCCC', 'CHRS', 'CLOV', 'CNTX', 'COYA', 'CTMX', 'CVLT', 'CYCN',
            'DERM', 'ELVN', 'ENSC', 'EVLO', 'FDMT', 'FGEN', 'FHTX', 'GHSI',
            'GMAB', 'GNPX', 'GOSS', 'GTBP', 'HOOK', 'IBIO', 'INAB', 'IONS',
            'KALA', 'KYMR', 'LCTX', 'LEGN', 'LENZ', 'LQDA', 'LRMR', 'LYRA',
            'MASS', 'MCRB', 'MEIP', 'MNOV', 'MRNA', 'MRSN', 'MRUS', 'MYNZ',
            'NAMS', 'NBTX', 'NCNA', 'NKTX', 'NMTC', 'NTRB', 'NUVB', 'NVAX',
            'NVCR', 'NWBO', 'OCGN', 'OCUL', 'OPCH', 'ORIC', 'OSPN', 'PBYI',
            'PCVX', 'PEPG', 'PHIO', 'PLRX', 'PMVP', 'PNTH', 'PRAX', 'PRVB',
            'PTCT', 'PTGX', 'PULM', 'QDEL', 'QLGN', 'QNCX', 'QURE', 'RAPT',
            'RCKT', 'REPL', 'RGNX', 'RNA', 'RNAZ', 'RPTX', 'RSVR', 'RYTM',
            'SAGE', 'SANA', 'SANM', 'SAVA', 'SBPH', 'SDGR', 'SEEL', 'SELB',
            'SEVN', 'SGTX', 'SLNO', 'SMMT', 'SNAL', 'SNCE', 'SNTI', 'SOPH',
            'SPRY', 'SRRK', 'STRO', 'SYRS', 'TALO', 'TARS', 'TBPH', 'TCRT',
            'TERN', 'TFFP', 'TGTX', 'TLIS', 'TLSA', 'TMBR', 'TMCI', 'TRDA',
            'TRVN', 'TYRA', 'VNDA', 'VKTX', 'VRCA', 'VRDN', 'VRTX', 'VTNR',
            'VTVT', 'VXRT', 'WEAV', 'WORX', 'XBIT', 'XENE', 'XERS', 'XFOR',
            'XOMA', 'XRTX', 'XTLB', 'ZCMD', 'ZDGE', 'ZLAB', 'ZNTL', 'ZURA',
            'ZVRA', 'ZYXI', 'ABCL', 'ABEO', 'ABUS', 'ACAD', 'ACIU', 'ADAP',
            'ADIL', 'ADMP', 'ADMS', 'ADRO', 'ADTX', 'ADXN', 'AEMD', 'AEVA',
            'AFMD', 'AGLE', 'AIMD', 'AKBA', 'AKYA', 'ALDX', 'ALEC', 'ALGS',
            'ALIM', 'ALLO', 'ALLK', 'ALNY', 'ALVR', 'ALXO', 'AMAM', 'AMBA',
            'AMPH', 'AMRN', 'AMRX', 'ANAB', 'ANCN', 'ANIP', 'ANIX'
        ]
    
    def analyze_patterns(self, explosions: List[Dict]):
        """
        Analyze common patterns in explosions.
        """
        print("\n" + "="*80)
        print("📊 PATTERN ANALYSIS")
        print("="*80)
        
        if not explosions:
            print("No explosions found")
            return
        
        # Count by magnitude
        count_100_200 = len([x for x in explosions if 100 < x['move_pct'] < 200])
        count_200_500 = len([x for x in explosions if 200 <= x['move_pct'] < 500])
        count_500_1000 = len([x for x in explosions if 500 <= x['move_pct'] < 1000])
        count_1000_5000 = len([x for x in explosions if 1000 <= x['move_pct'] < 5000])
        count_5000_plus = len([x for x in explosions if x['move_pct'] >= 5000])
        
        print(f"\nMOVE DISTRIBUTION (Last 12 Months):")
        print(f"  100-200%:   {count_100_200} biotechs")
        print(f"  200-500%:   {count_200_500} biotechs")
        print(f"  500-1000%:  {count_500_1000} biotechs")
        print(f"  1000-5000%: {count_1000_5000} biotechs")
        print(f"  5000%+:     {count_5000_plus} biotechs (UNICORNS)")
        print(f"\n  TOTAL 100%+: {len(explosions)} biotechs")
        
        # Float analysis
        with_float = [x for x in explosions if x['float_m'] > 0]
        if with_float:
            avg_float = sum(x['float_m'] for x in with_float) / len(with_float)
            print(f"\nAVERAGE FLOAT: {avg_float:.1f}M shares")
            
            small_float = [x for x in with_float if x['float_m'] < 10]
            med_float = [x for x in with_float if 10 <= x['float_m'] < 50]
            large_float = [x for x in with_float if x['float_m'] >= 50]
            
            print(f"  <10M float:  {len(small_float)} ({len(small_float)/len(with_float)*100:.0f}%)")
            print(f"  10-50M:      {len(med_float)} ({len(med_float)/len(with_float)*100:.0f}%)")
            print(f"  50M+:        {len(large_float)} ({len(large_float)/len(with_float)*100:.0f}%)")
        
        print("\n" + "="*80)
        print("THE REALITY:")
        if count_200_500 + count_500_1000 + count_1000_5000 + count_5000_plus > 10:
            print("  200%+ moves are NOT RARE in biotech")
            print("  They happen REGULARLY")
            print("  We're being TOO STRICT with criteria")
        else:
            print("  200%+ moves are RARE")
            print("  Current criteria might be appropriate")
        print("="*80)


if __name__ == '__main__':
    research = BiotechExplosionResearch()
    explosions = research.research_recent_biotech_explosions()
    
    print("\n" + "="*80)
    print(f"🚀 TOP 30 BIOTECH EXPLOSIONS (Last 12 Months)")
    print("="*80)
    
    for i, exp in enumerate(explosions[:30], 1):
        still_running = "🔥 STILL NEAR HIGH" if exp['from_high_pct'] < 20 else ""
        print(f"\n{i}. ${exp['ticker']}: +{exp['move_pct']:.0f}% {still_running}")
        print(f"   Low: ${exp['low_12m']:.2f} ({exp['low_date']}) → High: ${exp['high_12m']:.2f} ({exp['high_date']})")
        print(f"   Current: ${exp['current']:.2f} (Down {exp['from_high_pct']:.0f}% from high)")
        if exp['float_m'] > 0:
            print(f"   Float: {exp['float_m']:.1f}M, Market Cap: ${exp['market_cap_m']:.0f}M")
    
    research.analyze_patterns(explosions)
    
    # Save results
    df = pd.DataFrame(explosions)
    df.to_csv('biotech_explosions_12m.csv', index=False)
    print(f"\n💾 Saved full results to: biotech_explosions_12m.csv")
