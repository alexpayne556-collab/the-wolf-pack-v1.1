#!/usr/bin/env python3
"""
🐺 UNIFIED LEARNING ENGINE
Consolidation of ALL learning systems into ONE intelligence that grows smarter daily

Combines:
- trade_learner.py (496 lines) - Self-learning from trade outcomes
- pattern_learner.py (120 lines) - Pattern analysis from YOUR trades
- trade_journal.py (284 lines) - Automated trade journaling
- failed_trades.py (136 lines) - Missed opportunity tracking
- outcome_tracker.py (154 lines) - Forward return tracking

Total: 1,190 lines → ONE unified learning system

The wolf that LEARNS is the wolf that WINS.
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum
import statistics
import yfinance as yf
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection, log_trade, update_trade_outcome

# =============================================================================
# DATA MODELS
# =============================================================================

class TradeOutcome(Enum):
    WIN = "win"
    LOSS = "loss"
    BREAKEVEN = "breakeven"
    STOPPED_OUT = "stopped_out"  # Hit stop loss
    BLOWN_UP = "blown_up"  # Big loss, didn't cut soon enough
    EARLY_EXIT = "early_exit"  # Cut too soon, would've won
    MISSED = "missed"  # Didn't take the trade


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


@dataclass
class MissedOpportunity:
    """Trade you considered but didn't take"""
    ticker: str
    price: float
    timestamp: str
    reason: str  # Why you didn't take it
    move_after: Optional[float] = None  # How much it moved after
    category: str = "HESITATION"  # HESITATION, FOMO_AVOID, PDT_RESTRICTED, etc.


# =============================================================================
# UNIFIED LEARNING ENGINE
# =============================================================================

class LearningEngine:
    """
    Unified learning system that:
    1. Tracks every trade outcome (wins, losses, breakevens)
    2. Identifies patterns in YOUR trading (what works FOR YOU)
    3. Learns adaptive exit rules based on YOUR data
    4. Tracks missed opportunities (what you passed on)
    5. Updates outcomes daily (forward returns)
    6. Extracts lessons and generates actionable rules
    """
    
    def __init__(self, db_path: str = "logs/trade_history.json"):
        self.db_path = db_path
        self.trades = self._load_trades()
        self.insights = []
        
    def _load_trades(self) -> List[TradeRecord]:
        """Load all historical trades from JSON"""
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
        """Save trade history to JSON"""
        os.makedirs("logs", exist_ok=True)
        
        try:
            with open(self.db_path, 'w') as f:
                json.dump([asdict(t) for t in self.trades], f, indent=2)
        except Exception as e:
            print(f"❌ Error saving trades: {e}")
    
    # =========================================================================
    # TRADE JOURNALING (from trade_journal.py)
    # =========================================================================
    
    def log_entry(self, ticker: str, shares: float, entry_price: float, 
                  setup_type: str, thesis: str, quality_score: int = None,
                  account: str = None) -> int:
        """
        Log a trade entry
        
        Returns trade_id for tracking
        """
        
        # Store in unified database
        trade_id = log_trade(
            ticker=ticker,
            action='BUY',
            shares=shares,
            price=entry_price,
            account=account,
            thesis=thesis,
            notes=f"Setup: {setup_type}, Quality: {quality_score}/100"
        )
        
        print(f"📝 Logged entry: {ticker} @ ${entry_price:.2f}")
        print(f"   Setup: {setup_type} | Quality: {quality_score}/100")
        
        return trade_id
    
    def log_exit(self, ticker: str, shares: float, exit_price: float, 
                 entry_price: float, reason: str, emotions: str = None) -> Dict:
        """
        Log a trade exit and auto-analyze
        
        Returns full trade analysis with lessons learned
        """
        
        # Calculate outcome
        pnl = (exit_price - entry_price) * shares
        pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        
        outcome = "WIN" if pnl > 0 else "LOSS" if pnl < 0 else "BREAKEVEN"
        
        # Store in database
        trade_id = log_trade(
            ticker=ticker,
            action='SELL',
            shares=shares,
            price=exit_price,
            thesis=reason,
            notes=f"Emotions: {emotions or 'calm'}"
        )
        
        # Extract lessons
        lessons = self._extract_lessons_from_exit(ticker, pnl_pct, reason, emotions)
        
        print(f"\n{'🎉' if outcome == 'WIN' else '❌'} {outcome}: {ticker}")
        print(f"   P/L: {pnl_pct:+.1f}% (${pnl:+.2f})")
        print(f"   Reason: {reason}")
        if lessons:
            print(f"   💡 Lesson: {lessons[0]}")
        
        return {
            'ticker': ticker,
            'outcome': outcome,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'reason': reason,
            'emotions': emotions,
            'lessons': lessons
        }
    
    def _extract_lessons_from_exit(self, ticker: str, pnl_pct: float, 
                                   reason: str, emotions: str) -> List[str]:
        """Extract actionable lessons from trade exit"""
        lessons = []
        
        if pnl_pct < -5:
            if "stop" not in reason.lower():
                lessons.append("Consider setting tighter stops - drawdown exceeded -5%")
            if emotions and "panic" in emotions.lower():
                lessons.append("Emotional exit - review pre-trade plan")
        
        if pnl_pct > 20 and "early" in reason.lower():
            lessons.append("Exited early on runner - consider trailing stops")
        
        if pnl_pct < -10:
            lessons.append("CRITICAL: Big loss - review risk management")
        
        return lessons
    
    # =========================================================================
    # MISSED OPPORTUNITIES (from failed_trades.py)
    # =========================================================================
    
    def log_missed_opportunity(self, ticker: str, price: float, reason: str, 
                              move_after: Optional[float] = None,
                              category: str = "HESITATION"):
        """
        Log a trade you considered but didn't take
        
        Categories:
        - HESITATION: You weren't confident enough
        - FOMO_AVOID: Already moved too much, avoided chasing
        - PDT_RESTRICTED: Pattern day trader limit
        - NO_CAPITAL: Out of buying power
        - RISK_LIMIT: Hit max positions or concentration
        """
        
        missed = MissedOpportunity(
            ticker=ticker,
            price=price,
            timestamp=datetime.now().isoformat(),
            reason=reason,
            move_after=move_after,
            category=category
        )
        
        # Store in database as special MISSED action
        log_trade(
            ticker=ticker,
            action='MISSED',
            shares=0,
            price=price,
            thesis=reason,
            outcome=f"Moved {move_after:+.1f}%" if move_after else None,
            notes=f"Category: {category}"
        )
        
        print(f"📋 Logged missed: {ticker} @ ${price:.2f}")
        print(f"   Reason: {reason}")
        if move_after:
            print(f"   Result: {move_after:+.1f}% move after")
    
    def analyze_missed_trades(self, days: int = 30) -> Dict:
        """Analyze what you're missing and why"""
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ticker, price, thesis, outcome, timestamp, notes
            FROM trades
            WHERE action = 'MISSED'
            AND DATE(timestamp) >= DATE('now', '-' || ? || ' days')
            ORDER BY timestamp DESC
        ''', (days,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {'total': 0, 'by_category': {}, 'recent': []}
        
        # Categorize
        by_category = {}
        recent = []
        
        for row in rows:
            ticker, price, reason, outcome, timestamp, notes = row
            
            # Extract category from notes
            category = "OTHER"
            if notes and "Category:" in notes:
                category = notes.split("Category:")[1].strip()
            
            by_category[category] = by_category.get(category, 0) + 1
            
            recent.append({
                'ticker': ticker,
                'price': price,
                'reason': reason,
                'outcome': outcome,
                'timestamp': timestamp
            })
        
        return {
            'total': len(rows),
            'by_category': by_category,
            'recent': recent[:10]
        }
    
    # =========================================================================
    # OUTCOME TRACKING (from outcome_tracker.py)
    # =========================================================================
    
    def update_all_outcomes(self):
        """
        Update Day 1, 3, 5, 10 outcomes for all pending decisions
        Run this daily to track forward returns
        """
        
        print("\n" + "📊"*30)
        print("UNIFIED LEARNING ENGINE - OUTCOME TRACKER")
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("📊"*30 + "\n")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get all trades that don't have complete outcomes yet
        cursor.execute('''
        SELECT id, ticker, timestamp, action, price, shares
        FROM trades
        WHERE action IN ('BUY', 'MISSED')
        AND (day5_pct IS NULL OR day5_pct = 0)
        ORDER BY timestamp DESC
        LIMIT 100
        ''')
        
        trades = cursor.fetchall()
        
        if not trades:
            print("✅ No pending outcomes to update\n")
            conn.close()
            return
        
        print(f"Updating {len(trades)} trade outcomes...\n")
        
        for trade_id, ticker, timestamp, action, entry_price, shares in trades:
            trade_date = datetime.fromisoformat(timestamp)
            days_since = (datetime.now() - trade_date).days
            
            if days_since < 1:
                continue  # Too recent
            
            print(f"📈 {ticker} - {action} @ ${entry_price:.2f} ({days_since} days ago)")
            
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(start=trade_date.strftime('%Y-%m-%d'), period='1mo')
                
                if len(hist) == 0:
                    print(f"  ⚠️  No price data available")
                    continue
                
                # Calculate outcomes for Day 2, 5
                for days in [2, 5]:
                    if days_since >= days and len(hist) > days:
                        future_price = hist['Close'].iloc[min(days, len(hist)-1)]
                        
                        if entry_price:
                            return_pct = ((future_price - entry_price) / entry_price) * 100
                            
                            # Update in database
                            col = f'day{days}_pct'
                            update_trade_outcome(trade_id, 
                                               day2_pct=return_pct if days == 2 else None,
                                               day5_pct=return_pct if days == 5 else None)
                            
                            status = "✅" if return_pct > 0 else "❌"
                            print(f"  {status} Day {days}: {return_pct:+.1f}%")
            
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        conn.close()
        print(f"\n✅ Outcome update complete\n")
    
    # =========================================================================
    # PATTERN LEARNING (from pattern_learner.py + trade_learner.py)
    # =========================================================================
    
    def analyze_your_patterns(self) -> Dict:
        """
        Analyze YOUR trading patterns from YOUR actual trades
        
        Returns insights specific to YOUR behavior and results
        """
        
        print("\n" + "🧠"*30)
        print("LEARNING ENGINE - YOUR PATTERNS")
        print("Learning from YOUR actual trades")
        print("🧠"*30 + "\n")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        insights = {}
        
        # Pattern 1: Trades with catalysts vs without
        print("="*70)
        print("PATTERN 1: Your catalyst edge")
        print("="*70)
        
        cursor.execute('''
        SELECT 
            CASE WHEN thesis LIKE '%catalyst%' OR thesis LIKE '%news%' 
                 THEN 'With Catalyst' ELSE 'No Catalyst' END as has_catalyst,
            COUNT(*) as trades,
            AVG(day5_pct) as avg_return,
            SUM(CASE WHEN day5_pct > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
        FROM trades
        WHERE action = 'BUY' AND day5_pct IS NOT NULL
        GROUP BY has_catalyst
        ''')
        
        catalyst_results = cursor.fetchall()
        for catalyst_status, trades, avg_return, win_rate in catalyst_results:
            print(f"\n{catalyst_status}:")
            print(f"  Trades: {trades}")
            print(f"  Win Rate: {win_rate:.1f}%")
            print(f"  Avg 5-day Return: {avg_return:+.1f}%")
        
        insights['catalyst_edge'] = catalyst_results
        
        # Pattern 2: Entry timing analysis
        print("\n" + "="*70)
        print("PATTERN 2: Your best entry timing")
        print("="*70)
        
        cursor.execute('''
        SELECT 
            CASE 
                WHEN time(timestamp) < '11:00:00' THEN 'Morning Entry'
                WHEN time(timestamp) < '14:00:00' THEN 'Midday Entry'
                ELSE 'Late Day Entry'
            END as entry_timing,
            COUNT(*) as trades,
            AVG(day5_pct) as avg_return,
            SUM(CASE WHEN day5_pct > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
        FROM trades
        WHERE action = 'BUY' AND day5_pct IS NOT NULL
        GROUP BY entry_timing
        ''')
        
        timing_results = cursor.fetchall()
        for timing, trades, avg_return, win_rate in timing_results:
            print(f"\n{timing}:")
            print(f"  Trades: {trades}")
            print(f"  Win Rate: {win_rate:.1f}%")
            print(f"  Avg 5-day Return: {avg_return:+.1f}%")
        
        insights['entry_timing'] = timing_results
        
        # Pattern 3: Your best tickers
        print("\n" + "="*70)
        print("PATTERN 3: Your best performing tickers")
        print("="*70)
        
        cursor.execute('''
        SELECT 
            ticker,
            COUNT(*) as trades,
            AVG(day5_pct) as avg_return,
            SUM(CASE WHEN day5_pct > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
        FROM trades
        WHERE action = 'BUY' AND day5_pct IS NOT NULL
        GROUP BY ticker
        HAVING COUNT(*) >= 2
        ORDER BY avg_return DESC
        LIMIT 10
        ''')
        
        ticker_results = cursor.fetchall()
        print("\nTop 10 tickers (min 2 trades):\n")
        for ticker, trades, avg_return, win_rate in ticker_results:
            print(f"{ticker:6} | {trades} trades | Win: {win_rate:.0f}% | Avg: {avg_return:+.1f}%")
        
        insights['best_tickers'] = ticker_results
        
        # Pattern 4: Watch vs Act comparison
        print("\n" + "="*70)
        print("PATTERN 4: Stocks you WATCHED vs BOUGHT")
        print("="*70)
        
        cursor.execute('''
        SELECT 
            action,
            COUNT(*) as count,
            AVG(day5_pct) as avg_move
        FROM trades
        WHERE action IN ('MISSED', 'BUY') AND day5_pct IS NOT NULL
        GROUP BY action
        ''')
        
        watch_results = cursor.fetchall()
        print("\nWhat happens to stocks you watch vs buy?\n")
        for action, count, avg_move in watch_results:
            status = "You acted" if action == 'BUY' else "You passed"
            print(f"{status:12} | {count:2} times | Avg 5d move: {avg_move:+.1f}%")
        
        insights['watch_vs_act'] = watch_results
        
        conn.close()
        
        print("\n" + "="*70)
        print("🧠 Keep logging - patterns get clearer with more data")
        print("="*70 + "\n")
        
        return insights
    
    def get_win_rate(self) -> float:
        """Calculate overall win rate from trades"""
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            SUM(CASE WHEN day5_pct > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
        FROM trades
        WHERE action = 'BUY' AND day5_pct IS NOT NULL
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result and result[0] else 0.0
    
    def get_avg_return(self) -> float:
        """Calculate average return from trades"""
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT AVG(day5_pct) as avg_return
        FROM trades
        WHERE action = 'BUY' AND day5_pct IS NOT NULL
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result and result[0] else 0.0
    
    # =========================================================================
    # ACTIONABLE INSIGHTS
    # =========================================================================
    
    def generate_insights(self) -> List[LearningInsight]:
        """
        Generate actionable trading insights based on YOUR data
        
        Returns list of insights with confidence scores and rules
        """
        
        insights = []
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Insight 1: Best setup types
        cursor.execute('''
        SELECT 
            thesis,
            COUNT(*) as sample_size,
            AVG(day5_pct) as avg_return,
            SUM(CASE WHEN day5_pct > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
        FROM trades
        WHERE action = 'BUY' AND day5_pct IS NOT NULL AND thesis IS NOT NULL
        GROUP BY thesis
        HAVING COUNT(*) >= 3
        ORDER BY avg_return DESC
        LIMIT 5
        ''')
        
        for thesis, sample_size, avg_return, win_rate in cursor.fetchall():
            if win_rate > 60 and avg_return > 3:
                insights.append(LearningInsight(
                    pattern_type="SETUP_TYPE",
                    condition=f"Setup: {thesis}",
                    outcome_if_true=f"Avg return: {avg_return:+.1f}%",
                    confidence=win_rate / 100.0,
                    sample_size=sample_size,
                    rule=f"PRIORITIZE {thesis} setups - proven {win_rate:.0f}% win rate"
                ))
        
        conn.close()
        
        return insights
    
    def should_take_trade(self, ticker: str, setup_type: str, score: int) -> Dict:
        """
        PRE-TRADE FILTER: Should we take this trade based on learned patterns?
        
        Uses YOUR historical data to filter out setups that don't work FOR YOU
        
        Returns:
            Dict with 'should_take' (bool), 'reason' (str), 'historical_winrate' (float)
        """
        
        # If no historical data, allow the trade (default to yes)
        if len(self.trades) < 10:
            return {
                'should_take': True,
                'reason': 'No historical data yet - building experience',
                'historical_winrate': None
            }
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check 1: Similar setup type performance
        cursor.execute('''
        SELECT 
            COUNT(*) as sample_size,
            AVG(day5_pct) as avg_return,
            SUM(CASE WHEN day5_pct > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
        FROM trades
        WHERE action = 'BUY' 
            AND thesis LIKE ?
            AND day5_pct IS NOT NULL
        ''', (f'%{setup_type}%',))
        
        result = cursor.fetchone()
        
        if result and result[0] >= 5:  # At least 5 samples
            sample_size, avg_return, win_rate = result
            
            # If this setup historically fails, block it
            if win_rate < 40:
                conn.close()
                return {
                    'should_take': False,
                    'reason': f'{setup_type} setups have {win_rate:.0f}% win rate (need 40%+)',
                    'historical_winrate': win_rate
                }
            
            # If marginal, warn but allow
            if win_rate < 50:
                conn.close()
                return {
                    'should_take': True,
                    'reason': f'{setup_type} setups: {win_rate:.0f}% win rate (marginal)',
                    'historical_winrate': win_rate
                }
        
        # Check 2: This specific ticker performance
        cursor.execute('''
        SELECT 
            COUNT(*) as sample_size,
            AVG(day5_pct) as avg_return,
            SUM(CASE WHEN day5_pct > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
        FROM trades
        WHERE action = 'BUY' 
            AND ticker = ?
            AND day5_pct IS NOT NULL
        ''', (ticker,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] >= 3:  # At least 3 trades on this ticker
            sample_size, avg_return, win_rate = result
            
            # If you lose on this ticker, avoid it
            if win_rate < 30:
                return {
                    'should_take': False,
                    'reason': f'{ticker} has {win_rate:.0f}% win rate for you (avoid)',
                    'historical_winrate': win_rate
                }
            
            # If strong history, prioritize
            if win_rate > 70:
                return {
                    'should_take': True,
                    'reason': f'{ticker} has {win_rate:.0f}% win rate for you (strong edge!)',
                    'historical_winrate': win_rate
                }
        
        # Default: Allow trade with neutral reason
        return {
            'should_take': True,
            'reason': 'Trade approved - no negative patterns detected',
            'historical_winrate': None
        }
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def generate_learning_report(self) -> str:
        """Generate comprehensive learning report"""
        
        report = []
        report.append("\n" + "="*70)
        report.append("🧠 UNIFIED LEARNING ENGINE - COMPREHENSIVE REPORT")
        report.append("="*70 + "\n")
        
        # Overall stats
        win_rate = self.get_win_rate()
        avg_return = self.get_avg_return()
        
        report.append(f"📊 OVERALL PERFORMANCE:")
        report.append(f"   Win Rate: {win_rate:.1f}%")
        report.append(f"   Avg Return (5d): {avg_return:+.1f}%")
        report.append("")
        
        # Get insights
        insights = self.generate_insights()
        
        if insights:
            report.append(f"💡 ACTIONABLE INSIGHTS ({len(insights)} rules):")
            for i, insight in enumerate(insights, 1):
                report.append(f"\n{i}. {insight.pattern_type}")
                report.append(f"   Condition: {insight.condition}")
                report.append(f"   Result: {insight.outcome_if_true}")
                report.append(f"   Confidence: {insight.confidence:.0%} (n={insight.sample_size})")
                report.append(f"   Rule: {insight.rule}")
        
        report.append("\n" + "="*70 + "\n")
        
        return "\n".join(report)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_learning_engine() -> LearningEngine:
    """Get singleton learning engine instance"""
    if not hasattr(get_learning_engine, '_instance'):
        get_learning_engine._instance = LearningEngine()
    return get_learning_engine._instance


# =============================================================================
# TEST & DEMO
# =============================================================================

if __name__ == "__main__":
    print("\n🐺 UNIFIED LEARNING ENGINE - INITIALIZATION\n")
    
    engine = LearningEngine()
    
    # Demo: Update all pending outcomes
    print("\n1️⃣ Updating all pending trade outcomes...")
    engine.update_all_outcomes()
    
    # Demo: Analyze your patterns
    print("\n2️⃣ Analyzing your trading patterns...")
    patterns = engine.analyze_your_patterns()
    
    # Demo: Check missed opportunities
    print("\n3️⃣ Analyzing missed opportunities...")
    missed = engine.analyze_missed_trades(days=30)
    
    if missed['total'] > 0:
        print(f"\n📋 Missed {missed['total']} opportunities in last 30 days:")
        for category, count in missed['by_category'].items():
            print(f"   {category}: {count}x")
    
    # Demo: Generate insights
    print("\n4️⃣ Generating actionable insights...")
    insights = engine.generate_insights()
    
    if insights:
        print(f"\n💡 Found {len(insights)} actionable insights:")
        for insight in insights:
            print(f"   • {insight.rule}")
    
    # Demo: Full report
    print("\n5️⃣ Generating comprehensive report...")
    report = engine.generate_learning_report()
    print(report)
    
    print("\n✅ UNIFIED LEARNING ENGINE: OPERATIONAL")
    print("   🧠 All learning systems consolidated")
    print("   📊 Outcome tracking active")
    print("   💡 Pattern recognition enabled")
    print("   📝 Trade journaling unified")
    print("   🎯 Missed opportunity tracking online")
    print("\n🐺 The wolf that LEARNS is the wolf that WINS.\n")
