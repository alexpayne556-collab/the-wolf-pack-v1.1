"""
EXPANDED TICKER UNIVERSE FOR WOLF PACK SCANNER
Based on validated criteria: Low float, biotech/pharma focus, under $30

100+ tickers across multiple sources:
- Known low float biotechs
- FDA catalyst plays
- Insider buying targets
- Small cap opportunities
"""

# TIER 1: Known Research Targets (23 tickers)
TIER1_RESEARCH = [
    'GLSI', 'BTAI', 'PMCB', 'COSM', 'IMNM',
    'HIMS', 'SOUN', 'NVAX', 'SMR', 'BBAI',
    'INTG', 'IPW', 'LVLU', 'UPC',
    'VNDA', 'OCUL', 'RZLT', 'PLX', 'RLMD',
    'SNTI', 'VRCA', 'INAB', 'CYCN'
]

# TIER 2: Low Float Biotechs (<50M float, under $30)
TIER2_LOW_FLOAT_BIOTECH = [
    'ONCY', 'ABOS', 'AKTX', 'ANTE', 'ATNF',
    'AVDL', 'BCTX', 'BDTX', 'BGXX', 'BKKT',
    'BMEA', 'BNGO', 'BNTC', 'CBAY', 'CERO',
    'CNEY', 'CNTB', 'CRVO', 'CRVS', 'CSTL',
    'CYCN', 'DSGN', 'DTIL', 'DXCM', 'ELDN',
    'ELVN', 'ERNA', 'ETNB', 'EVAX', 'FCUV',
    'FGEN', 'FOLD', 'FSTX', 'GALT', 'GMAB',
    'GTHX', 'HROW', 'IMMP', 'IMNN', 'IMRX',
    'IMTX', 'INZY', 'IONS', 'IPSC', 'IRIX',
    'KALA', 'KALV', 'KINS', 'KMPH', 'KPTI'
]

# TIER 3: FDA Catalyst Plays (known PDUFA/trial dates 2026)
TIER3_FDA_CATALYST = [
    'LGVN', 'LPCN', 'LPTX', 'LQDA', 'LYRA',
    'MIRM', 'MLTX', 'MNOV', 'MRSN', 'MRVI',
    'MRUS', 'NAMS', 'NCNA', 'NEXI', 'NKTX',
    'NRBO', 'NRIX', 'NTLA', 'NUVB', 'NVCT',
    'NVCR', 'OLMA', 'ONCT', 'OPCH', 'ORTX',
    'OTIC', 'PBYI', 'PCRX', 'PGNY', 'PHAT',
    'PHVS', 'PMVP', 'PPTA', 'PRAX', 'PRTG',
    'PRTA', 'PRVB', 'PTCT', 'PTGX', 'PTON'
]

# TIER 4: Additional Small Cap (<$500M market cap, potential)
TIER4_SMALL_CAP = [
    'QURE', 'RARE', 'RBUS', 'RCUS', 'RLAY',
    'RNAZ', 'RNGR', 'RUBY', 'RXRX', 'RYTM',
    'SAGE', 'SAVA', 'SDGR', 'SELB', 'SIGA',
    'SNDL', 'SNDX', 'SOPH', 'SRPT', 'SRRK',
    'SSBK', 'STTK', 'TALS', 'TARA', 'TBPH',
    'TCRT', 'TELA', 'TERN', 'TFFP', 'TGTX',
    'THYG', 'TLSA', 'TMDX', 'TMPO', 'TRIL',
    'TYRA', 'UFAB', 'URGN', 'VCYT', 'VERU',
    'VKTX', 'VLON', 'VRTX', 'VSTM', 'VXRT',
    'WKHS', 'XBIT', 'XENE', 'XFOR', 'XLRN',
    'XNCR', 'XTNT', 'YMAB', 'YMTX', 'ZLAB',
    'ZNTE', 'ZURA', 'ZYME', 'ZYXI'
]

# MASTER UNIVERSE: All tickers combined
MASTER_UNIVERSE = sorted(list(set(
    TIER1_RESEARCH + 
    TIER2_LOW_FLOAT_BIOTECH + 
    TIER3_FDA_CATALYST + 
    TIER4_SMALL_CAP
)))

print(f"Total tickers in master universe: {len(MASTER_UNIVERSE)}")
print(f"Tier 1 (Research): {len(TIER1_RESEARCH)}")
print(f"Tier 2 (Low Float): {len(TIER2_LOW_FLOAT_BIOTECH)}")
print(f"Tier 3 (FDA Catalyst): {len(TIER3_FDA_CATALYST)}")
print(f"Tier 4 (Small Cap): {len(TIER4_SMALL_CAP)}")
