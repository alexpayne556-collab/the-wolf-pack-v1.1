"""
TRADE LEARNING ENGINE - ADAPTIVE BOT SYSTEM
Built: January 20, 2026

Philosophy:
- Bot learns YOUR trading style (not generic patterns)
- Tracks: which strategies you follow, which you ignore
- Measures: which strategies ACTUALLY make money for YOU
- Adapts: adjusts strategy weights based on YOUR results
- Improves: gets better over time as you teach it

How It Works:
1. System shows you signals from ALL strategies
2. You choose which ones to take (teach by example)
3. Bot tracks your choices + outcomes
4. Bot learns your preferences + what works
5. Bot adjusts weights to match YOUR style
6. Eventually bot can suggest trades that fit YOUR approach

Data Tracked Per Trade:
- Which strategy triggered it
- Your confidence at entry (scale 1-10)
- Entry/exit prices
- P&L outcome
- Why you took it (thesis)
- What you learned (post-trade notes)

Learning Dimensions:
- Strategy success rate (per strategy, per ticker type)
- Your selection patterns (which signals you take)
- Entry timing preferences (immediate vs wait)
- Position sizing patterns
- Exit discipline (hit targets? stops? early exit?)
- Emotional state impact (calm vs tilting trades)

Output:
- "This strategy has 72% win rate for you (8 wins, 3 losses)"
- "You typically take SupplyShock signals when confidence >80"
- "Your best trades come from BottomingReversal + biotech"
- "You tend to exit too early on BreakoutConfirmation (miss target 2)"
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics


@dataclass
class Trade:
    """Single trade record"""
    id: str  # Unique ID
    ticker: str
    strategy: str  # Which strategy triggered it
    entry_date: str  # ISO format
    entry_price: float
    shares: int
    your_confidence: int  # 1-10 scale (your gut feel at entry)
    strategy_confidence: int  # 0-100 (what strategy scored)
    thesis: str  # Why you took it
    
    # Exit data (filled when closed)
    exit_date: Optional[str] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None  # "Target 1", "Stop Loss", "Early Exit", etc.
    pnl_dollars: Optional[float] = None
    pnl_percent: Optional[float] = None
    
    # Learning data
    learned: Optional[str] = None  # Post-trade reflection
    emotional_state: Optional[str] = None  # "CALM", "ANXIOUS", "FOMO", etc.
    market_regime: Optional[str] = None  # "GRIND", "CHOP", "EXPLOSIVE", etc.
    
    # Metadata
    status: str = "OPEN"  # "OPEN", "CLOSED", "STOPPED"


class TradeLearningEngine:
    """
    Learns from YOUR trades to improve bot recommendations
    """
    
    def __init__(self, data_dir: str = "data/learning"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.trades_file = self.data_dir / "trades.json"
        self.insights_file = self.data_dir / "learned_insights.json"
        self.weights_file = self.data_dir / "strategy_weights.json"
        
        self.trades = self._load_trades()
        self.insights = self._load_insights()
        self.strategy_weights = self._load_weights()
    
    def _load_trades(self) -> List[Trade]:
        """Load trade history"""
        if self.trades_file.exists():
            with open(self.trades_file, 'r') as f:
                data = json.load(f)
                return [Trade(**t) for t in data]
        return []
    
    def _save_trades(self):
        """Save trade history"""
        with open(self.trades_file, 'w') as f:
            json.dump([asdict(t) for t in self.trades], f, indent=2)
    
    def _load_insights(self) -> Dict:
        """Load learned insights"""
        if self.insights_file.exists():
            with open(self.insights_file, 'r') as f:
                return json.load(f)
        return {
            'strategy_performance': {},
            'your_preferences': {},
            'learned_rules': [],
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_insights(self):
        """Save learned insights"""
        with open(self.insights_file, 'w') as f:
            json.dump(self.insights, f, indent=2)
    
    def _load_weights(self) -> Dict[str, float]:
        """Load current strategy weights"""
        if self.weights_file.exists():
            with open(self.weights_file, 'r') as f:
                return json.load(f)
        
        # Default weights (start equal)
        return {
            'FLAT_TO_BOOM': 1.0,
            'SUPPLY_SHOCK': 1.0,
            'BREAKOUT_CONFIRMATION': 1.0,
            'BOTTOMING_REVERSAL': 1.0,
            'CONVERGENCE_SCORING': 1.0
        }
    
    def _save_weights(self):
        """Save strategy weights"""
        with open(self.weights_file, 'w') as f:
            json.dump(self.strategy_weights, f, indent=2)
    
    def log_trade_entry(self, ticker: str, strategy: str, entry_price: float,
                       shares: int, your_confidence: int, strategy_confidence: int,
                       thesis: str, emotional_state: str = "CALM") -> str:
        """
        Log a new trade entry
        Returns trade ID
        """
        trade_id = f"{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        trade = Trade(
            id=trade_id,
            ticker=ticker,
            strategy=strategy,
            entry_date=datetime.now().isoformat(),
            entry_price=entry_price,
            shares=shares,
            your_confidence=your_confidence,
            strategy_confidence=strategy_confidence,
            thesis=thesis,
            emotional_state=emotional_state,
            status="OPEN"
        )
        
        self.trades.append(trade)
        self._save_trades()
        
        print(f"✅ Trade logged: {trade_id}")
        return trade_id
    
    def log_trade_exit(self, trade_id: str, exit_price: float, 
                      exit_reason: str, learned: str = ""):
        """Log trade exit and calculate P&L"""
        trade = next((t for t in self.trades if t.id == trade_id), None)
        
        if not trade:
            print(f"❌ Trade {trade_id} not found")
            return
        
        trade.exit_date = datetime.now().isoformat()
        trade.exit_price = exit_price
        trade.exit_reason = exit_reason
        trade.pnl_dollars = (exit_price - trade.entry_price) * trade.shares
        trade.pnl_percent = ((exit_price - trade.entry_price) / trade.entry_price) * 100
        trade.learned = learned
        trade.status = "CLOSED"
        
        self._save_trades()
        
        # Trigger learning update
        self._update_learning()
        
        print(f"✅ Trade closed: {trade_id}")
        print(f"   P&L: ${trade.pnl_dollars:.2f} ({trade.pnl_percent:+.1f}%)")
    
    def _update_learning(self):
        """
        Analyze all closed trades and update insights
        This is where the REAL learning happens
        """
        closed_trades = [t for t in self.trades if t.status == "CLOSED"]
        
        if len(closed_trades) < 5:
            return  # Need minimum sample size
        
        # 1. Calculate per-strategy performance
        strategy_stats = {}
        for strategy in self.strategy_weights.keys():
            strategy_trades = [t for t in closed_trades if t.strategy == strategy]
            
            if len(strategy_trades) > 0:
                wins = [t for t in strategy_trades if t.pnl_percent > 0]
                losses = [t for t in strategy_trades if t.pnl_percent <= 0]
                
                win_rate = len(wins) / len(strategy_trades) * 100
                avg_win = statistics.mean([t.pnl_percent for t in wins]) if wins else 0
                avg_loss = statistics.mean([t.pnl_percent for t in losses]) if losses else 0
                expectancy = (win_rate/100 * avg_win) + ((100-win_rate)/100 * avg_loss)
                
                strategy_stats[strategy] = {
                    'total_trades': len(strategy_trades),
                    'wins': len(wins),
                    'losses': len(losses),
                    'win_rate': win_rate,
                    'avg_win': avg_win,
                    'avg_loss': avg_loss,
                    'expectancy': expectancy
                }
        
        self.insights['strategy_performance'] = strategy_stats
        
        # 2. Learn YOUR selection patterns
        # Which strategies do you ACTUALLY take vs ignore?
        # (This would require tracking signals shown vs taken - future enhancement)
        
        # 3. Adjust strategy weights based on YOUR results
        for strategy, stats in strategy_stats.items():
            if stats['total_trades'] >= 5:  # Need minimum sample
                # Weight based on expectancy and win rate
                base_weight = 1.0
                
                # Increase weight if positive expectancy
                if stats['expectancy'] > 5:
                    base_weight += 0.5
                elif stats['expectancy'] > 10:
                    base_weight += 1.0
                
                # Increase weight if high win rate
                if stats['win_rate'] > 70:
                    base_weight += 0.5
                
                # Decrease weight if negative expectancy
                if stats['expectancy'] < 0:
                    base_weight = max(0.3, base_weight - 0.5)
                
                self.strategy_weights[strategy] = base_weight
        
        # 4. Extract learned rules
        self._extract_rules(closed_trades)
        
        # Save everything
        self.insights['last_updated'] = datetime.now().isoformat()
        self._save_insights()
        self._save_weights()
        
        print("🧠 Learning updated with latest trade data")
    
    def _extract_rules(self, closed_trades: List[Trade]):
        """
        Extract specific rules from trade patterns
        Example: "Exit biotech at +25% (you typically give back gains past that)"
        """
        rules = []
        
        # Rule: Early exit pattern
        early_exits = [t for t in closed_trades if t.exit_reason == "Early Exit"]
        if len(early_exits) > 3:
            avg_exit = statistics.mean([t.pnl_percent for t in early_exits if t.pnl_percent])
            rules.append({
                'rule': 'EARLY_EXIT_TENDENCY',
                'description': f'You tend to exit early around +{avg_exit:.1f}%',
                'recommendation': 'Consider setting profit targets higher',
                'sample_size': len(early_exits)
            })
        
        # Rule: Stop loss discipline
        stopped = [t for t in closed_trades if "Stop" in t.exit_reason]
        if len(closed_trades) > 10:
            stop_rate = len(stopped) / len(closed_trades) * 100
            if stop_rate < 20:
                rules.append({
                    'rule': 'WEAK_STOP_DISCIPLINE',
                    'description': f'Only {stop_rate:.0f}% of trades hit stops (holding losers)',
                    'recommendation': 'Improve stop-loss discipline',
                    'sample_size': len(closed_trades)
                })
        
        # Rule: Emotional state impact
        calm_trades = [t for t in closed_trades if t.emotional_state == "CALM"]
        fomo_trades = [t for t in closed_trades if t.emotional_state in ["FOMO", "ANXIOUS"]]
        
        if len(calm_trades) >= 3 and len(fomo_trades) >= 3:
            calm_win_rate = len([t for t in calm_trades if t.pnl_percent > 0]) / len(calm_trades) * 100
            fomo_win_rate = len([t for t in fomo_trades if t.pnl_percent > 0]) / len(fomo_trades) * 100
            
            if calm_win_rate > fomo_win_rate + 20:
                rules.append({
                    'rule': 'EMOTIONAL_STATE_IMPACT',
                    'description': f'CALM trades: {calm_win_rate:.0f}% win rate, FOMO trades: {fomo_win_rate:.0f}%',
                    'recommendation': 'Only trade when emotional state = CALM',
                    'sample_size': len(calm_trades) + len(fomo_trades)
                })
        
        self.insights['learned_rules'] = rules
    
    def get_strategy_recommendation(self, ticker: str, signals: Dict[str, Dict]) -> Dict:
        """
        Combine all strategy signals with learned weights
        Returns recommendation tailored to YOUR style
        
        Args:
            ticker: Stock symbol
            signals: Dict of {strategy_name: signal_dict}
            
        Returns:
            {
                'recommendation': 'BUY' | 'PASS',
                'confidence': 0-100,
                'reason': str,
                'top_strategies': [(strategy, confidence, weight), ...],
                'learned_insight': str
            }
        """
        weighted_scores = []
        
        for strategy_name, signal in signals.items():
            if signal['signal'] == 'BUY':
                weight = self.strategy_weights.get(strategy_name, 1.0)
                weighted_confidence = signal['confidence'] * weight
                
                weighted_scores.append({
                    'strategy': strategy_name,
                    'confidence': signal['confidence'],
                    'weight': weight,
                    'weighted_score': weighted_confidence,
                    'reason': signal['reason']
                })
        
        if not weighted_scores:
            return {
                'recommendation': 'PASS',
                'confidence': 0,
                'reason': 'No strategies triggered',
                'top_strategies': [],
                'learned_insight': ''
            }
        
        # Sort by weighted score
        weighted_scores.sort(key=lambda x: x['weighted_score'], reverse=True)
        
        # Calculate overall confidence
        total_weighted = sum(s['weighted_score'] for s in weighted_scores)
        max_possible = 100 * len(weighted_scores)
        overall_confidence = min(100, (total_weighted / max_possible) * 100) if max_possible > 0 else 0
        
        # Get top strategies
        top_3 = weighted_scores[:3]
        
        # Build recommendation
        if overall_confidence >= 70:
            recommendation = 'BUY'
            reason_parts = [f"{s['strategy']}: {s['reason']}" for s in top_3]
            reason = " | ".join(reason_parts)
        else:
            recommendation = 'PASS'
            reason = f"Confidence too low ({overall_confidence:.0f}%)"
        
        # Add learned insight
        insight = self._get_learned_insight_for_ticker(ticker, weighted_scores[0]['strategy'] if weighted_scores else None)
        
        return {
            'recommendation': recommendation,
            'confidence': overall_confidence,
            'reason': reason,
            'top_strategies': [(s['strategy'], s['confidence'], s['weight']) for s in top_3],
            'learned_insight': insight
        }
    
    def _get_learned_insight_for_ticker(self, ticker: str, top_strategy: Optional[str]) -> str:
        """Get relevant learned insight for this ticker/strategy"""
        if not top_strategy:
            return ""
        
        # Check if this strategy has historical performance
        strategy_stats = self.insights['strategy_performance'].get(top_strategy, {})
        
        if strategy_stats:
            win_rate = strategy_stats.get('win_rate', 0)
            total = strategy_stats.get('total_trades', 0)
            
            return f"[LEARNED] {top_strategy} has {win_rate:.0f}% win rate for you ({total} trades)"
        
        return ""
    
    def get_performance_report(self) -> str:
        """Generate human-readable performance report"""
        closed = [t for t in self.trades if t.status == "CLOSED"]
        
        if not closed:
            return "No closed trades yet. Keep trading to build your learning dataset!"
        
        total_trades = len(closed)
        wins = [t for t in closed if t.pnl_percent > 0]
        losses = [t for t in closed if t.pnl_percent <= 0]
        
        win_rate = len(wins) / total_trades * 100
        total_pnl = sum(t.pnl_dollars for t in closed)
        
        report = f"""
🧠 LEARNING ENGINE PERFORMANCE REPORT
{'='*60}

OVERALL STATS:
- Total Trades: {total_trades}
- Wins: {len(wins)} ({win_rate:.1f}%)
- Losses: {len(losses)} ({100-win_rate:.1f}%)
- Total P&L: ${total_pnl:,.2f}

STRATEGY PERFORMANCE:
"""
        
        for strategy, stats in self.insights['strategy_performance'].items():
            report += f"\n{strategy}:"
            report += f"\n  Trades: {stats['total_trades']}"
            report += f"\n  Win Rate: {stats['win_rate']:.1f}%"
            report += f"\n  Avg Win: +{stats['avg_win']:.1f}%"
            report += f"\n  Avg Loss: {stats['avg_loss']:.1f}%"
            report += f"\n  Expectancy: {stats['expectancy']:+.1f}%"
            report += f"\n  Current Weight: {self.strategy_weights.get(strategy, 1.0):.2f}"
        
        report += "\n\nLEARNED RULES:\n"
        for rule in self.insights['learned_rules']:
            report += f"\n⚠️ {rule['rule']}"
            report += f"\n   {rule['description']}"
            report += f"\n   → {rule['recommendation']}"
        
        return report


if __name__ == "__main__":
    # Example usage
    engine = TradeLearningEngine()
    
    # Log sample trade
    trade_id = engine.log_trade_entry(
        ticker="GLSI",
        strategy="FLAT_TO_BOOM",
        entry_price=24.88,
        shares=4,
        your_confidence=8,
        strategy_confidence=85,
        thesis="CEO buying $340K+, Phase 3 catalyst, 24% short",
        emotional_state="CALM"
    )
    
    print(f"\nTrade logged: {trade_id}")
    print("\n(Close this trade later with .log_trade_exit())")
