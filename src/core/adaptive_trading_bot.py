"""
ADAPTIVE TRADING BOT - LEARNS YOUR STYLE, IMPROVES OVER TIME
Built: January 20, 2026

Evolution Path:
Phase 1 (NOW): Bot shows you signals, you choose, it learns
Phase 2 (30+ trades): Bot suggests trades with confidence scores
Phase 3 (60+ trades): Bot can auto-execute high-confidence signals
Phase 4 (100+ trades): Bot fully adapted to YOUR style, minimal supervision

Current Mode: LEARNING MODE
- Bot shows ALL strategy signals
- YOU choose which to take
- Bot tracks your choices + outcomes
- Bot learns your preferences

Philosophy:
"The bot doesn't replace you. It becomes YOU."

What makes this different from generic bots:
- Learns YOUR risk tolerance (not generic)
- Learns YOUR sector preferences (biotech? tech? energy?)
- Learns YOUR exit style (hit targets? early exit? hold forever?)
- Learns YOUR emotional patterns (calm trades vs FOMO trades)
- Adapts weights based on what works for YOU (not what works for others)

The Goal:
Eventually the bot trades exactly like you would - but faster, without emotions,
and with perfect discipline. It becomes your digital twin.
"""

import yfinance as yf
from datetime import datetime
from typing import Dict, List, Tuple
import os
import sys

# Import our systems
sys.path.insert(0, os.path.dirname(__file__))
from multi_strategy_system import (
    SupplyShockStrategy, 
    BreakoutConfirmationStrategy,
    BottomingReversalStrategy
)
from trade_learning_engine import TradeLearningEngine
from flat_to_boom_detector import FlatToBoomDetector, analyze_ticker_comprehensive
from convergence_engine_v2 import ConvergenceEngine


class AdaptiveTradingBot:
    """
    The brain that combines all strategies + learns your style
    """
    
    def __init__(self, mode: str = "LEARNING"):
        """
        Initialize bot
        
        Args:
            mode: "LEARNING" | "ASSISTED" | "AUTONOMOUS"
                LEARNING: Shows signals, you choose, it learns
                ASSISTED: Suggests trades, you approve/reject
                AUTONOMOUS: Auto-executes high-confidence signals (needs 100+ trades)
        """
        self.mode = mode
        
        # Initialize all strategy engines
        self.strategies = {
            'SUPPLY_SHOCK': SupplyShockStrategy(),
            'BREAKOUT_CONFIRMATION': BreakoutConfirmationStrategy(),
            'BOTTOMING_REVERSAL': BottomingReversalStrategy(),
            'FLAT_TO_BOOM': FlatToBoomDetector(),
        }
        
        # Convergence engine (original 70-point system)
        self.convergence = ConvergenceEngine()
        
        # Learning engine
        self.learner = TradeLearningEngine()
        
        print(f"🐺 ADAPTIVE BOT INITIALIZED")
        print(f"   Mode: {self.mode}")
        print(f"   Strategies Loaded: {len(self.strategies)}")
        print(f"   Historical Trades: {len(self.learner.trades)}")
    
    def analyze_ticker(self, ticker: str, show_details: bool = True) -> Dict:
        """
        Run ALL strategies on a ticker and combine results
        
        Returns:
            {
                'ticker': str,
                'recommendation': 'BUY' | 'PASS',
                'confidence': 0-100,
                'reason': str,
                'strategy_signals': {...},
                'learned_insight': str,
                'entry_price': float,
                'stop_loss': float,
                'targets': [float, float, float]
            }
        """
        if show_details:
            print(f"\n{'='*80}")
            print(f"🔍 ANALYZING: ${ticker}")
            print(f"{'='*80}")
        
        # Get basic data for all strategies
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            current_price = info.get('currentPrice', 0)
            
            if current_price == 0:
                hist = stock.history(period="1d")
                current_price = hist['Close'].iloc[-1] if not hist.empty else 0
            
        except Exception as e:
            return {
                'ticker': ticker,
                'recommendation': 'PASS',
                'confidence': 0,
                'reason': f'Error fetching data: {str(e)}',
                'strategy_signals': {},
                'learned_insight': '',
                'entry_price': 0,
                'stop_loss': 0,
                'targets': [0, 0, 0]
            }
        
        # Build data package for strategies
        data = {
            'insider_buys': [],  # Would come from BR0KKR service
            'catalysts': [],  # Would come from catalyst service
            'current_price': current_price
        }
        
        # Run each strategy
        strategy_signals = {}
        
        # 1. Supply Shock
        try:
            supply_signal = self.strategies['SUPPLY_SHOCK'].analyze(ticker, data)
            strategy_signals['SUPPLY_SHOCK'] = supply_signal
            if show_details and supply_signal['signal'] == 'BUY':
                print(f"\n💥 SUPPLY SHOCK: {supply_signal['reason']}")
                print(f"   Confidence: {supply_signal['confidence']}/100")
        except Exception as e:
            strategy_signals['SUPPLY_SHOCK'] = {'signal': 'PASS', 'confidence': 0, 'reason': str(e)}
        
        # 2. Breakout Confirmation
        try:
            breakout_signal = self.strategies['BREAKOUT_CONFIRMATION'].analyze(ticker, data)
            strategy_signals['BREAKOUT_CONFIRMATION'] = breakout_signal
            if show_details and breakout_signal['signal'] == 'BUY':
                print(f"\n🚀 BREAKOUT: {breakout_signal['reason']}")
                print(f"   Confidence: {breakout_signal['confidence']}/100")
        except Exception as e:
            strategy_signals['BREAKOUT_CONFIRMATION'] = {'signal': 'PASS', 'confidence': 0, 'reason': str(e)}
        
        # 3. Bottoming Reversal
        try:
            bottom_signal = self.strategies['BOTTOMING_REVERSAL'].analyze(ticker, data)
            strategy_signals['BOTTOMING_REVERSAL'] = bottom_signal
            if show_details and bottom_signal['signal'] == 'BUY':
                print(f"\n🔄 BOTTOMING: {bottom_signal['reason']}")
                print(f"   Confidence: {bottom_signal['confidence']}/100")
        except Exception as e:
            strategy_signals['BOTTOMING_REVERSAL'] = {'signal': 'PASS', 'confidence': 0, 'reason': str(e)}
        
        # 4. Flat-to-Boom
        try:
            ftb_result = analyze_ticker_comprehensive(ticker, data['insider_buys'], data['catalysts'])
            ftb_signal = {
                'signal': 'BUY' if ftb_result.get('is_catching') else 'PASS',
                'confidence': ftb_result.get('flat_to_boom_score', 0),
                'reason': ftb_result.get('verdict', 'No pattern'),
                'entry_price': current_price,
                'stop_loss': current_price * 0.85,
                'targets': [current_price * 1.25, current_price * 1.5, current_price * 2.0],
                'strategy_specific': ftb_result
            }
            strategy_signals['FLAT_TO_BOOM'] = ftb_signal
            if show_details and ftb_signal['signal'] == 'BUY':
                print(f"\n⚡ FLAT-TO-BOOM: {ftb_signal['reason']}")
                print(f"   Confidence: {ftb_signal['confidence']}/100")
        except Exception as e:
            strategy_signals['FLAT_TO_BOOM'] = {'signal': 'PASS', 'confidence': 0, 'reason': str(e)}
        
        # 5. Convergence Scoring (original 70-point system)
        try:
            convergence_result = self.convergence.score_ticker(ticker)
            conv_signal = {
                'signal': 'BUY' if convergence_result.get('total_score', 0) >= 40 else 'PASS',
                'confidence': convergence_result.get('total_score', 0),
                'reason': f"{convergence_result.get('total_score', 0)}/70 points",
                'entry_price': current_price,
                'stop_loss': current_price * 0.85,
                'targets': [current_price * 1.3, current_price * 1.6, current_price * 2.0],
                'strategy_specific': convergence_result
            }
            strategy_signals['CONVERGENCE_SCORING'] = conv_signal
            if show_details and conv_signal['signal'] == 'BUY':
                print(f"\n📊 CONVERGENCE: {conv_signal['reason']}")
                print(f"   Confidence: {conv_signal['confidence']}/70")
        except Exception as e:
            strategy_signals['CONVERGENCE_SCORING'] = {'signal': 'PASS', 'confidence': 0, 'reason': str(e)}
        
        # Combine signals using learned weights
        recommendation = self.learner.get_strategy_recommendation(ticker, strategy_signals)
        
        # Get best targets from highest confidence strategy
        best_strategy = recommendation['top_strategies'][0] if recommendation['top_strategies'] else None
        
        if best_strategy:
            best_signal = strategy_signals[best_strategy[0]]
            entry = best_signal.get('entry_price', current_price)
            stop = best_signal.get('stop_loss', current_price * 0.85)
            targets = best_signal.get('targets', [current_price * 1.3, current_price * 1.6, current_price * 2.0])
        else:
            entry = current_price
            stop = current_price * 0.85
            targets = [0, 0, 0]
        
        result = {
            'ticker': ticker,
            'recommendation': recommendation['recommendation'],
            'confidence': recommendation['confidence'],
            'reason': recommendation['reason'],
            'strategy_signals': strategy_signals,
            'learned_insight': recommendation['learned_insight'],
            'entry_price': entry,
            'stop_loss': stop,
            'targets': targets,
            'top_strategies': recommendation['top_strategies']
        }
        
        if show_details:
            print(f"\n{'='*80}")
            print(f"🎯 FINAL RECOMMENDATION: {result['recommendation']}")
            print(f"   Overall Confidence: {result['confidence']:.0f}/100")
            print(f"   Reason: {result['reason']}")
            
            if result['learned_insight']:
                print(f"\n💡 {result['learned_insight']}")
            
            if result['recommendation'] == 'BUY':
                print(f"\n📍 ENTRY: ${entry:.2f}")
                print(f"🛑 STOP: ${stop:.2f} (-{((entry-stop)/entry)*100:.1f}%)")
                print(f"🎯 TARGETS:")
                print(f"   T1: ${targets[0]:.2f} (+{((targets[0]-entry)/entry)*100:.1f}%)")
                print(f"   T2: ${targets[1]:.2f} (+{((targets[1]-entry)/entry)*100:.1f}%)")
                print(f"   T3: ${targets[2]:.2f} (+{((targets[2]-entry)/entry)*100:.1f}%)")
            
            print(f"{'='*80}\n")
        
        return result
    
    def scan_watchlist(self, tickers: List[str]) -> List[Dict]:
        """
        Scan multiple tickers and return all BUY signals
        """
        print(f"\n🔍 SCANNING {len(tickers)} TICKERS...")
        print(f"Mode: {self.mode}")
        print(f"Strategies: {', '.join(self.strategies.keys())}")
        print()
        
        buy_signals = []
        
        for ticker in tickers:
            result = self.analyze_ticker(ticker, show_details=False)
            
            if result['recommendation'] == 'BUY':
                buy_signals.append(result)
                print(f"✅ {ticker}: {result['confidence']:.0f}/100 - {result['reason'][:60]}")
            else:
                print(f"⏭️  {ticker}: PASS")
        
        print(f"\n🎯 FOUND {len(buy_signals)} BUY SIGNALS")
        return buy_signals
    
    def teach_from_trade(self, ticker: str, strategy: str, took_trade: bool,
                        your_confidence: int = 0, why_or_why_not: str = ""):
        """
        Record your decision to take or pass a trade
        Bot learns from this
        
        Args:
            ticker: Stock symbol
            strategy: Which strategy triggered it
            took_trade: True if you entered, False if you passed
            your_confidence: Your gut feel (1-10) if you took it
            why_or_why_not: Your reasoning
        """
        if took_trade:
            print(f"\n📝 LEARNING: You TOOK {strategy} signal on {ticker}")
            print(f"   Your confidence: {your_confidence}/10")
            print(f"   Your reasoning: {why_or_why_not}")
            
            # This would integrate with actual order execution
            # For now, just log the decision
            
        else:
            print(f"\n📝 LEARNING: You PASSED {strategy} signal on {ticker}")
            print(f"   Your reasoning: {why_or_why_not}")
            
            # Bot learns: "Tyr passes SupplyShock when float > 2M"
            # Over time, bot stops showing you those signals
    
    def get_learning_report(self):
        """Show what the bot has learned about you"""
        return self.learner.get_performance_report()
    
    def autonomous_mode_ready(self) -> Tuple[bool, str]:
        """
        Check if bot has learned enough to trade autonomously
        
        Returns:
            (ready: bool, reason: str)
        """
        closed_trades = len([t for t in self.learner.trades if t.status == "CLOSED"])
        
        if closed_trades < 30:
            return False, f"Need 30+ closed trades (have {closed_trades})"
        
        # Check if any strategy has positive expectancy
        strategy_stats = self.learner.insights.get('strategy_performance', {})
        
        positive_strategies = [
            name for name, stats in strategy_stats.items()
            if stats.get('expectancy', 0) > 5  # >5% expectancy
            and stats.get('total_trades', 0) >= 10  # Minimum sample
        ]
        
        if not positive_strategies:
            return False, "No strategy with proven positive expectancy yet"
        
        return True, f"Ready! {len(positive_strategies)} strategies validated with positive expectancy"


def interactive_session():
    """
    Interactive session for teaching the bot
    """
    print("\n" + "="*80)
    print("🐺 ADAPTIVE BOT - LEARNING SESSION")
    print("="*80)
    print()
    print("This session will:")
    print("1. Show you signals from ALL strategies")
    print("2. Let you choose which to take")
    print("3. Learn from your choices")
    print("4. Improve recommendations over time")
    print()
    print("Eventually, the bot will trade EXACTLY like you would.")
    print("="*80)
    print()
    
    bot = AdaptiveTradingBot(mode="LEARNING")
    
    # Example tickers
    watchlist = ['GLSI', 'BTAI', 'PMCB', 'COSM', 'ONCY']
    
    print(f"Let's analyze your watchlist: {', '.join(watchlist)}")
    print()
    
    signals = bot.scan_watchlist(watchlist)
    
    if signals:
        print("\n" + "="*80)
        print("📊 DETAILED ANALYSIS OF BUY SIGNALS:")
        print("="*80)
        
        for signal in signals:
            bot.analyze_ticker(signal['ticker'], show_details=True)
    
    # Show learning status
    print("\n" + "="*80)
    print("🧠 CURRENT LEARNING STATUS:")
    print("="*80)
    print(bot.get_learning_report())


if __name__ == "__main__":
    interactive_session()
