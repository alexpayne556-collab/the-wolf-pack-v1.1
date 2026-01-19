# 🐺 FENRIR SECRETARY STRESS TEST
# Validate all 20 training patterns through natural language interface

from natural_language import chat
import traceback

def test_query(query: str, expected_module: str = None) -> dict:
    """Test a single query and capture results"""
    
    print(f"\n{'='*80}")
    print(f"USER: {query}")
    print(f"{'='*80}")
    
    try:
        response = chat(query)
        print(response)
        
        return {
            'query': query,
            'expected_module': expected_module,
            'success': True,
            'response_length': len(response),
            'error': None
        }
    except Exception as e:
        print(f"ERROR: {e}")
        return {
            'query': query,
            'expected_module': expected_module,
            'success': False,
            'error': str(e)
        }

def main():
    results = []
    
    print("[WOLF] FENRIR SECRETARY STRESS TEST")
    print("=" * 80)
    print("Testing natural language interface against 20 training patterns\n")
    
    # TIER 1 - BASIC FUNCTION TESTS
    print("\n" + "=" * 80)
    print("TIER 1 - BASIC FUNCTION TESTS")
    print("=" * 80)
    
    tier1_tests = [
        ("check IBRX", "ticker_analyzer"),
        ("what's happening with $MU", "ticker_analyzer"),
        ("KTOS news", "ticker_analyzer"),
        ("how's the space sector", "sector_tracker"),
        ("nuclear stocks today", "sector_tracker"),
        ("defense plays", "sector_tracker"),
        ("how are my positions", "portfolio"),
        ("what am I holding", "portfolio"),
    ]
    
    for query, module in tier1_tests:
        results.append(test_query(query, module))
    
    # TIER 2 - CONTEXT TESTS (Training Notes #1-10)
    print("\n" + "=" * 80)
    print("TIER 2 - CONTEXT TESTS (Training Notes #1-10)")
    print("=" * 80)
    
    tier2_tests = [
        ("any insider selling on KTOS?", "insider_analyzer"),
        ("check Form 144 filings for my watchlist", "insider_analyzer"),
        ("is IBRX in blue sky?", "level_tracker"),
        ("which stocks broke 52-week highs today?", "level_tracker"),
        ("what catalysts does IBRX have?", "catalyst_stacker"),
        ("show me stocks with multiple catalysts", "catalyst_stacker"),
        ("if CEG is down, what happens to UEC?", "sector_chain"),
        ("Trump power news - who gets hurt?", "policy_impact"),
        ("is IBRX volume unusual?", "volume_analyzer"),
        ("show me 3x volume stocks", "volume_analyzer"),
    ]
    
    for query, module in tier2_tests:
        results.append(test_query(query, module))
    
    # TIER 3 - HARD MODE (Training Notes #11-20)
    print("\n" + "=" * 80)
    print("TIER 3 - HARD MODE (Training Notes #11-20)")
    print("=" * 80)
    
    tier3_tests = [
        ("what's moving after hours?", "ah_anomaly_detector"),
        ("any big AH movers I should know about?", "ah_anomaly_detector"),
        ("any reversals today?", "reversal_detector"),
        ("VERO up big but now down - what's happening?", "reversal_detector"),
        ("why is TLN down 11%?", "news_connector"),
        ("connect the news to the move", "news_connector"),
        ("any 13D filings with >50% ownership?", "sec_filing_scanner"),
        ("squeeze setups?", "sec_filing_scanner"),
        ("any unconfirmed rumors moving stocks?", "rumor_tracker"),
        ("is the IVF move real or rumor?", "rumor_tracker"),
        ("summarize today's market", "market_wrap_parser"),
        ("what did Reuters say about MU?", "market_wrap_parser"),
    ]
    
    for query, module in tier3_tests:
        results.append(test_query(query, module))
    
    # TIER 4 - EDGE CASES
    print("\n" + "=" * 80)
    print("TIER 4 - NATURAL LANGUAGE EDGE CASES")
    print("=" * 80)
    
    tier4_tests = [
        ("chekc ibrx", "ticker_analyzer"),  # Typo
        ("whats mu doing", "ticker_analyzer"),  # No caps
        ("ktos good or bad", "ticker_analyzer"),
        ("what should I do", "clarification"),
        ("anything interesting?", "clarification"),
        ("help", "help"),
        ("compare MU and INTC", "comparison"),
        ("IBRX vs KTOS which is better", "comparison"),
        ("what happened today", "market_summary"),
        ("premarket movers tomorrow", "premarket_scanner"),
        ("anything for next week", "calendar"),
    ]
    
    for query, module in tier4_tests:
        results.append(test_query(query, module))
    
    # FAILURE MODE TESTS
    print("\n" + "=" * 80)
    print("FAILURE MODE TESTS (Should Not Crash)")
    print("=" * 80)
    
    failure_tests = [
        ("", "graceful_fail"),
        ("asdfghjkl", "graceful_fail"),
        ("🚀🚀🚀", "graceful_fail"),
        ("buy", "clarification"),
        ("sell", "clarification"),
        ("is it good", "clarification"),
        ("check XYZABC", "graceful_fail"),
        ("what's FAKERTICKER doing", "graceful_fail"),
    ]
    
    for query, module in failure_tests:
        results.append(test_query(query, module))
    
    # SUMMARY
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total = len(results)
    successes = sum(1 for r in results if r['success'])
    failures = total - successes
    
    print(f"\nTotal Queries: {total}")
    print(f"[OK] Successful: {successes} ({successes/total*100:.1f}%)")
    print(f"[FAIL] Failed: {failures} ({failures/total*100:.1f}%)")
    
    # Show failures
    if failures > 0:
        print(f"\n[FAIL] FAILED QUERIES:")
        for r in results:
            if not r['success']:
                print(f"  - {r['query']}")
                print(f"    Error: {r['error']}")
    
    # Module coverage
    print(f"\nMODULE COVERAGE:")
    modules_expected = set(r['expected_module'] for r in results if r['expected_module'])
    print(f"  Modules tested: {len(modules_expected)}")
    print(f"  Modules to build: {', '.join(sorted(modules_expected))}")
    
    print(f"\n[WOLF] Stress test complete!\n")
    
    return results


if __name__ == '__main__':
    results = main()
