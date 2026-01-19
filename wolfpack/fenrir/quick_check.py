"""
Quick portfolio check - NO OLLAMA, just raw data
"""
from position_health_checker import check_all_positions, HOLDINGS
from thesis_tracker import THESIS_DATABASE

print("=" * 60)
print("🐺 FENRIR - QUICK PORTFOLIO CHECK")
print("=" * 60)

print("\n📊 POSITION HEALTH:")
print("-" * 60)
health_results = check_all_positions()
for result in health_results:
    ticker = result.get('ticker', 'UNKNOWN')
    score = result.get('health_score', 0)
    pnl = result.get('pnl_percent', 0)
    status = result.get('status', 'UNKNOWN')
    
    print(f"{ticker:6} | Score: {score:+3} | P/L: {pnl:+6.1f}% | {status}")

print("\n🎯 THESIS VALIDATION:")
print("-" * 60)
for ticker in HOLDINGS.keys():
    if ticker in THESIS_DATABASE:
        thesis = THESIS_DATABASE[ticker]
        strength = thesis.thesis_strength
        demand = thesis.demand_type
        
        if strength >= 8:
            status = "💪 STRONG"
        elif strength >= 5:
            status = "🟡 MODERATE"
        else:
            status = "🔴 WEAK"
        
        print(f"{ticker:6} | Thesis: {strength:2}/10 | Demand: {demand:12} | {status}")

print("\n" + "=" * 60)
print("🎯 BOTTOM LINE:")
print("=" * 60)

# Find dead money
dead_money = [r.get('ticker') for r in health_results if r.get('health_score', 0) <= -5]
weak_thesis = [ticker for ticker in HOLDINGS.keys() if ticker in THESIS_DATABASE and THESIS_DATABASE[ticker].thesis_strength < 5]

if dead_money:
    print(f"🔴 DEAD MONEY: {', '.join(dead_money)}")
else:
    print("✅ NO DEAD MONEY")

if weak_thesis:
    print(f"⚠️  WEAK THESIS: {', '.join(weak_thesis)}")
else:
    print("✅ ALL THESES STRONG")

# Find runners
runners = [r.get('ticker') for r in health_results if r.get('health_score', 0) >= 5]
if runners:
    print(f"🔥 RUNNING HOT: {', '.join(runners)}")

print("=" * 60)
