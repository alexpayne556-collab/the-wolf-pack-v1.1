"""
WOLF TERMINAL - LIGHTWEIGHT THINKING TRADER
Built: January 20, 2026

NO GUI. Runs light. Brain THINKS, doesn't follow rigid rules.
Uses Leonard File as GUIDELINES. Experiments, learns, adapts.
Paper trades on Alpaca. Logs everything.

Usage:
    python wolf_terminal.py              # Interactive mode
    python wolf_terminal.py --auto       # Autonomous hunting mode
    python wolf_terminal.py --scan       # Quick scan
    python wolf_terminal.py --chat       # Just chat with brain
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading

# Load .env file for API keys
def load_env():
    """Load environment variables from .env file"""
    env_paths = [
        os.path.join(os.path.dirname(__file__), '..', '..', '.env'),
        os.path.join(os.path.dirname(__file__), '..', '.env'),
        '.env'
    ]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"').strip("'")
            print(f"[OK] Loaded env from {env_path}")
            return True
    return False

load_env()

# Setup logging (ASCII only for Windows compatibility)
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'wolf_brain', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, f'wolf_{datetime.now().strftime("%Y%m%d")}.log'), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('WolfTerminal')

# ============ THE KNOWLEDGE (GUIDELINES, NOT RULES) ============

WOLF_PACK_WISDOM = """
🐺 WOLF PACK TRADING WISDOM
These are GUIDELINES - think about them, don't blindly follow.

THE LEONARD FILE CORE PRINCIPLES:
1. RGC taught us: Supply destruction = physics, not speculation
   - Low float + insider buying + catalyst = explosive potential
   - CEO bought 81% of float → 20,000% move
   - This is MATH, not magic

2. WOUNDED PREY STRATEGY (our best edge so far):
   - Look for quality stocks down 20-40% from highs
   - Healthy chart pattern (stair-step up, not spike-crash)
   - Volume confirming interest
   - IBRX example: caught at +39.75%

3. HEAD HUNTER STRATEGY (moonshots):
   - Ultra-low float (<10M shares)
   - High insider ownership (>50%)
   - Binary catalyst approaching
   - Short squeeze potential (>15% short)

4. EXIT WISDOM (critical):
   - Let winners ride, cut losers fast
   - Scale out: sell 50% at first target, ride rest
   - Move stop to breakeven after partial
   - Trailing stop after big gains (10-15%)
   - NEVER let a winner turn into a loser

5. WHAT TO AVOID:
   - Spike-and-crash charts (IVF-style traps)
   - Chasing after 50%+ moves
   - Overconcentration in one sector
   - Trading on FOMO or revenge
   - Positions too large to exit cleanly

6. MARKET WIZARDS WISDOM:
   - PTJ: "The most important rule is to play great defense"
   - Livermore: "It was never my thinking that made big money, it was my sitting"
   - Kovner: "Risk no more than 2% of portfolio on any trade"
   - All of them: "Cut losses short, let profits run"

7. THE HUMILITY EDGE:
   - Never think you've figured it out
   - Market changes constantly
   - What worked yesterday may fail today
   - Stay curious, stay humble

CURRENT WATCHLIST PRIORITIES:
- GLSI: CEO buying $340K+, 24% short, Phase 3 catalyst
- BTAI: sNDA Q1 2026, tiny market cap, Fast Track
- PMCB: Trading below cash value, cluster insider buying
- IBRX: Already +39.75%, thesis intact

REMEMBER: These are THOUGHTS to consider, not rules to follow blindly.
The brain should THINK about each situation uniquely.
"""


class WolfBrain:
    """Lightweight brain using Ollama - THINKS, doesn't just score"""
    
    def __init__(self, model: str = 'fenrir:latest'):
        self.model = model
        self.base_url = "http://localhost:11434"
        self.connected = self._check_connection()
        self.conversation_history = []
        self.decisions_log = []
        
        if self.connected:
            logger.info(f"[BRAIN] Connected: {model}")
        else:
            logger.warning("[BRAIN] Offline - will use fallback logic")
    
    def _check_connection(self) -> bool:
        """Check if Ollama is running"""
        try:
            import requests
            r = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return r.status_code == 200
        except:
            return False
    
    def think(self, prompt: str, context: str = "") -> str:
        """
        Have the brain THINK about something
        Returns its reasoning, not just a score
        """
        if not self.connected:
            return "[Brain offline - using fallback logic]"
        
        full_prompt = f"""You are Fenrir, the Wolf Pack's trading brain.

CONTEXT (use as guidelines, not rigid rules):
{WOLF_PACK_WISDOM}

{context}

NOW THINK ABOUT THIS:
{prompt}

Give your REASONING. Think it through. What do you notice? What concerns you? What excites you?
Be honest - say "I don't know" if uncertain. This is real money.
"""
        
        try:
            import requests
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {"temperature": 0.7}
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json().get('response', '')
                self.conversation_history.append({
                    'time': datetime.now().isoformat(),
                    'prompt': prompt[:200],
                    'response': result[:500]
                })
                return result
            else:
                return f"[Brain error: {response.status_code}]"
                
        except Exception as e:
            logger.error(f"Brain think error: {e}")
            return f"[Brain error: {e}]"
    
    def should_buy(self, ticker: str, data: Dict) -> Tuple[bool, str, float]:
        """
        Ask brain if we should buy
        Returns: (should_buy, reasoning, confidence 0-1)
        """
        prompt = f"""
TICKER: {ticker}
CURRENT DATA:
- Price: ${data.get('price', 'N/A')}
- Change today: {data.get('change_pct', 'N/A')}%
- Volume vs avg: {data.get('rel_volume', 'N/A')}x
- Off 52w high: {data.get('off_high_pct', 'N/A')}%
- Float: {data.get('float', 'N/A')}
- Short interest: {data.get('short_pct', 'N/A')}%

QUESTION: Should we BUY this? 

Think through:
1. Does this fit any of our strategies (wounded prey, head hunter)?
2. What's the risk/reward?
3. What could go wrong?
4. What's the catalyst or reason to act NOW?

End with: DECISION: BUY or PASS, CONFIDENCE: 0-100%
"""
        
        reasoning = self.think(prompt)
        
        # Parse decision from response
        should_buy = 'DECISION: BUY' in reasoning.upper()
        
        # Extract confidence
        confidence = 0.5
        if 'CONFIDENCE:' in reasoning.upper():
            try:
                conf_text = reasoning.upper().split('CONFIDENCE:')[1][:10]
                conf_num = ''.join(c for c in conf_text if c.isdigit())
                if conf_num:
                    confidence = min(int(conf_num) / 100, 1.0)
            except:
                pass
        
        # Log decision
        self.decisions_log.append({
            'time': datetime.now().isoformat(),
            'ticker': ticker,
            'decision': 'BUY' if should_buy else 'PASS',
            'confidence': confidence,
            'reasoning': reasoning[:500]
        })
        
        return should_buy, reasoning, confidence
    
    def should_sell(self, ticker: str, data: Dict, entry_price: float) -> Tuple[bool, str, str]:
        """
        Ask brain if we should sell
        Returns: (should_sell, reasoning, sell_type: 'STOP'/'TARGET'/'TRAIL'/'HOLD')
        """
        current_price = data.get('price', entry_price)
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        
        prompt = f"""
POSITION: {ticker}
- Entry: ${entry_price:.2f}
- Current: ${current_price:.2f}
- P&L: {pnl_pct:+.1f}%
- Today's change: {data.get('change_pct', 'N/A')}%
- Volume: {data.get('rel_volume', 'N/A')}x average

QUESTION: Should we SELL, and why?

Consider:
1. Is it hitting a target? (10-20% for steady, 50%+ for moonshot)
2. Is it breaking down? (stop loss territory)
3. Has the thesis changed?
4. Should we scale out (sell half)?
5. Let it ride with trailing stop?

End with: ACTION: SELL/SCALE_OUT/TRAIL/HOLD, REASON: brief
"""
        
        reasoning = self.think(prompt)
        
        # Parse action
        action = 'HOLD'
        for act in ['SELL', 'SCALE_OUT', 'TRAIL', 'HOLD']:
            if f'ACTION: {act}' in reasoning.upper():
                action = act
                break
        
        should_sell = action in ['SELL', 'SCALE_OUT']
        
        return should_sell, reasoning, action


class AlpacaTrader:
    """Lightweight Alpaca integration for paper trading"""
    
    def __init__(self):
        self.api_key = os.environ.get('APCA_API_KEY_ID')
        self.api_secret = os.environ.get('APCA_API_SECRET_KEY')
        self.base_url = "https://paper-api.alpaca.markets"
        self.connected = False
        self.client = None
        
        self._connect()
    
    def _connect(self):
        """Connect to Alpaca"""
        if not self.api_key or not self.api_secret:
            logger.warning("[ALPACA] Keys not set in environment")
            return
        
        try:
            from alpaca.trading.client import TradingClient
            self.client = TradingClient(self.api_key, self.api_secret, paper=True)
            account = self.client.get_account()
            self.connected = True
            logger.info(f"[ALPACA] Connected: ${float(account.portfolio_value):,.2f}")
        except Exception as e:
            logger.error(f"❌ Alpaca connection failed: {e}")
    
    def get_account(self) -> Dict:
        """Get account info"""
        if not self.connected:
            return {'error': 'Not connected'}
        
        try:
            account = self.client.get_account()
            return {
                'equity': float(account.equity),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        if not self.connected:
            return []
        
        try:
            positions = self.client.get_all_positions()
            return [{
                'ticker': p.symbol,
                'qty': float(p.qty),
                'entry': float(p.avg_entry_price),
                'current': float(p.current_price),
                'pnl': float(p.unrealized_pl),
                'pnl_pct': float(p.unrealized_plpc) * 100
            } for p in positions]
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def buy(self, ticker: str, qty: int = None, dollars: float = None) -> Dict:
        """
        Buy shares
        Specify either qty OR dollars (notional order)
        """
        if not self.connected:
            return {'error': 'Not connected'}
        
        try:
            from alpaca.trading.requests import MarketOrderRequest
            from alpaca.trading.enums import OrderSide, TimeInForce
            
            if dollars:
                # Notional order (dollar amount)
                order = self.client.submit_order(
                    MarketOrderRequest(
                        symbol=ticker,
                        notional=dollars,
                        side=OrderSide.BUY,
                        time_in_force=TimeInForce.DAY
                    )
                )
            else:
                order = self.client.submit_order(
                    MarketOrderRequest(
                        symbol=ticker,
                        qty=qty,
                        side=OrderSide.BUY,
                        time_in_force=TimeInForce.DAY
                    )
                )
            
            logger.info(f"[BUY] {ticker} | {qty or f'${dollars}'} | ID: {order.id}")
            return {'success': True, 'order_id': str(order.id), 'ticker': ticker}
            
        except Exception as e:
            logger.error(f"[BUY FAILED] {e}")
            return {'error': str(e)}
    
    def sell(self, ticker: str, qty: int = None) -> Dict:
        """Sell shares (qty=None sells all)"""
        if not self.connected:
            return {'error': 'Not connected'}
        
        try:
            from alpaca.trading.requests import MarketOrderRequest
            from alpaca.trading.enums import OrderSide, TimeInForce
            
            if qty is None:
                # Sell all
                positions = {p.symbol: p for p in self.client.get_all_positions()}
                if ticker not in positions:
                    return {'error': f'No position in {ticker}'}
                qty = int(float(positions[ticker].qty))
            
            order = self.client.submit_order(
                MarketOrderRequest(
                    symbol=ticker,
                    qty=qty,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )
            )
            
            logger.info(f"[SELL] {ticker} | {qty} shares | ID: {order.id}")
            return {'success': True, 'order_id': str(order.id), 'ticker': ticker}
            
        except Exception as e:
            logger.error(f"[SELL FAILED] {e}")
            return {'error': str(e)}


class DataFetcher:
    """Lightweight data fetcher using yfinance"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
    
    def get_ticker_data(self, ticker: str, use_cache: bool = True) -> Dict:
        """Get basic data for a ticker"""
        # Check cache (5 min)
        if use_cache and ticker in self.cache:
            if datetime.now() - self.cache_time.get(ticker, datetime.min) < timedelta(minutes=5):
                return self.cache[ticker]
        
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            hist = stock.history(period='3mo')
            info = stock.info
            
            if hist.empty:
                return {'error': 'No data'}
            
            current = hist['Close'].iloc[-1]
            high_52w = info.get('fiftyTwoWeekHigh', hist['High'].max())
            avg_vol = hist['Volume'].mean()
            
            data = {
                'ticker': ticker,
                'price': float(current),
                'change_pct': float((current - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) if len(hist) > 1 else 0,
                'off_high_pct': float((high_52w - current) / high_52w * 100) if high_52w > 0 else 0,
                'rel_volume': float(hist['Volume'].iloc[-1] / avg_vol) if avg_vol > 0 else 1,
                'float': info.get('floatShares', 0),
                'short_pct': (info.get('shortPercentOfFloat', 0) or 0) * 100,
                'market_cap': info.get('marketCap', 0)
            }
            
            self.cache[ticker] = data
            self.cache_time[ticker] = datetime.now()
            return data
            
        except Exception as e:
            return {'error': str(e), 'ticker': ticker}
    
    def scan_watchlist(self, tickers: List[str]) -> List[Dict]:
        """Scan a list of tickers"""
        results = []
        for ticker in tickers:
            data = self.get_ticker_data(ticker)
            if 'error' not in data:
                results.append(data)
            time.sleep(0.2)  # Rate limit
        return results


class WolfTerminal:
    """
    The main terminal interface
    Lightweight, thinks, trades, learns
    """
    
    def __init__(self):
        print("\n" + "="*60)
        print("🐺 WOLF TERMINAL - Lightweight Thinking Trader")
        print("="*60 + "\n")
        
        self.brain = WolfBrain()
        self.trader = AlpacaTrader()
        self.data = DataFetcher()
        
        # Default watchlist
        self.watchlist = [
            'GLSI', 'BTAI', 'PMCB', 'ONCY', 'IBRX',
            'KTOS', 'RKLB', 'SMR', 'OKLO', 'IONQ',
            'MU', 'NVDA', 'PLTR', 'COIN', 'HOOD'
        ]
        
        # Trading state
        self.position_entries = {}  # ticker -> entry_price
        self.daily_trades = 0
        self.max_daily_trades = 5  # Don't overtrade
        
        logger.info("Wolf Terminal initialized")
    
    def show_status(self):
        """Show current status"""
        print("\n" + "-"*50)
        print("📊 CURRENT STATUS")
        print("-"*50)
        
        # Account
        if self.trader.connected:
            account = self.trader.get_account()
            print(f"💰 Portfolio: ${account.get('portfolio_value', 0):,.2f}")
            print(f"💵 Cash: ${account.get('cash', 0):,.2f}")
            print(f"🛒 Buying Power: ${account.get('buying_power', 0):,.2f}")
        else:
            print("⚠️  Alpaca not connected")
        
        # Positions
        positions = self.trader.get_positions()
        if positions:
            print(f"\n📈 POSITIONS ({len(positions)}):")
            for p in positions:
                emoji = '🟢' if p['pnl'] > 0 else '🔴'
                print(f"   {emoji} {p['ticker']}: {p['qty']} @ ${p['entry']:.2f} → ${p['current']:.2f} ({p['pnl_pct']:+.1f}%)")
        else:
            print("\n📈 No open positions")
        
        # Brain status
        print(f"\n🧠 Brain: {'ONLINE' if self.brain.connected else 'OFFLINE'}")
        print(f"📝 Decisions logged: {len(self.brain.decisions_log)}")
    
    def scan(self):
        """Scan watchlist and get brain's thoughts"""
        print("\n" + "-"*50)
        print("🔍 SCANNING WATCHLIST...")
        print("-"*50)
        
        results = self.data.scan_watchlist(self.watchlist)
        
        opportunities = []
        
        for data in results:
            ticker = data['ticker']
            
            # Quick filter
            off_high = data.get('off_high_pct', 0)
            rel_vol = data.get('rel_volume', 1)
            
            # Wounded prey check
            is_wounded = 15 <= off_high <= 50
            has_volume = rel_vol >= 1.2
            
            status = ""
            if is_wounded and has_volume:
                status = "⚡ POTENTIAL"
                opportunities.append(data)
            elif is_wounded:
                status = "👀 watching"
            elif data.get('change_pct', 0) > 5:
                status = "🚀 moving"
            
            print(f"   {ticker}: ${data['price']:.2f} ({data['change_pct']:+.1f}%) | {off_high:.0f}% off high | Vol: {rel_vol:.1f}x {status}")
        
        # Get brain's take on opportunities
        if opportunities and self.brain.connected:
            print("\n🧠 BRAIN'S THOUGHTS ON TOP OPPORTUNITIES:")
            for opp in opportunities[:3]:
                print(f"\n--- {opp['ticker']} ---")
                should_buy, reasoning, confidence = self.brain.should_buy(opp['ticker'], opp)
                print(f"Decision: {'BUY' if should_buy else 'PASS'} (Confidence: {confidence:.0%})")
                print(f"Reasoning: {reasoning[:300]}...")
        
        return opportunities
    
    def check_positions(self):
        """Check positions and decide on exits"""
        positions = self.trader.get_positions()
        
        if not positions:
            return
        
        print("\n" + "-"*50)
        print("📊 CHECKING POSITIONS...")
        print("-"*50)
        
        for pos in positions:
            ticker = pos['ticker']
            data = self.data.get_ticker_data(ticker)
            
            if 'error' in data:
                continue
            
            entry = pos['entry']
            current = pos['current']
            pnl_pct = pos['pnl_pct']
            
            print(f"\n{ticker}: ${entry:.2f} → ${current:.2f} ({pnl_pct:+.1f}%)")
            
            # Get brain's take on selling
            if self.brain.connected:
                should_sell, reasoning, action = self.brain.should_sell(ticker, data, entry)
                print(f"Brain says: {action}")
                print(f"Reasoning: {reasoning[:200]}...")
                
                if should_sell and action == 'SELL':
                    confirm = input(f"Execute SELL for {ticker}? (y/n): ").strip().lower()
                    if confirm == 'y':
                        result = self.trader.sell(ticker)
                        print(f"Result: {result}")
                elif action == 'SCALE_OUT':
                    qty = int(pos['qty'] / 2)
                    confirm = input(f"Sell half ({qty} shares) of {ticker}? (y/n): ").strip().lower()
                    if confirm == 'y':
                        result = self.trader.sell(ticker, qty)
                        print(f"Result: {result}")
    
    def chat(self, message: str) -> str:
        """Chat with the brain"""
        if not self.brain.connected:
            return "Brain is offline"
        return self.brain.think(message)
    
    def teach(self, idea: str):
        """Teach the brain a new idea/strategy"""
        prompt = f"""
NEW IDEA FROM TYR:
{idea}

Think about this. How does it fit with our existing strategies?
What's good about it? What could go wrong?
How would you apply it?

Store this as a new guideline to consider.
"""
        response = self.brain.think(prompt)
        print(f"\n🧠 Brain's thoughts:\n{response}")
        
        # Log the teaching
        logger.info(f"TAUGHT: {idea[:100]}")
    
    def execute_trade(self, ticker: str, dollars: float = None):
        """Execute a trade with brain confirmation"""
        data = self.data.get_ticker_data(ticker)
        
        if 'error' in data:
            print(f"❌ Error getting data: {data['error']}")
            return
        
        print(f"\n📊 {ticker}: ${data['price']:.2f}")
        
        # Get brain's opinion
        should_buy, reasoning, confidence = self.brain.should_buy(ticker, data)
        
        print(f"\n🧠 Brain says: {'BUY' if should_buy else 'PASS'} ({confidence:.0%} confidence)")
        print(f"Reasoning: {reasoning[:400]}...")
        
        if should_buy or input("\nProceed anyway? (y/n): ").strip().lower() == 'y':
            if dollars is None:
                dollars = float(input("Amount to invest ($): "))
            
            result = self.trader.buy(ticker, dollars=dollars)
            print(f"Result: {result}")
            
            if result.get('success'):
                self.position_entries[ticker] = data['price']
                self.daily_trades += 1
    
    def run_interactive(self):
        """Interactive terminal mode"""
        print("\n🐺 WOLF TERMINAL READY")
        print("Commands: scan, status, positions, check, buy <TICKER>, sell <TICKER>")
        print("          chat <message>, teach <idea>, watchlist, quit")
        print("-"*60)
        
        while True:
            try:
                cmd = input("\n🐺 > ").strip()
                
                if not cmd:
                    continue
                
                parts = cmd.split(maxsplit=1)
                action = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""
                
                if action == 'quit' or action == 'exit':
                    print("👋 Wolf out. AWOOOO!")
                    break
                
                elif action == 'scan':
                    self.scan()
                
                elif action == 'status':
                    self.show_status()
                
                elif action == 'positions' or action == 'pos':
                    self.check_positions()
                
                elif action == 'check':
                    self.check_positions()
                
                elif action == 'buy':
                    if arg:
                        self.execute_trade(arg.upper())
                    else:
                        print("Usage: buy <TICKER>")
                
                elif action == 'sell':
                    if arg:
                        result = self.trader.sell(arg.upper())
                        print(f"Result: {result}")
                    else:
                        print("Usage: sell <TICKER>")
                
                elif action == 'chat':
                    if arg:
                        response = self.chat(arg)
                        print(f"\n🧠 {response}")
                    else:
                        print("Usage: chat <message>")
                
                elif action == 'teach':
                    if arg:
                        self.teach(arg)
                    else:
                        print("Usage: teach <new strategy or idea>")
                
                elif action == 'watchlist' or action == 'wl':
                    if arg:
                        self.watchlist = [t.strip().upper() for t in arg.split(',')]
                        print(f"Watchlist updated: {self.watchlist}")
                    else:
                        print(f"Current watchlist: {self.watchlist}")
                
                elif action == 'analyze' or action == 'a':
                    if arg:
                        data = self.data.get_ticker_data(arg.upper())
                        print(f"\n{json.dumps(data, indent=2)}")
                        if self.brain.connected:
                            should_buy, reasoning, conf = self.brain.should_buy(arg.upper(), data)
                            print(f"\n🧠 Brain: {'BUY' if should_buy else 'PASS'} ({conf:.0%})")
                            print(reasoning[:500])
                    else:
                        print("Usage: analyze <TICKER>")
                
                elif action == 'log' or action == 'logs':
                    print(f"\n📝 Recent decisions ({len(self.brain.decisions_log)}):")
                    for d in self.brain.decisions_log[-5:]:
                        print(f"   {d['time'][:16]} | {d['ticker']} | {d['decision']} | {d['confidence']:.0%}")
                
                elif action == 'help':
                    print("""
Commands:
  scan              - Scan watchlist for opportunities
  status            - Show account and positions
  positions/pos     - Check positions with brain analysis
  check             - Same as positions
  buy <TICKER>      - Execute buy with brain confirmation
  sell <TICKER>     - Sell position
  chat <message>    - Chat with the brain
  teach <idea>      - Teach brain a new strategy/idea
  watchlist [list]  - View or set watchlist (comma separated)
  analyze <TICKER>  - Deep analysis of a ticker
  log               - View recent decisions
  quit              - Exit
""")
                
                else:
                    # Treat as chat
                    response = self.chat(cmd)
                    print(f"\n🧠 {response}")
                    
            except KeyboardInterrupt:
                print("\n👋 Wolf out.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def run_auto(self, interval_minutes: int = 30):
        """
        Autonomous mode - scans and trades on its own
        Still needs human to start it, but then runs independently
        """
        print("\n🤖 AUTONOMOUS MODE ACTIVATED")
        print(f"   Scanning every {interval_minutes} minutes")
        print("   Press Ctrl+C to stop\n")
        
        while True:
            try:
                # Morning routine (if market open)
                hour = datetime.now().hour
                
                if 9 <= hour < 16:  # Market hours (roughly)
                    # Scan for opportunities
                    logger.info("Running scan...")
                    opportunities = self.scan()
                    
                    # Check existing positions
                    self.check_positions()
                    
                    # Auto-trade if high confidence opportunity
                    if self.daily_trades < self.max_daily_trades:
                        for opp in opportunities[:2]:
                            data = opp
                            ticker = data['ticker']
                            
                            should_buy, reasoning, confidence = self.brain.should_buy(ticker, data)
                            
                            if should_buy and confidence >= 0.7:
                                logger.info(f"[TARGET] High confidence buy: {ticker} ({confidence:.0%})")
                                
                                # Small position size for auto trades
                                account = self.trader.get_account()
                                position_size = account.get('portfolio_value', 0) * 0.03  # 3% max
                                
                                if position_size > 0:
                                    result = self.trader.buy(ticker, dollars=position_size)
                                    logger.info(f"Auto trade result: {result}")
                                    self.daily_trades += 1
                else:
                    logger.info("Market closed - waiting...")
                
                # Wait for next cycle
                logger.info(f"Sleeping {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Auto mode stopped")
                break
            except Exception as e:
                logger.error(f"Auto mode error: {e}")
                time.sleep(60)


def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description='🐺 Wolf Terminal')
    parser.add_argument('--auto', action='store_true', help='Autonomous trading mode')
    parser.add_argument('--scan', action='store_true', help='Quick scan and exit')
    parser.add_argument('--chat', action='store_true', help='Chat mode only')
    parser.add_argument('--interval', type=int, default=30, help='Auto mode interval (minutes)')
    
    args = parser.parse_args()
    
    wolf = WolfTerminal()
    
    if args.scan:
        wolf.scan()
    elif args.auto:
        wolf.run_auto(args.interval)
    elif args.chat:
        print("🧠 Chat mode - type 'quit' to exit")
        while True:
            msg = input("\nYou: ").strip()
            if msg.lower() == 'quit':
                break
            response = wolf.chat(msg)
            print(f"\n🧠 Fenrir: {response}")
    else:
        wolf.run_interactive()


if __name__ == "__main__":
    main()
