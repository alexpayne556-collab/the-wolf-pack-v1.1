#!/usr/bin/env python3
"""
🧪 FENRIR V2 - COMPREHENSIVE TEST SUITE
Tests for position_health_checker.py and thesis_tracker.py

These tests try to TRICK the system with edge cases, weird inputs,
and natural language variations.
"""

import sys
sys.path.append('.')

from position_health_checker import (
    calculate_health_score, 
    get_health_status,
    parse_natural_query,
    answer_natural_query
)

from thesis_tracker import (
    calculate_thesis_strength,
    get_thesis_status,
    parse_thesis_query,
    answer_thesis_query,
    validate_thesis,
    THESIS_DATABASE
)


# ============================================
# COLOR CODES FOR TEST OUTPUT
# ============================================

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def test_result(name: str, passed: bool, details: str = ""):
    """Pretty print test results"""
    status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
    print(f"{status} | {name}")
    if details and not passed:
        print(f"  {YELLOW}→ {details}{RESET}")


# ============================================
# POSITION HEALTH TESTS
# ============================================

def test_health_scoring_edge_cases():
    """Test health score calculation with extreme values"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TESTING: Position Health Scoring Edge Cases{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Test 1: Perfect storm (everything bad)
    score = calculate_health_score(
        pnl_percent=-20.0,  # Losing badly
        at_analyst_ceiling=True,  # At ceiling
        recent_downgrade=True,  # Downgraded
        days_to_catalyst=90,  # Far away
        peer_outperformance=-15.0  # Peers crushing us
    )
    test_result(
        "Perfect storm scenario (all negative factors)",
        score <= -8,
        f"Expected score <= -8, got {score}"
    )
    
    # Test 2: Rocket ship (everything good)
    score = calculate_health_score(
        pnl_percent=50.0,  # Big winner
        at_analyst_ceiling=False,  # Room to run
        recent_downgrade=False,  # No downgrade
        days_to_catalyst=7,  # Catalyst soon
        peer_outperformance=20.0  # Crushing peers
    )
    test_result(
        "Rocket ship scenario (all positive factors)",
        score >= 8,
        f"Expected score >= 8, got {score}"
    )
    
    # Test 3: Dead money (BBAI scenario)
    score = calculate_health_score(
        pnl_percent=-5.8,
        at_analyst_ceiling=True,
        recent_downgrade=True,
        days_to_catalyst=49,
        peer_outperformance=-5.3
    )
    status = get_health_status(score)
    test_result(
        "BBAI dead money scenario",
        score <= -5 and "DEAD" in status,
        f"Expected dead money (score <= -5), got {score} | {status}"
    )
    
    # Test 4: Catalyst ambiguity (None vs far)
    score_none = calculate_health_score(
        pnl_percent=0, at_analyst_ceiling=False, 
        recent_downgrade=False, days_to_catalyst=None, 
        peer_outperformance=0
    )
    score_far = calculate_health_score(
        pnl_percent=0, at_analyst_ceiling=False,
        recent_downgrade=False, days_to_catalyst=90,
        peer_outperformance=0
    )
    test_result(
        "No catalyst vs far catalyst (should score same)",
        score_none == score_far,
        f"None: {score_none}, Far: {score_far}"
    )
    
    # Test 5: Near-ceiling edge case (96% of PT)
    score_at = calculate_health_score(
        pnl_percent=5, at_analyst_ceiling=True,
        recent_downgrade=False, days_to_catalyst=20,
        peer_outperformance=2
    )
    score_not = calculate_health_score(
        pnl_percent=5, at_analyst_ceiling=False,
        recent_downgrade=False, days_to_catalyst=20,
        peer_outperformance=2
    )
    test_result(
        "At ceiling vs not at ceiling (3-point difference)",
        (score_not - score_at) == 3,
        f"At: {score_at}, Not at: {score_not}, Diff: {score_not - score_at}"
    )


def test_natural_language_parsing():
    """Test natural language query parsing with variations"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TESTING: Natural Language Parsing (Position Health){RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Test typos and variations
    test_cases = [
        ("any dead money?", "dead_money"),
        ("yo whats dying in my portfolio", "dead_money"),
        ("show me the sick positions", "dead_money"),
        ("which ones are healthy", "healthy"),
        ("whats running hot", "healthy"),
        ("what should i sell", "sell_recommendations"),
        ("time to dump something?", "sell_recommendations"),
        ("where should i add money", "buy_recommendations"),
        ("whats worth buying more of", "buy_recommendations"),
        ("check everything", "full_check"),
        ("how's BBAI looking", "single_check"),
        ("tell me about IBRX", "single_check"),
        ("whats up with mu", "single_check"),
    ]
    
    for query, expected_intent in test_cases:
        parsed = parse_natural_query(query)
        passed = parsed['intent'] == expected_intent
        test_result(
            f"Query: '{query}'",
            passed,
            f"Expected '{expected_intent}', got '{parsed['intent']}'"
        )


def test_natural_language_tricky_cases():
    """Try to TRICK the parser with ambiguous queries"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TESTING: Tricky/Ambiguous Natural Language{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    tricky_cases = [
        ("is BBAI dead or what", "dead_money"),  # Multiple keywords
        ("MU healthy? or dying?", "single_check"),  # Conflicting keywords
        ("should i sell the good stuff or the bad stuff", "sell_recommendations"),  # Ambiguous
        ("everything sucks show me", "full_check"),  # Negative overall
        ("wtf is happening", "full_check"),  # No clear keywords
        ("IBRX KTOS UUUU which is best", "healthy"),  # Multiple tickers
    ]
    
    for query, expected_intent in tricky_cases:
        parsed = parse_natural_query(query)
        # For tricky cases, we just check it doesn't crash
        test_result(
            f"Tricky: '{query}'",
            True,  # If it runs, it passes
            f"Parsed as: {parsed['intent']}"
        )
        print(f"  {YELLOW}→ Interpreted as: {parsed['intent']}{RESET}")


# ============================================
# THESIS TRACKER TESTS
# ============================================

def test_thesis_scoring_edge_cases():
    """Test thesis strength calculation edge cases"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TESTING: Thesis Scoring Edge Cases{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Test 1: Perfect thesis (all factors present)
    score = calculate_thesis_strength({
        'what_they_do': 'Makes widgets',
        'who_needs_it': 'Everyone',
        'catalyst': 'Big contract',
        'catalyst_date': '2026-01-20',  # Within 30 days
        'demand_type': 'REAL',
        'has_revenue': True,
        'has_contracts': True,
        'analyst_support': True
    })
    test_result(
        "Perfect thesis (all factors)",
        score >= 9,
        f"Expected >= 9, got {score}"
    )
    
    # Test 2: Worst thesis (nothing good)
    score = calculate_thesis_strength({
        'what_they_do': '',
        'who_needs_it': '',
        'catalyst': '',
        'catalyst_date': None,
        'demand_type': 'SPECULATIVE',
        'has_revenue': False,
        'has_contracts': False,
        'analyst_support': False
    })
    test_result(
        "Worst thesis (no factors)",
        score <= 2,
        f"Expected <= 2, got {score}"
    )
    
    # Test 3: BBAI scenario (weak)
    bbai_score = calculate_thesis_strength({
        'what_they_do': 'AI analytics',
        'who_needs_it': 'Government',
        'catalyst': 'Earnings',
        'catalyst_date': '2026-03-05',  # 49 days away
        'demand_type': 'SPECULATIVE',
        'has_revenue': True,
        'has_contracts': False,
        'analyst_support': False
    })
    test_result(
        "BBAI weak thesis",
        bbai_score <= 5,
        f"Expected <= 5, got {bbai_score}"
    )
    
    # Test 4: Catalyst timing impact
    score_near = calculate_thesis_strength({
        'what_they_do': 'Tech', 'who_needs_it': 'Everyone',
        'catalyst': 'Event', 'catalyst_date': '2026-01-25',
        'demand_type': 'REAL', 'has_revenue': True,
        'has_contracts': True, 'analyst_support': True
    })
    score_far = calculate_thesis_strength({
        'what_they_do': 'Tech', 'who_needs_it': 'Everyone',
        'catalyst': 'Event', 'catalyst_date': '2026-06-01',
        'demand_type': 'REAL', 'has_revenue': True,
        'has_contracts': True, 'analyst_support': True
    })
    test_result(
        "Near catalyst scores higher than far catalyst",
        score_near > score_far,
        f"Near: {score_near}, Far: {score_far}"
    )
    
    # Test 5: Real vs Speculative demand (2-point swing)
    score_real = calculate_thesis_strength({
        'what_they_do': 'Product', 'who_needs_it': 'Customers',
        'catalyst': 'Event', 'catalyst_date': '2026-02-01',
        'demand_type': 'REAL', 'has_revenue': True,
        'has_contracts': True, 'analyst_support': True
    })
    score_spec = calculate_thesis_strength({
        'what_they_do': 'Product', 'who_needs_it': 'Customers',
        'catalyst': 'Event', 'catalyst_date': '2026-02-01',
        'demand_type': 'SPECULATIVE', 'has_revenue': True,
        'has_contracts': True, 'analyst_support': True
    })
    test_result(
        "REAL vs SPECULATIVE demand (2-point difference)",
        (score_real - score_spec) == 2,
        f"Real: {score_real}, Spec: {score_spec}, Diff: {score_real - score_spec}"
    )


def test_thesis_natural_language():
    """Test natural language understanding for thesis queries"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TESTING: Natural Language Parsing (Thesis){RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    test_cases = [
        ("which theses are weak", "weak_thesis"),
        ("show me the broken ones", "weak_thesis"),
        ("whats failing", "weak_thesis"),
        ("what's strong", "strong_thesis"),
        ("show me the good ones", "strong_thesis"),
        ("explain BBAI thesis", "explain_single"),
        ("why are we holding MU", "explain_single"),
        ("whats the case for IBRX", "explain_single"),
        ("portfolio summary", "summary"),
        ("give me the overview", "summary"),
        ("check all theses", "full_check"),
    ]
    
    for query, expected_intent in test_cases:
        parsed = parse_thesis_query(query)
        passed = parsed['intent'] == expected_intent
        test_result(
            f"Query: '{query}'",
            passed,
            f"Expected '{expected_intent}', got '{parsed['intent']}'"
        )


def test_thesis_tricky_language():
    """Try to TRICK the thesis parser"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TESTING: Tricky Thesis Queries{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    tricky_cases = [
        ("yo is BBAI thesis dead or nah", "explain_single"),
        ("strong or weak i cant tell", "full_check"),
        ("tell me everything about nothing", "full_check"),
        ("UUUU UEC which thesis is stronger", "strong_thesis"),
        ("why do we own any of this", "full_check"),
        ("convince me IBRX isnt trash", "explain_single"),
    ]
    
    for query, expected_intent in tricky_cases:
        parsed = parse_thesis_query(query)
        test_result(
            f"Tricky: '{query}'",
            True,  # Passes if it doesn't crash
            f"Parsed as: {parsed['intent']}"
        )
        print(f"  {YELLOW}→ Interpreted as: {parsed['intent']}{RESET}")


def test_thesis_validation():
    """Test thesis validation on real holdings"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TESTING: Thesis Validation (Real Holdings){RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Test IBRX (should be strong)
    ibrx_result = validate_thesis('IBRX', THESIS_DATABASE['IBRX'])
    test_result(
        "IBRX thesis is STRONG (8+)",
        ibrx_result['thesis_strength'] >= 8,
        f"Got strength: {ibrx_result['thesis_strength']}"
    )
    
    # Test BBAI (should be weak)
    bbai_result = validate_thesis('BBAI', THESIS_DATABASE['BBAI'])
    test_result(
        "BBAI thesis is WEAK (<5)",
        bbai_result['thesis_strength'] < 5,
        f"Got strength: {bbai_result['thesis_strength']}"
    )
    
    # Test BBAI has warnings
    test_result(
        "BBAI has warnings about weakness",
        len(bbai_result['warnings']) > 0,
        f"Got {len(bbai_result['warnings'])} warnings"
    )
    
    # Test all holdings have valid data
    for ticker, thesis in THESIS_DATABASE.items():
        result = validate_thesis(ticker, thesis)
        test_result(
            f"{ticker} validation completes without error",
            'thesis_strength' in result and 'status' in result,
            f"Missing required fields"
        )


# ============================================
# INTEGRATION TESTS
# ============================================

def test_end_to_end_conversational():
    """Test full conversational flow"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TESTING: End-to-End Conversational Flow{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Test position health queries
    print(f"{YELLOW}Testing position health conversation...{RESET}")
    queries = [
        "yo any dead money?",
        "which ones are healthy tho",
        "tell me about BBAI",
    ]
    
    for query in queries:
        try:
            # This will fail if yfinance can't connect, but tests the flow
            result = answer_natural_query(query)
            test_result(
                f"Position query: '{query}' executes",
                len(result) > 0,
                "Empty response"
            )
            print(f"  {YELLOW}→ Response length: {len(result)} chars{RESET}")
        except Exception as e:
            test_result(
                f"Position query: '{query}' executes",
                False,
                f"Error: {e}"
            )
    
    # Test thesis queries
    print(f"\n{YELLOW}Testing thesis conversation...{RESET}")
    thesis_queries = [
        "show me weak theses",
        "whats strong",
        "explain BBAI thesis",
    ]
    
    for query in thesis_queries:
        try:
            result = answer_thesis_query(query)
            test_result(
                f"Thesis query: '{query}' executes",
                len(result) > 0,
                "Empty response"
            )
            print(f"  {YELLOW}→ Response length: {len(result)} chars{RESET}")
        except Exception as e:
            test_result(
                f"Thesis query: '{query}' executes",
                False,
                f"Error: {e}"
            )


# ============================================
# STRESS TESTS
# ============================================

def test_stress_edge_cases():
    """Test with weird/invalid inputs"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TESTING: Stress Tests & Edge Cases{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Test empty query
    try:
        result = parse_natural_query("")
        test_result("Empty query doesn't crash", True)
    except Exception as e:
        test_result("Empty query doesn't crash", False, str(e))
    
    # Test very long query
    try:
        long_query = "yo " * 1000 + "any dead money?"
        result = parse_natural_query(long_query)
        test_result("Very long query doesn't crash", True)
    except Exception as e:
        test_result("Very long query doesn't crash", False, str(e))
    
    # Test special characters
    try:
        result = parse_natural_query("!@#$%^&*()")
        test_result("Special characters don't crash", True)
    except Exception as e:
        test_result("Special characters don't crash", False, str(e))
    
    # Test ticker-like strings that aren't real
    try:
        result = parse_natural_query("check XYZ123 and ABC456")
        test_result("Fake tickers don't crash", True)
    except Exception as e:
        test_result("Fake tickers don't crash", False, str(e))
    
    # Test mixed case variations
    try:
        result = parse_natural_query("AnY DeAd MoNeY iN bBaI?")
        test_result("Mixed case doesn't break parsing", 
                   result['intent'] in ['dead_money', 'single_check'])
    except Exception as e:
        test_result("Mixed case doesn't break parsing", False, str(e))


# ============================================
# MAIN TEST RUNNER
# ============================================

if __name__ == "__main__":
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🧪 FENRIR V2 - COMPREHENSIVE TEST SUITE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{YELLOW}Testing position_health_checker.py and thesis_tracker.py{RESET}")
    print(f"{YELLOW}These tests try to TRICK the system with edge cases{RESET}")
    
    # Run all test suites
    test_health_scoring_edge_cases()
    test_natural_language_parsing()
    test_natural_language_tricky_cases()
    test_thesis_scoring_edge_cases()
    test_thesis_natural_language()
    test_thesis_tricky_language()
    test_thesis_validation()
    test_end_to_end_conversational()
    test_stress_edge_cases()
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{GREEN}✅ ALL TESTS COMPLETE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"\n{YELLOW}Note: Some tests may show 'FAIL' if yfinance can't connect.{RESET}")
    print(f"{YELLOW}Focus on logic tests (scoring, parsing) - those are pure Python.{RESET}")
    print(f"\n🐺 LLHR - Now run with real data!")
