"""
🔌 STRATEGY PLUGIN SYSTEM - ADD STRATEGIES ANYTIME
Built: January 20, 2026

The brain can learn NEW strategies at any time:
1. Natural Language: Just describe it in English
2. Examples: Show it winning trade examples
3. Conversation: Just chat about patterns you notice

Usage:
    from wolf_brain.strategy_plugins import StrategyPluginManager
    
    manager = StrategyPluginManager(brain)
    
    # Add strategy by description
    manager.add_strategy_from_description(
        name="Trump Policy Play",
        description="Look for defense stocks when..."
    )
    
    # Add by showing examples
    manager.teach_by_example(
        name="FDA Runner",
        examples=[{'ticker': 'IBRX', 'outcome': '+197%'}]
    )
    
    # Check which strategies apply to a setup
    applicable = manager.get_applicable_strategies(setup_data)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.created_at = datetime.now().isoformat()
        self.performance = {
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'total_return': 0.0,
            'best_trade': 0.0,
            'worst_trade': 0.0
        }
    
    @abstractmethod
    def applies_to(self, setup_data: Dict) -> bool:
        """Check if this strategy applies to a setup"""
        pass
    
    @abstractmethod
    def analyze(self, ticker: str, data: Dict) -> Dict:
        """Analyze a ticker with this strategy"""
        pass
    
    def get_signal_strength(self, setup_data: Dict) -> int:
        """Return signal strength 0-100"""
        return 50  # Default medium
    
    def update_performance(self, trade_result: Dict):
        """Update performance metrics after a trade"""
        self.performance['trades'] += 1
        
        return_pct = trade_result.get('return_pct', 0)
        self.performance['total_return'] += return_pct
        
        if return_pct > 0:
            self.performance['wins'] += 1
            self.performance['best_trade'] = max(self.performance['best_trade'], return_pct)
        else:
            self.performance['losses'] += 1
            self.performance['worst_trade'] = min(self.performance['worst_trade'], return_pct)


class NaturalLanguageStrategy(BaseStrategy):
    """
    A strategy defined in plain English
    The brain interprets and applies it
    """
    
    def __init__(self, name: str, description: str, brain):
        super().__init__(name, description)
        self.brain = brain
        self.compiled_understanding = None
        self._compile_strategy()
    
    def _compile_strategy(self):
        """Ask the brain to understand the strategy"""
        if not self.brain or not self.brain.ollama_connected:
            self.compiled_understanding = self.description
            return
        
        prompt = f"""
Learn this trading strategy:

NAME: {self.name}

DESCRIPTION:
{self.description}

Summarize:
1. CORE IDEA in one sentence
2. KEY ENTRY SIGNALS (what to look for)
3. RED FLAGS (what disqualifies a setup)
4. POSITION SIZE approach
5. EXIT RULES

Remember this - you'll use it to find setups.
"""
        self.compiled_understanding = self.brain.think(prompt)
    
    def applies_to(self, setup_data: Dict) -> bool:
        """Ask the brain if this strategy applies"""
        if not self.brain or not self.brain.ollama_connected:
            # Offline mode - basic keyword matching
            desc_lower = self.description.lower()
            
            # Check for obvious matches
            if 'biotech' in desc_lower and setup_data.get('sector') == 'biotech':
                return True
            if 'insider' in desc_lower and setup_data.get('insider_buying'):
                return True
            if 'fda' in desc_lower and setup_data.get('fda_catalyst'):
                return True
            
            return False
        
        prompt = f"""
Does the "{self.name}" strategy apply to this setup?

STRATEGY:
{self.description}

SETUP:
{json.dumps(setup_data, indent=2, default=str)}

Answer: YES or NO, then explain briefly.
"""
        response = self.brain.think(prompt)
        return response.strip().upper().startswith('YES')
    
    def analyze(self, ticker: str, data: Dict) -> Dict:
        """Use the brain to analyze with this strategy"""
        if not self.brain or not self.brain.ollama_connected:
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'reason': 'Brain offline - cannot analyze'
            }
        
        prompt = f"""
Analyze {ticker} using the "{self.name}" strategy:

STRATEGY:
{self.description}

DATA:
{json.dumps(data, indent=2, default=str)}

Does this fit our strategy? 
Return: SIGNAL (BUY/PASS), CONFIDENCE (0-100), REASON (one line)

Format:
SIGNAL: [BUY or PASS]
CONFIDENCE: [0-100]
REASON: [Why]
"""
        response = self.brain.think(prompt)
        
        # Parse response
        signal = 'PASS'
        confidence = 0
        reason = response
        
        for line in response.upper().split('\n'):
            if 'SIGNAL:' in line:
                if 'BUY' in line:
                    signal = 'BUY'
            elif 'CONFIDENCE:' in line:
                import re
                nums = re.findall(r'\d+', line)
                if nums:
                    confidence = min(int(nums[0]), 100)
        
        for line in response.split('\n'):
            if line.strip().lower().startswith('reason:'):
                reason = line.split(':', 1)[1].strip()
                break
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'strategy': self.name
        }


# ============ BUILT-IN STRATEGIES ============

class WoundedPreyStrategy(BaseStrategy):
    """
    Validated strategy: 68.8% win rate, +37.5% expected value
    
    Quality stocks beaten down 20-50% due to:
    - Sector rotation (not company-specific)
    - Tax loss selling
    - Market overreaction
    """
    
    def __init__(self):
        super().__init__(
            name="Wounded Prey",
            description="""
            Quality stock beaten down 20-50% from 52-week high.
            Not due to fundamental deterioration.
            Has upcoming catalyst to unlock value.
            Insider buying is bonus signal.
            Validated 68.8% win rate.
            """
        )
    
    def applies_to(self, setup_data: Dict) -> bool:
        """Check if stock is wounded prey"""
        drawdown = setup_data.get('drawdown_from_high', 0)
        return 0.20 <= drawdown <= 0.50
    
    def analyze(self, ticker: str, data: Dict) -> Dict:
        """Analyze wounded prey setup"""
        score = 0
        reasons = []
        
        # Check drawdown
        price = data.get('current_price', 0)
        high_52w = data.get('high_52w', price)
        
        if high_52w > 0:
            drawdown = (high_52w - price) / high_52w
            
            if 0.20 <= drawdown <= 0.50:
                score += 30
                reasons.append(f"Wounded {drawdown:.0%} from highs")
            elif drawdown > 0.50:
                return {'signal': 'PASS', 'confidence': 0, 
                        'reason': 'Too wounded (>50% down) - possible trap'}
        
        # Check market cap (quality filter)
        market_cap = data.get('market_cap', 0)
        if market_cap >= 100_000_000:  # $100M+
            score += 10
            reasons.append("Quality market cap")
        
        # Check catalyst
        if data.get('catalyst'):
            score += 30
            reasons.append(f"Catalyst: {data.get('catalyst')}")
        
        # Check insider buying
        if data.get('insider_buying'):
            score += 20
            reasons.append("Insider buying detected")
        
        # Check chart health
        if data.get('chart_health') == 'HEALTHY':
            score += 10
            reasons.append("Healthy chart pattern")
        
        signal = 'BUY' if score >= 50 else 'PASS'
        
        return {
            'signal': signal,
            'confidence': min(score, 100),
            'reason': ' | '.join(reasons) if reasons else 'Insufficient signals',
            'strategy': self.name
        }


class HeadHunterStrategy(BaseStrategy):
    """
    High-risk, high-reward moonshot hunting
    
    Target: 50-500%+ gains
    Lower win rate but massive payoffs
    """
    
    def __init__(self):
        super().__init__(
            name="Head Hunter",
            description="""
            Low float (<20M shares) + binary catalyst = potential explosion.
            Penny stock range ($0.50 - $10).
            FDA approval, Phase 3 data, or major contract.
            Insider buying is strongest confirmation.
            Target 50-500%+ gains with smaller position size.
            """
        )
    
    def applies_to(self, setup_data: Dict) -> bool:
        """Check if stock is head hunter candidate"""
        float_shares = setup_data.get('float', float('inf'))
        price = setup_data.get('price', 0)
        
        return float_shares < 20_000_000 and 0.50 <= price <= 10.00
    
    def analyze(self, ticker: str, data: Dict) -> Dict:
        """Analyze head hunter setup"""
        score = 0
        reasons = []
        
        # Check float (REQUIRED)
        float_shares = data.get('float', float('inf'))
        if float_shares > 20_000_000:
            return {'signal': 'PASS', 'confidence': 0,
                    'reason': f"Float too high ({float_shares/1e6:.1f}M shares)"}
        
        if float_shares < 10_000_000:
            score += 25
            reasons.append(f"Ultra-low float: {float_shares/1e6:.1f}M")
        else:
            score += 15
            reasons.append(f"Low float: {float_shares/1e6:.1f}M")
        
        # Check price range
        price = data.get('current_price', 0)
        if 0.50 <= price <= 5.00:
            score += 15
            reasons.append(f"Prime price range: ${price:.2f}")
        elif 5.00 < price <= 10.00:
            score += 10
            reasons.append(f"Good price range: ${price:.2f}")
        
        # Check catalyst (CRITICAL)
        catalyst = data.get('catalyst', '')
        catalyst_type = data.get('catalyst_type', '').upper()
        
        if catalyst_type in ['FDA_APPROVAL', 'PHASE3_DATA', 'PDUFA']:
            score += 30
            reasons.append(f"Major catalyst: {catalyst}")
        elif catalyst_type in ['PHASE2_DATA', 'CONTRACT', 'EARNINGS']:
            score += 20
            reasons.append(f"Good catalyst: {catalyst}")
        elif catalyst:
            score += 10
            reasons.append(f"Catalyst: {catalyst}")
        
        # Insider buying (BIG bonus)
        insider_value = data.get('insider_buying_value', 0)
        if insider_value > 100_000:
            score += 25
            reasons.append(f"Heavy insider buying: ${insider_value:,.0f}")
        elif insider_value > 50_000:
            score += 15
            reasons.append(f"Insider buying: ${insider_value:,.0f}")
        
        # Short interest (squeeze potential)
        short_pct = data.get('short_interest_pct', 0)
        if short_pct > 20:
            score += 10
            reasons.append(f"High short interest: {short_pct:.0f}%")
        
        signal = 'BUY' if score >= 50 else 'PASS'
        
        return {
            'signal': signal,
            'confidence': min(score, 100),
            'reason': ' | '.join(reasons) if reasons else 'Insufficient signals',
            'strategy': self.name,
            'position_size': '5-8%'  # Smaller due to higher risk
        }


class SteadyGainerStrategy(BaseStrategy):
    """
    Consistent 5-20% gains strategy
    Higher win rate, smaller moves
    """
    
    def __init__(self):
        super().__init__(
            name="Steady Gainer",
            description="""
            Target 5-20% gains with higher win rate.
            Support bounce plays.
            Breakout confirmation (Day 2 follow-through).
            Sector momentum alignment.
            Larger position size (10-15%) due to lower risk.
            """
        )
    
    def applies_to(self, setup_data: Dict) -> bool:
        """Most stocks can be steady gainer candidates"""
        # Filter out pennies and moonshots
        price = setup_data.get('price', 0)
        return price > 2.00  # Minimum price
    
    def analyze(self, ticker: str, data: Dict) -> Dict:
        """Analyze steady gainer setup"""
        score = 0
        reasons = []
        
        # Check support level
        if data.get('near_support'):
            score += 25
            reasons.append("Near key support level")
        
        # Check chart health
        if data.get('chart_health') == 'HEALTHY':
            score += 20
            reasons.append("IBRX-style healthy pattern")
        
        # Check volume
        rel_volume = data.get('relative_volume', 1.0)
        if rel_volume >= 1.5:
            score += 15
            reasons.append(f"Volume surge: {rel_volume:.1f}x")
        
        # Check sector momentum
        if data.get('sector_hot'):
            score += 15
            reasons.append(f"Hot sector: {data.get('sector')}")
        
        # Check RSI (not overbought)
        rsi = data.get('rsi', 50)
        if 30 <= rsi <= 60:
            score += 10
            reasons.append(f"RSI healthy: {rsi:.0f}")
        elif rsi > 70:
            score -= 10
            reasons.append(f"⚠️ RSI overbought: {rsi:.0f}")
        
        # Above 50-day MA
        if data.get('above_50ma'):
            score += 15
            reasons.append("Above 50-day MA")
        
        signal = 'BUY' if score >= 45 else 'PASS'
        
        return {
            'signal': signal,
            'confidence': min(score, 100),
            'reason': ' | '.join(reasons) if reasons else 'Insufficient signals',
            'strategy': self.name,
            'target_gain': '10-15%',
            'position_size': '10-15%'
        }


class InsiderBuyStrategy(BaseStrategy):
    """
    Follow the smart money
    CEO/Director buying = highest conviction signal
    """
    
    def __init__(self):
        super().__init__(
            name="Insider Buy",
            description="""
            When insiders buy with their own money, PAY ATTENTION.
            CEO/CFO/Director purchases over $50K = high conviction.
            Cluster buying (multiple insiders) = very high conviction.
            Best combined with catalyst timing.
            RGC proved this - CEO buying 81% of float = explosion.
            """
        )
    
    def applies_to(self, setup_data: Dict) -> bool:
        """Check for recent insider buying"""
        return bool(setup_data.get('insider_buying'))
    
    def analyze(self, ticker: str, data: Dict) -> Dict:
        """Analyze insider buying setup"""
        insider_data = data.get('insider_data', {})
        
        if not insider_data and not data.get('insider_buying'):
            return {'signal': 'PASS', 'confidence': 0,
                    'reason': 'No insider buying detected'}
        
        score = 0
        reasons = []
        
        # Check buyer type
        buyer_type = insider_data.get('buyer_type', '').upper()
        if buyer_type in ['CEO', 'CFO', 'PRESIDENT']:
            score += 35
            reasons.append(f"{buyer_type} buying (highest conviction)")
        elif buyer_type in ['DIRECTOR', 'VP']:
            score += 25
            reasons.append(f"{buyer_type} buying")
        else:
            score += 15
            reasons.append("Insider buying detected")
        
        # Check value
        value = insider_data.get('value', 0) or data.get('insider_buying_value', 0)
        if value > 100_000:
            score += 25
            reasons.append(f"Large buy: ${value:,.0f}")
        elif value > 50_000:
            score += 15
            reasons.append(f"Meaningful buy: ${value:,.0f}")
        
        # Check cluster buying
        buy_count = insider_data.get('buy_count', 1)
        if buy_count >= 3:
            score += 25
            reasons.append(f"Cluster buying: {buy_count} insiders")
        elif buy_count >= 2:
            score += 15
            reasons.append(f"Multiple insiders: {buy_count}")
        
        # Check % of float
        pct_float = insider_data.get('pct_of_float', 0)
        if pct_float > 5:
            score += 20
            reasons.append(f"Buying {pct_float:.1f}% of float!")
        
        signal = 'BUY' if score >= 50 else 'PASS'
        
        return {
            'signal': signal,
            'confidence': min(score, 100),
            'reason': ' | '.join(reasons) if reasons else 'Weak insider signal',
            'strategy': self.name
        }


# ============ STRATEGY MANAGER ============

class StrategyPluginManager:
    """
    Manages trading strategies as plugins
    New strategies can be added anytime without code changes
    """
    
    def __init__(self, brain=None):
        """
        Initialize with optional brain connection for NL strategies
        """
        self.brain = brain
        self.strategies: Dict[str, BaseStrategy] = {}
        self.strategy_performance: Dict[str, Dict] = {}
        
        # Load core strategies
        self._load_core_strategies()
    
    def _load_core_strategies(self):
        """Load Wolf Pack's proven strategies"""
        self.add_strategy(WoundedPreyStrategy())
        self.add_strategy(HeadHunterStrategy())
        self.add_strategy(SteadyGainerStrategy())
        self.add_strategy(InsiderBuyStrategy())
        
        print(f"📦 Loaded {len(self.strategies)} core strategies")
    
    def add_strategy(self, strategy: BaseStrategy):
        """Add a strategy to the brain"""
        self.strategies[strategy.name] = strategy
        self.strategy_performance[strategy.name] = strategy.performance
        print(f"   + {strategy.name}")
    
    def add_strategy_from_description(self, name: str, description: str) -> BaseStrategy:
        """
        Add a new strategy by describing it in plain English
        """
        if not self.brain:
            print("⚠️  No brain connected - strategy will use basic matching")
        
        strategy = NaturalLanguageStrategy(name, description, self.brain)
        self.add_strategy(strategy)
        return strategy
    
    def teach_by_example(self, name: str, examples: List[Dict], 
                        description: str = "") -> BaseStrategy:
        """
        Teach a strategy by showing winning trade examples
        
        Args:
            name: Strategy name
            examples: List of example trades
            description: Optional additional description
        """
        # Build description from examples
        example_text = ""
        for ex in examples:
            example_text += f"\n- {ex.get('ticker', '?')}: {ex.get('outcome', '?')}"
            if ex.get('why_good'):
                example_text += f" ({ex['why_good']})"
        
        full_description = f"""
LEARNED FROM EXAMPLES:
{example_text}

{description}

Look for setups that share these characteristics.
"""
        return self.add_strategy_from_description(name, full_description)
    
    def get_applicable_strategies(self, setup_data: Dict) -> List[Dict]:
        """
        Find all strategies that apply to this setup
        """
        applicable = []
        
        for name, strategy in self.strategies.items():
            try:
                if strategy.applies_to(setup_data):
                    applicable.append({
                        'name': name,
                        'description': strategy.description,
                        'performance': self.strategy_performance.get(name, {})
                    })
            except Exception as e:
                print(f"⚠️  Error checking {name}: {e}")
        
        return applicable
    
    def analyze_with_all(self, ticker: str, data: Dict) -> Dict[str, Dict]:
        """
        Run ALL strategies on a ticker
        """
        results = {}
        
        for name, strategy in self.strategies.items():
            try:
                result = strategy.analyze(ticker, data)
                results[name] = result
            except Exception as e:
                results[name] = {
                    'signal': 'ERROR',
                    'confidence': 0,
                    'reason': str(e)
                }
        
        return results
    
    def get_best_strategy_for_setup(self, ticker: str, data: Dict) -> Optional[Dict]:
        """
        Find the best strategy for a setup based on:
        1. Strategy applies to setup
        2. Historical performance of strategy
        3. Current signal strength
        """
        results = self.analyze_with_all(ticker, data)
        
        best = None
        best_score = 0
        
        for name, result in results.items():
            if result['signal'] != 'BUY':
                continue
            
            # Score = confidence * performance multiplier
            perf = self.strategy_performance.get(name, {})
            win_rate = perf.get('wins', 0) / max(perf.get('trades', 1), 1)
            
            # Boost for proven strategies
            if perf.get('trades', 0) >= 10 and win_rate >= 0.6:
                multiplier = 1.5
            elif perf.get('trades', 0) >= 5 and win_rate >= 0.5:
                multiplier = 1.2
            else:
                multiplier = 1.0
            
            score = result['confidence'] * multiplier
            
            if score > best_score:
                best_score = score
                best = {
                    'strategy': name,
                    'analysis': result,
                    'adjusted_confidence': int(score)
                }
        
        return best
    
    def update_strategy_performance(self, strategy_name: str, trade_result: Dict):
        """Update performance metrics for a strategy"""
        if strategy_name in self.strategies:
            self.strategies[strategy_name].update_performance(trade_result)
            self.strategy_performance[strategy_name] = self.strategies[strategy_name].performance
    
    def get_performance_report(self) -> str:
        """Get formatted performance report for all strategies"""
        report = "\n📊 STRATEGY PERFORMANCE REPORT\n" + "="*50 + "\n"
        
        for name, strategy in self.strategies.items():
            perf = strategy.performance
            trades = perf['trades']
            
            if trades == 0:
                report += f"\n{name}: No trades yet\n"
                continue
            
            win_rate = perf['wins'] / trades * 100
            avg_return = perf['total_return'] / trades * 100
            
            report += f"\n{name}:\n"
            report += f"  Trades: {trades}\n"
            report += f"  Win Rate: {win_rate:.1f}%\n"
            report += f"  Avg Return: {avg_return:+.1f}%\n"
            report += f"  Best: {perf['best_trade']*100:+.1f}%\n"
            report += f"  Worst: {perf['worst_trade']*100:+.1f}%\n"
        
        return report


# ============ TESTING ============

def test_strategies():
    """Test the strategy plugin system"""
    print("\n" + "="*80)
    print("🔌 TESTING STRATEGY PLUGIN SYSTEM")
    print("="*80)
    
    # Create manager without brain (offline mode)
    manager = StrategyPluginManager(brain=None)
    
    # Test setup data
    test_data = {
        'ticker': 'GLSI',
        'current_price': 24.88,
        'high_52w': 32.91,
        'float': 6_570_000,
        'market_cap': 150_000_000,
        'catalyst': 'Phase 3 breast cancer vaccine data',
        'catalyst_type': 'PHASE3_DATA',
        'insider_buying': True,
        'insider_buying_value': 340_000,
        'insider_data': {
            'buyer_type': 'CEO',
            'value': 340_000,
            'buy_count': 5
        },
        'chart_health': 'HEALTHY',
        'short_interest_pct': 24.33,
        'drawdown_from_high': 0.24
    }
    
    print("\n📝 Test Data: GLSI")
    print(f"   Price: ${test_data['current_price']}")
    print(f"   Float: {test_data['float']/1e6:.1f}M")
    print(f"   Insider Buying: ${test_data['insider_buying_value']:,}")
    
    # Find applicable strategies
    print("\n🔍 Finding applicable strategies...")
    applicable = manager.get_applicable_strategies(test_data)
    print(f"   Found {len(applicable)} applicable strategies")
    
    for strat in applicable:
        print(f"   - {strat['name']}")
    
    # Analyze with all strategies
    print("\n📊 Running all strategies...")
    results = manager.analyze_with_all('GLSI', test_data)
    
    for name, result in results.items():
        signal = result['signal']
        conf = result['confidence']
        icon = '✅' if signal == 'BUY' else '⬜'
        print(f"   {icon} {name}: {signal} ({conf}/100)")
        if signal == 'BUY':
            print(f"      → {result['reason'][:60]}...")
    
    # Get best strategy
    print("\n🏆 Best strategy for this setup:")
    best = manager.get_best_strategy_for_setup('GLSI', test_data)
    if best:
        print(f"   Strategy: {best['strategy']}")
        print(f"   Confidence: {best['adjusted_confidence']}/100")
    
    # Add custom strategy
    print("\n➕ Adding custom strategy...")
    manager.add_strategy_from_description(
        name="Trump Defense Play",
        description="""
        Defense stocks that benefit from Trump administration:
        - Military budget increases
        - Space Force expansion
        - Border security contracts
        Look for: KTOS, RKLB, LUNR type companies
        """
    )
    
    print("\n✅ Strategy plugin tests complete!")
    print(manager.get_performance_report())


if __name__ == "__main__":
    test_strategies()
