"""
🐺🧠 THE WOLF BRAIN - AI-POWERED AUTONOMOUS TRADING SYSTEM
Built: January 20, 2026

Not a score-based robot. A THINKING, LEARNING, GROWING Brain.

Components:
- brain_core.py: Main WolfBrain class with Ollama integration
- strategy_plugins.py: Pluggable strategy system
- memory_system.py: Learning and memory
- autonomous_trader.py: Full buy/sell execution
- universe_scanner.py: 100+ ticker scanning
- wolf_pack_runner.py: Main orchestrator
- wolf_pack_knowledge.py: ALL trading wisdom (Market Wizards, RGC, strategies)
- dashboards/: Portfolio and trading dashboards

Usage:
    from wolf_brain import WolfBrain, UniverseScanner, AutonomousTrader
    
    # Or run the full system:
    python wolf_pack_runner.py
"""

from .brain_core import WolfBrain
from .strategy_plugins import StrategyPluginManager, BaseStrategy
from .memory_system import MemorySystem
from .universe_scanner import UniverseScanner
from .autonomous_trader import AutonomousTrader, TradeStrategy
from .wolf_pack_knowledge import WOLF_PACK_PHILOSOPHY, CORE_STRATEGIES, EXIT_RULES, POSITION_SIZING

__all__ = [
    'WolfBrain',
    'StrategyPluginManager',
    'BaseStrategy', 
    'MemorySystem',
    'UniverseScanner',
    'AutonomousTrader',
    'TradeStrategy',
    'WOLF_PACK_PHILOSOPHY',
    'CORE_STRATEGIES',
    'EXIT_RULES',
    'POSITION_SIZING'
]
