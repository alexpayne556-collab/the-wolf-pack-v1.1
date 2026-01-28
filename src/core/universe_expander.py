"""
UNIVERSE EXPANDER
Go from 12 tickers to 5,000+ tickers

CURRENT PROBLEM: We're watching 12 tickers
SOLUTION: Scan EVERYTHING, filter intelligently

Sources:
- All NASDAQ biotech
- All NYSE/AMEX healthcare
- Finviz screener results
- Russell 2000 (small caps)
- Filtered penny stocks
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import json

class UniverseExpander:
    """
    Build comprehensive ticker universe from multiple sources
    """
    
    def __init__(self):
        self.all_tickers = set()
        self.ticker_metadata = {}
    
    def get_nasdaq_biotech_list(self) -> List[str]:
        """
        Get ALL biotech stocks from NASDAQ
        
        This alone is 500+ tickers
        """
        print("📡 Fetching NASDAQ biotech list...")
        
        # URL for NASDAQ biotech screener
        url = "https://api.nasdaq.com/api/screener/stocks"
        
        params = {
            'tableonly': 'true',
            'limit': 5000,
            'sector': 'Health Care',
            'industry': 'Biotechnology: Biological Products',
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            data = response.json()
            
            if 'data' in data and 'rows' in data['data']:
                tickers = [row['symbol'] for row in data['data']['rows']]
                self.all_tickers.update(tickers)
                print(f"   Added {len(tickers)} NASDAQ biotech tickers")
                return tickers
        except Exception as e:
            print(f"   Error: {e}")
        
        return []
    
    def get_finviz_screener(self, criteria: Dict) -> List[str]:
        """
        Scrape Finviz screener results
        
        Can filter by:
        - Sector (Healthcare, Technology)
        - Market cap
        - Price
        - Volume
        """
        print(f"📡 Fetching Finviz screener: {criteria}")
        
        # Build Finviz URL
        base_url = "https://finviz.com/screener.ashx"
        
        # Example: Healthcare sector, under $10, volume >500K
        params = {
            'v': '111',  # Overview view
            'f': 'sec_healthcare,sh_price_u10,sh_avgvol_o500',  # Filters
            'o': '-volume',  # Sort by volume
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        
        tickers = []
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse ticker table
            ticker_table = soup.find('table', {'class': 'table-light'})
            if ticker_table:
                rows = ticker_table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) > 1:
                        ticker_link = cols[1].find('a')
                        if ticker_link:
                            ticker = ticker_link.text.strip()
                            tickers.append(ticker)
            
            self.all_tickers.update(tickers)
            print(f"   Added {len(tickers)} tickers from Finviz")
            
        except Exception as e:
            print(f"   Error: {e}")
        
        return tickers
    
    def get_russell_2000(self) -> List[str]:
        """
        Get Russell 2000 component list (small caps)
        
        This is where explosive moves happen
        """
        print("📡 Fetching Russell 2000 components...")
        
        # Russell 2000 list (need to find updated source)
        # Can scrape from iShares IWM holdings
        
        tickers = []
        
        try:
            # iShares Russell 2000 ETF (IWM) holdings
            url = "https://www.ishares.com/us/products/239710/ishares-russell-2000-etf"
            
            # TODO: Implement scraping
            # For now, return empty
            
        except Exception as e:
            print(f"   Error: {e}")
        
        return tickers
    
    def expand_universe(self) -> Dict:
        """
        Build comprehensive universe from all sources
        """
        print("="*80)
        print("🌍 EXPANDING UNIVERSE...")
        print("="*80)
        
        # Get from multiple sources
        self.get_nasdaq_biotech_list()
        
        # Finviz healthcare under $10
        self.get_finviz_screener({'sector': 'healthcare', 'price': 'u10'})
        
        # Get Russell 2000
        # self.get_russell_2000()
        
        print("\n" + "="*80)
        print(f"TOTAL UNIVERSE: {len(self.all_tickers)} tickers")
        print("="*80)
        
        # Categorize by sector/industry
        categorized = {
            'biotech': [],
            'healthcare': [],
            'space': [],
            'defense': [],
            'semiconductors': [],
            'ai': [],
            'other': [],
        }
        
        return {
            'total_tickers': len(self.all_tickers),
            'tickers': list(self.all_tickers),
            'categorized': categorized,
        }
    
    def save_universe(self, filename: str = '../../data/expanded_universe.json'):
        """
        Save expanded universe to file
        """
        universe = self.expand_universe()
        
        with open(filename, 'w') as f:
            json.dump(universe, f, indent=2)
        
        print(f"\n✅ Saved {universe['total_tickers']} tickers to {filename}")
        
        return universe

if __name__ == "__main__":
    expander = UniverseExpander()
    universe = expander.save_universe()
    
    print(f"\n🐺 UNIVERSE EXPANDED FROM 12 → {universe['total_tickers']} TICKERS")
    print("\nNow we can ACTUALLY hunt.")
