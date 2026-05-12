"""Delta-fetch: bottleneck/notable names that were excluded by the avg-close filter.

These tickers may have spent part of the window above $200 but had qualifying days below.
The original universe filter (avg close <= 200) excluded them. Re-include their full OHLCV
so the backtest can evaluate them on days when entry_price <= 200.
"""
import pickle, time
from pathlib import Path
import yfinance as yf

OUT = Path(__file__).parent

EXTRA = [
    # User's bottleneck list
    "MU","WOLF","TGB","LXFR","IE","ERO","AMSC","AMKR","POWI","NVT","SMR","ALGM","OKLO",
    # Common big-move names from 2025-2026
    "PLTR","GME","AMC","RKLB","SOFI","HOOD","RIOT","MARA","CIFR","WULF","BITF","HUT",
    "BBAI","SOUN","DJT","TRUMP","RDDT","ASTS","DNN","UEC","UUUU","LEU","NNE","BWXT",
    "VST","TLN","CEG","NRG","ETR",
    # Highly-shorted small caps people have flagged
    "BYND","UPST","FUBO","CVNA","WOOF","DJT","CHGG","BIRD","RIVN","LCID",
]

def main():
    with open(OUT / "ohlcv.pkl", "rb") as f:
        OHLCV = pickle.load(f)
    print(f"current universe: {len(OHLCV)}")

    to_fetch = sorted(set(EXTRA) - set(OHLCV.keys()))
    print(f"to fetch (not in universe): {len(to_fetch)}: {to_fetch}")
    if not to_fetch:
        print("nothing to add")
        return

    # yfinance batch download, no price filter
    df = yf.download(" ".join(to_fetch), period="8mo", interval="1d",
                     group_by="ticker", auto_adjust=False, progress=False, threads=True)
    import pandas as pd
    added = 0
    if isinstance(df.columns, pd.MultiIndex):
        for t in to_fetch:
            if t in df.columns.get_level_values(0):
                sub = df[t].dropna(how="all")
                if len(sub) >= 100 and "Close" in sub.columns:
                    OHLCV[t] = sub
                    added += 1
    print(f"added: {added}")

    with open(OUT / "ohlcv.pkl", "wb") as f:
        pickle.dump(OHLCV, f)
    print(f"new universe: {len(OHLCV)}  saved.")

if __name__ == "__main__":
    main()
