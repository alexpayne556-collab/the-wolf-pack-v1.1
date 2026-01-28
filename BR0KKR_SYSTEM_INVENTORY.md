# BR0KKR - SYSTEM INVENTORY
**What Exists and Where**  
**Date:** January 28, 2026

---

## DATABASES

### Main Database: `data/wolfpack.db` (160 KB)
**Status:** ✅ Active - This is where everything should go

**Tables (16 total):**
- `trades` (16 rows) - Historical trades
- `journal_entries` (22 rows) - Daily session logs  
- `brain_thoughts` (1 row) - Reasoning output
- `brain_context` (2 rows) - Context storage
- `user_decisions` (0 rows) - ⚠️ EMPTY - Your decision_log duplicates this
- `learned_patterns` (0 rows) - ⚠️ EMPTY - Your pattern_library duplicates this
- `investigations` (0 rows) - Research tracking
- `alerts` (0 rows) - Alert system
- `stock_state` (0 rows) - Ticker state
- `daily_records` (0 rows) - Daily market data
- `realtime_moves` (0 rows) - Intraday tracking
- `catalyst_archive` (0 rows) - Historical catalysts
- `day2_tracker` (0 rows) - Multi-day runners
- `intraday_ticks` (0 rows) - Tick data
- `daily_summary` (0 rows) - Daily summaries
- `sqlite_sequence` (4 rows) - System table

### Brain Memory Database: `data/wolf_brain/autonomous_memory.db` (152 KB)
**Status:** ✅ Active - Autonomous brain uses this

**Tables (6 total):**
- `research` (41 rows) - Ticker research
- `prepop_scans` (62 rows) - Premarket scans
- `paper_trade_ideas` (8 rows) - Paper trades
- `decisions` (0 rows) - Empty
- `learnings` (0 rows) - Empty
- `trades` (0 rows) - Empty

### YOUR Database (WRONG LOCATION): `./wolfpack.db` (24 KB)
**Status:** ❌ Isolated - Created in wrong location

**Tables (4 total):**
- `ticker_memory` (0 rows) - Your temporal price data
- `decision_log` (2 rows) - NTLA, MRNO trades
- `pattern_library` (3 rows) - 3 identified patterns
- `sqlite_sequence` (2 rows) - System table

**Action Required:** Migrate to `data/wolfpack.db`

### Other Databases
- `data/wolf_brain/memory.db` (40 KB) - Legacy, mostly empty
- `wolfpack/data/wolfpack.db` (112 KB) - Legacy/test
- Multiple others (legacy/archived)

---

## PYTHON FILES

### Root Directory (Core Scripts)

| File | Purpose | Database Used |
|------|---------|---------------|
| `fenrir_thinking_engine.py` | Brain reasoning - connects brain_config + influence_map | data/wolfpack.db |
| `autonomous_wolf_brain.py` | Legacy autonomous brain runner | Various |
| `data_fetcher.py` | Market data API wrapper | None |
| `alerter.py` | Alert/notification system | None |
| `safe_position_monitor.py` | Position tracking | wolfpack.db (wrong path) |
| `daily_journal.py` | Daily logging | data/wolfpack.db |
| `initialize_memory_system.py` | ❌ YOUR FILE - Creates temporal tables | ./wolfpack.db (WRONG) |
| `log_daily_trades.py` | ✅ YOUR FILE - Reusable logger | ./wolfpack.db (WRONG) |

### src/wolf_brain/ (Brain Components)

| File | Lines | Purpose | Temporal Data? |
|------|-------|---------|----------------|
| `brain_core.py` | 798 | Main thinking engine using Ollama LLM | ❌ No |
| `memory_system.py` | 857 | Long-term memory system | ⚠️ Uses data/wolf_brain/memory.db |
| `autonomous_brain.py` | 2978 | 24/7 autonomous trader | ❌ Logs but doesn't read history |
| `autonomous_trader.py` | ? | Alpaca trading interface | No |
| `terminal_brain.py` | ? | Terminal interface | No |
| `strategy_coordinator.py` | ? | Strategy orchestration | No |
| `wolf_pack_runner.py` | ? | Main runner - integrates components | ⚠️ No temporal analysis |

---

## INTELLIGENCE FILES (JSON)

| File | Size | Purpose |
|------|------|---------|
| `brain_config.json` | ? | 205 tickers + theses |
| `influence_map.json` | ? | Event relationship intelligence |
| `brain_methodology.json` | ? | How to think, research, learn |
| `position_management.json` | ? | When to add/hold/cut |

---

## CONNECTION MAP

```
WHAT'S CONNECTED:
==================

fenrir_thinking_engine.py
    ├── Loads: brain_config.json
    ├── Loads: influence_map.json  
    ├── Loads: brain_methodology.json
    ├── Loads: position_management.json
    └── Writes: data/wolfpack.db → brain_thoughts table

autonomous_brain.py
    └── Writes: data/wolfpack.db → trades table

daily_journal.py
    └── Writes: data/wolfpack.db → journal_entries table

memory_system.py
    └── Uses: data/wolf_brain/memory.db (SEPARATE DATABASE)


WHAT'S DISCONNECTED (ISLANDS):
================================

YOUR temporal memory tables (./wolfpack.db)
    ├── ticker_memory (0 rows)
    ├── decision_log (2 rows)  
    └── pattern_library (3 rows)
    └── ❌ NOT connected to any component

brain_core.py
    └── ❌ Doesn't read temporal context

autonomous_brain.py  
    └── ❌ Logs trades but doesn't read history before deciding

fenrir_thinking_engine.py
    └── ❌ Has reasoning but no temporal analysis
```

---

## WHAT'S MISSING FOR TEMPORAL MEMORY

### 1. Database Location ❌
- Temporal tables in wrong database
- Need to move to `data/wolfpack.db`

### 2. Schema Integration ❌
- `user_decisions` exists but missing columns
- `learned_patterns` exists but missing columns
- Need to extend existing tables, not duplicate

### 3. Data Collection ❌
- No daily price data collection (ticker_memory empty)
- No automated decision logging
- No outcome tracking (outcome_5d, outcome_10d, outcome_30d all NULL)

### 4. Brain Integration ❌
- `brain_core.py` doesn't call temporal context
- `autonomous_brain.py` doesn't read historical patterns
- `fenrir_thinking_engine.py` has no temporal analysis

### 5. Learning Loops ❌
- No pattern recognition automation
- No success rate updates
- No continuous learning

---

## IMMEDIATE NEXT STEPS

1. ✅ Audit complete
2. ⏳ Move temporal tables to `data/wolfpack.db`
3. ⏳ Extend `user_decisions` and `learned_patterns` schemas
4. ⏳ Migrate your 2 trades + 3 patterns to correct location
5. ⏳ Wire `fenrir_thinking_engine.py` first
6. ⏳ Build data collection automation
7. ⏳ Wire remaining brain components

---

**This inventory shows: System is sophisticated but temporal memory is not wired.**

**AWOOOO 🐺**
