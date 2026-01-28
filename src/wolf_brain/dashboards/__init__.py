"""
📊 WOLF PACK DASHBOARDS - SEE EVERYTHING, CONTROL EVERYTHING
Built: January 20, 2026

Two main dashboards:
1. PORTFOLIO DASHBOARD - Shows Alpaca holdings, P&L, positions
2. TRADING BOT DASHBOARD - Interact with the Wolf Brain, teach strategies

Run: python -m wolf_brain.dashboards.main
Then open: http://localhost:8050

Dependencies:
    pip install dash plotly pandas alpaca-trade-api
"""

import os
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

print("📊 Wolf Pack Dashboards module")
print("   Run: python -m wolf_brain.dashboards.main")
