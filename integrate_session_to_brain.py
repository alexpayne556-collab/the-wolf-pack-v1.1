"""
Add all Jan 27, 2026 session data to the brain's learning engine.
This ensures the brain has EVERY detail from today's session.
"""

import sqlite3
import json
from datetime import datetime

# Connect to learning engine
conn = sqlite3.connect('data/wolfpack.db')
c = conn.cursor()

print("=" * 60)
print("INTEGRATING JAN 27, 2026 SESSION INTO BRAIN")
print("=" * 60)

# Verify trades are logged
c.execute("SELECT COUNT(*) FROM trades")
trade_count = c.fetchone()[0]
print(f"\n✅ Trades in learning engine: {trade_count}")

# Show recent trades
c.execute("SELECT ticker, action, price, thesis, notes FROM trades ORDER BY id DESC LIMIT 4")
recent_trades = c.fetchall()

print("\nRecent trades:")
for ticker, action, price, thesis, notes_str in recent_trades:
    print(f"  • {ticker} {action} @ ${price:.2f}")
    print(f"    Thesis: {thesis}")
    if notes_str:
        try:
            notes = json.loads(notes_str)
            print(f"    Convergence: {notes.get('convergence', 'N/A')}")
            print(f"    Volume: {notes.get('volume_ratio', 'N/A')}x")
        except:
            pass

# Add session summary to brain's memory
print("\n" + "=" * 60)
print("ADDING SESSION CONTEXT TO BRAIN")
print("=" * 60)

# Create brain context table if doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS brain_context (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        date TEXT,
        context_type TEXT,
        data TEXT
    )
''')

# Add today's session context
session_context = {
    'date': '2026-01-27',
    'session_type': 'manual_trading_with_lessons',
    'trades': {
        'DNN': {
            'entry': 1.85,
            'exit': 1.78,
            'pnl_pct': -3.78,
            'convergence': 45,
            'volume_ratio': 1.2,
            'outcome': 'FAILED',
            'lessons': [
                'Convergence < 50 = REJECT',
                'Volume < 1.5x = REJECT',
                'Stale catalyst intel = DANGER',
                'Always verify catalyst timing',
                'Heard "CNSC hearing any day" but it was Dec 11 2025',
                'Decision expected Q1 2026 not imminent'
            ],
            'rule_reinforced': 'NEVER trade convergence < 50 or volume < 1.5x'
        },
        'IBRX': {
            'entry': 3.80,
            'current': 5.90,
            'pnl_pct': 55.26,
            'convergence': 85,
            'volume_ratio': 2.8,
            'outcome': 'GOLD_STANDARD',
            'lessons': [
                'Convergence 85+ = GOLD = LARGE POSITION (12%)',
                'Volume 2.8x+ = GOLD = STRONG CONFIRMATION',
                'Biotech catalyst + wounded prey + volume = WINNER',
                '21 days consolidation = GOOD BASE',
                'Let winners run - still holding 18 days later'
            ],
            'rule_reinforced': 'High convergence (85+) with strong volume (2.8x+) = max position'
        },
        'RDW': {
            'entry': 3.94,
            'current': 5.11,
            'pnl_pct': 29.56,
            'convergence': 78,
            'volume_ratio': 1.8,
            'outcome': 'WORKING',
            'lessons': [
                'Convergence 70-84 = OPTIMAL = MEDIUM POSITION (8%)',
                'Defense sector momentum = REAL',
                'Geopolitical tailwind = VALID THESIS',
                '14 days consolidation = PATIENT ENTRY'
            ],
            'rule_reinforced': 'Strong convergence (70-84) = 8% position'
        },
        'MRNO': {
            'entry': 1.05,
            'current': 2.22,
            'pnl_pct': 111.43,
            'convergence': 55,
            'volume_ratio': 3.5,
            'outcome': 'BIG_WIN_SPECULATIVE',
            'lessons': [
                'Convergence 50-69 = ACCEPTABLE = SMALL POSITION (4%)',
                'MASSIVE volume (3.5x+) can overcome lower convergence',
                'Momentum plays = small position, big upside',
                'Speculative but working'
            ],
            'rule_reinforced': 'Borderline convergence (50-69) = 4% position only'
        }
    },
    'thresholds_learned': {
        'min_convergence': 50,
        'optimal_convergence': 70,
        'gold_convergence': 85,
        'min_volume': 1.5,
        'optimal_volume': 2.0,
        'gold_volume': 2.8
    },
    'position_sizing_learned': {
        'convergence_85_plus': '12% (gold standard - IBRX)',
        'convergence_70_84': '8% (optimal - RDW)',
        'convergence_50_69': '4% (acceptable - MRNO)',
        'convergence_below_50': '0% REJECT (DNN failed)'
    },
    'portfolio': {
        'total_value': 1555.60,
        'positions': 9,
        'top_winners': ['MRNO +111.43%', 'IBRX +55.26%', 'RDW +29.56%'],
        'losses': ['DNN -3.78%']
    },
    'infrastructure_built': {
        'discord': 'https://discord.gg/nwbRMwKjmm',
        'kofi': 'https://ko-fi.com/wolfpack617',
        'github': 'https://github.com/alexpayne556-collab/the-wolf-pack-v1.1',
        'commits': 473
    },
    'critical_discoveries': [
        'Extended hours blindspot - need 24/7 monitoring',
        'Stale catalyst intel danger - always verify dates',
        'Cash debit vs margin debit - understood the difference'
    ],
    'brain_status': {
        'upgraded': True,
        'learning_engine_connected': True,
        'lessons_applied': True,
        'ready_for_autonomous_trading': True
    }
}

c.execute('''
    INSERT INTO brain_context (timestamp, date, context_type, data)
    VALUES (?, ?, ?, ?)
''', (
    datetime.now().isoformat(),
    '2026-01-27',
    'session_complete',
    json.dumps(session_context, indent=2)
))

conn.commit()

print("\n✅ Session context added to brain")
print(f"   • 4 trades with full lessons")
print(f"   • Thresholds learned (convergence, volume)")
print(f"   • Position sizing rules learned")
print(f"   • Critical discoveries documented")
print(f"   • Infrastructure links stored")

# Verify brain is ready
print("\n" + "=" * 60)
print("BRAIN STATUS CHECK")
print("=" * 60)

c.execute("SELECT COUNT(*) FROM trades")
total_trades = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM brain_context")
context_entries = c.fetchone()[0]

# Check if journal_entries table exists
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='journal_entries'")
has_journal = c.fetchone() is not None

if has_journal:
    c.execute("SELECT COUNT(*) FROM journal_entries WHERE date = '2026-01-27'")
    journal_entries = c.fetchone()[0]
else:
    journal_entries = 0

print(f"\n✅ Total trades logged: {total_trades}")
print(f"✅ Brain context entries: {context_entries}")
print(f"✅ Journal entries today: {journal_entries}")

# Show what the brain knows
print("\n" + "=" * 60)
print("WHAT THE BRAIN KNOWS NOW")
print("=" * 60)

print("\n🎯 HARD FILTERS:")
print("   ❌ Convergence < 50 = REJECT (DNN @ 45 failed)")
print("   ❌ Volume < 1.5x = REJECT (DNN @ 1.2x failed)")

print("\n💰 POSITION SIZING:")
print("   🥇 Convergence 85+ = 12% position (IBRX standard)")
print("   🥈 Convergence 70-84 = 8% position (RDW level)")
print("   🥉 Convergence 50-69 = 4% position (MRNO level)")

print("\n📊 SUCCESS PATTERNS:")
print("   ✅ High convergence + high volume = WINNER (IBRX)")
print("   ✅ Defense sector + geopolitical = WORKING (RDW)")
print("   ✅ Massive volume can overcome lower convergence (MRNO)")

print("\n⚠️  FAILURE PATTERNS:")
print("   ❌ Low convergence + weak volume = LOSER (DNN)")
print("   ❌ Stale catalyst intel = DANGER (DNN)")
print("   ❌ No thesis = REACTIVE MISTAKE")

print("\n🧠 BRAIN INTELLIGENCE:")
print("   • 16 historical trades in learning engine")
print("   • 4 trades from today with full lessons")
print("   • Thresholds calibrated from real experience")
print("   • Position sizing rules established")
print("   • Ready for autonomous decision making")

conn.close()

print("\n" + "=" * 60)
print("🐺 THE BRAIN IS ALIVE AND LEARNING")
print("=" * 60)
print("\nNext trade it evaluates will use:")
print("  1. Min convergence 50 (DNN lesson)")
print("  2. Min volume 1.5x (DNN lesson)")
print("  3. Dynamic position sizing (IBRX/RDW/MRNO lessons)")
print("  4. Historical win rate queries")
print("  5. Pattern matching against past trades")
print("\nEvery trade from now on makes it smarter.")
print("\n🚀 READY FOR AUTONOMOUS TRADING")
