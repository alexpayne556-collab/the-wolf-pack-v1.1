#!/usr/bin/env python3
"""
OVERNIGHT SCAN - Ready for Market Open 🐺🌙

RUNS: 11pm every night
READY: 6am for you to review
WHAT IT DOES: Scans wounded prey + scores them for tomorrow

THE WOLF HUNTS WHILE YOU SLEEP.
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict
import yfinance as yf

# Add parent paths
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.core.wolf_mind import WolfMind

class OvernightScanner:
    """
    Nightly scan that:
    1. Loads wounded prey universe
    2. Gets current prices + basic signals
    3. Scores through Wolf Mind (YOUR context)
    4. Outputs top 10 for morning
    """
    
    def __init__(self):
        self.wolf_mind = WolfMind()
        self.universe_file = 'data/wounded_prey_universe.json'
        self.output_file = 'data/morning_opportunities.json'
    
    def load_wounded_prey(self) -> List[Dict]:
        """Load wounded prey universe"""
        if not os.path.exists(self.universe_file):
            print(f"❌ No wounded prey universe found. Run universe_scanner.py first.")
            return []
        
        with open(self.universe_file, 'r') as f:
            data = json.load(f)
        
        wounded = data.get('wounded_prey', [])
        print(f"✅ Loaded {len(wounded)} wounded prey")
        
        return wounded
    
    def score_ticker(self, ticker: str, wounded_score: int) -> Dict:
        """
        Score ticker for trading opportunity
        
        Args:
            ticker: Stock ticker
            wounded_score: How wounded it is (0-100)
            
        Returns:
            Dict with score and reasoning
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='5d')
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            # Calculate basic signals
            volume_5d_avg = hist['Volume'].mean()
            volume_today = hist['Volume'].iloc[-1]
            volume_ratio = volume_today / volume_5d_avg if volume_5d_avg > 0 else 1.0
            
            price_5d_ago = hist['Close'].iloc[0]
            price_change_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
            
            # Base score = wounded score + volume spike + momentum
            base_score = wounded_score
            
            # Volume spike bonus
            if volume_ratio > 2.0:
                base_score += 10
            elif volume_ratio > 1.5:
                base_score += 5
            
            # Bounce from bottom bonus
            if -10 < price_change_5d < 0:
                base_score += 5  # Consolidating
            elif 0 < price_change_5d < 10:
                base_score += 10  # Bouncing
            elif price_change_5d > 10:
                base_score += 15  # Strong bounce
            
            base_score = min(base_score, 100)
            
            # Filter through Wolf Mind
            should_trade, reasoning, adjusted_score = self.wolf_mind.analyze_opportunity(
                ticker=ticker,
                base_score=base_score,
                setup_type='wounded_prey_bounce',
                catalyst=f"{volume_ratio:.1f}x volume, {price_change_5d:+.1f}% 5-day"
            )
            
            return {
                'ticker': ticker,
                'base_score': base_score,
                'adjusted_score': adjusted_score,
                'should_trade': should_trade,
                'price': round(current_price, 2),
                'volume_ratio': round(volume_ratio, 2),
                'price_change_5d': round(price_change_5d, 1),
                'reasoning': reasoning[:200],  # First 200 chars
                'scanned_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"   ❌ {ticker}: {str(e)[:50]}")
            return None
    
    def run_overnight_scan(self):
        """Run complete overnight scan"""
        print("="*70)
        print("🐺 OVERNIGHT SCAN")
        print("="*70)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
        
        # Load wounded prey
        wounded_prey = self.load_wounded_prey()
        
        if not wounded_prey:
            print("❌ No wounded prey to scan")
            return
        
        # Score each ticker
        print(f"\n🔍 Scoring {len(wounded_prey)} tickers...")
        
        opportunities = []
        for i, prey in enumerate(wounded_prey, 1):
            ticker = prey['ticker']
            wounded_score = prey['wounded_score']
            
            if i % 5 == 0:
                print(f"   Progress: {i}/{len(wounded_prey)}")
            
            result = self.score_ticker(ticker, wounded_score)
            if result:
                opportunities.append(result)
        
        # Sort by adjusted score (through Wolf Mind lens)
        opportunities.sort(key=lambda x: x['adjusted_score'], reverse=True)
        
        # Save top opportunities
        os.makedirs('data', exist_ok=True)
        with open(self.output_file, 'w') as f:
            json.dump({
                'scan_date': datetime.now().isoformat(),
                'opportunities': opportunities,
                'trader': self.wolf_mind.profile.name
            }, f, indent=2)
        
        print(f"\n💾 Saved {len(opportunities)} opportunities to {self.output_file}")
        
        # Print top 10
        print("\n" + "="*70)
        print("📊 TOP 10 OPPORTUNITIES FOR TOMORROW:")
        print("="*70)
        
        for i, opp in enumerate(opportunities[:10], 1):
            status = "✅ TRADE" if opp['should_trade'] else "⚠️  FILTERED"
            print(f"\n{i}. {opp['ticker']} - Adjusted Score: {opp['adjusted_score']}/100 (base: {opp['base_score']})")
            print(f"   {status}")
            print(f"   Price: ${opp['price']:.2f} | Volume: {opp['volume_ratio']:.1f}x | 5d: {opp['price_change_5d']:+.1f}%")
            print(f"   {opp['reasoning'][:120]}...")
        
        print("\n" + "="*70)
        print(f"✅ OVERNIGHT SCAN COMPLETE")
        print(f"   Total scanned: {len(wounded_prey)}")
        print(f"   Opportunities found: {len(opportunities)}")
        print(f"   Recommended for YOU: {sum(1 for o in opportunities if o['should_trade'])}")
        print("="*70)
        
        return opportunities


def main():
    """Run overnight scan"""
    scanner = OvernightScanner()
    scanner.run_overnight_scan()


if __name__ == "__main__":
    main()
