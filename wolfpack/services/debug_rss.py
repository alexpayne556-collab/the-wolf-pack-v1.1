#!/usr/bin/env python3
"""
Quick test to debug SEC RSS feed parsing
"""

import requests
import xml.etree.ElementTree as ET

SEC_HEADERS = {
    'User-Agent': 'Wolf Pack Trading Bot alex@wolfpacktrading.com',
    'Accept-Encoding': 'gzip, deflate',
}

url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&output=atom'

print("Fetching Form 4 RSS feed...")
response = requests.get(url, headers=SEC_HEADERS, timeout=15)
print(f"Status: {response.status_code}")

# Save raw response to file
with open('form4_rss_debug.xml', 'w', encoding='utf-8') as f:
    f.write(response.text)

print("Saved raw RSS to form4_rss_debug.xml")
print(f"\nFirst 500 characters:")
print(response.text[:500])

# Try to parse
try:
    root = ET.fromstring(response.content)
    print(f"\nRoot tag: {root.tag}")
    print(f"Root attribs: {root.attrib}")
    
    # Try different namespace variations
    namespaces = [
        {'atom': 'http://www.w3.org/2005/Atom'},
        {},
        None
    ]
    
    for ns in namespaces:
        if ns:
            entries = root.findall('atom:entry', ns)
            print(f"\nWith namespace {ns}: Found {len(entries)} entries")
        else:
            # Try without namespace
            entries = root.findall('.//entry')
            print(f"\nWithout namespace: Found {len(entries)} entries")
            
        if entries:
            print(f"First entry tag: {entries[0].tag}")
            for child in entries[0]:
                print(f"  - {child.tag}: {child.text[:50] if child.text else 'None'}")
            break
    
except Exception as e:
    print(f"Parse error: {e}")
