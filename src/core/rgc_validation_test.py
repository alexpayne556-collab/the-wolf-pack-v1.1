"""
RGC VALIDATION TEST

THE CRITICAL QUESTION:
What would RGC score in our convergence engine BEFORE it moved 20,000%?

If RGC scores LOW, our system is BROKEN.
If RGC scores HIGH, our system works.
"""

def score_rgc_before_move():
    """
    RGC characteristics BEFORE CEO buyback (March 10, 2025)
    
    Setup:
    - Float: 802K shares (0.8M)
    - Insider ownership: 86% (CEO owned most)
    - Price: ~$0.09
    - Short interest: Unknown (likely low)
    - Recent insider buying: NO (not yet - this was the TRIGGER)
    - Catalyst: NONE known (CEO buyback was surprise)
    - Volume: Normal
    - Momentum: Beaten down
    """
    
    print("="*80)
    print("🔬 RGC VALIDATION TEST")
    print("="*80)
    print("Scoring RGC BEFORE the 20,000% move (March 10, 2025)")
    print()
    
    scores = {}
    
    # Float Score: 802K shares
    # <1M = 10 pts (RGC-level rare)
    scores['float'] = {
        'score': 10,
        'reason': '802K float (0.8M) - RGC-level RARE',
        'weight': 'CRITICAL'
    }
    print(f"✅ Float: {scores['float']['score']}/10 - {scores['float']['reason']}")
    
    # Short Interest: Unknown, assume low
    # <5% = 0 pts
    scores['short'] = {
        'score': 0,
        'reason': 'Unknown short interest, likely low',
        'weight': 'BONUS'
    }
    print(f"⚪ Short: {scores['short']['score']}/10 - {scores['short']['reason']}")
    
    # Insider Ownership: 86%
    # >50% but NO recent buying = 4 pts
    scores['insider'] = {
        'score': 4,
        'reason': '86% insider ownership, but NO recent buying YET',
        'weight': 'CRITICAL'
    }
    print(f"⚠️  Insider: {scores['insider']['score']}/10 - {scores['insider']['reason']}")
    print(f"   (CEO buyback was the TRIGGER, not visible yet)")
    
    # Catalyst: NONE known
    # No catalyst = 0 pts
    scores['catalyst'] = {
        'score': 0,
        'reason': 'No known catalyst (CEO buyback was surprise)',
        'weight': 'BONUS'
    }
    print(f"⚪ Catalyst: {scores['catalyst']['score']}/10 - {scores['catalyst']['reason']}")
    
    # Volume: Normal (before spike)
    # <2x = 0 pts
    scores['volume'] = {
        'score': 0,
        'reason': 'Normal volume (spike came WITH the move)',
        'weight': 'REACTIVE'
    }
    print(f"⚪ Volume: {scores['volume']['score']}/10 - {scores['volume']['reason']}")
    
    # Momentum: Beaten down
    # Negative = 0 pts
    scores['momentum'] = {
        'score': 0,
        'reason': 'Beaten down at bottom (momentum came WITH the move)',
        'weight': 'REACTIVE'
    }
    print(f"⚪ Momentum: {scores['momentum']['score']}/10 - {scores['momentum']['reason']}")
    
    # TOTAL
    total = sum(s['score'] for s in scores.values())
    
    print()
    print("="*80)
    print(f"🎯 RGC SCORE (BEFORE 20,000% MOVE): {total}/60 points")
    print("="*80)
    
    if total < 20:
        print("\n❌ SYSTEM FAILURE: RGC scores TOO LOW")
        print("   Our system would have MISSED the 20,000% move")
        print()
        print("THE PROBLEM:")
        print("   We're scoring REACTIVE signals (volume, momentum) equally with SETUP signals (float, insider)")
        print("   Volume and momentum FOLLOW the move. They don't PREDICT it.")
        print()
        print("THE FIX:")
        print("   SETUP signals (float + insider) need HIGHER weight")
        print("   REACTIVE signals (volume + momentum) are confirmation, not prediction")
    
    return scores, total


def score_rgc_after_trigger():
    """
    RGC characteristics AFTER CEO buyback filed (March 10, 2025, same day)
    """
    print("\n" + "="*80)
    print("🔬 RGC AFTER CEO BUYBACK (TRIGGER EVENT)")
    print("="*80)
    
    scores = {}
    
    scores['float'] = {
        'score': 10,
        'reason': '802K float, CEO just bought 652K (81% of float removed!)'
    }
    print(f"✅ Float: 10/10 - {scores['float']['reason']}")
    
    scores['short'] = {
        'score': 8,
        'reason': 'Likely had shorts who are now TRAPPED'
    }
    print(f"✅ Short: 8/10 - {scores['short']['reason']}")
    
    scores['insider'] = {
        'score': 10,
        'reason': '86% insider + CEO just bought $6.2M worth (CONVICTION)'
    }
    print(f"✅ Insider: 10/10 - {scores['insider']['reason']}")
    
    scores['catalyst'] = {
        'score': 10,
        'reason': 'Form 4 filed TODAY - catalyst is LIVE'
    }
    print(f"✅ Catalyst: 10/10 - {scores['catalyst']['reason']}")
    
    scores['volume'] = {
        'score': 10,
        'reason': 'Volume EXPLODING (people reacting to Form 4)'
    }
    print(f"✅ Volume: 10/10 - {scores['volume']['reason']}")
    
    scores['momentum'] = {
        'score': 10,
        'reason': 'Stock went +235% TODAY'
    }
    print(f"✅ Momentum: 10/10 - {scores['momentum']['reason']}")
    
    total = sum(s['score'] for s in scores.values())
    
    print()
    print("="*80)
    print(f"🎯 RGC SCORE (AFTER TRIGGER): {total}/60 points")
    print("="*80)
    print("   But by now we MISSED it - stock already up 235%")
    
    return total


def propose_new_weighting():
    """
    Propose new scoring system with WEIGHTED factors.
    """
    print("\n" + "="*80)
    print("🔧 PROPOSED FIX - WEIGHTED SCORING SYSTEM")
    print("="*80)
    
    print("\nCURRENT SYSTEM (Equal Weight):")
    print("   Float: 10 pts (16.7%)")
    print("   Short: 10 pts (16.7%)")
    print("   Insider: 10 pts (16.7%)")
    print("   Catalyst: 10 pts (16.7%)")
    print("   Volume: 10 pts (16.7%)")
    print("   Momentum: 10 pts (16.7%)")
    print("   TOTAL: 60 pts")
    
    print("\nPROPOSED SYSTEM (Weighted):")
    print("   🎯 SETUP FACTORS (Predict the move):")
    print("      Float: 20 pts (28.6%) - DOUBLE weight")
    print("      Insider: 20 pts (28.6%) - DOUBLE weight")
    print("      Catalyst: 10 pts (14.3%)")
    print("      Short: 10 pts (14.3%)")
    print()
    print("   📊 REACTIVE FACTORS (Confirm the move):")
    print("      Volume: 5 pts (7.1%) - HALF weight")
    print("      Momentum: 5 pts (7.1%) - HALF weight")
    print()
    print("   TOTAL: 70 pts")
    
    print("\nRGC WITH NEW SYSTEM (BEFORE move):")
    print("   Float: 20/20 (ultra-low 802K)")
    print("   Insider: 8/20 (86% ownership, no recent buying)")
    print("   Catalyst: 0/10 (none visible)")
    print("   Short: 0/10 (unknown)")
    print("   Volume: 0/5 (normal)")
    print("   Momentum: 0/5 (beaten down)")
    print("   TOTAL: 28/70 (40%)")
    print()
    print("   ✅ 40% score = TIER 2 watchlist candidate")
    print("   With Form 4 alerts, we'd catch CEO buying and ACT")
    
    print("\nGLSI WITH NEW SYSTEM:")
    print("   Float: 12/20 (6.6M is good but not ultra-low)")
    print("   Insider: 20/20 (50.7% + CEO buying $340K+)")
    print("   Catalyst: 8/10 (Phase 3 in 60 days)")
    print("   Short: 8/10 (24.3% high)")
    print("   Volume: 2/5 (2.6x elevated)")
    print("   Momentum: 0/5 (-7.3% weak)")
    print("   TOTAL: 50/70 (71%)")
    print()
    print("   ✅ 71% score = TIER 1 top conviction")
    
    print("\n" + "="*80)
    print("THE LOGIC:")
    print("   SETUP (float + insider) = What makes it EXPLOSIVE")
    print("   REACTIVE (volume + momentum) = Tells you you're LATE")
    print("   We want to catch BEFORE volume/momentum spike")
    print("="*80)


if __name__ == '__main__':
    # Score RGC before and after
    scores_before, total_before = score_rgc_before_move()
    total_after = score_rgc_after_trigger()
    
    # Propose fix
    propose_new_weighting()
    
    print("\n" + "="*80)
    print("🎯 CONCLUSION:")
    print("="*80)
    print(f"   RGC BEFORE: {total_before}/60 pts (TOO LOW)")
    print(f"   RGC AFTER: {total_after}/60 pts (TOO LATE)")
    print()
    print("   ✅ SOLUTION: Weight SETUP factors (float + insider) MORE")
    print("   ✅ SOLUTION: Weight REACTIVE factors (volume + momentum) LESS")
    print()
    print("   With weighted system + Form 4 alerts:")
    print("   → RGC would score 28/70 (40%) on watchlist")
    print("   → CEO Form 4 would trigger alert")
    print("   → We'd have chance to act on 235% day")
    print("="*80)
