#!/usr/bin/env python3
"""
🐺 WOLF PACK TRADING RULES

Hard rules that NEVER get broken. These protect capital and ensure survival.
Built from painful lessons and winning patterns.

POSITION SIZING:
- Test trades: 2% max position (prove thesis first)
- Proven setups (3+ wins): Scale to 5-10%
- NEVER more than 25% in any single position
- NEVER learn with rent money

ENTRY RULES:
- Wait for the setup, don't chase
- Enter on pullbacks, not spikes
- Volume must confirm
- Have a plan BEFORE entry

EXIT RULES:
- Stop loss is SACRED - never move it down
- Scale out at targets (1R, 2R, 3R)
- Never give back more than 50% of gains
- Take profits into strength

THE EDGES:
1. Wounded Prey - Quality stocks 20-40% off highs
2. Compression Breakout - Flat stocks with catalyst
3. Head Hunter - Low float + catalyst squeezes
4. Gap and Go - Premarket gaps with volume
"""

from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum


class SetupType(Enum):
    """Types of setups the Wolf Pack trades"""
    TEST_TRADE = "test_trade"           # Unproven thesis, 2% max
    COMPRESSION_BREAKOUT = "compression" # Flat stock waking up
    WOUNDED_PREY = "wounded_prey"        # Quality 20-40% off highs
    HEAD_HUNTER = "head_hunter"          # Low float squeeze
    GAP_AND_GO = "gap_and_go"           # Premarket momentum
    FDA_CATALYST = "fda_catalyst"        # Binary event play
    PROVEN_WINNER = "proven_winner"      # Setup that's worked 3+ times


@dataclass
class PositionSizeRule:
    """Position sizing based on setup type"""
    setup_type: SetupType
    max_position_pct: float
    min_conviction: float
    notes: str


# POSITION SIZING RULES
POSITION_RULES = {
    SetupType.TEST_TRADE: PositionSizeRule(
        SetupType.TEST_TRADE,
        max_position_pct=2.0,
        min_conviction=0.5,
        notes="Prove thesis with small money. Scale up AFTER it works 3+ times."
    ),
    SetupType.COMPRESSION_BREAKOUT: PositionSizeRule(
        SetupType.COMPRESSION_BREAKOUT,
        max_position_pct=5.0,
        min_conviction=0.7,
        notes="Flat stock + catalyst + volume = clean setup"
    ),
    SetupType.WOUNDED_PREY: PositionSizeRule(
        SetupType.WOUNDED_PREY,
        max_position_pct=10.0,
        min_conviction=0.75,
        notes="Quality company on sale. Fenrir's bread and butter."
    ),
    SetupType.HEAD_HUNTER: PositionSizeRule(
        SetupType.HEAD_HUNTER,
        max_position_pct=5.0,
        min_conviction=0.7,
        notes="Low float squeeze. High reward but volatile."
    ),
    SetupType.GAP_AND_GO: PositionSizeRule(
        SetupType.GAP_AND_GO,
        max_position_pct=5.0,
        min_conviction=0.65,
        notes="Premarket momentum. Need volume confirmation."
    ),
    SetupType.FDA_CATALYST: PositionSizeRule(
        SetupType.FDA_CATALYST,
        max_position_pct=3.0,
        min_conviction=0.6,
        notes="Binary event. Small size, defined risk."
    ),
    SetupType.PROVEN_WINNER: PositionSizeRule(
        SetupType.PROVEN_WINNER,
        max_position_pct=15.0,
        min_conviction=0.8,
        notes="Setup has worked 3+ times. Full conviction."
    ),
}


class WolfPackRules:
    """
    The Wolf Pack's immutable trading rules.
    These NEVER get broken. Ever.
    """
    
    # === HARD LIMITS ===
    MAX_SINGLE_POSITION_PCT = 25.0  # Never more than 25% in one stock
    MAX_SECTOR_EXPOSURE_PCT = 40.0  # Never more than 40% in one sector
    MAX_DAILY_LOSS_PCT = 5.0        # Stop trading if down 5% in a day
    MIN_CASH_RESERVE_PCT = 20.0     # Always keep 20% cash for opportunities
    
    # === TEST TRADE RULE ===
    TEST_TRADE_MAX_PCT = 2.0        # Unproven ideas = 2% max
    PROVEN_THRESHOLD = 3            # Need 3 wins to scale up
    
    # === STOP LOSS RULES ===
    MAX_LOSS_PER_TRADE_PCT = 7.0    # Max 7% loss on any trade
    STOP_LOSS_SACRED = True         # NEVER move stop loss down
    
    # === PROFIT RULES ===
    SCALE_OUT_1R = 0.33            # Sell 1/3 at 1R
    SCALE_OUT_2R = 0.33            # Sell 1/3 at 2R
    TRAIL_AFTER_2R = True          # Trail stop after 2R hit
    MAX_GIVEBACK_PCT = 50.0        # Never give back more than 50% of gains
    
    @staticmethod
    def calculate_position_size(
        portfolio_value: float,
        setup_type: SetupType,
        conviction: float = 0.7,
        current_price: float = 0,
        stop_loss: float = 0,
    ) -> Dict:
        """
        Calculate position size based on rules.
        
        Args:
            portfolio_value: Total portfolio value
            setup_type: Type of setup
            conviction: Confidence level (0-1)
            current_price: Entry price
            stop_loss: Stop loss price
            
        Returns:
            Dict with position sizing info
        """
        rule = POSITION_RULES.get(setup_type, POSITION_RULES[SetupType.TEST_TRADE])
        
        # Check minimum conviction
        if conviction < rule.min_conviction:
            return {
                'allowed': False,
                'reason': f"Conviction {conviction:.0%} below minimum {rule.min_conviction:.0%}",
                'max_shares': 0,
                'max_dollars': 0,
            }
        
        # Calculate max position based on setup type
        max_position_pct = min(rule.max_position_pct, WolfPackRules.MAX_SINGLE_POSITION_PCT)
        
        # Adjust for conviction (higher conviction = closer to max)
        adjusted_pct = max_position_pct * conviction
        
        # Calculate dollars
        max_dollars = portfolio_value * (adjusted_pct / 100)
        
        # Calculate shares if price provided
        max_shares = int(max_dollars / current_price) if current_price > 0 else 0
        
        # Risk-based sizing if stop loss provided
        risk_based_shares = 0
        if current_price > 0 and stop_loss > 0:
            risk_per_share = current_price - stop_loss
            max_risk_dollars = portfolio_value * 0.01  # Risk 1% of portfolio max
            risk_based_shares = int(max_risk_dollars / risk_per_share) if risk_per_share > 0 else 0
            
            # Use the smaller of position-based or risk-based
            max_shares = min(max_shares, risk_based_shares)
            max_dollars = max_shares * current_price
        
        return {
            'allowed': True,
            'setup_type': setup_type.value,
            'max_position_pct': adjusted_pct,
            'max_dollars': max_dollars,
            'max_shares': max_shares,
            'conviction': conviction,
            'notes': rule.notes,
            'risk_based_shares': risk_based_shares,
        }
    
    @staticmethod
    def check_trade_allowed(
        portfolio_value: float,
        current_positions: Dict[str, float],
        new_ticker: str,
        new_position_value: float,
        sector: str = None,
    ) -> Dict:
        """
        Check if a new trade is allowed based on rules.
        
        Returns dict with 'allowed' bool and 'reason' if not allowed.
        """
        # Check single position limit
        position_pct = (new_position_value / portfolio_value) * 100
        if position_pct > WolfPackRules.MAX_SINGLE_POSITION_PCT:
            return {
                'allowed': False,
                'reason': f"Position {position_pct:.1f}% exceeds max {WolfPackRules.MAX_SINGLE_POSITION_PCT}%"
            }
        
        # Check total exposure
        total_invested = sum(current_positions.values()) + new_position_value
        total_pct = (total_invested / portfolio_value) * 100
        max_invested_pct = 100 - WolfPackRules.MIN_CASH_RESERVE_PCT
        
        if total_pct > max_invested_pct:
            return {
                'allowed': False,
                'reason': f"Would exceed max invested {max_invested_pct}% (cash reserve rule)"
            }
        
        return {'allowed': True, 'reason': None}
    
    @staticmethod
    def get_exit_plan(
        entry_price: float,
        stop_loss: float,
        shares: int,
    ) -> Dict:
        """
        Generate exit plan based on rules.
        
        Returns targets and share quantities for scaling out.
        """
        risk = entry_price - stop_loss
        
        # Calculate targets
        target_1r = entry_price + risk
        target_2r = entry_price + (risk * 2)
        target_3r = entry_price + (risk * 3)
        
        # Calculate shares to sell at each target
        shares_1r = int(shares * WolfPackRules.SCALE_OUT_1R)
        shares_2r = int(shares * WolfPackRules.SCALE_OUT_2R)
        shares_3r = shares - shares_1r - shares_2r  # Rest at 3R
        
        return {
            'entry': entry_price,
            'stop_loss': stop_loss,
            'risk_per_share': risk,
            'total_risk': risk * shares,
            'targets': [
                {'price': target_1r, 'shares': shares_1r, 'label': '1R'},
                {'price': target_2r, 'shares': shares_2r, 'label': '2R'},
                {'price': target_3r, 'shares': shares_3r, 'label': '3R'},
            ],
            'trail_stop_after': target_2r,
            'notes': "Move stop to breakeven after 1R. Trail after 2R."
        }


# ============ WOLF PACK EDGES ============

WOLF_PACK_EDGES = {
    'wounded_prey': {
        'name': 'Wounded Prey',
        'description': 'Quality stocks 20-40% off highs with no fundamental damage',
        'criteria': [
            'Down 20-40% from 52-week high',
            'Strong fundamentals (profitable or clear path)',
            'No major news/scandal causing drop',
            'Sector rotation or market fear, not company specific',
            'Institutional ownership still present',
        ],
        'entry': 'Buy when RSI < 30 or at major support level',
        'stop': 'Below recent low or support level (max 10%)',
        'target': 'Previous high or resistance (20-40% upside)',
        'position_size': '5-10% portfolio',
    },
    
    'compression_breakout': {
        'name': 'Compression Breakout',
        'description': 'Find stocks sleeping (flat + low volume), wait for catalyst to wake them up',
        'criteria': [
            'Trading in tight range (< 10% high-to-low for 5+ days)',
            'Volume below average (sleeping)',
            'REAL catalyst emerges (FDA, earnings, deal)',
            'Volume spikes 10x+ on breakout day',
            'Breaks above compression range',
        ],
        'entry': 'First pullback to VWAP or breakout level, NOT the initial spike',
        'stop': 'Below VWAP or below breakout level',
        'target': 'Measured move = range height added to breakout',
        'position_size': '5% portfolio (test), scale if works',
    },
    
    'head_hunter': {
        'name': 'Head Hunter (Low Float Squeeze)',
        'description': 'Low float + catalyst + short interest = explosive move',
        'criteria': [
            'Float under 20M shares (ideally under 10M)',
            'Short interest > 15%',
            'Clear catalyst (FDA, earnings, contract)',
            'Premarket gap 10%+',
            'Heavy premarket volume',
        ],
        'entry': 'First consolidation after initial spike (flag pattern)',
        'stop': 'Below flag low (tight)',
        'target': 'No target - trail stop and let it run',
        'position_size': '3-5% portfolio (volatile!)',
    },
    
    'gap_and_go': {
        'name': 'Gap and Go',
        'description': 'Strong premarket gap with volume confirmation',
        'criteria': [
            'Gap up 5%+ in premarket',
            'Volume 5x+ normal premarket volume',
            'Clear catalyst for the gap',
            'Holding above VWAP',
            'Making higher lows in premarket',
        ],
        'entry': 'Break of premarket high OR first pullback to VWAP',
        'stop': 'Below VWAP or below premarket low',
        'target': '1R, 2R, 3R scaling',
        'position_size': '5% portfolio',
    },
    
    'fda_catalyst': {
        'name': 'FDA Catalyst',
        'description': 'Binary event play on FDA decisions',
        'criteria': [
            'Known PDUFA date within 2 weeks',
            'Drug/indication has merit',
            'Stock not already priced for approval',
            'Float manageable (under 100M)',
            'Options available for hedging',
        ],
        'entry': 'Small position before event OR larger after positive news',
        'stop': 'Defined risk (options) or 20% max',
        'target': '50-200% on approval, -50% on rejection',
        'position_size': '2-3% portfolio (binary risk!)',
    },
}


def print_rules():
    """Print all Wolf Pack rules"""
    print("🐺 WOLF PACK TRADING RULES")
    print("=" * 60)
    print()
    print("POSITION SIZING:")
    print(f"  • Test trades: {WolfPackRules.TEST_TRADE_MAX_PCT}% max")
    print(f"  • Max single position: {WolfPackRules.MAX_SINGLE_POSITION_PCT}%")
    print(f"  • Min cash reserve: {WolfPackRules.MIN_CASH_RESERVE_PCT}%")
    print(f"  • Max daily loss: {WolfPackRules.MAX_DAILY_LOSS_PCT}%")
    print()
    print("EXIT RULES:")
    print(f"  • Scale out: {WolfPackRules.SCALE_OUT_1R:.0%} at 1R, {WolfPackRules.SCALE_OUT_2R:.0%} at 2R")
    print(f"  • Max giveback: {WolfPackRules.MAX_GIVEBACK_PCT}%")
    print(f"  • Trail stop after 2R: {WolfPackRules.TRAIL_AFTER_2R}")
    print()
    print("THE EDGES:")
    for key, edge in WOLF_PACK_EDGES.items():
        print(f"\n{edge['name'].upper()}")
        print(f"  {edge['description']}")


if __name__ == '__main__':
    print_rules()
    
    # Example position sizing
    print("\n" + "=" * 60)
    print("EXAMPLE: Position sizing for $100,000 portfolio")
    print("=" * 60)
    
    portfolio = 100000
    
    for setup_type in SetupType:
        result = WolfPackRules.calculate_position_size(
            portfolio_value=portfolio,
            setup_type=setup_type,
            conviction=0.75,
            current_price=50,
        )
        if result['allowed']:
            print(f"\n{setup_type.value}:")
            print(f"  Max position: ${result['max_dollars']:,.0f} ({result['max_position_pct']:.1f}%)")
            print(f"  Max shares at $50: {result['max_shares']}")
            print(f"  Notes: {result['notes']}")
