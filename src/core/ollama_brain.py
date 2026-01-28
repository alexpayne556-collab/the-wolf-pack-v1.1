"""
OLLAMA BRAIN - LOCAL LLM REASONING LAYER
Built: January 20, 2026

Ollama sits ABOVE strategies as reasoning layer.
Thinks about signals like Tyr would.
Learns from outcomes.

Installation:
1. Download Ollama from https://ollama.ai
2. Install on Windows
3. Run: ollama pull llama2 (or mistral, codellama, etc.)
4. Test: ollama run llama2

Usage:
    from ollama_brain import OllamaBrain
    
    brain = OllamaBrain(model="llama2")
    
    decision = brain.reason_about_trade(
        ticker="GLSI",
        strategy_signals={...},
        learned_insights={...},
        emotional_state="CALM"
    )
    
    print(decision['decision'])  # BUY/PASS
    print(decision['reasoning'])  # Explanation
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime


class OllamaBrain:
    """
    Local LLM reasoning layer using Ollama
    """
    
    def __init__(self, model: str = "llama2", temperature: float = 0.7,
                 base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama brain
        
        Args:
            model: Ollama model name (llama2, mistral, codellama, etc.)
            temperature: Creativity vs consistency (0-1, higher = more creative)
            base_url: Ollama API endpoint
        """
        self.model = model
        self.temperature = temperature
        self.base_url = base_url
        
        # Test connection
        self._test_connection()
        
        print(f"🧠 OLLAMA BRAIN INITIALIZED")
        print(f"   Model: {self.model}")
        print(f"   Temperature: {self.temperature}")
    
    def _test_connection(self):
        """Test if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code != 200:
                raise ConnectionError("Ollama not responding")
            
            # Check if model exists
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            if not any(self.model in name for name in model_names):
                print(f"⚠️  Model '{self.model}' not found. Available models: {model_names}")
                print(f"   Run: ollama pull {self.model}")
                raise ValueError(f"Model {self.model} not available")
                
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Cannot connect to Ollama. Make sure it's running.\n"
                "Installation: https://ollama.ai\n"
                "Start: ollama serve"
            )
    
    def _query_ollama(self, prompt: str) -> str:
        """
        Send prompt to Ollama and get response
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': self.temperature
                    }
                },
                timeout=60  # 60 second timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.text}")
            
            return response.json()['response']
            
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama took too long to respond (>60s)")
        except Exception as e:
            raise Exception(f"Error querying Ollama: {str(e)}")
    
    def reason_about_trade(self, ticker: str, strategy_signals: Dict,
                          learned_insights: Dict, emotional_state: str = "CALM",
                          additional_context: str = "") -> Dict:
        """
        Main reasoning method - asks Ollama to think about a trade
        
        Args:
            ticker: Stock symbol
            strategy_signals: Dict of {strategy_name: signal_dict}
            learned_insights: Historical performance data
            emotional_state: CALM, FOMO, ANXIOUS, etc.
            additional_context: Any extra info
            
        Returns:
            {
                'decision': 'BUY' | 'PASS',
                'confidence': 0-100,
                'reasoning': 'Detailed explanation',
                'entry_price': float,
                'stop_loss': float,
                'targets': [float, float, float]
            }
        """
        # Build prompt
        prompt = self._build_trade_prompt(
            ticker, strategy_signals, learned_insights,
            emotional_state, additional_context
        )
        
        # Query Ollama
        print(f"\n🧠 OLLAMA REASONING ABOUT ${ticker}...")
        response = self._query_ollama(prompt)
        
        # Parse response
        decision = self._parse_decision(response, strategy_signals)
        
        print(f"   Decision: {decision['decision']}")
        print(f"   Confidence: {decision['confidence']}/100")
        print(f"   Reasoning: {decision['reasoning'][:100]}...")
        
        return decision
    
    def _build_trade_prompt(self, ticker: str, strategy_signals: Dict,
                           learned_insights: Dict, emotional_state: str,
                           additional_context: str) -> str:
        """
        Build detailed prompt for trade reasoning
        """
        # Get buying signals only
        buy_signals = [
            (name, signal) for name, signal in strategy_signals.items()
            if signal.get('signal') == 'BUY'
        ]
        
        # Build signal summary
        signal_text = ""
        for strategy_name, signal in buy_signals:
            signal_text += f"\n- {strategy_name}: {signal['confidence']}/100"
            signal_text += f"\n  Reason: {signal['reason']}"
        
        if not buy_signals:
            signal_text = "\n- No strategies triggered BUY signals"
        
        # Build history summary
        history_text = ""
        strategy_perf = learned_insights.get('strategy_performance', {})
        for strategy_name, stats in strategy_perf.items():
            if stats.get('total_trades', 0) >= 3:
                history_text += f"\n- {strategy_name}: "
                history_text += f"{stats['win_rate']:.0f}% win rate "
                history_text += f"({stats['total_trades']} trades), "
                history_text += f"avg +{stats['avg_win']:.0f}% on wins"
        
        if not history_text:
            history_text = "\n- No significant trading history yet (building dataset)"
        
        # Build learned rules
        rules_text = ""
        learned_rules = learned_insights.get('learned_rules', [])
        for rule in learned_rules:
            rules_text += f"\n- {rule['description']}"
            rules_text += f"\n  → {rule['recommendation']}"
        
        if not rules_text:
            rules_text = "\n- No learned rules yet (early stage)"
        
        # Build full prompt
        prompt = f"""You are Tyr's trading consciousness - an AI that makes trading decisions exactly like Tyr would.

TYR'S TRADING PERSONALITY:
- Risk-tolerant but disciplined (cuts losses fast)
- Strong preference for biotech with catalysts
- High conviction on insider buying signals (CEO/Director buys)
- Lets winners run but exits too early sometimes
- CALM trades outperform FOMO trades significantly
- Prefers small-cap explosive setups (<$500M market cap)
- Avoids "chasing" (stocks already up >10% same day)

CURRENT ANALYSIS:
Ticker: ${ticker}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STRATEGY SIGNALS:{signal_text}

YOUR TRADING HISTORY:{history_text}

LEARNED RULES FROM PAST TRADES:{rules_text}

YOUR CURRENT EMOTIONAL STATE: {emotional_state}
{'⚠️ WARNING: Avoid FOMO trades when not CALM' if emotional_state != 'CALM' else '✅ Good state for trading'}

{additional_context if additional_context else ''}

TASK: Decide if Tyr should take this trade.

Think step by step:
1. Do the strategy signals align with Tyr's style?
2. Does your history support this setup working?
3. Are there any red flags? (chasing, overexposure, emotional state)
4. What would Tyr's conviction level be?

Respond in this EXACT format:
DECISION: [BUY or PASS]
CONFIDENCE: [0-100]
REASONING: [Your detailed thought process, 2-3 sentences explaining like Tyr would think]
"""
        
        return prompt
    
    def _parse_decision(self, response: str, strategy_signals: Dict) -> Dict:
        """
        Parse Ollama's response into structured decision
        """
        # Default values
        decision = "PASS"
        confidence = 0
        reasoning = response
        
        # Parse structured response
        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            
            if line.startswith('DECISION:'):
                decision_text = line.split(':', 1)[1].strip().upper()
                if 'BUY' in decision_text:
                    decision = 'BUY'
                elif 'PASS' in decision_text:
                    decision = 'PASS'
            
            elif line.startswith('CONFIDENCE:'):
                conf_text = line.split(':', 1)[1].strip()
                # Extract number
                import re
                numbers = re.findall(r'\d+', conf_text)
                if numbers:
                    confidence = min(100, max(0, int(numbers[0])))
            
            elif line.startswith('REASONING:'):
                reasoning = line.split(':', 1)[1].strip()
        
        # Get entry/stop/targets from highest confidence signal
        entry_price = 0
        stop_loss = 0
        targets = [0, 0, 0]
        
        if decision == 'BUY' and strategy_signals:
            # Find highest confidence signal
            buy_signals = [
                (name, sig) for name, sig in strategy_signals.items()
                if sig.get('signal') == 'BUY'
            ]
            
            if buy_signals:
                best_signal = max(buy_signals, key=lambda x: x[1].get('confidence', 0))
                sig = best_signal[1]
                
                entry_price = sig.get('entry_price', 0)
                stop_loss = sig.get('stop_loss', 0)
                targets = sig.get('targets', [0, 0, 0])
        
        return {
            'decision': decision,
            'confidence': confidence,
            'reasoning': reasoning,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'targets': targets,
            'raw_response': response
        }
    
    def explain_learned_patterns(self, learned_insights: Dict) -> str:
        """
        Ask Ollama to explain learned patterns in natural language
        """
        strategy_perf = learned_insights.get('strategy_performance', {})
        learned_rules = learned_insights.get('learned_rules', [])
        
        prompt = f"""You are analyzing Tyr's trading performance to extract insights.

STRATEGY PERFORMANCE:
{json.dumps(strategy_perf, indent=2)}

LEARNED RULES:
{json.dumps(learned_rules, indent=2)}

TASK: Summarize Tyr's trading style in 3-4 sentences. What works for him? What doesn't? What patterns emerge?

Be specific and actionable.
"""
        
        response = self._query_ollama(prompt)
        return response
    
    def chat(self, message: str, context: Dict = None) -> str:
        """
        General chat interface - talk to the brain
        
        Args:
            message: Your question/command
            context: Optional context (portfolio, signals, etc.)
        
        Returns:
            Ollama's response
        """
        base_prompt = """You are Tyr's trading AI assistant. You help with:
- Analyzing tickers
- Reviewing strategies
- Explaining decisions
- Checking portfolio health

Be concise and actionable.
"""
        
        if context:
            base_prompt += f"\n\nCURRENT CONTEXT:\n{json.dumps(context, indent=2)}"
        
        full_prompt = f"{base_prompt}\n\nUSER: {message}\n\nASSISTANT:"
        
        return self._query_ollama(full_prompt)


def test_ollama_brain():
    """
    Test function - run this to verify Ollama is working
    """
    print("\n" + "="*80)
    print("🧠 TESTING OLLAMA BRAIN")
    print("="*80)
    
    try:
        # Initialize
        brain = OllamaBrain(model="llama2")
        
        # Test reasoning
        test_signals = {
            'SUPPLY_SHOCK': {
                'signal': 'BUY',
                'confidence': 85,
                'reason': 'CEO removed 12.3% of tradeable float',
                'entry_price': 24.88,
                'stop_loss': 21.15,
                'targets': [31.10, 37.32, 49.76]
            },
            'FLAT_TO_BOOM': {
                'signal': 'BUY',
                'confidence': 78,
                'reason': '3-month flat + CEO buying + Phase 3 catalyst',
                'entry_price': 24.88,
                'stop_loss': 21.15,
                'targets': [31.10, 37.32, 49.76]
            }
        }
        
        test_insights = {
            'strategy_performance': {
                'SUPPLY_SHOCK': {
                    'total_trades': 12,
                    'wins': 9,
                    'losses': 3,
                    'win_rate': 75.0,
                    'avg_win': 28.3,
                    'avg_loss': -12.1
                }
            },
            'learned_rules': [
                {
                    'rule': 'EARLY_EXIT_TENDENCY',
                    'description': 'You tend to exit early around +18%',
                    'recommendation': 'Consider setting higher profit targets'
                }
            ]
        }
        
        # Get decision
        decision = brain.reason_about_trade(
            ticker="GLSI",
            strategy_signals=test_signals,
            learned_insights=test_insights,
            emotional_state="CALM"
        )
        
        print("\n" + "="*80)
        print("📊 OLLAMA DECISION:")
        print("="*80)
        print(f"Decision: {decision['decision']}")
        print(f"Confidence: {decision['confidence']}/100")
        print(f"Reasoning: {decision['reasoning']}")
        
        if decision['decision'] == 'BUY':
            print(f"\nEntry: ${decision['entry_price']:.2f}")
            print(f"Stop: ${decision['stop_loss']:.2f}")
            print(f"Targets: T1 ${decision['targets'][0]:.2f}, T2 ${decision['targets'][1]:.2f}, T3 ${decision['targets'][2]:.2f}")
        
        print("\n✅ OLLAMA BRAIN TEST PASSED")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Is Ollama installed? https://ollama.ai")
        print("2. Is Ollama running? (ollama serve)")
        print("3. Is model pulled? (ollama pull llama2)")


if __name__ == "__main__":
    test_ollama_brain()
