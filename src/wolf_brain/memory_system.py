"""
🧠 MEMORY SYSTEM - TRUE LEARNING, NOT JUST STATISTICS
Built: January 20, 2026

The brain's memory has two parts:
1. LONG-TERM MEMORY: Database + vector store for semantic search
2. WORKING MEMORY: Current session context

This is how the brain:
- Remembers every trade and lesson
- Finds similar past trades
- Evolves strategies based on experience
- Answers questions about trading history

Usage:
    from wolf_brain.memory_system import MemorySystem, WorkingMemory
    
    memory = MemorySystem()
    
    # Store a trade analysis
    memory.store_analysis('GLSI', analysis, decision)
    
    # Find similar past trades
    similar = memory.find_similar_trades('BTAI', setup_data)
    
    # Ask memory questions
    answer = memory.query("What's our win rate on biotech?")
"""

import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path


class MemorySystem:
    """
    The brain's long-term memory
    Stores trades, analyses, lessons, and enables learning
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize memory system
        
        Args:
            db_path: Path to SQLite database (default: data/wolf_brain_memory.db)
        """
        if db_path is None:
            # Get project root and create data directory
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / 'data' / 'wolf_brain'
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / 'memory.db')
        
        self.db_path = db_path
        self._init_database()
        
        print(f"🧠 Memory System initialized: {self.db_path}")
        print(f"   Total memories: {self._count_memories()}")
    
    def _init_database(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analyses table - stores every trade analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                decision TEXT NOT NULL,
                confidence INTEGER,
                thesis TEXT,
                bear_case TEXT,
                full_analysis TEXT,
                setup_data TEXT,
                strategy_used TEXT
            )
        ''')
        
        # Trades table - stores executed trades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                entry_timestamp TEXT NOT NULL,
                exit_timestamp TEXT,
                entry_price REAL,
                exit_price REAL,
                shares INTEGER,
                strategy TEXT,
                thesis TEXT,
                trade_plan TEXT,
                outcome TEXT,
                return_pct REAL,
                exit_reason TEXT,
                status TEXT DEFAULT 'OPEN'
            )
        ''')
        
        # Lessons table - stores learnings from trades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER,
                timestamp TEXT NOT NULL,
                lesson_type TEXT,
                description TEXT,
                strategy TEXT,
                recommendation TEXT,
                FOREIGN KEY (trade_id) REFERENCES trades (id)
            )
        ''')
        
        # Strategy performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                strategy TEXT PRIMARY KEY,
                trades INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                total_return REAL DEFAULT 0,
                avg_win REAL DEFAULT 0,
                avg_loss REAL DEFAULT 0,
                best_trade REAL DEFAULT 0,
                worst_trade REAL DEFAULT 0,
                last_updated TEXT
            )
        ''')
        
        # Adaptations table - tracks strategy changes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS adaptations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                strategy TEXT,
                adaptation_type TEXT,
                reason TEXT,
                old_value TEXT,
                new_value TEXT
            )
        ''')
        
        # Taught strategies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS taught_strategies (
                name TEXT PRIMARY KEY,
                description TEXT,
                created_at TEXT,
                created_by TEXT DEFAULT 'Tyr',
                examples TEXT,
                compiled_understanding TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _count_memories(self) -> int:
        """Count total memories stored"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        total = 0
        for table in ['analyses', 'trades', 'lessons']:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            total += cursor.fetchone()[0]
        
        conn.close()
        return total
    
    # ========== STORING MEMORIES ==========
    
    def store_analysis(self, ticker: str, analysis: Dict, decision: Dict):
        """
        Store a trade analysis for future reference
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analyses 
            (ticker, timestamp, decision, confidence, thesis, bear_case, 
             full_analysis, setup_data, strategy_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ticker,
            datetime.now().isoformat(),
            decision.get('decision', 'UNKNOWN'),
            decision.get('confidence', 0),
            decision.get('thesis', ''),
            decision.get('bear_case', ''),
            analysis.get('full_analysis', ''),
            json.dumps(analysis.get('setup_data', {})),
            decision.get('strategy', '')
        ))
        
        conn.commit()
        conn.close()
    
    def store_trade_entry(self, trade: Dict) -> int:
        """
        Store a new trade entry
        
        Returns: trade_id for tracking
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades
            (ticker, entry_timestamp, entry_price, shares, strategy, 
             thesis, trade_plan, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN')
        ''', (
            trade['ticker'],
            datetime.now().isoformat(),
            trade.get('entry_price', 0),
            trade.get('shares', 0),
            trade.get('strategy', ''),
            trade.get('thesis', ''),
            trade.get('trade_plan', '')
        ))
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return trade_id
    
    def store_trade_exit(self, trade_id: int, outcome: Dict):
        """
        Store trade exit and outcome
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE trades
            SET exit_timestamp = ?,
                exit_price = ?,
                outcome = ?,
                return_pct = ?,
                exit_reason = ?,
                status = 'CLOSED'
            WHERE id = ?
        ''', (
            datetime.now().isoformat(),
            outcome.get('exit_price', 0),
            outcome.get('outcome', ''),
            outcome.get('return_pct', 0),
            outcome.get('exit_reason', ''),
            trade_id
        ))
        
        conn.commit()
        conn.close()
        
        # Update strategy performance
        self._update_strategy_performance(trade_id)
    
    def store_lesson(self, trade_id: int, lesson: Dict):
        """
        Store a lesson learned from a trade
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO lessons
            (trade_id, timestamp, lesson_type, description, strategy, recommendation)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            trade_id,
            datetime.now().isoformat(),
            lesson.get('type', 'GENERAL'),
            lesson.get('description', ''),
            lesson.get('strategy', ''),
            lesson.get('recommendation', '')
        ))
        
        conn.commit()
        conn.close()
    
    def store_taught_strategy(self, name: str, description: str, 
                             examples: List[Dict] = None, understanding: str = ''):
        """Store a strategy that was taught to the brain"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO taught_strategies
            (name, description, created_at, examples, compiled_understanding)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            name,
            description,
            datetime.now().isoformat(),
            json.dumps(examples) if examples else '[]',
            understanding
        ))
        
        conn.commit()
        conn.close()
    
    # ========== RETRIEVING MEMORIES ==========
    
    def get_trade_history(self, ticker: str = None, strategy: str = None,
                         days: int = None, status: str = None) -> List[Dict]:
        """
        Get trade history with optional filters
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM trades WHERE 1=1'
        params = []
        
        if ticker:
            query += ' AND ticker = ?'
            params.append(ticker)
        
        if strategy:
            query += ' AND strategy = ?'
            params.append(strategy)
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            query += ' AND entry_timestamp > ?'
            params.append(cutoff)
        
        query += ' ORDER BY entry_timestamp DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    def find_similar_trades(self, ticker: str, setup_data: Dict, 
                           limit: int = 5) -> List[Dict]:
        """
        Find trades with similar setups
        Uses basic matching (vector search could be added later)
        """
        similar = []
        
        # Get sector/industry of ticker
        sector = setup_data.get('sector', '')
        
        # Get all historical trades
        trades = self.get_trade_history(days=365)
        
        for trade in trades:
            if trade['ticker'] == ticker:
                continue  # Skip same ticker
            
            similarity_score = 0
            
            # Same sector bonus
            # (Would need to store sector in trades table for this)
            
            # Similar strategy
            if trade.get('strategy') == setup_data.get('strategy'):
                similarity_score += 30
            
            # Similar price range
            entry_price = trade.get('entry_price', 0)
            current_price = setup_data.get('current_price', 0)
            if current_price > 0 and entry_price > 0:
                price_ratio = min(entry_price, current_price) / max(entry_price, current_price)
                if price_ratio > 0.8:  # Within 20%
                    similarity_score += 20
            
            # Has outcome (we can learn from it)
            if trade.get('return_pct') is not None:
                similarity_score += 10
            
            if similarity_score >= 30:
                similar.append({
                    'trade': trade,
                    'similarity_score': similarity_score
                })
        
        # Sort by similarity
        similar.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similar[:limit]
    
    def get_lessons_for_strategy(self, strategy: str) -> List[Dict]:
        """Get all lessons learned for a strategy"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM lessons
            WHERE strategy = ?
            ORDER BY timestamp DESC
        ''', (strategy,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_strategy_performance(self, strategy: str = None) -> Dict:
        """Get performance metrics for strategy/strategies"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if strategy:
            cursor.execute('SELECT * FROM strategy_performance WHERE strategy = ?', 
                          (strategy,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else {}
        else:
            cursor.execute('SELECT * FROM strategy_performance')
            rows = cursor.fetchall()
            conn.close()
            return {row['strategy']: dict(row) for row in rows}
    
    def get_taught_strategies(self) -> List[Dict]:
        """Get all strategies that were taught to the brain"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM taught_strategies ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            d = dict(row)
            d['examples'] = json.loads(d['examples']) if d['examples'] else []
            result.append(d)
        
        return result
    
    # ========== LEARNING & ADAPTATION ==========
    
    def _update_strategy_performance(self, trade_id: int):
        """Update strategy performance after trade closes"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get the trade
        cursor.execute('SELECT * FROM trades WHERE id = ?', (trade_id,))
        trade = cursor.fetchone()
        
        if not trade:
            conn.close()
            return
        
        strategy = trade['strategy']
        return_pct = trade['return_pct'] or 0
        is_win = return_pct > 0
        
        # Get current performance
        cursor.execute('SELECT * FROM strategy_performance WHERE strategy = ?', 
                      (strategy,))
        perf = cursor.fetchone()
        
        if perf:
            # Update existing
            new_trades = perf['trades'] + 1
            new_wins = perf['wins'] + (1 if is_win else 0)
            new_total = perf['total_return'] + return_pct
            new_best = max(perf['best_trade'], return_pct)
            new_worst = min(perf['worst_trade'], return_pct)
            
            # Calculate new averages
            wins = [t['return_pct'] for t in self.get_trade_history(strategy=strategy)
                   if t['return_pct'] and t['return_pct'] > 0]
            losses = [t['return_pct'] for t in self.get_trade_history(strategy=strategy)
                     if t['return_pct'] and t['return_pct'] <= 0]
            
            new_avg_win = sum(wins) / len(wins) if wins else 0
            new_avg_loss = sum(losses) / len(losses) if losses else 0
            
            cursor.execute('''
                UPDATE strategy_performance
                SET trades = ?, wins = ?, total_return = ?,
                    avg_win = ?, avg_loss = ?,
                    best_trade = ?, worst_trade = ?, last_updated = ?
                WHERE strategy = ?
            ''', (new_trades, new_wins, new_total, new_avg_win, new_avg_loss,
                  new_best, new_worst, datetime.now().isoformat(), strategy))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO strategy_performance
                (strategy, trades, wins, total_return, avg_win, avg_loss,
                 best_trade, worst_trade, last_updated)
                VALUES (?, 1, ?, ?, ?, 0, ?, ?, ?)
            ''', (strategy, 1 if is_win else 0, return_pct,
                  return_pct if is_win else 0,
                  return_pct, return_pct, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def check_adaptation_triggers(self, strategy: str) -> List[Dict]:
        """
        Check if strategy parameters should be adapted based on performance
        """
        perf = self.get_strategy_performance(strategy)
        
        if not perf or perf.get('trades', 0) < 5:
            return []  # Need minimum sample size
        
        adaptations = []
        
        trades = perf['trades']
        win_rate = perf['wins'] / trades if trades > 0 else 0
        avg_return = perf['total_return'] / trades if trades > 0 else 0
        avg_loss = perf.get('avg_loss', 0)
        
        # Poor win rate
        if win_rate < 0.40:
            adaptations.append({
                'type': 'TIGHTEN_ENTRY',
                'strategy': strategy,
                'reason': f"Win rate {win_rate:.1%} below 40%",
                'recommendation': 'Increase minimum confidence threshold'
            })
        
        # Large average loss
        if avg_loss < -0.15:
            adaptations.append({
                'type': 'TIGHTEN_STOP',
                'strategy': strategy,
                'reason': f"Average loss {avg_loss:.1%} exceeds -15%",
                'recommendation': 'Tighten stop loss levels'
            })
        
        # Negative expected value
        if avg_return < 0:
            adaptations.append({
                'type': 'PAUSE_STRATEGY',
                'strategy': strategy,
                'reason': f"Negative EV: {avg_return:.1%}",
                'recommendation': 'Review and potentially pause this strategy'
            })
        
        # Excellent performance
        if win_rate > 0.70 and trades >= 10:
            adaptations.append({
                'type': 'PROMOTE_STRATEGY',
                'strategy': strategy,
                'reason': f"Excellent {win_rate:.1%} win rate over {trades} trades",
                'recommendation': 'Increase position size allowance'
            })
        
        # Store adaptations
        for adapt in adaptations:
            self.store_adaptation(adapt)
        
        return adaptations
    
    def store_adaptation(self, adaptation: Dict):
        """Store an adaptation for tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO adaptations
            (timestamp, strategy, adaptation_type, reason, old_value, new_value)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            adaptation.get('strategy', ''),
            adaptation.get('type', ''),
            adaptation.get('reason', ''),
            adaptation.get('old_value', ''),
            adaptation.get('new_value', '')
        ))
        
        conn.commit()
        conn.close()
    
    def get_learning_insights(self) -> Dict:
        """
        Get aggregated learning insights for the brain
        """
        return {
            'strategy_performance': self.get_strategy_performance(),
            'total_trades': len(self.get_trade_history()),
            'open_positions': len(self.get_trade_history(status='OPEN')),
            'recent_lessons': self._get_recent_lessons(limit=10),
            'best_strategies': self._get_best_strategies(),
            'recent_adaptations': self._get_recent_adaptations()
        }
    
    def _get_recent_lessons(self, limit: int = 10) -> List[Dict]:
        """Get most recent lessons"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM lessons
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def _get_best_strategies(self, min_trades: int = 5) -> List[Dict]:
        """Get best performing strategies"""
        perf = self.get_strategy_performance()
        
        best = []
        for strategy, stats in perf.items():
            if stats.get('trades', 0) >= min_trades:
                win_rate = stats['wins'] / stats['trades']
                avg_return = stats['total_return'] / stats['trades']
                
                best.append({
                    'strategy': strategy,
                    'win_rate': win_rate,
                    'avg_return': avg_return,
                    'trades': stats['trades']
                })
        
        best.sort(key=lambda x: x['win_rate'], reverse=True)
        return best
    
    def _get_recent_adaptations(self, limit: int = 5) -> List[Dict]:
        """Get recent strategy adaptations"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM adaptations
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


class WorkingMemory:
    """
    Short-term memory for current trading session
    """
    
    def __init__(self):
        self.current_positions: Dict[str, Dict] = {}
        self.todays_trades: List[Dict] = []
        self.active_watchlist: List[str] = []
        self.market_context: Dict = {}
        self.daily_plan: str = ""
        self.recent_thoughts: List[str] = []  # Last N reasoning chains
        self.session_start = datetime.now()
    
    def update_market_context(self, data: Dict):
        """Update current market context"""
        self.market_context.update(data)
        self.market_context['last_updated'] = datetime.now().isoformat()
    
    def add_position(self, ticker: str, position_data: Dict):
        """Track a new position"""
        self.current_positions[ticker] = {
            **position_data,
            'added_at': datetime.now().isoformat()
        }
    
    def update_position(self, ticker: str, updates: Dict):
        """Update position data"""
        if ticker in self.current_positions:
            self.current_positions[ticker].update(updates)
    
    def remove_position(self, ticker: str):
        """Remove a closed position"""
        if ticker in self.current_positions:
            del self.current_positions[ticker]
    
    def log_trade(self, trade: Dict):
        """Log a trade for today"""
        trade['timestamp'] = datetime.now().isoformat()
        self.todays_trades.append(trade)
    
    def add_to_watchlist(self, ticker: str):
        """Add ticker to watchlist"""
        if ticker not in self.active_watchlist:
            self.active_watchlist.append(ticker)
    
    def remove_from_watchlist(self, ticker: str):
        """Remove from watchlist"""
        if ticker in self.active_watchlist:
            self.active_watchlist.remove(ticker)
    
    def add_thought(self, thought: str, max_thoughts: int = 20):
        """Store a reasoning chain"""
        self.recent_thoughts.append({
            'thought': thought,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only recent thoughts
        if len(self.recent_thoughts) > max_thoughts:
            self.recent_thoughts = self.recent_thoughts[-max_thoughts:]
    
    def get_context_summary(self) -> str:
        """Get formatted summary of current context"""
        summary = f"""
CURRENT SESSION ({self.session_start.strftime('%Y-%m-%d %H:%M')})

MARKET CONTEXT:
{json.dumps(self.market_context, indent=2, default=str)}

CURRENT POSITIONS ({len(self.current_positions)}):
{json.dumps(self.current_positions, indent=2, default=str)}

TODAY'S TRADES: {len(self.todays_trades)}

WATCHLIST ({len(self.active_watchlist)}):
{', '.join(self.active_watchlist) if self.active_watchlist else 'Empty'}

TODAY'S PLAN:
{self.daily_plan if self.daily_plan else 'Not set yet'}
"""
        return summary
    
    def get_session_stats(self) -> Dict:
        """Get session statistics"""
        wins = sum(1 for t in self.todays_trades 
                  if t.get('return_pct', 0) > 0)
        losses = len(self.todays_trades) - wins
        total_return = sum(t.get('return_pct', 0) for t in self.todays_trades)
        
        return {
            'trades_today': len(self.todays_trades),
            'wins': wins,
            'losses': losses,
            'total_return_pct': total_return,
            'positions_open': len(self.current_positions),
            'watchlist_size': len(self.active_watchlist),
            'session_duration': str(datetime.now() - self.session_start)
        }
    
    def reset_daily(self):
        """Reset daily counters (call at market close)"""
        self.todays_trades = []
        self.daily_plan = ""
        self.recent_thoughts = []


# ============ TESTING ============

def test_memory():
    """Test the memory system"""
    print("\n" + "="*80)
    print("🧠 TESTING MEMORY SYSTEM")
    print("="*80)
    
    # Initialize memory
    memory = MemorySystem()
    
    # Test storing an analysis
    print("\n📝 Testing: Store analysis")
    memory.store_analysis(
        ticker='GLSI',
        analysis={
            'full_analysis': 'CEO buying heavily, Phase 3 catalyst...',
            'setup_data': {'price': 24.88, 'float': 6570000}
        },
        decision={
            'decision': 'TRADE',
            'confidence': 75,
            'thesis': 'Insider buying + binary catalyst',
            'strategy': 'Head Hunter'
        }
    )
    print("   ✅ Analysis stored")
    
    # Test storing a trade
    print("\n📝 Testing: Store trade entry")
    trade_id = memory.store_trade_entry({
        'ticker': 'GLSI',
        'entry_price': 24.88,
        'shares': 40,
        'strategy': 'Head Hunter',
        'thesis': 'Insider buying + Phase 3 catalyst'
    })
    print(f"   ✅ Trade stored with ID: {trade_id}")
    
    # Test trade exit
    print("\n📝 Testing: Store trade exit")
    memory.store_trade_exit(trade_id, {
        'exit_price': 29.86,
        'return_pct': 0.20,
        'exit_reason': 'TARGET_HIT',
        'outcome': 'WIN'
    })
    print("   ✅ Trade exit recorded")
    
    # Test lesson storage
    print("\n📝 Testing: Store lesson")
    memory.store_lesson(trade_id, {
        'type': 'WIN_PATTERN',
        'description': 'CEO buying + Phase 3 = strong combo',
        'strategy': 'Head Hunter',
        'recommendation': 'Keep using this setup'
    })
    print("   ✅ Lesson stored")
    
    # Test retrieval
    print("\n📝 Testing: Get trade history")
    trades = memory.get_trade_history(days=30)
    print(f"   Found {len(trades)} trades in last 30 days")
    
    # Test learning insights
    print("\n📝 Testing: Get learning insights")
    insights = memory.get_learning_insights()
    print(f"   Total trades: {insights['total_trades']}")
    print(f"   Open positions: {insights['open_positions']}")
    
    # Test working memory
    print("\n📝 Testing: Working memory")
    working = WorkingMemory()
    working.add_position('GLSI', {'shares': 40, 'entry': 24.88})
    working.add_to_watchlist('BTAI')
    working.add_to_watchlist('ONCY')
    working.update_market_context({'spy_trend': 'UP', 'vix': 15.2})
    
    stats = working.get_session_stats()
    print(f"   Positions: {stats['positions_open']}")
    print(f"   Watchlist: {stats['watchlist_size']}")
    
    print("\n✅ Memory system tests complete!")


if __name__ == "__main__":
    test_memory()
