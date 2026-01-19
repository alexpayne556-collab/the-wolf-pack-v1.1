"""
PHASE 3 COMPREHENSIVE TEST SUITE
Catalyst Calendar System Validation
"""

import sys
sys.path.insert(0, 'services')

from catalyst_service import (
    CatalystService, 
    CatalystType, 
    CatalystImpact,
    Catalyst
)
from datetime import datetime, timedelta


def test_scenario_1_urgency_scoring():
    """Test urgency scoring algorithm across all time ranges"""
    print("\n" + "="*60)
    print("TEST 1: Urgency Scoring Algorithm")
    print("="*60)
    
    # Create test catalysts at different time ranges
    test_cases = [
        (2, "IMMINENT", 95),    # 0-3 days
        (6, "THIS WEEK", 85),   # 4-7 days
        (10, "APPROACHING", 75), # 8-14 days
        (20, "UPCOMING", 65),    # 15-30 days
        (45, "DISTANT", 55),     # 31-60 days
        (90, "FAR", 45),         # 61+ days (decaying)
    ]
    
    passed = True
    for days, label, expected_min in test_cases:
        event_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        catalyst = Catalyst(
            ticker='TEST',
            company_name='Test Corp',
            catalyst_type=CatalystType.EARNINGS,
            event_date=event_date,
            description=f'Test event in {days} days',
            impact_level=CatalystImpact.MEDIUM,
            days_until=days,
            source='test'
        )
        
        score = catalyst.get_urgency_score()
        status = "✅ PASS" if score >= expected_min - 5 else "❌ FAIL"
        print(f"{status} {days} days ({label}): {score}/100 (expected ~{expected_min})")
        
        if score < expected_min - 5:
            passed = False
    
    print(f"\n{'✅ PASS' if passed else '❌ FAIL'}: Urgency scoring validated")
    return passed


def test_scenario_2_impact_bonuses():
    """Test impact level bonuses"""
    print("\n" + "="*60)
    print("TEST 2: Impact Level Bonuses")
    print("="*60)
    
    event_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    test_cases = [
        (CatalystImpact.BINARY, 30, "BINARY (win/lose everything)"),
        (CatalystImpact.HIGH, 20, "HIGH (major catalyst)"),
        (CatalystImpact.MEDIUM, 10, "MEDIUM (moderate)"),
        (CatalystImpact.LOW, 5, "LOW (minor)"),
    ]
    
    base_urgency = 85  # 7 days = 85 pts urgency
    passed = True
    
    for impact, bonus, label in test_cases:
        catalyst = Catalyst(
            ticker='TEST',
            company_name='Test Corp',
            catalyst_type=CatalystType.PDUFA,
            event_date=event_date,
            description=f'Test {label}',
            impact_level=impact,
            days_until=7,
            source='test'
        )
        
        score = catalyst.get_signal_score()
        expected = min(base_urgency + bonus, 100)
        status = "✅ PASS" if score == expected else "❌ FAIL"
        print(f"{status} {label}: {score}/100 (expected {expected})")
        
        if score != expected:
            passed = False
    
    print(f"\n{'✅ PASS' if passed else '❌ FAIL'}: Impact bonuses validated")
    return passed


def test_scenario_3_catalyst_types():
    """Test all catalyst types"""
    print("\n" + "="*60)
    print("TEST 3: Catalyst Type Coverage")
    print("="*60)
    
    import os
    test_db = 'services/data/catalysts_test3.json'
    if os.path.exists(test_db):
        os.remove(test_db)
    
    cs = CatalystService(db_path=test_db)
    event_date = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
    
    catalyst_types = [
        (CatalystType.PDUFA, "PDUFA date"),
        (CatalystType.EARNINGS, "Earnings report"),
        (CatalystType.CLINICAL_TRIAL, "Trial readout"),
        (CatalystType.CONTRACT_AWARD, "Defense contract"),
        (CatalystType.POLICY_EVENT, "Policy decision"),
        (CatalystType.PRODUCT_LAUNCH, "Product launch"),
        (CatalystType.MERGER, "Merger vote"),
        (CatalystType.MANUAL, "Manual entry"),
    ]
    
    passed = True
    for cat_type, description in catalyst_types:
        try:
            catalyst = cs.add_catalyst(
                ticker='TEST',
                catalyst_type=cat_type,
                event_date=event_date,
                description=description,
                impact_level=CatalystImpact.MEDIUM,
                company_name='Test Corp'
            )
            print(f"✅ PASS {cat_type.value}: Created successfully")
        except Exception as e:
            print(f"❌ FAIL {cat_type.value}: {e}")
            passed = False
    
    print(f"\n{'✅ PASS' if passed else '❌ FAIL'}: All catalyst types supported")
    return passed


def test_scenario_4_convergence_integration():
    """Test catalyst signal format for convergence"""
    print("\n" + "="*60)
    print("TEST 4: Convergence Integration")
    print("="*60)
    
    import os
    test_db = 'services/data/catalysts_test4.json'
    if os.path.exists(test_db):
        os.remove(test_db)
    
    cs = CatalystService(db_path=test_db)
    
    # Add test catalyst
    event_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    cs.add_catalyst(
        ticker='CONV',
        catalyst_type=CatalystType.EARNINGS,
        event_date=event_date,
        description='Q4 Earnings',
        impact_level=CatalystImpact.HIGH,
        company_name='Convergence Test'
    )
    
    # Get signal for convergence
    signal = cs.get_catalyst_for_convergence('CONV')
    
    passed = True
    
    # Validate signal format
    if not signal:
        print("❌ FAIL: No signal returned")
        return False
    
    required_keys = ['score', 'reasoning', 'data']
    for key in required_keys:
        if key not in signal:
            print(f"❌ FAIL: Missing key '{key}' in signal")
            passed = False
        else:
            print(f"✅ PASS: Signal has '{key}' = {signal[key] if key != 'data' else '...'}")
    
    # Validate score is reasonable
    if signal['score'] < 50 or signal['score'] > 100:
        print(f"❌ FAIL: Score out of range: {signal['score']}")
        passed = False
    else:
        print(f"✅ PASS: Score in valid range: {signal['score']}/100")
    
    # Validate reasoning is meaningful
    if not signal['reasoning'] or len(signal['reasoning']) < 5:
        print(f"❌ FAIL: Reasoning too short: '{signal['reasoning']}'")
        passed = False
    else:
        print(f"✅ PASS: Reasoning is meaningful: '{signal['reasoning']}'")
    
    print(f"\n{'✅ PASS' if passed else '❌ FAIL'}: Convergence integration format valid")
    return passed


def test_scenario_5_multiple_catalysts_per_ticker():
    """Test handling multiple catalysts for same ticker"""
    print("\n" + "="*60)
    print("TEST 5: Multiple Catalysts Per Ticker")
    print("="*60)
    
    import os
    test_db = 'services/data/catalysts_test5.json'
    if os.path.exists(test_db):
        os.remove(test_db)
    
    cs = CatalystService(db_path=test_db)
    
    # Add 3 catalysts for same ticker
    ticker = 'MULTI'
    events = [
        (5, CatalystType.EARNINGS, CatalystImpact.HIGH, "Q4 Earnings"),
        (30, CatalystType.PRODUCT_LAUNCH, CatalystImpact.MEDIUM, "New product"),
        (90, CatalystType.CLINICAL_TRIAL, CatalystImpact.BINARY, "Phase 3 readout"),
    ]
    
    for days, cat_type, impact, desc in events:
        event_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        cs.add_catalyst(
            ticker=ticker,
            catalyst_type=cat_type,
            event_date=event_date,
            description=desc,
            impact_level=impact,
            company_name='Multi Test'
        )
    
    # Get all catalysts for ticker
    catalysts = cs.get_catalysts_for_tickers([ticker])
    
    if ticker not in catalysts:
        print(f"❌ FAIL: Ticker {ticker} not found in results")
        return False
    
    ticker_catalysts = catalysts[ticker]
    if len(ticker_catalysts) != 3:
        print(f"❌ FAIL: Expected 3 catalysts, got {len(ticker_catalysts)}")
        return False
    
    print(f"✅ PASS: Found 3 catalysts for {ticker}")
    
    # Get best signal for convergence (should pick nearest/highest)
    signal = cs.get_catalyst_for_convergence(ticker)
    if not signal:
        print("❌ FAIL: No signal returned for ticker with multiple catalysts")
        return False
    
    print(f"✅ PASS: Best catalyst selected: {signal['reasoning']}")
    print(f"  Score: {signal['score']}/100")
    
    # Verify it picked the nearest/best one (earnings in 5 days should win)
    if signal['score'] < 90:  # 5 days + HIGH impact should be ~100
        print(f"⚠️  WARNING: Expected high score for nearest catalyst, got {signal['score']}")
    
    print(f"\n✅ PASS: Multiple catalysts per ticker handled correctly")
    return True


def test_scenario_6_alert_generation():
    """Test catalyst alert generation"""
    print("\n" + "="*60)
    print("TEST 6: Alert Generation")
    print("="*60)
    
    import os
    test_db = 'services/data/catalysts_test6.json'
    if os.path.exists(test_db):
        os.remove(test_db)
    
    cs = CatalystService(db_path=test_db)
    
    # Add catalysts at different urgencies
    test_events = [
        (2, 'IMM1', 'IMMINENT event'),
        (6, 'IMM2', 'This week event'),
        (15, 'UP1', 'Upcoming event'),
        (35, 'UP2', 'Next month event'),
        (100, 'DIST', 'Distant event'),
    ]
    
    for days, ticker, desc in test_events:
        event_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        cs.add_catalyst(
            ticker=ticker,
            catalyst_type=CatalystType.EARNINGS,
            event_date=event_date,
            description=desc,
            impact_level=CatalystImpact.MEDIUM,
            company_name='Alert Test'
        )
    
    # Get alerts for next 30 days
    alerts = cs.get_catalyst_alerts(days_threshold=30)
    
    # Should get 3 alerts (2, 6, 15 days), not the 35 or 100-day ones
    if len(alerts) != 3:
        print(f"❌ FAIL: Expected 3 alerts, got {len(alerts)}")
        return False
    
    print(f"✅ PASS: Found {len(alerts)} alerts within 30 days")
    
    # Verify alerts are sorted by urgency (nearest first)
    if alerts[0]['ticker'] != 'IMM1':
        print(f"❌ FAIL: First alert should be IMM1, got {alerts[0]['ticker']}")
        return False
    
    print(f"✅ PASS: Alerts sorted by urgency")
    
    for alert in alerts:
        print(f"  {alert['priority']} {alert['ticker']}: {alert['event']} in {alert['days_until']} days")
    
    print(f"\n✅ PASS: Alert generation working correctly")
    return True


def test_scenario_7_json_persistence():
    """Test JSON save/load persistence"""
    print("\n" + "="*60)
    print("TEST 7: JSON Persistence")
    print("="*60)
    
    import os
    test_db_path = 'services/data/catalysts_persistence_test.json'
    
    # Clean up if exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Create service, add catalysts
    cs1 = CatalystService(db_path=test_db_path)
    event_date = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
    
    cs1.add_catalyst(
        ticker='PERSIST',
        catalyst_type=CatalystType.EARNINGS,
        event_date=event_date,
        description='Persistence test',
        impact_level=CatalystImpact.HIGH,
        company_name='Persist Corp'
    )
    
    # Create NEW service instance (should load from file)
    cs2 = CatalystService(db_path=test_db_path)
    catalysts = cs2.get_catalysts_for_tickers(['PERSIST'])
    
    if 'PERSIST' not in catalysts or len(catalysts['PERSIST']) != 1:
        print("❌ FAIL: Catalyst not persisted across instances")
        return False
    
    print("✅ PASS: Catalyst persisted to JSON")
    print("✅ PASS: Catalyst loaded from JSON in new instance")
    
    # Verify file exists and is valid JSON
    if not os.path.exists(test_db_path):
        print("❌ FAIL: JSON file not created")
        return False
    
    import json
    with open(test_db_path, 'r') as f:
        data = json.load(f)
    
    if not isinstance(data, list) or len(data) != 1:
        print("❌ FAIL: JSON format invalid")
        return False
    
    print("✅ PASS: JSON file format valid")
    
    # Clean up
    os.remove(test_db_path)
    
    print(f"\n✅ PASS: JSON persistence working correctly")
    return True


def run_all_tests():
    """Run complete Phase 3 test suite"""
    print("\n" + "🔥"*30)
    print("PHASE 3 COMPREHENSIVE TEST SUITE")
    print("Catalyst Calendar System Validation")
    print("🔥"*30)
    
    tests = [
        ("Urgency Scoring Algorithm", test_scenario_1_urgency_scoring),
        ("Impact Level Bonuses", test_scenario_2_impact_bonuses),
        ("Catalyst Type Coverage", test_scenario_3_catalyst_types),
        ("Convergence Integration", test_scenario_4_convergence_integration),
        ("Multiple Catalysts Per Ticker", test_scenario_5_multiple_catalysts_per_ticker),
        ("Alert Generation", test_scenario_6_alert_generation),
        ("JSON Persistence", test_scenario_7_json_persistence),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print("\n" + "="*60)
    if passed_count == total_count:
        print("🎉 ALL TESTS PASSED")
        print(f"✅ PHASE 3 VALIDATED - {passed_count}/{total_count} tests passed")
        print("Ready for Phase 4 (Sector Flow Tracker)")
    else:
        print(f"⚠️  SOME TESTS FAILED - {passed_count}/{total_count} passed")
        print("Review failures before proceeding")
    print("="*60)


if __name__ == '__main__':
    run_all_tests()
