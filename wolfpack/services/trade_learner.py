#!/usr/bin/env python3
"""
TRADE LEARNER - Self-Learning Exit System
Analyzes all trade outcomes and learns:
- When to cut losers (pattern recognition)
- When to let winners run (don't exit too early)
- What convergence scores actually work
- What patterns lead to blowups

"Cut losers quick, let winners run" - but LEARN what that means from data
"""

import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum
import statistics

class TradeOutcome(Enum):
    WIN = "win"
    LOSS = "loss"
    BREAKEVEN = "breakeven"
    STOPPED_OUT = "stopped_out"  # Hit stop loss
    BLOWN_UP = "blown_up"  # Big loss, didn't cut soon enough
    EARLY_EXIT = "early_exit"  # Cut too soon, would've won

@dataclass
class TradeRecord:
    """Complete record of a trade from entry to exit"""
    ticker: str
    entry_date: str
    entry_price: float
    entry_convergence: int
    entry_signals: List[str]  # Which signals were active
    shares: int
    position_size_pct: float
    
    # Pattern data at entry
    pivotal_point_score: int
    volume_ratio: float
    consolidation_days: int
    
    # Exit data
    exit_date: str
    exit_price: float
    exit_reason: str
    outcome: str  # TradeOutcome
    
    # Performance
    return_pct: float
    return_dollars: float
    days_held: int
    max_drawdown_pct: float  # Worst dip during hold
    
    # Learning metrics
    warning_signs: List[str]  # What went wrong (for losses)
    success_factors: List[str]  # What went right (for wins)

@dataclass
class LearningInsight:
    """Pattern learned from analyzing trades"""
    pattern_type: str
    condition: str
    outcome_if_true: str  # What happens when this pattern appears
    confidence: float  # 0-1, how often this pattern predicts correctly
    sample_size: int
    rule: str  # Actionable rule based on this pattern

class TradeLearner:
    """
    Machine learning system that:
    1. Tracks every trade outcome
    2. Identifies patterns in wins vs losses
    3. Learns adaptive exit rules
    4. Self-corrects when wrong
    """
    
    def __init__(self, db_path: str = "logs/trade_history.json"):
        self.db_path = db_path
        self.trades = self._load_trades()
        self.insights = []
        
    def _load_trades(self) -> List[TradeRecord]:
        """Load all historical trades"""
        if not os.path.exists(self.db_path):
            return []
        
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
                return [TradeRecord(**t) for t in data]
        except Exception as e:
            print(f"⚠️  Error loading trades: {e}")
            return []
    
    def _save_trades(self):
        """Save trade history"""
        os.makedirs("logs", exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump([asdict(t) for t in self.trades], f, indent=2)
    
    def record_trade(self, trade: TradeRecord):
        """Add completed trade to learning database"""
        self.trades.append(trade)
        self._save_trades()
        
        # Immediate learning - analyze this trade
        self._analyze_single_trade(trade)
        
        # Update insights every 10 trades
        if len(self.trades) % 10 == 0:
            self.learn_from_all_trades()
    
    def _analyze_single_trade(self, trade: TradeRecord):
        """Real-time analysis of what just happened"""
        
        if trade.outcome in [TradeOutcome.LOSS.value, TradeOutcome.BLOWN_UP.value]:
            print(f"\n🔍 ANALYZING LOSS: {trade.ticker}")
            
            # What were the warning signs?
            warnings = []
            
            if trade.entry_convergence < 80:
                warnings.append(f"Low convergence at entry ({trade.entry_convergence}/100)")
            
            if trade.volume_ratio < 1.5:
                warnings.append(f"Weak volume confirmation ({trade.volume_ratio:.1f}x)")
            
            if trade.consolidation_days < 14:
                warnings.append(f"Short consolidation ({trade.consolidation_days}d)")
            
            if trade.max_drawdown_pct > 15:
                warnings.append(f"Deep drawdown hit ({trade.max_drawdown_pct:.1f}%)")
            
            if warnings:
                print(f"⚠️  Warning signs that were IGNORED:")
                for w in warnings:
                    print(f"   - {w}")
                
                # Update trade record with learnings
                trade.warning_signs = warnings
                self._save_trades()
        
        elif trade.outcome in [TradeOutcome.WIN.value]:
            print(f"\n✅ ANALYZING WIN: {trade.ticker}")
            
            success_factors = []
            
            if trade.entry_convergence >= 85:
                success_factors.append(f"HIGH convergence ({trade.entry_convergence}/100)")
            
            if trade.volume_ratio >= 2.0:
                success_factors.append(f"Strong volume ({trade.volume_ratio:.1f}x)")
            
            if trade.consolidation_days >= 20:
                success_factors.append(f"Solid base ({trade.consolidation_days}d)")
            
            if len(trade.entry_signals) >= 5:
                success_factors.append(f"Multi-signal convergence ({len(trade.entry_signals)} signals)")
            
            if success_factors:
                print(f"🔥 Success factors:")
                for sf in success_factors:
                    print(f"   - {sf}")
                
                trade.success_factors = success_factors
                self._save_trades()
    
    def learn_from_all_trades(self):
        """Analyze entire trade history and extract patterns"""
        
        if len(self.trades) < 10:
            print("⚠️  Need at least 10 trades to learn patterns")
            return
        
        print(f"\n{'=' * 70}")
        print(f"🧠 LEARNING FROM {len(self.trades)} TRADES")
        print(f"{'=' * 70}")
        
        wins = [t for t in self.trades if t.outcome == TradeOutcome.WIN.value]
        losses = [t for t in self.trades if t.outcome in [TradeOutcome.LOSS.value, TradeOutcome.BLOWN_UP.value]]
        
        win_rate = len(wins) / len(self.trades) * 100 if self.trades else 0
        
        print(f"\n📊 Overall Performance:")
        print(f"   Win Rate: {win_rate:.1f}% ({len(wins)}W / {len(losses)}L)")
        
        if wins:
            avg_win = statistics.mean([t.return_pct for t in wins])
            print(f"   Avg Win: {avg_win:.1f}%")
        
        if losses:
            avg_loss = statistics.mean([t.return_pct for t in losses])
            print(f"   Avg Loss: {avg_loss:.1f}%")
        
        # Learn patterns
        self.insights = []
        
        # Pattern 1: Convergence threshold
        self._learn_convergence_threshold(wins, losses)
        
        # Pattern 2: Volume confirmation importance
        self._learn_volume_patterns(wins, losses)
        
        # Pattern 3: Consolidation time matters
        self._learn_consolidation_patterns(wins, losses)
        
        # Pattern 4: When to cut (drawdown limits)
        self._learn_cut_rules(losses)
        
        # Pattern 5: Signal count effectiveness
        self._learn_signal_count_patterns(wins, losses)
        
        # Save insights
        self._save_insights()
    
    def _learn_convergence_threshold(self, wins: List[TradeRecord], losses: List[TradeRecord]):
        """What convergence score actually works?"""
        
        if not wins or not losses:
            return
        
        win_convergence = statistics.mean([t.entry_convergence for t in wins])
        loss_convergence = statistics.mean([t.entry_convergence for t in losses])
        
        print(f"\n🎯 Convergence Pattern:")
        print(f"   Winners avg: {win_convergence:.0f}/100")
        print(f"   Losers avg: {loss_convergence:.0f}/100")
        
        # Find optimal threshold
        threshold = (win_convergence + loss_convergence) / 2
        
        insight = LearningInsight(
            pattern_type="convergence_threshold",
            condition=f"entry_convergence >= {threshold:.0f}",
            outcome_if_true=f"Higher win probability",
            confidence=0.75,  # Would calculate from data
            sample_size=len(wins) + len(losses),
            rule=f"⚠️  RULE: Only enter trades with convergence >= {threshold:.0f}/100"
        )
        
        self.insights.append(insight)
        print(f"   💡 {insight.rule}")
    
    def _learn_volume_patterns(self, wins: List[TradeRecord], losses: List[TradeRecord]):
        """Does volume confirmation matter?"""
        
        if not wins or not losses:
            return
        
        win_volume = statistics.mean([t.volume_ratio for t in wins])
        loss_volume = statistics.mean([t.volume_ratio for t in losses])
        
        print(f"\n📊 Volume Pattern:")
        print(f"   Winners avg: {win_volume:.1f}x")
        print(f"   Losers avg: {loss_volume:.1f}x")
        
        if win_volume > loss_volume * 1.3:  # 30% higher
            insight = LearningInsight(
                pattern_type="volume_confirmation",
                condition=f"volume_ratio >= {win_volume * 0.8:.1f}",
                outcome_if_true="Higher win probability",
                confidence=0.70,
                sample_size=len(wins) + len(losses),
                rule=f"⚠️  RULE: Avoid trades with volume < {win_volume * 0.8:.1f}x average"
            )
            
            self.insights.append(insight)
            print(f"   💡 {insight.rule}")
    
    def _learn_consolidation_patterns(self, wins: List[TradeRecord], losses: List[TradeRecord]):
        """Does base-building time matter?"""
        
        if not wins or not losses:
            return
        
        win_consol = statistics.mean([t.consolidation_days for t in wins if t.consolidation_days > 0])
        loss_consol = statistics.mean([t.consolidation_days for t in losses if t.consolidation_days > 0])
        
        print(f"\n📦 Consolidation Pattern:")
        print(f"   Winners avg: {win_consol:.0f} days")
        print(f"   Losers avg: {loss_consol:.0f} days")
        
        if win_consol > loss_consol * 1.2:
            insight = LearningInsight(
                pattern_type="consolidation_time",
                condition=f"consolidation_days >= {win_consol * 0.7:.0f}",
                outcome_if_true="Stronger base = higher win rate",
                confidence=0.65,
                sample_size=len(wins) + len(losses),
                rule=f"⚠️  RULE: Prefer setups with {win_consol * 0.7:.0f}+ day consolidation"
            )
            
            self.insights.append(insight)
            print(f"   💡 {insight.rule}")
    
    def _learn_cut_rules(self, losses: List[TradeRecord]):
        """When should we have cut? Learn from losses."""
        
        if not losses:
            return
        
        blown_ups = [t for t in losses if t.outcome == TradeOutcome.BLOWN_UP.value]
        
        if blown_ups:
            avg_max_dd = statistics.mean([t.max_drawdown_pct for t in blown_ups])
            
            print(f"\n✂️  Cut Loss Pattern:")
            print(f"   Blown up trades hit {avg_max_dd:.1f}% drawdown on average")
            
            # Learn the cut point (should've cut at half that drawdown)
            cut_point = avg_max_dd * 0.5
            
            insight = LearningInsight(
                pattern_type="cut_loss",
                condition=f"current_drawdown >= {cut_point:.1f}%",
                outcome_if_true="Trade likely to blow up - CUT NOW",
                confidence=0.80,
                sample_size=len(blown_ups),
                rule=f"🚨 RULE: CUT position if drawdown hits {cut_point:.1f}% (before it blows up)"
            )
            
            self.insights.append(insight)
            print(f"   💡 {insight.rule}")
    
    def _learn_signal_count_patterns(self, wins: List[TradeRecord], losses: List[TradeRecord]):
        """Does more signals = better results?"""
        
        if not wins or not losses:
            return
        
        win_signals = statistics.mean([len(t.entry_signals) for t in wins])
        loss_signals = statistics.mean([len(t.entry_signals) for t in losses])
        
        print(f"\n⚡ Signal Count Pattern:")
        print(f"   Winners avg: {win_signals:.1f} signals")
        print(f"   Losers avg: {loss_signals:.1f} signals")
        
        if win_signals > loss_signals:
            insight = LearningInsight(
                pattern_type="signal_count",
                condition=f"signal_count >= {win_signals:.0f}",
                outcome_if_true="More confirmation = higher win rate",
                confidence=0.70,
                sample_size=len(wins) + len(losses),
                rule=f"⚠️  RULE: Prefer setups with {win_signals:.0f}+ signals aligned"
            )
            
            self.insights.append(insight)
            print(f"   💡 {insight.rule}")
    
    def _save_insights(self):
        """Save learned patterns"""
        insights_file = "logs/learned_patterns.json"
        os.makedirs("logs", exist_ok=True)
        
        with open(insights_file, 'w') as f:
            json.dump([asdict(i) for i in self.insights], f, indent=2)
        
        print(f"\n💾 Saved {len(self.insights)} learned patterns to {insights_file}")
    
    def should_enter(self, convergence: int, volume_ratio: float, 
                    consolidation_days: int, signal_count: int) -> tuple[bool, str]:
        """
        Use learned patterns to decide if we should enter
        Returns (should_enter, reasoning)
        """
        
        if not self.insights:
            return (True, "No learning data yet - taking trade")
        
        warnings = []
        
        for insight in self.insights:
            if insight.pattern_type == "convergence_threshold":
                min_convergence = float(insight.condition.split(">=")[1])
                if convergence < min_convergence:
                    warnings.append(f"Convergence {convergence} < learned threshold {min_convergence:.0f}")
            
            elif insight.pattern_type == "volume_confirmation":
                min_volume = float(insight.condition.split(">=")[1])
                if volume_ratio < min_volume:
                    warnings.append(f"Volume {volume_ratio:.1f}x < learned threshold {min_volume:.1f}x")
            
            elif insight.pattern_type == "consolidation_time":
                min_days = float(insight.condition.split(">=")[1])
                if consolidation_days < min_days and consolidation_days > 0:
                    warnings.append(f"Consolidation {consolidation_days}d < learned threshold {min_days:.0f}d")
            
            elif insight.pattern_type == "signal_count":
                min_signals = float(insight.condition.split(">=")[1])
                if signal_count < min_signals:
                    warnings.append(f"Signal count {signal_count} < learned threshold {min_signals:.0f}")
        
        if warnings:
            reasoning = "❌ LEARNED PATTERNS SAY NO:\n" + "\n".join(f"   - {w}" for w in warnings)
            return (False, reasoning)
        else:
            return (True, "✅ Passes all learned filters")
    
    def should_cut(self, current_drawdown_pct: float, days_held: int) -> tuple[bool, str]:
        """
        Use learned patterns to decide if we should cut NOW
        Returns (should_cut, reasoning)
        """
        
        if not self.insights:
            # Default rule: Cut at -10%
            if current_drawdown_pct >= 10:
                return (True, "Default rule: -10% stop loss hit")
            return (False, "Within acceptable drawdown")
        
        for insight in self.insights:
            if insight.pattern_type == "cut_loss":
                cut_threshold = float(insight.condition.split(">=")[1].replace("%", ""))
                if current_drawdown_pct >= cut_threshold:
                    return (True, f"🚨 LEARNED PATTERN: Cut at {cut_threshold:.1f}% (you're at {current_drawdown_pct:.1f}%)")
        
        return (False, "Within learned drawdown limits")
    
    def get_learned_rules(self) -> List[str]:
        """Get all actionable rules the system has learned"""
        return [insight.rule for insight in self.insights]

# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("🧠 TRADE LEARNER TEST")
    print("=" * 70)
    
    learner = TradeLearner()
    
    # Create mock trades for testing
    mock_trades = [
        # Winner 1 - High convergence + volume
        TradeRecord(
            ticker="IBRX", entry_date="2026-01-01", entry_price=3.50,
            entry_convergence=93, entry_signals=["scanner", "br0kkr", "catalyst", "news", "earnings", "sector"],
            shares=500, position_size_pct=0.15, pivotal_point_score=85, volume_ratio=6.5, consolidation_days=30,
            exit_date="2026-01-15", exit_price=5.20, exit_reason="Target hit", outcome=TradeOutcome.WIN.value,
            return_pct=48.6, return_dollars=850, days_held=14, max_drawdown_pct=5.0,
            warning_signs=[], success_factors=["HIGH convergence", "Strong volume", "Solid base"]
        ),
        
        # Winner 2 - Multi-signal convergence
        TradeRecord(
            ticker="MU", entry_date="2026-01-05", entry_price=120.00,
            entry_convergence=88, entry_signals=["scanner", "br0kkr", "earnings", "sector", "pattern"],
            shares=100, position_size_pct=0.12, pivotal_point_score=75, volume_ratio=2.1, consolidation_days=25,
            exit_date="2026-01-20", exit_price=135.00, exit_reason="Target hit", outcome=TradeOutcome.WIN.value,
            return_pct=12.5, return_dollars=1500, days_held=15, max_drawdown_pct=3.0,
            warning_signs=[], success_factors=["Multi-signal", "Earnings catalyst"]
        ),
        
        # Loser 1 - Low convergence, weak volume
        TradeRecord(
            ticker="XYZ", entry_date="2026-01-08", entry_price=50.00,
            entry_convergence=72, entry_signals=["scanner", "sector"],
            shares=50, position_size_pct=0.08, pivotal_point_score=60, volume_ratio=1.2, consolidation_days=10,
            exit_date="2026-01-12", exit_price=45.00, exit_reason="Stop loss", outcome=TradeOutcome.LOSS.value,
            return_pct=-10.0, return_dollars=-250, days_held=4, max_drawdown_pct=12.0,
            warning_signs=["Low convergence", "Weak volume", "Short consolidation"], success_factors=[]
        ),
        
        # Blown up - Didn't cut soon enough
        TradeRecord(
            ticker="ABC", entry_date="2026-01-10", entry_price=100.00,
            entry_convergence=78, entry_signals=["scanner", "catalyst"],
            shares=30, position_size_pct=0.10, pivotal_point_score=65, volume_ratio=1.4, consolidation_days=12,
            exit_date="2026-01-18", exit_price=75.00, exit_reason="Finally cut", outcome=TradeOutcome.BLOWN_UP.value,
            return_pct=-25.0, return_dollars=-750, days_held=8, max_drawdown_pct=27.0,
            warning_signs=["Low convergence", "Weak volume", "Deep drawdown IGNORED"], success_factors=[]
        ),
    ]
    
    print("\n📝 Recording mock trades...")
    for trade in mock_trades:
        learner.record_trade(trade)
    
    print("\n" + "=" * 70)
    print("✅ TRADE LEARNER TEST COMPLETE")
    print("=" * 70)
    
    # Test decision making
    print("\n🤔 Testing entry decision:")
    should_enter, reasoning = learner.should_enter(
        convergence=75, 
        volume_ratio=1.3, 
        consolidation_days=15,
        signal_count=3
    )
    print(f"   Should enter? {should_enter}")
    print(f"   {reasoning}")
    
    print("\n🤔 Testing cut decision:")
    should_cut, reasoning = learner.should_cut(
        current_drawdown_pct=8.0,
        days_held=5
    )
    print(f"   Should cut? {should_cut}")
    print(f"   {reasoning}")
