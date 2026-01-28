"""
🐺 WOLF PACK TRADING RULES
===========================
Core trading rules learned from Tyr and Fenrir
Updated: January 21, 2026
"""

WOLF_PACK_RULES = {
    
    "test_trade_rule": {
        "name": "2% Test Trade Rule",
        "rule": "Test trades = 2% max position size",
        "reason": "Prove the thesis with small money before scaling",
        "application": [
            "First entry into new setup: 2% max",
            "After 3+ successful trades: Can scale to 5%",
            "Never learn with rent money",
            "Paper trade first if unsure"
        ],
        "example": "If portfolio = $100k, test trade = $2k max position"
    },
    
    "compression_breakout": {
        "name": "Compression Breakout Edge",
        "rule": "Find stocks sleeping (flat + low volume), wait for catalyst, ride the boom",
        "entry": "First pullback to VWAP after initial spike, NOT on the spike",
        "criteria": [
            "Flat for 10+ days (price range <15%)",
            "Low volume (below average)",
            "REAL catalyst arrives (FDA, partnership, data)",
            "Volume explodes (10x+ normal)",
            "Enter on first pullback, not initial spike"
        ],
        "example": "Stock flat $2.00-$2.10 for 2 weeks → FDA news → spikes to $2.80 → pullback to $2.40 VWAP → ENTRY"
    },
    
    "pdufa_runup": {
        "name": "PDUFA Runup Play",
        "rule": "Buy 7-14 days before PDUFA, sell 1-2 days before decision",
        "timing": "Sweet spot: 7-14 days before PDUFA date",
        "exit": "EXIT 1-2 days before decision - avoid binary risk",
        "expected_move": "15-30% runup typical",
        "risk": "If holding through: +20-50% on approval, -40-80% on CRL",
        "application": [
            "Check FDA calendar for upcoming PDUFAs",
            "Enter 10-12 days before",
            "Set profit target at 20-25%",
            "EXIT before binary event unless conviction 9/10"
        ]
    },
    
    "insider_buying": {
        "name": "Follow Smart Money",
        "rule": "Directors buying = They know something",
        "signals": [
            "Multiple buys by same insider = High conviction",
            "Buying near lows = Usually smart timing",
            "Buying before known catalyst = Very bullish",
            "3+ insider buys = STRONG signal"
        ],
        "application": "Track Form 4 filings, follow directors who buy aggressively"
    },
    
    "wounded_prey": {
        "name": "Wounded Prey Setup",
        "rule": "20-40% off highs + healthy chart + catalyst",
        "criteria": [
            "Down 20-40% from 52-week high",
            "Reason for drop was EXTERNAL (sector rotation, not company)",
            "Chart showing support/accumulation",
            "New catalyst approaching",
            "Relative strength building"
        ],
        "entry": "Breakout above resistance or on catalyst news"
    },
    
    "head_hunter": {
        "name": "Head Hunter Setup (Short Squeeze)",
        "rule": "Low float + catalyst + high short interest = Explosion",
        "criteria": [
            "Float <50M shares (ideally <20M)",
            "Short interest >20%",
            "REAL catalyst (not just hype)",
            "Volume building",
            "Above key moving average"
        ],
        "warning": "High risk - use tight stops, can reverse violently"
    },
    
    "gap_and_go_runner": {
        "name": "Gap-and-Go Runner",
        "rule": "Premarket gap holding + volume = Runner at open",
        "process": [
            "4 AM scan finds 5%+ gaps",
            "Check news - REAL catalyst?",
            "Check chart - Was it FLAT before?",
            "Check volume - Is it 10x+ normal?",
            "6 AM recheck - Gap still holding?",
            "9:15 AM - Final decision",
            "9:30 AM - Execute if ALL criteria met"
        ],
        "entry": "First pullback after open, not initial spike",
        "stop": "Below premarket low"
    },
    
    "biotech_formula": {
        "name": "The Biotech Formula",
        "formula": "LOW FLOAT + FDA CATALYST + POSITIVE NEWS = 100-500%",
        "application": [
            "Find low float biotech (<50M)",
            "Upcoming FDA catalyst (PDUFA, Phase data)",
            "Positive trial data or FDA meeting result",
            "Enter on compression breakout or runup",
            "Exit before binary event or on target hit"
        ]
    },
    
    "risk_management": {
        "name": "Risk Management Rules",
        "rules": [
            "Max 5% per position (2% for test trades)",
            "Stop loss ALWAYS set",
            "Never risk more than 1-2% of portfolio per trade",
            "Max 3 biotech positions at once (binary risk)",
            "If down 3 trades in row = STOP, analyze mistakes",
            "Never average down on biotech (binary events)",
            "Max 20% portfolio in speculative plays"
        ]
    },
    
    "position_sizing": {
        "name": "Position Sizing Guide",
        "guide": {
            "Test trades (new setup)": "2%",
            "Proven setups (3+ wins)": "5%",
            "High conviction (9/10)": "7%",
            "Binary events (PDUFA hold-through)": "3% max",
            "Blue chips / hedges": "10-15%"
        }
    },
    
    "trade_process": {
        "name": "The Wolf Pack Process",
        "steps": [
            "1. SCAN: 4 AM premarket or catalyst calendar",
            "2. VERIFY: Check chart - Was it FLAT before?",
            "3. CATALYST: Is news REAL? (FDA, deal, data)",
            "4. VOLUME: Is volume 10x+ normal?",
            "5. PATTERN: Does it match a Wolf Pack setup?",
            "6. ENTRY: First pullback, not spike",
            "7. STOP: Set immediately",
            "8. TARGET: Know exit before entry",
            "9. SIZE: 2% test OR 5% proven",
            "10. EXECUTE: Follow the plan"
        ]
    },
    
    "mistakes_to_avoid": {
        "name": "Common Mistakes",
        "mistakes": [
            "❌ Chasing spikes - Wait for pullback",
            "❌ Buying on old news - Need fresh catalyst",
            "❌ No stop loss - Always protect capital",
            "❌ Oversizing - Start small, scale up",
            "❌ Averaging down biotech - Adds to losers",
            "❌ Trading at night - Wait for 4 AM data",
            "❌ Holding through binary events - Exit before unless 9/10 conviction",
            "❌ FOMO - Missing a trade is better than losing money"
        ]
    }
}


def get_rule(rule_name: str) -> dict:
    """Get a specific rule"""
    return WOLF_PACK_RULES.get(rule_name, {})


def get_all_rules() -> dict:
    """Get all rules"""
    return WOLF_PACK_RULES


def print_rules():
    """Print all rules in readable format"""
    print("\n" + "="*70)
    print("🐺 WOLF PACK TRADING RULES")
    print("="*70 + "\n")
    
    for rule_id, rule in WOLF_PACK_RULES.items():
        print(f"📝 {rule.get('name', rule_id)}")
        print("-" * 50)
        
        if 'rule' in rule:
            print(f"RULE: {rule['rule']}")
        
        if 'formula' in rule:
            print(f"FORMULA: {rule['formula']}")
        
        if 'timing' in rule:
            print(f"TIMING: {rule['timing']}")
        
        if 'entry' in rule:
            print(f"ENTRY: {rule['entry']}")
        
        if 'criteria' in rule:
            print("CRITERIA:")
            for c in rule['criteria']:
                print(f"  • {c}")
        
        if 'application' in rule:
            print("APPLICATION:")
            for a in rule['application']:
                print(f"  • {a}")
        
        if 'rules' in rule:
            print("RULES:")
            for r in rule['rules']:
                print(f"  • {r}")
        
        print()


if __name__ == '__main__':
    print_rules()
