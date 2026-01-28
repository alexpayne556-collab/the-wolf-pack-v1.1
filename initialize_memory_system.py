"""
Temporal Memory - Phase 1 Database Setup
Creates the three new tables for Fenrir's memory system
"""

import sqlite3
from pathlib import Path

def create_memory_tables(db_path="wolfpack.db"):
    """Create temporal memory tables in wolfpack.db"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Creating temporal memory tables...")
    
    # Table 1: ticker_memory (OHLCV history per ticker)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticker_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date DATE NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            events TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker, date)
        )
    """)
    print("✓ ticker_memory table created")
    
    # Table 2: decision_log (our decisions with full context and outcomes)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decision_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date DATE NOT NULL,
            action TEXT NOT NULL,
            price REAL,
            quantity INTEGER,
            reasoning TEXT,
            context TEXT,
            outcome_5d REAL,
            outcome_10d REAL,
            outcome_30d REAL,
            pnl_percent REAL,
            trade_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ decision_log table created")
    
    # Table 3: pattern_library (identified patterns and their success rates)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pattern_library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_name TEXT NOT NULL,
            pattern_criteria TEXT,
            ticker TEXT,
            occurrences INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            avg_return REAL,
            avg_duration_days REAL,
            last_seen DATE,
            lesson TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ pattern_library table created")
    
    conn.commit()
    conn.close()
    print(f"\n✓ All temporal memory tables created in {db_path}")
    

def insert_jan28_trades(db_path="wolfpack.db"):
    """Insert today's trade lessons into decision_log"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\nInserting Jan 28, 2026 trade lessons...")
    
    # NTLA - Loss (no thesis)
    cursor.execute("""
        INSERT INTO decision_log (
            ticker, date, action, price, quantity, reasoning, context, 
            pnl_percent, trade_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'NTLA',
        '2026-01-28',
        'SELL',
        14.80,
        2,
        'No thesis could be stated. Rule: no thesis = exit immediately. Cannot articulate why we own it = gambling, not trading.',
        '{"market_state": "mixed", "thesis_status": "NONE", "trade_type": "no_thesis", "sector": "biotech", "catalyst": "none"}',
        -11.32,
        'no_thesis'
    ))
    print("✓ NTLA trade logged (no thesis, -11.32% loss)")
    
    # MRNO - Win (momentum)
    cursor.execute("""
        INSERT INTO decision_log (
            ticker, date, action, price, quantity, reasoning, context,
            pnl_percent, trade_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'MRNO',
        '2026-01-28',
        'SELL',
        7.92,
        3,
        'Momentum trade hit +20% profit target. Small position size because speculative. Taking profit per momentum rules - don\'t get greedy.',
        '{"market_state": "momentum", "thesis_status": "momentum_play", "trade_type": "momentum", "sector": "speculative", "catalyst": "volume_spike"}',
        9.24,
        'momentum'
    ))
    print("✓ MRNO trade logged (momentum, +9.24% win)")
    
    conn.commit()
    conn.close()
    print(f"\n✓ Trade decisions saved to {db_path}")


def insert_jan28_patterns(db_path="wolfpack.db"):
    """Insert identified patterns into pattern_library"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\nInserting identified patterns...")
    
    # Pattern 1: no_thesis_trade
    cursor.execute("""
        INSERT INTO pattern_library (
            pattern_name, pattern_criteria, ticker, occurrences, success_count,
            avg_return, last_seen, lesson
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'no_thesis_trade',
        '{"thesis": "none_stated", "reasoning": "cannot_articulate", "entry_trigger": "reactive_buying"}',
        None,
        1,
        0,
        -11.32,
        '2026-01-28',
        'No thesis = expected loss. Exit immediately when discovered.'
    ))
    print("✓ Pattern logged: no_thesis_trade (0% success rate)")
    
    # Pattern 2: momentum_small_position
    cursor.execute("""
        INSERT INTO pattern_library (
            pattern_name, pattern_criteria, ticker, occurrences, success_count,
            avg_return, last_seen, lesson
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'momentum_small_position',
        '{"trade_type": "momentum", "position_size": "1-3%", "exit_trigger": "profit_target", "target_return": "15-30%"}',
        'MRNO',
        1,
        1,
        9.24,
        '2026-01-28',
        'Small position + take profit = consistent wins on momentum'
    ))
    print("✓ Pattern logged: momentum_small_position (100% success rate)")
    
    # Pattern 3: thesis_hold_through_volatility
    cursor.execute("""
        INSERT INTO pattern_library (
            pattern_name, pattern_criteria, ticker, occurrences, success_count,
            avg_return, last_seen, lesson
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'thesis_hold_through_volatility',
        '{"thesis": "intact", "catalysts": "confirming", "trade_type": "thesis", "action": "hold"}',
        None,
        4,
        4,
        4.0,
        '2026-01-28',
        'Thesis trades held through noise = consistent green days (MU +4.85%, UUUU +6.87%, UEC +0.70%, RCAT +2.49%)'
    ))
    print("✓ Pattern logged: thesis_hold_through_volatility (100% success rate on 4 positions)")
    
    conn.commit()
    conn.close()
    print(f"\n✓ Patterns saved to {db_path}")


def verify_memory_system(db_path="wolfpack.db"):
    """Verify the temporal memory tables and data"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("TEMPORAL MEMORY SYSTEM - VERIFICATION")
    print("="*60)
    
    # Check decision_log
    cursor.execute("SELECT COUNT(*) FROM decision_log")
    decision_count = cursor.fetchone()[0]
    print(f"\n✓ decision_log: {decision_count} entries")
    
    if decision_count > 0:
        cursor.execute("SELECT ticker, action, pnl_percent, trade_type FROM decision_log ORDER BY date DESC LIMIT 5")
        for row in cursor.fetchall():
            ticker, action, pnl, trade_type = row
            print(f"  - {ticker}: {action} ({pnl:+.2f}%) [{trade_type}]")
    
    # Check pattern_library
    cursor.execute("SELECT COUNT(*) FROM pattern_library")
    pattern_count = cursor.fetchone()[0]
    print(f"\n✓ pattern_library: {pattern_count} patterns")
    
    if pattern_count > 0:
        cursor.execute("SELECT pattern_name, occurrences, success_count, avg_return FROM pattern_library")
        for row in cursor.fetchall():
            name, occur, success, avg_ret = row
            win_rate = (success / occur * 100) if occur > 0 else 0
            print(f"  - {name}: {success}/{occur} ({win_rate:.0f}% win rate, avg {avg_ret:+.2f}%)")
    
    # Check ticker_memory
    cursor.execute("SELECT COUNT(*) FROM ticker_memory")
    memory_count = cursor.fetchone()[0]
    print(f"\n✓ ticker_memory: {memory_count} entries")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✓ TEMPORAL MEMORY SYSTEM OPERATIONAL")
    print("="*60)


if __name__ == "__main__":
    print("PHASE 1: Temporal Memory Database Setup")
    print("="*60)
    
    # Create tables
    create_memory_tables()
    
    # Insert today's trades
    insert_jan28_trades()
    
    # Insert identified patterns
    insert_jan28_patterns()
    
    # Verify
    verify_memory_system()
    
    print("\n🐺 AWOOOO - Memory system initialized!")
    print("Fenrir can now learn from experience.")
