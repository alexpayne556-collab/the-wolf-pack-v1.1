"""
🧠 WOLF BRAIN CORE - THE THINKING ENGINE
Built: January 20, 2026

This is NOT a score-based system. It THINKS.

The brain uses Ollama (local LLM) to:
- REASON about each trade opportunity
- PLAN entries, exits, and contingencies
- REFLECT on outcomes and learn
- ADAPT strategies based on experience
- ANSWER questions in natural language
- EXECUTE trades via Alpaca integration

Usage:
    from wolf_brain.brain_core import WolfBrain
    
    brain = WolfBrain(model='fenrir:latest')
    
    # Reason about a trade
    analysis = brain.reason_about_opportunity('GLSI', data)
    
    # Execute a trade
    brain.execute_buy('GLSI', conviction=0.8, reason="Insider buying cluster")
    
    # Ask it questions
    response = brain.ask("What's our best performing strategy?")
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import the complete Wolf Pack knowledge
try:
    from wolf_brain.wolf_pack_knowledge import WOLF_PACK_PHILOSOPHY, CORE_STRATEGIES, EXIT_RULES, POSITION_SIZING
except ImportError:
    from wolf_pack_knowledge import WOLF_PACK_PHILOSOPHY, CORE_STRATEGIES, EXIT_RULES, POSITION_SIZING


class WolfBrain:
    """
    The AI brain that THINKS about trades, not just scores them.
    Connected to Alpaca for real BUY/SELL execution.
    """
    
    def __init__(self, model: str = 'fenrir:latest', temperature: float = 0.7,
                 base_url: str = "http://localhost:11434"):
        """
        Initialize the Wolf Brain
        
        Args:
            model: Ollama model ('fenrir:latest', 'llama3.1:8b', 'mistral', etc.)
            temperature: Creativity level 0-1 (0.7 = balanced)
            base_url: Ollama API endpoint
        """
        self.model = model
        self.model_name = model  # For dashboard display
        self.temperature = temperature
        self.base_url = base_url
        
        # Core components (initialized later)
        self.memory = None  # Will be MemorySystem
        self.strategies = None  # Will be StrategyPluginManager
        self.trader = None  # Will be AutonomousTrader
        
        # Load Wolf Pack trading philosophy (complete knowledge base)
        self.context = WOLF_PACK_PHILOSOPHY
        self.strategies_config = CORE_STRATEGIES
        self.exit_rules = EXIT_RULES
        self.position_sizing = POSITION_SIZING
        
        # Test connection
        self.ollama_connected = self._test_connection()
        
        # Initialize trader connection
        self._init_trader()
        
        print(f"🧠 WOLF BRAIN INITIALIZED")
        print(f"   Model: {self.model}")
        print(f"   Ollama Connected: {'✅' if self.ollama_connected else '❌'}")
        print(f"   Trader Connected: {'✅' if self.trader else '❌'}")
        print(f"   Strategies Loaded: {len(self.strategies_config)}")
    
    def _init_trader(self):
        """Initialize connection to Alpaca trader"""
        try:
            try:
                from wolf_brain.autonomous_trader import AutonomousTrader
            except ImportError:
                from autonomous_trader import AutonomousTrader
            self.trader = AutonomousTrader(paper_trading=True)
        except Exception as e:
            print(f"⚠️  Trader not initialized: {e}")
            self.trader = None
    
    def _test_connection(self) -> bool:
        """Test if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '') for m in models]
                
                if not any(self.model in name for name in model_names):
                    print(f"⚠️  Model '{self.model}' not found")
                    print(f"   Available: {model_names}")
                    print(f"   Run: ollama pull {self.model}")
                    return False
                return True
            return False
        except:
            print("⚠️  Ollama not running. Start with: ollama serve")
            return False

    def think(self, prompt: str, context: str = None) -> str:
        """
        Core thinking function - asks the LLM to reason
        
        Args:
            prompt: What to think about
            context: Additional context (optional)
            
        Returns:
            LLM's thoughtful response
        """
        if not self.ollama_connected:
            return "[OFFLINE MODE] Ollama not connected. Run: ollama serve"
        
        full_context = self.context
        if context:
            full_context += f"\n\nAdditional Context:\n{context}"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    'model': self.model,
                    'prompt': f"{full_context}\n\n{prompt}",
                    'stream': False,
                    'options': {
                        'temperature': self.temperature
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"[ERROR] Ollama returned: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "[ERROR] Ollama timed out after 120s"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def reason_about_opportunity(self, ticker: str, data: Dict) -> Dict:
        """
        THINK about a potential trade opportunity
        
        This is the main analysis function. Unlike score-based systems,
        this REASONS through the opportunity like a human trader would.
        
        Args:
            ticker: Stock symbol
            data: All available data about the stock
            
        Returns:
            {
                'ticker': str,
                'decision': 'TRADE' | 'PASS' | 'WATCH',
                'confidence': int (0-100),
                'thesis': str (why this could work),
                'bear_case': str (what could go wrong),
                'entry_plan': str,
                'exit_plan': str,
                'position_size': str,
                'full_analysis': str
            }
        """
        prompt = f"""
Analyze this trading opportunity for {ticker}:

CURRENT DATA:
{json.dumps(data, indent=2, default=str)}

Please THINK through this opportunity step by step:

1. THESIS: What's the bull case? Why might this stock move up?

2. CHART HEALTH: Does this look like IBRX-style (healthy stair-step) or IVF-style (pump and dump)?

3. CATALYSTS: Are there real catalysts? FDA dates? Insider buying? Or just hype?

4. BEAR CASE: What could go wrong? What's the downside?

5. HISTORICAL COMPARISON: Have we seen similar setups before? How did they perform?

6. GUT CHECK: Is this a Tyr-style trade? Would he be excited or hesitant?

Finally, give your DECISION in this exact format:
DECISION: [TRADE or PASS or WATCH]
CONFIDENCE: [0-100]
THESIS: [One sentence summary of why]
BEAR_CASE: [One sentence on the risk]
ENTRY: [Where to enter]
STOP: [Where to stop out]
TARGET: [Profit target]
SIZE: [Position size as % of capital]
"""
        
        print(f"\n🧠 WOLF BRAIN REASONING ABOUT ${ticker}...")
        
        analysis = self.think(prompt)
        
        # Parse the structured response
        result = self._parse_analysis(ticker, analysis)
        
        print(f"   Decision: {result['decision']}")
        print(f"   Confidence: {result['confidence']}/100")
        
        return result
    
    def _parse_analysis(self, ticker: str, analysis: str) -> Dict:
        """Parse the brain's analysis into structured format"""
        
        result = {
            'ticker': ticker,
            'decision': 'PASS',
            'confidence': 0,
            'thesis': '',
            'bear_case': '',
            'entry_plan': '',
            'exit_plan': '',
            'position_size': '5%',
            'full_analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        lines = analysis.upper().split('\n')
        
        for line in lines:
            if 'DECISION:' in line:
                if 'TRADE' in line:
                    result['decision'] = 'TRADE'
                elif 'WATCH' in line:
                    result['decision'] = 'WATCH'
                else:
                    result['decision'] = 'PASS'
            
            elif 'CONFIDENCE:' in line:
                try:
                    # Extract number
                    import re
                    nums = re.findall(r'\d+', line)
                    if nums:
                        result['confidence'] = min(int(nums[0]), 100)
                except:
                    pass
        
        # Get thesis from original (not uppercased)
        for line in analysis.split('\n'):
            if line.strip().startswith('THESIS:'):
                result['thesis'] = line.replace('THESIS:', '').strip()
            elif line.strip().startswith('BEAR_CASE:'):
                result['bear_case'] = line.replace('BEAR_CASE:', '').strip()
            elif line.strip().startswith('ENTRY:'):
                result['entry_plan'] = line.replace('ENTRY:', '').strip()
            elif line.strip().startswith('TARGET:'):
                result['exit_plan'] = line.replace('TARGET:', '').strip()
            elif line.strip().startswith('SIZE:'):
                result['position_size'] = line.replace('SIZE:', '').strip()
        
        return result
    
    def plan_trade(self, analysis: Dict) -> Dict:
        """
        Create a detailed trade plan from analysis
        
        Only called if decision is TRADE
        """
        if analysis['decision'] != 'TRADE':
            return None
        
        ticker = analysis['ticker']
        
        prompt = f"""
We've decided to trade {ticker}.

Our analysis:
{analysis['full_analysis']}

Now create a detailed TRADE PLAN:

1. ENTRY STRATEGY:
   - Market or limit order?
   - At what exact price?
   - Any conditions that must be met first?

2. POSITION SIZE:
   - What % of capital and WHY?
   - Is this a "test position" (5%) or "full conviction" (10-15%)?

3. STOP LOSS:
   - Exact price level
   - WHY that level (support, %, technical)?
   - Hard stop or mental stop?

4. PROFIT TARGETS:
   - First target: Where to take 1/3 off?
   - Second target: Where to take another 1/3?
   - Final: Where to exit completely or trail?

5. TIME HORIZON:
   - How long willing to hold?
   - What changes our thesis?

6. CONTINGENCIES:
   - What if it gaps down at open?
   - What if the catalyst is delayed?
   - What if market crashes?

Be specific. This plan will be executed.
"""
        
        plan = self.think(prompt)
        
        return {
            'ticker': ticker,
            'trade_plan': plan,
            'analysis': analysis,
            'created_at': datetime.now().isoformat()
        }
    
    def reflect_on_trade(self, trade_record: Dict, outcome: Dict) -> Dict:
        """
        LEARN from a completed trade
        
        This is how the brain improves over time
        """
        prompt = f"""
Let's learn from this completed trade:

ORIGINAL ANALYSIS:
{trade_record.get('analysis', {}).get('full_analysis', 'N/A')}

TRADE PLAN:
{trade_record.get('trade_plan', 'N/A')}

ACTUAL OUTCOME:
- Entry Price: ${outcome.get('entry_price', 0)}
- Exit Price: ${outcome.get('exit_price', 0)}
- Return: {outcome.get('return_pct', 0):+.1%}
- Days Held: {outcome.get('days_held', 0)}
- Exit Reason: {outcome.get('exit_reason', 'Unknown')}

Now REFLECT honestly:

1. Was our THESIS correct? Did it move for the reasons we expected?

2. Was our TIMING good? Entry? Exit?

3. What did we get RIGHT? (Remember this)

4. What did we get WRONG? (Learn from this)

5. LESSON: One key takeaway to remember for future trades?

6. STRATEGY UPDATE: Should we change anything based on this?

7. If we saw this EXACT setup again, would we trade it the same way?

Be brutally honest. We learn more from mistakes than wins.
"""
        
        reflection = self.think(prompt)
        
        return {
            'trade': trade_record,
            'outcome': outcome,
            'reflection': reflection,
            'timestamp': datetime.now().isoformat()
        }
    
    def ask(self, question: str, context: str = None) -> str:
        """
        Ask the brain anything in natural language
        
        Examples:
            brain.ask("What's our best performing strategy?")
            brain.ask("Have we traded any biotech stocks recently?")
            brain.ask("What patterns do our losses have in common?")
            brain.ask("Should I add to my ONCY position?")
        """
        prompt = f"""
Question from Tyr: {question}

Think carefully and provide a helpful, specific answer.
If you need more information, say what you need.
If you're not sure, be honest about uncertainty.

Your answer:
"""
        
        return self.think(prompt, context)
    
    def chat(self, message: str) -> str:
        """
        Have a conversation with the brain
        
        This is more casual than ask() - for brainstorming, discussing ideas, etc.
        """
        return self.think(f"Tyr says: {message}\n\nRespond naturally as the Wolf Brain:")
    
    def teach_strategy(self, name: str, description: str) -> str:
        """
        Teach the brain a new trading strategy
        
        Args:
            name: Strategy name (e.g., "Trump Policy Play")
            description: Detailed description in plain English
            
        Returns:
            Confirmation that the strategy is understood
        """
        prompt = f"""
A new trading strategy is being added to our arsenal:

STRATEGY NAME: {name}

DESCRIPTION:
{description}

Please:
1. Summarize the CORE IDEA in one sentence
2. List the KEY SIGNALS that would trigger this strategy
3. List RED FLAGS that would disqualify a setup
4. Suggest POSITION SIZING approach
5. Suggest EXIT RULES

Confirm you understand this strategy and can identify setups matching it.
"""
        
        understanding = self.think(prompt)
        
        return f"✅ Strategy '{name}' learned.\n\n{understanding}"
    
    def morning_planning(self, market_data: Dict, positions: List[Dict], 
                        watchlist: List[str]) -> str:
        """
        Brain's morning planning session
        
        Call this at market open to get the day's game plan
        """
        prompt = f"""
Good morning! It's {datetime.now().strftime('%A, %B %d, %Y at %H:%M')}.

MARKET CONDITIONS:
{json.dumps(market_data, indent=2, default=str)}

OUR CURRENT POSITIONS:
{json.dumps(positions, indent=2, default=str)}

WATCHLIST TO MONITOR:
{', '.join(watchlist)}

Let's plan the trading day:

1. MARKET READ: What's the overall setup today? Bullish, bearish, choppy?

2. THEMES: Any major news or themes driving the market?

3. STRATEGY FIT: Which of our strategies might work well today?

4. TOP OPPORTUNITIES: Which 3 stocks should we watch closest?

5. POSITION CHECK: Should we adjust any existing positions?

6. CASH DEPLOYMENT: Should we be aggressive or defensive today?

Create a clear game plan for today.
"""
        
        return self.think(prompt)
    
    def evening_review(self, trades_today: List[Dict], pnl: float) -> str:
        """
        Brain's evening review and learning session
        
        Call this after market close
        """
        prompt = f"""
End of day review for {datetime.now().strftime('%A, %B %d')}.

TODAY'S TRADES:
{json.dumps(trades_today, indent=2, default=str)}

TODAY'S P&L: ${pnl:+,.2f}

Let's reflect:

1. Did the day go as PLANNED? What was different?

2. Were our READS on the market correct?

3. WINS: What worked? Why?

4. LOSSES: What didn't work? Why?

5. LESSONS: What should we remember tomorrow?

6. OVERNIGHT: Anything to watch or research tonight?

7. IMPROVEMENT: One thing to do better tomorrow?

Be honest and specific. This is how we get better.
"""
        
        return self.think(prompt)
    
    # ============ TRADING EXECUTION METHODS ============
    
    def execute_buy(self, ticker: str, strategy: str = 'steady_hunter',
                   conviction: float = 0.5, reason: str = "") -> Dict:
        """
        Execute a BUY trade via Alpaca
        
        Args:
            ticker: Stock symbol
            strategy: Strategy name from CORE_STRATEGIES
            conviction: 0.0-1.0 confidence level
            reason: Why we're buying
            
        Returns:
            Trade execution result
        """
        if not self.trader:
            return {'success': False, 'error': 'Trader not connected'}
        
        # Get strategy config
        strat_config = self.strategies_config.get(strategy, self.strategies_config['wounded_prey'])
        
        # Determine position size based on conviction
        if conviction >= 0.8:
            size_pct = self.position_sizing['by_conviction']['extreme']
        elif conviction >= 0.65:
            size_pct = self.position_sizing['by_conviction']['high']
        elif conviction >= 0.5:
            size_pct = self.position_sizing['by_conviction']['medium']
        else:
            size_pct = self.position_sizing['by_conviction']['low']
        
        # Map to TradeStrategy enum
        try:
            from wolf_brain.autonomous_trader import TradeStrategy
        except ImportError:
            from autonomous_trader import TradeStrategy
            
        if strategy in ['head_hunter', 'supply_shock']:
            trade_strategy = TradeStrategy.HEAD_HUNTER
        else:
            trade_strategy = TradeStrategy.STEADY_HUNTER
        
        # Get current price (would need scanner integration)
        # For now, this is handled by the trader
        try:
            trade = self.trader.execute_buy(
                ticker=ticker,
                strategy=trade_strategy,
                entry_price=0,  # Trader will get market price
                conviction=conviction,
                reason=reason
            )
            
            if trade:
                return {
                    'success': True,
                    'trade_id': trade.id,
                    'ticker': ticker,
                    'strategy': strategy,
                    'conviction': conviction
                }
            else:
                return {'success': False, 'error': 'Trade execution returned None'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def execute_sell(self, ticker: str, quantity: int = None, 
                    reason: str = "") -> Dict:
        """
        Execute a SELL trade via Alpaca
        
        Args:
            ticker: Stock symbol
            quantity: Shares to sell (None = all)
            reason: Why we're selling
            
        Returns:
            Trade execution result
        """
        if not self.trader:
            return {'success': False, 'error': 'Trader not connected'}
        
        try:
            trade = self.trader.execute_sell(
                ticker=ticker,
                quantity=quantity,
                reason=reason
            )
            
            if trade:
                return {
                    'success': True,
                    'trade_id': trade.id,
                    'ticker': ticker,
                    'quantity': trade.quantity,
                    'reason': reason
                }
            else:
                return {'success': False, 'error': 'Sell execution returned None'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def should_sell(self, ticker: str, current_price: float, entry_price: float,
                   strategy: str = 'wounded_prey') -> Dict:
        """
        Brain decides if we should sell a position
        
        Uses exit rules and LLM reasoning
        
        Returns:
            {
                'action': 'HOLD' | 'SELL_PARTIAL' | 'SELL_ALL',
                'reason': str,
                'suggested_stop': float,
                'brain_analysis': str
            }
        """
        # Calculate current P&L
        pnl_pct = (current_price - entry_price) / entry_price
        
        # Get strategy exit rules
        strat = self.strategies_config.get(strategy, self.strategies_config['wounded_prey'])
        stop_loss = strat.get('stop_loss', 0.08)
        target_1 = strat.get('target_1', 0.10)
        target_2 = strat.get('target_2', 0.20)
        
        # Rule-based checks first
        action = 'HOLD'
        reason = 'Thesis intact, within parameters'
        
        # Check stop loss
        if pnl_pct <= -stop_loss:
            action = 'SELL_ALL'
            reason = f'STOP LOSS HIT: {pnl_pct:.1%} <= -{stop_loss:.0%}'
        
        # Check target 1
        elif pnl_pct >= target_1 and pnl_pct < target_2:
            action = 'SELL_PARTIAL'
            reason = f'TARGET 1 HIT: {pnl_pct:.1%} - Consider scaling out 50%'
        
        # Check target 2
        elif pnl_pct >= target_2:
            action = 'SELL_PARTIAL'
            reason = f'TARGET 2 HIT: {pnl_pct:.1%} - Trail remaining position'
        
        # Get brain's deeper analysis
        brain_analysis = ""
        if self.ollama_connected:
            prompt = f"""
Should we sell {ticker}?

Entry: ${entry_price:.2f}
Current: ${current_price:.2f}
P&L: {pnl_pct:+.1%}
Strategy: {strategy}

Rules say: {action} - {reason}

But think deeper:
1. Is the THESIS still intact?
2. Is there more room to RUN?
3. Are there WARNING signs we're missing?
4. What would you do?

Keep response brief (3-5 sentences).
"""
            brain_analysis = self.think(prompt)
        
        return {
            'action': action,
            'reason': reason,
            'current_pnl': pnl_pct,
            'suggested_stop': entry_price * (1 - stop_loss),
            'target_1': entry_price * (1 + target_1),
            'target_2': entry_price * (1 + target_2),
            'brain_analysis': brain_analysis
        }
    
    def get_trading_status(self) -> Dict:
        """Get current trading status from Alpaca"""
        if not self.trader:
            return {'connected': False, 'error': 'Trader not initialized'}
        
        return self.trader.get_status()
    
    def get_positions(self) -> Dict:
        """Get all open positions"""
        if not self.trader:
            return {}
        
        return self.trader.get_open_positions()
    
    def manage_all_positions(self, current_prices: Dict[str, float] = None):
        """
        Have the brain manage all open positions
        
        This checks stops, targets, and decides on exits
        """
        if not self.trader:
            print("⚠️ Trader not connected")
            return
        
        self.trader.manage_positions(current_prices)


# ============ TESTING ============

def test_brain():
    """Test the Wolf Brain"""
    print("\n" + "="*80)
    print("🧠 TESTING WOLF BRAIN")
    print("="*80)
    
    brain = WolfBrain(model='fenrir:latest')
    
    if not brain.ollama_connected:
        print("\n⚠️  Ollama not connected. To test:")
        print("   1. Install Ollama: https://ollama.ai")
        print("   2. Run: ollama pull mistral")
        print("   3. Start: ollama serve")
        print("   4. Run this test again")
        return
    
    # Test asking a question
    print("\n📝 Testing: Ask a question")
    response = brain.ask("What makes a biotech stock a good trade?")
    print(f"Response: {response[:500]}...")
    
    # Test reasoning
    print("\n📝 Testing: Reason about opportunity")
    test_data = {
        'ticker': 'GLSI',
        'price': 24.88,
        'float': 6570000,
        'short_interest': '24.33%',
        'insider_buying': '$340K in past month',
        'catalyst': 'Phase 3 breast cancer vaccine data pending',
        'chart_health': 'HEALTHY - stair-step pattern'
    }
    
    analysis = brain.reason_about_opportunity('GLSI', test_data)
    print(f"Decision: {analysis['decision']}")
    print(f"Confidence: {analysis['confidence']}/100")
    print(f"Thesis: {analysis['thesis']}")
    
    # Test teaching a strategy
    print("\n📝 Testing: Teach new strategy")
    result = brain.teach_strategy(
        "After Hours Gap",
        """
        When a stock gaps up 5-15% after hours on REAL NEWS:
        - Gap must be 5-15% (not already exploded)
        - Must have real catalyst (FDA, earnings, contract)
        - Volume must be elevated (2x+ normal AH)
        - Buy in premarket if continuation confirms
        - Sell into morning spike (10-11am usually)
        - Stop if it fades below previous close
        """
    )
    print(f"Result: {result[:500]}...")
    
    # Test trading execution
    if brain.trader:
        print("\n📝 Testing: Trade execution")
        status = brain.get_trading_status()
        print(f"Trading Status: {status}")
    
    print("\n✅ Wolf Brain tests complete!")


if __name__ == "__main__":
    test_brain()
