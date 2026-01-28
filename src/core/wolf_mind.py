#!/usr/bin/env python3
"""
WOLF MIND - ONE Consciousness with YOUR Context 🐺🧠

THE SHIFT:
FROM: 10 separate modules giving separate opinions
TO:   ONE MIND that knows YOU and makes ONE decision

THE WOLF DOESN'T HAVE 10 BRAINS. THE WOLF HAS ONE MIND THAT USES ALL ITS SENSES.

WHAT IT KNOWS:
- Your situation (capital, positions, risk tolerance)
- Your state (emotional, win streak, last mistake)
- Your history (best setups, worst tickers, patterns)
- Your goals (learning, protection, preparing for larger portfolio)

WHAT IT DOES:
- Filters every decision through YOUR context
- Speaks FIRST (proactive, not reactive)
- Protects you from yourself
- Teaches as it guides
- Remembers EVERYTHING
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class EmotionalState(Enum):
    CALM = "CALM"
    EXCITED = "EXCITED"
    FEARFUL = "FEARFUL"
    TILTED = "TILTED"
    OVERCONFIDENT = "OVERCONFIDENT"

class ProtectionMode(Enum):
    LOW = "LOW"       # Can afford losses
    MEDIUM = "MEDIUM" # Normal risk tolerance
    HIGH = "HIGH"     # Cannot afford losses

@dataclass
class TraderProfile:
    """Your complete profile - who you are, what you need"""
    
    # Your situation
    name: str
    capital: float
    risk_per_trade_pct: float  # 0.02 = 2%
    max_positions: int
    current_positions: int
    account_heat: float  # % of capital deployed
    
    # Your state
    emotional_state: EmotionalState
    recent_pnl: float
    win_streak: int
    loss_streak: int
    last_mistake: Optional[str]
    last_win: Optional[str]
    
    # Your history
    total_trades: int
    win_rate: float
    best_setups: List[str]  # ['catalyst', 'insider_cluster']
    worst_tickers: List[str]  # Tickers you lose on
    best_time_of_day: str  # 'morning', 'afternoon'
    avg_hold_days: float
    avg_r_multiple: float  # Average R:R achieved
    
    # Your goals
    learning_mode: bool  # True = explain decisions
    protection_mode: ProtectionMode
    preparing_for: str  # 'larger portfolio', 'inheritance'
    
    # Your constraints
    pdt_restricted: bool  # Pattern Day Trader restriction
    disabled: bool  # Can't work traditional job
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        d = asdict(self)
        d['emotional_state'] = self.emotional_state.value
        d['protection_mode'] = self.protection_mode.value
        return d
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary"""
        data['emotional_state'] = EmotionalState(data['emotional_state'])
        data['protection_mode'] = ProtectionMode(data['protection_mode'])
        return cls(**data)

class WolfMind:
    """
    ONE consciousness that knows YOU and makes intelligent decisions
    
    Not a toolbox. A partner that:
    - Knows your situation, state, history
    - Filters decisions through YOUR context
    - Speaks first, doesn't wait
    - Protects you from traps AND yourself
    - Teaches as it guides
    """
    
    def __init__(self, profile_file: str = 'data/trader_profile.json'):
        self.profile_file = profile_file
        self.profile = self.load_profile()
        
        # Memory
        self.trade_history = []
        self.mistake_history = []
        self.session_log = []
        
    def load_profile(self) -> TraderProfile:
        """Load trader profile from file"""
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                data = json.load(f)
            return TraderProfile.from_dict(data)
        else:
            # Create default profile
            return self.create_default_profile()
    
    def create_default_profile(self) -> TraderProfile:
        """Create default profile (customize for Tyr)"""
        return TraderProfile(
            # Situation
            name="Tyr",
            capital=1400.0,
            risk_per_trade_pct=0.02,  # 2% risk = $28/trade
            max_positions=6,
            current_positions=0,
            account_heat=0.0,
            
            # State
            emotional_state=EmotionalState.CALM,
            recent_pnl=0.0,
            win_streak=0,
            loss_streak=0,
            last_mistake=None,
            last_win=None,
            
            # History
            total_trades=0,
            win_rate=0.0,
            best_setups=['catalyst', 'insider_cluster'],
            worst_tickers=[],
            best_time_of_day='morning',
            avg_hold_days=4.0,
            avg_r_multiple=2.0,
            
            # Goals
            learning_mode=True,
            protection_mode=ProtectionMode.HIGH,
            preparing_for='larger portfolio inheritance',
            
            # Constraints
            pdt_restricted=True,
            disabled=True
        )
    
    def save_profile(self):
        """Save trader profile to file"""
        os.makedirs(os.path.dirname(self.profile_file), exist_ok=True)
        with open(self.profile_file, 'w') as f:
            json.dump(self.profile.to_dict(), f, indent=2)
    
    def analyze_opportunity(self, ticker: str, base_score: int, 
                           setup_type: str, catalyst: Optional[str] = None) -> Tuple[bool, str, int]:
        """
        Analyze opportunity through YOUR lens
        
        Args:
            ticker: Stock ticker
            base_score: Raw convergence score (0-100)
            setup_type: Type of setup ('catalyst', 'insider', 'technical', etc.)
            catalyst: Optional catalyst description
            
        Returns:
            (should_trade: bool, reasoning: str, adjusted_score: int)
        """
        reasons = []
        score_adjustments = 0
        warnings = []
        
        # 1. CHECK HISTORY - Do you lose on this ticker?
        if ticker in self.profile.worst_tickers:
            score_adjustments -= 30
            warnings.append(f"⚠️  HISTORY ALERT: You've lost on {ticker} before")
            reasons.append(f"Your track record on {ticker} is negative. Pattern recognition suggests SKIP.")
        
        # 2. CHECK SETUP TYPE - Is this your best setup?
        if setup_type in self.profile.best_setups:
            score_adjustments += 10
            reasons.append(f"✅ This is one of your best setups: {setup_type}")
        
        # 3. CHECK EMOTIONAL STATE - Are you tilted?
        if self.profile.emotional_state == EmotionalState.TILTED:
            score_adjustments -= 20
            warnings.append("⚠️  EMOTIONAL ALERT: You're tilted. Step away.")
            reasons.append("Your emotional state is compromised. Any decision now is suspect.")
        
        elif self.profile.emotional_state == EmotionalState.OVERCONFIDENT:
            score_adjustments -= 15
            warnings.append("⚠️  OVERCONFIDENCE ALERT: Win streak detected")
            reasons.append("You're on a winning streak. This is when mistakes happen. Be extra careful.")
        
        # 4. CHECK WIN STREAK - Overtrade risk?
        if self.profile.win_streak >= 3:
            score_adjustments -= 10
            warnings.append(f"⚠️  WIN STREAK: {self.profile.win_streak} wins in a row - overtrade risk HIGH")
            reasons.append(f"{self.profile.win_streak}-win streak detected. Historically, this is when you overtrade. Consider passing.")
        
        # 5. CHECK LOSS STREAK - Revenge trade risk?
        if self.profile.loss_streak >= 2:
            score_adjustments -= 15
            warnings.append(f"⚠️  LOSS STREAK: {self.profile.loss_streak} losses - revenge trade risk HIGH")
            reasons.append(f"{self.profile.loss_streak} consecutive losses. DO NOT revenge trade. Only take A+ setups.")
        
        # 6. CHECK ACCOUNT HEAT - Too much deployed?
        if self.profile.account_heat > 0.50:  # >50% deployed
            score_adjustments -= 10
            warnings.append(f"⚠️  PORTFOLIO HEAT: {self.profile.account_heat*100:.0f}% deployed")
            reasons.append(f"You have {self.profile.account_heat*100:.0f}% of capital deployed. Leave dry powder for better setups.")
        
        # 7. CHECK POSITIONS - At max?
        if self.profile.current_positions >= self.profile.max_positions:
            warnings.append(f"❌ MAX POSITIONS: {self.profile.current_positions}/{self.profile.max_positions}")
            reasons.append(f"You're at max positions ({self.profile.max_positions}). Can't add unless you close something.")
            return (False, "\n".join(warnings + reasons), base_score + score_adjustments)
        
        # 8. CHECK CAPITAL - Enough for position?
        max_risk = self.profile.capital * self.profile.risk_per_trade_pct
        if max_risk < 20:  # Less than $20 risk
            warnings.append(f"⚠️  LOW CAPITAL: Only ${max_risk:.2f} risk per trade")
            reasons.append(f"With ${self.profile.capital:.0f} capital, your max risk is ${max_risk:.2f}. Consider growing capital first.")
        
        # 9. PROTECTION MODE - Extra checks
        if self.profile.protection_mode == ProtectionMode.HIGH:
            # In HIGH protection, only take 85+ scores after adjustments
            adjusted_score = base_score + score_adjustments
            if adjusted_score < 85:
                warnings.append(f"🛡️  PROTECTION MODE: Score {adjusted_score} < 85 threshold")
                reasons.append(f"Protection mode is HIGH. You can't afford losses. Only taking 85+ setups. This is {adjusted_score}.")
                return (False, "\n".join(warnings + reasons), adjusted_score)
        
        # FINAL DECISION
        adjusted_score = base_score + score_adjustments
        
        # Threshold: 70+ after adjustments
        if adjusted_score >= 70:
            decision = True
            reasons.insert(0, f"✅ ADJUSTED SCORE: {adjusted_score}/100 (base: {base_score}, adj: {score_adjustments:+d})")
            
            # Add teaching moment
            if self.profile.learning_mode:
                reasons.append(f"\n💡 LEARNING: This {setup_type} setup fits your profile. "
                             f"You tend to win on these. Your avg hold is {self.profile.avg_hold_days:.1f} days. "
                             f"Target R:R based on your history: {self.profile.avg_r_multiple:.1f}:1")
        else:
            decision = False
            reasons.insert(0, f"❌ ADJUSTED SCORE: {adjusted_score}/100 (base: {base_score}, adj: {score_adjustments:+d})")
            reasons.append(f"\n💡 SKIP THIS. Score dropped below 70 after adjusting for YOUR context.")
        
        # Format final response
        response = "\n".join(warnings + ["\n"] + reasons if warnings else reasons)
        
        return (decision, response, adjusted_score)
    
    def should_exit(self, ticker: str, entry_price: float, current_price: float,
                   days_held: int, pnl_pct: float) -> Tuple[bool, str]:
        """
        Should you exit this position? (considering YOUR patterns)
        
        Args:
            ticker: Stock ticker
            entry_price: Your entry price
            current_price: Current price
            days_held: Days you've held
            pnl_pct: Current P/L percentage
            
        Returns:
            (should_exit: bool, reasoning: str)
        """
        reasons = []
        
        # 1. CHECK PROFIT TARGET - Based on your avg R:R
        target_pct = self.profile.avg_r_multiple * (self.profile.risk_per_trade_pct * 100)
        
        if pnl_pct >= target_pct:
            reasons.append(f"🎯 PROFIT TARGET HIT: {pnl_pct:.1f}% (target: {target_pct:.1f}%)")
            reasons.append(f"Your average R:R is {self.profile.avg_r_multiple:.1f}:1. This hit your typical target.")
            return (True, "\n".join(reasons))
        
        # 2. CHECK HOLD TIME - Based on your average
        if days_held >= self.profile.avg_hold_days * 1.5:
            reasons.append(f"⏰ HOLD TIME EXCEEDED: {days_held} days (your avg: {self.profile.avg_hold_days:.1f} days)")
            reasons.append(f"You typically hold {self.profile.avg_hold_days:.1f} days. This is {days_held}. If it hasn't moved, it won't.")
            
            if pnl_pct > 0:
                reasons.append(f"💰 You're up {pnl_pct:.1f}%. Take the win and redeploy.")
                return (True, "\n".join(reasons))
            else:
                reasons.append(f"📉 You're down {abs(pnl_pct):.1f}%. Cut it and move on.")
                return (True, "\n".join(reasons))
        
        # 3. CHECK LAST MISTAKE - Is this similar?
        if self.profile.last_mistake and f"Held {ticker} too long" in self.profile.last_mistake:
            reasons.append(f"⚠️  PATTERN ALERT: Last mistake was holding {ticker} too long")
            reasons.append(f"Don't repeat the same mistake. If in doubt, exit.")
            
            if pnl_pct > 5:
                return (True, "\n".join(reasons))
        
        # 4. HOLD
        reasons.append(f"✅ HOLD: {days_held} days, {pnl_pct:+.1f}%")
        reasons.append(f"Within your typical timeframe ({self.profile.avg_hold_days:.1f} days).")
        reasons.append(f"Target: {target_pct:.1f}% (you're at {pnl_pct:.1f}%)")
        
        return (False, "\n".join(reasons))
    
    def update_from_trade(self, ticker: str, entry_date: datetime, exit_date: datetime,
                         entry_price: float, exit_price: float, setup_type: str,
                         won: bool):
        """
        Learn from trade and update profile
        
        Args:
            ticker: Stock ticker
            entry_date: Entry datetime
            exit_date: Exit datetime
            entry_price: Entry price
            exit_price: Exit price
            setup_type: Type of setup
            won: True if profitable, False if loss
        """
        # Update trade count
        self.profile.total_trades += 1
        
        # Update win/loss streaks
        if won:
            self.profile.win_streak += 1
            self.profile.loss_streak = 0
            self.profile.last_win = f"{ticker} on {exit_date.date()}"
            
            # Update emotional state
            if self.profile.win_streak >= 3:
                self.profile.emotional_state = EmotionalState.OVERCONFIDENT
        else:
            self.profile.loss_streak += 1
            self.profile.win_streak = 0
            
            # Track worst tickers
            if ticker not in self.profile.worst_tickers:
                # If lost 2+ times, add to worst tickers
                losses_on_ticker = sum(1 for t in self.trade_history 
                                      if t['ticker'] == ticker and not t['won'])
                if losses_on_ticker >= 2:
                    self.profile.worst_tickers.append(ticker)
            
            # Update emotional state
            if self.profile.loss_streak >= 2:
                self.profile.emotional_state = EmotionalState.TILTED
        
        # Update best setups
        if won and setup_type not in self.profile.best_setups:
            # If won 3+ times on this setup type, add to best setups
            wins_on_setup = sum(1 for t in self.trade_history 
                               if t['setup_type'] == setup_type and t['won'])
            if wins_on_setup >= 3:
                self.profile.best_setups.append(setup_type)
        
        # Update win rate
        total_wins = sum(1 for t in self.trade_history if t['won']) + (1 if won else 0)
        self.profile.win_rate = total_wins / self.profile.total_trades
        
        # Update hold time
        days_held = (exit_date - entry_date).days
        if self.profile.avg_hold_days == 0:
            self.profile.avg_hold_days = days_held
        else:
            self.profile.avg_hold_days = (self.profile.avg_hold_days * 0.8 + days_held * 0.2)
        
        # Update R multiple
        r_multiple = abs((exit_price - entry_price) / entry_price) / self.profile.risk_per_trade_pct
        if won:
            if self.profile.avg_r_multiple == 0:
                self.profile.avg_r_multiple = r_multiple
            else:
                self.profile.avg_r_multiple = (self.profile.avg_r_multiple * 0.8 + r_multiple * 0.2)
        
        # Log trade
        self.trade_history.append({
            'ticker': ticker,
            'entry_date': entry_date.isoformat(),
            'exit_date': exit_date.isoformat(),
            'entry_price': entry_price,
            'exit_price': exit_price,
            'setup_type': setup_type,
            'won': won,
            'days_held': days_held,
            'r_multiple': r_multiple
        })
        
        # Save updated profile
        self.save_profile()
    
    def morning_briefing(self, opportunities: List[Dict], 
                        current_positions: List[Dict]) -> str:
        """
        Generate morning briefing with YOUR context
        
        Args:
            opportunities: List of opportunities from scanner
            current_positions: Your current positions
            
        Returns:
            Formatted briefing string
        """
        briefing = []
        
        briefing.append("="*70)
        briefing.append(f"🐺 WOLF PACK MORNING SCAN - {datetime.now().strftime('%B %d, %Y')}")
        briefing.append("="*70)
        briefing.append(f"Good morning, {self.profile.name}.")
        briefing.append(f"Capital: ${self.profile.capital:,.2f} | Risk/trade: ${self.profile.capital * self.profile.risk_per_trade_pct:.2f}")
        briefing.append(f"Positions: {self.profile.current_positions}/{self.profile.max_positions} | Heat: {self.profile.account_heat*100:.0f}%")
        
        # Emotional state warning
        if self.profile.emotional_state != EmotionalState.CALM:
            briefing.append(f"\n⚠️  EMOTIONAL STATE: {self.profile.emotional_state.value}")
            if self.profile.emotional_state == EmotionalState.OVERCONFIDENT:
                briefing.append(f"   You're on a {self.profile.win_streak}-win streak. Stay disciplined.")
            elif self.profile.emotional_state == EmotionalState.TILTED:
                briefing.append(f"   You've had {self.profile.loss_streak} losses. Take a break.")
        
        briefing.append("\n" + "="*70)
        briefing.append("TOP OPPORTUNITIES:")
        briefing.append("="*70)
        
        # Filter opportunities through YOUR lens
        for i, opp in enumerate(opportunities[:10], 1):
            ticker = opp['ticker']
            base_score = opp['score']
            setup_type = opp.get('setup_type', 'technical')
            
            should_trade, reasoning, adjusted_score = self.analyze_opportunity(
                ticker, base_score, setup_type
            )
            
            briefing.append(f"\n{i}. {ticker} - Score: {adjusted_score}/100 (base: {base_score})")
            briefing.append(f"   Setup: {setup_type}")
            if should_trade:
                briefing.append(f"   ✅ MATCH FOR YOU")
            else:
                briefing.append(f"   ⚠️  FILTERED OUT")
            briefing.append(f"   {reasoning[:100]}...")  # First 100 chars
        
        # Current positions
        if current_positions:
            briefing.append("\n" + "="*70)
            briefing.append("YOUR POSITIONS:")
            briefing.append("="*70)
            
            for pos in current_positions:
                ticker = pos['ticker']
                entry_price = pos['entry_price']
                current_price = pos['current_price']
                days_held = pos['days_held']
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
                
                should_exit, exit_reasoning = self.should_exit(
                    ticker, entry_price, current_price, days_held, pnl_pct
                )
                
                briefing.append(f"\n{ticker}: {pnl_pct:+.1f}% ({days_held} days)")
                if should_exit:
                    briefing.append(f"   🎯 EXIT SIGNAL")
                else:
                    briefing.append(f"   ✅ HOLD")
                briefing.append(f"   {exit_reasoning[:100]}...")
        
        briefing.append("\n" + "="*70)
        briefing.append("🐺 THE WOLF KNOWS YOU. THE WOLF PROTECTS YOU. AWOOOO.")
        briefing.append("="*70)
        
        return "\n".join(briefing)


def demo():
    """Demo: Show how Wolf Mind filters decisions through YOUR context"""
    
    print("🐺 WOLF MIND DEMO\n")
    
    # Create wolf mind
    wolf = WolfMind()
    
    # Demo opportunity
    print("SCENARIO: BBAI scored 85/100 on technical setup\n")
    
    # First time - clean slate
    should_trade, reasoning, adjusted_score = wolf.analyze_opportunity(
        ticker='BBAI',
        base_score=85,
        setup_type='technical'
    )
    
    print(f"DECISION: {'TRADE' if should_trade else 'PASS'}")
    print(f"ADJUSTED SCORE: {adjusted_score}/100")
    print(f"\nREASONING:\n{reasoning}\n")
    
    # Now simulate you lost on BBAI twice
    print("\n" + "="*70)
    print("SIMULATING: You lost on BBAI twice...")
    print("="*70 + "\n")
    
    wolf.profile.worst_tickers.append('BBAI')
    wolf.profile.loss_streak = 2
    wolf.profile.emotional_state = EmotionalState.TILTED
    
    # Same opportunity, different context
    should_trade, reasoning, adjusted_score = wolf.analyze_opportunity(
        ticker='BBAI',
        base_score=85,
        setup_type='technical'
    )
    
    print(f"DECISION: {'TRADE' if should_trade else 'PASS'}")
    print(f"ADJUSTED SCORE: {adjusted_score}/100")
    print(f"\nREASONING:\n{reasoning}\n")
    
    print("="*70)
    print("👆 SEE THE DIFFERENCE? Same stock, same score.")
    print("But the WOLF KNOWS YOUR HISTORY and PROTECTS YOU.")
    print("="*70)


if __name__ == "__main__":
    demo()
