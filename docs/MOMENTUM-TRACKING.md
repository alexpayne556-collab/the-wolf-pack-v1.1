# 🔥 MOMENTUM TRACKING - Sustained Runner Detection

## What This Does

The Wolf Brain now tracks **SUSTAINED MOMENTUM** across multiple premarket scans.

**KEY INSIGHT**: Real runners appear in MULTIPLE scans with INCREASING or HOLDING volume. Flash-in-the-pan gaps fade. Sustained gaps with volume = REAL STRENGTH.

---

## How It Works

### 1. **Track Across Scans**

Every time the system scans (4 AM, 5 AM, 5:30 AM, etc.), it tracks:
- Which tickers are gapping
- Current gap %
- Volume ratio
- Classification (RUNNER vs FADER)

### 2. **Identify Sustained Runners**

After 2+ scans, the system checks:
- ✅ **Gap Holding**: Latest gap ≥ 85% of first gap (allowing 15% fade)
- ✅ **Volume Sustained**: Latest volume ≥ 90% of first volume (not dying)
- ✅ **Classification**: Still marked as RUNNER (not a fader)

If all 3 checks pass → **SUSTAINED RUNNER** ⚡

### 3. **Prioritize at 5 AM**

By 5 AM scan, you'll see:
```
🔥 SUSTAINED RUNNERS (3 tickers with momentum):
   AQST: Seen in 2 scans | HOLDING gap | BUILDING volume
   PHAR: Seen in 2 scans | HOLDING gap | SUSTAINED volume
   IRON: Seen in 2 scans | HOLDING gap | BUILDING volume
```

**These are NOT just the highest % gainer** - they're the ones showing CONSISTENT STRENGTH.

---

## What You'll See

### In Real-Time Logs

```
⏰ SCHEDULED SCAN: 4:00 AM
Found 8 stocks gapping 3%+
🔥 MOMENTUM TRACKING: Tracked 8 tickers at 4:00 AM

⏰ SCHEDULED SCAN: 5:00 AM
Found 12 stocks gapping 3%+
🔥 SUSTAINED RUNNERS (3 tickers with momentum):
   AQST: Seen in 2 scans | HOLDING gap | BUILDING volume
   BTAI: Seen in 2 scans | HOLDING gap | SUSTAINED volume
   GLSI: Seen in 2 scans | HOLDING gap | BUILDING volume

⚡ These are the REAL MOVERS - not flash-in-the-pan
```

### In Premarket Reports

File: `data/wolf_brain/PREMARKET_SCANS_20260122.txt`

```
======================================================================
⏰ 5:00 AM SCAN - 2026-01-22 05:00:15
======================================================================
Found 12 stocks gapping 3%+:

   1. 🚀 AQST   | Gap: +12.3% | Vol:  4.2x | Float: 23M ⚡ SUSTAINED
   2. 🔥 BTAI   | Gap:  +8.7% | Vol:  3.1x | Float: 15M ⚡ SUSTAINED
   3. 🔥 PHAR   | Gap:  +7.2% | Vol:  2.8x | Float: 45M
   4. 📈 GLSI   | Gap:  +5.1% | Vol:  2.2x | Float: 12M ⚡ SUSTAINED

🔥 SUSTAINED RUNNERS (appearing in multiple scans with strength):
   • AQST: 2 scans | Gap: 12.3% | Vol: 4.2x | HOLDING
   • BTAI: 2 scans | Gap: 8.7% | Vol: 3.1x | HOLDING
   • GLSI: 2 scans | Gap: 5.1% | Vol: 2.2x | HOLDING

⚡ These are NOT flash-in-the-pan - sustained momentum = REAL STRENGTH
```

---

## Why This Matters

### OLD WAY (Just Highest % Gainer)
```
4:00 AM: SCAM up 25% (low volume, PR fluff)
5:00 AM: SCAM down to +8% (fading, no volume)
6:00 AM: SCAM flat (dead)
Result: AVOIDED ✅
```

### NEW WAY (Sustained Runners)
```
4:00 AM: AQST up 10% (PDUFA news, 3x volume)
5:00 AM: AQST up 12% (volume building to 4x) ⚡ SUSTAINED
6:00 AM: AQST up 15% (volume 5x) ⚡ SUSTAINED
Result: REAL RUNNER - Enter at open 🚀
```

---

## What Gets Filtered Out

❌ **Flash Gaps** - Up 30% at 4 AM, fading by 5 AM
❌ **Low Volume Pops** - Gap but no volume follow-through
❌ **PR Fluff** - Gap on nothing, classified as FADER

✅ **Real Runners** - Gap holding, volume building, news catalyst

---

## Technical Details

### Code Location
`src/wolf_brain/autonomous_brain.py` - Lines 280-290, 1080-1160, 2360-2380

### Database
Momentum data stored in memory (`self.momentum_tracker`), not persisted to DB yet.

### Data Structure
```python
momentum_tracker = {
    'AQST': [
        {
            'time': '4:00 AM',
            'timestamp': datetime(...),
            'gap_pct': 10.2,
            'volume_ratio': 3.1,
            'price': 3.36,
            'classification': 'RUNNER'
        },
        {
            'time': '5:00 AM',
            'timestamp': datetime(...),
            'gap_pct': 12.3,
            'volume_ratio': 4.2,
            'price': 3.42,
            'classification': 'RUNNER'
        }
    ]
}

sustained_runners = [
    {
        'ticker': 'AQST',
        'first_seen': '4:00 AM',
        'scans_appeared': 2,
        'gap_trend': 'HOLDING',
        'volume_trend': 'BUILDING',
        'latest_data': {...}
    }
]
```

---

## Commands

All automatic - no commands needed!

System tracks momentum on every scheduled scan:
- 4:00 AM - First scan (baseline)
- 5:00 AM - 2nd scan (sustained runners detected)
- 5:30 AM - 3rd scan (momentum confirmation)
- 6:00 AM - 4th scan (volume peak)
- 6:30 AM - 5th scan (prime time)
- 7:00 AM - 6th scan (peak action)
- 7:30 AM - 7th scan (final confirmation)

By 5 AM, you'll know which runners have **sustained strength**.

---

## Integration with Auto-Execution

At 9:30 AM market open, Wolf Brain prioritizes:
1. ⚡ **SUSTAINED RUNNERS** (appeared in 2+ scans with strength)
2. 🧬 **PDUFA PLAYS** (in 7-14 day window)
3. 🔥 **TOP CONFIDENCE SETUPS** (70%+ from Fenrir)

Sustained runners get **EXTRA WEIGHT** in auto-execution decisions.

---

## Example Morning Workflow

```
4:00 AM
-------
Scan: 15 tickers gapping
Runners: AQST, BTAI, PHAR, GLSI, IRON
Faders: SCAM, PUMP, JUNK

5:00 AM
-------
Scan: 18 tickers gapping (3 new, 12 holding)
Sustained: AQST, BTAI, GLSI (gap holding, volume building)
Faded: PHAR (volume dying), IRON (gap fading)
New: OCUL (FDA news just hit)

6:00 AM
-------
Scan: 22 tickers
Sustained: AQST (3 scans), BTAI (3 scans), GLSI (3 scans), OCUL (2 scans)
Faded: Previous faders now dead

7:00 AM
-------
Fenrir analyzes sustained runners
Top Pick: AQST (4 scans sustained, PDUFA catalyst, low float)

9:30 AM
-------
AUTO-EXECUTE: AQST at market open (70%+ confidence + sustained momentum)
```

---

## Future Enhancements

- [ ] Persist momentum tracking to database
- [ ] Track momentum across multiple days (pre-PDUFA runners)
- [ ] Add "acceleration" detection (gap % increasing each scan)
- [ ] Volume profile analysis (morning peak vs sustained)
- [ ] Integration with L2 data (if available)

---

## Status

✅ **LIVE** - System running with momentum tracking
✅ **Tested** - Validated with test scans
✅ **Integrated** - Works with existing premarket scanner
✅ **Documented** - This file + code comments

---

**The Wolf Pack hunts at dawn. Now we know which prey is REALLY worth chasing.** 🐺
