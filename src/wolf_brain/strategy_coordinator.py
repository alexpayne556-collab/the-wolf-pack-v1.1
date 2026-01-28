"""
🎯 STRATEGY COORDINATOR

Central hub that coordinates ALL Wolf Pack strategy modules.
Ranks opportunities across multiple strategies and prevents over-concentration.

STRATEGIES COORDINATED:
1. PDUFA Runup (Biotech catalysts 7-14 days out)
2. Insider Buying (Follow the smart money)
3. Compression Breakout (Flat consolidation + catalyst)
4. Gap and Go (Premarket gaps holding)
5. Wounded Prey (Oversold + catalyst)
6. Head Hunter (Low float + squeeze)
7. Night Research (Homework opportunities)

RISK MANAGEMENT:
- Max 5 total positions
- Max 3 biotech positions
- Max 20% portfolio in any single strategy
- Diversification across setups
"""

import logging
from typing import Dict, List
from datetime import datetime

log = logging.getLogger('WolfBrain')


class StrategyCoordinator:
    """Coordinates multiple strategy modules"""
    
    def __init__(self):
        self.max_positions = 5
        self.max_biotech_positions = 3
        self.max_strategy_pct = 0.20  # 20% per strategy
        
        # Track which strategies are active
        self.active_strategies = {
            'PDUFA_RUNUP': True,
            'INSIDER_BUYING': True,
            'COMPRESSION_BREAKOUT': True,
            'GAP_AND_GO': True,
            'WOUNDED_PREY': True,
            'HEAD_HUNTER': True,
            'NIGHT_RESEARCH': True
        }
        
        # Strategy confidence modifiers (adjusted based on win rate)
        self.strategy_multipliers = {
            'PDUFA_RUNUP': 1.0,
            'INSIDER_BUYING': 1.0,
            'COMPRESSION_BREAKOUT': 1.0,
            'GAP_AND_GO': 1.0,
            'WOUNDED_PREY': 1.0,
            'HEAD_HUNTER': 1.0,
            'NIGHT_RESEARCH': 1.0
        }
        
        log.info("🎯 Strategy Coordinator initialized")
    
    def rank_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """
        Rank all opportunities across strategies
        
        Scoring factors:
        - Base confidence (from Fenrir)
        - Strategy multiplier (win rate)
        - Catalyst timing
        - Risk/reward ratio
        - Market conditions
        """
        scored = []
        
        for opp in opportunities:
            strategy = opp.get('strategy', 'UNKNOWN')
            base_confidence = opp.get('confidence', 0.5)
            
            # Apply strategy multiplier
            multiplier = self.strategy_multipliers.get(strategy, 1.0)
            adjusted_confidence = base_confidence * multiplier
            
            # Bonus points for specific conditions
            bonus = 0
            
            # PDUFA timing bonus
            if strategy == 'PDUFA_RUNUP':
                days_until = opp.get('days_until', 10)
                if 9 <= days_until <= 12:
                    bonus += 0.10  # Sweet spot
                elif 7 <= days_until <= 14:
                    bonus += 0.05  # Good window
            
            # Insider buying bonus
            if strategy == 'INSIDER_BUYING':
                conviction = opp.get('conviction', 5)
                if conviction >= 9:
                    bonus += 0.10
                elif conviction >= 7:
                    bonus += 0.05
            
            # Compression bonus (flat days)
            if strategy == 'COMPRESSION_BREAKOUT':
                flat_days = opp.get('flat_days', 0)
                if flat_days >= 15:
                    bonus += 0.10
                elif flat_days >= 10:
                    bonus += 0.05
            
            # Risk/reward bonus
            entry = opp.get('entry_price', 10)
            stop = opp.get('stop_price', entry * 0.92)
            target = opp.get('target_price', entry * 1.20)
            
            risk = entry - stop
            reward = target - entry
            
            if risk > 0:
                rr_ratio = reward / risk
                if rr_ratio >= 3:
                    bonus += 0.10  # 3:1 or better
                elif rr_ratio >= 2:
                    bonus += 0.05  # 2:1 or better
            
            final_score = min(adjusted_confidence + bonus, 0.98)  # Cap at 98%
            
            opp['final_score'] = final_score
            opp['score_breakdown'] = {
                'base': base_confidence,
                'multiplier': multiplier,
                'bonus': bonus,
                'final': final_score
            }
            
            scored.append(opp)
        
        # Sort by final score
        scored.sort(key=lambda x: x['final_score'], reverse=True)
        
        return scored
    
    def check_portfolio_limits(self, current_positions: Dict, new_opportunity: Dict) -> Dict:
        """
        Check if adding this opportunity would violate limits
        
        Returns:
        {
            'allowed': bool,
            'reason': str,
            'current_stats': dict
        }
        """
        strategy = new_opportunity.get('strategy')
        ticker = new_opportunity.get('ticker')
        
        # Count current positions
        total_positions = len(current_positions)
        
        # Count biotech positions
        biotech_strategies = ['PDUFA_RUNUP', 'INSIDER_BUYING', 'WOUNDED_PREY']
        biotech_count = sum(1 for pos_info in current_positions.values() 
                           if pos_info.get('strategy') in biotech_strategies)
        
        # Count positions in this strategy
        strategy_count = sum(1 for pos_info in current_positions.values() 
                           if pos_info.get('strategy') == strategy)
        
        # Check if ticker already has position
        if ticker in current_positions:
            return {
                'allowed': False,
                'reason': f"Already have position in {ticker}",
                'current_stats': {
                    'total': total_positions,
                    'biotech': biotech_count,
                    'strategy': strategy_count
                }
            }
        
        # Check total positions
        if total_positions >= self.max_positions:
            return {
                'allowed': False,
                'reason': f"Max positions reached: {total_positions}/{self.max_positions}",
                'current_stats': {
                    'total': total_positions,
                    'biotech': biotech_count,
                    'strategy': strategy_count
                }
            }
        
        # Check biotech concentration
        if strategy in biotech_strategies and biotech_count >= self.max_biotech_positions:
            return {
                'allowed': False,
                'reason': f"Max biotech positions: {biotech_count}/{self.max_biotech_positions}",
                'current_stats': {
                    'total': total_positions,
                    'biotech': biotech_count,
                    'strategy': strategy_count
                }
            }
        
        # Check strategy concentration (max 2 per strategy)
        if strategy_count >= 2:
            return {
                'allowed': False,
                'reason': f"Max positions in {strategy}: {strategy_count}/2",
                'current_stats': {
                    'total': total_positions,
                    'biotech': biotech_count,
                    'strategy': strategy_count
                }
            }
        
        # All checks passed
        return {
            'allowed': True,
            'reason': 'Within all limits',
            'current_stats': {
                'total': total_positions,
                'biotech': biotech_count,
                'strategy': strategy_count
            }
        }
    
    def update_strategy_performance(self, strategy: str, win: bool):
        """
        Update strategy multiplier based on win/loss
        
        Winning strategies get boosted, losing strategies get reduced
        """
        current = self.strategy_multipliers.get(strategy, 1.0)
        
        if win:
            # Boost by 5% on win (max 1.5x)
            new_value = min(current * 1.05, 1.5)
            log.info(f"📈 {strategy} multiplier: {current:.2f} → {new_value:.2f} (WIN)")
        else:
            # Reduce by 5% on loss (min 0.5x)
            new_value = max(current * 0.95, 0.5)
            log.warning(f"📉 {strategy} multiplier: {current:.2f} → {new_value:.2f} (LOSS)")
        
        self.strategy_multipliers[strategy] = new_value
    
    def get_strategy_report(self) -> str:
        """Generate a report of all strategies and their status"""
        report = "\n🎯 STRATEGY COORDINATOR STATUS\n"
        report += "=" * 50 + "\n\n"
        
        report += "ACTIVE STRATEGIES:\n"
        for strategy, active in self.active_strategies.items():
            multiplier = self.strategy_multipliers.get(strategy, 1.0)
            status = "✅ ACTIVE" if active else "❌ DISABLED"
            report += f"  {strategy:25s} {status}  (×{multiplier:.2f})\n"
        
        report += f"\nRISK LIMITS:\n"
        report += f"  Max total positions: {self.max_positions}\n"
        report += f"  Max biotech positions: {self.max_biotech_positions}\n"
        report += f"  Max per strategy: 2\n"
        
        return report
    
    def disable_strategy(self, strategy: str):
        """Temporarily disable a strategy (e.g., if performing poorly)"""
        if strategy in self.active_strategies:
            self.active_strategies[strategy] = False
            log.warning(f"⚠️  Strategy disabled: {strategy}")
    
    def enable_strategy(self, strategy: str):
        """Re-enable a strategy"""
        if strategy in self.active_strategies:
            self.active_strategies[strategy] = True
            log.info(f"✅ Strategy enabled: {strategy}")


def test_coordinator():
    """Test the strategy coordinator"""
    print("🧪 Testing Strategy Coordinator\n")
    
    coord = StrategyCoordinator()
    
    # Sample opportunities from different strategies
    opportunities = [
        {
            'ticker': 'AQST',
            'strategy': 'PDUFA_RUNUP',
            'confidence': 0.75,
            'days_until': 10,
            'entry_price': 5.50,
            'stop_price': 4.84,
            'target_price': 6.88
        },
        {
            'ticker': 'PALI',
            'strategy': 'INSIDER_BUYING',
            'confidence': 0.80,
            'conviction': 9,
            'entry_price': 2.30,
            'stop_price': 2.07,
            'target_price': 2.99
        },
        {
            'ticker': 'IONS',
            'strategy': 'COMPRESSION_BREAKOUT',
            'confidence': 0.70,
            'flat_days': 12,
            'entry_price': 8.20,
            'stop_price': 7.79,
            'target_price': 10.25
        }
    ]
    
    # Rank them
    print("RANKING OPPORTUNITIES:")
    ranked = coord.rank_opportunities(opportunities)
    
    for i, opp in enumerate(ranked, 1):
        print(f"\n{i}. {opp['ticker']} ({opp['strategy']})")
        print(f"   Base confidence: {opp['score_breakdown']['base']:.0%}")
        print(f"   Multiplier: {opp['score_breakdown']['multiplier']:.2f}")
        print(f"   Bonus: {opp['score_breakdown']['bonus']:.0%}")
        print(f"   FINAL SCORE: {opp['final_score']:.0%}")
    
    # Test limits
    print("\n" + "="*50)
    print("TESTING PORTFOLIO LIMITS:")
    
    current_positions = {
        'TICKER1': {'strategy': 'PDUFA_RUNUP'},
        'TICKER2': {'strategy': 'PDUFA_RUNUP'},
        'TICKER3': {'strategy': 'INSIDER_BUYING'}
    }
    
    result = coord.check_portfolio_limits(current_positions, opportunities[0])
    print(f"\nCan add {opportunities[0]['ticker']}?")
    print(f"  Allowed: {result['allowed']}")
    print(f"  Reason: {result['reason']}")
    print(f"  Stats: {result['current_stats']}")
    
    # Test performance tracking
    print("\n" + "="*50)
    print("TESTING PERFORMANCE TRACKING:")
    
    print(f"\nInitial PDUFA_RUNUP multiplier: {coord.strategy_multipliers['PDUFA_RUNUP']:.2f}")
    coord.update_strategy_performance('PDUFA_RUNUP', win=True)
    coord.update_strategy_performance('PDUFA_RUNUP', win=True)
    coord.update_strategy_performance('PDUFA_RUNUP', win=False)
    
    # Print report
    print("\n" + "="*50)
    print(coord.get_strategy_report())


if __name__ == '__main__':
    test_coordinator()
