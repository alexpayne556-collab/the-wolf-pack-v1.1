"""
🐺 WOLF PACK STRATEGIES

All the edges that make us money.

STRATEGIES:
1. Wounded Prey - Quality stocks on sale
2. Compression Breakout - Flat stocks waking up
3. Head Hunter - Low float squeezes
4. Gap and Go - Premarket momentum
5. FDA Catalyst - Binary event plays

RULES:
- Position sizing based on setup type
- Test trades = 2% max (prove thesis first)
- Scale up only after 3+ wins
- Never break the rules
"""

from .wolf_pack_rules import (
    WolfPackRules,
    SetupType,
    PositionSizeRule,
    POSITION_RULES,
    WOLF_PACK_EDGES,
)

from .compression_breakout import CompressionBreakoutStrategy

__all__ = [
    'WolfPackRules',
    'SetupType',
    'PositionSizeRule',
    'POSITION_RULES',
    'WOLF_PACK_EDGES',
    'CompressionBreakoutStrategy',
]
