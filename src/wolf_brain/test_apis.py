#!/usr/bin/env python3
"""Test all APIs to make sure they're working"""

import os
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv('../../.env')

import requests

print('=' * 60)
print('🧪 TESTING ALL APIs')
print('=' * 60)

# Test 1: Finnhub News
FINNHUB_KEY = os.environ.get('FINNHUB_API_KEY', '')
if FINNHUB_KEY:
    r = requests.get(f'https://finnhub.io/api/v1/company-news?symbol=AAPL&from=2026-01-15&to=2026-01-20&token={FINNHUB_KEY}', timeout=5)
    print(f'✅ FINNHUB: {len(r.json())} news articles for AAPL')
else:
    print('❌ FINNHUB: No API key')

# Test 2: NewsAPI
NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY', '')
if NEWSAPI_KEY:
    r = requests.get(f'https://newsapi.org/v2/everything?q=AAPL&pageSize=5&apiKey={NEWSAPI_KEY}', timeout=5)
    articles = r.json().get('articles', [])
    print(f'✅ NEWSAPI: {len(articles)} articles for AAPL')
else:
    print('❌ NEWSAPI: No API key')

# Test 3: Polygon
POLYGON_KEY = os.environ.get('POLYGON_API_KEY', '')
if POLYGON_KEY:
    r = requests.get(f'https://api.polygon.io/v3/reference/tickers/AAPL?apiKey={POLYGON_KEY}', timeout=5)
    data = r.json().get('results', {})
    name = data.get('name', 'N/A')
    mcap = data.get('market_cap', 0)
    print(f'✅ POLYGON: {name} - Market Cap: ${mcap/1e12:.2f}T')
else:
    print('❌ POLYGON: No API key')

# Test 4: Alpha Vantage
ALPHAVANTAGE_KEY = os.environ.get('ALPHAVANTAGE_API_KEY', '')
if ALPHAVANTAGE_KEY:
    r = requests.get(f'https://www.alphavantage.co/query?function=OVERVIEW&symbol=AAPL&apikey={ALPHAVANTAGE_KEY}', timeout=5)
    data = r.json()
    if 'Symbol' in data:
        pe = data.get('PERatio', 'N/A')
        target = data.get('AnalystTargetPrice', 'N/A')
        print(f'✅ ALPHA VANTAGE: PE={pe} | Target=${target}')
    else:
        print(f'⚠️  ALPHA VANTAGE: Rate limited or error - {data}')
else:
    print('❌ ALPHA VANTAGE: No API key')

# Test 5: Finnhub Insider
if FINNHUB_KEY:
    r = requests.get(f'https://finnhub.io/api/v1/stock/insider-transactions?symbol=AAPL&token={FINNHUB_KEY}', timeout=5)
    txns = r.json().get('data', [])
    buys = sum(1 for t in txns if t.get('transactionCode') == 'P')
    sells = sum(1 for t in txns if t.get('transactionCode') == 'S')
    print(f'✅ INSIDER DATA: {buys} buys, {sells} sells for AAPL')

# Test 6: Polygon News
if POLYGON_KEY:
    r = requests.get(f'https://api.polygon.io/v2/reference/news?ticker=AAPL&limit=5&apiKey={POLYGON_KEY}', timeout=5)
    news = r.json().get('results', [])
    print(f'✅ POLYGON NEWS: {len(news)} articles for AAPL')

print('=' * 60)
print('🎯 ALL APIs TESTED!')
print('=' * 60)
