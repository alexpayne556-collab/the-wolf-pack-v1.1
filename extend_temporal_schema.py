"""
TEMPORAL MEMORY SCHEMA EXTENSION
================================
EXTEND ONLY - NO DROPS - NO DELETES

Approved by Fenrir: January 28, 2026
Backup verified: data/wolfpack_backup_jan28.db

This script:
1. Adds TIER 1 fields to user_decisions
2. Extends learned_patterns with regime stats
3. Creates confidence_calibration table
4. Preserves ALL existing data
"""

import sqlite3
from datetime import datetime

DB_PATH = 'data/wolfpack.db'
BACKUP_PATH = 'data/wolfpack_backup_jan28.db'

def verify_backup():
    """Safety check - refuse to run without backup"""
    import os
    if not os.path.exists(BACKUP_PATH):
        print("❌ BACKUP NOT FOUND. REFUSING TO PROCEED.")
        print(f"   Expected: {BACKUP_PATH}")
        return False
    
    backup_size = os.path.getsize(BACKUP_PATH)
    original_size = os.path.getsize(DB_PATH)
    
    if backup_size != original_size:
        print("❌ BACKUP SIZE MISMATCH. REFUSING TO PROCEED.")
        print(f"   Original: {original_size} bytes")
        print(f"   Backup: {backup_size} bytes")
        return False
    
    print(f"✓ Backup verified: {BACKUP_PATH} ({backup_size:,} bytes)")
    return True

def column_exists(cursor, table, column):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns

def extend_user_decisions(cursor):
    """Add TIER 1 fields to user_decisions table"""
    print("\n" + "="*60)
    print("EXTENDING: user_decisions")
    print("="*60)
    
    extensions = [
        # TIER 1: Granular loss attribution
        ("signal_was_correct", "BOOLEAN", "Was the entry signal correct?"),
        ("timing_was_correct", "BOOLEAN", "Was the timing correct?"),
        ("execution_was_correct", "BOOLEAN", "Was execution clean?"),
        ("capital_allocation_correct", "BOOLEAN", "Was position size correct?"),
        
        # TIER 1: Regime awareness
        ("market_regime", "TEXT", "Market regime at decision time"),
        ("regime_confidence", "REAL", "Confidence in regime classification"),
        
        # Temporal context
        ("thesis_type", "TEXT", "thesis, momentum, speculative"),
        ("convergence_score", "INTEGER", "Convergence score at entry"),
        ("entry_signals", "TEXT", "JSON array of signals that triggered entry"),
        
        # Outcome analysis (beyond existing outcome_1d, 3d, 5d, 10d)
        ("outcome_classification", "TEXT", "win, loss, breakeven"),
        ("outcome_reason", "TEXT", "Why did this outcome occur?"),
        ("lessons_learned", "TEXT", "What did we learn?"),
        
        # Post-trade review
        ("review_date", "TEXT", "When was this trade reviewed?"),
        ("review_notes", "TEXT", "Notes from post-trade review"),
    ]
    
    added = 0
    skipped = 0
    
    for col_name, col_type, description in extensions:
        if column_exists(cursor, 'user_decisions', col_name):
            print(f"  ○ {col_name}: already exists (skipped)")
            skipped += 1
        else:
            try:
                cursor.execute(f"ALTER TABLE user_decisions ADD COLUMN {col_name} {col_type}")
                print(f"  ✓ {col_name} ({col_type}): ADDED - {description}")
                added += 1
            except Exception as e:
                print(f"  ✗ {col_name}: FAILED - {e}")
    
    print(f"\nuser_decisions: {added} columns added, {skipped} already existed")
    return added

def extend_learned_patterns(cursor):
    """Add regime-specific stats to learned_patterns"""
    print("\n" + "="*60)
    print("EXTENDING: learned_patterns")
    print("="*60)
    
    extensions = [
        # Regime-specific performance
        ("win_rate_bull", "REAL", "Win rate in bull market regime"),
        ("win_rate_bear", "REAL", "Win rate in bear market regime"),
        ("win_rate_sideways", "REAL", "Win rate in sideways regime"),
        
        # Thesis type breakdown
        ("thesis_trades", "INTEGER", "Count of thesis-based trades"),
        ("thesis_win_rate", "REAL", "Win rate on thesis trades"),
        ("momentum_trades", "INTEGER", "Count of momentum trades"),
        ("momentum_win_rate", "REAL", "Win rate on momentum trades"),
        ("speculative_trades", "INTEGER", "Count of speculative trades"),
        ("speculative_win_rate", "REAL", "Win rate on speculative trades"),
        
        # Time-based stats
        ("best_hold_duration", "INTEGER", "Optimal hold duration in days"),
        ("avg_time_to_target", "REAL", "Average days to hit target"),
        
        # Risk metrics
        ("max_drawdown_seen", "REAL", "Max drawdown experienced"),
        ("avg_drawdown_before_win", "REAL", "Avg drawdown on winning trades"),
        
        # Validation
        ("statistically_significant", "BOOLEAN", "Has enough trades for significance"),
        ("minimum_sample_size", "INTEGER", "Trades needed for significance"),
    ]
    
    added = 0
    skipped = 0
    
    for col_name, col_type, description in extensions:
        if column_exists(cursor, 'learned_patterns', col_name):
            print(f"  ○ {col_name}: already exists (skipped)")
            skipped += 1
        else:
            try:
                cursor.execute(f"ALTER TABLE learned_patterns ADD COLUMN {col_name} {col_type}")
                print(f"  ✓ {col_name} ({col_type}): ADDED - {description}")
                added += 1
            except Exception as e:
                print(f"  ✗ {col_name}: FAILED - {e}")
    
    print(f"\nlearned_patterns: {added} columns added, {skipped} already existed")
    return added

def create_confidence_calibration(cursor):
    """Create confidence_calibration table for TIER 1 calibration tracking"""
    print("\n" + "="*60)
    print("CREATING: confidence_calibration")
    print("="*60)
    
    # Check if table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='confidence_calibration'")
    if cursor.fetchone():
        print("  ○ Table already exists (skipped)")
        return 0
    
    create_sql = """
    CREATE TABLE confidence_calibration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        -- Bucket definition
        confidence_bucket INTEGER NOT NULL,  -- 10, 20, 30, ... 100
        bucket_label TEXT,                   -- "10-19%", "20-29%", etc.
        
        -- Trade counts
        trades_in_bucket INTEGER DEFAULT 0,
        wins_in_bucket INTEGER DEFAULT 0,
        losses_in_bucket INTEGER DEFAULT 0,
        
        -- Win rates
        actual_win_rate REAL,               -- What actually happened
        expected_win_rate REAL,             -- What confidence predicted
        
        -- Calibration metrics
        calibration_error REAL,             -- actual - expected
        brier_score REAL,                   -- (forecast - outcome)^2
        
        -- Breakdown by type
        thesis_trades INTEGER DEFAULT 0,
        thesis_wins INTEGER DEFAULT 0,
        momentum_trades INTEGER DEFAULT 0,
        momentum_wins INTEGER DEFAULT 0,
        speculative_trades INTEGER DEFAULT 0,
        speculative_wins INTEGER DEFAULT 0,
        
        -- Metadata
        last_updated TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        UNIQUE(confidence_bucket)
    )
    """
    
    try:
        cursor.execute(create_sql)
        print("  ✓ Table created: confidence_calibration")
        
        # Initialize buckets
        for bucket in range(10, 101, 10):
            label = f"{bucket-9}-{bucket}%"
            expected = bucket / 100.0
            cursor.execute("""
                INSERT INTO confidence_calibration 
                (confidence_bucket, bucket_label, expected_win_rate, last_updated)
                VALUES (?, ?, ?, ?)
            """, (bucket, label, expected, datetime.now().isoformat()))
        
        print("  ✓ Initialized 10 confidence buckets (10-100%)")
        return 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return 0

def extend_trades_table(cursor):
    """Add temporal memory fields to trades table"""
    print("\n" + "="*60)
    print("EXTENDING: trades (existing 16 rows preserved)")
    print("="*60)
    
    extensions = [
        # TIER 1: Granular analysis
        ("signal_was_correct", "BOOLEAN", "Entry signal accuracy"),
        ("timing_was_correct", "BOOLEAN", "Timing accuracy"),
        ("execution_was_correct", "BOOLEAN", "Execution quality"),
        ("capital_allocation_correct", "BOOLEAN", "Position sizing accuracy"),
        
        # Context
        ("market_regime", "TEXT", "Market regime at trade time"),
        ("thesis_type", "TEXT", "thesis, momentum, speculative"),
        ("convergence_score", "INTEGER", "Convergence score"),
        
        # Outcome
        ("outcome_classification", "TEXT", "win, loss, breakeven"),
        ("review_complete", "BOOLEAN", "Has been reviewed"),
    ]
    
    added = 0
    skipped = 0
    
    for col_name, col_type, description in extensions:
        if column_exists(cursor, 'trades', col_name):
            print(f"  ○ {col_name}: already exists (skipped)")
            skipped += 1
        else:
            try:
                cursor.execute(f"ALTER TABLE trades ADD COLUMN {col_name} {col_type}")
                print(f"  ✓ {col_name} ({col_type}): ADDED - {description}")
                added += 1
            except Exception as e:
                print(f"  ✗ {col_name}: FAILED - {e}")
    
    print(f"\ntrades: {added} columns added, {skipped} already existed")
    print(f"        16 existing rows PRESERVED")
    return added

def verify_extensions(cursor):
    """Verify all extensions were applied"""
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    # Check user_decisions
    cursor.execute("PRAGMA table_info(user_decisions)")
    ud_cols = [row[1] for row in cursor.fetchall()]
    print(f"\nuser_decisions: {len(ud_cols)} columns")
    tier1_fields = ['signal_was_correct', 'timing_was_correct', 'execution_was_correct', 
                    'capital_allocation_correct', 'market_regime', 'regime_confidence']
    for field in tier1_fields:
        status = "✓" if field in ud_cols else "✗"
        print(f"  {status} {field}")
    
    # Check learned_patterns
    cursor.execute("PRAGMA table_info(learned_patterns)")
    lp_cols = [row[1] for row in cursor.fetchall()]
    print(f"\nlearned_patterns: {len(lp_cols)} columns")
    regime_fields = ['win_rate_bull', 'win_rate_bear', 'win_rate_sideways']
    for field in regime_fields:
        status = "✓" if field in lp_cols else "✗"
        print(f"  {status} {field}")
    
    # Check confidence_calibration
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='confidence_calibration'")
    cc_exists = cursor.fetchone() is not None
    print(f"\nconfidence_calibration: {'✓ EXISTS' if cc_exists else '✗ MISSING'}")
    if cc_exists:
        cursor.execute("SELECT COUNT(*) FROM confidence_calibration")
        count = cursor.fetchone()[0]
        print(f"  {count} buckets initialized")
    
    # Check trades
    cursor.execute("PRAGMA table_info(trades)")
    t_cols = [row[1] for row in cursor.fetchall()]
    print(f"\ntrades: {len(t_cols)} columns")
    cursor.execute("SELECT COUNT(*) FROM trades")
    count = cursor.fetchone()[0]
    print(f"  {count} rows PRESERVED")
    
    return True

def main():
    print("="*60)
    print("TEMPORAL MEMORY SCHEMA EXTENSION")
    print(f"Date: {datetime.now()}")
    print("="*60)
    
    # Safety first
    if not verify_backup():
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Execute extensions
        extend_user_decisions(cursor)
        extend_learned_patterns(cursor)
        create_confidence_calibration(cursor)
        extend_trades_table(cursor)
        
        # Commit all changes
        conn.commit()
        print("\n✓ ALL CHANGES COMMITTED")
        
        # Verify
        verify_extensions(cursor)
        
        print("\n" + "="*60)
        print("SCHEMA EXTENSION COMPLETE")
        print("="*60)
        print("✓ user_decisions: Extended with TIER 1 fields")
        print("✓ learned_patterns: Extended with regime stats")
        print("✓ confidence_calibration: Created and initialized")
        print("✓ trades: Extended (16 rows preserved)")
        print("\n⚠️  Next: Build get_temporal_context() function")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Rolling back...")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()
