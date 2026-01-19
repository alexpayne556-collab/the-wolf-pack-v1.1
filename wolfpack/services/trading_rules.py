#!/usr/bin/env python3
"""
THE 10 COMMANDMENTS - Trading Rules Enforcer

This module enforces the Market Wizards' wisdom as HARD RULES.
Based on 50+ years of experience from PTJ, Livermore, Kovner, Seykota, etc.

These are not suggestions. These are LAW.
"""

import yfinance as yf
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

class RuleViolation(Enum):
    """Types of rule violations"""
    RISK_TOO_HIGH = "risk_too_high"  # Commandment 3: Risk > 2%
    NO_EXIT_PLAN = "no_exit_plan"  # Commandment 4: No stop loss
    BAD_RR_RATIO = "bad_rr_ratio"  # 5:1 rule violated
    BELOW_200MA = "below_200ma"  # PTJ's rule: Below 200-day MA
    OVERTRADING = "overtrading"  # Commandment 7: Too many trades
    CHASING = "chasing"  # Commandment 6: Ego-driven entry
    
@dataclass
class RuleCheck:
    """Result of checking a trade against the commandments"""
    passed: bool
    rule_violated: Optional[RuleViolation]
    reasoning: str
    severity: str  # 'BLOCK' or 'WARNING'

class TenCommandments:
    """
    Enforces the 10 Commandments of Trading
    
    Every trade MUST pass these checks before execution.
    This is the wisdom layer - prevents us from doing stupid shit.
    """
    
    def __init__(self, account_value: float = 100000):
        self.account_value = account_value
        self.max_risk_pct = 0.02  # Commandment 3: Max 2% risk per trade
        self.min_rr_ratio = 5.0  # PTJ's 5:1 rule
        
    def check_commandment_3_risk_limit(self, risk_dollars: float) -> RuleCheck:
        """
        Commandment 3: Risk 1-2% max per trade (Kovner, Dennis)
        
        "Survive losing streaks. 10 losses in a row = still alive"
        """
        
        max_risk = self.account_value * self.max_risk_pct
        risk_pct = (risk_dollars / self.account_value) * 100
        
        if risk_dollars > max_risk:
            return RuleCheck(
                passed=False,
                rule_violated=RuleViolation.RISK_TOO_HIGH,
                reasoning=f"🚫 COMMANDMENT 3 VIOLATED: Risking ${risk_dollars:.0f} ({risk_pct:.1f}%) > max ${max_risk:.0f} (2%)\n"
                         f"   Kovner: 'Risk control is the most important thing'\n"
                         f"   BLOCKED - Reduce position size",
                severity='BLOCK'
            )
        
        return RuleCheck(
            passed=True,
            rule_violated=None,
            reasoning=f"✅ Risk ${risk_dollars:.0f} ({risk_pct:.1f}%) within 2% limit",
            severity='OK'
        )
    
    def check_commandment_4_exit_plan(self, entry: float, stop: Optional[float]) -> RuleCheck:
        """
        Commandment 4: Know exit before entry (Kovner, Schwartz)
        
        "How much can I LOSE? comes before How much can I make?"
        """
        
        if stop is None or stop <= 0:
            return RuleCheck(
                passed=False,
                rule_violated=RuleViolation.NO_EXIT_PLAN,
                reasoning=f"🚫 COMMANDMENT 4 VIOLATED: No stop loss defined\n"
                         f"   Kovner: 'The first thing I do is figure out how much money I could lose'\n"
                         f"   BLOCKED - Define your stop loss FIRST",
                severity='BLOCK'
            )
        
        if stop >= entry:
            return RuleCheck(
                passed=False,
                rule_violated=RuleViolation.NO_EXIT_PLAN,
                reasoning=f"🚫 COMMANDMENT 4 VIOLATED: Stop ${stop:.2f} >= Entry ${entry:.2f}\n"
                         f"   That's not a stop loss, that's a stop GAIN\n"
                         f"   BLOCKED - Fix your exit plan",
                severity='BLOCK'
            )
        
        return RuleCheck(
            passed=True,
            rule_violated=None,
            reasoning=f"✅ Exit plan defined: Stop at ${stop:.2f}",
            severity='OK'
        )
    
    def check_5to1_rule(self, entry: float, stop: float, target: float) -> RuleCheck:
        """
        PTJ's 5:1 Risk/Reward Rule
        
        "5:1 means I'm risking one dollar to make five. I can be wrong 80% of 
        the time, and I'm still not going to lose."
        """
        
        risk = entry - stop
        reward = target - entry
        
        if risk <= 0:
            return RuleCheck(
                passed=False,
                rule_violated=RuleViolation.BAD_RR_RATIO,
                reasoning=f"🚫 5:1 RULE VIOLATED: Risk ${risk:.2f} <= 0 (impossible)\n"
                         f"   Check your entry/stop prices",
                severity='BLOCK'
            )
        
        rr_ratio = reward / risk
        
        if rr_ratio < self.min_rr_ratio:
            return RuleCheck(
                passed=False,
                rule_violated=RuleViolation.BAD_RR_RATIO,
                reasoning=f"🚫 5:1 RULE VIOLATED: R/R {rr_ratio:.1f}:1 < minimum {self.min_rr_ratio:.0f}:1\n"
                         f"   Risk: ${risk:.2f} | Reward: ${reward:.2f}\n"
                         f"   PTJ: 'I can be wrong 80% of the time and still not lose'\n"
                         f"   BLOCKED - Need better R/R or skip this trade",
                severity='BLOCK'
            )
        
        return RuleCheck(
            passed=True,
            rule_violated=None,
            reasoning=f"✅ R/R {rr_ratio:.1f}:1 exceeds 5:1 minimum (Risk: ${risk:.2f}, Reward: ${reward:.2f})",
            severity='OK'
        )
    
    def check_200day_ma_rule(self, ticker: str, current_price: float) -> RuleCheck:
        """
        PTJ's 200-Day Moving Average Rule
        
        "My metric for everything I look at is the 200-day moving average. 
        If you use the 200-day moving average rule, then you get out."
        
        This is the FINAL EXIT TRIGGER - thesis broken.
        """
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            
            if len(hist) < 200:
                return RuleCheck(
                    passed=True,
                    rule_violated=None,
                    reasoning=f"⚠️ Not enough data for 200-day MA (only {len(hist)} days)",
                    severity='WARNING'
                )
            
            ma_200 = hist['Close'].tail(200).mean()
            pct_from_ma = ((current_price - ma_200) / ma_200) * 100
            
            if current_price < ma_200:
                return RuleCheck(
                    passed=False,
                    rule_violated=RuleViolation.BELOW_200MA,
                    reasoning=f"🚨 PTJ'S 200-MA RULE: Price ${current_price:.2f} below 200-MA ${ma_200:.2f} ({pct_from_ma:+.1f}%)\n"
                             f"   PTJ: 'The whole trick in investing is: How do I keep from losing everything?'\n"
                             f"   WARNING - Consider exit. Thesis may be broken.",
                    severity='WARNING'  # Warning not block (this is for exits, not entries)
                )
            
            return RuleCheck(
                passed=True,
                rule_violated=None,
                reasoning=f"✅ Above 200-MA ${ma_200:.2f} by {pct_from_ma:+.1f}% (thesis intact)",
                severity='OK'
            )
            
        except Exception as e:
            return RuleCheck(
                passed=True,
                rule_violated=None,
                reasoning=f"⚠️ Could not check 200-MA: {e}",
                severity='WARNING'
            )
    
    def check_all_commandments(
        self, 
        ticker: str,
        entry_price: float,
        stop_price: Optional[float],
        target_price: float,
        shares: int
    ) -> Tuple[bool, list[RuleCheck]]:
        """
        Check ALL commandments before executing a trade
        
        Returns:
            (can_proceed, list_of_checks)
        """
        
        checks = []
        
        # Calculate risk
        if stop_price:
            risk_per_share = entry_price - stop_price
            total_risk = shares * risk_per_share
        else:
            total_risk = shares * entry_price * 0.10  # Assume 10% if no stop
        
        # Commandment 3: Risk limit
        checks.append(self.check_commandment_3_risk_limit(total_risk))
        
        # Commandment 4: Exit plan
        checks.append(self.check_commandment_4_exit_plan(entry_price, stop_price))
        
        # 5:1 Rule
        if stop_price:
            checks.append(self.check_5to1_rule(entry_price, stop_price, target_price))
        
        # PTJ's 200-MA Rule
        checks.append(self.check_200day_ma_rule(ticker, entry_price))
        
        # Determine if we can proceed
        can_proceed = all(
            check.passed or check.severity == 'WARNING' 
            for check in checks
        )
        
        return (can_proceed, checks)

def format_commandments_report(checks: list[RuleCheck]) -> str:
    """Format commandment checks for display"""
    
    report = "\n" + "=" * 70 + "\n"
    report += "📜 THE 10 COMMANDMENTS - RULE CHECK\n"
    report += "=" * 70 + "\n"
    
    blocks = [c for c in checks if c.severity == 'BLOCK' and not c.passed]
    warnings = [c for c in checks if c.severity == 'WARNING' and not c.passed]
    passed = [c for c in checks if c.passed]
    
    if blocks:
        report += "\n🚫 BLOCKED VIOLATIONS:\n"
        for check in blocks:
            report += f"\n{check.reasoning}\n"
    
    if warnings:
        report += "\n⚠️  WARNINGS:\n"
        for check in warnings:
            report += f"\n{check.reasoning}\n"
    
    if passed:
        report += "\n✅ PASSED RULES:\n"
        for check in passed:
            report += f"   {check.reasoning}\n"
    
    if blocks:
        report += "\n" + "=" * 70 + "\n"
        report += "❌ TRADE BLOCKED - Fix violations above\n"
        report += "=" * 70 + "\n"
    elif warnings:
        report += "\n" + "=" * 70 + "\n"
        report += "⚠️  TRADE APPROVED WITH WARNINGS - Proceed with caution\n"
        report += "=" * 70 + "\n"
    else:
        report += "\n" + "=" * 70 + "\n"
        report += "✅ ALL COMMANDMENTS PASSED - Trade approved\n"
        report += "=" * 70 + "\n"
    
    return report

# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("📜 THE 10 COMMANDMENTS - RULE ENFORCER TEST")
    print("=" * 70)
    
    rules = TenCommandments(account_value=100000)
    
    # Test 1: Good trade (IBRX example)
    print("\n🧪 TEST 1: IBRX Entry (Good 5:1 Setup)")
    can_proceed, checks = rules.check_all_commandments(
        ticker="IBRX",
        entry_price=3.80,
        stop_price=3.50,
        target_price=5.50,
        shares=500
    )
    print(format_commandments_report(checks))
    
    # Test 2: Risk too high
    print("\n🧪 TEST 2: Risk Too High (Violates Commandment 3)")
    can_proceed, checks = rules.check_all_commandments(
        ticker="AAPL",
        entry_price=150.00,
        stop_price=140.00,
        target_price=200.00,
        shares=300  # $3k risk on $100k = 3%
    )
    print(format_commandments_report(checks))
    
    # Test 3: Bad R/R ratio
    print("\n🧪 TEST 3: Bad R/R (Violates 5:1 Rule)")
    can_proceed, checks = rules.check_all_commandments(
        ticker="TSLA",
        entry_price=250.00,
        stop_price=240.00,  # $10 risk
        target_price=270.00,  # $20 reward = only 2:1
        shares=50
    )
    print(format_commandments_report(checks))
    
    # Test 4: No stop loss
    print("\n🧪 TEST 4: No Stop Loss (Violates Commandment 4)")
    can_proceed, checks = rules.check_all_commandments(
        ticker="NVDA",
        entry_price=500.00,
        stop_price=None,  # No exit plan!
        target_price=600.00,
        shares=20
    )
    print(format_commandments_report(checks))
    
    print("\n" + "=" * 70)
    print("✅ COMMANDMENTS TEST COMPLETE")
    print("=" * 70)
    print("\nThe 10 Commandments protect us from ourselves.")
    print("These rules are LAW. Not suggestions.")
    print("\n🐺 AWOOOO - The wizards' wisdom, automated.")
