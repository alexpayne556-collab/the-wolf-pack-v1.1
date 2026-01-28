"""
🐺 AUTONOMOUS WOLF BRAIN - 24/7 HUNTER
Built: January 20, 2026

Runs continuously. Thinks for itself. Trades autonomously.
Uses Leonard File as GUIDELINES - not rigid rules.
Scrapes, researches, decides, executes, learns.

FEATURES:
- 24/7 continuous operation with scheduled tasks
- Premarket scanning (4-9:30 AM)
- Market hours trading (9:30 AM - 4 PM)
- After hours analysis
- Web scraping for news/catalysts
- API integration (Alpaca, Finnhub, NewsAPI)
- Full autonomy with safety limits
- Complete logging of all decisions

Usage:
    python autonomous_brain.py              # Start 24/7 autonomous mode
    python autonomous_brain.py --dry-run    # Run without executing trades
    python autonomous_brain.py --once       # Run one cycle then exit

The brain THINKS. It uses our wisdom as guidelines, not rules.
It experiments, learns, adapts. We review logs to guide it.
"""

import os
import sys
import json
import time
import sqlite3
import logging
import requests
import threading
from datetime import datetime, timedelta, time as dtime
from typing import Dict, List, Optional, Tuple, Any
import argparse
from concurrent.futures import ThreadPoolExecutor
import random

# ============ DEPENDENCIES ============

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False
    print("⚠️  pip install yfinance")

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, StopOrderRequest, StopLimitOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    print("⚠️  pip install alpaca-py")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("⚠️  pip install beautifulsoup4 (optional - for web scraping)")

# Load .env file
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(env_path)
    print(f"[OK] Loaded .env from {env_path}")
except ImportError:
    print("[WARN] pip install python-dotenv (will use environment variables)")

# Load strategy modules
sys.path.insert(0, os.path.dirname(__file__))
try:
    from modules.biotech_catalyst_scanner import BiotechCatalystScanner
    from modules import biotech_prompts
    from modules import wolf_pack_rules
    MODULES_AVAILABLE = True
    print("✅ Strategy modules loaded")
except ImportError as e:
    MODULES_AVAILABLE = False
    print(f"⚠️  Strategy modules not found: {e}")


# ============ CONFIGURATION ============

# API Keys from environment - ALL AVAILABLE APIs
ALPACA_KEY = os.environ.get('ALPACA_API_KEY') or os.environ.get('APCA_API_KEY_ID', '')
ALPACA_SECRET = os.environ.get('ALPACA_SECRET_KEY') or os.environ.get('APCA_API_SECRET_KEY', '')
ALPACA_BASE_URL = os.environ.get('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')

# News APIs
FINNHUB_KEY = os.environ.get('FINNHUB_API_KEY', '')
NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY') or os.environ.get('NEWS_API_KEY', '')

# Market Data APIs
ALPHAVANTAGE_KEY = os.environ.get('ALPHAVANTAGE_API_KEY') or os.environ.get('ALPHA_VANTAGE_KEY', '')
POLYGON_KEY = os.environ.get('POLYGON_API_KEY', '')

# SEC Edgar (free, just needs user agent)
SEC_USER_AGENT = os.environ.get('SEC_USER_AGENT', 'Wolf Pack Trading')

# Log loaded APIs
print("📡 APIs Loaded:")
print(f"   Alpaca: {'✅' if ALPACA_KEY else '❌'}")
print(f"   Finnhub: {'✅' if FINNHUB_KEY else '❌'}")
print(f"   NewsAPI: {'✅' if NEWSAPI_KEY else '❌'}")
print(f"   Alpha Vantage: {'✅' if ALPHAVANTAGE_KEY else '❌'}")
print(f"   Polygon: {'✅' if POLYGON_KEY else '❌'}")
print(f"   SEC Edgar: {'✅' if SEC_USER_AGENT else '❌'}")

# Ollama
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "fenrir:latest"

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'wolf_brain')
os.makedirs(DATA_DIR, exist_ok=True)

# Logging - detailed file + console
LOG_FILE = os.path.join(DATA_DIR, f'autonomous_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger('AutonomousBrain')


# ============ RUNNER INTELLIGENCE ============
# When and how huge runners happen - deep research

RUNNER_INTELLIGENCE = """
═══════════════════════════════════════════════════════════════════════
                    WHEN HUGE RUNNERS HAPPEN
═══════════════════════════════════════════════════════════════════════

NEWS TYPE → WHEN IT DROPS → WHEN STOCK MOVES:
- FDA Approval: ANY TIME (often before 8AM or after 4PM) → IMMEDIATELY
- Clinical Trial Data: Usually pre-market 6-8AM or after close 4-6PM → IMMEDIATELY  
- Earnings: After close (4-5PM) or pre-market (6-8AM) → That evening or 4AM gap
- Contract Awarded: Often morning press release 7-9AM → Same session or premarket
- Merger/Acquisition: Usually premarket 6-9AM → GAP UP at open

SECTORS WITH BIGGEST RUNNERS:
- BIOTECH: FDA is binary yes/no = 50-500%+ moves (PDUFA dates, trial data)
- SPACE/DEFENSE: Government contracts, geopolitics = 20-100% (Trump policy)
- EV: Delivery numbers, partnerships = 15-50%
- AI/CHIPS: Earnings, demand cycles = 10-30%
- LOW FLOAT ANYTHING: Small supply = 100%+ on any positive news

═══════════════════════════════════════════════════════════════════════
                    THE BIOTECH FORMULA (BIGGEST RUNNERS)
═══════════════════════════════════════════════════════════════════════

LOW FLOAT (<20M shares) + FDA CATALYST + POSITIVE NEWS = 100-500% IN ONE DAY

Recent Examples:
- SNGX: 3M float + Phase 2 positive = +330%
- BTAI: 5M float + Phase 3 completion = +50%+
- TNXP: 7M float + DOD contract = +100%+

═══════════════════════════════════════════════════════════════════════
                    HOW TO SPOT THE RUNNER (4AM PROTOCOL)
═══════════════════════════════════════════════════════════════════════

1. PREMARKET SCANNER - Sort by % gain at 4AM
2. LOOK FOR +10% GAP minimum (bigger = better)
3. CHECK THE NEWS - Is it REAL? (FDA, earnings, contract - NOT fluff PR)
4. CHECK FLOAT - Under 20M = bigger potential, under 10M = moon potential
5. CHECK VOLUME - Heavy premarket volume = real move, Light = fake/fade
6. WATCH 6-8AM - Volume CONFIRMS or DENIES the move
7. DECISION BY 9:30AM - Entry at open or pass

RUNNER vs FADER:
✅ RUNNER: Real news, low float, volume building, holds premarket gains
❌ FADER: PR fluff, high float, volume dying, bleeding from premarket highs
"""

# Key FDA dates to watch - potential 100%+ runners
FDA_CALENDAR = {
    'AQST': {'date': '2026-01-31', 'drug': 'Anaphylm', 'indication': 'Oral EpiPen alternative', 'float': '30M', 'notes': 'Analyst target $9.20 vs ~$3.33 = +176% upside'},
    'PHAR': {'date': '2026-01-31', 'drug': 'Leniolisib', 'indication': 'Rare disease', 'float': 'Small', 'notes': 'Orphan drug'},
    'IRON': {'date': '2026-01-31', 'drug': 'Bitopertinib', 'indication': 'Schizophrenia', 'float': '40M', 'notes': 'CNS play'},
    'VNDA': {'date': '2026-02-21', 'drug': 'Bysanti', 'indication': 'Motion sickness', 'float': '50M', 'notes': 'Larger cap'},
    'ETON': {'date': '2026-02-25', 'drug': 'ET-600', 'indication': 'Rare disease', 'float': 'Small', 'notes': 'Specialty pharma'},
}


# ============ SAFETY LIMITS ============

SAFETY = {
    'max_position_pct': 0.10,      # Max 10% of portfolio in one position
    'max_daily_trades': 10,         # Max trades per day
    'max_daily_loss_pct': 0.05,     # Stop trading if down 5% today
    'max_portfolio_heat': 0.30,     # Max 30% of portfolio at risk
    'require_stop_loss': True,      # All trades must have stops
    'paper_only': True,             # PAPER TRADING ONLY (safety)
}


# ============ WOLF PACK WISDOM (Guidelines) ============

from wolf_pack_knowledge import WOLF_PACK_PHILOSOPHY


# ============ UNIVERSE OF TICKERS ============

UNIVERSE = {
    # FDA plays - upcoming catalysts
    'fda_plays': ['AQST', 'PHAR', 'IRON', 'VNDA', 'ETON'],
    
    # Core watchlist - researched setups
    'core_watchlist': [
        'GLSI', 'BTAI', 'PMCB', 'ONCY', 'IBRX', 'SNGX', 'TNXP',
    ],
    
    # Low float biotech - biggest runner potential
    'low_float_biotech': [
        'SNGX', 'TNXP', 'BTAI', 'OCGN', 'MNMD', 'IBRX', 'GLSI', 
        'PMCB', 'HGEN', 'ONCY', 'EDSA', 'KROS'
    ],
    
    # Defense/Space - Trump policy momentum
    'defense_space': ['KTOS', 'RKLB', 'LUNR', 'ASTS', 'PLTR', 'GILT', 'LMT', 'RTX'],
    
    # Nuclear - Energy play
    'nuclear': ['SMR', 'OKLO', 'NNE', 'BWXT', 'LEU', 'UEC', 'UUUU', 'CCJ'],
    
    # AI/Quantum - Tech momentum  
    'ai_quantum': ['IONQ', 'QBTS', 'RGTI', 'SOUN', 'BBAI', 'AI', 'PATH'],
    
    # General biotech (expanded list)
    'biotech': [
        'ONCY', 'BTAI', 'EDSA', 'SNGX', 'TNXP', 'IBRX', 'OCGN', 'MNMD',
        'KROS', 'CELC', 'VNDA', 'NUVL', 'GLSI', 'PMCB', 'HGEN', 'TGTX'
    ],
    
    # Defense (separate)
    'defense': ['KTOS', 'RKLB', 'LUNR', 'ASTS', 'PLTR', 'GILT'],
    
    # Momentum plays
    'momentum': ['CIFR', 'HIMS', 'RXRX', 'GEVO', 'PLUG'],
}


# ============ THE BRAIN ============

class AutonomousBrain:
    """
    24/7 Autonomous Trading Brain
    
    Thinks, researches, trades, learns - all on its own.
    Uses wisdom as guidelines, makes its own decisions.
    """
    
    def __init__(self, dry_run: bool = False):
        """Initialize the autonomous brain"""
        self.dry_run = dry_run
        self.running = False
        self.ollama_connected = False
        self.alpaca_connected = False
        self.trading_client = None
        
        # Daily tracking
        self.daily_trades = 0
        self.daily_pnl = 0
        self.last_reset = datetime.now().date()
        
        # Memory - USE MAIN LEARNING ENGINE (not separate DB)
        self.learning_db = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'wolfpack.db')
        self.db_path = os.path.join(DATA_DIR, 'autonomous_memory.db')  # Keep for backwards compat
        self._init_database()
        
        # Load lessons learned from historical trades
        self.lessons = self._load_lessons_from_history()
        
        # Open positions tracking
        self.positions = {}
        self.pending_stops = {}
        
        # MOMENTUM TRACKING - Track tickers across multiple scans for sustained runners
        self.momentum_tracker = {}  # {ticker: [scan_data1, scan_data2, ...]}
        self.sustained_runners = []  # Tickers with sustained strength across multiple scans
        
        # Strategy modules
        if MODULES_AVAILABLE:
            self.biotech_scanner = BiotechCatalystScanner()
            log.info("✅ Biotech catalyst scanner initialized")
        else:
            self.biotech_scanner = None
        
        # Connect services
        self._connect_ollama()
        self._connect_alpaca()
        
        log.info("="*60)
        log.info("🐺 AUTONOMOUS WOLF BRAIN INITIALIZED")
        log.info(f"   Learning DB: {self.learning_db}")
        log.info(f"   Lessons loaded: {len(self.lessons)} patterns")
        log.info("="*60)
        log.info("🐺 AUTONOMOUS WOLF BRAIN INITIALIZED")
        log.info(f"   Mode: {'DRY RUN' if dry_run else 'LIVE PAPER TRADING'}")
        log.info(f"   Brain: {'ONLINE' if self.ollama_connected else 'OFFLINE'}")
        log.info(f"   Alpaca: {'CONNECTED' if self.alpaca_connected else 'NOT CONNECTED'}")
        log.info(f"   Modules: {'LOADED' if MODULES_AVAILABLE else 'NOT AVAILABLE'}")
        log.info(f"   Log: {LOG_FILE}")
        log.info("="*60)
    
    def _init_database(self):
        """Initialize SQLite for persistent memory"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Decisions log - every decision the brain makes
        c.execute('''CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            decision_type TEXT,
            ticker TEXT,
            action TEXT,
            reasoning TEXT,
            confidence REAL,
            outcome TEXT
        )''')
        
        # Trades log
        c.execute('''CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            ticker TEXT,
            side TEXT,
            quantity INTEGER,
            entry_price REAL,
            stop_price REAL,
            target_price REAL,
            strategy TEXT,
            reasoning TEXT,
            status TEXT,
            exit_price REAL,
            pnl REAL
        )''')
        
        # Research log - what the brain discovered
        c.execute('''CREATE TABLE IF NOT EXISTS research (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            source TEXT,
            ticker TEXT,
            content TEXT,
            relevance REAL
        )''')
        
        # Learnings - patterns discovered
        c.execute('''CREATE TABLE IF NOT EXISTS learnings (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            pattern TEXT,
            description TEXT,
            success_rate REAL,
            sample_size INTEGER
        )''')
        
        conn.commit()
        conn.close()
    
    def _load_lessons_from_history(self) -> Dict:
        """
        🧠 LEARN FROM HISTORY - Load lessons from all historical trades
        
        This is the CORE of the learning engine.
        Analyzes ALL past trades to extract:
        - Convergence thresholds (what scores work)
        - Volume confirmation (what volume ratios work)
        - Signal combinations that succeed
        - Tickers/sectors to avoid or favor
        
        CRITICAL LESSONS FROM JAN 27, 2026 SESSION:
        ✅ IBRX: Convergence 85, Volume 2.8x = GOLD STANDARD (+55.26% and holding)
        ✅ RDW: Convergence 78, Volume 1.8x = WORKING (+29.56%)
        ✅ MRNO: Convergence 55, Volume 3.5x = WORKING (+111.43% speculative)
        ❌ DNN: Convergence 45, Volume 1.2x = FAILED (-3.78% - stale intel)
        
        THRESHOLDS LEARNED:
        - Min convergence: 50 (45 failed)
        - Optimal convergence: 70+ (78 and 85 working great)
        - Min volume: 1.5x (1.2x failed)
        - Optimal volume: 2.0x+ (2.8x gold standard)
        """
        lessons = {
            'min_convergence': 50,      # Hard floor (DNN @ 45 failed)
            'optimal_convergence': 70,   # Sweet spot (RDW @ 78, IBRX @ 85 working)
            'gold_convergence': 85,      # Gold standard (IBRX @ 85 = big position)
            'min_volume': 1.5,           # Hard floor (DNN @ 1.2x failed)
            'optimal_volume': 2.0,       # Sweet spot
            'gold_volume': 2.8,          # Gold standard (IBRX volume)
            'winning_signals': {},       # Track which signals work
            'losing_signals': {},        # Track which signals fail
            'ticker_history': {},        # Win/loss by ticker
            'sector_history': {},        # Win/loss by sector
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0.0
        }
        
        if not os.path.exists(self.learning_db):
            log.warning("⚠️  Learning database not found - using default thresholds")
            return lessons
        
        try:
            conn = sqlite3.connect(self.learning_db)
            c = conn.cursor()
            
            # Get all historical trades with metadata
            c.execute("SELECT ticker, action, price, thesis, notes, outcome, day2_pct, day5_pct FROM trades ORDER BY id")
            trades = c.fetchall()
            
            lessons['total_trades'] = len(trades)
            
            for ticker, action, price, thesis, notes_str, outcome, day2_pct, day5_pct in trades:
                # Parse metadata
                try:
                    import json
                    notes = json.loads(notes_str) if notes_str else {}
                except:
                    notes = {}
                
                # Get convergence and volume from notes
                convergence = notes.get('convergence', 0)
                volume_ratio = notes.get('volume_ratio', 0)
                signals = notes.get('signals', [])
                
                # Track signals
                for signal in signals:
                    if signal not in lessons['winning_signals']:
                        lessons['winning_signals'][signal] = {'count': 0}
                    lessons['winning_signals'][signal]['count'] += 1
            
            # Calculate win rate from completed trades only
            c.execute("SELECT COUNT(*) FROM trades WHERE action = 'SELL' AND notes LIKE '%outcome%'")
            completed = c.fetchone()[0]
            if completed > 0:
                # Count wins and losses
                c.execute("SELECT notes FROM trades WHERE action = 'SELL'")
                for (notes_str,) in c.fetchall():
                    try:
                        import json
                        notes = json.loads(notes_str) if notes_str else {}
                        outcome = notes.get('outcome', '')
                        if 'early_exit' not in outcome.lower() and notes.get('days_held', 1) > 0:
                            # Was this a win or loss? Check if it was DNN
                            lessons_learned = notes.get('lessons_learned', [])
                            if lessons_learned:
                                lessons['losses'] += 1
                            else:
                                lessons['wins'] += 1
                    except:
                        pass
            
            # Set win rate
            if lessons['wins'] + lessons['losses'] > 0:
                lessons['win_rate'] = lessons['wins'] / (lessons['wins'] + lessons['losses'])
            
            conn.close()
            
            log.info("📚 LESSONS LOADED:")
            log.info(f"   Total trades: {lessons['total_trades']}")
            log.info(f"   Win rate: {lessons['win_rate']:.1%}")
            log.info(f"   Min convergence: {lessons['min_convergence']}")
            log.info(f"   Min volume: {lessons['min_volume']}x")
            
        except Exception as e:
            log.error(f"❌ Failed to load lessons: {e}")
        
        return lessons
    
    def _connect_ollama(self):
        """Check Ollama connection"""
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            if r.status_code == 200:
                models = [m['name'] for m in r.json().get('models', [])]
                if any(OLLAMA_MODEL.split(':')[0] in m for m in models):
                    self.ollama_connected = True
                    log.info(f"🧠 Ollama connected: {OLLAMA_MODEL}")
                else:
                    log.warning(f"⚠️  Model not found. Available: {models}")
        except Exception as e:
            log.warning(f"⚠️  Ollama not available: {e}")
    
    def _connect_alpaca(self):
        """Connect to Alpaca paper trading"""
        if not ALPACA_AVAILABLE or not ALPACA_KEY:
            log.warning("⚠️  Alpaca not configured")
            return
        
        try:
            self.trading_client = TradingClient(
                ALPACA_KEY, ALPACA_SECRET, 
                paper=SAFETY['paper_only']
            )
            acc = self.trading_client.get_account()
            self.alpaca_connected = True
            log.info(f"💰 Alpaca connected: ${float(acc.portfolio_value):,.2f}")
        except Exception as e:
            log.error(f"❌ Alpaca failed: {e}")
    
    def should_take_trade(self, ticker: str, convergence: float, volume_ratio: float, 
                         signals: List[str], strategy: str) -> Tuple[bool, str, float]:
        """
        🧠 LEARNING ENGINE DECISION - Should we take this trade?
        
        Queries historical data to determine if this setup has worked before.
        Applies all lessons learned from past trades.
        
        Returns: (should_trade, reason, position_size_pct)
        
        CRITICAL THRESHOLDS FROM LESSONS:
        - Convergence < 50: REJECT (DNN @ 45 failed)
        - Volume < 1.5x: REJECT (DNN @ 1.2x failed)
        - Convergence 50-69: SMALL position (4%)
        - Convergence 70-84: MEDIUM position (8%)
        - Convergence 85+: LARGE position (12%) - IBRX gold standard
        """
        # HARD FILTERS FROM LESSONS
        if convergence < self.lessons['min_convergence']:
            return False, f"Convergence {convergence} < minimum {self.lessons['min_convergence']} (learned from DNN failure)", 0.0
        
        if volume_ratio < self.lessons['min_volume']:
            return False, f"Volume {volume_ratio:.1f}x < minimum {self.lessons['min_volume']}x (learned from DNN failure)", 0.0
        
        # Check ticker history
        if ticker in self.lessons['ticker_history']:
            ticker_data = self.lessons['ticker_history'][ticker]
            if 'win_rate' in ticker_data and ticker_data['win_rate'] < 0.3:
                return False, f"Ticker {ticker} has poor history: {ticker_data['win_rate']:.0%} win rate", 0.0
        
        # POSITION SIZING BY CONVERGENCE (learned from IBRX success)
        position_size = 0.04  # Default 4%
        confidence_reason = []
        
        if convergence >= self.lessons['gold_convergence']:
            # GOLD STANDARD - IBRX @ 85 working great
            position_size = 0.12  # 12% position
            confidence_reason.append(f"GOLD convergence {convergence} (IBRX standard)")
        elif convergence >= self.lessons['optimal_convergence']:
            # OPTIMAL - RDW @ 78 working well
            position_size = 0.08  # 8% position
            confidence_reason.append(f"Strong convergence {convergence} (RDW level)")
        else:
            # ACCEPTABLE - Above minimum but not optimal
            position_size = 0.04  # 4% position
            confidence_reason.append(f"Acceptable convergence {convergence} (above min {self.lessons['min_convergence']})")
        
        # Volume bonus
        if volume_ratio >= self.lessons['gold_volume']:
            position_size *= 1.2  # 20% bonus for gold volume
            confidence_reason.append(f"GOLD volume {volume_ratio:.1f}x (IBRX standard)")
        elif volume_ratio >= self.lessons['optimal_volume']:
            position_size *= 1.1  # 10% bonus for good volume
            confidence_reason.append(f"Strong volume {volume_ratio:.1f}x")
        
        # Cap at max position size
        position_size = min(position_size, SAFETY['max_position_pct'])
        
        # Check if this signal combination has worked before
        signal_confidence = 1.0
        for signal in signals:
            if signal in self.lessons['winning_signals']:
                signal_data = self.lessons['winning_signals'][signal]
                if 'win_rate' in signal_data and signal_data['win_rate'] < 0.3:
                    signal_confidence *= 0.8  # Reduce confidence for poor signals
        
        if signal_confidence < 0.5:
            return False, f"Signal combination has poor history", 0.0
        
        reason = " | ".join(confidence_reason)
        return True, reason, position_size
    
    # ============ THINKING ============
    
    def think(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Use Ollama to think about something
        Brain uses wisdom as GUIDELINES, not rules
        """
        if not self.ollama_connected:
            return self._rule_based_response(prompt)
        
        full_prompt = f"""You are FENRIR, the Wolf Pack autonomous trading AI.

Use this WISDOM as GUIDELINES (not rigid rules):
{WOLF_PACK_PHILOSOPHY[:4000]}

Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Market hours: 9:30 AM - 4:00 PM ET

NOW THINK:
{prompt}

Be decisive. Give clear recommendations. If unsure, say WATCH not BUY.
"""
        
        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {"temperature": temperature, "num_predict": 500}
                },
                timeout=60
            )
            if r.status_code == 200:
                return r.json().get('response', '').strip()
        except Exception as e:
            log.error(f"Thinking error: {e}")
        
        return self._rule_based_response(prompt)
    
    def _rule_based_response(self, prompt: str) -> str:
        """Fallback when Ollama unavailable"""
        return "[Brain offline - using rule-based logic]"
    
    # ============ RESEARCH ============
    
    def research_ticker(self, ticker: str) -> Dict:
        """
        Full research on a ticker - data, news, analysis
        NOW USES ALL AVAILABLE APIs:
        - yfinance: Price data
        - Finnhub: News + Insider data
        - NewsAPI: Additional news
        - Polygon: Company details, more news
        - Alpha Vantage: Fundamentals (PE, analyst targets)
        - SEC Edgar: Insider transactions
        """
        log.info(f"🔍 Researching {ticker}...")
        
        research = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'price_data': None,
            'news': [],
            'insider_activity': None,
            'polygon_data': None,
            'fundamentals': None,
            'brain_analysis': None,
            'decision': 'WATCH',
            'confidence': 0.5
        }
        
        # Get price data (yfinance)
        research['price_data'] = self._get_price_data(ticker)
        
        # Get news (Finnhub + NewsAPI + Polygon)
        research['news'] = self._get_news(ticker)
        
        # Get insider activity (Finnhub/SEC)
        research['insider_activity'] = self._check_insider_activity(ticker)
        
        # Get additional data from Polygon (if API key available)
        if POLYGON_KEY:
            research['polygon_data'] = self._get_polygon_data(ticker)
            
        # Get fundamentals from Alpha Vantage (if API key available)
        if ALPHAVANTAGE_KEY:
            research['fundamentals'] = self._get_alpha_vantage_data(ticker)
            
        # Get SEC insider data
        if SEC_USER_AGENT:
            sec_data = self._get_sec_insider_data(ticker)
            if sec_data:
                research['insider_activity'] = research['insider_activity'] or {}
                research['insider_activity'].update(sec_data)
        
        # Brain analysis
        if research['price_data']:
            research['brain_analysis'] = self._analyze_with_brain(ticker, research)
            
            # Determine decision
            analysis = research['brain_analysis'].upper()
            if 'BUY' in analysis and 'DON\'T BUY' not in analysis and 'AVOID' not in analysis:
                research['decision'] = 'BUY'
                research['confidence'] = 0.7
            elif 'STRONG BUY' in analysis:
                research['decision'] = 'BUY'
                research['confidence'] = 0.85
            elif 'AVOID' in analysis or 'SELL' in analysis:
                research['decision'] = 'AVOID'
                research['confidence'] = 0.8
        
        # Store research
        self._store_research(ticker, research)
        
        return research
    
    def _get_price_data(self, ticker: str) -> Optional[Dict]:
        """Get price data from yfinance"""
        if not YF_AVAILABLE:
            return None
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='3mo')
            
            if hist.empty:
                return None
            
            info = stock.info
            current = hist['Close'].iloc[-1]
            
            # Calculate metrics
            high_52w = info.get('fiftyTwoWeekHigh', hist['High'].max())
            low_52w = info.get('fiftyTwoWeekLow', hist['Low'].min())
            off_high = (high_52w - current) / high_52w * 100
            
            # Volume analysis
            avg_vol = hist['Volume'].mean()
            curr_vol = hist['Volume'].iloc[-1]
            rel_vol = curr_vol / avg_vol if avg_vol > 0 else 1
            
            # Trend
            ma_20 = hist['Close'].rolling(20).mean().iloc[-1] if len(hist) >= 20 else current
            ma_50 = hist['Close'].rolling(50).mean().iloc[-1] if len(hist) >= 50 else current
            
            return {
                'price': float(current),
                'change_1d': float((current - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) if len(hist) > 1 else 0,
                'change_5d': float((current - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5] * 100) if len(hist) > 5 else 0,
                'high_52w': float(high_52w),
                'low_52w': float(low_52w),
                'off_high_pct': float(off_high),
                'volume': int(curr_vol),
                'avg_volume': int(avg_vol),
                'rel_volume': float(rel_vol),
                'ma_20': float(ma_20),
                'ma_50': float(ma_50),
                'above_ma20': current > ma_20,
                'above_ma50': current > ma_50,
                'market_cap': info.get('marketCap', 0),
                'float_shares': info.get('floatShares', 0),
                'short_pct': info.get('shortPercentOfFloat', 0) * 100 if info.get('shortPercentOfFloat') else 0
            }
        except Exception as e:
            log.error(f"Price data error {ticker}: {e}")
            return None
    
    def _get_news(self, ticker: str) -> List[Dict]:
        """Get recent news for ticker from ALL available APIs"""
        news = []
        
        # SOURCE 1: Finnhub (60 calls/min)
        if FINNHUB_KEY:
            try:
                url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}&to={datetime.now().strftime('%Y-%m-%d')}&token={FINNHUB_KEY}"
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    for item in r.json()[:5]:
                        news.append({
                            'headline': item.get('headline', ''),
                            'source': item.get('source', 'Finnhub'),
                            'time': item.get('datetime', 0),
                            'url': item.get('url', '')
                        })
            except Exception as e:
                log.debug(f"Finnhub news error: {e}")
        
        # SOURCE 2: NewsAPI (100/day)
        if NEWSAPI_KEY and len(news) < 3:
            try:
                url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&pageSize=5&apiKey={NEWSAPI_KEY}"
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    for item in r.json().get('articles', [])[:3]:
                        news.append({
                            'headline': item.get('title', ''),
                            'source': item.get('source', {}).get('name', 'NewsAPI'),
                            'time': item.get('publishedAt', ''),
                            'url': item.get('url', '')
                        })
            except Exception as e:
                log.debug(f"NewsAPI error: {e}")
        
        # SOURCE 3: Polygon (5/min free)
        if POLYGON_KEY and len(news) < 3:
            try:
                url = f"https://api.polygon.io/v2/reference/news?ticker={ticker}&limit=5&apiKey={POLYGON_KEY}"
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    for item in r.json().get('results', [])[:3]:
                        news.append({
                            'headline': item.get('title', ''),
                            'source': item.get('publisher', {}).get('name', 'Polygon'),
                            'time': item.get('published_utc', ''),
                            'url': item.get('article_url', '')
                        })
            except Exception as e:
                log.debug(f"Polygon news error: {e}")
        
        # Remove duplicates by headline
        seen = set()
        unique_news = []
        for n in news:
            if n['headline'] not in seen:
                seen.add(n['headline'])
                unique_news.append(n)
        
        return unique_news[:10]  # Max 10 news items
    
    def _get_polygon_data(self, ticker: str) -> Optional[Dict]:
        """Get additional data from Polygon API"""
        if not POLYGON_KEY:
            return None
        
        try:
            # Get ticker details
            url = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={POLYGON_KEY}"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json().get('results', {})
                return {
                    'name': data.get('name', ''),
                    'market_cap': data.get('market_cap', 0),
                    'shares_outstanding': data.get('share_class_shares_outstanding', 0),
                    'description': data.get('description', '')[:200] if data.get('description') else '',
                    'sic_description': data.get('sic_description', ''),
                    'homepage': data.get('homepage_url', '')
                }
        except Exception as e:
            log.debug(f"Polygon data error: {e}")
        
        return None
    
    def _get_alpha_vantage_data(self, ticker: str) -> Optional[Dict]:
        """Get fundamental data from Alpha Vantage"""
        if not ALPHAVANTAGE_KEY:
            return None
        
        try:
            # Company overview
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHAVANTAGE_KEY}"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                if 'Symbol' in data:
                    return {
                        'pe_ratio': float(data.get('PERatio', 0) or 0),
                        'peg_ratio': float(data.get('PEGRatio', 0) or 0),
                        'eps': float(data.get('EPS', 0) or 0),
                        'revenue_ttm': float(data.get('RevenueTTM', 0) or 0),
                        'profit_margin': float(data.get('ProfitMargin', 0) or 0),
                        'analyst_target': float(data.get('AnalystTargetPrice', 0) or 0),
                        '52w_high': float(data.get('52WeekHigh', 0) or 0),
                        '52w_low': float(data.get('52WeekLow', 0) or 0),
                        'beta': float(data.get('Beta', 0) or 0),
                        'dividend_yield': float(data.get('DividendYield', 0) or 0),
                        'sector': data.get('Sector', ''),
                        'industry': data.get('Industry', '')
                    }
        except Exception as e:
            log.debug(f"Alpha Vantage error: {e}")
        
        return None
    
    def _get_sec_insider_data(self, ticker: str) -> Optional[Dict]:
        """Get insider trading data from SEC EDGAR"""
        if not SEC_USER_AGENT:
            return None
        
        try:
            # Get company CIK from SEC
            headers = {'User-Agent': SEC_USER_AGENT}
            
            # First get insider sentiment from Finnhub as backup
            insider_data = {'recent_buys': 0, 'recent_sells': 0, 'net_activity': 'NEUTRAL'}
            
            if FINNHUB_KEY:
                url = f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={ticker}&token={FINNHUB_KEY}"
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    transactions = r.json().get('data', [])
                    buys = sum(1 for t in transactions if t.get('transactionCode') == 'P')
                    sells = sum(1 for t in transactions if t.get('transactionCode') == 'S')
                    insider_data['recent_buys'] = buys
                    insider_data['recent_sells'] = sells
                    if buys > sells:
                        insider_data['net_activity'] = 'BUYING'
                    elif sells > buys:
                        insider_data['net_activity'] = 'SELLING'
            
            return insider_data
            
        except Exception as e:
            log.debug(f"SEC insider data error: {e}")
        
        return None
    
    def _check_insider_activity(self, ticker: str) -> Optional[Dict]:
        """Check for insider buying (SEC Form 4)"""
        # This would scrape SEC EDGAR - simplified version
        try:
            # Use Finnhub insider sentiment as proxy
            if FINNHUB_KEY:
                url = f"https://finnhub.io/api/v1/stock/insider-sentiment?symbol={ticker}&from={(datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')}&to={datetime.now().strftime('%Y-%m-%d')}&token={FINNHUB_KEY}"
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    data = r.json().get('data', [])
                    if data:
                        recent = data[-1] if data else {}
                        return {
                            'mspr': recent.get('mspr', 0),  # Monthly share purchase ratio
                            'change': recent.get('change', 0)
                        }
        except Exception as e:
            log.debug(f"Insider check error: {e}")
        
        return None
    
    def _analyze_with_brain(self, ticker: str, research: Dict) -> str:
        """Get brain's analysis - USES ALL AVAILABLE DATA"""
        data = research['price_data']
        news = research['news']
        insider = research['insider_activity']
        polygon = research.get('polygon_data', {})
        fundamentals = research.get('fundamentals', {})
        
        news_summary = "\n".join([f"- {n['headline']}" for n in news[:5]]) if news else "No recent news"
        insider_summary = f"Insider sentiment: {insider}" if insider else "No insider data"
        
        # Build fundamentals summary
        fund_summary = "No fundamental data"
        if fundamentals:
            fund_summary = f"""
Sector: {fundamentals.get('sector', 'N/A')} | Industry: {fundamentals.get('industry', 'N/A')}
P/E: {fundamentals.get('pe_ratio', 'N/A')} | PEG: {fundamentals.get('peg_ratio', 'N/A')}
EPS: ${fundamentals.get('eps', 'N/A')} | Revenue TTM: ${fundamentals.get('revenue_ttm', 0)/1e9:.2f}B
Analyst Target: ${fundamentals.get('analyst_target', 'N/A')} | Beta: {fundamentals.get('beta', 'N/A')}
52W High: ${fundamentals.get('52w_high', 'N/A')} | 52W Low: ${fundamentals.get('52w_low', 'N/A')}"""
        
        # Build company summary from Polygon
        company_summary = ""
        if polygon:
            company_summary = f"""
Company: {polygon.get('name', ticker)}
Market Cap: ${polygon.get('market_cap', 0)/1e9:.2f}B
Shares Outstanding: {polygon.get('shares_outstanding', 0)/1e6:.1f}M
Industry: {polygon.get('sic_description', 'N/A')}"""
        
        prompt = f"""
ANALYZE {ticker} FOR TRADING:

PRICE DATA:
- Current: ${data['price']:.2f}
- 1-Day Change: {data['change_1d']:+.1f}%
- 5-Day Change: {data['change_5d']:+.1f}%
- Off 52W High: {data['off_high_pct']:.1f}%
- Relative Volume: {data['rel_volume']:.1f}x
- Above 20MA: {data['above_ma20']}
- Above 50MA: {data['above_ma50']}
- Float: {data['float_shares']/1e6:.1f}M shares
- Short Interest: {data['short_pct']:.1f}%
{company_summary}

FUNDAMENTALS:
{fund_summary}

RECENT NEWS (from Finnhub, NewsAPI, Polygon):
{news_summary}

INSIDER ACTIVITY:
{insider_summary}

QUESTIONS:
1. Is this a WOUNDED PREY setup (20-40% off highs, healthy)?
2. Is this a HEAD HUNTER setup (low float, catalyst, squeeze)?
3. Is this a GAP-AND-GO RUNNER (premarket move holding)?
4. Chart health: HEALTHY or UNHEALTHY?
5. Do fundamentals support a move?

DECIDE: BUY (with entry/stop/target), WATCH, or AVOID
If BUY, explain why and give specific prices.
"""
        return self.think(prompt)
    
    def _store_research(self, ticker: str, research: Dict):
        """Store research in database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO research (timestamp, source, ticker, content, relevance) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().isoformat(), 'full_research', ticker, json.dumps(research, default=str), research['confidence'])
        )
        conn.commit()
        conn.close()
    
    # ============ 4AM PREMARKET SCANNER ============
    
    def scan_premarket_runners(self) -> List[Dict]:
        """
        THE 4AM PREMARKET SCANNER
        
        This is WHERE THE MONEY IS MADE.
        Scans for gap-and-go runners BEFORE market open.
        
        CRITERIA:
        1. Gap up 10%+ premarket
        2. Low float (<50M, ideally <20M)
        3. REAL catalyst (FDA, earnings, deal)
        4. Heavy premarket volume
        5. Catalyst matches sector thesis
        
        THE BIOTECH FORMULA:
        LOW FLOAT + FDA CATALYST + POSITIVE NEWS = 100-500%
        """
        log.info("=" * 60)
        log.info("🌅 4AM PREMARKET SCANNER ACTIVATED")
        log.info("=" * 60)
        
        runners = []
        faders = []
        
        # PHASE 1: Check FDA Calendar for TODAY's catalysts
        today = datetime.now().strftime('%Y-%m-%d')
        todays_fda_plays = []
        
        for ticker, info in FDA_CALENDAR.items():
            if info['date'] <= today <= info['date']:
                drug = info.get('drug', info.get('indication', 'FDA event'))
                notes = info.get('notes', '')
                log.info(f"🔥 FDA CATALYST TODAY: {ticker} - {drug} ({notes})")
                todays_fda_plays.append(ticker)
        
        # PHASE 2: Scan ALL sectors for gaps
        scan_targets = []
        
        # Priority 1: FDA plays today
        scan_targets.extend(todays_fda_plays)
        
        # Priority 2: FDA plays this week
        scan_targets.extend(UNIVERSE.get('fda_plays', []))
        
        # Priority 3: Core watchlist (proven movers)
        scan_targets.extend(UNIVERSE.get('core_watchlist', []))
        
        # Priority 4: Low float biotech (biggest runners)
        scan_targets.extend(UNIVERSE.get('low_float_biotech', []))
        
        # Priority 5: Hot sectors
        scan_targets.extend(UNIVERSE.get('defense_space', [])[:5])
        scan_targets.extend(UNIVERSE.get('nuclear', [])[:3])
        scan_targets.extend(UNIVERSE.get('ai_quantum', [])[:3])
        
        # Remove duplicates, keep order
        seen = set()
        unique_targets = []
        for t in scan_targets:
            if t not in seen:
                seen.add(t)
                unique_targets.append(t)
        
        log.info(f"📊 Scanning {len(unique_targets)} targets...")
        
        # PHASE 3: Check each ticker for gap
        for ticker in unique_targets[:50]:  # Limit to 50 for speed
            try:
                gap_data = self._check_premarket_gap(ticker)
                
                if gap_data and gap_data['gap_pct'] >= 5:  # 5%+ gap
                    log.info(f"🚀 GAP DETECTED: {ticker} +{gap_data['gap_pct']:.1f}%")
                    
                    # Full research on gapper
                    research = self.research_ticker(ticker)
                    
                    # Classify: RUNNER or FADER?
                    classification = self._classify_runner_vs_fader(ticker, gap_data, research)
                    
                    research['gap_data'] = gap_data
                    research['classification'] = classification
                    
                    if classification['verdict'] == 'RUNNER':
                        runners.append(research)
                        log.info(f"✅ RUNNER CANDIDATE: {ticker} - {classification['reason']}")
                    else:
                        faders.append(research)
                        log.info(f"⚠️  FADE CANDIDATE: {ticker} - {classification['reason']}")
                
                time.sleep(0.2)  # Rate limit
                
            except Exception as e:
                log.debug(f"Scan error {ticker}: {e}")
        
        # Sort runners by conviction
        runners.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Log summary
        log.info("=" * 60)
        log.info(f"🎯 PREMARKET SUMMARY:")
        log.info(f"   RUNNERS: {len(runners)}")
        for r in runners[:5]:
            log.info(f"      {r['ticker']}: +{r.get('gap_data', {}).get('gap_pct', 0):.1f}% gap | {r['confidence']:.0%} confidence")
        log.info(f"   FADERS: {len(faders)} (avoiding)")
        log.info("=" * 60)
        
        # Store for later analysis
        self._log_scan_result('premarket_4am', {
            'runners': [r['ticker'] for r in runners],
            'faders': [f['ticker'] for f in faders],
            'timestamp': datetime.now().isoformat()
        })
        
        return runners
    
    def _check_premarket_gap(self, ticker: str) -> Optional[Dict]:
        """Check if ticker has premarket gap"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get yesterday's close and current price
            hist = stock.history(period='5d')
            if len(hist) < 2:
                return None
            
            prev_close = hist['Close'].iloc[-2]
            current = hist['Close'].iloc[-1]
            
            # Try to get premarket price (if available)
            info = stock.info
            premarket_price = info.get('preMarketPrice', current)
            
            if premarket_price and premarket_price > 0:
                gap_pct = ((premarket_price - prev_close) / prev_close) * 100
            else:
                gap_pct = ((current - prev_close) / prev_close) * 100
            
            volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            
            return {
                'prev_close': prev_close,
                'premarket_price': premarket_price or current,
                'gap_pct': gap_pct,
                'premarket_volume': volume,
                'relative_volume': volume / avg_volume if avg_volume > 0 else 0,
                'float_shares': info.get('floatShares', 0),
                'market_cap': info.get('marketCap', 0)
            }
            
        except Exception as e:
            log.debug(f"Gap check error {ticker}: {e}")
            return None
    
    def _classify_runner_vs_fader(self, ticker: str, gap_data: Dict, research: Dict) -> Dict:
        """
        THE CRITICAL DECISION: Is this a RUNNER or FADER?
        
        NOW ENHANCED WITH LEARNING ENGINE - Uses lessons from historical trades!
        
        RUNNER SIGNS:
        - Low float (<20M)
        - REAL catalyst (FDA, earnings, partnership)
        - Heavy volume (3x+ normal)
        - Clean chart (breaking out of base)
        - News from reputable source
        
        FADER SIGNS:
        - High float (>100M)
        - No real catalyst
        - Light volume
        - Already extended
        - Pump from newsletter/social
        
        ⚠️  LESSONS APPLIED FROM DNN FAILURE & IBRX SUCCESS ⚠️
        - Reject volume < 1.5x (DNN @ 1.2x failed)
        - Reject if no fresh catalyst (DNN = stale intel)
        - Prioritize volume 2.0x+ (IBRX @ 2.8x succeeded)
        """
        score = 0
        reasons = []
        
        float_shares = gap_data.get('float_shares', 0)
        rel_volume = gap_data.get('relative_volume', 0)
        news = research.get('news', [])
        
        # 🚨 HARD FILTER FROM LESSONS - Volume must be >= 1.5x
        if rel_volume < self.lessons['min_volume']:
            score -= 5  # Instant rejection
            reasons.append(f"⛔ Volume {rel_volume:.1f}x < {self.lessons['min_volume']}x (DNN lesson: FAILED @ 1.2x)")
        
        # FLOAT CHECK
        if float_shares and float_shares < 20_000_000:
            score += 3
            reasons.append(f"LOW FLOAT: {float_shares/1_000_000:.1f}M (explosive potential)")
        elif float_shares and float_shares < 50_000_000:
            score += 1
            reasons.append(f"Medium float: {float_shares/1_000_000:.1f}M")
        elif float_shares and float_shares > 100_000_000:
            score -= 2
            reasons.append(f"HIGH FLOAT: {float_shares/1_000_000:.1f}M (hard to move)")
        
        # VOLUME CHECK - ENHANCED WITH LESSONS
        if rel_volume >= 5:
            score += 3
            reasons.append(f"MASSIVE VOLUME: {rel_volume:.1f}x normal")
        elif rel_volume >= 3:
            score += 2
            reasons.append(f"Heavy volume: {rel_volume:.1f}x normal")
        elif rel_volume >= 1.5:
            score += 1
            reasons.append(f"Good volume: {rel_volume:.1f}x")
        else:
            score -= 1
            reasons.append(f"Light volume: {rel_volume:.1f}x (suspicious)")
        
        # NEWS/CATALYST CHECK
        catalyst_keywords = ['FDA', 'approval', 'phase 3', 'clinical', 'earnings', 
                           'partnership', 'acquisition', 'contract', 'breakthrough']
        
        has_real_catalyst = False
        if news:
            for n in news[:3]:
                headline = n.get('headline', '').lower()
                if any(kw.lower() in headline for kw in catalyst_keywords):
                    has_real_catalyst = True
                    score += 3
                    reasons.append(f"REAL CATALYST: {n.get('headline', '')[:50]}...")
                    break
        
        if not has_real_catalyst:
            score -= 1
            reasons.append("No clear catalyst found (proceed with caution)")
        
        # FDA CALENDAR CHECK
        if ticker in FDA_CALENDAR:
            fda_info = FDA_CALENDAR[ticker]
            score += 3
            catalyst_desc = fda_info.get('drug', fda_info.get('indication', 'FDA event'))
            reasons.append(f"FDA DATE: {fda_info['date']} - {catalyst_desc}")
        
        # GAP SIZE
        gap_pct = gap_data.get('gap_pct', 0)
        if 10 <= gap_pct <= 30:
            score += 1
            reasons.append(f"Good gap size: +{gap_pct:.1f}%")
        elif gap_pct > 50:
            score -= 1
            reasons.append(f"Gap too big: +{gap_pct:.1f}% (chasing risk)")
        
        # VERDICT
        if score >= 5:
            verdict = 'RUNNER'
            confidence = 'HIGH'
        elif score >= 3:
            verdict = 'RUNNER'
            confidence = 'MEDIUM'
        elif score >= 1:
            verdict = 'WATCH'
            confidence = 'LOW'
        else:
            verdict = 'FADER'
            confidence = 'AVOID'
        
        return {
            'verdict': verdict,
            'confidence': confidence,
            'score': score,
            'reason': ' | '.join(reasons[:3])
        }
    
    def _log_scan_result(self, scan_type: str, data: Dict):
        """Log scan result for learning"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO research (timestamp, source, ticker, content, relevance) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().isoformat(), scan_type, 'SCAN', json.dumps(data), 0.5)
        )
        conn.commit()
        conn.close()
    
    def _track_momentum(self, scan_results: List[Dict], scan_time: str):
        """
        🔥 MOMENTUM TRACKER - Watch for SUSTAINED runners
        
        Tracks tickers across multiple scans to find sustained strength.
        Not just flash-in-the-pan - looking for consistent building momentum.
        
        KEY INSIGHT: Real runners appear in MULTIPLE scans with INCREASING volume
        """
        timestamp = datetime.now()
        
        for result in scan_results:
            ticker = result['ticker']
            gap_pct = result.get('gap_data', {}).get('gap_pct', 0)
            volume = result.get('gap_data', {}).get('relative_volume', 0)
            price = result.get('price', 0)
            
            scan_data = {
                'time': scan_time,
                'timestamp': timestamp,
                'gap_pct': gap_pct,
                'volume_ratio': volume,
                'price': price,
                'classification': result.get('classification', {}).get('verdict', 'UNKNOWN')
            }
            
            # Add to tracker
            if ticker not in self.momentum_tracker:
                self.momentum_tracker[ticker] = []
            
            self.momentum_tracker[ticker].append(scan_data)
            
            # SUSTAINED RUNNER DETECTION
            scans = self.momentum_tracker[ticker]
            
            if len(scans) >= 2:
                # Check if momentum is building
                first = scans[0]
                latest = scans[-1]
                
                # Strong criteria: appeared 2+ times, gap holding (not fading), volume increasing
                gap_holding = latest['gap_pct'] >= first['gap_pct'] * 0.85  # Allow 15% fade
                volume_building = latest['volume_ratio'] >= first['volume_ratio'] * 0.9  # Volume not dying
                is_runner = latest['classification'] == 'RUNNER'
                
                if gap_holding and volume_building and is_runner:
                    if ticker not in [r['ticker'] for r in self.sustained_runners]:
                        log.info(f"🔥 SUSTAINED RUNNER DETECTED: {ticker}")
                        log.info(f"   First seen: {first['time']} @ {first['gap_pct']:.1f}% gap, {first['volume_ratio']:.1f}x vol")
                        log.info(f"   Now: {latest['time']} @ {latest['gap_pct']:.1f}% gap, {latest['volume_ratio']:.1f}x vol")
                        log.info(f"   ✅ GAP HOLDING + VOLUME SUSTAINED = REAL STRENGTH")
                        
                        self.sustained_runners.append({
                            'ticker': ticker,
                            'first_seen': first['time'],
                            'scans_appeared': len(scans),
                            'gap_trend': 'HOLDING' if gap_holding else 'FADING',
                            'volume_trend': 'BUILDING' if volume_building else 'DYING',
                            'latest_data': latest
                        })
    
    def get_sustained_runners(self) -> List[Dict]:
        """
        Return list of sustained runners (appeared in 2+ scans with strength)
        """
        return self.sustained_runners
    
    def scan_premarket(self) -> List[Dict]:
        """
        Legacy premarket scan - now redirects to enhanced scanner
        """
        return self.scan_premarket_runners()
    
    # ============ REAL PREMARKET GAINER SCANNER ============
    
    def scan_real_premarket_gainers(self) -> List[Dict]:
        """
        🔥 HUNT THE REAL MOVERS - NOT JUST WATCHLIST
        
        This scans TRADINGVIEW/FINVIZ style for what's ACTUALLY gapping.
        Not limited to our watchlist - finds the unknown movers.
        
        Uses multiple sources to find premarket gainers:
        1. Yahoo Finance screener
        2. Finnhub (if available)
        3. Cross-reference with our watchlist
        """
        log.info("=" * 60)
        log.info("🔥 REAL PREMARKET GAINER SCANNER")
        log.info("   Hunting what's ACTUALLY moving...")
        log.info("=" * 60)
        
        all_gainers = []
        
        # METHOD 1: Scan ALL SECTORS from UNIVERSE - not just biotech!
        # The system has MULTIPLE strategies across ALL sectors
        hot_sectors = []
        
        # Priority order - most likely runners first
        priority_order = [
            'fda_plays',           # FDA catalysts (highest priority)
            'core_watchlist',      # Proven movers
            'low_float_biotech',   # Biotech runners
            'defense_space',       # Space/Defense momentum
            'ai_quantum',          # AI/Quantum tech
            'nuclear',             # Nuclear energy
            'defense',             # Defense contractors
            'momentum',            # Momentum plays
            'biotech',             # General biotech
        ]
        
        # Build ticker list from ALL sectors
        for sector in priority_order:
            if sector in UNIVERSE:
                hot_sectors.extend(UNIVERSE[sector])
        
        # Remove duplicates while keeping priority order
        seen = set()
        unique_sectors = []
        for t in hot_sectors:
            if t not in seen:
                seen.add(t)
                unique_sectors.append(t)
        hot_sectors = unique_sectors
        
        log.info(f"📊 Scanning {len(hot_sectors)} potential runners...")
        
        # Sequential scanning (more reliable than parallel)
        gainers = []
        for ticker in hot_sectors:
            try:
                gap = self._check_premarket_gap(ticker)
                if gap and gap.get('gap_pct', 0) >= 3:  # 3%+ gap
                    gainers.append({
                        'ticker': ticker,
                        'gap_pct': gap['gap_pct'],
                        'volume_ratio': gap.get('relative_volume', 0),
                        'float': gap.get('float_shares', 0),
                        'price': gap.get('premarket_price', 0),
                        'prev_close': gap.get('prev_close', 0)
                    })
                    log.info(f"   🚀 {ticker}: +{gap['gap_pct']:.1f}%")
            except Exception as e:
                log.debug(f"   Skip {ticker}: {e}")
        
        # Sort by gap percentage
        gainers.sort(key=lambda x: x['gap_pct'], reverse=True)
        
        # Top 20 gainers
        top_gainers = gainers[:20]
        
        log.info(f"🎯 Found {len(gainers)} stocks gapping 3%+")
        log.info(f"")
        log.info(f"   📊 TOP MOVERS WITH VOLUME:")
        for i, g in enumerate(top_gainers[:15], 1):
            emoji = '🚀' if g['gap_pct'] >= 10 else ('🔥' if g['gap_pct'] >= 5 else '📈')
            float_str = f"{g['float']/1e6:.0f}M" if g.get('float') else "N/A"
            log.info(f"   {i:2}. {emoji} {g['ticker']:6} | Gap: {g['gap_pct']:+6.1f}% | Vol: {g['volume_ratio']:5.1f}x | Float: {float_str:>6} | ${g['price']:.2f}")
        log.info(f"")
        
        return top_gainers
    
    def generate_intel_report(self, save_path: str = None) -> str:
        """
        🐺 GENERATE MORNING INTEL REPORT
        
        Creates a comprehensive report for Tyr to review at 7 AM.
        Saved to file so it's ready when you wake up.
        """
        log.info("=" * 60)
        log.info("📝 GENERATING INTEL REPORT...")
        log.info("=" * 60)
        
        report_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # Get all data - just gainers, skip slow full research
        real_gainers = self.scan_real_premarket_gainers()
        # Skip full premarket scan for speed: watchlist_check = self.scan_premarket_runners()
        
        # Get positions
        positions = []
        if self.alpaca_connected:
            try:
                pos = self.trading_client.get_all_positions()
                for p in pos:
                    positions.append({
                        'ticker': p.symbol,
                        'qty': float(p.qty),
                        'entry': float(p.avg_entry_price),
                        'current': float(p.current_price),
                        'pnl': float(p.unrealized_pl),
                        'pnl_pct': float(p.unrealized_plpc) * 100
                    })
            except:
                pass
        
        # Get account
        account_value = 0
        if self.alpaca_connected:
            try:
                acc = self.trading_client.get_account()
                account_value = float(acc.portfolio_value)
            except:
                pass
        
        # Build report
        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     🐺 WOLF BRAIN INTEL REPORT                                       ║
║     Generated: {report_time}                                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════
📊 ACCOUNT STATUS
═══════════════════════════════════════════════════════════════════════

Portfolio Value: ${account_value:,.2f}

CURRENT POSITIONS:
"""
        
        if positions:
            for p in positions:
                emoji = '🟢' if p['pnl'] >= 0 else '🔴'
                report += f"  {emoji} {p['ticker']:6} | {p['qty']:.0f} shares @ ${p['entry']:.2f} | Now ${p['current']:.2f} | P&L: ${p['pnl']:+.2f} ({p['pnl_pct']:+.1f}%)\n"
        else:
            report += "  No open positions\n"
        
        report += f"""
═══════════════════════════════════════════════════════════════════════
🔥 TOP PREMARKET GAINERS (What's ACTUALLY Moving)
═══════════════════════════════════════════════════════════════════════
"""
        
        if real_gainers:
            for i, g in enumerate(real_gainers[:15], 1):
                emoji = '🚀' if g['gap_pct'] >= 10 else ('🔥' if g['gap_pct'] >= 5 else '📈')
                float_str = f"{g['float']/1e6:.0f}M" if g['float'] else "N/A"
                
                # Check if it's in our watchlist
                in_watchlist = "⭐ WATCHLIST" if g['ticker'] in UNIVERSE.get('fda_plays', []) + UNIVERSE.get('core_watchlist', []) else ""
                
                # Check FDA calendar
                fda_note = ""
                if g['ticker'] in FDA_CALENDAR:
                    fda_note = f"📅 FDA: {FDA_CALENDAR[g['ticker']]['date']}"
                
                report += f"  {i:2}. {emoji} {g['ticker']:6} | Gap: {g['gap_pct']:+6.1f}% | Vol: {g['volume_ratio']:4.1f}x | Float: {float_str:>8} {in_watchlist} {fda_note}\n"
        else:
            report += "  No significant gaps detected\n"
        
        report += f"""
═══════════════════════════════════════════════════════════════════════
🎯 RUNNER vs FADER CLASSIFICATION
═══════════════════════════════════════════════════════════════════════
"""
        
        # Classify top gainers
        for g in real_gainers[:10]:
            classification = self._classify_runner_vs_fader(
                g['ticker'], 
                {'gap_pct': g['gap_pct'], 'relative_volume': g['volume_ratio'], 'float_shares': g['float']},
                {'news': []}
            )
            
            if classification['verdict'] == 'RUNNER':
                emoji = '✅'
            elif classification['verdict'] == 'WATCH':
                emoji = '👀'
            else:
                emoji = '❌'
            
            report += f"  {emoji} {g['ticker']:6} | {classification['verdict']:6} ({classification['confidence']}) | {classification['reason'][:60]}\n"
        
        report += f"""
═══════════════════════════════════════════════════════════════════════
📅 FDA CALENDAR - UPCOMING CATALYSTS
═══════════════════════════════════════════════════════════════════════
"""
        
        # Sort FDA calendar by date
        for ticker, info in sorted(FDA_CALENDAR.items(), key=lambda x: x[1]['date']):
            days_away = (datetime.strptime(info['date'], '%Y-%m-%d') - datetime.now()).days
            if days_away >= 0:
                urgency = "🔴 IMMINENT" if days_away <= 3 else ("🟡 SOON" if days_away <= 7 else "🟢")
                drug = info.get('drug', info.get('indication', 'FDA event'))
                notes = info.get('notes', '')
                report += f"  {urgency} {ticker:6} | {info['date']} ({days_away} days) | {drug} | {notes}\n"
        
        report += f"""
═══════════════════════════════════════════════════════════════════════
🧠 BRAIN'S MORNING THOUGHTS
═══════════════════════════════════════════════════════════════════════
"""
        
        # Get brain's analysis
        top_3 = real_gainers[:3] if real_gainers else []
        if top_3 and self.ollama_connected:
            thoughts = self.think(f"""
Morning scan complete. Top 3 premarket gainers:
1. {top_3[0]['ticker'] if len(top_3) > 0 else 'N/A'}: +{top_3[0]['gap_pct']:.1f}% gap
2. {top_3[1]['ticker'] if len(top_3) > 1 else 'N/A'}: +{top_3[1]['gap_pct']:.1f}% gap  
3. {top_3[2]['ticker'] if len(top_3) > 2 else 'N/A'}: +{top_3[2]['gap_pct']:.1f}% gap

FDA plays to watch: AQST (Jan 31), IRON (Jan 31)
Current positions: {[p['ticker'] for p in positions]}

What's your assessment? Which ones are real? Which to avoid?
What's the play for today?

Keep it brief - key points only.
""")
            report += f"\n{thoughts}\n"
        else:
            report += "\n  Brain offline - manual analysis required\n"
        
        report += f"""
═══════════════════════════════════════════════════════════════════════
🎬 ACTION PLAN
═══════════════════════════════════════════════════════════════════════

RUNNERS TO WATCH (Gap + Volume + Catalyst):
"""
        
        # Filter for true runners
        true_runners = [g for g in real_gainers if g['gap_pct'] >= 5 and g['volume_ratio'] >= 1.5]
        for r in true_runners[:5]:
            report += f"  🎯 {r['ticker']} - Gap {r['gap_pct']:+.1f}%, Volume {r['volume_ratio']:.1f}x\n"
        
        report += f"""
AVOID (Likely Faders):
"""
        faders = [g for g in real_gainers if g['volume_ratio'] < 1 and g['gap_pct'] < 10]
        for f in faders[:3]:
            report += f"  ❌ {f['ticker']} - Low volume fade risk\n"
        
        report += f"""
═══════════════════════════════════════════════════════════════════════

Report generated by Wolf Brain 🐺
The pack hunts at 4 AM.

═══════════════════════════════════════════════════════════════════════
"""
        
        # Save report to file
        if save_path is None:
            save_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'data', 'wolf_brain',
                f'intel_report_{datetime.now().strftime("%Y%m%d_%H%M")}.txt'
            )
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        log.info(f"📄 Intel report saved to: {save_path}")
        
        # Also save a "latest" copy for easy access
        latest_path = os.path.join(os.path.dirname(save_path), 'LATEST_INTEL_REPORT.txt')
        with open(latest_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        log.info(f"📄 Latest report: {latest_path}")
        
        return report
    
    def scan_market_hours(self) -> List[Dict]:
        """
        During market hours - look for setups developing
        """
        log.info("☀️ MARKET HOURS SCAN...")
        
        opportunities = []
        
        # Quick scan of all sectors
        all_tickers = []
        for sector, tickers in UNIVERSE.items():
            all_tickers.extend(tickers[:5])  # Top 5 from each
        
        # Remove duplicates
        all_tickers = list(set(all_tickers))
        
        # Parallel scanning for speed
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(self.research_ticker, all_tickers[:20]))
        
        for research in results:
            if research and research['decision'] == 'BUY':
                opportunities.append(research)
        
        return opportunities
    
    # ============ TRADING ============
    
    def execute_trade(self, ticker: str, side: str, quantity: int,
                     entry_price: float, stop_price: float, target_price: float,
                     strategy: str, reasoning: str, convergence: float = 0,
                     volume_ratio: float = 0, signals: List[str] = None) -> Dict:
        """
        Execute a trade with proper risk management
        
        🧠 NOW ENHANCED WITH LEARNING ENGINE CHECKS
        - Queries historical win rates before trading
        - Applies lessons from past trades
        - Dynamic position sizing based on convergence
        """
        signals = signals or [strategy]
        
        # 🧠 LEARNING ENGINE CHECK - Should we take this trade?
        if convergence > 0 and volume_ratio > 0:
            should_trade, reason, position_size_pct = self.should_take_trade(
                ticker, convergence, volume_ratio, signals, strategy
            )
            
            if not should_trade:
                log.warning(f"⛔ TRADE REJECTED BY LEARNING ENGINE: {ticker}")
                log.warning(f"   Reason: {reason}")
                self._log_decision('trade_rejected', ticker, f"Would {side} {quantity}", reason, 0.0)
                return {'success': False, 'error': f'Learning engine rejection: {reason}'}
            
            # Use learning engine position sizing
            log.info(f"✅ LEARNING ENGINE APPROVED: {ticker}")
            log.info(f"   {reason}")
            log.info(f"   Position size: {position_size_pct:.1%}")
            
            # Recalculate quantity based on learned position size
            if self.alpaca_connected:
                account = self.trading_client.get_account()
                portfolio_value = float(account.portfolio_value)
                position_value = portfolio_value * position_size_pct
                quantity = int(position_value / entry_price)
        
        # Safety checks
        if self.daily_trades >= SAFETY['max_daily_trades']:
            log.warning(f"⚠️  Max daily trades reached ({SAFETY['max_daily_trades']})")
            return {'success': False, 'error': 'Max daily trades'}
        
        if not self.alpaca_connected:
            log.error("❌ Alpaca not connected")
            return {'success': False, 'error': 'Not connected'}
        
        if self.dry_run:
            log.info(f"🧪 DRY RUN: Would {side} {quantity} {ticker} @ ${entry_price:.2f}")
            self._log_decision('trade', ticker, f"{side} {quantity}", reasoning, 0.8)
            return {'success': True, 'dry_run': True}
        
        try:
            # Check position size limit
            account = self.trading_client.get_account()
            portfolio_value = float(account.portfolio_value)
            position_value = quantity * entry_price
            
            if position_value / portfolio_value > SAFETY['max_position_pct']:
                log.warning(f"⚠️  Position too large: {position_value/portfolio_value:.1%} > {SAFETY['max_position_pct']:.0%}")
                return {'success': False, 'error': 'Position too large'}
            
            # Execute order
            order_side = OrderSide.BUY if side.upper() == 'BUY' else OrderSide.SELL
            
            order = MarketOrderRequest(
                symbol=ticker,
                qty=quantity,
                side=order_side,
                time_in_force=TimeInForce.DAY
            )
            
            result = self.trading_client.submit_order(order)
            
            log.info(f"✅ EXECUTED: {side} {quantity} {ticker} | Order: {result.id}")
            
            # Store trade
            self._store_trade(ticker, side, quantity, entry_price, stop_price, 
                            target_price, strategy, reasoning)
            
            # Track for stop management
            self.positions[ticker] = {
                'quantity': quantity,
                'entry': entry_price,
                'stop': stop_price,
                'target': target_price,
                'strategy': strategy,  # Store strategy for learning
                'order_id': str(result.id)
            }
            
            self.daily_trades += 1
            
            return {
                'success': True,
                'order_id': str(result.id),
                'ticker': ticker,
                'quantity': quantity
            }
            
        except Exception as e:
            log.error(f"❌ Trade failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def manage_positions(self):
        """
        Check positions and manage exits
        
        🚨 AUTO STOP-LOSS & TAKE-PROFIT 🚨
        Wolf Brain manages positions autonomously:
        - Sell on stop loss hit
        - Take partial profits at targets
        - Learn from losses
        """
        if not self.alpaca_connected:
            return
        
        try:
            positions = self.trading_client.get_all_positions()
            
            for pos in positions:
                ticker = pos.symbol
                current_price = float(pos.current_price)
                entry_price = float(pos.avg_entry_price)
                qty = int(pos.qty)
                pnl_pct = (current_price - entry_price) / entry_price * 100
                
                # Check if we have stop info
                if ticker in self.positions:
                    stop_price = self.positions[ticker].get('stop', entry_price * 0.92)
                    target_price = self.positions[ticker].get('target', entry_price * 1.20)
                    strategy = self.positions[ticker].get('strategy', 'UNKNOWN')
                    
                    # 🛑 STOP LOSS HIT - LEARN FROM IT
                    if current_price <= stop_price:
                        log.warning(f"🛑 STOP HIT: {ticker} @ ${current_price:.2f} (stop was ${stop_price:.2f})")
                        log.warning(f"   Loss: {pnl_pct:.1f}%")
                        
                        self._close_position(ticker, qty, "Stop loss triggered")
                        
                        # 🧠 LEARN FROM THIS LOSS
                        self._analyze_loss(ticker, entry_price, current_price, stop_price, strategy, pnl_pct)
                    
                    # 🎯 TARGET HIT - TAKE PROFIT
                    elif current_price >= target_price:
                        log.info(f"🎯 TARGET HIT: {ticker} @ ${current_price:.2f}")
                        log.info(f"   Profit: {pnl_pct:.1f}%")
                        
                        # Sell half, move stop to breakeven
                        half_qty = qty // 2
                        if half_qty > 0:
                            self._close_position(ticker, half_qty, "Target 1 reached - taking profits")
                            self.positions[ticker]['stop'] = entry_price  # Move to breakeven
                            self.positions[ticker]['quantity'] = qty - half_qty
                            log.info(f"   📈 Moved stop to breakeven, holding {qty - half_qty} shares")
                    
                    # ⚠️  BIG LOSS - EMERGENCY EXIT (20% stop override)
                    elif pnl_pct <= -20:
                        log.error(f"🚨 EMERGENCY EXIT: {ticker} down {pnl_pct:.1f}%")
                        self._close_position(ticker, qty, "Emergency 20% stop")
                        self._analyze_loss(ticker, entry_price, current_price, stop_price, strategy, pnl_pct)
                
                log.info(f"📊 {ticker}: ${current_price:.2f} ({pnl_pct:+.1f}%)")
                
        except Exception as e:
            log.error(f"Position management error: {e}")
    
    def _analyze_loss(self, ticker: str, entry_price: float, exit_price: float, 
                     stop_price: float, strategy: str, pnl_pct: float):
        """
        🧠 ANALYZE A LOSS AND LEARN FROM IT
        
        The Wolf Brain's learning system:
        1. Record the loss details
        2. Ask Fenrir to analyze what went wrong
        3. Store lessons learned
        4. Adjust strategy confidence if needed
        """
        log.info(f"🧠 ANALYZING LOSS: {ticker} ({strategy})")
        
        # Get additional context
        try:
            stock = yf.Ticker(ticker)
            news = stock.news[:3] if hasattr(stock, 'news') else []
            news_summary = "\n".join([f"- {n.get('title', 'No title')}" for n in news]) if news else "No recent news"
        except:
            news_summary = "Could not fetch news"
        
        # Ask Fenrir to analyze
        if self.ollama_connected:
            prompt = f"""
🐺 LOSS ANALYSIS - LEARN FROM THIS MISTAKE

TRADE DETAILS:
• Ticker: {ticker}
• Strategy: {strategy}
• Entry: ${entry_price:.2f}
• Exit: ${exit_price:.2f}
• Stop: ${stop_price:.2f}
• P&L: {pnl_pct:.1f}%

RECENT NEWS:
{news_summary}

ANALYZE:
1. What went wrong? (Be specific - was it timing, strategy flawed, news event, etc.)
2. Could this have been avoided? (Were there warning signs?)
3. What should we learn? (How do we avoid this in the future?)
4. Should we adjust the {strategy} strategy? (Tighter stops, different entry rules, etc.)

FORMAT YOUR RESPONSE:
WHAT WENT WRONG: [1-2 sentences]
COULD IT BE AVOIDED: [Yes/No and why]
LESSON LEARNED: [Key takeaway]
STRATEGY ADJUSTMENT: [Specific change or "No change needed"]
"""
            
            try:
                analysis = self.think(prompt)
                
                # Store the lesson
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                
                c.execute('''CREATE TABLE IF NOT EXISTS lessons_learned (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    ticker TEXT,
                    strategy TEXT,
                    entry_price REAL,
                    exit_price REAL,
                    pnl_pct REAL,
                    analysis TEXT,
                    lesson TEXT
                )''')
                
                c.execute(
                    """INSERT INTO lessons_learned 
                    (timestamp, ticker, strategy, entry_price, exit_price, pnl_pct, analysis, lesson)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (datetime.now().isoformat(), ticker, strategy, entry_price, exit_price, 
                     pnl_pct, analysis, analysis[:500])
                )
                
                conn.commit()
                conn.close()
                
                log.info(f"📚 Lesson learned and stored:")
                log.info(f"   {analysis[:200]}...")
                
            except Exception as e:
                log.error(f"Error in Fenrir analysis: {e}")
        
        # Update trade record
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "UPDATE trades SET status = ?, exit_price = ?, pnl = ? WHERE ticker = ? AND status = 'open'",
            ('closed_loss', exit_price, pnl_pct, ticker)
        )
        conn.commit()
        conn.close()
    
    def _close_position(self, ticker: str, quantity: int, reason: str):
        """Close a position"""
        if self.dry_run:
            log.info(f"🧪 DRY RUN: Would close {quantity} {ticker} - {reason}")
            return
        
        try:
            order = MarketOrderRequest(
                symbol=ticker,
                qty=quantity,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )
            
            result = self.trading_client.submit_order(order)
            log.info(f"💰 CLOSED: {quantity} {ticker} - {reason}")
            
            # Update tracking
            if ticker in self.positions:
                self.positions[ticker]['quantity'] -= quantity
                if self.positions[ticker]['quantity'] <= 0:
                    del self.positions[ticker]
                    
        except Exception as e:
            log.error(f"Close position error: {e}")
    
    def _store_trade(self, ticker: str, side: str, quantity: int, 
                    entry_price: float, stop_price: float, target_price: float,
                    strategy: str, reasoning: str):
        """
        Store trade in MAIN LEARNING ENGINE (wolfpack.db)
        
        🧠 This feeds the learning system with every trade for continuous improvement.
        Schema matches the main learning engine for consistency.
        """
        # Store in main learning engine
        try:
            conn = sqlite3.connect(self.learning_db)
            c = conn.cursor()
            
            # Main learning engine schema
            metadata = {
                'convergence': 0,  # Would need to extract from reasoning/strategy
                'signals': [strategy],
                'volume_ratio': 0,  # Would need to extract
                'entry_price': entry_price,
                'stop_price': stop_price,
                'target_price': target_price
            }
            
            c.execute('''INSERT INTO trades 
                (timestamp, ticker, action, shares, price, account, thesis, fenrir_said, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (datetime.now().isoformat(), ticker, side, quantity, entry_price,
                 'autonomous_brain', strategy, reasoning, json.dumps(metadata), datetime.now().isoformat()))
            conn.commit()
            conn.close()
            log.info(f"✅ Trade logged to learning engine: {ticker} {side}")
        except Exception as e:
            log.error(f"❌ Failed to log to learning engine: {e}")
        
        # Also store in autonomous memory for backwards compatibility
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO trades 
            (timestamp, ticker, side, quantity, entry_price, stop_price, target_price, strategy, reasoning, status, exit_price, pnl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (datetime.now().isoformat(), ticker, side, quantity, entry_price, 
             stop_price, target_price, strategy, reasoning, 'open', 0, 0))
        conn.commit()
        conn.close()
    
    def _log_decision(self, decision_type: str, ticker: str, action: str, 
                     reasoning: str, confidence: float):
        """Log a decision"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO decisions 
            (timestamp, decision_type, ticker, action, reasoning, confidence, outcome)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (datetime.now().isoformat(), decision_type, ticker, action, reasoning, confidence, 'pending'))
        conn.commit()
        conn.close()
    
    def _parse_fenrir_analysis(self, ticker: str, analysis: str, data: Dict, strategy: str) -> Dict:
        """
        Parse Fenrir's analysis to extract trading parameters
        
        Returns dict with:
        - confidence: 0-1 score
        - entry_price: current/target entry
        - stop_price: stop loss
        - target_price: profit target
        - position_size_pct: % of portfolio
        """
        # Get current price
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1d')
            if hist.empty:
                current_price = data.get('current_price', 10.0)
            else:
                current_price = float(hist['Close'].iloc[-1])
        except:
            current_price = data.get('current_price', 10.0)
        
        # Extract confidence from analysis (look for keywords)
        confidence = 0.5  # Default
        analysis_lower = analysis.lower()
        
        if 'high confidence' in analysis_lower or 'strong buy' in analysis_lower:
            confidence = 0.85
        elif 'conviction: 9' in analysis_lower or 'conviction: 10' in analysis_lower:
            confidence = 0.90
        elif 'conviction: 8' in analysis_lower:
            confidence = 0.80
        elif 'conviction: 7' in analysis_lower:
            confidence = 0.75
        elif 'moderate' in analysis_lower:
            confidence = 0.65
        elif 'low confidence' in analysis_lower or 'risky' in analysis_lower:
            confidence = 0.50
        
        # Strategy-specific logic
        if strategy == 'PDUFA_RUNUP':
            # Wolf Pack rule: Buy 7-14 days before, target 15-30%
            days_until = data.get('days_until', 10)
            
            if 7 <= days_until <= 14:
                confidence += 0.10  # Boost for ideal window
            elif days_until < 7:
                confidence -= 0.15  # Reduce - too close
            
            entry_price = current_price
            stop_price = current_price * 0.88  # 12% stop (biotech can be volatile)
            target_price = current_price * 1.25  # 25% target
            position_size_pct = 0.03  # 3% - biotech is binary
            
        elif strategy == 'INSIDER_BUYING':
            # Follow the smart money
            conviction = data.get('conviction', 5)
            
            if conviction >= 9:
                confidence = 0.85
                position_size_pct = 0.05  # 5% - high conviction
            elif conviction >= 7:
                confidence = 0.75
                position_size_pct = 0.04  # 4%
            else:
                confidence = 0.60
                position_size_pct = 0.03  # 3%
            
            entry_price = current_price
            stop_price = current_price * 0.90  # 10% stop
            target_price = current_price * 1.30  # 30% target
            
        elif strategy == 'COMPRESSION_BREAKOUT':
            # Wait for breakout, tight stop
            entry_price = current_price * 1.02  # Buy on 2% breakout
            stop_price = current_price * 0.95  # 5% stop
            target_price = current_price * 1.25  # 25% target
            position_size_pct = 0.05  # 5% - clear setup
            
        else:
            # Default conservative
            entry_price = current_price
            stop_price = current_price * 0.92  # 8% stop
            target_price = current_price * 1.20  # 20% target
            position_size_pct = 0.02  # 2% - test trade
        
        return {
            'confidence': min(confidence, 0.95),  # Cap at 95%
            'entry_price': entry_price,
            'stop_price': stop_price,
            'target_price': target_price,
            'position_size_pct': position_size_pct
        }
    
    def _should_auto_execute(self, ticker: str, strategy: str, confidence: float, position_size_pct: float) -> bool:
        """
        Decide if we should AUTO-EXECUTE this trade
        
        Checks:
        1. Confidence threshold
        2. Position limits
        3. Daily trade limits
        4. Sector concentration
        """
        # Confidence threshold by strategy
        thresholds = {
            'PDUFA_RUNUP': 0.70,  # High threshold - biotech is risky
            'INSIDER_BUYING': 0.75,  # Smart money gets trust
            'COMPRESSION_BREAKOUT': 0.75,  # Clear technical setup
            'GAP_AND_GO': 0.80,  # Need strong confirmation
            'WOUNDED_PREY': 0.70,  # Turnaround plays
            'HEAD_HUNTER': 0.75,  # Squeeze plays
        }
        
        min_confidence = thresholds.get(strategy, 0.80)  # Default: 80%
        
        if confidence < min_confidence:
            log.info(f"   ⏸️  Confidence {confidence:.0%} < {min_confidence:.0%} threshold")
            return False
        
        # Check daily trade limit
        if self.daily_trades >= SAFETY['max_daily_trades']:
            log.warning(f"   ⏸️  Daily trade limit reached: {self.daily_trades}/{SAFETY['max_daily_trades']}")
            return False
        
        # Check total position count
        if len(self.positions) >= 5:
            log.warning(f"   ⏸️  Max positions: {len(self.positions)}/5")
            return False
        
        # Check biotech concentration (max 3 biotech positions)
        biotech_strategies = ['PDUFA_RUNUP', 'INSIDER_BUYING', 'WOUNDED_PREY']
        if strategy in biotech_strategies:
            biotech_count = sum(1 for pos_info in self.positions.values() 
                              if pos_info.get('strategy') in biotech_strategies)
            if biotech_count >= 3:
                log.warning(f"   ⏸️  Max biotech positions: {biotech_count}/3")
                return False
        
        # All checks passed
        log.info(f"   ✅ AUTO-EXECUTE approved:")
        log.info(f"      • Confidence: {confidence:.0%} > {min_confidence:.0%}")
        log.info(f"      • Daily trades: {self.daily_trades}/{SAFETY['max_daily_trades']}")
        log.info(f"      • Open positions: {len(self.positions)}/5")
        return True
    
    # ============ MAIN LOOP ============
    
    def get_market_status(self) -> str:
        """Check market status with PRECISE timing for runner hunting"""
        now = datetime.now()
        
        # Check if weekend
        if now.weekday() >= 5:
            return 'CLOSED_WEEKEND'
        
        market_open = now.replace(hour=9, minute=30, second=0)
        market_close = now.replace(hour=16, minute=0, second=0)
        premarket_start = now.replace(hour=4, minute=0, second=0)
        
        # KEY TIMES for runners:
        # 4:00 AM - Premarket opens (first scan)
        # 6:00 AM - Volume picks up (second scan)  
        # 8:30 AM - Economic data releases
        # 9:15 AM - Final pre-open scan
        # 9:30 AM - MARKET OPEN (action time)
        
        if now < premarket_start:
            return 'OVERNIGHT'
        elif now.hour == 4 and now.minute < 30:
            return 'PREMARKET_EARLY'  # 4:00-4:30 AM first scan
        elif now.hour < 6:
            return 'PREMARKET'  # 4:30-6:00 AM
        elif now.hour < 9:
            return 'PREMARKET_PRIME'  # 6:00-9:00 AM volume building
        elif now.hour == 9 and now.minute < 30:
            return 'PREMARKET_FINAL'  # 9:00-9:30 AM final positioning
        elif now < market_close:
            return 'OPEN'
        else:
            return 'AFTER_HOURS'
    
    def scan_biotech_catalysts(self) -> Dict:
        """
        🧬 BIOTECH CATALYST SCAN
        
        Scans for biotech opportunities using the catalyst scanner module.
        Returns opportunities that Fenrir will analyze for paper trades.
        """
        if not self.biotech_scanner:
            log.warning("Biotech scanner not available")
            return {}
        
        log.info("🧬 SCANNING BIOTECH CATALYSTS...")
        
        # Get all opportunities
        opportunities = self.biotech_scanner.scan_for_catalyst_setups()
        
        # Log what we found
        pdufa_plays = opportunities.get('pdufa_runup_plays', [])
        insider_plays = opportunities.get('insider_buying_plays', [])
        imminent = opportunities.get('imminent_catalysts', [])
        
        if pdufa_plays:
            log.info(f"   🔥 {len(pdufa_plays)} PDUFA runup plays (7-14 day window)")
            for play in pdufa_plays:
                log.info(f"      • {play['ticker']}: {play['days_until']} days to {play['type']}")
        
        if insider_plays:
            log.info(f"   👔 {len(insider_plays)} insider buying signals")
            for play in insider_plays:
                log.info(f"      • {play['ticker']}: Conviction {play['conviction']}/10")
        
        if imminent:
            log.info(f"   ⚠️  {len(imminent)} imminent catalysts (risky)")
        
        # Have Fenrir analyze and generate paper trade ideas
        if pdufa_plays and self.ollama_connected:
            for play in pdufa_plays[:2]:  # Top 2 only
                # Get price data
                ticker = play['ticker']
                price_data = self._get_price_data(ticker)
                
                if price_data:
                    # Generate analysis prompt
                    prompt = biotech_prompts.get_pdufa_analysis_prompt(
                        ticker=ticker,
                        catalyst_data=play,
                        price_data=price_data
                    )
                    
                    # Get Fenrir's analysis
                    analysis = self.think(prompt)
                    
                    log.info(f"🧠 FENRIR ANALYSIS - {ticker}:")
                    log.info(f"   {analysis[:500]}")
                    
                    # Store as a paper trade idea
                    self._store_paper_trade_idea(ticker, 'PDUFA_RUNUP', analysis, play)
        
        return opportunities
    
    def _store_paper_trade_idea(self, ticker: str, strategy: str, analysis: str, data: Dict):
        """
        Store and EXECUTE a paper trade idea from Fenrir
        
        🚨 AUTO-EXECUTION MODE 🚨
        If confidence is high enough and risk management allows, 
        the Wolf Brain will AUTOMATICALLY execute paper trades.
        
        This is the CORE of autonomous trading.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create table if doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS paper_trade_ideas (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            ticker TEXT,
            strategy TEXT,
            analysis TEXT,
            catalyst_data TEXT,
            confidence REAL,
            entry_price REAL,
            stop_price REAL,
            target_price REAL,
            position_size_pct REAL,
            status TEXT,
            executed_at TEXT,
            trade_id INTEGER
        )''')
        
        # Parse Fenrir's analysis to extract trading parameters
        trade_params = self._parse_fenrir_analysis(ticker, analysis, data, strategy)
        
        if not trade_params:
            log.warning(f"⚠️  Could not parse trade parameters for {ticker}")
            c.execute(
                "INSERT INTO paper_trade_ideas (timestamp, ticker, strategy, analysis, catalyst_data, confidence, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (datetime.now().isoformat(), ticker, strategy, analysis, json.dumps(data, default=str), 0.0, 'REJECTED')
            )
            conn.commit()
            conn.close()
            return
        
        confidence = trade_params['confidence']
        entry_price = trade_params['entry_price']
        stop_price = trade_params['stop_price']
        target_price = trade_params['target_price']
        position_size_pct = trade_params['position_size_pct']
        
        # Store the idea first
        c.execute(
            """INSERT INTO paper_trade_ideas 
            (timestamp, ticker, strategy, analysis, catalyst_data, confidence, 
             entry_price, stop_price, target_price, position_size_pct, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (datetime.now().isoformat(), ticker, strategy, analysis, 
             json.dumps(data, default=str), confidence, entry_price, stop_price, 
             target_price, position_size_pct, 'PENDING')
        )
        idea_id = c.lastrowid
        conn.commit()
        
        log.info(f"💡 Paper trade idea stored: {ticker} ({strategy}) - Confidence: {confidence:.0%}")
        
        # 🚨 AUTO-EXECUTION DECISION 🚨
        should_execute = self._should_auto_execute(ticker, strategy, confidence, position_size_pct)
        
        if should_execute:
            log.info(f"🎯 AUTO-EXECUTING paper trade: {ticker}")
            log.info(f"   Strategy: {strategy}")
            log.info(f"   Confidence: {confidence:.0%}")
            log.info(f"   Entry: ${entry_price:.2f} | Stop: ${stop_price:.2f} | Target: ${target_price:.2f}")
            
            # Calculate position size
            if not self.alpaca_connected:
                log.warning("⚠️  Alpaca not connected - cannot execute")
                c.execute("UPDATE paper_trade_ideas SET status = ? WHERE id = ?", ('REJECTED_NO_CONNECTION', idea_id))
                conn.commit()
                conn.close()
                return
            
            try:
                account = self.trading_client.get_account()
                buying_power = float(account.buying_power)
                position_value = buying_power * position_size_pct
                quantity = int(position_value / entry_price)
                
                if quantity < 1:
                    log.warning(f"⚠️  Position too small: {quantity} shares")
                    c.execute("UPDATE paper_trade_ideas SET status = ? WHERE id = ?", ('REJECTED_TOO_SMALL', idea_id))
                    conn.commit()
                    conn.close()
                    return
                
                # EXECUTE THE TRADE
                result = self.execute_trade(
                    ticker=ticker,
                    side='BUY',
                    quantity=quantity,
                    entry_price=entry_price,
                    stop_price=stop_price,
                    target_price=target_price,
                    strategy=strategy,
                    reasoning=f"AUTO-EXECUTE: {strategy} setup | Confidence: {confidence:.0%}\n{analysis[:200]}"
                )
                
                if result['success']:
                    log.info(f"✅ AUTO-EXECUTED: {ticker} - {quantity} shares @ ${entry_price:.2f}")
                    c.execute(
                        "UPDATE paper_trade_ideas SET status = ?, executed_at = ? WHERE id = ?",
                        ('EXECUTED', datetime.now().isoformat(), idea_id)
                    )
                else:
                    log.error(f"❌ Execution failed: {result.get('error', 'Unknown')}")
                    c.execute(
                        "UPDATE paper_trade_ideas SET status = ? WHERE id = ?",
                        (f"REJECTED_{result.get('error', 'FAILED')}", idea_id)
                    )
                    
            except Exception as e:
                log.error(f"❌ Auto-execute error: {e}")
                c.execute("UPDATE paper_trade_ideas SET status = ? WHERE id = ?", (f'ERROR_{str(e)[:50]}', idea_id))
        else:
            log.info(f"⏸️  Stored for review (confidence {confidence:.0%} not high enough or limits hit)")
            
        conn.commit()
        conn.close()
    
    def run_cycle(self):
        """
        Run one full cycle based on market status
        
        THE WOLF'S DAILY RHYTHM:
        4:00 AM - Wake up, first scan for gaps
        6:00 AM - Volume confirmation scan
        9:15 AM - Final positioning decisions
        9:30 AM - EXECUTE on runners
        During day - Manage positions, find swing setups
        4:00 PM - Close day trades, review
        Overnight - Light research
        """
        status = self.get_market_status()
        log.info(f"⏰ Market status: {status}")
        
        # Reset daily counters if new day
        if datetime.now().date() != self.last_reset:
            self.daily_trades = 0
            self.daily_pnl = 0
            self.last_reset = datetime.now().date()
            log.info("📅 New day - counters reset")
        
        if status == 'PREMARKET_EARLY':
            # 4 AM - FIRST SCAN + INTEL REPORT + BIOTECH CATALYSTS
            log.info("🌅 4 AM SCAN - GENERATING INTEL REPORT FOR TYR...")
            log.info("   Report will be ready at data/wolf_brain/LATEST_INTEL_REPORT.txt")
            
            # Generate the full intel report (includes scanning)
            report = self.generate_intel_report()
            
            # BIOTECH CATALYST SCAN
            biotech_opps = self.scan_biotech_catalysts()
            
            # Also do the standard runner scan
            runners = self.scan_premarket_runners()
            
            if runners:
                # 🔥 TRACK MOMENTUM - Monitor for sustained strength
                self._track_momentum(runners, '4:00 AM')
                
                self.premarket_candidates = runners  # Store for later
                log.info(f"🎯 Found {len(runners)} potential runners to monitor")
                
                # Brain analysis of top candidates
                for r in runners[:3]:
                    analysis = self.think(f"""
4 AM RUNNER CHECK: {r['ticker']}

Gap: +{r.get('gap_data', {}).get('gap_pct', 0):.1f}%
Float: {r.get('gap_data', {}).get('float_shares', 0)/1_000_000:.1f}M
Volume: {r.get('gap_data', {}).get('relative_volume', 0):.1f}x normal
Classification: {r.get('classification', {}).get('verdict', 'UNKNOWN')}

News: {r.get('news', [{}])[0].get('headline', 'No news')[:100] if r.get('news') else 'No news'}

Is this worth monitoring for market open? Brief assessment.
""")
                    log.info(f"🧠 {r['ticker']}: {analysis[:200]}")
        
        elif status == 'PREMARKET':
            # Light monitoring, no major decisions
            log.info("☕ Premarket - monitoring...")
        
        elif status == 'PREMARKET_PRIME':
            # 6-9 AM - VOLUME CONFIRMATION
            log.info("📊 PRIME TIME - Checking volume on candidates...")
            
            if hasattr(self, 'premarket_candidates') and self.premarket_candidates:
                confirmed_runners = []
                
                for candidate in self.premarket_candidates[:5]:
                    # Re-check gap and volume
                    new_gap_data = self._check_premarket_gap(candidate['ticker'])
                    
                    if new_gap_data:
                        vol_ratio = new_gap_data.get('relative_volume', 0)
                        gap = new_gap_data.get('gap_pct', 0)
                        
                        log.info(f"   {candidate['ticker']}: Gap {gap:+.1f}% | Volume {vol_ratio:.1f}x")
                        
                        # RUNNER CONFIRMATION: Gap held + Volume building
                        if gap >= 5 and vol_ratio >= 2:
                            confirmed_runners.append(candidate)
                            log.info(f"   ✅ {candidate['ticker']} CONFIRMED - Gap holding with volume")
                        else:
                            log.info(f"   ⚠️ {candidate['ticker']} - Gap fading or no volume")
                
                self.premarket_candidates = confirmed_runners
                log.info(f"🎯 {len(confirmed_runners)} runners confirmed for open")
        
        elif status == 'PREMARKET_FINAL':
            # 9:00-9:30 AM - FINAL DECISIONS
            log.info("🎯 FINAL POSITIONING - 15 minutes to open!")
            
            if hasattr(self, 'premarket_candidates') and self.premarket_candidates:
                # Brain makes final decision
                for candidate in self.premarket_candidates[:2]:
                    decision = self.think(f"""
FINAL DECISION - Market opens in 15 minutes!

{candidate['ticker']}:
- Gap: +{candidate.get('gap_data', {}).get('gap_pct', 0):.1f}%
- Volume: {candidate.get('gap_data', {}).get('relative_volume', 0):.1f}x normal
- Float: {candidate.get('gap_data', {}).get('float_shares', 0)/1_000_000:.1f}M shares
- Classification: {candidate.get('classification', {})}

QUESTION: Should we enter at market open?

If YES - what entry, stop, target?
If NO - why not?
""")
                    log.info(f"🧠 FINAL DECISION {candidate['ticker']}: {decision[:300]}")
        
        elif status == 'OPEN':
            # MARKET OPEN - Execute and manage
            self.manage_positions()
            
            # Scan for new opportunities
            opportunities = self.scan_market_hours()
            
            # Consider executing trades (top opportunity only)
            if opportunities and self.daily_trades < SAFETY['max_daily_trades']:
                top = opportunities[0]
                
                # Get account for sizing
                if self.alpaca_connected:
                    acc = self.trading_client.get_account()
                    portfolio_value = float(acc.portfolio_value)
                    
                    # Calculate position size (5% base)
                    position_value = portfolio_value * 0.05
                    price = top['price_data']['price']
                    quantity = int(position_value / price)
                    
                    if quantity > 0:
                        # Calculate stop and target
                        stop_price = price * 0.92  # 8% stop
                        target_price = price * 1.15  # 15% target
                        
                        # Brain decides
                        decision = self.think(f"""
Should we BUY {top['ticker']} now?

Analysis: {top['brain_analysis'][:500]}
Price: ${price:.2f}
Stop: ${stop_price:.2f} (-8%)
Target: ${target_price:.2f} (+15%)
Position: {quantity} shares (${position_value:.2f})

YES or NO with brief reason.
""")
                        
                        if 'YES' in decision.upper():
                            self.execute_trade(
                                ticker=top['ticker'],
                                side='BUY',
                                quantity=quantity,
                                entry_price=price,
                                stop_price=stop_price,
                                target_price=target_price,
                                strategy='autonomous',
                                reasoning=top['brain_analysis'][:200]
                            )
        
        elif status == 'AFTER_HOURS':
            # After hours - analyze the day, learn
            self.manage_positions()
            self._end_of_day_review()
        
        else:
            # Closed - light research
            log.info("💤 Market closed - light research mode")
    
    def _end_of_day_review(self):
        """End of day review and learning"""
        log.info("📝 END OF DAY REVIEW")
        
        # Get today's decisions
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute("SELECT * FROM decisions WHERE timestamp LIKE ?", (f"{today}%",))
        decisions = c.fetchall()
        c.execute("SELECT * FROM trades WHERE timestamp LIKE ?", (f"{today}%",))
        trades = c.fetchall()
        conn.close()
        
        log.info(f"   Decisions today: {len(decisions)}")
        log.info(f"   Trades today: {len(trades)}")
        
        # Brain reflection
        if decisions:
            reflection = self.think(f"""
End of day reflection. Today we made {len(decisions)} decisions and {len(trades)} trades.

What patterns did we see? What worked? What didn't?
What should we adjust for tomorrow?

Keep it brief - key learnings only.
""")
            log.info(f"🧠 Reflection: {reflection[:300]}")
    
    def run_scheduled_scans(self):
        """
        RUN SCANS AT SCHEDULED TIMES FOR TYR
        
        Scan times: 4:00, 5:00, 5:30, 6:00, 6:30, 7:00, 7:30 AM
        Each scan saves results so Tyr can review at 8 AM
        """
        SCAN_TIMES = [
            (4, 0),   # 4:00 AM - First look
            (5, 0),   # 5:00 AM - Early movers
            (5, 30),  # 5:30 AM - Building momentum
            (6, 0),   # 6:00 AM - Volume confirmation
            (6, 30),  # 6:30 AM - Prime time starts
            (7, 0),   # 7:00 AM - Peak action
            (7, 30),  # 7:30 AM - Final scan before 8
        ]
        
        now = datetime.now()
        current_time = (now.hour, now.minute)
        
        for scan_hour, scan_min in SCAN_TIMES:
            # Check if it's time for this scan (within 2 min window)
            if now.hour == scan_hour and scan_min <= now.minute < scan_min + 2:
                log.info(f"⏰ SCHEDULED SCAN: {scan_hour}:{scan_min:02d} AM")
                
                # Run the scan
                gainers = self.scan_real_premarket_gainers()
                
                # 🔥 MOMENTUM TRACKING - Track sustained runners across scans
                scan_label = f"{scan_hour}:{scan_min:02d} AM"
                self._track_momentum(gainers, scan_label)
                
                # Show sustained runners (appeared in 2+ scans)
                sustained = self.get_sustained_runners()
                if sustained:
                    log.info(f"🔥 SUSTAINED RUNNERS ({len(sustained)} tickers with momentum):")
                    for s in sustained:
                        log.info(f"   {s['ticker']}: Seen in {s['scans_appeared']} scans | {s['gap_trend']} gap | {s['volume_trend']} volume")
                
                # Save results with timestamp
                scan_name = f"scan_{scan_hour:02d}{scan_min:02d}"
                self._save_scan_results(scan_name, gainers)
                
                # Also update the rolling report (include sustained runners)
                self._update_rolling_report(scan_hour, scan_min, gainers, sustained)
                
                return True
        
        return False
    
    def _save_scan_results(self, scan_name: str, gainers: List[Dict]):
        """Save scan results to file"""
        scan_file = os.path.join(self.data_dir, f'{scan_name}_{datetime.now().strftime("%Y%m%d")}.json')
        
        with open(scan_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'scan_name': scan_name,
                'gainers': gainers
            }, f, indent=2, default=str)
        
        log.info(f"💾 Scan saved: {scan_file}")
    
    def _update_rolling_report(self, hour: int, minute: int, gainers: List[Dict], sustained_runners: List[Dict] = None):
        """Update the rolling premarket report - builds up through the morning"""
        report_file = os.path.join(self.data_dir, f'PREMARKET_SCANS_{datetime.now().strftime("%Y%m%d")}.txt')
        
        # Build this scan's section
        section = f"""
{'='*70}
⏰ {hour}:{minute:02d} AM SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}
"""
        
        if gainers:
            section += f"Found {len(gainers)} stocks gapping 3%+:\n\n"
            for i, g in enumerate(gainers[:15], 1):
                emoji = '🚀' if g['gap_pct'] >= 10 else ('🔥' if g['gap_pct'] >= 5 else '📈')
                float_str = f"{g['float']/1e6:.0f}M" if g.get('float') else "N/A"
                
                # Mark sustained runners with special emoji
                is_sustained = any(s['ticker'] == g['ticker'] for s in (sustained_runners or []))
                sustained_mark = ' ⚡ SUSTAINED' if is_sustained else ''
                
                section += f"  {i:2}. {emoji} {g['ticker']:6} | Gap: {g['gap_pct']:+6.1f}% | Vol: {g['volume_ratio']:4.1f}x | Float: {float_str}{sustained_mark}\n"
            
            # Track which tickers are showing up repeatedly (strongest movers)
            section += f"\n📊 Top 5 by gap: {', '.join([g['ticker'] for g in sorted(gainers, key=lambda x: x['gap_pct'], reverse=True)[:5]])}\n"
            
            # Add sustained runners section
            if sustained_runners:
                section += f"\n🔥 SUSTAINED RUNNERS (appearing in multiple scans with strength):\n"
                for s in sustained_runners:
                    latest = s['latest_data']
                    section += f"   • {s['ticker']}: {s['scans_appeared']} scans | Gap: {latest['gap_pct']:.1f}% | Vol: {latest['volume_ratio']:.1f}x | {s['gap_trend']}\n"
                section += "\n⚡ These are NOT flash-in-the-pan - sustained momentum = REAL STRENGTH\n"
        else:
            section += "No significant gaps detected yet.\n"
        
        section += "\n"
        
        # Append to report
        with open(report_file, 'a', encoding='utf-8') as f:
            f.write(section)
        
        log.info(f"📝 Updated rolling report: {report_file}")
    
    def _active_hunt_cycle(self):
        """
        🐺 ACTIVE HUNTING MODE - 4:05 AM onwards
        
        Scans every 10 minutes with DETAILED LOGGING for review at 6 AM.
        This is where Fenrir and Tyr can see EXACTLY what's happening.
        """
        now = datetime.now()
        hunt_time = now.strftime('%H:%M:%S')
        
        log.info("=" * 70)
        log.info(f"🐺 ACTIVE HUNT CYCLE @ {hunt_time}")
        log.info("=" * 70)
        
        # Create detailed hunt log file
        hunt_log_file = os.path.join(self.data_dir, f'HUNT_LOG_{datetime.now().strftime("%Y%m%d")}.txt')
        
        hunt_entry = f"""
{'='*70}
🐺 HUNT CYCLE @ {hunt_time} EST
{'='*70}

"""
        
        # Scan for gainers
        try:
            gainers = self.scan_real_premarket_gainers()
            
            if gainers:
                hunt_entry += f"📊 FOUND {len(gainers)} STOCKS GAPPING 3%+:\n\n"
                
                for i, g in enumerate(gainers[:20], 1):
                    emoji = '🚀' if g['gap_pct'] >= 10 else ('🔥' if g['gap_pct'] >= 5 else '📈')
                    float_str = f"{g['float']/1e6:.0f}M" if g.get('float') else "N/A"
                    
                    # Check if it's a sustained runner
                    is_sustained = any(s['ticker'] == g['ticker'] for s in self.sustained_runners)
                    sustained_mark = ' ⚡ SUSTAINED' if is_sustained else ''
                    
                    hunt_entry += f"  {i:2}. {emoji} {g['ticker']:6} | Gap: {g['gap_pct']:+6.1f}% | Vol: {g['volume_ratio']:5.1f}x | Float: {float_str:>6} | ${g['price']:.2f}{sustained_mark}\n"
                
                # Add sustained runners summary
                if self.sustained_runners:
                    hunt_entry += f"\n🔥 SUSTAINED RUNNERS ({len(self.sustained_runners)} tickers building momentum):\n"
                    for s in self.sustained_runners:
                        latest = s['latest_data']
                        hunt_entry += f"   • {s['ticker']:6} - Seen in {s['scans_appeared']} scans | Gap: {latest['gap_pct']:+6.1f}% | Vol: {latest['volume_ratio']:4.1f}x | {s['gap_trend']}\n"
                    hunt_entry += "\n⚡ These are the REAL MOVERS - not flash-in-the-pan\n"
                
                # Add top picks for Fenrir to analyze
                hunt_entry += f"\n🎯 TOP 3 FOR FENRIR ANALYSIS:\n"
                for i, g in enumerate(gainers[:3], 1):
                    hunt_entry += f"   {i}. {g['ticker']} @ ${g['price']:.2f} - Gap +{g['gap_pct']:.1f}% with {g['volume_ratio']:.1f}x volume\n"
            else:
                hunt_entry += "No significant gaps detected at this time.\n"
            
            hunt_entry += f"\n{'='*70}\n\n"
            
            # Append to hunt log
            with open(hunt_log_file, 'a', encoding='utf-8') as f:
                f.write(hunt_entry)
            
            log.info(f"📝 Hunt logged to: {hunt_log_file}")
            log.info(f"   Found {len(gainers)} movers | {len(self.sustained_runners)} sustained")
            
        except Exception as e:
            log.error(f"Hunt cycle error: {e}")
            hunt_entry += f"⚠️ Error during hunt: {e}\n\n"
            with open(hunt_log_file, 'a', encoding='utf-8') as f:
                f.write(hunt_entry)
    
    def run_forever(self):
        """
        Run the brain 24/7
        
        SCHEDULED SCANS FOR TYR:
        4:00 AM, 5:00 AM, 5:30 AM, 6:00 AM, 6:30 AM, 7:00 AM, 7:30 AM
        Results saved to PREMARKET_SCANS_YYYYMMDD.txt
        """
        self.running = True
        log.info("🐺 STARTING 24/7 AUTONOMOUS MODE")
        log.info("   Press Ctrl+C to stop")
        log.info("")
        log.info("📅 SCHEDULED SCANS:")
        log.info("   4:00 AM - First look at gaps")
        log.info("   5:00 AM - Early movers")
        log.info("   5:30 AM - Building momentum")
        log.info("   6:00 AM - Volume confirmation")
        log.info("   6:30 AM - Prime time")
        log.info("   7:00 AM - Peak action")
        log.info("   7:30 AM - Final scan")
        log.info("")
        log.info("   Results saved to: data/wolf_brain/PREMARKET_SCANS_*.txt")
        log.info("")
        
        # Determine check interval based on market status
        while self.running:
            try:
                status = self.get_market_status()
                
                # Check for scheduled scans (4 AM - 7:30 AM)
                now = datetime.now()
                if 4 <= now.hour < 8:
                    self.run_scheduled_scans()
                
                # Run a cycle
                self.run_cycle()
                
                # Determine sleep time based on market status
                # THE WOLF'S SLEEP SCHEDULE:
                # - 4:05 AM - 8 AM: ACTIVE HUNTING MODE - Every 10 min with detailed logging
                # - Premarket: 30 min checks
                # - Prime time (6-9 AM): Every 10 min - critical period
                # - Final 30 min: Every 5 min - decision time
                # - Market open: Every 2 min - action time
                # - After hours: Every 15 min
                # - Overnight/weekend: Every hour
                
                if now.hour == 4 and now.minute >= 5:
                    # 4:05 AM+ → ACTIVE HUNTING MODE - Scan every 10 min, detailed logging
                    sleep_time = 600  # 10 min - active monitoring with logging
                    self._active_hunt_cycle()
                elif 5 <= now.hour < 8:
                    # 5-8 AM → Continue hunting every 10 min
                    sleep_time = 600  # 10 min - keep hunting
                    self._active_hunt_cycle()
                elif status == 'PREMARKET_EARLY':
                    sleep_time = 900  # 15 min - first scans
                elif status == 'PREMARKET':
                    sleep_time = 1800  # 30 min - light monitoring
                elif status == 'PREMARKET_PRIME':
                    sleep_time = 600  # 10 min - volume confirmation
                elif status == 'PREMARKET_FINAL':
                    sleep_time = 300  # 5 min - final decisions
                elif status == 'OPEN':
                    sleep_time = 120  # 2 min during market
                elif status == 'AFTER_HOURS':
                    sleep_time = 900  # 15 min after hours
                else:
                    sleep_time = 3600  # 1 hour overnight/weekend
                
                log.info(f"💤 Sleeping {sleep_time//60} minutes until next cycle...")
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                log.info("🛑 Shutdown requested")
                self.running = False
            except Exception as e:
                log.error(f"Cycle error: {e}")
                time.sleep(60)
        
        log.info("👋 Autonomous brain shutting down")


# ============ MAIN ============

def main():
    parser = argparse.ArgumentParser(description='🐺 Autonomous Wolf Brain')
    parser.add_argument('--dry-run', action='store_true', help='Run without executing trades')
    parser.add_argument('--once', action='store_true', help='Run one cycle then exit')
    parser.add_argument('--scan', action='store_true', help='Run 4AM premarket scan NOW (test mode)')
    parser.add_argument('--report', action='store_true', help='Generate INTEL REPORT now')
    parser.add_argument('--gainers', action='store_true', help='Scan for real premarket gainers')
    parser.add_argument('--analyze', type=str, help='Analyze a specific ticker')
    
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     🐺 A U T O N O M O U S   W O L F   B R A I N 🐺          ║
    ║                                                              ║
    ║     24/7 Thinking • Trading • Learning                       ║
    ║                                                              ║
    ║     EQUIPPED WITH:                                           ║
    ║     • 4AM Premarket Scanner                                  ║
    ║     • Real Premarket Gainer Detection                        ║
    ║     • Intel Report Generator                                 ║
    ║     • FDA Calendar Intelligence                              ║
    ║     • Runner vs Fader Classification                         ║
    ║     • Biotech Formula Detection                              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    brain = AutonomousBrain(dry_run=args.dry_run)
    
    if args.report:
        # Generate full intel report
        print("\n📝 GENERATING INTEL REPORT...\n")
        report = brain.generate_intel_report()
        print(report)
        print(f"\n✅ Report saved to: data/wolf_brain/LATEST_INTEL_REPORT.txt")
        
    elif args.gainers:
        # Scan for real premarket gainers
        print("\n🔥 SCANNING FOR REAL PREMARKET GAINERS...\n")
        gainers = brain.scan_real_premarket_gainers()
        
        print("\n" + "=" * 60)
        print("🔥 TOP PREMARKET GAINERS:")
        print("=" * 60)
        
        for i, g in enumerate(gainers[:15], 1):
            emoji = '🚀' if g['gap_pct'] >= 10 else ('🔥' if g['gap_pct'] >= 5 else '📈')
            float_str = f"{g['float']/1e6:.0f}M" if g['float'] else "N/A"
            print(f"  {i:2}. {emoji} {g['ticker']:6} | Gap: {g['gap_pct']:+6.1f}% | Vol: {g['volume_ratio']:4.1f}x | Float: {float_str}")
    
    elif args.scan:
        # Force run 4AM scan regardless of time
        print("\n🔥 FORCE RUNNING 4AM PREMARKET SCAN...\n")
        runners = brain.scan_premarket_runners()
        
        print("\n" + "=" * 60)
        print("📊 SCAN RESULTS:")
        print("=" * 60)
        
        if runners:
            for i, r in enumerate(runners[:10], 1):
                print(f"\n{i}. {r['ticker']}")
                print(f"   Gap: +{r.get('gap_data', {}).get('gap_pct', 0):.1f}%")
                print(f"   Volume: {r.get('gap_data', {}).get('relative_volume', 0):.1f}x normal")
                print(f"   Float: {r.get('gap_data', {}).get('float_shares', 0)/1_000_000:.1f}M")
                print(f"   Class: {r.get('classification', {}).get('verdict', 'UNKNOWN')}")
                print(f"   Confidence: {r.get('confidence', 0):.0%}")
        else:
            print("   No runners found - market may be closed or gaps not significant")
            
    elif args.analyze:
        # Deep analysis of single ticker
        print(f"\n🔍 DEEP ANALYSIS: {args.analyze.upper()}\n")
        
        research = brain.research_ticker(args.analyze.upper())
        
        print(f"Ticker: {research['ticker']}")
        print(f"Decision: {research['decision']}")
        print(f"Confidence: {research['confidence']:.0%}")
        print(f"\nPrice Data:")
        for k, v in research.get('price_data', {}).items():
            print(f"   {k}: {v}")
        print(f"\nNews:")
        for n in research.get('news', [])[:3]:
            print(f"   • {n.get('headline', '')[:80]}")
        print(f"\nBrain Analysis:")
        print(f"   {research.get('brain_analysis', 'No analysis')[:500]}")
        
        # Runner classification
        gap_data = brain._check_premarket_gap(args.analyze.upper())
        if gap_data:
            classification = brain._classify_runner_vs_fader(args.analyze.upper(), gap_data, research)
            print(f"\nRunner Classification:")
            print(f"   Verdict: {classification['verdict']}")
            print(f"   Confidence: {classification['confidence']}")
            print(f"   Reason: {classification['reason']}")
            
    elif args.once:
        brain.run_cycle()
    else:
        brain.run_forever()


if __name__ == "__main__":
    main()
