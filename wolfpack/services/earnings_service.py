#!/usr/bin/env python3
"""
EARNINGS INTELLIGENCE SERVICE
Automated Earnings Calendar + Historical Analysis

Fetches upcoming earnings dates and provides intelligence:
- Historical beat/miss rate
- Estimate revision trends (are analysts getting bullish?)
- Post-earnings behavior (does it fade or follow through?)
- Whisper numbers (when available)

Integrates with Catalyst Service to auto-populate earnings

Data Source: Finnhub API (60 calls/min free tier)
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class EarningsEvent:
    """Upcoming earnings event"""
    ticker: str
    company_name: str
    earnings_date: str  # YYYY-MM-DD
    estimate_eps: Optional[float]  # Analyst consensus
    report_time: str  # "bmo" (before market open) or "amc" (after market close)
    days_until: int


@dataclass
class EarningsHistory:
    """Historical earnings performance"""
    ticker: str
    quarters_analyzed: int
    beat_count: int
    miss_count: int
    meet_count: int
    beat_rate: float  # Percentage
    avg_surprise: float  # Average EPS surprise %
    avg_price_reaction: float  # Average price move on earnings day %


@dataclass
class EarningsSignal:
    """Earnings intelligence signal"""
    ticker: str
    score: int  # 0-100
    event: EarningsEvent
    history: Optional[EarningsHistory]
    estimate_trend: str  # "RISING", "FALLING", "STABLE"
    reasoning: str
    conviction: str  # "HIGH", "MEDIUM", "LOW"


# =============================================================================
# FINNHUB API CLIENT
# =============================================================================

class FinnhubClient:
    """Wrapper for Finnhub API"""
    
    def __init__(self, api_key: str = FINNHUB_API_KEY):
        if not api_key:
            raise ValueError("Finnhub API key required. Set FINNHUB_API_KEY in .env file")
        
        self.api_key = api_key
        self.base_url = FINNHUB_BASE_URL
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request to Finnhub"""
        if params is None:
            params = {}
        
        params['token'] = self.api_key
        
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Finnhub API error ({endpoint}): {e}")
            return None
    
    def get_earnings_calendar(
        self,
        from_date: str,
        to_date: str
    ) -> List[Dict]:
        """
        Fetch earnings calendar for date range
        
        Args:
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
        
        Returns:
            List of earnings events
        """
        data = self._make_request('calendar/earnings', {
            'from': from_date,
            'to': to_date
        })
        
        return data.get('earningsCalendar', []) if data else []
    
    def get_earnings_surprises(self, ticker: str, limit: int = 10) -> List[Dict]:
        """
        Get historical earnings surprises
        
        Args:
            ticker: Stock ticker
            limit: Number of quarters to retrieve
        
        Returns:
            List of earnings surprises
        """
        data = self._make_request('stock/earnings', {
            'symbol': ticker,
            'limit': limit
        })
        
        return data if data and isinstance(data, list) else []
    
    def get_analyst_estimates(self, ticker: str) -> Optional[Dict]:
        """
        Get analyst EPS/revenue estimates
        
        Args:
            ticker: Stock ticker
        
        Returns:
            Dict with estimates or None
        """
        return self._make_request('stock/metric', {
            'symbol': ticker,
            'metric': 'all'
        })


# =============================================================================
# EARNINGS SERVICE
# =============================================================================

class EarningsService:
    """Earnings intelligence and calendar automation"""
    
    def __init__(self, api_key: str = FINNHUB_API_KEY):
        self.client = FinnhubClient(api_key)
    
    def fetch_upcoming_earnings(
        self,
        tickers: List[str] = None,
        days_ahead: int = 60
    ) -> List[EarningsEvent]:
        """
        Fetch upcoming earnings for specific tickers or entire market
        
        Args:
            tickers: List of tickers to check (None = fetch all)
            days_ahead: How many days ahead to look
        
        Returns:
            List of EarningsEvent objects
        """
        today = datetime.now()
        from_date = today.strftime('%Y-%m-%d')
        to_date = (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        calendar = self.client.get_earnings_calendar(from_date, to_date)
        
        events = []
        for item in calendar:
            ticker = item.get('symbol', '').upper()
            
            # Filter by tickers if provided
            if tickers and ticker not in tickers:
                continue
            
            earnings_date_str = item.get('date', '')
            if not earnings_date_str:
                continue
            
            # Calculate days until
            try:
                earnings_date = datetime.strptime(earnings_date_str, '%Y-%m-%d')
                days_until = (earnings_date - today).days
            except:
                days_until = 0
            
            events.append(EarningsEvent(
                ticker=ticker,
                company_name=item.get('companyName', ticker),
                earnings_date=earnings_date_str,
                estimate_eps=item.get('epsEstimate'),
                report_time=item.get('hour', 'unknown'),
                days_until=days_until
            ))
        
        # Sort by date
        events.sort(key=lambda x: x.days_until)
        
        return events
    
    def get_earnings_history(self, ticker: str, quarters: int = 10) -> Optional[EarningsHistory]:
        """
        Analyze historical earnings performance
        
        Args:
            ticker: Stock ticker
            quarters: Number of quarters to analyze
        
        Returns:
            EarningsHistory object or None
        """
        surprises = self.client.get_earnings_surprises(ticker, limit=quarters)
        
        if not surprises:
            return None
        
        beat_count = 0
        miss_count = 0
        meet_count = 0
        total_surprise = 0.0
        
        for surprise in surprises:
            actual = surprise.get('actual')
            estimate = surprise.get('estimate')
            
            if actual is None or estimate is None:
                continue
            
            # Calculate surprise percentage
            if estimate != 0:
                surprise_pct = ((actual - estimate) / abs(estimate)) * 100
            else:
                surprise_pct = 0
            
            total_surprise += surprise_pct
            
            # Categorize
            if actual > estimate * 1.01:  # Beat by > 1%
                beat_count += 1
            elif actual < estimate * 0.99:  # Miss by > 1%
                miss_count += 1
            else:
                meet_count += 1
        
        total_events = beat_count + miss_count + meet_count
        if total_events == 0:
            return None
        
        return EarningsHistory(
            ticker=ticker,
            quarters_analyzed=len(surprises),
            beat_count=beat_count,
            miss_count=miss_count,
            meet_count=meet_count,
            beat_rate=(beat_count / total_events) * 100,
            avg_surprise=total_surprise / total_events,
            avg_price_reaction=0.0  # TODO: Need price data to calculate
        )
    
    def get_earnings_signal_for_convergence(
        self,
        ticker: str,
        days_ahead: int = 60
    ) -> Optional[Dict]:
        """
        Get earnings signal formatted for convergence engine
        
        Combines:
        1. Upcoming earnings proximity (closer = higher urgency)
        2. Historical beat rate (consistent beater = higher confidence)
        3. Estimate trend (upgrades = bullish)
        
        Returns:
            Dict with score, reasoning, and data
        """
        # Find upcoming earnings
        events = self.fetch_upcoming_earnings([ticker], days_ahead)
        
        if not events:
            return None
        
        event = events[0]  # Next earnings
        
        # Get historical performance
        history = self.get_earnings_history(ticker)
        
        # Calculate score (0-100)
        score = 50  # Base score
        
        # 1. Proximity bonus (closer = higher urgency)
        if event.days_until <= 7:
            proximity_bonus = 40
        elif event.days_until <= 14:
            proximity_bonus = 30
        elif event.days_until <= 30:
            proximity_bonus = 20
        else:
            proximity_bonus = 10
        
        score += proximity_bonus
        
        # 2. Historical beat rate bonus
        if history:
            if history.beat_rate >= 80:
                beat_bonus = 10
            elif history.beat_rate >= 70:
                beat_bonus = 5
            elif history.beat_rate >= 60:
                beat_bonus = 0
            else:
                beat_bonus = -10  # Consistent misser = penalty
            
            score += beat_bonus
        
        # 3. Clamp to 0-100
        score = max(0, min(100, score))
        
        # Determine conviction
        if score >= 85:
            conviction = "HIGH"
        elif score >= 70:
            conviction = "MEDIUM"
        else:
            conviction = "LOW"
        
        # Build reasoning
        reasoning = f"{ticker} earnings in {event.days_until}d"
        if history:
            reasoning += f", {history.beat_rate:.0f}% beat rate ({history.beat_count}W-{history.miss_count}L)"
        
        # Estimate trend (simplified - would need time series data)
        estimate_trend = "STABLE"  # TODO: Track estimate revisions over time
        
        return {
            'score': score,
            'reasoning': reasoning,
            'data': {
                'earnings_date': event.earnings_date,
                'days_until': event.days_until,
                'estimate_eps': event.estimate_eps,
                'report_time': event.report_time,
                'history': {
                    'beat_rate': history.beat_rate if history else None,
                    'quarters_analyzed': history.quarters_analyzed if history else 0,
                    'beat_count': history.beat_count if history else 0,
                    'miss_count': history.miss_count if history else 0,
                } if history else None,
                'conviction': conviction,
                'estimate_trend': estimate_trend
            }
        }


# =============================================================================
# FORMATTING
# =============================================================================

def format_earnings_report(signal: Optional[Dict], ticker: str) -> str:
    """Format earnings signal for terminal display"""
    if not signal:
        return f"📊 {ticker}: No upcoming earnings in next 60 days"
    
    data = signal['data']
    score = signal['score']
    
    # Emoji based on score
    if score >= 85:
        emoji = "🔴"  # IMMINENT
    elif score >= 70:
        emoji = "🟡"  # UPCOMING
    else:
        emoji = "⚪"  # DISTANT
    
    report = f"""
{emoji} {ticker} EARNINGS ({score}/100)
Date: {data['earnings_date']} ({data['days_until']} days)
Time: {data['report_time'].upper()}
Conviction: {data['conviction']}
"""
    
    if data.get('estimate_eps'):
        report += f"Est EPS: ${data['estimate_eps']:.2f}\n"
    
    if data.get('history'):
        hist = data['history']
        if hist['beat_rate'] is not None:
            report += f"Historical: {hist['beat_rate']:.0f}% beat rate ({hist['beat_count']}W-{hist['miss_count']}L in {hist['quarters_analyzed']}Q)\n"
    
    return report


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("📊 EARNINGS SERVICE TEST\n")
    
    earnings_service = EarningsService()
    
    # Test 1: Fetch upcoming earnings for specific tickers
    print("=" * 60)
    print("TEST 1: Upcoming Earnings Calendar")
    print("=" * 60)
    
    test_tickers = ['MU', 'NVDA', 'AMD', 'TSLA', 'AAPL']
    
    events = earnings_service.fetch_upcoming_earnings(test_tickers, days_ahead=90)
    
    print(f"\nFound {len(events)} upcoming earnings:\n")
    for event in events[:5]:  # Show first 5
        print(f"{event.ticker:6} {event.earnings_date}  ({event.days_until:2}d)  {event.report_time}")
    
    # Test 2: Get historical performance
    print("\n" + "=" * 60)
    print("TEST 2: Historical Earnings Performance")
    print("=" * 60)
    
    for ticker in ['MU', 'NVDA']:
        print(f"\n{ticker}:")
        history = earnings_service.get_earnings_history(ticker)
        
        if history:
            print(f"  Quarters analyzed: {history.quarters_analyzed}")
            print(f"  Beat rate: {history.beat_rate:.1f}% ({history.beat_count}W-{history.miss_count}L-{history.meet_count}M)")
            print(f"  Avg surprise: {history.avg_surprise:+.1f}%")
        else:
            print("  No historical data available")
    
    # Test 3: Get convergence signals
    print("\n" + "=" * 60)
    print("TEST 3: Earnings Signals for Convergence")
    print("=" * 60)
    
    for ticker in ['MU', 'NVDA', 'AMD']:
        signal = earnings_service.get_earnings_signal_for_convergence(ticker)
        print(format_earnings_report(signal, ticker))
    
    print("\n✅ EARNINGS SERVICE TEST COMPLETE")
