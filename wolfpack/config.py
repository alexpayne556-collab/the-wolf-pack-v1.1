#!/usr/bin/env python3
"""
Wolf Pack Tracker Configuration
MONEY's trading universe + system settings
"""

from datetime import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# =============================================================================
# API KEYS (Loaded from .env)
# =============================================================================

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')
ALPHAVANTAGE_API_KEY = os.getenv('ALPHAVANTAGE_API_KEY', '')
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY', '')
SEC_EDGAR_BASE_URL = os.getenv('SEC_EDGAR_BASE_URL', 'https://www.sec.gov')

# API Configuration
MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 50))
REQUEST_DELAY_MS = int(os.getenv('REQUEST_DELAY_MS', 100))
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', 300))

# =============================================================================
# TRADING UNIVERSE - WOLFPACK 100 (99 stocks across 11 sectors)
# =============================================================================

UNIVERSE = {
    "Holdings": ["MU", "UEC", "KTOS", "SLV", "SRTA", "BBAI"],
    
    "Defense": ["AVAV", "RCAT", "LMT", "NOC", "RTX", "GD", 
                "PLTR", "LDOS", "BAH", "HII", "LHX", "MRCY"],
    
    "Space": ["LUNR", "RKLB", "RDW", "ASTS", "BKSY", "SPCE", 
              "IRDM", "GSAT"],
    
    "Nuclear": ["UUUU", "LEU", "CCJ", "NNE", "OKLO", "SMR", 
                "DNN", "URG"],
    
    "Semis": ["AMD", "NVDA", "INTC", "MRVL", "QCOM", "AVGO", 
              "TSM", "AMAT", "LRCX", "KLAC", "ASML", "ON"],
    
    "AI_Tech": ["AAPL", "MSFT", "GOOGL", "META", "AMZN", "TSLA", 
                "SNOW", "AI", "SOUN", "UPST", "PATH"],
    
    "Biotech": ["EDIT", "BEAM", "CRSP", "MRNA", "REGN", "VRTX", 
                "SRPT", "ALNY", "IONS", "EXAS", "NTLA"],
    
    "Quantum": ["QUBT", "QBTS", "RGTI", "IONQ"],
    
    "Crypto": ["RIOT", "MARA", "COIN", "MSTR", "HOOD", "SOFI", 
               "AFRM", "CLSK"],
    
    "Materials": ["FCX", "VALE", "NEM", "GOLD", "AA", "X", "CLF"],
    
    "EVs": ["RIVN", "LCID", "NIO", "XPEV", "LI", "CHPT", "BLNK"],
    
    "Energy": ["FCEL", "PLUG", "BE", "ENPH", "RUN"]
}

# Flatten to list of all tickers
ALL_TICKERS = []
TICKER_TO_SECTOR = {}

for sector, tickers in UNIVERSE.items():
    ALL_TICKERS.extend(tickers)
    for ticker in tickers:
        TICKER_TO_SECTOR[ticker] = sector

# =============================================================================
# SYSTEM SETTINGS
# =============================================================================

# Directories
DATA_DIR = Path(os.getenv('DATA_DIR', './data'))
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR = Path('./reports')
REPORTS_DIR.mkdir(exist_ok=True)

# Database
DB_PATH = str(DATA_DIR / 'wolfpack.db')

# Data collection
DATA_LOOKBACK_DAYS = 365  # How far back to pull for calculations
RATE_LIMIT_DELAY = REQUEST_DELAY_MS / 1000.0  # Convert to seconds

# Data collection
DATA_LOOKBACK_DAYS = 100  # How far back to pull for calculations
RATE_LIMIT_DELAY = 0.3    # Seconds between API calls

# Market hours (ET)
MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)

# Move thresholds (for investigation and alerts)
BIG_MOVE_THRESHOLD = 5.0          # % triggers investigation
MEDIUM_MOVE_THRESHOLD = 3.0       # % flags for monitoring
SMALL_MOVE_THRESHOLD = 2.0        # % recorded but not investigated
VOLUME_SPIKE_THRESHOLD = 2.0      # x average for "volume spike"
EXTREME_VOLUME_THRESHOLD = 5.0    # x average for extreme volume
WOUNDED_THRESHOLD = 40.0          # % from high for "wounded prey"

# Alert thresholds
PORTFOLIO_STOP_LOSS_PCT = -8.0    # Alert when position down X%
WATCHLIST_DIP_BUY_PCT = -5.0      # Alert when quality stock dips X%
SECTOR_BREAKOUT_PCT = 3.0         # Alert when sector moves X%+

# Analysis defaults
DEFAULT_WINNER_THRESHOLD = 20.0   # % gain to qualify as "winner"
DEFAULT_TIMEFRAME = 10            # days forward to check

# Our portfolio (for position tracking)
PORTFOLIO = {
    "MU": {"shares": 1, "avg_cost": 333.01, "tier": "core"},
    "UEC": {"shares": 2, "avg_cost": 4.87, "tier": "core"},
    "KTOS": {"shares": 1, "avg_cost": 27.12, "tier": "core"},
    "SLV": {"shares": 5, "avg_cost": 27.83, "tier": "core"},
    "SRTA": {"shares": 5, "avg_cost": 9.66, "tier": "speculative"},
    "BBAI": {"shares": 10, "avg_cost": 4.00, "tier": "speculative"}
}

# =============================================================================
# DISPLAY SETTINGS
# =============================================================================

# Console colors (for terminal output)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def get_color(value):
    """Get color based on positive/negative value"""
    if value > 0:
        return GREEN
    elif value < 0:
        return RED
    else:
        return RESET
