#!/usr/bin/env python3
"""
🐺 WOLF PACK BIOTECH CATALYST SCANNER MODULE
============================================
Integrated module for autonomous_brain.py

Scans for biotech catalysts and feeds them to Fenrir for AI analysis
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf
import time

# ============================================
# FDA CALENDAR
# ============================================

FDA_CALENDAR = {
    'OCUL': {'date': '2026-01-28', 'drug': 'Wet AMD treatment', 'type': 'PDUFA', 'indication': 'AMD'},
    'AQST': {'date': '2026-01-31', 'drug': 'AQST-109', 'indication': 'Epilepsy', 'type': 'PDUFA'},
    'PHAR': {'date': '2026-01-31', 'drug': 'Undisclosed', 'indication': 'TBD', 'type': 'PDUFA'},
    'IRON': {'date': '2026-01-31', 'drug': 'Ferric Maltol', 'indication': 'Iron Deficiency', 'type': 'PDUFA'},
    'VNDA': {'date': '2026-02-21', 'drug': 'Bysanti', 'indication': 'Bipolar/Schizo', 'type': 'PDUFA'},
    'ETON': {'date': '2026-02-25', 'drug': 'Undisclosed', 'indication': 'TBD', 'type': 'PDUFA'},
    'ASND': {'date': '2026-02-28', 'drug': 'Asc Treatment', 'indication': 'Achondroplasia', 'type': 'PDUFA'},
    'DNLI': {'date': '2026-04-05', 'drug': 'tividenofusp alfa', 'indication': 'TBD', 'type': 'PDUFA'},
    'VKTX': {'date': '2026-02-21', 'drug': 'VK2735', 'indication': 'Obesity', 'type': 'Phase 2 Data'},
    'IONS': {'date': '2026-02-15', 'drug': 'Donidalorsen', 'indication': 'HAE', 'type': 'Phase 3 Data'},
}

BIOTECH_WATCHLIST = [
    'PALI', 'NVAX', 'LXRX', 'ZURA', 'ONCY', 'AQST', 'OCUL', 'VNDA',
    'IBRX', 'MRNA', 'BNTX', 'REGN', 'VRTX', 'BIIB', 'ALNY',
    'NTLA', 'CRSP', 'BEAM', 'EDIT', 'ARWR', 'IONS', 'SRPT', 'RARE'
]


class BiotechCatalystScanner:
    """Scans for biotech catalysts and trading opportunities"""
    
    def __init__(self):
        self.fda_calendar = FDA_CALENDAR
        self.watchlist = BIOTECH_WATCHLIST
    
    def get_upcoming_catalysts(self, days_ahead: int = 30) -> List[Dict]:
        """Get catalysts in next N days"""
        today = datetime.now()
        cutoff = today + timedelta(days=days_ahead)
        
        upcoming = []
        for ticker, info in self.fda_calendar.items():
            try:
                if 'Q' in info['date']:
                    # Quarter-based date
                    upcoming.append({
                        'ticker': ticker,
                        'date': info['date'],
                        'days_until': 'Q-based',
                        'drug': info['drug'],
                        'indication': info['indication'],
                        'type': info['type'],
                        'urgency': 'LOW'
                    })
                else:
                    catalyst_date = datetime.strptime(info['date'], '%Y-%m-%d')
                    days_until = (catalyst_date - today).days
                    
                    if 0 <= days_until <= days_ahead:
                        # Determine urgency
                        if days_until <= 7:
                            urgency = 'IMMINENT'
                        elif days_until <= 14:
                            urgency = 'HIGH'
                        else:
                            urgency = 'MEDIUM'
                        
                        upcoming.append({
                            'ticker': ticker,
                            'date': info['date'],
                            'days_until': days_until,
                            'drug': info['drug'],
                            'indication': info['indication'],
                            'type': info['type'],
                            'urgency': urgency
                        })
            except Exception as e:
                pass
        
        # Sort by days_until
        upcoming.sort(key=lambda x: x['days_until'] if isinstance(x['days_until'], int) else 999)
        return upcoming
    
    def find_pdufa_runup_plays(self) -> List[Dict]:
        """Find PDUFA plays in the optimal buy window (7-14 days before)"""
        all_catalysts = self.get_upcoming_catalysts(30)
        
        runup_plays = []
        for catalyst in all_catalysts:
            if isinstance(catalyst['days_until'], int):
                # Sweet spot: 7-14 days before PDUFA
                if 7 <= catalyst['days_until'] <= 14:
                    runup_plays.append({
                        **catalyst,
                        'strategy': 'PDUFA_RUNUP',
                        'entry_zone': 'NOW',
                        'exit_strategy': 'Sell 1-2 days before decision',
                        'expected_move': '15-30% run-up',
                        'risk': 'Exit before binary event'
                    })
        
        return runup_plays
    
    def check_insider_buying(self, ticker: str) -> Optional[Dict]:
        """Check for recent insider buying (simplified - in production, scrape SEC)"""
        
        # Known insider buying patterns
        insider_data = {
            'PALI': {
                'recent_buys': 3,
                'buyers': ['Director Donald Allen Williams'],
                'total_value': 22610,
                'last_purchase': '2026-01-16',
                'signal': 'STRONG_BUY',
                'conviction': 9
            },
            'ONCY': {
                'recent_buys': 1,
                'buyers': ['Director'],
                'total_value': 'Unknown',
                'last_purchase': '2026-01-20',
                'signal': 'BUY',
                'conviction': 6
            }
        }
        
        return insider_data.get(ticker)
    
    def get_conference_movers(self) -> List[str]:
        """Tickers that recently presented at major conferences"""
        return [
            'LXRX',  # J.P. Morgan Jan 12 → FDA approval Jan 21 → +19.79%
            'ZURA',  # J.P. Morgan Jan 12
            'PALI',  # Watch for future conference announcements
        ]
    
    def scan_for_catalyst_setups(self) -> Dict:
        """Comprehensive catalyst scan - returns all opportunities"""
        
        opportunities = {
            'pdufa_runup_plays': self.find_pdufa_runup_plays(),
            'imminent_catalysts': [],
            'insider_buying_plays': [],
            'conference_movers': self.get_conference_movers(),
            'all_upcoming_catalysts': self.get_upcoming_catalysts(60)
        }
        
        # Check for imminent catalysts (0-7 days)
        for catalyst in opportunities['all_upcoming_catalysts']:
            if isinstance(catalyst['days_until'], int) and catalyst['days_until'] <= 7:
                opportunities['imminent_catalysts'].append(catalyst)
        
        # Check insider buying on watchlist
        for ticker in ['PALI', 'ONCY', 'NVAX', 'LXRX']:
            insider = self.check_insider_buying(ticker)
            if insider and insider.get('conviction', 0) >= 7:
                opportunities['insider_buying_plays'].append({
                    'ticker': ticker,
                    **insider
                })
        
        return opportunities
    
    def generate_catalyst_report(self) -> str:
        """Generate text report of catalyst opportunities"""
        
        opportunities = self.scan_for_catalyst_setups()
        
        report = []
        report.append("=" * 70)
        report.append("🧬 BIOTECH CATALYST OPPORTUNITIES")
        report.append("=" * 70)
        report.append("")
        
        # PDUFA Runup Plays (HIGHEST PRIORITY)
        if opportunities['pdufa_runup_plays']:
            report.append("🔥 PDUFA RUNUP PLAYS (7-14 days out - BUY WINDOW):")
            report.append("-" * 50)
            for play in opportunities['pdufa_runup_plays']:
                report.append(f"  • {play['ticker']}: {play['drug']} - {play['indication']}")
                report.append(f"    Date: {play['date']} ({play['days_until']} days)")
                report.append(f"    Strategy: {play['exit_strategy']}")
                report.append(f"    Expected: {play['expected_move']}")
            report.append("")
        
        # Imminent Catalysts (0-7 days)
        if opportunities['imminent_catalysts']:
            report.append("⚠️  IMMINENT CATALYSTS (0-7 days - HIGH RISK):")
            report.append("-" * 50)
            for catalyst in opportunities['imminent_catalysts']:
                report.append(f"  • {catalyst['ticker']}: {catalyst['drug']}")
                report.append(f"    Date: {catalyst['date']} ({catalyst['days_until']} days)")
                report.append(f"    ⚠️  TOO CLOSE - Only for high conviction plays")
            report.append("")
        
        # Insider Buying Signals
        if opportunities['insider_buying_plays']:
            report.append("👔 INSIDER BUYING SIGNALS:")
            report.append("-" * 50)
            for play in opportunities['insider_buying_plays']:
                report.append(f"  • {play['ticker']}: {play['signal']}")
                report.append(f"    {play['recent_buys']} buys | ${play['total_value']:,} value")
                report.append(f"    Conviction: {play['conviction']}/10")
            report.append("")
        
        # All Upcoming (30-60 days)
        report.append("📅 UPCOMING CATALYSTS (WATCH LIST):")
        report.append("-" * 50)
        for catalyst in opportunities['all_upcoming_catalysts'][:10]:
            if isinstance(catalyst['days_until'], int) and catalyst['days_until'] > 14:
                report.append(f"  • {catalyst['ticker']}: {catalyst['date']} ({catalyst['days_until']} days)")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def test_scanner():
    """Test the scanner"""
    scanner = BiotechCatalystScanner()
    
    print("\n" + "=" * 70)
    print("🧬 TESTING BIOTECH CATALYST SCANNER")
    print("=" * 70)
    
    # Test 1: Get all upcoming
    print("\n1. UPCOMING CATALYSTS (30 days):")
    catalysts = scanner.get_upcoming_catalysts(30)
    for c in catalysts[:5]:
        print(f"   {c['ticker']}: {c['date']} ({c['days_until']} days) - {c['urgency']}")
    
    # Test 2: PDUFA runup plays
    print("\n2. PDUFA RUNUP PLAYS:")
    plays = scanner.find_pdufa_runup_plays()
    for p in plays:
        print(f"   {p['ticker']}: {p['days_until']} days - {p['strategy']}")
    
    # Test 3: Full report
    print("\n3. FULL CATALYST REPORT:")
    report = scanner.generate_catalyst_report()
    print(report)


if __name__ == '__main__':
    test_scanner()
