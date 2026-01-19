#!/usr/bin/env python3
"""
RISK MANAGEMENT MODULE
The Safety Layer - Position sizing, portfolio heat, correlation analysis

This module ensures we don't blow up the account.
Calculates proper position sizes based on:
- Kelly Criterion (optimal bet size given win rate and payoff)
- Portfolio heat (total risk across all positions)
- Correlation (don't have 5 uranium stocks = 500% exposure)
- Max position limits (no YOLO trades)
"""

import sqlite3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math


# =============================================================================
# CONFIGURATION
# =============================================================================

# Risk parameters (conservative default values)
MAX_POSITION_SIZE = 0.20  # 20% max per position
MAX_PORTFOLIO_HEAT = 0.50  # 50% total portfolio risk max
MIN_POSITION_SIZE = 0.02   # 2% minimum (below this = not worth it)
KELLY_FRACTION = 0.50      # Use 50% of Kelly (full Kelly is too aggressive)


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class PositionSizeCalculation:
    """Result of position sizing calculation"""
    ticker: str
    recommended_size: float  # Percentage of portfolio (0.0 - 1.0)
    max_shares: int
    risk_per_share: float
    entry_price: float
    stop_price: float
    target_price: float
    convergence_score: int
    reasoning: str
    warnings: List[str]


@dataclass
class PortfolioRisk:
    """Current portfolio risk metrics"""
    total_heat: float  # Sum of all position risks
    open_positions: int
    capital_deployed: float  # Percentage of portfolio in positions
    available_capital: float  # Percentage available for new positions
    correlation_risk: float  # Risk from correlated positions
    warnings: List[str]


@dataclass
class CorrelationGroup:
    """Group of correlated positions"""
    group_name: str
    tickers: List[str]
    total_exposure: float  # Combined percentage
    risk_multiplier: float  # How correlated (1.0 = independent, 3.0 = moving together)


# =============================================================================
# KELLY CRITERION CALCULATOR
# =============================================================================

def calculate_kelly_criterion(
    win_rate: float,
    avg_winner: float,
    avg_loser: float,
    fraction: float = KELLY_FRACTION
) -> float:
    """
    Calculate optimal position size using Kelly Criterion
    
    Kelly Formula: f = (p * b - q) / b
    Where:
    - f = fraction of bankroll to bet
    - p = probability of winning (win_rate)
    - q = probability of losing (1 - win_rate)
    - b = ratio of win to loss (avg_winner / avg_loser)
    
    Args:
        win_rate: Historical win rate (0.0 - 1.0)
        avg_winner: Average winning trade return (as decimal, e.g., 0.15 for 15%)
        avg_loser: Average losing trade return (as decimal, e.g., 0.10 for 10%)
        fraction: Kelly fraction to use (0.5 = half Kelly, safer)
    
    Returns:
        Recommended position size as decimal (0.0 - 1.0)
    """
    if win_rate <= 0 or win_rate >= 1:
        return 0.0
    
    if avg_winner <= 0 or avg_loser <= 0:
        return 0.0
    
    p = win_rate
    q = 1 - win_rate
    b = avg_winner / avg_loser
    
    # Kelly formula
    kelly = (p * b - q) / b
    
    # Apply fraction (half Kelly is more conservative)
    kelly_fractional = kelly * fraction
    
    # Never bet more than MAX_POSITION_SIZE
    return max(0.0, min(kelly_fractional, MAX_POSITION_SIZE))


def calculate_position_size_from_risk(
    account_value: float,
    entry_price: float,
    stop_price: float,
    risk_per_trade: float = 0.02  # 2% risk per trade
) -> Tuple[float, int]:
    """
    Calculate position size based on risk per trade
    
    Formula: Position Size = (Account Value * Risk%) / (Entry - Stop)
    
    Args:
        account_value: Total account value in dollars
        entry_price: Entry price per share
        stop_price: Stop loss price per share
        risk_per_trade: Percentage of account to risk (0.02 = 2%)
    
    Returns:
        (position_value, shares)
    """
    if entry_price <= stop_price:
        return (0.0, 0)
    
    risk_per_share = entry_price - stop_price
    risk_dollars = account_value * risk_per_trade
    
    shares = int(risk_dollars / risk_per_share)
    position_value = shares * entry_price
    
    return (position_value, shares)


# =============================================================================
# RISK MANAGER
# =============================================================================

class RiskManager:
    """
    Manages position sizing and portfolio risk
    """
    
    def __init__(
        self,
        account_value: float,
        max_position_size: float = MAX_POSITION_SIZE,
        max_portfolio_heat: float = MAX_PORTFOLIO_HEAT,
        min_position_size: float = MIN_POSITION_SIZE
    ):
        self.account_value = account_value
        self.max_position_size = max_position_size
        self.max_portfolio_heat = max_portfolio_heat
        self.min_position_size = min_position_size
        
        # Track open positions
        self.open_positions: List[Dict] = []
    
    def calculate_position_size(
        self,
        ticker: str,
        entry_price: float,
        stop_price: float,
        target_price: float,
        convergence_score: int,
        pattern_stats: Optional[Dict] = None
    ) -> PositionSizeCalculation:
        """
        Calculate recommended position size for a new trade
        
        Combines:
        1. Kelly Criterion (based on historical pattern stats)
        2. Fixed risk per trade (2-3% risk)
        3. Convergence score adjustment (higher score = higher conviction)
        4. Portfolio heat check (can we add more risk?)
        
        Args:
            ticker: Stock ticker
            entry_price: Planned entry price
            stop_price: Stop loss price
            target_price: Target price
            convergence_score: Score from convergence engine (0-100)
            pattern_stats: Historical win rate / avg winner / avg loser
        
        Returns:
            PositionSizeCalculation with recommended size and reasoning
        """
        warnings = []
        
        # 1. Calculate Kelly size (if we have historical stats)
        kelly_size = 0.0
        if pattern_stats:
            win_rate = pattern_stats.get('win_rate', 0.50)
            avg_winner = pattern_stats.get('avg_winner', 0.15)
            avg_loser = pattern_stats.get('avg_loser', 0.10)
            
            kelly_size = calculate_kelly_criterion(win_rate, avg_winner, avg_loser)
            
            if kelly_size == 0:
                warnings.append("Kelly calculation suggests SKIP (negative expectancy)")
        
        # 2. Calculate fixed risk size (2-3% risk per trade)
        # Higher convergence score = willing to risk more
        if convergence_score >= 85:
            risk_per_trade = 0.03  # 3% risk (high conviction)
        elif convergence_score >= 70:
            risk_per_trade = 0.025  # 2.5% risk (medium-high)
        elif convergence_score >= 50:
            risk_per_trade = 0.02  # 2% risk (medium)
        else:
            risk_per_trade = 0.015  # 1.5% risk (low conviction)
        
        position_value, shares = calculate_position_size_from_risk(
            self.account_value,
            entry_price,
            stop_price,
            risk_per_trade
        )
        
        risk_size = position_value / self.account_value
        
        # 3. Take the SMALLER of Kelly and risk size (conservative)
        if kelly_size > 0:
            recommended_size = min(kelly_size, risk_size)
            reasoning = f"Kelly: {kelly_size:.1%}, Risk-based: {risk_size:.1%} → Using {recommended_size:.1%}"
        else:
            recommended_size = risk_size
            reasoning = f"Risk-based sizing: {risk_size:.1%} (no Kelly data)"
        
        # 4. Apply convergence score multiplier
        # High conviction (85+) = allow up to 1.5x size
        # Low conviction (50-69) = reduce to 0.75x size
        if convergence_score >= 85:
            multiplier = 1.5
            reasoning += f" × 1.5 (high conviction {convergence_score}/100)"
        elif convergence_score >= 70:
            multiplier = 1.2
            reasoning += f" × 1.2 (good conviction {convergence_score}/100)"
        elif convergence_score >= 50:
            multiplier = 1.0
        else:
            multiplier = 0.75
            reasoning += f" × 0.75 (lower conviction {convergence_score}/100)"
        
        recommended_size *= multiplier
        
        # 5. Check portfolio heat (can we add more risk?)
        current_heat = self._calculate_current_heat()
        risk_per_share = entry_price - stop_price
        new_position_heat = (recommended_size * self.account_value * risk_per_share) / (entry_price * self.account_value)
        total_heat_after = current_heat + new_position_heat
        
        if total_heat_after > self.max_portfolio_heat:
            # Reduce size to fit under heat limit
            available_heat = self.max_portfolio_heat - current_heat
            if available_heat <= 0:
                warnings.append(f"Portfolio heat at {current_heat:.1%} (max {self.max_portfolio_heat:.1%}) - SKIP")
                recommended_size = 0.0
            else:
                # Scale down to fit
                scale = available_heat / new_position_heat
                recommended_size *= scale
                warnings.append(f"Position reduced to fit portfolio heat limit (was {recommended_size/scale:.1%}, now {recommended_size:.1%})")
        
        # 6. Apply hard limits
        if recommended_size > self.max_position_size:
            warnings.append(f"Position capped at {self.max_position_size:.1%} (max position size)")
            recommended_size = self.max_position_size
        
        if recommended_size < self.min_position_size:
            warnings.append(f"Position too small ({recommended_size:.1%} < {self.min_position_size:.1%} min) - SKIP")
            recommended_size = 0.0
        
        # 7. Calculate final shares
        position_value = recommended_size * self.account_value
        max_shares = int(position_value / entry_price)
        
        return PositionSizeCalculation(
            ticker=ticker,
            recommended_size=recommended_size,
            max_shares=max_shares,
            risk_per_share=entry_price - stop_price,
            entry_price=entry_price,
            stop_price=stop_price,
            target_price=target_price,
            convergence_score=convergence_score,
            reasoning=reasoning,
            warnings=warnings
        )
    
    def _calculate_current_heat(self) -> float:
        """Calculate current portfolio heat (total risk from open positions)"""
        total_heat = 0.0
        
        for pos in self.open_positions:
            # Heat = (shares * risk_per_share) / account_value
            risk_dollars = pos['shares'] * (pos['entry_price'] - pos['stop_price'])
            heat = risk_dollars / self.account_value
            total_heat += heat
        
        return total_heat
    
    def get_portfolio_risk(self) -> PortfolioRisk:
        """Get current portfolio risk metrics"""
        total_heat = self._calculate_current_heat()
        
        # Calculate capital deployed
        capital_deployed = sum(
            pos['shares'] * pos['current_price'] 
            for pos in self.open_positions
        ) / self.account_value
        
        # Calculate correlation risk
        correlation_groups = self._detect_correlation_groups()
        correlation_risk = sum(
            group.total_exposure * (group.risk_multiplier - 1.0)
            for group in correlation_groups
        )
        
        warnings = []
        if total_heat > self.max_portfolio_heat * 0.8:
            warnings.append(f"⚠️  Portfolio heat at {total_heat:.1%} (near max {self.max_portfolio_heat:.1%})")
        
        if capital_deployed > 0.80:
            warnings.append(f"⚠️  Capital deployed: {capital_deployed:.1%} (low cash reserve)")
        
        if correlation_risk > 0.20:
            warnings.append(f"⚠️  High correlation risk: {correlation_risk:.1%} (positions moving together)")
        
        return PortfolioRisk(
            total_heat=total_heat,
            open_positions=len(self.open_positions),
            capital_deployed=capital_deployed,
            available_capital=1.0 - capital_deployed,
            correlation_risk=correlation_risk,
            warnings=warnings
        )
    
    def _detect_correlation_groups(self) -> List[CorrelationGroup]:
        """Detect correlated positions (same sector, same basket)"""
        # Simple heuristic: group by sector keywords
        groups = []
        
        sector_keywords = {
            'uranium': ['URA', 'UEC', 'UUUU', 'CCJ', 'DNN'],
            'quantum': ['IONQ', 'RGTI', 'QTUM', 'ARQQ'],
            'defense': ['KTOS', 'ITA', 'LMT', 'RTX', 'NOC'],
            'semis': ['SMCI', 'NVDA', 'AMD', 'AVGO', 'TSM', 'MU', 'SOXX'],
            'biotech': ['IBRX', 'XBI', 'MRNA', 'CRSP'],
        }
        
        tickers = [pos['ticker'] for pos in self.open_positions]
        
        for sector, sector_tickers in sector_keywords.items():
            matching = [t for t in tickers if t in sector_tickers]
            if len(matching) >= 2:
                # Multiple positions in same sector
                total_exposure = sum(
                    pos['shares'] * pos['current_price'] / self.account_value
                    for pos in self.open_positions
                    if pos['ticker'] in matching
                )
                
                # Risk multiplier: 2 positions = 1.5x, 3+ = 2.0x
                risk_multiplier = 1.0 + (0.5 * len(matching))
                
                groups.append(CorrelationGroup(
                    group_name=sector.title(),
                    tickers=matching,
                    total_exposure=total_exposure,
                    risk_multiplier=risk_multiplier
                ))
        
        return groups
    
    def add_position(
        self,
        ticker: str,
        shares: int,
        entry_price: float,
        stop_price: float,
        target_price: float,
        current_price: float = None
    ):
        """Add a position to tracking"""
        if current_price is None:
            current_price = entry_price
        
        self.open_positions.append({
            'ticker': ticker,
            'shares': shares,
            'entry_price': entry_price,
            'stop_price': stop_price,
            'target_price': target_price,
            'current_price': current_price,
            'entry_date': datetime.now().isoformat()
        })
    
    def remove_position(self, ticker: str):
        """Remove a position from tracking"""
        self.open_positions = [
            pos for pos in self.open_positions 
            if pos['ticker'] != ticker
        ]
    
    def update_position_price(self, ticker: str, current_price: float):
        """Update current price for a position"""
        for pos in self.open_positions:
            if pos['ticker'] == ticker:
                pos['current_price'] = current_price


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_position_size_report(calc: PositionSizeCalculation) -> str:
    """Format position size calculation for display"""
    if calc.recommended_size == 0:
        return f"""
🚫 SKIP {calc.ticker}
{calc.reasoning}
Warnings: {', '.join(calc.warnings) if calc.warnings else 'None'}
"""
    
    position_value = calc.recommended_size * 100000  # Assuming $100k account for display
    r_multiple = (calc.target_price - calc.entry_price) / (calc.entry_price - calc.stop_price)
    
    return f"""
💰 {calc.ticker} POSITION SIZE
Size: {calc.recommended_size:.1%} of portfolio (${position_value:,.0f} on $100k account)
Shares: {calc.max_shares}
Entry: ${calc.entry_price:.2f} | Stop: ${calc.stop_price:.2f} | Target: ${calc.target_price:.2f}
Risk: ${calc.risk_per_share:.2f}/share | R-multiple: {r_multiple:.1f}R
Conviction: {calc.convergence_score}/100

{calc.reasoning}
{'Warnings: ' + ', '.join(calc.warnings) if calc.warnings else '✅ No warnings'}
"""


def format_portfolio_risk_report(risk: PortfolioRisk) -> str:
    """Format portfolio risk metrics for display"""
    status_emoji = "🟢" if risk.total_heat < 0.30 else "🟡" if risk.total_heat < 0.45 else "🔴"
    
    report = f"""
{status_emoji} PORTFOLIO RISK STATUS
Total Heat: {risk.total_heat:.1%} (max {MAX_PORTFOLIO_HEAT:.1%})
Open Positions: {risk.open_positions}
Capital Deployed: {risk.capital_deployed:.1%}
Available Capital: {risk.available_capital:.1%}
Correlation Risk: {risk.correlation_risk:.1%}
"""
    
    if risk.warnings:
        report += "\n⚠️  WARNINGS:\n"
        for warning in risk.warnings:
            report += f"  {warning}\n"
    else:
        report += "\n✅ Portfolio risk is healthy\n"
    
    return report


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("🎯 RISK MANAGER TEST\n")
    
    # Initialize risk manager with $100k account
    rm = RiskManager(account_value=100000)
    
    # Test 1: Calculate position size for high conviction signal
    print("=" * 60)
    print("TEST 1: High Conviction Signal (85/100)")
    print("=" * 60)
    
    calc = rm.calculate_position_size(
        ticker="MU",
        entry_price=125.00,
        stop_price=118.00,
        target_price=145.00,
        convergence_score=85,
        pattern_stats={
            'win_rate': 0.70,
            'avg_winner': 0.15,
            'avg_loser': 0.10
        }
    )
    
    print(format_position_size_report(calc))
    
    # Add position
    if calc.recommended_size > 0:
        rm.add_position("MU", calc.max_shares, calc.entry_price, calc.stop_price, calc.target_price)
    
    # Test 2: Calculate position size for medium conviction
    print("=" * 60)
    print("TEST 2: Medium Conviction Signal (65/100)")
    print("=" * 60)
    
    calc2 = rm.calculate_position_size(
        ticker="SMCI",
        entry_price=32.64,
        stop_price=29.14,
        target_price=42.00,
        convergence_score=65,
        pattern_stats={
            'win_rate': 0.68,
            'avg_winner': 0.12,
            'avg_loser': 0.08
        }
    )
    
    print(format_position_size_report(calc2))
    
    if calc2.recommended_size > 0:
        rm.add_position("SMCI", calc2.max_shares, calc2.entry_price, calc2.stop_price, calc2.target_price)
    
    # Test 3: Check portfolio risk
    print("=" * 60)
    print("TEST 3: Portfolio Risk Status")
    print("=" * 60)
    
    portfolio_risk = rm.get_portfolio_risk()
    print(format_portfolio_risk_report(portfolio_risk))
    
    # Test 4: Try adding too many positions (test heat limit)
    print("=" * 60)
    print("TEST 4: Adding Multiple Positions (Test Heat Limit)")
    print("=" * 60)
    
    for i, ticker in enumerate(['IONQ', 'RGTI', 'KTOS', 'UEC'], start=3):
        calc = rm.calculate_position_size(
            ticker=ticker,
            entry_price=50.00,
            stop_price=45.00,
            target_price=65.00,
            convergence_score=70,
            pattern_stats={'win_rate': 0.65, 'avg_winner': 0.12, 'avg_loser': 0.09}
        )
        
        print(f"\nPosition {i}: {ticker}")
        print(f"  Recommended: {calc.recommended_size:.1%}")
        if calc.warnings:
            print(f"  Warnings: {', '.join(calc.warnings)}")
        
        if calc.recommended_size > 0:
            rm.add_position(ticker, calc.max_shares, calc.entry_price, calc.stop_price, calc.target_price)
    
    # Final portfolio status
    print("\n" + "=" * 60)
    print("FINAL PORTFOLIO STATUS")
    print("=" * 60)
    portfolio_risk = rm.get_portfolio_risk()
    print(format_portfolio_risk_report(portfolio_risk))
    
    print("\n✅ RISK MANAGER TEST COMPLETE")
