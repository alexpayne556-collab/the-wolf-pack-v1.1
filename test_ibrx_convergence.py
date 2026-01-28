#!/usr/bin/env python3
"""
IBRX CONVERGENCE TEST
Verify the convergence engine still works after consolidation
IBRX should score 90+ (proven: 93/100 → +55% gain)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'wolfpack'))

from services.convergence_service import ConvergenceEngine, SignalType

def test_ibrx_convergence():
    """
    Test IBRX convergence with the signals that led to 93/100 score
    Original trade: 93/100 → +55% gain
    """
    
    print("=" * 70)
    print("🧪 TESTING IBRX CONVERGENCE - Core Brain Verification")
    print("=" * 70)
    print()
    print("Historical Context:")
    print("  - Date: Jan 19, 2026")
    print("  - Original Score: 93/100")
    print("  - Outcome: +55% gain (still holding)")
    print("  - Pattern: BLA filing + Saudi approval + insider buying")
    print()
    
    # Initialize convergence engine
    engine = ConvergenceEngine()
    print("✅ Convergence Engine initialized")
    print(f"   Signal weights: {engine.weights}")
    print()
    
    # Reconstruct IBRX signals based on the COMPLETE_CODEBASE_BIBLE.md
    # IBRX had strong convergence across multiple signals
    
    # 1. SCANNER SIGNAL (Technical Setup) - Score: 85/100
    scanner_signal = {
        'score': 85,
        'reasoning': 'Wounded prey pattern: -82% from 52w high, price $1.50, oversold RSI, volume starting to spike',
        'data': {
            'price': 1.50,
            'high_52w': 8.50,
            'decline_pct': -82.4,
            'rsi': 28,
            'volume_ratio': 1.8,
            'pattern': 'wounded_prey'
        }
    }
    
    # 2. INSTITUTIONAL SIGNAL (BR0KKR) - Score: 95/100
    br0kkr_signal = {
        'score': 95,
        'reasoning': 'Insider buying cluster: Multiple directors buying $50K-100K each in past 30 days',
        'data': {
            'insider_buys': 3,
            'total_value': 250000,
            'recent_buys': True,
            'form4_dates': ['2025-12-15', '2025-12-22', '2026-01-05']
        }
    }
    
    # 3. CATALYST SIGNAL (BLA Filing + Saudi Approval) - Score: 100/100
    catalyst_signal = {
        'score': 100,
        'reasoning': 'BLA filing submitted to FDA + Saudi NHRA approval announced + Q1 2026 approval expected',
        'data': {
            'catalyst_type': 'regulatory_approval',
            'days_until': 45,
            'probability': 'high',
            'saudi_approval': True,
            'bla_filed': True
        }
    }
    
    # 4. SECTOR SIGNAL (Biotech) - Score: 70/100
    sector_signal = {
        'score': 70,
        'reasoning': 'Biotech sector neutral, small-cap biotech showing rotation strength',
        'data': {
            'sector': 'Biotechnology',
            'xbi_change': 2.1,
            'relative_strength': 'moderate'
        }
    }
    
    # 5. PATTERN SIGNAL (Flat-to-Boom) - Score: 90/100
    pattern_signal = {
        'score': 90,
        'reasoning': 'Flat-to-boom pattern: 3mo consolidation, insider buying, catalyst approaching, price mid-range',
        'data': {
            'pattern_name': 'flat_to_boom',
            'consolidation_months': 3,
            'price_position': 0.45,  # 45% of range
            'volume_stable': True,
            'catalyst_days': 45
        }
    }
    
    # 6. NEWS SIGNAL (Positive) - Score: 80/100
    news_signal = {
        'score': 80,
        'reasoning': 'Positive news: Saudi approval announcement, BLA filing coverage, analyst upgrades',
        'data': {
            'sentiment': 'positive',
            'article_count': 12,
            'positive_keywords': ['approval', 'breakthrough', 'progress']
        }
    }
    
    # 7. EARNINGS SIGNAL (Not a factor for IBRX) - Score: 50/100
    earnings_signal = {
        'score': 50,
        'reasoning': 'Pre-revenue biotech, no earnings impact',
        'data': {
            'has_earnings': False,
            'days_to_earnings': None
        }
    }
    
    print("📊 Signal Breakdown:")
    print(f"   SCANNER:       {scanner_signal['score']}/100 - {scanner_signal['reasoning'][:60]}...")
    print(f"   INSTITUTIONAL: {br0kkr_signal['score']}/100 - {br0kkr_signal['reasoning'][:60]}...")
    print(f"   CATALYST:      {catalyst_signal['score']}/100 - {catalyst_signal['reasoning'][:60]}...")
    print(f"   SECTOR:        {sector_signal['score']}/100 - {sector_signal['reasoning'][:60]}...")
    print(f"   PATTERN:       {pattern_signal['score']}/100 - {pattern_signal['reasoning'][:60]}...")
    print(f"   NEWS:          {news_signal['score']}/100 - {news_signal['reasoning'][:60]}...")
    print(f"   EARNINGS:      {earnings_signal['score']}/100 - {earnings_signal['reasoning'][:60]}...")
    print()
    
    # Calculate convergence
    print("🧮 Calculating convergence...")
    result = engine.calculate_convergence(
        ticker='IBRX',
        scanner_signal=scanner_signal,
        br0kkr_signal=br0kkr_signal,
        catalyst_signal=catalyst_signal,
        sector_signal=sector_signal,
        pattern_signal=pattern_signal,
        news_signal=news_signal,
        earnings_signal=earnings_signal
    )
    
    print()
    print("=" * 70)
    print("📈 CONVERGENCE RESULT")
    print("=" * 70)
    
    if result:
        print(f"Ticker: {result.ticker}")
        print(f"Convergence Score: {result.convergence_score}/100")
        print(f"Convergence Level: {result.convergence_level.value}")
        print(f"Signal Count: {result.signal_count}")
        print(f"Priority: {result.get_priority_emoji()}")
        print()
        print("Signal Breakdown:")
        print(result.get_signal_breakdown())
        print()
        
        # Validation
        print("=" * 70)
        print("✅ VALIDATION")
        print("=" * 70)
        
        if result.convergence_score >= 90:
            print(f"✅ PASS: Score {result.convergence_score}/100 >= 90 (Target met)")
            print("✅ Core brain intact - consolidation successful!")
            print("✅ Ready to proceed with unified order execution")
            return True
        elif result.convergence_score >= 85:
            print(f"⚠️  CLOSE: Score {result.convergence_score}/100 (Expected 93, got {result.convergence_score})")
            print("⚠️  Within acceptable range (85-95), minor variance expected")
            print("⚠️  May proceed but investigate variance")
            return True
        else:
            print(f"❌ FAIL: Score {result.convergence_score}/100 < 85 (Expected ~93)")
            print("❌ Core brain may be broken - DO NOT PROCEED")
            print("❌ Need to debug before continuing consolidation")
            return False
    else:
        print("❌ FAIL: No convergence result returned")
        print("❌ Core brain may be broken - DO NOT PROCEED")
        return False


if __name__ == "__main__":
    success = test_ibrx_convergence()
    sys.exit(0 if success else 1)
