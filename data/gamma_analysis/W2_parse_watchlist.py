"""Parse Tyr's watchlist (~300 tickers across multiple categories) into a deduped list
with category and current-holding tags.
"""
import json
from pathlib import Path

OUT = Path(__file__).parent

RAW = """
ROBINHOOD:
EZGO,CELU,SHPH,ROKU,SYRE,GVH,FC,GV,SKYQ,ONDS,PL,NEXT,VG,B,XME,
KMTS,RXRX,FSM,AMZN,CRDO,IVV,MTZ,ISPR,NET,SNOW,KRYS,WDC,SRTA,GRRR,
IBLC,STCE,NVTS,OBAI,RIME,PAVM,RIOT,TLRY,SATL,NVVE,KTOS,SIDU,UA,
TGT,UMAC,SYM,SLV,GLD,CYPH,RKLB,RCAT,HMY,TM,PII,BDRBF,MPLX,MP,
KDK,YYAI,APPS,LIN,TEVA,BMNR,GEO,CXW,PCAR,UBER,LYFT,MNDY,BA,LAC,
MCD,SNAP,MU,UEC,INTC,APTV,OKLO,LEU,QTUM,SCHA,PG,UNH,BSX,LLY,ALK,
LMT,SEA,PHOE,RIG,WULF,AQMS,ACB,SNDL,NNNN,GHRS,PALI,DLB,ISRG,ALB,
HOOD,TSLA,NOW,WDC,AMD,NVDA,MU,ASTS,XBIO,EVLV,NIO,UPC,BEN,GRAL,
APGE,FIG,CNMD,KFFB,WYY,RXT,SQFT,UUUU,ANNX,BAC,WSHP,AVGO,MRVL,
QCOM,STX,OPEN,CEG,INOD,MS,WPM,IREN,COIN,GDX,CIFR,NOC,HL,MUX,TEM,
TDOC,HTHIY,SOFI,JD,JPM,CVS,GEV,GE,PDC,CPSH,FLNA,CNSP,RIVN,GOOW,
META,GOOGL,MSFT,BATL,TPET,WTI,IMO,DSX,NTLA,KYTX,CUE,BMNU,RPGL,
RPAY,UCAR,PBM,FRMM,EFOI,BZAI,SNYR,BOXL,RECT,MVST,RR,AIFF,PGEN

FIDELITY SEMICONDUCTORS:
MU,MRVL,NVDA,AMD,INTC,TSM,AVGO,AMAT,LRCX,KLAC,ASML,QCOM,ARM,ON,
STX,WDC,COHR,CRDO,ANET,CSCO,ALAB,CDNS,SNPS,CEVA,SYNA,FN,AMKR,
CAMT,ONTO,LITE

FIDELITY AI INFRASTRUCTURE:
ONTO,LITE,IREN,CORZ,APLD,CIFR,VRT,MOD,ETN,GEV,PWR,FIX,STRL,WLDN,
DLR,EQIX,AMT,NVT,PSTG,MRNO,MUU,CVU,AVD,VELO,ISSC,BIOX,SES,UMAC,
INSG,TATT

FIDELITY NUCLEAR/ENERGY:
UEC,UUUU,CCJ,DNN,LEU,NXE,LTBR,URG,UROY,SMR,OKLO,BWXT,CEG,VST,
TLN,NRG,NEE,TPET,BATL,TMDE

FIDELITY MINERALS:
MP,ALB,FCX,LAC,XPON

FIDELITY CYBERSECURITY:
CRWD,PANW,ZS,S,NET,FTNT,OKTA,CYBR,TENB,QLYS

FIDELITY DEFENSE/SPACE:
KTOS,PLTR,RCAT,RDW,LUNR,RKLB,PL,BKSY,ASTS,SPIR,GSAT,IRDM,VSAT,
AXON,LMT,NOC,RTX,GD,LHX,BAH,CACI,LDOS,SAIC,MRCY,DRS,AVAV,ACHR,
JOBY,DPRO,SIDU

FIDELITY QUANTUM/BIOTECH:
IONQ,QBTS,RGTI,QUBT,ARQQ,LAES,BTQ,NTLA,CRSP,BEAM,DNA,EDIT,SANA,
RLAY,FATE,ALT,KYTX,NBIS,SOUN,GPCR

FIDELITY MOVERS:
RKT,UPST,BIDU,BILI,CELH,HE,SLV,KULR,SKIL,SATL,ZIM,BABA,CAVA,GME,
JD,NIO,PDD,RGR,LCID,LI,TSLA,XPEV,HUYA,STNG,INSW,CGC,SNDL,NVAX,
MRNA,AEHR,AEVA,ACB,ANNX,BTDR,CFLT,CURLF,DAWN,DVAX,ENPH,FORM,FSLR,
GTLB,GPCR,ICHR,GTBIF,IBRX,IVF,MARA,MSTR,RGC,RIOT,SEDG,SLAB,RXRX,
SAVA,TMDX,TXG,OUST,PATH

FIDELITY WOLFPACKALL:
KTOS,RCAT,AVAV,WTI,KOS,INDO,MXC,REI,NAT,TOPS,FRO,STNG,TNK,MOS,
NTR,CF,AA,CENX,KALU,UEC,CCJ,LEU,DNN,RCKT,HOWL,TIL,NSP,JAN,SBSW,
RKLB,PLAY,GO,BORR,GRCE,GSM,MOBX,NCNO,RCKT

FIDELITY OTHER:
HIMS,EOSE,KSS,FFAI,IONQ,RDW,BIRD,WKHS,GCL,GAUZ,TIVC,IFRX,SST,
ARTL,IZM,ATPC,GVH,CETY,NTRP,MSC
"""

HOLDINGS = {
    "INTC": {"shares": 3, "broker": "Fidelity", "pl_pct": None},
    "QUBT": {"shares": 4, "broker": "Fidelity", "pl_pct": None},
    "VG":   {"shares": 5, "broker": "Robinhood", "pl_pct": +19},
    "BSX":  {"shares": 3, "broker": "Robinhood", "pl_pct": None},
    "FIG":  {"shares": 100, "broker": "Fidelity", "pl_pct": -35},
    "BATL": {"shares": 200, "broker": "Fidelity", "pl_pct": -85},
    "TPET": {"shares": 100, "broker": "Fidelity", "pl_pct": -74},
    "TMDE": {"shares": 500, "broker": "Fidelity", "pl_pct": -46},
}

def parse():
    cat = None
    by_ticker: dict[str, dict] = {}
    for line in RAW.splitlines():
        line = line.strip()
        if not line: continue
        if line.endswith(":") and not "," in line:
            cat = line[:-1].strip()
            continue
        for token in line.split(","):
            t = token.strip().upper()
            if not t or not t.replace(".","").isalnum(): continue
            if len(t) > 5: continue
            entry = by_ticker.setdefault(t, {"ticker": t, "categories": []})
            if cat and cat not in entry["categories"]:
                entry["categories"].append(cat)
    # Annotate holdings
    for t, h in HOLDINGS.items():
        if t not in by_ticker:
            by_ticker[t] = {"ticker": t, "categories": ["CURRENT_HOLDING_ONLY"]}
        by_ticker[t].update({"holding": h})
    return sorted(by_ticker.values(), key=lambda x: x["ticker"])

def main():
    rows = parse()
    print(f"unique tickers: {len(rows)}")
    holdings_present = sum(1 for r in rows if r.get("holding"))
    print(f"current-holding tickers: {holdings_present}")
    with open(OUT / "watchlist_parsed.json","w") as f:
        json.dump(rows, f, indent=2)
    print(f"saved {OUT/'watchlist_parsed.json'}")

if __name__ == "__main__":
    main()
