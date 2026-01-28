"""
🐺 Wolf Brain Strategy Modules
================================
All trading strategies and scanners
"""

from .biotech_catalyst_scanner import BiotechCatalystScanner
from . import biotech_prompts
from . import wolf_pack_rules

__all__ = [
    'BiotechCatalystScanner',
    'biotech_prompts',
    'wolf_pack_rules'
]
