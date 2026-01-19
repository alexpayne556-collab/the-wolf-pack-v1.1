#!/usr/bin/env python3
"""
PHASE 2 COMPREHENSIVE TEST
Test convergence engine with mock data to validate all scenarios
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))

from convergence_service import ConvergenceEngine, ConvergenceLevel

def test_scenario_1_single_signal():
    """Test: Single signal should return None"""
    print("=" * 60)
    print("TEST 1: Single Signal (Should Reject)")
    print("=" * 60)
    
    engine = ConvergenceEngine()
    result = engine.calculate_convergence(
        ticker="TEST1",
        scanner_signal={'score': 70, 'reasoning': 'Strong setup'},
    )
    
    assert result is None, "Single signal should return None"
    print("✅ PASS: Single signal correctly rejected\n")


def test_scenario_2_two_weak_signals():
    """Test: Two weak signals below threshold"""
    print("=" * 60)
    print("TEST 2: Two Weak Signals (Should Reject)")
    print("=" * 60)
    
    engine = ConvergenceEngine()
    result = engine.calculate_convergence(
        ticker="TEST2",
        scanner_signal={'score': 30, 'reasoning': 'Weak setup'},
        br0kkr_signal={'score': 40, 'reasoning': 'Minor insider buy'},
    )
    
    # Weighted: (30*0.25 + 40*0.35) / 0.6 = 35.8 + 5 bonus = 40.8 (below 50 threshold)
    assert result is None, "Two weak signals should return None"
    print("✅ PASS: Weak signals correctly rejected\n")


def test_scenario_3_scanner_plus_institutional():
    """Test: Scanner + BR0KKR (realistic scenario)"""
    print("=" * 60)
    print("TEST 3: Scanner + Institutional (High Conviction)")
    print("=" * 60)
    
    engine = ConvergenceEngine()
    result = engine.calculate_convergence(
        ticker="SMCI",
        scanner_signal={'score': 65, 'reasoning': 'Wounded prey, down 48% from highs'},
        br0kkr_signal={'score': 75, 'reasoning': '2 Directors bought $450k'},
    )
    
    # Weighted: (65*0.25 + 75*0.35) / 0.6 = 70.83 + 5 bonus = 75.83
    assert result is not None, "Should detect convergence"
    assert result.signal_count == 2, "Should have 2 signals"
    assert 70 <= result.convergence_score <= 80, f"Score should be ~76, got {result.convergence_score}"
    assert result.convergence_level == ConvergenceLevel.HIGH, "Should be HIGH level"
    
    print(f"✅ PASS: {result.ticker} = {result.convergence_score}/100 ({result.convergence_level.value})")
    print(f"   Signals: {result.signal_count}")
    print(result.get_signal_breakdown())
    print()


def test_scenario_4_three_signals_critical():
    """Test: Scanner + BR0KKR + Catalyst (CRITICAL level)"""
    print("=" * 60)
    print("TEST 4: Three Signals (CRITICAL Convergence)")
    print("=" * 60)
    
    engine = ConvergenceEngine()
    result = engine.calculate_convergence(
        ticker="SOUN",
        scanner_signal={'score': 70, 'reasoning': 'Wounded prey + volume spike'},
        br0kkr_signal={'score': 95, 'reasoning': 'CEO ($800k) + CFO ($700k) + Director ($600k)'},
        catalyst_signal={'score': 75, 'reasoning': 'Earnings in 10 days'},
    )
    
    # Weighted: (70*0.25 + 95*0.35 + 75*0.20) / 0.8 = 81.25 + 10 bonus = 91.25
    assert result is not None, "Should detect convergence"
    assert result.signal_count == 3, "Should have 3 signals"
    assert 85 <= result.convergence_score <= 100, f"Score should be ~91, got {result.convergence_score}"
    assert result.convergence_level == ConvergenceLevel.CRITICAL, "Should be CRITICAL level"
    
    print(f"✅ PASS: {result.ticker} = {result.convergence_score}/100 ({result.convergence_level.value})")
    print(f"   Signals: {result.signal_count}")
    print(result.get_signal_breakdown())
    print()


def test_scenario_5_batch_analysis():
    """Test: Batch analysis with multiple tickers"""
    print("=" * 60)
    print("TEST 5: Batch Analysis (Multiple Tickers)")
    print("=" * 60)
    
    from br0kkr_service import ClusterBuy, InsiderTransaction, InsiderRole, TransactionType
    
    # Mock scanner results
    scanner_results = [
        {'ticker': 'SMCI', 'score': 65, 'reasoning': 'Wounded prey', 'type': 'WOUNDED_PREY'},
        {'ticker': 'AMD', 'score': 55, 'reasoning': 'Early momentum', 'type': 'EARLY_MOMENTUM'},
        {'ticker': 'IONQ', 'score': 65, 'reasoning': 'Wounded prey', 'type': 'WOUNDED_PREY'},
    ]
    
    # Mock cluster buy for SMCI
    mock_transaction = InsiderTransaction(
        ticker='SMCI',
        company_name='Super Micro Computer',
        insider_name='Director 1',
        insider_role=InsiderRole.DIRECTOR,
        transaction_date='2026-01-15',
        shares=10000,
        price_per_share=30.0,
        total_value=300000,
        transaction_type=TransactionType.BUY,
        filing_date='2026-01-16',
        filing_url='https://sec.gov/test'
    )
    
    mock_cluster = ClusterBuy(
        ticker='SMCI',
        company_name='Super Micro Computer',
        transactions=[mock_transaction],
        total_value=300000,
        unique_insiders=2,
        date_range_start='2026-01-15',
        date_range_end='2026-01-16',
        has_ceo=False,
        has_cfo=False,
        has_director=True,
    )
    
    br0kkr_results = {
        'cluster_buys': [mock_cluster],
        'activist_filings': []
    }
    
    engine = ConvergenceEngine()
    convergence_signals = engine.batch_analyze(
        scanner_results=scanner_results,
        br0kkr_results=br0kkr_results,
    )
    
    assert len(convergence_signals) > 0, "Should find at least one convergence"
    
    # SMCI should have convergence (scanner + institutional)
    smci_signal = next((s for s in convergence_signals if s.ticker == 'SMCI'), None)
    assert smci_signal is not None, "SMCI should have convergence"
    assert smci_signal.signal_count == 2, "SMCI should have 2 signals"
    
    print(f"✅ PASS: Found {len(convergence_signals)} convergence signals")
    print(f"   SMCI: {smci_signal.convergence_score}/100 with {smci_signal.signal_count} signals")
    print()


def test_scenario_6_weight_validation():
    """Test: Validate that institutional signal has highest weight"""
    print("=" * 60)
    print("TEST 6: Weight Validation (Institutional > Scanner)")
    print("=" * 60)
    
    engine = ConvergenceEngine()
    
    # Test A: High scanner, low institutional
    result_a = engine.calculate_convergence(
        ticker="TEST_A",
        scanner_signal={'score': 90, 'reasoning': 'Perfect setup'},
        br0kkr_signal={'score': 50, 'reasoning': 'Minor buy'},
    )
    
    # Test B: Low scanner, high institutional
    result_b = engine.calculate_convergence(
        ticker="TEST_B",
        scanner_signal={'score': 50, 'reasoning': 'Weak setup'},
        br0kkr_signal={'score': 90, 'reasoning': 'CEO cluster'},
    )
    
    # Result B should score higher because institutional has more weight (0.35 vs 0.25)
    assert result_b.convergence_score > result_a.convergence_score, \
        f"Institutional weight test failed: B={result_b.convergence_score} should be > A={result_a.convergence_score}"
    
    print(f"✅ PASS: Weight validation correct")
    print(f"   High scanner (90) + Low institutional (50) = {result_a.convergence_score}")
    print(f"   Low scanner (50) + High institutional (90) = {result_b.convergence_score}")
    print(f"   Institutional signal properly weighted higher\n")


def test_scenario_7_convergence_bonus():
    """Test: Validate convergence bonus increases with signal count"""
    print("=" * 60)
    print("TEST 7: Convergence Bonus Scaling")
    print("=" * 60)
    
    engine = ConvergenceEngine()
    
    # 2 signals
    result_2 = engine.calculate_convergence(
        ticker="TEST",
        scanner_signal={'score': 60, 'reasoning': 'Setup'},
        br0kkr_signal={'score': 60, 'reasoning': 'Buy'},
    )
    
    # 3 signals
    result_3 = engine.calculate_convergence(
        ticker="TEST",
        scanner_signal={'score': 60, 'reasoning': 'Setup'},
        br0kkr_signal={'score': 60, 'reasoning': 'Buy'},
        catalyst_signal={'score': 60, 'reasoning': 'Earnings'},
    )
    
    # 4 signals
    result_4 = engine.calculate_convergence(
        ticker="TEST",
        scanner_signal={'score': 60, 'reasoning': 'Setup'},
        br0kkr_signal={'score': 60, 'reasoning': 'Buy'},
        catalyst_signal={'score': 60, 'reasoning': 'Earnings'},
        sector_signal={'score': 60, 'reasoning': 'Hot sector'},
    )
    
    # Scores should increase with more signals
    assert result_3.convergence_score > result_2.convergence_score, "3 signals should score higher than 2"
    assert result_4.convergence_score > result_3.convergence_score, "4 signals should score higher than 3"
    
    bonus_2_to_3 = result_3.convergence_score - result_2.convergence_score
    bonus_3_to_4 = result_4.convergence_score - result_3.convergence_score
    
    print(f"✅ PASS: Convergence bonus scales correctly")
    print(f"   2 signals: {result_2.convergence_score}/100")
    print(f"   3 signals: {result_3.convergence_score}/100 (+{bonus_2_to_3} bonus)")
    print(f"   4 signals: {result_4.convergence_score}/100 (+{bonus_3_to_4} additional bonus)\n")


def run_all_tests():
    """Run all test scenarios"""
    print("\n🧠 PHASE 2 COMPREHENSIVE TEST SUITE")
    print("Testing Convergence Engine with all scenarios\n")
    
    try:
        test_scenario_1_single_signal()
        test_scenario_2_two_weak_signals()
        test_scenario_3_scanner_plus_institutional()
        test_scenario_4_three_signals_critical()
        test_scenario_5_batch_analysis()
        test_scenario_6_weight_validation()
        test_scenario_7_convergence_bonus()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED")
        print("=" * 60)
        print("✅ Single signal rejection")
        print("✅ Weak signal filtering")
        print("✅ Two-signal convergence (HIGH)")
        print("✅ Three-signal convergence (CRITICAL)")
        print("✅ Batch analysis")
        print("✅ Weight validation (institutional > scanner)")
        print("✅ Convergence bonus scaling")
        print("\n✅ PHASE 2 VALIDATED - Ready for Phase 3")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
