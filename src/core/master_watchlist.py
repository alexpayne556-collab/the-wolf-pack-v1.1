"""
MASTER WATCHLIST - 20 Moonshot Candidates
Compiled from manual research + database hunting

THE TARGETS WE NEED TO WATCH
"""

MASTER_WATCHLIST = {
    'tier1_triple_threat': [
        {
            'ticker': 'GLSI',
            'name': 'Greenwich LifeSciences',
            'price': 28.0,
            'float_m': 6.57,
            'short_pct': 24.6,
            'insider_buying': 'CEO $340K+ cluster',
            'catalyst': 'Phase 3 GP2 breast cancer vaccine',
            'score': 37,
            'why': 'TRIPLE THREAT: Low float + high short + CEO buying constantly',
            'tier': 1
        },
        {
            'ticker': 'BTAI',
            'name': 'BioXcel Therapeutics',
            'price': 3.0,
            'float_m': 5.0,
            'short_pct': 15,
            'insider_buying': 'Monitor',
            'catalyst': 'sNDA Q1 2026, Fast Track, Breakthrough',
            'score': 29,
            'why': 'Phase 3 met endpoint, $10-$66 analyst targets',
            'tier': 1
        },
        {
            'ticker': 'PMCB',
            'name': 'PharmaCyte Biotech',
            'price': 0.89,
            'float_m': 6.8,
            'short_pct': 5,
            'insider_buying': 'CEO + Director $128K cluster',
            'catalyst': 'Cancer Cell-in-a-Box tech',
            'score': 27,
            'why': 'CLUSTER BUY signal, $20M cash',
            'tier': 1
        },
        {
            'ticker': 'COSM',
            'name': 'Cosmos Health',
            'price': 0.50,
            'float_m': 8.0,
            'short_pct': 3,
            'insider_buying': 'CEO $400K+ monthly',
            'catalyst': 'Greek pharma + biotech',
            'score': 25,
            'why': 'CEO buying EVERY WEEK obsessively',
            'tier': 1
        },
        {
            'ticker': 'IMNM',
            'name': 'Immunome',
            'price': 2.0,
            'float_m': 21.0,
            'short_pct': 5,
            'insider_buying': 'CEO $1M+',
            'catalyst': 'Immunome antibody cancer',
            'score': 23,
            'why': 'Major CEO conviction buy',
            'tier': 1
        }
    ],
    
    'tier2_squeeze_potential': [
        {
            'ticker': 'HIMS',
            'name': 'Hims & Hers',
            'price': 18.0,
            'float_m': 206.0,
            'short_pct': 32.2,
            'catalyst': 'GLP-1 + buyback',
            'score': 25,
            'why': 'Massive short, positive news = squeeze',
            'tier': 2
        },
        {
            'ticker': 'SOUN',
            'name': 'SoundHound AI',
            'price': 17.0,
            'float_m': 379.0,
            'short_pct': 30.2,
            'catalyst': 'AI voice, profitability 2026',
            'score': 24,
            'why': 'Heavily shorted, approaching breakeven',
            'tier': 2
        },
        {
            'ticker': 'NVAX',
            'name': 'Novavax',
            'price': 6.0,
            'float_m': 159.0,
            'short_pct': 33.5,
            'catalyst': 'Vaccine pivot',
            'score': 24,
            'why': 'High short, beaten down',
            'tier': 2
        },
        {
            'ticker': 'SMR',
            'name': 'NuScale Power',
            'price': 25.0,
            'float_m': 96.0,
            'short_pct': 23.1,
            'catalyst': 'Nuclear revival',
            'score': 24,
            'why': 'Trump policy + energy demand',
            'tier': 2
        },
        {
            'ticker': 'BBAI',
            'name': 'BigBear.ai',
            'price': 5.0,
            'float_m': 433.0,
            'short_pct': 24.5,
            'catalyst': 'Defense AI contracts',
            'score': 23,
            'why': 'On OUR list already',
            'tier': 2
        }
    ],
    
    'tier3_ultralow_float': [
        {
            'ticker': 'INTG',
            'name': 'Intergroup',
            'price': 40.0,
            'float_m': 0.36,
            'short_pct': 0.4,
            'catalyst': 'Real estate',
            'score': 23,
            'why': 'Ultra-low 360K float, needs catalyst',
            'tier': 3
        },
        {
            'ticker': 'IPW',
            'name': 'iPower',
            'price': 5.0,
            'float_m': 0.43,
            'short_pct': 16.6,
            'catalyst': 'Trading company',
            'score': 23,
            'why': 'Low float + moderate short',
            'tier': 3
        },
        {
            'ticker': 'LVLU',
            'name': 'Lulu\'s Fashion',
            'price': 2.0,
            'float_m': 0.45,
            'short_pct': 12.6,
            'catalyst': 'Fashion retail',
            'score': 22,
            'why': 'Beaten down, tiny float',
            'tier': 3
        },
        {
            'ticker': 'UPC',
            'name': 'Universe Pharma',
            'price': 2.5,
            'float_m': 0.60,
            'short_pct': 4.5,
            'catalyst': 'Chinese pharma',
            'score': 21,
            'why': 'Sub-1M float',
            'tier': 3
        }
    ],
    
    'tier4_fda_catalysts': [
        {
            'ticker': 'VNDA',
            'name': 'Vanda Pharma',
            'price': 5.0,
            'float_m': 52.6,
            'catalyst': 'PDUFA Bysanti bipolar/schizo',
            'catalyst_date': '2026-02-21',
            'score': 20,
            'why': 'FDA decision Feb 21, 2026',
            'tier': 4
        },
        {
            'ticker': 'OCUL',
            'name': 'Ocular Therapeutix',
            'price': 10.0,
            'float_m': 58.0,
            'catalyst': 'PDUFA Axpaxli wet AMD',
            'catalyst_date': '2026-01-28',
            'score': 20,
            'why': 'FDA decision Jan 28, 2026 - COMING SOON',
            'tier': 4
        },
        {
            'ticker': 'RZLT',
            'name': 'RayzeBio',
            'price': 1.77,
            'float_m': 40.0,
            'catalyst': 'H1 2026 diabetes/rare disease data',
            'catalyst_date': '2026-06-30',
            'insider_buying': 'CEO + CFO Dec 15',
            'score': 19,
            'why': 'CEO + CFO buying, data H1 2026',
            'tier': 4
        },
        {
            'ticker': 'PLX',
            'name': 'Protalix',
            'price': 1.81,
            'float_m': 30.0,
            'catalyst': 'Ongoing trials enzyme replacement',
            'insider_buying': 'CEO $101K Dec 19',
            'score': 18,
            'why': 'CEO buying, enzyme trials',
            'tier': 4
        },
        {
            'ticker': 'RLMD',
            'name': 'Relmada',
            'price': 4.12,
            'float_m': 25.0,
            'catalyst': 'CNS depression trials',
            'insider_buying': 'CEO + CFO $161K Dec 15',
            'score': 18,
            'why': 'Both execs buying together',
            'tier': 4
        }
    ]
}

# Scanners from our own research
OUR_SCANNER_FINDS = [
    {'ticker': 'SNTI', 'float_m': 9.71, 'insider_pct': 56.8, 'price': 1.03},
    {'ticker': 'VRCA', 'float_m': 3.98, 'insider_pct': 51.8, 'price': 7.26},
    {'ticker': 'INAB', 'float_m': 2.41, 'insider_pct': 24.5, 'price': 2.59},
    {'ticker': 'CYCN', 'float_m': 3.07, 'insider_pct': 26.8, 'price': 1.36}
]

# Current portfolio
CURRENT_PORTFOLIO = [
    {'ticker': 'AI', 'shares': 17, 'entry': 13.04},
    {'ticker': 'SRPT', 'shares': 11, 'entry': 21.13},
    {'ticker': 'NTLA', 'shares': 18, 'entry': 12.50},
    {'ticker': 'UUUU', 'shares': 10, 'entry': 21.94},
    {'ticker': 'LUNR', 'shares': 10, 'entry': 21.58},
    {'ticker': 'INTC', 'shares': 4, 'entry': 46.99}
]

def get_top_5():
    """Top 5 to watch CLOSEST"""
    return [
        {'rank': 1, 'ticker': 'GLSI', 'why': 'CEO buying constantly + 24.6% short + Phase 3 catalyst = PERFECT STORM'},
        {'rank': 2, 'ticker': 'BTAI', 'why': 'sNDA Q1 2026 + 5M float + Fast Track + Breakthrough'},
        {'rank': 3, 'ticker': 'PMCB', 'why': 'Cluster buy (CEO + Director) + $0.89 price + $20M cash'},
        {'rank': 4, 'ticker': 'HIMS', 'why': '32% short + GLP-1 pivot + buyback = squeeze setup'},
        {'rank': 5, 'ticker': 'SMR', 'why': 'Nuclear policy + 23% short + on wounded prey list already'}
    ]

def get_all_tickers():
    """Get flat list of all 20 tickers"""
    all_tickers = []
    for tier in MASTER_WATCHLIST.values():
        all_tickers.extend([stock['ticker'] for stock in tier])
    return all_tickers

def print_watchlist():
    """Print the master watchlist"""
    print("="*80)
    print("🐺 WOLF PACK MASTER WATCHLIST - 20 MOONSHOT CANDIDATES")
    print("="*80)
    
    print("\n📍 TIER 1: TRIPLE THREAT (Low Float + Insider + Catalyst)")
    for stock in MASTER_WATCHLIST['tier1_triple_threat']:
        print(f"\n${stock['ticker']}: ${stock['price']}")
        print(f"   Float: {stock['float_m']:.1f}M, Short: {stock['short_pct']}%")
        print(f"   Insider: {stock['insider_buying']}")
        print(f"   Catalyst: {stock['catalyst']}")
        print(f"   Why: {stock['why']}")
        print(f"   Score: {stock['score']}/40")
    
    print("\n📍 TIER 2: SQUEEZE POTENTIAL (High Short + Catalyst)")
    for stock in MASTER_WATCHLIST['tier2_squeeze_potential']:
        print(f"\n${stock['ticker']}: ${stock['price']}")
        print(f"   Float: {stock['float_m']:.1f}M, Short: {stock['short_pct']}%")
        print(f"   Catalyst: {stock['catalyst']}")
        print(f"   Why: {stock['why']}")
    
    print("\n📍 TIER 3: ULTRA-LOW FLOAT (RGC Mechanics)")
    for stock in MASTER_WATCHLIST['tier3_ultralow_float']:
        print(f"\n${stock['ticker']}: ${stock['price']}")
        print(f"   Float: {stock['float_m']:.2f}M ({stock['float_m']*1000:.0f}K shares)")
        print(f"   Short: {stock['short_pct']}%")
        print(f"   Why: {stock['why']}")
    
    print("\n📍 TIER 4: FDA CATALYSTS (Binary Events Q1-H1 2026)")
    for stock in MASTER_WATCHLIST['tier4_fda_catalysts']:
        print(f"\n${stock['ticker']}: ${stock['price']}")
        if 'catalyst_date' in stock:
            print(f"   Catalyst Date: {stock['catalyst_date']}")
        print(f"   Catalyst: {stock['catalyst']}")
        if 'insider_buying' in stock:
            print(f"   Insider: {stock['insider_buying']}")
        print(f"   Why: {stock['why']}")
    
    print("\n" + "="*80)
    print("🎯 THE TOP 5 - WATCH CLOSEST")
    print("="*80)
    for pick in get_top_5():
        print(f"\n#{pick['rank']}. ${pick['ticker']}")
        print(f"   {pick['why']}")
    
    print("\n" + "="*80)
    print(f"TOTAL WATCHLIST: {len(get_all_tickers())} tickers")
    print("="*80)


if __name__ == '__main__':
    print_watchlist()
    
    print("\n📋 ALL TICKERS:")
    print(", ".join(get_all_tickers()))
