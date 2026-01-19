#!/usr/bin/env python3
"""
CATALYST SERVICE - The Timing Layer
Tracks upcoming binary events: PDUFA dates, earnings, policy events
The "Catalyst Ahead" validation system
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import json
import os


# =============================================================================
# DATA MODELS
# =============================================================================

class CatalystType(Enum):
    """Types of catalyst events"""
    PDUFA = "PDUFA"  # FDA decision date
    EARNINGS = "Earnings"
    CLINICAL_TRIAL = "Clinical Trial"
    CONTRACT_AWARD = "Contract Award"
    POLICY_EVENT = "Policy Event"
    PRODUCT_LAUNCH = "Product Launch"
    MERGER = "Merger/Acquisition"
    MANUAL = "Manual Entry"


class CatalystImpact(Enum):
    """Expected impact level"""
    BINARY = "BINARY"  # Win or lose everything (PDUFA, trial results)
    HIGH = "HIGH"  # Major catalyst
    MEDIUM = "MEDIUM"  # Notable event
    LOW = "LOW"  # Minor event


@dataclass
class Catalyst:
    """Individual catalyst event"""
    ticker: str
    company_name: str
    catalyst_type: CatalystType
    event_date: str  # YYYY-MM-DD
    description: str
    impact_level: CatalystImpact
    days_until: int
    source: str  # Where we got this data
    
    def get_urgency_score(self) -> int:
        """
        Calculate urgency score based on days until event
        
        Philosophy:
        - 0-3 days: IMMINENT (90-100 points)
        - 4-7 days: NEAR (80-89 points)
        - 8-14 days: APPROACHING (70-79 points)
        - 15-30 days: UPCOMING (60-69 points)
        - 31-60 days: DISTANT (50-59 points)
        - 61+ days: FAR (0-49 points)
        """
        if self.days_until <= 0:
            return 100  # Today or past
        elif self.days_until <= 3:
            return 95  # Imminent
        elif self.days_until <= 7:
            return 85  # This week
        elif self.days_until <= 14:
            return 75  # Next 2 weeks
        elif self.days_until <= 30:
            return 65  # This month
        elif self.days_until <= 60:
            return 55  # Next 2 months
        else:
            return max(50 - (self.days_until - 60) // 10, 20)  # Decay over time
    
    def get_signal_score(self) -> int:
        """
        Calculate catalyst signal score for convergence engine
        Combines urgency + impact level
        """
        urgency = self.get_urgency_score()
        
        # Impact multipliers
        impact_bonus = {
            CatalystImpact.BINARY: 30,
            CatalystImpact.HIGH: 20,
            CatalystImpact.MEDIUM: 10,
            CatalystImpact.LOW: 5,
        }
        
        bonus = impact_bonus.get(self.impact_level, 0)
        return min(urgency + bonus, 100)


# =============================================================================
# CATALYST DATABASE (Manual Entries)
# =============================================================================

class CatalystDatabase:
    """
    Manual catalyst tracking database
    Stores user-added catalysts in JSON file
    """
    
    def __init__(self, db_path: str = "data/catalysts.json"):
        self.db_path = db_path
        self.catalysts = []
        self._load()
    
    def _load(self):
        """Load catalysts from JSON file"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    # Convert to Catalyst objects
                    self.catalysts = []
                    for item in data:
                        catalyst = Catalyst(
                            ticker=item['ticker'],
                            company_name=item.get('company_name', ''),
                            catalyst_type=CatalystType(item['catalyst_type']),
                            event_date=item['event_date'],
                            description=item['description'],
                            impact_level=CatalystImpact(item['impact_level']),
                            days_until=self._calculate_days_until(item['event_date']),
                            source=item.get('source', 'manual'),
                        )
                        self.catalysts.append(catalyst)
            except Exception as e:
                print(f"Error loading catalyst database: {e}")
                self.catalysts = []
    
    def _save(self):
        """Save catalysts to JSON file"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        data = []
        for catalyst in self.catalysts:
            data.append({
                'ticker': catalyst.ticker,
                'company_name': catalyst.company_name,
                'catalyst_type': catalyst.catalyst_type.value,
                'event_date': catalyst.event_date if isinstance(catalyst.event_date, str) else catalyst.event_date.isoformat(),
                'description': catalyst.description,
                'impact_level': catalyst.impact_level.value,
                'source': catalyst.source,
            })
        
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _calculate_days_until(self, event_date: str) -> int:
        """Calculate days until event"""
        try:
            event = datetime.strptime(event_date, '%Y-%m-%d')
            today = datetime.now()
            return (event - today).days
        except:
            return 999
    
    def add_catalyst(
        self,
        ticker: str,
        catalyst_type: CatalystType,
        event_date: str,
        description: str,
        impact_level: CatalystImpact,
        company_name: str = "",
    ):
        """Add new catalyst to database"""
        days_until = self._calculate_days_until(event_date)
        
        catalyst = Catalyst(
            ticker=ticker,
            company_name=company_name,
            catalyst_type=catalyst_type,
            event_date=event_date,
            description=description,
            impact_level=impact_level,
            days_until=days_until,
            source='manual',
        )
        
        self.catalysts.append(catalyst)
        self._save()
        
        return catalyst
    
    def get_catalysts_for_ticker(self, ticker: str) -> List[Catalyst]:
        """Get all catalysts for a specific ticker"""
        return [c for c in self.catalysts if c.ticker == ticker]
    
    def get_upcoming_catalysts(self, days_ahead: int = 30) -> List[Catalyst]:
        """Get all catalysts in next N days"""
        return [c for c in self.catalysts if 0 <= c.days_until <= days_ahead]
    
    def get_all_catalysts(self) -> List[Catalyst]:
        """Get all catalysts"""
        # Refresh days_until
        for catalyst in self.catalysts:
            catalyst.days_until = self._calculate_days_until(catalyst.event_date)
        return sorted(self.catalysts, key=lambda c: c.days_until)


# =============================================================================
# EARNINGS CALENDAR (API)
# =============================================================================

def fetch_earnings_calendar(tickers: List[str]) -> List[Catalyst]:
    """
    Fetch earnings dates for tickers
    Note: Free APIs are limited. This is a placeholder for future enhancement.
    
    Options:
    1. Yahoo Finance (free, but needs scraping)
    2. Alpha Vantage (free tier limited)
    3. Finnhub (free tier limited)
    4. Manual entry
    
    For now, returns empty list. Use manual entry.
    """
    catalysts = []
    
    # TODO: Implement API integration
    # For now, return empty - users add manually
    
    return catalysts


# =============================================================================
# PDUFA CALENDAR (Scraper - Future Enhancement)
# =============================================================================

def fetch_pdufa_dates() -> List[Catalyst]:
    """
    Fetch PDUFA dates from FDA calendar
    
    Sources:
    1. FDA website (https://www.fda.gov/patients/drug-development-process/drug-approvals-and-databases)
    2. BioPharma Dive PDUFA calendar
    3. Biotech analyst websites
    
    Note: This requires web scraping. For now, returns empty list.
    Use manual entry for PDUFA dates.
    """
    catalysts = []
    
    # TODO: Implement PDUFA scraper
    # For now, return empty - users add manually
    
    return catalysts


# =============================================================================
# CATALYST SERVICE (Main API)
# =============================================================================

class CatalystService:
    """
    Main catalyst tracking service
    Combines manual entries + API data
    """
    
    def __init__(self, db_path: str = "data/catalysts.json"):
        self.db = CatalystDatabase(db_path)
    
    def add_catalyst(
        self,
        ticker: str,
        catalyst_type: CatalystType,
        event_date: str,
        description: str,
        impact_level: CatalystImpact,
        company_name: str = "",
    ) -> Catalyst:
        """Add new catalyst"""
        return self.db.add_catalyst(
            ticker=ticker,
            catalyst_type=catalyst_type,
            event_date=event_date,
            description=description,
            impact_level=impact_level,
            company_name=company_name,
        )
    
    def get_catalysts_for_tickers(self, tickers: List[str]) -> Dict[str, List[Catalyst]]:
        """Get catalysts organized by ticker"""
        result = {}
        
        for ticker in tickers:
            catalysts = self.db.get_catalysts_for_ticker(ticker)
            if catalysts:
                result[ticker] = catalysts
        
        return result
    
    def get_upcoming_catalysts(self, days_ahead: int = 30) -> List[Catalyst]:
        """Get all upcoming catalysts"""
        return self.db.get_upcoming_catalysts(days_ahead)
    
    def get_catalyst_alerts(self, days_threshold: int = 7) -> List[Dict]:
        """
        Generate alerts for imminent catalysts
        
        Returns alerts for events within threshold days
        """
        upcoming = self.get_upcoming_catalysts(days_ahead=days_threshold)
        
        alerts = []
        for catalyst in upcoming:
            if catalyst.days_until <= 3:
                priority = "🔴 IMMINENT"
            elif catalyst.days_until <= 7:
                priority = "🟠 THIS WEEK"
            else:
                priority = "🟡 UPCOMING"
            
            alert = {
                'priority': priority,
                'ticker': catalyst.ticker,
                'event': catalyst.description,
                'days_until': catalyst.days_until,
                'date': catalyst.event_date,
                'impact': catalyst.impact_level.value,
                'score': catalyst.get_signal_score(),
            }
            alerts.append(alert)
        
        # Sort by urgency (days until)
        alerts.sort(key=lambda a: a['days_until'])
        
        return alerts
    
    def get_catalyst_for_convergence(self, ticker: str) -> Optional[Dict]:
        """
        Get best catalyst signal for convergence engine
        Returns highest-scoring catalyst for ticker
        """
        catalysts = self.db.get_catalysts_for_ticker(ticker)
        
        if not catalysts:
            return None
        
        # Get highest scoring catalyst
        best = max(catalysts, key=lambda c: c.get_signal_score())
        
        # Only return if score is meaningful (50+)
        if best.get_signal_score() < 50:
            return None
        
        return {
            'score': best.get_signal_score(),
            'reasoning': f"{best.catalyst_type.value} in {best.days_until} days",
            'data': {
                'catalyst': best,
                'description': best.description,
                'date': best.event_date,
                'days_until': best.days_until,
                'impact': best.impact_level.value,
            }
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_catalyst_calendar(catalysts: List[Catalyst], days_ahead: int = 30) -> str:
    """Format catalyst calendar for display"""
    upcoming = [c for c in catalysts if 0 <= c.days_until <= days_ahead]
    
    if not upcoming:
        return f"No catalysts scheduled in next {days_ahead} days"
    
    lines = []
    lines.append(f"📅 CATALYST CALENDAR (Next {days_ahead} days):")
    lines.append("=" * 60)
    
    # Group by urgency
    imminent = [c for c in upcoming if c.days_until <= 3]
    this_week = [c for c in upcoming if 4 <= c.days_until <= 7]
    next_two_weeks = [c for c in upcoming if 8 <= c.days_until <= 14]
    rest = [c for c in upcoming if c.days_until > 14]
    
    if imminent:
        lines.append("\n🔴 IMMINENT (0-3 days):")
        for c in sorted(imminent, key=lambda x: x.days_until):
            lines.append(f"  {c.ticker}: {c.description}")
            lines.append(f"    → {c.event_date} ({c.days_until} days) - {c.impact_level.value}")
    
    if this_week:
        lines.append("\n🟠 THIS WEEK (4-7 days):")
        for c in sorted(this_week, key=lambda x: x.days_until):
            lines.append(f"  {c.ticker}: {c.description}")
            lines.append(f"    → {c.event_date} ({c.days_until} days) - {c.impact_level.value}")
    
    if next_two_weeks:
        lines.append("\n🟡 NEXT 2 WEEKS (8-14 days):")
        for c in sorted(next_two_weeks, key=lambda x: x.days_until):
            lines.append(f"  {c.ticker}: {c.description}")
            lines.append(f"    → {c.event_date} ({c.days_until} days) - {c.impact_level.value}")
    
    if rest:
        lines.append(f"\n🟢 UPCOMING (15-{days_ahead} days):")
        for c in sorted(rest, key=lambda x: x.days_until):
            lines.append(f"  {c.ticker}: {c.description} - {c.event_date} ({c.days_until} days)")
    
    return "\n".join(lines)


# =============================================================================
# CLI for Manual Entry
# =============================================================================

def add_catalyst_cli():
    """Command-line interface for adding catalysts"""
    print("📅 ADD CATALYST")
    print("=" * 60)
    
    ticker = input("Ticker: ").upper()
    company_name = input("Company Name (optional): ")
    
    print("\nCatalyst Type:")
    for i, ct in enumerate(CatalystType, 1):
        print(f"  {i}. {ct.value}")
    type_idx = int(input("Choose (1-8): ")) - 1
    catalyst_type = list(CatalystType)[type_idx]
    
    event_date = input("Event Date (YYYY-MM-DD): ")
    description = input("Description: ")
    
    print("\nImpact Level:")
    for i, il in enumerate(CatalystImpact, 1):
        print(f"  {i}. {il.value}")
    impact_idx = int(input("Choose (1-4): ")) - 1
    impact_level = list(CatalystImpact)[impact_idx]
    
    service = CatalystService()
    catalyst = service.add_catalyst(
        ticker=ticker,
        catalyst_type=catalyst_type,
        event_date=event_date,
        description=description,
        impact_level=impact_level,
        company_name=company_name,
    )
    
    print(f"\n✅ Added: {ticker} - {description}")
    print(f"   Date: {event_date} ({catalyst.days_until} days away)")
    print(f"   Signal Score: {catalyst.get_signal_score()}/100")


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("📅 CATALYST SERVICE TEST\n")
    
    # Initialize service
    service = CatalystService(db_path="data/catalysts_test.json")
    
    # Add test catalysts
    print("Adding test catalysts...")
    
    service.add_catalyst(
        ticker="IBRX",
        catalyst_type=CatalystType.PDUFA,
        event_date="2026-12-31",
        description="BLA filing expected",
        impact_level=CatalystImpact.BINARY,
        company_name="Immuneering",
    )
    
    service.add_catalyst(
        ticker="KTOS",
        catalyst_type=CatalystType.EARNINGS,
        event_date="2026-02-01",
        description="Q4 2025 Earnings",
        impact_level=CatalystImpact.HIGH,
        company_name="Kratos Defense",
    )
    
    service.add_catalyst(
        ticker="MU",
        catalyst_type=CatalystType.EARNINGS,
        event_date="2026-01-25",
        description="Q1 2026 Earnings",
        impact_level=CatalystImpact.HIGH,
        company_name="Micron",
    )
    
    print("✅ Added 3 test catalysts\n")
    
    # Get upcoming catalysts
    upcoming = service.get_upcoming_catalysts(days_ahead=365)
    print(f"📊 {len(upcoming)} upcoming catalysts:\n")
    
    for c in upcoming:
        print(f"{c.ticker}: {c.description}")
        print(f"  Date: {c.event_date} ({c.days_until} days)")
        print(f"  Signal Score: {c.get_signal_score()}/100")
        print()
    
    # Get catalyst alerts
    alerts = service.get_catalyst_alerts(days_threshold=30)
    if alerts:
        print(f"🚨 {len(alerts)} catalyst alerts:\n")
        for alert in alerts:
            print(f"{alert['priority']} {alert['ticker']}: {alert['event']}")
            print(f"  {alert['days_until']} days - Score: {alert['score']}/100")
    
    # Test convergence integration
    print("\n🧠 Convergence Integration Test:")
    signal = service.get_catalyst_for_convergence("MU")
    if signal:
        print(f"  MU catalyst signal: {signal['score']}/100")
        print(f"  Reasoning: {signal['reasoning']}")
    
    print("\n✅ Catalyst service test complete")
