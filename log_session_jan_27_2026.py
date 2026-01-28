#!/usr/bin/env python3
"""
🐺 SESSION LOGGER - January 27, 2026
Log complete trading session to unified learning engine

This script:
1. Logs all trades from today (DNN, IBRX, RDW, MRNO)
2. Records infrastructure built (Discord, Ko-fi, GitHub)
3. Documents discoveries (extended hours blindspot, stale intel danger)
4. Establishes trading philosophy and rules
5. Saves portfolio snapshot
6. Creates session memory for future learning
"""

import json
import os
import sys
from datetime import datetime

# Add wolfpack to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wolfpack.services.learning_engine import LearningEngine
from wolfpack.database import get_connection, log_trade, init_database, update_trade_outcome

# =============================================================================
# SESSION DATA - JANUARY 27, 2026
# =============================================================================

SESSION_DATA = {
    "session_id": "session_2026_01_27_evening",
    "session_date": "2026-01-27",
    "session_time": "17:30-19:30_ET",
    "participants": ["tyr_human", "fenrir_research_ai"],
    "session_type": "infrastructure_build_and_trade_review"
}

TRADES_DATA = [
    {
        "ticker": "DNN",
        "entry_date": "2026-01-27",
        "entry_price": 1.85,
        "entry_convergence": 45,
        "entry_signals": ["stale_catalyst_intel", "no_fresh_verification"],
        "shares": 27,
        "position_size_pct": 6.3,
        "pivotal_point_score": 3,
        "volume_ratio": 1.2,
        "consolidation_days": 0,
        "exit_date": "2026-01-27",
        "exit_price": 1.78,
        "exit_reason": "panic_sell_on_red_morning",
        "outcome": "early_exit",
        "return_pct": -3.78,
        "return_dollars": -1.89,
        "days_held": 0,
        "max_drawdown_pct": 5.0,
        "post_exit_price": 1.90,
        "post_exit_gain_missed": 6.49,
        "lessons_learned": [
            "Intel was stale - CNSC hearing already happened Dec 11 2025",
            "Decision expected Q1 2026 not 'any day'",
            "Fenrir repeated old info without verification",
            "Panic sold on red when thesis wasnt broken",
            "Same day stock ran +6.49% after exit"
        ],
        "rule_violations": [
            "Bought on unverified catalyst timing",
            "Sold on emotion not thesis break",
            "No stop loss set before entry"
        ],
        "warning_signs_ignored": [
            "Low convergence score (45)",
            "Weak volume confirmation (1.2x)",
            "Zero consolidation days"
        ]
    },
    {
        "ticker": "IBRX",
        "entry_date": "2026-01-09",
        "entry_price": 3.80,
        "entry_convergence": 85,
        "entry_signals": ["biotech_catalyst", "wounded_prey_pattern", "volume_spike"],
        "shares": 50,
        "position_size_pct": 12.0,
        "pivotal_point_score": 8,
        "volume_ratio": 2.8,
        "consolidation_days": 21,
        "exit_date": None,
        "exit_price": None,
        "exit_reason": "still_holding",
        "outcome": "open_position",
        "return_pct": 55.26,
        "return_dollars": 105.0,
        "days_held": 18,
        "max_drawdown_pct": 8.0,
        "current_price": 5.90,
        "lessons_learned": [
            "Thesis-driven hold through volatility works",
            "High convergence + volume confirmation = stronger setup",
            "Wounded prey pattern showing real edge",
            "Patience over panic"
        ],
        "success_factors": [
            "High convergence at entry (85)",
            "Strong volume confirmation (2.8x)",
            "Extended consolidation (21 days)",
            "Held through noise"
        ]
    },
    {
        "ticker": "RDW",
        "entry_date": "2026-01-27",
        "entry_price": 3.94,
        "entry_convergence": 78,
        "entry_signals": ["defense_sector_momentum", "geopolitical_tailwind"],
        "shares": 3.583,
        "position_size_pct": 1.8,
        "pivotal_point_score": 6,
        "volume_ratio": 1.8,
        "consolidation_days": 14,
        "exit_date": None,
        "exit_price": None,
        "exit_reason": "still_holding",
        "outcome": "open_position",
        "return_pct": 29.56,
        "return_dollars": 4.17,
        "days_held": 0,
        "max_drawdown_pct": 0,
        "current_price": 5.11,
        "lessons_learned": [
            "Defense sector running on policy tailwinds",
            "Small position but thesis intact"
        ],
        "success_factors": [
            "Sector momentum alignment",
            "Clear catalyst (geopolitical)"
        ]
    },
    {
        "ticker": "MRNO",
        "entry_date": "2026-01-27",
        "entry_price": 1.05,
        "entry_convergence": 55,
        "entry_signals": ["momentum_play", "volume_spike", "small_position"],
        "shares": 3,
        "position_size_pct": 0.4,
        "pivotal_point_score": 4,
        "volume_ratio": 3.5,
        "consolidation_days": 0,
        "exit_date": None,
        "exit_price": None,
        "exit_reason": "still_holding",
        "outcome": "open_position",
        "return_pct": 111.43,
        "return_dollars": 3.51,
        "days_held": 0,
        "max_drawdown_pct": 0,
        "current_price": 2.22,
        "management_rules": {
            "above_2.20": "hold_for_continuation",
            "between_2.00_2.20": "watch_closely",
            "below_1.80": "cut_position"
        },
        "lessons_learned": [
            "Small speculative positions can run big",
            "Volume spike was real signal",
            "Extended hours data not visible on Fidelity heatmap"
        ]
    }
]

INFRASTRUCTURE_BUILT = {
    "discord": {
        "server_name": "Wolf Pack Trading",
        "invite_link": "https://discord.gg/nwbRMwKjmm",
        "expires": "never",
        "status": "live",
        "purpose": "community_hub_for_traders_and_developers"
    },
    "kofi": {
        "page_url": "https://ko-fi.com/wolfpack617",
        "category": "science_and_tech",
        "payment_method": "paypal",
        "status": "live",
        "purpose": "funding_for_api_costs_and_infrastructure"
    },
    "github": {
        "repo_url": "https://github.com/alexpayne556-collab/the-wolf-pack-v1.1",
        "commits": 473,
        "status": "active_development",
        "needs_update": ["add_discord_link_to_readme", "add_kofi_link_to_readme"]
    }
}

DISCOVERIES = {
    "extended_hours_blindspot": {
        "problem": "Fidelity heatmaps do NOT update with extended hours trading",
        "example": "MRNO showed +56.30% on heatmap but was actually +111.75% after-hours",
        "solution": "Build Wolf Pack Heatmap tool with Finnhub WebSocket for real-time extended hours data",
        "priority": "high"
    },
    "stale_intel_danger": {
        "problem": "AI repeated old catalyst info without verification",
        "example": "DNN CNSC hearing already happened Dec 11 2025, not upcoming",
        "solution": "All intel must be timestamped and verified fresh before acting",
        "rule": "No 'any day' language - real timelines or 'unknown'"
    },
    "cash_debit_explanation": {
        "what_it_means": "T+1 settlement creates temporary debit until trade settles",
        "example": "-$50.59 debit = committed funds from RDW purchase, not actual negative balance",
        "resolution": "Settles next trading day"
    }
}

PHILOSOPHY = {
    "honesty_framework": {
        "question_asked": "If we are trading and the system learns from our trades, is it a lie to say the system made decisions?",
        "answer": "NO - human decisions become training data, AI learns patterns from outcomes",
        "honest_statements": [
            "I made this trade. I'm documenting it. The system is learning from my decisions.",
            "I'm building a system that learns from real trades.",
            "The system improves as I feed it more data."
        ],
        "dishonest_statements": [
            "The AI system predicted this winner (when human decided)",
            "Showing only wins, hiding losses",
            "Claiming automation that doesn't exist"
        ],
        "truth": "Right now the HUMAN is the system. Human judgment becomes training data."
    },
    "transparency_commitment": [
        "Document EVERY trade: entry, exit, thesis, outcome",
        "Post wins AND losses publicly",
        "Show the learning process, not just results",
        "Let the work speak for itself"
    ]
}

PACK_RULES = [
    "We win together, lose together. Every dollar is OUR dollar.",
    "No lazy research. All intel timestamped and verified fresh.",
    "No panic sells. Thesis didn't break = hold through noise.",
    "Document everything. Wins, losses, reasoning - all public.",
    "Build for everyone. Tools for people who can't afford institutional shit."
]

TRADING_RULES_REINFORCED = [
    "10% mandatory stop loss on all positions",
    "Verify catalyst timing before entry",
    "Sell no-thesis positions immediately",
    "Small speculative positions only (<2% of portfolio)"
]

PORTFOLIO_SNAPSHOT = {
    "snapshot_id": "portfolio_2026_01_28_0100",
    "timestamp": "2026-01-28T01:00:00-05:00",
    "total_portfolio_value": 1555.60,
    "robinhood_value": 795.12,
    "fidelity_value": 760.48,
    "total_cash_available": 57.35,
    "total_positions": 9,
    "sectors_exposed": [
        "AI_memory",
        "defense_drones", 
        "defense_space",
        "nuclear_uranium",
        "nuclear_rare_earth",
        "biotech",
        "momentum_speculative"
    ]
}

PENDING_ACTIONS = [
    {
        "action": "SELL",
        "ticker": "NTLA",
        "shares": 2,
        "reason": "No thesis - cutting no-thesis positions",
        "timing": "Market open Jan 28, 2026"
    }
]

VALIDATED_PATTERNS = {
    "working": [
        "IBRX wounded prey pattern (55%+ gain, still holding)",
        "Thesis-driven holds outperforming speculation",
        "Defense sector timing on policy catalysts"
    ],
    "not_working": [
        "Random micro-cap speculation (DNN loss pattern)",
        "Buying on stale intel without verification",
        "Panic selling on red days when thesis intact"
    ]
}

KEY_INSIGHT = "The edge isn't in finding universal patterns but in understanding which specific stocks have 'continuation DNA' versus those that mean-revert. Document everything, learn from outcomes, adjust the model."


# =============================================================================
# LOGGING FUNCTIONS
# =============================================================================

def log_trades_to_learning_engine(engine: LearningEngine):
    """Log all trades from session to learning engine"""
    print("\n" + "="*70)
    print("📝 LOGGING TRADES TO LEARNING ENGINE")
    print("="*70)
    
    for trade in TRADES_DATA:
        ticker = trade['ticker']
        entry_price = trade['entry_price']
        shares = trade['shares']
        convergence = trade['entry_convergence']
        
        # Log entry
        print(f"\n🔵 LOGGING ENTRY: {ticker}")
        print(f"   Date: {trade['entry_date']}")
        print(f"   Price: ${entry_price:.2f}")
        print(f"   Shares: {shares}")
        print(f"   Convergence: {convergence}/100")
        print(f"   Signals: {', '.join(trade['entry_signals'])}")
        
        # Create thesis string
        signals_str = " + ".join(trade['entry_signals'])
        thesis = f"Convergence {convergence}/100 | Signals: {signals_str}"
        
        # Log to database
        log_trade(
            ticker=ticker,
            action='BUY',
            shares=shares,
            price=entry_price,
            thesis=thesis,
            notes=json.dumps({
                'convergence': convergence,
                'signals': trade['entry_signals'],
                'volume_ratio': trade['volume_ratio'],
                'consolidation_days': trade['consolidation_days'],
                'pivotal_point_score': trade['pivotal_point_score']
            })
        )
        
        # If trade is closed, log exit
        if trade['exit_date']:
            print(f"\n🔴 LOGGING EXIT: {ticker}")
            print(f"   Exit Date: {trade['exit_date']}")
            print(f"   Exit Price: ${trade['exit_price']:.2f}")
            print(f"   Return: {trade['return_pct']:+.2f}%")
            print(f"   Outcome: {trade['outcome']}")
            print(f"   Reason: {trade['exit_reason']}")
            
            # Log lessons learned
            if 'lessons_learned' in trade and trade['lessons_learned']:
                print(f"   Lessons:")
                for lesson in trade['lessons_learned']:
                    print(f"      • {lesson}")
            
            # Log rule violations
            if 'rule_violations' in trade and trade['rule_violations']:
                print(f"   Rule Violations:")
                for violation in trade['rule_violations']:
                    print(f"      ⚠️  {violation}")
            
            log_trade(
                ticker=ticker,
                action='SELL',
                shares=shares,
                price=trade['exit_price'],
                thesis=trade['exit_reason'],
                notes=json.dumps({
                    'outcome': trade['outcome'],
                    'days_held': trade['days_held'],
                    'max_drawdown_pct': trade['max_drawdown_pct'],
                    'lessons_learned': trade.get('lessons_learned', []),
                    'rule_violations': trade.get('rule_violations', []),
                    'warning_signs_ignored': trade.get('warning_signs_ignored', []),
                    'post_exit_price': trade.get('post_exit_price'),
                    'post_exit_gain_missed': trade.get('post_exit_gain_missed')
                })
            )
        else:
            # Open position
            print(f"   Status: OPEN POSITION (+{trade['return_pct']:.2f}%)")
            print(f"   Current Price: ${trade['current_price']:.2f}")
            
            # Log success factors for winners
            if 'success_factors' in trade and trade['success_factors']:
                print(f"   Success Factors:")
                for factor in trade['success_factors']:
                    print(f"      ✅ {factor}")


def save_session_memory():
    """Save complete session data as JSON for future reference"""
    print("\n" + "="*70)
    print("💾 SAVING SESSION MEMORY")
    print("="*70)
    
    os.makedirs("memory/brokkr-memory", exist_ok=True)
    
    session_memory = {
        "session": SESSION_DATA,
        "trades": TRADES_DATA,
        "infrastructure": INFRASTRUCTURE_BUILT,
        "discoveries": DISCOVERIES,
        "philosophy": PHILOSOPHY,
        "pack_rules": PACK_RULES,
        "trading_rules_reinforced": TRADING_RULES_REINFORCED,
        "portfolio_snapshot": PORTFOLIO_SNAPSHOT,
        "pending_actions": PENDING_ACTIONS,
        "validated_patterns": VALIDATED_PATTERNS,
        "key_insight": KEY_INSIGHT
    }
    
    filename = f"memory/brokkr-memory/SESSION-JAN-27-2026.json"
    
    with open(filename, 'w') as f:
        json.dump(session_memory, f, indent=2)
    
    print(f"\n✅ Session memory saved: {filename}")
    print(f"   Trades: {len(TRADES_DATA)}")
    print(f"   Infrastructure: {len(INFRASTRUCTURE_BUILT)} platforms")
    print(f"   Discoveries: {len(DISCOVERIES)} insights")
    print(f"   Rules: {len(PACK_RULES)} pack rules + {len(TRADING_RULES_REINFORCED)} trading rules")


def save_discoveries_doc():
    """Save discoveries as markdown for easy reference"""
    print("\n" + "="*70)
    print("📚 CREATING DISCOVERIES DOCUMENT")
    print("="*70)
    
    doc = []
    doc.append("# 🔍 DISCOVERIES - January 27, 2026\n")
    doc.append(f"**Session Date:** {SESSION_DATA['session_date']}")
    doc.append(f"**Session Time:** {SESSION_DATA['session_time']}")
    doc.append(f"**Session Type:** {SESSION_DATA['session_type']}\n")
    doc.append("---\n")
    
    doc.append("## 🚨 CRITICAL DISCOVERIES\n")
    
    for name, discovery in DISCOVERIES.items():
        doc.append(f"### {name.replace('_', ' ').title()}\n")
        
        # Handle different discovery structures
        if 'problem' in discovery:
            doc.append(f"**Problem:** {discovery['problem']}\n")
        if 'example' in discovery:
            doc.append(f"**Example:** {discovery['example']}\n")
        if 'solution' in discovery:
            doc.append(f"**Solution:** {discovery['solution']}\n")
        if 'what_it_means' in discovery:
            doc.append(f"**What it means:** {discovery['what_it_means']}\n")
        if 'resolution' in discovery:
            doc.append(f"**Resolution:** {discovery['resolution']}\n")
        if 'rule' in discovery:
            doc.append(f"**Rule:** {discovery['rule']}\n")
        if 'priority' in discovery:
            doc.append(f"**Priority:** {discovery['priority']}\n")
        doc.append("")
    
    doc.append("\n---\n")
    doc.append("## 🐺 PACK RULES ESTABLISHED\n")
    for i, rule in enumerate(PACK_RULES, 1):
        doc.append(f"{i}. {rule}")
    
    doc.append("\n\n---\n")
    doc.append("## 📊 VALIDATED PATTERNS\n")
    doc.append("\n### ✅ Working\n")
    for pattern in VALIDATED_PATTERNS['working']:
        doc.append(f"- {pattern}")
    
    doc.append("\n### ❌ Not Working\n")
    for pattern in VALIDATED_PATTERNS['not_working']:
        doc.append(f"- {pattern}")
    
    doc.append("\n\n---\n")
    doc.append(f"## 💡 KEY INSIGHT\n\n{KEY_INSIGHT}\n")
    
    filename = "DISCOVERIES_JAN_27_2026.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(doc))
    
    print(f"\n✅ Discoveries document created: {filename}")


def save_infrastructure_doc():
    """Save infrastructure info as markdown"""
    print("\n" + "="*70)
    print("🏗️ CREATING INFRASTRUCTURE DOCUMENT")
    print("="*70)
    
    doc = []
    doc.append("# 🏗️ WOLF PACK INFRASTRUCTURE\n")
    doc.append(f"**Built:** {SESSION_DATA['session_date']}\n")
    doc.append("---\n")
    
    doc.append("## 💬 Discord Server\n")
    discord = INFRASTRUCTURE_BUILT['discord']
    doc.append(f"**Server Name:** {discord['server_name']}")
    doc.append(f"**Invite Link:** {discord['invite_link']}")
    doc.append(f"**Status:** {discord['status']}")
    doc.append(f"**Purpose:** {discord['purpose']}\n")
    
    doc.append("\n## ☕ Ko-fi Page\n")
    kofi = INFRASTRUCTURE_BUILT['kofi']
    doc.append(f"**Page URL:** {kofi['page_url']}")
    doc.append(f"**Category:** {kofi['category']}")
    doc.append(f"**Payment Method:** {kofi['payment_method']}")
    doc.append(f"**Status:** {kofi['status']}")
    doc.append(f"**Purpose:** {kofi['purpose']}\n")
    
    doc.append("\n## 💻 GitHub Repository\n")
    github = INFRASTRUCTURE_BUILT['github']
    doc.append(f"**Repo URL:** {github['repo_url']}")
    doc.append(f"**Total Commits:** {github['commits']}")
    doc.append(f"**Status:** {github['status']}\n")
    doc.append("**Needs Update:**")
    for item in github['needs_update']:
        doc.append(f"- {item}")
    
    doc.append("\n\n---\n")
    doc.append("## 🎯 Next Steps\n")
    doc.append("1. Add Discord link to README.md")
    doc.append("2. Add Ko-fi link to README.md")
    doc.append("3. Build Wolf Pack Heatmap tool (extended hours)")
    doc.append("4. Implement catalyst timestamp verification")
    doc.append("5. Document DNN lesson in learning engine\n")
    
    filename = "WOLF_PACK_INFRASTRUCTURE.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(doc))
    
    print(f"\n✅ Infrastructure document created: {filename}")


def print_summary():
    """Print session summary"""
    print("\n" + "="*70)
    print("📊 SESSION SUMMARY - January 27, 2026")
    print("="*70 + "\n")
    
    print("🎯 TRADES LOGGED:")
    for trade in TRADES_DATA:
        outcome_emoji = "✅" if trade['return_pct'] > 0 else "❌"
        status = "OPEN" if not trade['exit_date'] else trade['outcome'].upper()
        print(f"   {outcome_emoji} {trade['ticker']}: {trade['return_pct']:+.2f}% ({status})")
    
    print(f"\n🏗️ INFRASTRUCTURE BUILT:")
    print(f"   💬 Discord: {INFRASTRUCTURE_BUILT['discord']['status']}")
    print(f"   ☕ Ko-fi: {INFRASTRUCTURE_BUILT['kofi']['status']}")
    print(f"   💻 GitHub: {INFRASTRUCTURE_BUILT['github']['commits']} commits")
    
    print(f"\n🔍 DISCOVERIES: {len(DISCOVERIES)}")
    for name in DISCOVERIES.keys():
        print(f"   • {name.replace('_', ' ').title()}")
    
    print(f"\n🐺 PACK RULES: {len(PACK_RULES)} established")
    
    print(f"\n💰 PORTFOLIO:")
    print(f"   Total Value: ${PORTFOLIO_SNAPSHOT['total_portfolio_value']:.2f}")
    print(f"   Open Positions: {PORTFOLIO_SNAPSHOT['total_positions']}")
    print(f"   Cash Available: ${PORTFOLIO_SNAPSHOT['total_cash_available']:.2f}")
    
    print(f"\n📋 PENDING ACTIONS:")
    for action in PENDING_ACTIONS:
        print(f"   • {action['action']} {action['ticker']} - {action['reason']}")
    
    print("\n" + "="*70)
    print("✅ ALL DATA LOGGED TO LEARNING ENGINE")
    print("🐺 The wolf that LEARNS is the wolf that WINS.")
    print("="*70 + "\n")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("\n🐺 WOLF PACK - SESSION LOGGER")
    print("   Logging complete session data to learning brain...\n")
    
    # Initialize database first
    print("🔧 Initializing database...")
    init_database()
    print("   ✅ Database ready\n")
    
    # Initialize learning engine
    engine = LearningEngine()
    
    # Log all trades
    log_trades_to_learning_engine(engine)
    
    # Save session memory
    save_session_memory()
    
    # Create documentation
    save_discoveries_doc()
    save_infrastructure_doc()
    
    # Print summary
    print_summary()
    
    print("🎉 SESSION LOGGING COMPLETE!\n")
    print("📂 Files created:")
    print("   • memory/brokkr-memory/SESSION-JAN-27-2026.json")
    print("   • DISCOVERIES_JAN_27_2026.md")
    print("   • WOLF_PACK_INFRASTRUCTURE.md")
    print("\n🧠 All data now available to learning engine for pattern recognition.\n")
