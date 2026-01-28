#!/usr/bin/env python3
"""
BR0KKR SERVICE - Institutional Tracking
Tracks Form 4 insider transactions, 13D activist filings, cluster buys
The Smart Money Layer
"""

import requests
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# SEC EDGAR CONFIGURATION
# =============================================================================

SEC_USER_AGENT = os.getenv('SEC_USER_AGENT', 'Wolf Pack Trading tyr@wolfpacktrading.com')
SEC_BASE_URL = os.getenv('SEC_EDGAR_BASE_URL', 'https://www.sec.gov')

SEC_HEADERS = {
    'User-Agent': SEC_USER_AGENT,
    'Accept-Encoding': 'gzip, deflate',
}

SEC_BASE_URL = 'https://www.sec.gov'
EDGAR_RSS_FORM4 = f'{SEC_BASE_URL}/cgi-bin/browse-edgar?action=getcurrent&type=4&output=atom'
EDGAR_RSS_13D = f'{SEC_BASE_URL}/cgi-bin/browse-edgar?action=getcurrent&type=SC%2013D&output=atom'
EDGAR_RSS_13G = f'{SEC_BASE_URL}/cgi-bin/browse-edgar?action=getcurrent&type=SC%2013G&output=atom'


# =============================================================================
# DATA MODELS
# =============================================================================

class TransactionType(Enum):
    """Insider transaction types"""
    BUY = "P"  # Purchase
    SELL = "S"  # Sale
    AWARD = "A"  # Award (RSUs, options)
    GIFT = "G"  # Gift
    UNKNOWN = "U"


class InsiderRole(Enum):
    """Insider role types"""
    CEO = "Chief Executive Officer"
    CFO = "Chief Financial Officer"
    COO = "Chief Operating Officer"
    DIRECTOR = "Director"
    OFFICER = "Officer"
    TEN_PERCENT_OWNER = "10% Owner"
    UNKNOWN = "Unknown"


@dataclass
class InsiderTransaction:
    """Individual insider transaction"""
    ticker: str
    company_name: str
    insider_name: str
    insider_role: InsiderRole
    transaction_date: str
    shares: int
    price_per_share: float
    total_value: float
    transaction_type: TransactionType
    filing_date: str
    filing_url: str
    
    def is_buy(self) -> bool:
        """Check if transaction is a purchase"""
        return self.transaction_type == TransactionType.BUY
    
    def is_significant(self) -> bool:
        """Check if transaction is significant (>$100k)"""
        return self.total_value > 100000


@dataclass
class ClusterBuy:
    """Cluster of insider buys within short timeframe"""
    ticker: str
    company_name: str
    transactions: List[InsiderTransaction]
    total_value: float
    unique_insiders: int
    date_range_start: str
    date_range_end: str
    has_ceo: bool
    has_cfo: bool
    has_director: bool
    
    def get_score(self) -> int:
        """Calculate cluster buy signal score"""
        score = 0
        
        # Base score: number of insiders
        score += self.unique_insiders * 10
        
        # CEO buy bonus
        if self.has_ceo:
            score += 40
        
        # CFO buy bonus
        if self.has_cfo:
            score += 35
        
        # Director buy bonus
        if self.has_director:
            score += 20
        
        # Total value bonuses
        if self.total_value > 1_000_000:
            score += 30
        elif self.total_value > 500_000:
            score += 20
        elif self.total_value > 100_000:
            score += 10
        
        return min(score, 100)  # Cap at 100


@dataclass
class ActivistFiling:
    """13D/13G activist filing"""
    ticker: str
    company_name: str
    filer_name: str
    filing_type: str  # 13D or 13G
    filing_date: str
    filing_url: str
    ownership_pct: Optional[float]
    is_known_activist: bool
    activist_tier: str  # LEGENDARY, TOP_TIER, STRONG, EMERGING
    
    def get_score(self) -> int:
        """Calculate activist filing signal score"""
        score = 0
        
        # Base 13D score (more aggressive than 13G)
        if self.filing_type == "13D":
            score += 30
        else:
            score += 15
        
        # Activist tier bonus
        if self.is_known_activist:
            if self.activist_tier == "LEGENDARY":
                score += 50
            elif self.activist_tier == "TOP_TIER":
                score += 40
            elif self.activist_tier == "STRONG":
                score += 30
            elif self.activist_tier == "EMERGING":
                score += 20
        
        # Ownership bonus
        if self.ownership_pct:
            if self.ownership_pct > 10:
                score += 20
            elif self.ownership_pct > 5:
                score += 10
        
        return min(score, 100)


# =============================================================================
# KNOWN ACTIVISTS DATABASE
# =============================================================================

KNOWN_ACTIVISTS = {
    "LEGENDARY": [
        "Carl Icahn",
        "Icahn",
        "Bill Ackman",
        "Ackman",
        "Pershing Square",
        "Elliott Management",
        "Paul Singer",
        "Dan Loeb",
        "Third Point",
        "Prem Watsa",
        "Fairfax Financial",
    ],
    "TOP_TIER": [
        "Starboard Value",
        "ValueAct",
        "Jana Partners",
        "Trian Partners",
        "Nelson Peltz",
        "Corvex Management",
        "Keith Meister",
    ],
    "STRONG": [
        "Engine Capital",
        "Ancora Holdings",
        "Land & Buildings",
        "Macellum",
        "GAMCO Investors",
        "Mario Gabelli",
    ],
    "EMERGING": [
        "Mantle Ridge",
        "Legion Partners",
        "Ancora Advisors",
    ]
}


def identify_activist_tier(filer_name: str) -> tuple[bool, str]:
    """
    Check if filer is a known activist and return tier
    Returns: (is_known_activist, tier)
    """
    filer_lower = filer_name.lower()
    
    for tier, names in KNOWN_ACTIVISTS.items():
        for activist in names:
            if activist.lower() in filer_lower:
                return True, tier
    
    return False, "UNKNOWN"


# =============================================================================
# SEC EDGAR PARSERS
# =============================================================================

def fetch_recent_form4_rss(max_items: int = 100) -> List[Dict]:
    """
    Fetch recent Form 4 filings from SEC EDGAR RSS feed
    Returns list of raw filing metadata
    """
    try:
        response = requests.get(EDGAR_RSS_FORM4, headers=SEC_HEADERS, timeout=15)
        response.raise_for_status()
        
        # Parse ATOM feed
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        filings = []
        for entry in root.findall('atom:entry', ns)[:max_items]:
            filing = {}
            
            # Title usually contains: "4 - Company Name (Ticker)"
            title = entry.find('atom:title', ns)
            if title is not None:
                filing['title'] = title.text
                
                # Extract ticker from title (format varies)
                ticker_match = re.search(r'\(([A-Z]{1,5})\)', title.text)
                if ticker_match:
                    filing['ticker'] = ticker_match.group(1)
            
            # Filing date
            updated = entry.find('atom:updated', ns)
            if updated is not None:
                filing['filing_date'] = updated.text[:10]
            
            # Link to filing
            link = entry.find('atom:link', ns)
            if link is not None:
                filing['url'] = link.get('href')
            
            # Summary contains insider name and transaction details
            summary = entry.find('atom:summary', ns)
            if summary is not None:
                filing['summary'] = summary.text
            
            if filing.get('ticker'):
                filings.append(filing)
        
        return filings
    
    except Exception as e:
        print(f"Error fetching Form 4 RSS: {e}")
        return []


def parse_form4_summary(summary: str) -> Dict:
    """
    Parse Form 4 summary text to extract transaction details
    SEC summary format varies, this is best-effort parsing
    """
    result = {
        'insider_name': None,
        'insider_role': InsiderRole.UNKNOWN,
        'transaction_type': TransactionType.UNKNOWN,
        'shares': 0,
        'price': 0.0,
        'total_value': 0.0,
    }
    
    if not summary:
        return result
    
    # Extract insider name (usually first line or early in summary)
    lines = summary.split('\n')
    if lines:
        result['insider_name'] = lines[0].strip()
    
    # Detect insider role
    summary_lower = summary.lower()
    if 'chief executive' in summary_lower or 'ceo' in summary_lower:
        result['insider_role'] = InsiderRole.CEO
    elif 'chief financial' in summary_lower or 'cfo' in summary_lower:
        result['insider_role'] = InsiderRole.CFO
    elif 'chief operating' in summary_lower or 'coo' in summary_lower:
        result['insider_role'] = InsiderRole.COO
    elif 'director' in summary_lower and 'chief' not in summary_lower:
        result['insider_role'] = InsiderRole.DIRECTOR
    elif '10%' in summary or 'ten percent' in summary_lower:
        result['insider_role'] = InsiderRole.TEN_PERCENT_OWNER
    elif 'officer' in summary_lower:
        result['insider_role'] = InsiderRole.OFFICER
    
    # Detect transaction type
    if 'acquisition' in summary_lower or 'purchase' in summary_lower or 'bought' in summary_lower:
        result['transaction_type'] = TransactionType.BUY
    elif 'disposition' in summary_lower or 'sale' in summary_lower or 'sold' in summary_lower:
        result['transaction_type'] = TransactionType.SELL
    elif 'award' in summary_lower or 'grant' in summary_lower:
        result['transaction_type'] = TransactionType.AWARD
    
    # Extract shares (look for numbers followed by "shares")
    shares_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*(?:shares?|common)', summary_lower)
    if shares_match:
        shares_str = shares_match.group(1).replace(',', '')
        result['shares'] = int(shares_str)
    
    # Extract price (look for dollar amounts)
    price_match = re.search(r'\$(\d+\.?\d*)', summary)
    if price_match:
        result['price'] = float(price_match.group(1))
    
    # Calculate total value
    if result['shares'] > 0 and result['price'] > 0:
        result['total_value'] = result['shares'] * result['price']
    
    return result


def fetch_form4_transactions(tickers: List[str] = None, days_back: int = 14) -> List[InsiderTransaction]:
    """
    Fetch and parse Form 4 insider transactions
    
    Args:
        tickers: List of tickers to filter (None = all tickers)
        days_back: How many days back to fetch
    
    Returns:
        List of InsiderTransaction objects
    """
    raw_filings = fetch_recent_form4_rss(max_items=200)
    
    cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    transactions = []
    
    for filing in raw_filings:
        ticker = filing.get('ticker')
        filing_date = filing.get('filing_date', '')
        
        # Filter by ticker if specified
        if tickers and ticker not in tickers:
            continue
        
        # Filter by date
        if filing_date < cutoff_date:
            continue
        
        # Parse transaction details
        parsed = parse_form4_summary(filing.get('summary', ''))
        
        # Only track actual buys (not awards/grants)
        if parsed['transaction_type'] != TransactionType.BUY:
            continue
        
        # Skip if no value data
        if parsed['total_value'] == 0:
            continue
        
        transaction = InsiderTransaction(
            ticker=ticker,
            company_name=filing.get('title', '').split('(')[0].strip(),
            insider_name=parsed['insider_name'] or 'Unknown',
            insider_role=parsed['insider_role'],
            transaction_date=filing_date,  # Approximate (actual transaction date in XML)
            shares=parsed['shares'],
            price_per_share=parsed['price'],
            total_value=parsed['total_value'],
            transaction_type=parsed['transaction_type'],
            filing_date=filing_date,
            filing_url=filing.get('url', ''),
        )
        
        transactions.append(transaction)
    
    return transactions


def detect_cluster_buys(transactions: List[InsiderTransaction], window_days: int = 14) -> List[ClusterBuy]:
    """
    Detect cluster buys: multiple insiders buying within short timeframe
    
    Args:
        transactions: List of insider transactions
        window_days: Time window for clustering (default 14 days)
    
    Returns:
        List of ClusterBuy objects
    """
    # Group transactions by ticker
    by_ticker = {}
    for t in transactions:
        if t.ticker not in by_ticker:
            by_ticker[t.ticker] = []
        by_ticker[t.ticker].append(t)
    
    clusters = []
    
    for ticker, ticker_transactions in by_ticker.items():
        # Sort by date
        ticker_transactions.sort(key=lambda x: x.transaction_date)
        
        # Need at least 2 transactions for a cluster
        if len(ticker_transactions) < 2:
            continue
        
        # Check if transactions are within window
        date_range_start = ticker_transactions[0].transaction_date
        date_range_end = ticker_transactions[-1].transaction_date
        
        date_start = datetime.strptime(date_range_start, '%Y-%m-%d')
        date_end = datetime.strptime(date_range_end, '%Y-%m-%d')
        
        if (date_end - date_start).days > window_days:
            continue
        
        # Calculate cluster metrics
        unique_insiders = len(set(t.insider_name for t in ticker_transactions))
        total_value = sum(t.total_value for t in ticker_transactions)
        
        has_ceo = any(t.insider_role == InsiderRole.CEO for t in ticker_transactions)
        has_cfo = any(t.insider_role == InsiderRole.CFO for t in ticker_transactions)
        has_director = any(t.insider_role == InsiderRole.DIRECTOR for t in ticker_transactions)
        
        cluster = ClusterBuy(
            ticker=ticker,
            company_name=ticker_transactions[0].company_name,
            transactions=ticker_transactions,
            total_value=total_value,
            unique_insiders=unique_insiders,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            has_ceo=has_ceo,
            has_cfo=has_cfo,
            has_director=has_director,
        )
        
        clusters.append(cluster)
    
    # Sort by score (highest first)
    clusters.sort(key=lambda c: c.get_score(), reverse=True)
    
    return clusters


def fetch_recent_13d_rss(max_items: int = 50) -> List[Dict]:
    """
    Fetch recent 13D filings from SEC EDGAR RSS feed
    13D = Activist filing (intent to influence)
    """
    try:
        response = requests.get(EDGAR_RSS_13D, headers=SEC_HEADERS, timeout=15)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        filings = []
        for entry in root.findall('atom:entry', ns)[:max_items]:
            filing = {}
            
            title = entry.find('atom:title', ns)
            if title is not None:
                filing['title'] = title.text
                ticker_match = re.search(r'\(([A-Z]{1,5})\)', title.text)
                if ticker_match:
                    filing['ticker'] = ticker_match.group(1)
            
            updated = entry.find('atom:updated', ns)
            if updated is not None:
                filing['filing_date'] = updated.text[:10]
            
            link = entry.find('atom:link', ns)
            if link is not None:
                filing['url'] = link.get('href')
            
            summary = entry.find('atom:summary', ns)
            if summary is not None:
                filing['summary'] = summary.text
            
            if filing.get('ticker'):
                filings.append(filing)
        
        return filings
    
    except Exception as e:
        print(f"Error fetching 13D RSS: {e}")
        return []


def parse_13d_filing(filing: Dict) -> Optional[ActivistFiling]:
    """
    Parse 13D filing to extract activist details
    """
    ticker = filing.get('ticker')
    if not ticker:
        return None
    
    title = filing.get('title', '')
    summary = filing.get('summary', '')
    
    # Extract filer name (usually in title after "SC 13D -")
    filer_name = "Unknown"
    if ' - ' in title:
        parts = title.split(' - ')
        if len(parts) >= 2:
            filer_name = parts[1].split('(')[0].strip()
    
    # Check if known activist
    is_known, tier = identify_activist_tier(filer_name)
    
    # Try to extract ownership percentage
    ownership_pct = None
    pct_match = re.search(r'(\d+\.?\d*)%', summary)
    if pct_match:
        ownership_pct = float(pct_match.group(1))
    
    return ActivistFiling(
        ticker=ticker,
        company_name=title.split('(')[0].split('-')[-1].strip(),
        filer_name=filer_name,
        filing_type="13D",
        filing_date=filing.get('filing_date', ''),
        filing_url=filing.get('url', ''),
        ownership_pct=ownership_pct,
        is_known_activist=is_known,
        activist_tier=tier,
    )


def fetch_activist_filings(days_back: int = 30) -> List[ActivistFiling]:
    """
    Fetch recent 13D activist filings
    """
    raw_filings = fetch_recent_13d_rss(max_items=100)
    
    cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    activist_filings = []
    for filing in raw_filings:
        filing_date = filing.get('filing_date', '')
        if filing_date < cutoff_date:
            continue
        
        parsed = parse_13d_filing(filing)
        if parsed:
            activist_filings.append(parsed)
    
    # Sort by score (highest first)
    activist_filings.sort(key=lambda a: a.get_score(), reverse=True)
    
    return activist_filings


# =============================================================================
# ALERT SYSTEM
# =============================================================================

def generate_alerts(
    cluster_buys: List[ClusterBuy],
    activist_filings: List[ActivistFiling],
    cluster_threshold: int = 70,
    activist_threshold: int = 60,
) -> List[Dict]:
    """
    Generate alerts for significant institutional activity
    
    Returns list of alerts with priority levels:
    - 🔴 CRITICAL: Score 85+
    - 🟠 HIGH: Score 70-84
    - 🟡 MEDIUM: Score 50-69
    - 🟢 LOW: Score <50
    """
    alerts = []
    
    # Cluster buy alerts
    for cluster in cluster_buys:
        score = cluster.get_score()
        
        if score < cluster_threshold:
            continue
        
        # Determine priority
        if score >= 85:
            priority = "🔴 CRITICAL"
        elif score >= 70:
            priority = "🟠 HIGH"
        elif score >= 50:
            priority = "🟡 MEDIUM"
        else:
            priority = "🟢 LOW"
        
        alert = {
            'priority': priority,
            'score': score,
            'type': 'CLUSTER_BUY',
            'ticker': cluster.ticker,
            'company': cluster.company_name,
            'message': f"{cluster.unique_insiders} insiders bought ${cluster.total_value:,.0f}",
            'details': {
                'insiders': cluster.unique_insiders,
                'total_value': cluster.total_value,
                'has_ceo': cluster.has_ceo,
                'has_cfo': cluster.has_cfo,
                'date_range': f"{cluster.date_range_start} to {cluster.date_range_end}",
            }
        }
        alerts.append(alert)
    
    # Activist filing alerts
    for filing in activist_filings:
        score = filing.get_score()
        
        if score < activist_threshold:
            continue
        
        if score >= 85:
            priority = "🔴 CRITICAL"
        elif score >= 70:
            priority = "🟠 HIGH"
        elif score >= 50:
            priority = "🟡 MEDIUM"
        else:
            priority = "🟢 LOW"
        
        alert = {
            'priority': priority,
            'score': score,
            'type': 'ACTIVIST_FILING',
            'ticker': filing.ticker,
            'company': filing.company_name,
            'message': f"{filing.filer_name} filed 13D",
            'details': {
                'filer': filing.filer_name,
                'is_known': filing.is_known_activist,
                'tier': filing.activist_tier,
                'ownership_pct': filing.ownership_pct,
                'filing_date': filing.filing_date,
                'url': filing.filing_url,
            }
        }
        alerts.append(alert)
    
    # Sort by score (highest first)
    alerts.sort(key=lambda a: a['score'], reverse=True)
    
    return alerts


# =============================================================================
# MAIN API
# =============================================================================

def scan_institutional_activity(
    tickers: List[str] = None,
    days_back: int = 14,
) -> Dict:
    """
    Main API: Scan for institutional activity
    
    Args:
        tickers: List of tickers to monitor (None = all)
        days_back: How many days back to scan
    
    Returns:
        Dict with:
        - insider_transactions: List[InsiderTransaction]
        - cluster_buys: List[ClusterBuy]
        - activist_filings: List[ActivistFiling]
        - alerts: List[Dict]
    """
    print("🔍 Scanning Form 4 insider transactions...")
    transactions = fetch_form4_transactions(tickers=tickers, days_back=days_back)
    
    print("🔍 Detecting cluster buys...")
    clusters = detect_cluster_buys(transactions, window_days=days_back)
    
    print("🔍 Scanning 13D activist filings...")
    activists = fetch_activist_filings(days_back=days_back * 2)  # Wider window for activists
    
    print("🔍 Generating alerts...")
    alerts = generate_alerts(clusters, activists)
    
    return {
        'insider_transactions': transactions,
        'cluster_buys': clusters,
        'activist_filings': activists,
        'alerts': alerts,
    }


# =============================================================================
# 8-K CATALYST SCANNING (from sec_speed_scanner.py)
# =============================================================================

CATALYST_KEYWORDS = [
    # Contracts
    'contract', 'award', 'agreement', 'deal', 'order',
    # AI / Tech
    'nvidia', 'gpu', 'artificial intelligence', 'ai ', 'data center',
    # Government
    'government', 'federal', 'defense', 'military', 'nasa', 'dod', 'doe',
    # M&A
    'merger', 'acquisition', 'acquire', 'buyout', 'tender offer',
    # Dollar amounts
    'million', 'billion',
    # FDA / Biotech
    'fda', 'approval', 'clearance', 'breakthrough', 'phase 3', 'phase 2',
    # Nuclear / Energy
    'nuclear', 'uranium', 'reactor', 'power purchase',
]

SKIP_PATTERNS = [
    'executive', 'director', 'board', 'compensation', 'officer',
    'employment', 'termination', 'separation', 'resign',
]


def get_recent_8k_filings(count: int = 20) -> List[Dict]:
    """Get recent 8-K filings from SEC RSS feed"""
    url = f'{SEC_BASE_URL}/cgi-bin/browse-edgar?action=getcurrent&type=8-K&output=atom'
    
    try:
        response = requests.get(url, headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        filings = []
        for entry in root.findall('atom:entry', ns)[:count]:
            title_elem = entry.find('atom:title', ns)
            link_elem = entry.find('atom:link', ns)
            updated_elem = entry.find('atom:updated', ns)
            
            filing = {
                'title': title_elem.text if title_elem is not None else '',
                'link': link_elem.get('href') if link_elem is not None else '',
                'date': updated_elem.text if updated_elem is not None else ''
            }
            filings.append(filing)
        
        return filings
        
    except Exception as e:
        print(f"Error fetching 8-K filings: {e}")
        return []


def score_8k_filing(filing: Dict) -> tuple[int, List[str]]:
    """Score an 8-K filing based on catalyst keywords
    Returns (score, matched_keywords)
    """
    title = filing.get('title', '').lower()
    
    # Skip noise
    for skip in SKIP_PATTERNS:
        if skip in title:
            return (0, [])
    
    # Score based on keyword matches
    score = 0
    matches = []
    
    for keyword in CATALYST_KEYWORDS:
        if keyword.lower() in title:
            score += 1
            matches.append(keyword)
    
    return (score, matches)


def scan_8k_catalysts(count: int = 20) -> List[Dict]:
    """Scan recent 8-K filings for potential catalysts
    Returns list of scored filings with catalyst potential
    """
    filings = get_recent_8k_filings(count=count)
    alerts = []
    
    for filing in filings:
        score, matches = score_8k_filing(filing)
        if score >= 1:
            # Extract ticker from title (basic parsing)
            title = filing.get('title', '')
            ticker_match = re.search(r'\(([A-Z]{1,5})\)', title)
            ticker = ticker_match.group(1) if ticker_match else 'UNKNOWN'
            
            alerts.append({
                'ticker': ticker,
                'company': title.split('(')[0].strip() if '(' in title else title,
                'score': score,
                'matches': matches,
                'date': filing.get('date', ''),
                'url': filing.get('link', ''),
                'type': '8-K_CATALYST'
            })
    
    # Sort by score descending
    alerts.sort(key=lambda x: x['score'], reverse=True)
    return alerts


# =============================================================================
# GENERAL SEC FILING FUNCTIONS (from sec_fetcher.py)
# =============================================================================

def get_cik_from_ticker(ticker: str) -> Optional[str]:
    """Get CIK number from ticker symbol"""
    url = f"{SEC_BASE_URL}/cgi-bin/browse-edgar"
    params = {
        'action': 'getcompany',
        'CIK': ticker,
        'type': '8-K',
        'dateb': '',
        'owner': 'include',
        'count': '1',
        'output': 'atom'
    }
    
    try:
        response = requests.get(url, params=params, headers=SEC_HEADERS, timeout=10)
        # Extract CIK from response
        if 'CIK=' in response.text:
            start = response.text.find('CIK=') + 4
            end = response.text.find('&', start)
            if end == -1:
                end = response.text.find('"', start)
            return response.text[start:end].zfill(10)
    except Exception as e:
        print(f"Error getting CIK for {ticker}: {e}")
    
    return None


def get_company_filings(ticker: str, filing_type: str = '8-K', count: int = 10) -> List[Dict]:
    """Get recent SEC filings for a specific company
    
    Filing types:
    - 8-K: Material events (contracts, acquisitions, management changes)
    - 10-K: Annual report
    - 10-Q: Quarterly report
    - 4: Insider transactions
    - SC 13D: Activist filings
    """
    cik = get_cik_from_ticker(ticker)
    if not cik:
        return []
    
    url = f"{SEC_BASE_URL}/cgi-bin/browse-edgar"
    params = {
        'action': 'getcompany',
        'CIK': cik,
        'type': filing_type,
        'dateb': '',
        'owner': 'include',
        'count': str(count),
        'output': 'atom'
    }
    
    try:
        response = requests.get(url, params=params, headers=SEC_HEADERS, timeout=10)
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        filings = []
        for entry in root.findall('atom:entry', ns):
            title_elem = entry.find('atom:title', ns)
            link_elem = entry.find('atom:link', ns)
            updated_elem = entry.find('atom:updated', ns)
            
            filing = {
                'ticker': ticker,
                'title': title_elem.text if title_elem is not None else '',
                'link': link_elem.get('href') if link_elem is not None else '',
                'date': updated_elem.text if updated_elem is not None else '',
                'type': filing_type
            }
            filings.append(filing)
        
        return filings
        
    except Exception as e:
        print(f"Error fetching {filing_type} filings for {ticker}: {e}")
        return []


# =============================================================================
# 8-K / 10-K / 10-Q FILINGS (Material Events & Reports)
# =============================================================================

def get_recent_filings(ticker: str, filing_type: str = '8-K', count: int = 10) -> List[Dict]:
    """Get recent SEC filings for a ticker
    
    Filing types:
    - 8-K: Material events (contracts, acquisitions, management changes)
    - 10-K: Annual report
    - 10-Q: Quarterly report
    - 4: Insider trading (use Form 4 functions above instead)
    """
    
    search_url = f"{SEC_BASE_URL}/cgi-bin/browse-edgar"
    search_params = {
        'action': 'getcompany',
        'CIK': ticker,
        'type': filing_type,
        'dateb': '',
        'owner': 'include',
        'count': str(count),
        'output': 'atom'
    }
    
    try:
        response = requests.get(search_url, params=search_params, headers=SEC_HEADERS, timeout=10)
        
        if response.status_code != 200:
            return []
        
        # Parse the ATOM feed
        filings = []
        content = response.text
        
        # Find all entries
        entries = content.split('<entry>')
        for entry in entries[1:]:  # Skip first split (before first entry)
            filing = {}
            
            # Extract title
            if '<title>' in entry:
                start = entry.find('<title>') + 7
                end = entry.find('</title>', start)
                filing['title'] = entry[start:end].strip()
            
            # Extract link
            if 'href="' in entry:
                start = entry.find('href="') + 6
                end = entry.find('"', start)
                filing['url'] = entry[start:end]
            
            # Extract date
            if '<updated>' in entry:
                start = entry.find('<updated>') + 9
                end = entry.find('</updated>', start)
                filing['date'] = entry[start:end][:10]  # Just the date part
            
            # Extract summary
            if '<summary' in entry:
                start = entry.find('>', entry.find('<summary')) + 1
                end = entry.find('</summary>', start)
                summary = entry[start:end].strip()
                # Clean HTML
                summary = summary.replace('&lt;', '<').replace('&gt;', '>')
                summary = summary.replace('<b>', '').replace('</b>', '')
                filing['summary'] = summary[:300] + '...' if len(summary) > 300 else summary
            
            if filing.get('title'):
                filings.append(filing)
        
        return filings
        
    except Exception as e:
        print(f"Error fetching {filing_type} filings for {ticker}: {e}")
        return []


def get_8k_filings(ticker: str, count: int = 5) -> List[Dict]:
    """Get recent 8-K filings (material events)
    
    8-K reports major events like:
    - M&A transactions
    - Contract wins
    - Management changes
    - Bankruptcies
    - Asset sales
    """
    return get_recent_filings(ticker, filing_type='8-K', count=count)


def get_10k_filings(ticker: str, count: int = 3) -> List[Dict]:
    """Get recent 10-K filings (annual reports)"""
    return get_recent_filings(ticker, filing_type='10-K', count=count)


def get_10q_filings(ticker: str, count: int = 4) -> List[Dict]:
    """Get recent 10-Q filings (quarterly reports)"""
    return get_recent_filings(ticker, filing_type='10-Q', count=count)


def format_filings_for_context(filings: List[Dict]) -> str:
    """Format filings as string for LLM context"""
    if not filings:
        return "No recent SEC filings found."
    
    lines = []
    for f in filings[:5]:
        line = f"[{f.get('date', 'N/A')}] {f.get('title', 'No title')}"
        lines.append(line)
    
    return "\n".join(lines)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("🐺 BR0KKR SERVICE TEST\n")
    
    # Scan institutional activity
    results = scan_institutional_activity(days_back=14)
    
    print(f"\n📊 RESULTS:")
    print(f"  Insider Transactions: {len(results['insider_transactions'])}")
    print(f"  Cluster Buys: {len(results['cluster_buys'])}")
    print(f"  Activist Filings: {len(results['activist_filings'])}")
    print(f"  Alerts: {len(results['alerts'])}")
    
    # Show top alerts
    if results['alerts']:
        print(f"\n🚨 TOP ALERTS:")
        for alert in results['alerts'][:5]:
            print(f"\n  {alert['priority']} (Score: {alert['score']})")
            print(f"  {alert['ticker']}: {alert['message']}")
            if alert['type'] == 'CLUSTER_BUY':
                details = alert['details']
                roles = []
                if details['has_ceo']:
                    roles.append('CEO')
                if details['has_cfo']:
                    roles.append('CFO')
                print(f"  Roles: {', '.join(roles) if roles else 'Various'}")
                print(f"  Date Range: {details['date_range']}")
    
    # Show top cluster buys
    if results['cluster_buys']:
        print(f"\n💰 TOP CLUSTER BUYS:")
        for cluster in results['cluster_buys'][:3]:
            print(f"\n  {cluster.ticker} - Score: {cluster.get_score()}")
            print(f"  {cluster.unique_insiders} insiders bought ${cluster.total_value:,.0f}")
            roles = []
            if cluster.has_ceo:
                roles.append('CEO')
            if cluster.has_cfo:
                roles.append('CFO')
            if cluster.has_director:
                roles.append('Director')
            print(f"  Roles: {', '.join(roles)}")
    
    print("\n✅ BR0KKR test complete")
