#!/usr/bin/env python3
"""
SEC SPEED SCANNER
Get 8-K filings BEFORE Fidelity shows the move.

Free. Real-time. Edge.

Run this, watch for alerts, check Fidelity, buy if it fits.

STATUS: PROTOTYPE - Needs integration with trap detection system
"""

import urllib.request
import xml.etree.ElementTree as ET
import re
import time
from datetime import datetime
import json
import os

# ============================================================
# KEYWORDS THAT MOVE STOCKS
# ============================================================

CATALYST_KEYWORDS = [
    # Contracts
    'contract', 'award', 'agreement', 'deal', 'order',
    
    # AI / Tech
    'nvidia', 'gpu', 'artificial intelligence', 'ai ', 'data center',
    
    # Government
    'government', 'federal', 'defense', 'military', 'nasa', 'dod', 'doe',
    
    # M&A
    'merger', 'acquisition', 'acquire', 'buyout', 'tender offer',
    
    # Dollar amounts (will catch $XXM, $XXB patterns)
    'million', 'billion',
    
    # FDA / Biotech
    'fda', 'approval', 'clearance', 'breakthrough', 'phase 3', 'phase 2',
    
    # Nuclear / Energy
    'nuclear', 'uranium', 'reactor', 'power purchase',
]

# Skip these - usually noise
SKIP_PATTERNS = [
    'executive', 'director', 'board', 'compensation', 'officer',
    'audit', 'accounting', 'internal control',
]

# ============================================================
# SCANNER
# ============================================================

def get_recent_8k_filings():
    """Fetch most recent 8-K filings from SEC EDGAR"""
    url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&company=&dateb=&owner=include&count=40&output=atom'
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Research Bot (contact@example.com)'
        })
        response = urllib.request.urlopen(req, timeout=15)
        data = response.read().decode('utf-8')
        
        root = ET.fromstring(data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        filings = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text
            updated = entry.find('atom:updated', ns).text
            link = entry.find('atom:link', ns).get('href')
            summary = entry.find('atom:summary', ns)
            summary_text = summary.text if summary is not None else ''
            
            filings.append({
                'title': title,
                'updated': updated,
                'link': link,
                'summary': summary_text
            })
        
        return filings
    
    except Exception as e:
        print(f"[ERROR] Failed to fetch filings: {e}")
        return []


def extract_ticker_from_title(title):
    """Try to extract company name from SEC title"""
    # SEC format: "8-K - COMPANY NAME (CIK) (Filer)"
    match = re.search(r'8-K(?:/A)? - ([^(]+)', title)
    if match:
        return match.group(1).strip()
    return title


def get_filing_content(link):
    """Fetch the actual 8-K filing content to scan for keywords"""
    try:
        req = urllib.request.Request(link, headers={
            'User-Agent': 'Research Bot (contact@example.com)'
        })
        response = urllib.request.urlopen(req, timeout=15)
        html = response.read().decode('utf-8', errors='ignore')
        
        # Find link to actual 8-K document
        doc_match = re.search(r'href="([^"]+\.htm)"', html)
        if doc_match:
            doc_url = 'https://www.sec.gov' + doc_match.group(1)
            req2 = urllib.request.Request(doc_url, headers={
                'User-Agent': 'Research Bot (contact@example.com)'
            })
            response2 = urllib.request.urlopen(req2, timeout=15)
            return response2.read().decode('utf-8', errors='ignore').lower()
        
        return html.lower()
    
    except Exception as e:
        return ""


def find_dollar_amounts(text):
    """Extract dollar amounts from text"""
    amounts = []
    
    # Match $X million, $X billion, $XXM, $XXB
    patterns = [
        r'\$[\d,.]+ ?million',
        r'\$[\d,.]+ ?billion', 
        r'\$[\d,.]+[mb]',
        r'\$[\d,]+,000,000',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        amounts.extend(matches)
    
    return amounts


def score_filing(filing):
    """Score a filing for potential catalyst value"""
    text = (filing['title'] + ' ' + filing['summary']).lower()
    
    # Check for skip patterns first
    for skip in SKIP_PATTERNS:
        if skip in text:
            return 0, []
    
    score = 0
    matches = []
    
    for keyword in CATALYST_KEYWORDS:
        if keyword.lower() in text:
            score += 1
            matches.append(keyword)
    
    # Bonus for dollar amounts
    dollars = find_dollar_amounts(text)
    if dollars:
        score += 2
        matches.extend(dollars)
    
    return score, matches


def scan_once(seen_ids, verbose=True):
    """Run one scan cycle"""
    filings = get_recent_8k_filings()
    alerts = []
    
    for filing in filings:
        filing_id = filing['link']
        
        if filing_id in seen_ids:
            continue
        
        seen_ids.add(filing_id)
        
        score, matches = score_filing(filing)
        
        if score >= 2:  # At least 2 keyword matches
            company = extract_ticker_from_title(filing['title'])
            
            alert = {
                'time': filing['updated'][:16],
                'company': company,
                'score': score,
                'matches': matches,
                'link': filing['link']
            }
            alerts.append(alert)
            
            if verbose:
                print()
                print("=" * 60)
                print(f"🚨 ALERT: {company}")
                print(f"   Time: {filing['updated'][:16]}")
                print(f"   Score: {score}")
                print(f"   Matches: {', '.join(matches)}")
                print(f"   Link: {filing['link']}")
                print("=" * 60)
    
    return alerts


def run_scanner(interval=60):
    """Run continuous scanner"""
    print()
    print("=" * 60)
    print("🐺 SEC SPEED SCANNER - Running")
    print(f"   Checking every {interval} seconds")
    print("   Watching for: contracts, AI/NVIDIA, M&A, FDA, etc.")
    print("   Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    seen_ids = set()
    all_alerts = []
    
    # Initial scan - mark existing as seen
    print("[*] Initial scan - loading existing filings...")
    filings = get_recent_8k_filings()
    for f in filings:
        seen_ids.add(f['link'])
    print(f"[*] Loaded {len(seen_ids)} existing filings")
    print("[*] Now watching for NEW filings...")
    print()
    
    try:
        while True:
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            alerts = scan_once(seen_ids, verbose=True)
            
            if alerts:
                all_alerts.extend(alerts)
                # Save alerts to file
                with open('sec_alerts.json', 'w') as f:
                    json.dump(all_alerts, f, indent=2)
            else:
                print(f"[{timestamp}] No new catalyst filings", end='\r')
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print()
        print()
        print("[*] Scanner stopped")
        print(f"[*] Total alerts found: {len(all_alerts)}")
        if all_alerts:
            print("[*] Alerts saved to sec_alerts.json")


# ============================================================
# QUICK TEST
# ============================================================

def test_scanner():
    """Quick test - scan once and show results"""
    print()
    print("🐺 SEC SPEED SCANNER - Test Mode")
    print("=" * 60)
    
    filings = get_recent_8k_filings()
    print(f"Fetched {len(filings)} recent 8-K filings")
    print()
    
    alerts_found = 0
    for filing in filings:
        score, matches = score_filing(filing)
        company = extract_ticker_from_title(filing['title'])
        
        if score >= 1:
            alerts_found += 1
            print(f"Score {score}: {company[:40]}")
            print(f"         Matches: {', '.join(matches)}")
            print()
    
    print("=" * 60)
    print(f"Found {alerts_found} potential catalyst filings")
    print()
    print("To run continuous monitoring:")
    print("  python3 sec_speed_scanner.py")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_scanner()
    else:
        run_scanner(interval=60)
