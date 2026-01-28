"""
PATTERN EXCAVATOR
Reverse-engineer stocks that moved 200-20,000% in last 6 months

LEARN FROM THE PAST TO PREDICT THE FUTURE

What did RGC look like BEFORE it went 207x?
What did EVTV look like BEFORE it went 33x?
What signals were there that we missed?

This module finds the patterns so we catch the NEXT one.
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
import json

class PatternExcavator:
    """
    Dig through past massive winners to find the patterns
    """
    
    def __init__(self):
        self.winners = []
        self.patterns = {}
    
    def find_massive_gainers(self, lookback_months=6, min_gain_pct=200) -> List[Dict]:
        """
        Find ALL stocks that moved 200%+ in the last 6 months
        
        This is the real work - finding what moved and WHY
        """
        print(f"🔍 SCANNING FOR {min_gain_pct}%+ GAINERS IN LAST {lookback_months} MONTHS...")
        
        # Known massive gainers (need to expand this list)
        known_winners = [
            'RGC',   # +20,746%
            'EVTV',  # +3,233%
            'IBRX',  # +248% (still running)
            # Need to find 100+ more programmatically
        ]
        
        winners = []
        
        for ticker in known_winners:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1y')
                
                if len(hist) < 2:
                    continue
                
                # Get price 6 months ago
                six_months_ago = datetime.now() - timedelta(days=180)
                recent_data = hist[hist.index >= six_months_ago]
                
                if len(recent_data) < 2:
                    continue
                
                start_price = recent_data['Close'].iloc[0]
                high_price = recent_data['High'].max()
                current_price = recent_data['Close'].iloc[-1]
                
                gain_from_start = ((high_price - start_price) / start_price) * 100
                
                if gain_from_start >= min_gain_pct:
                    winners.append({
                        'ticker': ticker,
                        'start_price': start_price,
                        'high_price': high_price,
                        'current_price': current_price,
                        'max_gain_pct': gain_from_start,
                        'timeframe': '6 months',
                    })
                    
            except Exception as e:
                print(f"   Error checking {ticker}: {e}")
                continue
        
        self.winners = winners
        return winners
    
    def analyze_pre_run_characteristics(self, ticker: str) -> Dict:
        """
        Look at what the stock looked like BEFORE it ran
        
        This is the KEY - what were the signals?
        """
        print(f"\n📊 ANALYZING {ticker} PRE-RUN CHARACTERISTICS...")
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period='1y')
            
            # Find the bottom (before the run)
            low_price = hist['Low'].min()
            low_date = hist['Low'].idxmin()
            
            # Get characteristics at the low
            low_period = hist[hist.index <= low_date].tail(30)
            
            if len(low_period) < 2:
                return {}
            
            characteristics = {
                'ticker': ticker,
                'bottom_price': low_price,
                'bottom_date': str(low_date.date()),
                
                # Price characteristics
                'avg_price_at_bottom': low_period['Close'].mean(),
                'was_under_5': low_price < 5.0,
                'was_under_2': low_price < 2.0,
                'was_under_1': low_price < 1.0,
                
                # Volume characteristics  
                'avg_volume_before': low_period['Volume'].mean(),
                'volume_increasing': low_period['Volume'].iloc[-1] > low_period['Volume'].iloc[0],
                
                # Get current info
                'float': info.get('floatShares', 0),
                'float_m': info.get('floatShares', 0) / 1_000_000 if info.get('floatShares') else 0,
                'market_cap_at_bottom': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
            }
            
            return characteristics
            
        except Exception as e:
            print(f"   Error analyzing {ticker}: {e}")
            return {}
    
    def find_catalyst_before_run(self, ticker: str) -> List[str]:
        """
        What was the CATALYST that made it run?
        
        - FDA approval?
        - Merger news?
        - Trial data?
        - Insider buying?
        - Contract award?
        
        This requires digging through news/filings
        """
        print(f"\n🔎 SEARCHING FOR CATALYST ON {ticker}...")
        
        # TODO: Scrape news from:
        # - SEC EDGAR (8-K filings)
        # - Press releases
        # - FDA announcements
        # - Insider trading (Form 4)
        
        catalysts = []
        
        # Placeholder - need to implement news scraping
        catalyst_keywords = [
            'FDA approval',
            'Phase 3 results',
            'Merger',
            'Acquisition',
            'Contract award',
            'Breakthrough therapy',
            'Orphan drug',
            'PDUFA',
            'BLA',
        ]
        
        return catalysts
    
    def extract_common_patterns(self) -> Dict:
        """
        After analyzing multiple winners, what are the COMMON patterns?
        
        This is what we build the scanner around
        """
        print("\n🧠 EXTRACTING COMMON PATTERNS...")
        
        if not self.winners:
            return {}
        
        patterns = {
            'common_characteristics': [],
            'average_float': 0,
            'average_start_price': 0,
            'common_sectors': [],
            'catalyst_types': [],
        }
        
        # Analyze all winners
        all_chars = []
        for winner in self.winners:
            chars = self.analyze_pre_run_characteristics(winner['ticker'])
            if chars:
                all_chars.append(chars)
        
        if not all_chars:
            return patterns
        
        # Find commonalities
        patterns['pct_under_5'] = sum(1 for c in all_chars if c.get('was_under_5')) / len(all_chars) * 100
        patterns['pct_under_2'] = sum(1 for c in all_chars if c.get('was_under_2')) / len(all_chars) * 100
        patterns['pct_under_1'] = sum(1 for c in all_chars if c.get('was_under_1')) / len(all_chars) * 100
        
        patterns['avg_float_m'] = sum(c.get('float_m', 0) for c in all_chars) / len(all_chars)
        
        # Get sectors
        sectors = [c.get('sector') for c in all_chars if c.get('sector')]
        patterns['most_common_sectors'] = list(set(sectors))
        
        self.patterns = patterns
        return patterns
    
    def generate_scanner_rules(self) -> Dict:
        """
        Based on patterns, generate RULES for catching the next one
        
        Output: Criteria to scan for
        """
        print("\n⚙️ GENERATING SCANNER RULES...")
        
        if not self.patterns:
            self.extract_common_patterns()
        
        rules = {
            'price_max': 5.0,  # Most were under $5
            'float_max': self.patterns.get('avg_float_m', 50) * 1.5 * 1_000_000,  # 1.5x average
            'sectors_focus': self.patterns.get('most_common_sectors', []),
            'volume_spike_threshold': 2.0,  # 2x average volume
            'catalysts_to_watch': [
                'FDA PDUFA dates',
                'Phase 3 trial readouts',
                'Merger announcements',
                'Breakthrough therapy designation',
            ],
        }
        
        return rules
    
    def generate_report(self) -> str:
        """
        Full excavation report
        """
        report = []
        report.append("="*80)
        report.append("🔬 PATTERN EXCAVATION REPORT - REVERSE ENGINEERING WINNERS")
        report.append("="*80)
        
        if not self.winners:
            report.append("\n⚠️  No winners analyzed yet. Run find_massive_gainers() first.")
            return "\n".join(report)
        
        report.append(f"\nAnalyzed: {len(self.winners)} massive gainers (200%+ in 6 months)")
        report.append("\n" + "-"*80)
        report.append("WINNERS:")
        report.append("-"*80)
        
        for w in sorted(self.winners, key=lambda x: x['max_gain_pct'], reverse=True):
            report.append(
                f"{w['ticker']:<8} "
                f"${w['start_price']:>7.2f} → ${w['high_price']:>8.2f} "
                f"(+{w['max_gain_pct']:>8.1f}%)"
            )
        
        if self.patterns:
            report.append("\n" + "="*80)
            report.append("COMMON PATTERNS FOUND:")
            report.append("="*80)
            report.append(f"• {self.patterns.get('pct_under_5', 0):.0f}% started under $5")
            report.append(f"• {self.patterns.get('pct_under_2', 0):.0f}% started under $2")
            report.append(f"• Average float: {self.patterns.get('avg_float_m', 0):.1f}M shares")
            report.append(f"• Common sectors: {', '.join(self.patterns.get('most_common_sectors', []))}")
        
        rules = self.generate_scanner_rules()
        report.append("\n" + "="*80)
        report.append("🎯 SCANNER RULES TO CATCH NEXT ONE:")
        report.append("="*80)
        report.append(f"• Scan stocks under: ${rules['price_max']:.2f}")
        report.append(f"• Float under: {rules['float_max']/1_000_000:.1f}M shares")
        report.append(f"• Volume spike over: {rules['volume_spike_threshold']}x average")
        report.append(f"• Watch for catalysts: {', '.join(rules['catalysts_to_watch'])}")
        
        report.append("\n" + "="*80)
        return "\n".join(report)

if __name__ == "__main__":
    excavator = PatternExcavator()
    
    # Find winners
    winners = excavator.find_massive_gainers(lookback_months=6, min_gain_pct=200)
    
    # Analyze each
    for winner in winners:
        excavator.analyze_pre_run_characteristics(winner['ticker'])
    
    # Extract patterns
    excavator.extract_common_patterns()
    
    # Generate report
    print(excavator.generate_report())
    
    # Save
    with open('../../data/pattern_excavation.json', 'w') as f:
        json.dump({
            'winners': excavator.winners,
            'patterns': excavator.patterns,
        }, f, indent=2)
    
    print("\n✅ Analysis saved to data/pattern_excavation.json")
