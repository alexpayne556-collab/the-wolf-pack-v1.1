# 🐺 FENRIR V2 - CONFIG
# Personal AI Trading Companion Configuration

import os
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# API KEYS
# =============================================================================
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")

# =============================================================================
# YOUR HOLDINGS (REAL DATA - Updated 1/16/2026)
# =============================================================================
HOLDINGS = {
    'KTOS': {'shares': 2.717026, 'avg_cost': 117.83, 'account': 'robinhood', 'thesis': 'Defense/Drones'},
    'IBRX': {'shares': 37.081823, 'avg_cost': 4.69, 'account': 'robinhood', 'thesis': 'Biotech - cancer drug revenue'},
    'MU': {'shares': 1.268306, 'avg_cost': 334.48, 'account': 'both', 'thesis': 'AI memory'},
    'UUUU': {'shares': 3.0, 'avg_cost': 22.09, 'account': 'robinhood', 'thesis': 'Nuclear'},
    'BBAI': {'shares': 7.686, 'avg_cost': 6.50, 'account': 'fidelity', 'thesis': 'AI/Defense'},
    'UEC': {'shares': 2.0, 'avg_cost': 17.29, 'account': 'fidelity', 'thesis': 'Nuclear'},
}

ROBINHOOD_CASH = 100.74
FIDELITY_CASH = 87.64
TOTAL_CASH = 188.38

# =============================================================================
# WATCHLIST BY SECTOR
# =============================================================================
WATCHLIST = {
    'nuclear': ['UEC', 'UUUU', 'DNN', 'URG', 'SMR', 'LEU'],
    'defense': ['KTOS', 'RCAT', 'UMAC', 'ONDS', 'JOBY', 'ACHR', 'BBAI', 'LMT', 'RTX', 'NOC'],
    'ai_semis': ['MU', 'NVDA', 'AMD', 'INTC', 'AVGO', 'SMCI', 'PLTR', 'AEHR', 'ICHR'],
    'space': ['RKLB', 'LUNR', 'RDW', 'BKSY', 'ASTS'],
    'biotech': ['IBRX', 'DVAX', 'BEAM', 'CRSP', 'NTLA', 'RGC', 'GPCR'],
    'silver': ['SLV', 'HL', 'AG', 'EXK', 'CDE', 'WPM'],
    'crypto': ['COIN', 'HOOD', 'MSTR', 'BTDR', 'MARA', 'RIOT'],
    'energy': ['BE', 'FSLR', 'ENPH'],
}

# Flat list for scanning
ALL_WATCHLIST = []
for sector, tickers in WATCHLIST.items():
    ALL_WATCHLIST.extend(tickers)
ALL_WATCHLIST = list(set(ALL_WATCHLIST))

# =============================================================================
# STOCK STATES - Adaptive tracking
# =============================================================================
STOCK_STATES = {
    'dead': 'No movement, check daily',
    'watching': 'On watchlist, check hourly',
    'mover': '5%+ move today, check every 30 min',
    'running': 'Multi-day run with catalyst, check every 15 min',
    'RUNNING_POSITION': 'WE OWN IT and its running, check every 5 min',
    'BLEEDING_POSITION': 'WE OWN IT and its dropping, check every 2 min - URGENT',
}

# =============================================================================
# ALERT THRESHOLDS
# =============================================================================
MOVE_THRESHOLD_PCT = 5.0      # Alert on 5%+ moves
VOLUME_THRESHOLD_RATIO = 2.0  # Alert on 2x average volume
POSITION_URGENT_THRESHOLD = 5.0  # Position move that triggers urgent check

# =============================================================================
# FULL MARKET SCAN CONFIG
# =============================================================================
FULL_SCAN_ENABLED = True
FULL_SCAN_MIN_CHANGE = 5.0
FULL_SCAN_MIN_VOLUME_RATIO = 1.5
FULL_SCAN_MIN_PRICE = 1.0
FULL_SCAN_MAX_PRICE = 100.0
FULL_SCAN_MIN_AVG_VOLUME = 100000
FULL_SCAN_MAX_WORKERS = 50  # Parallel threads

# =============================================================================
# DATABASE PATH
# =============================================================================
DB_PATH = 'data/fenrir.db'
SCAN_INTERVAL_MINUTES = 15    # How often to scan during market hours

# =============================================================================
# ACCOUNT INFO
# =============================================================================
ROBINHOOD_CASH = 191.74
FIDELITY_CASH = 87.64
TOTAL_CASH = ROBINHOOD_CASH + FIDELITY_CASH

# =============================================================================
# OLLAMA SETTINGS
# =============================================================================
OLLAMA_MODEL = "fenrir"
OLLAMA_URL = "http://localhost:11434/api/generate"

# =============================================================================
# DATABASE
# =============================================================================
DB_PATH = "fenrir_trades.db"
