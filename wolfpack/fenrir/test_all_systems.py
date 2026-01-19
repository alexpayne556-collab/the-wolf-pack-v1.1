# 🐺 FENRIR V2 - FULL SYSTEM TEST
# Test all secretary features to verify functionality

import sys

print("\n" + "="*60)
print("🐺 FENRIR V2 - FULL SYSTEM TEST")
print("="*60 + "\n")

tests_passed = 0
tests_failed = 0

# Test 1: Risk Manager
print("[1/10] Testing Risk Manager...")
try:
    from risk_manager import format_risk_report
    import config
    report = format_risk_report(config.HOLDINGS)
    assert "Day Trades" in report
    assert "POSITION SIZES" in report
    print("✅ Risk Manager working\n")
    tests_passed += 1
except Exception as e:
    print(f"❌ Risk Manager failed: {e}\n")
    tests_failed += 1

# Test 2: Pre-Market Tracker
print("[2/10] Testing Pre-Market Tracker...")
try:
    from premarket_tracker import PremarketTracker
    tracker = PremarketTracker()
    gaps = tracker.scan_for_gaps(list(config.HOLDINGS.keys()))
    print(f"✅ Pre-Market Tracker working (found {len(gaps)} gaps)\n")
    tests_passed += 1
except Exception as e:
    print(f"❌ Pre-Market Tracker failed: {e}\n")
    tests_failed += 1

# Test 3: After-Hours Monitor
print("[3/10] Testing After-Hours Monitor...")
try:
    from afterhours_monitor import AfterHoursMonitor
    monitor = AfterHoursMonitor()
    report = monitor.generate_ah_report(list(config.HOLDINGS.keys()))
    assert "AFTER-HOURS" in report
    print("✅ After-Hours Monitor working\n")
    tests_passed += 1
except Exception as e:
    print(f"❌ After-Hours Monitor failed: {e}\n")
    tests_failed += 1

# Test 4: Daily Briefing
print("[4/10] Testing Daily Briefing...")
try:
    from daily_briefing import DailyBriefing
    briefing = DailyBriefing()
    report = briefing.generate_briefing()
    assert "FENRIR DAILY BRIEFING" in report
    print("✅ Daily Briefing working\n")
    tests_passed += 1
except Exception as e:
    print(f"❌ Daily Briefing failed: {e}\n")
    tests_failed += 1

# Test 5: Catalyst Calendar
print("[5/10] Testing Catalyst Calendar...")
try:
    from catalyst_calendar import quick_catalyst_check
    report = quick_catalyst_check()
    assert "CATALYST CALENDAR" in report
    print("✅ Catalyst Calendar working\n")
    tests_passed += 1
except Exception as e:
    print(f"❌ Catalyst Calendar failed: {e}\n")
    tests_failed += 1

# Test 6: Key Levels Tracker
print("[6/10] Testing Key Levels Tracker...")
try:
    from key_levels import KeyLevelsTracker
    tracker = KeyLevelsTracker()
    levels = tracker.calculate_levels('IBRX')
    assert 'support' in levels
    assert 'resistance' in levels
    print(f"✅ Key Levels working (IBRX has {len(levels.get('support', []))} support, {len(levels.get('resistance', []))} resistance)\n")
    tests_passed += 1
except Exception as e:
    print(f"❌ Key Levels failed: {e}\n")
    tests_failed += 1

# Test 7: EOD Report
print("[7/10] Testing EOD Report...")
try:
    from eod_report import EODReport
    report = EODReport()
    output = report.generate_report()
    assert "END OF DAY REPORT" in output
    print("✅ EOD Report working\n")
    tests_passed += 1
except Exception as e:
    print(f"❌ EOD Report failed: {e}\n")
    tests_failed += 1

# Test 8: Correlation Tracker
print("[8/10] Testing Correlation Tracker...")
try:
    from correlation_tracker import CorrelationTracker
    tracker = CorrelationTracker()
    plays = tracker.get_sector_sympathy_plays('MU')
    print(f"✅ Correlation Tracker working (MU has {len(plays)} sympathy plays)\n")
    tests_passed += 1
except Exception as e:
    print(f"❌ Correlation Tracker failed: {e}\n")
    tests_failed += 1

# Test 9: Failed Trades Logger
print("[9/10] Testing Failed Trades Logger...")
try:
    import failed_trades
    report = failed_trades.analyze_missed_trades()
    # Just check it runs without error
    print("✅ Failed Trades Logger working\n")
    tests_passed += 1
except Exception as e:
    print(f"❌ Failed Trades Logger failed: {e}\n")
    tests_failed += 1

# Test 10: Notification System
print("[10/10] Testing Notification System...")
try:
    from notifications import NotificationSystem
    notifier = NotificationSystem()
    # Test console notification (won't actually toast during test)
    notifier.alert_custom("System Test", "This is a test", urgent=False)
    print("✅ Notification System working\n")
    tests_passed += 1
except Exception as e:
    print(f"❌ Notification System failed: {e}\n")
    tests_failed += 1

# Summary
print("="*60)
print(f"RESULTS: {tests_passed}/10 tests passed, {tests_failed} failed")
print("="*60 + "\n")

if tests_passed == 10:
    print("🐺 ALL SYSTEMS OPERATIONAL!")
    print("Fenrir V2 is ready for trading.\n")
    sys.exit(0)
else:
    print("⚠️  Some systems need attention")
    print("Check errors above for details.\n")
    sys.exit(1)
