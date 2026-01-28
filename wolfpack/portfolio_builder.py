#!/usr/bin/env python3
"""
PORTFOLIO BUILDER - Spreads Our Wings 🐺🦅

THE PROBLEM: 
- System finds 5-10 opportunities
- But only trades 1-2 (conservative)
- Result: Tiny portfolio, missed opportunities

THE SOLUTION:
- Build 10-15 position portfolio DAILY
- Diversify across sectors, market caps
- Pre-market scan → Order queue → Execute at open
- Dynamic allocation (confidence-based)

THE WOLF PACK DOESN'T HUNT ONE PREY. THE PACK SPREADS OUT.
"""

import os
import sys
from datetime import datetime, time
from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import defaultdict
import json

@dataclass
class PortfolioPosition:
    """Single position in target portfolio"""
    ticker: str
    sector: str
    market_cap: str  # 'mega', 'large', 'mid', 'small', 'micro'
    convergence_score: int
    allocation_pct: float  # % of portfolio (0.05 = 5%)
    shares: int
    entry_price: float
    reasoning: str
    confidence: str  # 'HIGH', 'MEDIUM', 'LOW'
    
class PortfolioBuilder:
    """
    Builds diversified portfolio from scan results
    
    INTELLIGENCE:
    - Sector limits (no more than 30% in one sector)
    - Market cap diversity (mix of sizes)
    - Confidence weighting (high conviction = bigger size)
    - Position limits (10-15 positions max)
    - Portfolio balance (not all tech, not all small caps)
    """
    
    def __init__(self, 
                 target_positions: int = 12,
                 max_sector_allocation: float = 0.30,  # 30% max per sector
                 max_position_size: float = 0.12,      # 12% max per position
                 min_position_size: float = 0.05):     # 5% min per position
        """
        Initialize portfolio builder
        
        Args:
            target_positions: Target number of positions (default 12)
            max_sector_allocation: Max % in one sector (default 30%)
            max_position_size: Max % per position (default 12%)
            min_position_size: Min % per position (default 5%)
        """
        self.target_positions = target_positions
        self.max_sector_allocation = max_sector_allocation
        self.max_position_size = max_position_size
        self.min_position_size = min_position_size
        
        # Sector mapping
        self.sector_map = {
            # AI & Tech
            'NVDA': 'AI/Semiconductors', 'AMD': 'AI/Semiconductors', 'AVGO': 'AI/Semiconductors',
            'MSFT': 'AI/Cloud', 'GOOGL': 'AI/Cloud', 'META': 'AI/Cloud',
            'PLTR': 'AI/Software', 'ARM': 'AI/Semiconductors', 'SMCI': 'AI/Hardware',
            
            # Semiconductors
            'TSM': 'Semiconductors', 'INTC': 'Semiconductors', 'QCOM': 'Semiconductors',
            'AMAT': 'Semiconductors', 'ASML': 'Semiconductors',
            
            # Quantum
            'IONQ': 'Quantum', 'RGTI': 'Quantum', 'QBTS': 'Quantum',
            
            # Biotech
            'MRNA': 'Biotech', 'BNTX': 'Biotech', 'GILD': 'Biotech',
            'VRTX': 'Biotech', 'CRSP': 'Biotech', 'IBRX': 'Biotech',
            
            # Defense/Aerospace
            'LMT': 'Defense', 'RTX': 'Defense', 'NOC': 'Defense',
            'BA': 'Defense', 'KTOS': 'Defense', 'ASTS': 'Space', 'RKLB': 'Space',
            
            # Uranium/Energy
            'UUUU': 'Uranium', 'UEC': 'Uranium', 'CCJ': 'Uranium', 'DNN': 'Uranium',
            
            # Crypto/Mining
            'MARA': 'Crypto', 'RIOT': 'Crypto', 'CLSK': 'Crypto', 'COIN': 'Crypto',
            
            # Space
            'LUNR': 'Space', 'PL': 'Space',
            
            # Cloud/SaaS
            'SNOW': 'Cloud', 'DDOG': 'Cloud', 'NET': 'Cloud', 'CRWD': 'Cybersecurity',
            
            # Consumer
            'AAPL': 'Consumer Tech', 'TSLA': 'Consumer Tech'
        }
        
        # Market cap tiers (approximate, update as needed)
        self.market_cap_tiers = {
            'mega': ['NVDA', 'MSFT', 'GOOGL', 'META', 'AAPL', 'TSLA', 'AMD', 'AVGO', 'TSM'],
            'large': ['PLTR', 'CRWD', 'SNOW', 'COIN', 'ARM', 'ASML', 'GILD', 'VRTX', 'LMT', 'RTX', 'NOC', 'BA'],
            'mid': ['SMCI', 'DDOG', 'NET', 'MRNA', 'BNTX', 'INTC', 'QCOM', 'AMAT', 'CRSP'],
            'small': ['MARA', 'RIOT', 'CLSK', 'CCJ', 'KTOS', 'RKLB', 'ASTS', 'LUNR', 'PL'],
            'micro': ['IONQ', 'RGTI', 'QBTS', 'IBRX', 'UUUU', 'UEC', 'DNN']
        }
        
    def get_sector(self, ticker: str) -> str:
        """Get sector for ticker"""
        return self.sector_map.get(ticker, 'Other')
    
    def get_market_cap_tier(self, ticker: str) -> str:
        """Get market cap tier for ticker"""
        for tier, tickers in self.market_cap_tiers.items():
            if ticker in tickers:
                return tier
        return 'unknown'
    
    def build_portfolio(self, 
                       scan_results: List[Dict],
                       account_value: float = 100000.0) -> List[PortfolioPosition]:
        """
        Build diversified portfolio from scan results
        
        Args:
            scan_results: List of opportunities from wolf_pack.py scan
                Format: [{'ticker': 'NVDA', 'score': 95, 'price': 450.0, ...}, ...]
            account_value: Total account value for position sizing
            
        Returns:
            List of PortfolioPosition objects
        """
        print("\n" + "="*70)
        print("🏗️  BUILDING PORTFOLIO")
        print("="*70)
        print(f"Scan results: {len(scan_results)} opportunities")
        print(f"Target positions: {self.target_positions}")
        print(f"Account value: ${account_value:,.2f}")
        
        # Filter and sort by score
        opportunities = sorted(scan_results, key=lambda x: x.get('score', 0), reverse=True)
        
        # Track sector allocations
        sector_allocations = defaultdict(float)
        market_cap_allocations = defaultdict(float)
        
        # Build portfolio
        portfolio = []
        
        for opp in opportunities:
            if len(portfolio) >= self.target_positions:
                break
                
            ticker = opp['ticker']
            score = opp.get('score', 0)
            price = opp.get('price', 0)
            
            # Get sector and market cap
            sector = self.get_sector(ticker)
            market_cap = self.get_market_cap_tier(ticker)
            
            # Check sector limits
            if sector_allocations[sector] >= self.max_sector_allocation:
                print(f"   ⚠️  {ticker} skipped: {sector} at max allocation ({self.max_sector_allocation*100:.0f}%)")
                continue
            
            # Calculate position size based on confidence
            confidence = self._get_confidence(score)
            allocation_pct = self._calculate_allocation(score, confidence, len(portfolio))
            
            # Check if allocation is valid
            if allocation_pct < self.min_position_size:
                print(f"   ⚠️  {ticker} skipped: allocation too small ({allocation_pct*100:.1f}%)")
                continue
            if allocation_pct > self.max_position_size:
                allocation_pct = self.max_position_size
            
            # Calculate shares
            position_value = account_value * allocation_pct
            shares = int(position_value / price) if price > 0 else 0
            
            if shares < 1:
                print(f"   ⚠️  {ticker} skipped: not enough capital for 1 share")
                continue
            
            # Add to portfolio
            position = PortfolioPosition(
                ticker=ticker,
                sector=sector,
                market_cap=market_cap,
                convergence_score=score,
                allocation_pct=allocation_pct,
                shares=shares,
                entry_price=price,
                reasoning=opp.get('reasoning', 'Convergence detected'),
                confidence=confidence
            )
            
            portfolio.append(position)
            sector_allocations[sector] += allocation_pct
            market_cap_allocations[market_cap] += allocation_pct
            
            print(f"   ✅ {ticker}: {allocation_pct*100:.1f}% ({shares} shares @ ${price:.2f}) - {confidence} confidence")
        
        # Report
        print(f"\n📊 PORTFOLIO BUILT: {len(portfolio)} positions")
        print(f"\nSector breakdown:")
        for sector, alloc in sorted(sector_allocations.items(), key=lambda x: x[1], reverse=True):
            print(f"   {sector}: {alloc*100:.1f}%")
        
        print(f"\nMarket cap breakdown:")
        for tier, alloc in sorted(market_cap_allocations.items(), key=lambda x: x[1], reverse=True):
            print(f"   {tier.capitalize()}: {alloc*100:.1f}%")
        
        total_allocation = sum(p.allocation_pct for p in portfolio)
        print(f"\n💰 Total allocation: {total_allocation*100:.1f}%")
        
        return portfolio
    
    def _get_confidence(self, score: int) -> str:
        """Map convergence score to confidence level"""
        if score >= 90:
            return 'HIGH'
        elif score >= 75:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_allocation(self, score: int, confidence: str, current_positions: int) -> float:
        """
        Calculate position allocation based on confidence and score
        
        Higher confidence = bigger size
        More positions filled = smaller remaining sizes
        """
        # Base allocation
        if confidence == 'HIGH':
            base_alloc = 0.10  # 10%
        elif confidence == 'MEDIUM':
            base_alloc = 0.07  # 7%
        else:
            base_alloc = 0.05  # 5%
        
        # Adjust for score within confidence tier
        score_multiplier = 1.0 + ((score - 70) / 100.0)  # 70-100 score range
        
        # Reduce as portfolio fills up
        slots_remaining = self.target_positions - current_positions
        if slots_remaining <= 3:
            reduction = 0.8  # Reduce last few positions
        else:
            reduction = 1.0
        
        allocation = base_alloc * score_multiplier * reduction
        
        # Clamp to limits
        return max(self.min_position_size, min(self.max_position_size, allocation))
    
    def export_to_trader(self, portfolio: List[PortfolioPosition], output_file: str = 'portfolio_orders.json'):
        """
        Export portfolio to JSON for wolf_pack_trader.py to execute
        
        Args:
            portfolio: List of PortfolioPosition objects
            output_file: Path to output JSON file
        """
        orders = []
        
        for pos in portfolio:
            order = {
                'ticker': pos.ticker,
                'action': 'BUY',
                'shares': pos.shares,
                'price': pos.entry_price,
                'allocation_pct': pos.allocation_pct,
                'convergence_score': pos.convergence_score,
                'sector': pos.sector,
                'market_cap': pos.market_cap,
                'confidence': pos.confidence,
                'reasoning': pos.reasoning,
                'timestamp': datetime.now().isoformat()
            }
            orders.append(order)
        
        # Save to file
        output_path = os.path.join(os.path.dirname(__file__), output_file)
        with open(output_path, 'w') as f:
            json.dump(orders, f, indent=2)
        
        print(f"\n💾 Portfolio exported to: {output_path}")
        print(f"   {len(orders)} orders ready for execution")
        
        return output_path
    
    def print_portfolio_summary(self, portfolio: List[PortfolioPosition]):
        """Print readable portfolio summary"""
        print("\n" + "="*70)
        print("📋 PORTFOLIO SUMMARY")
        print("="*70)
        
        for i, pos in enumerate(portfolio, 1):
            print(f"\n{i}. {pos.ticker} - {pos.confidence} CONFIDENCE")
            print(f"   Sector: {pos.sector} | Market Cap: {pos.market_cap}")
            print(f"   Score: {pos.convergence_score}/100")
            print(f"   Allocation: {pos.allocation_pct*100:.1f}%")
            print(f"   Shares: {pos.shares} @ ${pos.entry_price:.2f} = ${pos.shares * pos.entry_price:,.2f}")
            print(f"   Reasoning: {pos.reasoning}")
        
        total_value = sum(p.shares * p.entry_price for p in portfolio)
        total_allocation = sum(p.allocation_pct for p in portfolio)
        
        print("\n" + "="*70)
        print(f"Total positions: {len(portfolio)}")
        print(f"Total value: ${total_value:,.2f}")
        print(f"Total allocation: {total_allocation*100:.1f}%")
        print("="*70)


def demo():
    """Demo: Build portfolio from mock scan results"""
    
    # Mock scan results (what wolf_pack.py would return)
    mock_results = [
        {'ticker': 'NVDA', 'score': 95, 'price': 450.0, 'reasoning': '7-signal convergence + AI boom'},
        {'ticker': 'PLTR', 'score': 92, 'price': 25.0, 'reasoning': 'Government contracts + AI integration'},
        {'ticker': 'IONQ', 'score': 88, 'price': 15.0, 'reasoning': 'Quantum breakthrough + AWS partnership'},
        {'ticker': 'MRNA', 'score': 85, 'price': 110.0, 'reasoning': 'Cancer vaccine trial + insider buying'},
        {'ticker': 'RKLB', 'score': 83, 'price': 8.5, 'reasoning': 'Launch success + NASA contracts'},
        {'ticker': 'CCJ', 'score': 81, 'price': 45.0, 'reasoning': 'Uranium demand + nuclear revival'},
        {'ticker': 'CRWD', 'score': 80, 'price': 300.0, 'reasoning': 'Cybersecurity growth + earnings beat'},
        {'ticker': 'MARA', 'score': 78, 'price': 20.0, 'reasoning': 'Bitcoin rally + mining efficiency'},
        {'ticker': 'AMD', 'score': 77, 'price': 180.0, 'reasoning': 'AI chip demand + data center growth'},
        {'ticker': 'SNOW', 'score': 75, 'price': 180.0, 'reasoning': 'Cloud data growth + enterprise adoption'},
        {'ticker': 'TSM', 'score': 74, 'price': 120.0, 'reasoning': 'Semiconductor demand + Apple orders'},
        {'ticker': 'IBRX', 'score': 73, 'price': 4.5, 'reasoning': 'Clinical trial data + short squeeze potential'},
        {'ticker': 'UUUU', 'score': 72, 'price': 6.0, 'reasoning': 'Rare earth demand + uranium exposure'},
        {'ticker': 'ASTS', 'score': 71, 'price': 25.0, 'reasoning': 'Satellite deployment + AT&T partnership'},
        {'ticker': 'QBTS', 'score': 70, 'price': 3.0, 'reasoning': 'Quantum computing + government grants'}
    ]
    
    # Build portfolio
    builder = PortfolioBuilder(target_positions=12)
    portfolio = builder.build_portfolio(mock_results, account_value=100000.0)
    
    # Print summary
    builder.print_portfolio_summary(portfolio)
    
    # Export for execution
    builder.export_to_trader(portfolio)
    
    print("\n🐺 PORTFOLIO READY FOR EXECUTION")
    print("Next step: python wolf_pack_trader.py --execute portfolio_orders.json")


if __name__ == "__main__":
    demo()
