"""
PATTERN DATABASE SERVICE (Layer 8 - Memory)
The Learning System

Stores validated patterns, tracks win rates, learns what works.
Provides 5th signal type for convergence engine.

From THE_BIG_PICTURE.md:
- Store researched patterns (validation through live testing)
- Track every setup outcome
- Calculate pattern win rates
- Historical pattern validation

Edge: System remembers what works. "Wounded prey + 30% compression = 68.8% win rate"
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import os


# =============================================================================
# DATA MODELS
# =============================================================================

class PatternType(Enum):
    """Known successful patterns"""
    WOUNDED_PREY = "WOUNDED_PREY"
    EARLY_MOMENTUM = "EARLY_MOMENTUM"
    BREAKOUT = "BREAKOUT"
    MEAN_REVERSION = "MEAN_REVERSION"
    VOLUME_SPIKE = "VOLUME_SPIKE"
    INSIDER_CLUSTER = "INSIDER_CLUSTER"
    ACTIVIST_13D = "ACTIVIST_13D"
    CATALYST_PLAY = "CATALYST_PLAY"
    SECTOR_ROTATION = "SECTOR_ROTATION"


@dataclass
class PatternInstance:
    """Single occurrence of a pattern"""
    id: Optional[int]
    ticker: str
    pattern_type: PatternType
    detected_date: str
    entry_price: float
    stop_price: float
    target_price: Optional[float]
    
    # Setup characteristics
    distance_from_high: float
    volume_ratio: float
    rsi: Optional[float]
    
    # Outcome (filled when position closed)
    exit_date: Optional[str]
    exit_price: Optional[float]
    return_pct: Optional[float]
    hit_target: Optional[bool]
    hit_stop: Optional[bool]
    hold_days: Optional[int]
    
    # Classification
    outcome: Optional[str]  # "WIN", "LOSS", "SCRATCH", "OPEN"
    
    # Additional signals (convergence data)
    had_institutional_signal: bool = False
    had_catalyst_signal: bool = False
    had_sector_signal: bool = False
    convergence_score: Optional[int] = None


@dataclass
class PatternStats:
    """Statistics for a pattern type"""
    pattern_type: PatternType
    total_instances: int
    closed_instances: int
    win_count: int
    loss_count: int
    scratch_count: int
    win_rate: float
    avg_return: float
    avg_winner: float
    avg_loser: float
    avg_hold_days: float
    best_return: float
    worst_return: float
    
    # Convergence analysis
    with_institutional_win_rate: Optional[float] = None
    with_catalyst_win_rate: Optional[float] = None
    convergence_boost: Optional[float] = None


# =============================================================================
# PATTERN DATABASE
# =============================================================================

class PatternDatabase:
    """
    SQLite database for pattern tracking and learning
    Stores all patterns and their outcomes
    """
    
    def __init__(self, db_path: str = "data/patterns.db"):
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Create pattern tracking tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                detected_date TEXT NOT NULL,
                entry_price REAL NOT NULL,
                stop_price REAL NOT NULL,
                target_price REAL,
                
                distance_from_high REAL,
                volume_ratio REAL,
                rsi REAL,
                
                exit_date TEXT,
                exit_price REAL,
                return_pct REAL,
                hit_target INTEGER,
                hit_stop INTEGER,
                hold_days INTEGER,
                outcome TEXT,
                
                had_institutional_signal INTEGER DEFAULT 0,
                had_catalyst_signal INTEGER DEFAULT 0,
                had_sector_signal INTEGER DEFAULT 0,
                convergence_score INTEGER,
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pattern performance summary view
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS pattern_performance AS
            SELECT 
                pattern_type,
                COUNT(*) as total_instances,
                COUNT(CASE WHEN outcome IS NOT NULL THEN 1 END) as closed_instances,
                COUNT(CASE WHEN outcome = 'WIN' THEN 1 END) as wins,
                COUNT(CASE WHEN outcome = 'LOSS' THEN 1 END) as losses,
                CAST(COUNT(CASE WHEN outcome = 'WIN' THEN 1 END) AS REAL) / 
                    NULLIF(COUNT(CASE WHEN outcome IS NOT NULL THEN 1 END), 0) * 100 as win_rate,
                AVG(CASE WHEN outcome IS NOT NULL THEN return_pct END) as avg_return,
                AVG(CASE WHEN outcome = 'WIN' THEN return_pct END) as avg_winner,
                AVG(CASE WHEN outcome = 'LOSS' THEN return_pct END) as avg_loser,
                AVG(CASE WHEN outcome IS NOT NULL THEN hold_days END) as avg_hold_days,
                MAX(return_pct) as best_return,
                MIN(return_pct) as worst_return
            FROM patterns
            GROUP BY pattern_type
        ''')
        
        conn.commit()
        conn.close()
    
    def add_pattern(self, pattern: PatternInstance) -> int:
        """Add new pattern instance, returns pattern ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO patterns (
                ticker, pattern_type, detected_date, entry_price, stop_price, target_price,
                distance_from_high, volume_ratio, rsi,
                had_institutional_signal, had_catalyst_signal, had_sector_signal, convergence_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern.ticker,
            pattern.pattern_type.value,
            pattern.detected_date,
            pattern.entry_price,
            pattern.stop_price,
            pattern.target_price,
            pattern.distance_from_high,
            pattern.volume_ratio,
            pattern.rsi,
            1 if pattern.had_institutional_signal else 0,
            1 if pattern.had_catalyst_signal else 0,
            1 if pattern.had_sector_signal else 0,
            pattern.convergence_score
        ))
        
        pattern_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return pattern_id
    
    def update_outcome(self, pattern_id: int, exit_date: str, exit_price: float,
                       hit_target: bool = False, hit_stop: bool = False):
        """Update pattern with outcome data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get entry price
        cursor.execute('SELECT entry_price, detected_date FROM patterns WHERE id = ?', (pattern_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return
        
        entry_price, entry_date = result
        
        # Calculate metrics
        return_pct = ((exit_price - entry_price) / entry_price) * 100
        hold_days = (datetime.strptime(exit_date, '%Y-%m-%d') - 
                    datetime.strptime(entry_date, '%Y-%m-%d')).days
        
        # Determine outcome
        if abs(return_pct) < 2:
            outcome = "SCRATCH"
        elif return_pct > 0:
            outcome = "WIN"
        else:
            outcome = "LOSS"
        
        # Update record
        cursor.execute('''
            UPDATE patterns 
            SET exit_date = ?,
                exit_price = ?,
                return_pct = ?,
                hit_target = ?,
                hit_stop = ?,
                hold_days = ?,
                outcome = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (exit_date, exit_price, return_pct, 
              1 if hit_target else 0, 1 if hit_stop else 0, 
              hold_days, outcome, pattern_id))
        
        conn.commit()
        conn.close()
    
    def get_pattern_stats(self, pattern_type: Optional[PatternType] = None) -> List[PatternStats]:
        """Get statistics for patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if pattern_type:
            cursor.execute('''
                SELECT * FROM pattern_performance 
                WHERE pattern_type = ?
            ''', (pattern_type.value,))
        else:
            cursor.execute('SELECT * FROM pattern_performance')
        
        results = []
        for row in cursor.fetchall():
            stats = PatternStats(
                pattern_type=PatternType(row[0]),
                total_instances=row[1],
                closed_instances=row[2],
                win_count=row[3],
                loss_count=row[4],
                scratch_count=row[2] - row[3] - row[4],
                win_rate=row[5] or 0,
                avg_return=row[6] or 0,
                avg_winner=row[7] or 0,
                avg_loser=row[8] or 0,
                avg_hold_days=row[9] or 0,
                best_return=row[10] or 0,
                worst_return=row[11] or 0
            )
            results.append(stats)
        
        conn.close()
        return results
    
    def get_convergence_boost_stats(self, pattern_type: PatternType) -> Dict:
        """
        Analyze how convergence (multiple signals) affects win rate
        Returns dict with win rates for single signal vs multiple signals
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Single signal only (scanner)
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN outcome = 'WIN' THEN 1 END) * 100.0 / 
                    NULLIF(COUNT(CASE WHEN outcome IS NOT NULL THEN 1 END), 0) as win_rate
            FROM patterns
            WHERE pattern_type = ?
              AND had_institutional_signal = 0
              AND had_catalyst_signal = 0
              AND had_sector_signal = 0
              AND outcome IS NOT NULL
        ''', (pattern_type.value,))
        
        single_signal_wr = cursor.fetchone()[0] or 0
        
        # With institutional signal
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN outcome = 'WIN' THEN 1 END) * 100.0 / 
                    NULLIF(COUNT(CASE WHEN outcome IS NOT NULL THEN 1 END), 0) as win_rate
            FROM patterns
            WHERE pattern_type = ?
              AND had_institutional_signal = 1
              AND outcome IS NOT NULL
        ''', (pattern_type.value,))
        
        institutional_wr = cursor.fetchone()[0] or 0
        
        # With catalyst signal
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN outcome = 'WIN' THEN 1 END) * 100.0 / 
                    NULLIF(COUNT(CASE WHEN outcome IS NOT NULL THEN 1 END), 0) as win_rate
            FROM patterns
            WHERE pattern_type = ?
              AND had_catalyst_signal = 1
              AND outcome IS NOT NULL
        ''', (pattern_type.value,))
        
        catalyst_wr = cursor.fetchone()[0] or 0
        
        # Multiple signals (2+)
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN outcome = 'WIN' THEN 1 END) * 100.0 / 
                    NULLIF(COUNT(CASE WHEN outcome IS NOT NULL THEN 1 END), 0) as win_rate
            FROM patterns
            WHERE pattern_type = ?
              AND (had_institutional_signal + had_catalyst_signal + had_sector_signal) >= 2
              AND outcome IS NOT NULL
        ''', (pattern_type.value,))
        
        convergence_wr = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'single_signal_win_rate': single_signal_wr,
            'with_institutional_win_rate': institutional_wr,
            'with_catalyst_win_rate': catalyst_wr,
            'convergence_win_rate': convergence_wr,
            'convergence_boost': convergence_wr - single_signal_wr if single_signal_wr > 0 else 0
        }


# =============================================================================
# PATTERN SERVICE (Main API)
# =============================================================================

class PatternService:
    """
    Main pattern tracking service
    Integrates with convergence engine
    """
    
    def __init__(self, db_path: str = "data/patterns.db"):
        self.db = PatternDatabase(db_path)
    
    def record_pattern(self, ticker: str, pattern_type: PatternType, 
                      entry_price: float, stop_price: float, target_price: float,
                      distance_from_high: float, volume_ratio: float, rsi: Optional[float],
                      had_institutional: bool = False, had_catalyst: bool = False,
                      had_sector: bool = False, convergence_score: Optional[int] = None) -> int:
        """Record a new pattern detection"""
        pattern = PatternInstance(
            id=None,
            ticker=ticker,
            pattern_type=pattern_type,
            detected_date=datetime.now().strftime('%Y-%m-%d'),
            entry_price=entry_price,
            stop_price=stop_price,
            target_price=target_price,
            distance_from_high=distance_from_high,
            volume_ratio=volume_ratio,
            rsi=rsi,
            exit_date=None,
            exit_price=None,
            return_pct=None,
            hit_target=None,
            hit_stop=None,
            hold_days=None,
            outcome=None,
            had_institutional_signal=had_institutional,
            had_catalyst_signal=had_catalyst,
            had_sector_signal=had_sector,
            convergence_score=convergence_score
        )
        
        return self.db.add_pattern(pattern)
    
    def close_pattern(self, pattern_id: int, exit_price: float,
                     hit_target: bool = False, hit_stop: bool = False):
        """Record pattern outcome"""
        exit_date = datetime.now().strftime('%Y-%m-%d')
        self.db.update_outcome(pattern_id, exit_date, exit_price, hit_target, hit_stop)
    
    def get_pattern_signal_for_convergence(self, ticker: str, pattern_type: PatternType) -> Optional[Dict]:
        """
        Get pattern reliability signal for convergence
        Returns historical win rate as signal score
        """
        stats = self.db.get_pattern_stats(pattern_type)
        
        if not stats or stats[0].closed_instances < 5:
            # Not enough data
            return None
        
        stat = stats[0]
        
        # Score based on win rate (0-100)
        score = int(stat.win_rate)
        
        # Adjust based on sample size
        if stat.closed_instances < 20:
            score = int(score * 0.8)  # Reduce confidence for small samples
        
        reasoning = f"{pattern_type.value} pattern: {stat.win_rate:.1f}% win rate ({stat.closed_instances} trades)"
        
        return {
            'score': score,
            'reasoning': reasoning,
            'data': {
                'pattern_type': pattern_type.value,
                'win_rate': stat.win_rate,
                'total_trades': stat.closed_instances,
                'avg_return': stat.avg_return,
                'avg_hold_days': stat.avg_hold_days
            }
        }
    
    def get_all_stats(self) -> List[PatternStats]:
        """Get statistics for all patterns"""
        return self.db.get_pattern_stats()
    
    def analyze_convergence_effect(self, pattern_type: PatternType) -> Dict:
        """Analyze how convergence affects pattern performance"""
        return self.db.get_convergence_boost_stats(pattern_type)


# =============================================================================
# FORMATTING
# =============================================================================

def format_pattern_report(stats: List[PatternStats]) -> str:
    """Format pattern statistics as report"""
    lines = []
    lines.append("\n🎯 PATTERN PERFORMANCE REPORT")
    lines.append("=" * 60)
    
    for stat in stats:
        lines.append(f"\n{stat.pattern_type.value}:")
        lines.append(f"  Trades: {stat.closed_instances} closed / {stat.total_instances} total")
        lines.append(f"  Win Rate: {stat.win_rate:.1f}% ({stat.win_count}W-{stat.loss_count}L-{stat.scratch_count}S)")
        lines.append(f"  Avg Return: {stat.avg_return:+.1f}%")
        lines.append(f"  Avg Winner: {stat.avg_winner:+.1f}% | Avg Loser: {stat.avg_loser:+.1f}%")
        lines.append(f"  Avg Hold: {stat.avg_hold_days:.1f} days")
        lines.append(f"  Best: {stat.best_return:+.1f}% | Worst: {stat.worst_return:+.1f}%")
    
    return "\n".join(lines)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == '__main__':
    print("🎯 PATTERN DATABASE TEST")
    print("="*60)
    
    service = PatternService(db_path='data/patterns_test.db')
    
    # Add test patterns (wounded prey historical data)
    print("\n📝 Adding historical wounded prey patterns...")
    
    # Historical validated wounded prey: 68.8% win rate
    test_patterns = [
        # Winners (68.8% = ~70 of these)
        *[(f"TEST{i}", PatternType.WOUNDED_PREY, 100, 85, 120, -35, 2.1, 35, True, False, False, 65) 
          for i in range(1, 71)],
        # Losers (~30 of these)
        *[(f"TEST{i}", PatternType.WOUNDED_PREY, 100, 85, 120, -35, 1.8, 40, False, False, False, 50)
          for i in range(71, 101)]
    ]
    
    pattern_ids = []
    for ticker, ptype, entry, stop, target, dist, vol, rsi, inst, cat, sec, conv in test_patterns:
        pid = service.record_pattern(ticker, ptype, entry, stop, target, dist, vol, rsi, inst, cat, sec, conv)
        pattern_ids.append(pid)
    
    print(f"✅ Added {len(pattern_ids)} patterns")
    
    # Close patterns with outcomes (simulate wins/losses)
    print("\n📊 Simulating outcomes...")
    for i, pid in enumerate(pattern_ids):
        if i < 70:  # Winners
            service.close_pattern(pid, exit_price=115, hit_target=False)
        else:  # Losers
            service.close_pattern(pid, exit_price=90, hit_stop=True)
    
    print("✅ Outcomes recorded")
    
    # Get stats
    stats = service.get_all_stats()
    print(format_pattern_report(stats))
    
    # Test convergence signal
    print("\n\n🧠 CONVERGENCE INTEGRATION TEST:")
    print("="*60)
    
    signal = service.get_pattern_signal_for_convergence('SMCI', PatternType.WOUNDED_PREY)
    if signal:
        print(f"\nWOUNDED_PREY pattern signal: {signal['score']}/100")
        print(f"Reasoning: {signal['reasoning']}")
    
    print("\n" + "="*60)
    print("✅ Pattern database test complete")
