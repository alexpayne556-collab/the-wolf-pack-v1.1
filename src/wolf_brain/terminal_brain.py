"""
🐺 WOLF BRAIN TERMINAL - LIGHTWEIGHT THINKING ENGINE
Built: January 20, 2026

No GUI. No bloat. Just pure thinking.

Uses:
- Ollama for reasoning (fenrir:latest)
- Alpaca for paper trading
- Leonard File as GUIDELINES (not rigid rules)
- Simple terminal interface

The brain THINKS for itself. We give it ideas, it experiments and learns.

Usage:
    python terminal_brain.py              # Interactive mode
    python terminal_brain.py --scan       # Scan and show opportunities
    python terminal_brain.py --auto       # Autonomous mode (careful!)
    python terminal_brain.py --status     # Show current status
"""

import os
import sys
import json
import time
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import argparse

# Lightweight data fetching
try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

# Ollama for thinking
import requests

# Alpaca for trading
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, StopOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False


# ============ CONFIGURATION ============

# Load from environment or use defaults
ALPACA_KEY = os.environ.get('APCA_API_KEY_ID', '')
ALPACA_SECRET = os.environ.get('APCA_API_SECRET_KEY', '')
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "fenrir:latest"

# Data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'wolf_brain')
os.makedirs(DATA_DIR, exist_ok=True)

# Logging setup
LOG_FILE = os.path.join(DATA_DIR, 'brain_log.txt')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger('WolfBrain')


# ============ THE WOLF PACK KNOWLEDGE ============
# These are GUIDELINES, not rigid rules. The brain uses them to inform decisions.

WOLF_PACK_WISDOM = """
🐺 WOLF PACK TRADING WISDOM (Guidelines, Not Rules)

== THE CORE PHILOSOPHY ==
- We are hunters, not gamblers
- Patience is our edge - wait for the perfect setup
- Protect capital FIRST, profits second
- Small losses, big wins - asymmetric bets
- The market is always right, ego is always wrong

== STRATEGIES TO CONSIDER ==

1. WOUNDED PREY (Our Best Edge - ~68% historical)
   - Stock 20-40% off highs with healthy chart
   - Look for: CEO buying, analyst upgrades, catalyst ahead
   - Avoid: Spike-and-crash charts (IVF-style)
   - Target: 10-20% bounce to equilibrium
   - Stop: 8-10% below entry
   
2. HEAD HUNTER (High Risk, High Reward)
   - Ultra-low float (<10M shares) with catalyst
   - Price $0.50-$10 for maximum % gain potential
   - High short interest = squeeze fuel
   - Target: 50-500%+ (hold runners, cut losers fast)
   - Stop: 15% (needs room to breathe)

3. INSIDER FOLLOWING (Smart Money)
   - Track Form 4 filings (CEO/CFO buys most important)
   - Cluster buying = multiple insiders = stronger signal
   - Buy amount matters ($100K+ is conviction)
   - They know more than we do - follow smart money

4. CATALYST PLAYS (Binary Events)
   - FDA dates, trial results, earnings
   - Position BEFORE event (not during/after)
   - Size SMALL (binary = can go either way)
   - These can 10x or -50%, no middle ground

== THE 10 COMMANDMENTS (Market Wizards) ==
1. Never risk more than 2% per trade
2. Always use stops (no exceptions)
3. Cut losses, let winners run
4. Never add to a losing position
5. Wait for the setup, don't force trades
6. Trade what you see, not what you think
7. Take profits in tranches (scale out)
8. Respect the trend
9. Paper trade new strategies first
10. Log EVERYTHING - learning requires data

== RGC LESSON (20,000% Move) ==
Supply destruction = forced price discovery
- 86% insider ownership = 14% float
- CEO bought 81% of remaining float
- Result: 150K shares tradeable, ANY demand = moon
- Formula: Low Float + Insider Lock + New Buying + Catalyst

== CHART HEALTH (Critical) ==
HEALTHY (IBRX-style): Stair-step up, controlled pullbacks, higher lows
UNHEALTHY (IVF-style): Spike → crash → dead, bagholders trapped
ONLY trade healthy charts. Unhealthy = trap.

== EXIT RULES ==
- First target: 10% (sell 1/3)
- Second target: 20% (sell 1/3)
- Let final 1/3 run with trailing stop
- Move stop to breakeven after first target
- NEVER let winner become loser

== POSITION SIZING ==
- Base: 5% of portfolio per trade
- High conviction: 7-10% max
- Speculative: 2-3% max
- Kelly Criterion for optimal sizing
- Total portfolio heat: <20% at risk

== WHAT TO AVOID ==
- Chasing (if you missed it, you missed it)
- Revenge trading (loss → emotional trade → bigger loss)
- FOMO (there's always another setup)
- Overtrading (quality over quantity)
- Fighting the trend
- Averaging down on losers
- Trading without a plan
"""


# ============ THE BRAIN ============

class TerminalBrain:
    """
    Lightweight Wolf Brain - thinks, trades, learns
    """
    
    def __init__(self):
        """Initialize the brain"""
        self.ollama_connected = False
        self.alpaca_connected = False
        self.trading_client = None
        self.data_client = None
        
        # Memory database
        self.db_path = os.path.join(DATA_DIR, 'brain_memory.db')
        self._init_database()
        
        # Check connections
        self._check_ollama()
        self._connect_alpaca()
        
        log.info("🐺 Wolf Brain Terminal initialized")
    
    def _init_database(self):
        """Initialize SQLite for memory"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Ideas/learnings table
        c.execute('''CREATE TABLE IF NOT EXISTS learnings (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            category TEXT,
            content TEXT,
            outcome TEXT
        )''')
        
        # Trades table
        c.execute('''CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            ticker TEXT,
            side TEXT,
            quantity INTEGER,
            price REAL,
            strategy TEXT,
            reasoning TEXT,
            outcome TEXT,
            pnl REAL
        )''')
        
        # Analysis log
        c.execute('''CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            ticker TEXT,
            analysis TEXT,
            decision TEXT,
            confidence REAL
        )''')
        
        conn.commit()
        conn.close()
    
    def _check_ollama(self):
        """Check if Ollama is running"""
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
            if r.status_code == 200:
                models = [m['name'] for m in r.json().get('models', [])]
                if OLLAMA_MODEL in models or any(OLLAMA_MODEL.split(':')[0] in m for m in models):
                    self.ollama_connected = True
                    log.info(f"🧠 Ollama connected (model: {OLLAMA_MODEL})")
                else:
                    log.warning(f"⚠️  Model {OLLAMA_MODEL} not found. Available: {models}")
        except:
            log.warning("⚠️  Ollama not running. Brain will use rule-based decisions.")
    
    def _connect_alpaca(self):
        """Connect to Alpaca"""
        if not ALPACA_AVAILABLE:
            log.warning("⚠️  Alpaca SDK not installed")
            return
        
        if not ALPACA_KEY or not ALPACA_SECRET:
            log.warning("⚠️  Alpaca credentials not set")
            return
        
        try:
            self.trading_client = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=True)
            self.data_client = StockHistoricalDataClient(ALPACA_KEY, ALPACA_SECRET)
            
            account = self.trading_client.get_account()
            self.alpaca_connected = True
            log.info(f"💰 Alpaca connected | Portfolio: ${float(account.portfolio_value):,.2f}")
        except Exception as e:
            log.error(f"❌ Alpaca connection failed: {e}")
    
    # ============ THINKING ============
    
    def think(self, prompt: str, context: str = "") -> str:
        """
        Use Ollama to think about something
        """
        if not self.ollama_connected:
            return "[Brain offline - using guidelines only]"
        
        full_prompt = f"""You are a Wolf Pack trader. Use this wisdom as GUIDELINES (not rigid rules):

{WOLF_PACK_WISDOM}

{f"Additional context: {context}" if context else ""}

Now think about this:
{prompt}

Be concise but thorough. Think like a trader, not a textbook."""
        
        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {"temperature": 0.7}
                },
                timeout=60
            )
            
            if r.status_code == 200:
                return r.json().get('response', '').strip()
        except Exception as e:
            log.error(f"Thinking error: {e}")
        
        return "[Thinking failed]"
    
    def analyze_ticker(self, ticker: str) -> Dict:
        """
        Full analysis of a ticker
        """
        log.info(f"🔍 Analyzing {ticker}...")
        
        # Get data
        data = self._get_ticker_data(ticker)
        if not data:
            return {'error': f'Could not get data for {ticker}'}
        
        # Format data for brain
        data_summary = f"""
TICKER: {ticker}
Price: ${data['price']:.2f}
Change Today: {data['change_pct']:+.1f}%
52W High: ${data['high_52w']:.2f}
52W Low: ${data['low_52w']:.2f}
Off High: {data['off_high']:.1f}%
Volume: {data['volume']:,} (Rel: {data['rel_volume']:.1f}x)
Avg Volume: {data['avg_volume']:,}
Market Cap: ${data['market_cap']/1e9:.2f}B
"""
        
        # Think about it
        analysis = self.think(f"""
Analyze {ticker} for potential trade:

{data_summary}

Questions to answer:
1. Is this a wounded prey setup (20-40% off highs, healthy chart)?
2. Is this a head hunter setup (low float, catalyst, squeeze potential)?
3. What's the chart health (HEALTHY stair-step or UNHEALTHY spike-crash)?
4. Should we BUY, WATCH, or AVOID?
5. If buy, what entry/stop/target?

Give your honest assessment. No trade is fine if setup isn't there.
""")
        
        # Determine decision
        decision = "WATCH"
        confidence = 0.5
        
        if "BUY" in analysis.upper() and "AVOID" not in analysis.upper():
            decision = "BUY"
            confidence = 0.7
        elif "AVOID" in analysis.upper():
            decision = "AVOID"
            confidence = 0.8
        
        # Store analysis
        self._store_analysis(ticker, analysis, decision, confidence)
        
        return {
            'ticker': ticker,
            'data': data,
            'analysis': analysis,
            'decision': decision,
            'confidence': confidence
        }
    
    def _get_ticker_data(self, ticker: str) -> Optional[Dict]:
        """Get ticker data from yfinance"""
        if not YF_AVAILABLE:
            return None
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='3mo')
            
            if hist.empty:
                return None
            
            info = stock.info
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
            high_52w = info.get('fiftyTwoWeekHigh', hist['High'].max())
            low_52w = info.get('fiftyTwoWeekLow', hist['Low'].min())
            
            return {
                'price': float(current),
                'change_pct': float((current - prev) / prev * 100),
                'high_52w': float(high_52w),
                'low_52w': float(low_52w),
                'off_high': float((high_52w - current) / high_52w * 100),
                'volume': int(hist['Volume'].iloc[-1]),
                'avg_volume': int(hist['Volume'].mean()),
                'rel_volume': float(hist['Volume'].iloc[-1] / hist['Volume'].mean()),
                'market_cap': info.get('marketCap', 0)
            }
        except Exception as e:
            log.error(f"Data error for {ticker}: {e}")
            return None
    
    # ============ TRADING ============
    
    def execute_trade(self, ticker: str, side: str, quantity: int, 
                     strategy: str, reasoning: str) -> Dict:
        """
        Execute a trade on Alpaca
        """
        if not self.alpaca_connected:
            log.error("❌ Alpaca not connected")
            return {'success': False, 'error': 'Not connected'}
        
        try:
            order_side = OrderSide.BUY if side.upper() == 'BUY' else OrderSide.SELL
            
            order = MarketOrderRequest(
                symbol=ticker,
                qty=quantity,
                side=order_side,
                time_in_force=TimeInForce.DAY
            )
            
            result = self.trading_client.submit_order(order)
            
            log.info(f"✅ {side.upper()} {quantity} {ticker} | Order ID: {result.id}")
            
            # Store trade
            self._store_trade(ticker, side, quantity, 0, strategy, reasoning)
            
            return {
                'success': True,
                'order_id': str(result.id),
                'ticker': ticker,
                'side': side,
                'quantity': quantity
            }
            
        except Exception as e:
            log.error(f"❌ Trade failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        if not self.alpaca_connected:
            return []
        
        try:
            positions = self.trading_client.get_all_positions()
            return [{
                'ticker': p.symbol,
                'qty': int(p.qty),
                'entry': float(p.avg_entry_price),
                'current': float(p.current_price),
                'pnl': float(p.unrealized_pl),
                'pnl_pct': float(p.unrealized_plpc) * 100
            } for p in positions]
        except:
            return []
    
    def get_account(self) -> Dict:
        """Get account info"""
        if not self.alpaca_connected:
            return {}
        
        try:
            acc = self.trading_client.get_account()
            return {
                'portfolio_value': float(acc.portfolio_value),
                'cash': float(acc.cash),
                'buying_power': float(acc.buying_power),
                'day_pnl': float(acc.equity) - float(acc.last_equity)
            }
        except:
            return {}
    
    # ============ LEARNING ============
    
    def learn(self, category: str, content: str):
        """
        Store a new learning/idea
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO learnings (timestamp, category, content, outcome) VALUES (?, ?, ?, ?)",
            (datetime.now().isoformat(), category, content, "pending")
        )
        conn.commit()
        conn.close()
        log.info(f"📚 Learned: [{category}] {content[:50]}...")
    
    def _store_analysis(self, ticker: str, analysis: str, decision: str, confidence: float):
        """Store analysis in database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO analyses (timestamp, ticker, analysis, decision, confidence) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().isoformat(), ticker, analysis, decision, confidence)
        )
        conn.commit()
        conn.close()
    
    def _store_trade(self, ticker: str, side: str, quantity: int, price: float,
                    strategy: str, reasoning: str):
        """Store trade in database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO trades (timestamp, ticker, side, quantity, price, strategy, reasoning, outcome, pnl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (datetime.now().isoformat(), ticker, side, quantity, price, strategy, reasoning, "open", 0)
        )
        conn.commit()
        conn.close()
    
    def get_learnings(self, limit: int = 10) -> List[Dict]:
        """Get recent learnings"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM learnings ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        
        return [{'id': r[0], 'time': r[1], 'category': r[2], 'content': r[3]} for r in rows]
    
    # ============ SCANNING ============
    
    def scan_universe(self, tickers: List[str] = None) -> List[Dict]:
        """
        Scan tickers for opportunities
        """
        if not tickers:
            # Default watchlist
            tickers = [
                'GLSI', 'BTAI', 'PMCB', 'ONCY', 'IBRX',
                'MU', 'KTOS', 'SMR', 'OKLO', 'IONQ',
                'RKLB', 'LUNR', 'SOUN', 'BBAI', 'UUUU'
            ]
        
        opportunities = []
        
        for ticker in tickers:
            try:
                result = self.analyze_ticker(ticker)
                if result.get('decision') == 'BUY':
                    opportunities.append(result)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                log.error(f"Error scanning {ticker}: {e}")
        
        # Sort by confidence
        opportunities.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return opportunities


# ============ INTERACTIVE CLI ============

def print_banner():
    """Print the Wolf Pack banner"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     🐺 W O L F   B R A I N   T E R M I N A L 🐺              ║
    ║                                                              ║
    ║     Lightweight. Thinking. Trading.                          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)


def interactive_mode(brain: TerminalBrain):
    """
    Interactive terminal interface
    """
    print_banner()
    
    print(f"🧠 Brain: {'ONLINE' if brain.ollama_connected else 'OFFLINE (rule-based)'}")
    print(f"💰 Alpaca: {'CONNECTED' if brain.alpaca_connected else 'NOT CONNECTED'}")
    print(f"📁 Data: {DATA_DIR}")
    print()
    print("Commands:")
    print("  analyze <TICKER>  - Analyze a stock")
    print("  scan              - Scan default watchlist")
    print("  positions         - Show current positions")
    print("  account           - Show account info")
    print("  buy <TICKER> <QTY> - Execute buy order")
    print("  sell <TICKER> <QTY> - Execute sell order")
    print("  learn <category> <content> - Teach the brain something")
    print("  learnings         - Show what brain has learned")
    print("  ask <question>    - Ask the brain anything")
    print("  quit              - Exit")
    print()
    
    while True:
        try:
            cmd = input("🐺 > ").strip()
            
            if not cmd:
                continue
            
            parts = cmd.split(maxsplit=2)
            action = parts[0].lower()
            
            if action == 'quit' or action == 'exit':
                print("👋 AWOOOO! (goodbye)")
                break
            
            elif action == 'analyze' and len(parts) > 1:
                ticker = parts[1].upper()
                result = brain.analyze_ticker(ticker)
                print(f"\n📊 {ticker} Analysis:")
                print(f"Decision: {result.get('decision', 'UNKNOWN')}")
                print(f"Confidence: {result.get('confidence', 0):.0%}")
                print(f"\n{result.get('analysis', 'No analysis')}")
                print()
            
            elif action == 'scan':
                print("\n🔍 Scanning watchlist...")
                opps = brain.scan_universe()
                if opps:
                    print(f"\n🎯 Found {len(opps)} opportunities:")
                    for opp in opps:
                        print(f"  {opp['ticker']}: {opp['decision']} ({opp['confidence']:.0%})")
                else:
                    print("No strong opportunities found")
                print()
            
            elif action == 'positions':
                positions = brain.get_positions()
                if positions:
                    print("\n📊 Current Positions:")
                    for p in positions:
                        emoji = "🟢" if p['pnl'] >= 0 else "🔴"
                        print(f"  {emoji} {p['ticker']}: {p['qty']} @ ${p['entry']:.2f} | P&L: ${p['pnl']:.2f} ({p['pnl_pct']:+.1f}%)")
                else:
                    print("No open positions")
                print()
            
            elif action == 'account':
                acc = brain.get_account()
                if acc:
                    print(f"\n💰 Account:")
                    print(f"  Portfolio: ${acc['portfolio_value']:,.2f}")
                    print(f"  Cash: ${acc['cash']:,.2f}")
                    print(f"  Buying Power: ${acc['buying_power']:,.2f}")
                    print(f"  Day P&L: ${acc['day_pnl']:+,.2f}")
                else:
                    print("Could not get account info")
                print()
            
            elif action == 'buy' and len(parts) >= 3:
                ticker = parts[1].upper()
                qty = int(parts[2])
                reasoning = brain.think(f"Why should we buy {ticker} right now?")
                result = brain.execute_trade(ticker, 'BUY', qty, 'manual', reasoning)
                if result['success']:
                    print(f"✅ Bought {qty} {ticker}")
                else:
                    print(f"❌ Failed: {result.get('error')}")
                print()
            
            elif action == 'sell' and len(parts) >= 3:
                ticker = parts[1].upper()
                qty = int(parts[2])
                reasoning = brain.think(f"Why should we sell {ticker} right now?")
                result = brain.execute_trade(ticker, 'SELL', qty, 'manual', reasoning)
                if result['success']:
                    print(f"✅ Sold {qty} {ticker}")
                else:
                    print(f"❌ Failed: {result.get('error')}")
                print()
            
            elif action == 'learn' and len(parts) >= 3:
                category = parts[1]
                content = parts[2]
                brain.learn(category, content)
                print(f"📚 Learned!")
                print()
            
            elif action == 'learnings':
                learnings = brain.get_learnings()
                if learnings:
                    print("\n📚 Recent Learnings:")
                    for l in learnings:
                        print(f"  [{l['category']}] {l['content'][:60]}...")
                else:
                    print("No learnings yet")
                print()
            
            elif action == 'ask':
                question = cmd[4:].strip()
                if question:
                    response = brain.think(question)
                    print(f"\n🧠 {response}\n")
                else:
                    print("Ask me something!")
                print()
            
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for commands")
                print()
                
        except KeyboardInterrupt:
            print("\n👋 AWOOOO!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='🐺 Wolf Brain Terminal')
    parser.add_argument('--scan', action='store_true', help='Scan and show opportunities')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--analyze', type=str, help='Analyze a specific ticker')
    
    args = parser.parse_args()
    
    # Initialize brain
    brain = TerminalBrain()
    
    if args.scan:
        print_banner()
        print("🔍 Scanning universe...")
        opps = brain.scan_universe()
        for opp in opps:
            print(f"\n{'='*60}")
            print(f"🎯 {opp['ticker']} - {opp['decision']} ({opp['confidence']:.0%})")
            print(opp['analysis'][:500])
        return
    
    if args.status:
        print_banner()
        print(f"🧠 Brain: {'ONLINE' if brain.ollama_connected else 'OFFLINE'}")
        print(f"💰 Alpaca: {'CONNECTED' if brain.alpaca_connected else 'NOT CONNECTED'}")
        acc = brain.get_account()
        if acc:
            print(f"📊 Portfolio: ${acc['portfolio_value']:,.2f}")
        positions = brain.get_positions()
        print(f"📈 Open Positions: {len(positions)}")
        return
    
    if args.analyze:
        print_banner()
        result = brain.analyze_ticker(args.analyze.upper())
        print(f"\n📊 {args.analyze.upper()} Analysis:")
        print(f"Decision: {result.get('decision')}")
        print(f"\n{result.get('analysis')}")
        return
    
    # Default: interactive mode
    interactive_mode(brain)


if __name__ == "__main__":
    main()
