"""
Study the 9 winners.

For each: pull 12 months OHLCV + yfinance .info + SEC EDGAR Form 4 purchases.
Identify the "run start" — defined as the lowest close in the 60 days before
the all-time-12mo-high.  Snapshot characteristics AS OF the run-start date.
Save winners_raw.json and winners_profile.csv.
"""
from __future__ import annotations
import json, os, time, re
from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from xml.etree import ElementTree as ET

OUT = Path(__file__).parent
HDRS = {"User-Agent": "wolf-pack-research backtest@example.com"}
SESS = requests.Session(); SESS.headers.update(HDRS)

WINNERS = ["MU","INOD","BATL","RKLB","RXT","FLNC","QUBT","NNE","AEVA"]


def fetch_ohlcv_12mo(t: str) -> pd.DataFrame | None:
    for attempt in range(3):
        try:
            df = yf.Ticker(t).history(period="1y", interval="1d", auto_adjust=False)
            if df is not None and len(df) > 100:
                if df.index.tz is not None:
                    df.index = df.index.tz_convert(None)
                df.index = pd.to_datetime(df.index).normalize()
                return df
        except Exception:
            pass
        time.sleep(2 ** attempt)
    return None


def fetch_info(t: str) -> dict:
    for attempt in range(3):
        try:
            return dict(yf.Ticker(t).info or {})
        except Exception:
            time.sleep(2 ** attempt)
    return {}


def fetch_earnings_dates(t: str) -> pd.DataFrame | None:
    try:
        ed = yf.Ticker(t).earnings_dates
        if ed is None or len(ed) == 0: return None
        return ed
    except Exception:
        return None


def get_cik(t: str) -> str | None:
    r = SESS.get("https://www.sec.gov/files/company_tickers.json", timeout=20).json()
    for row in r.values():
        if row["ticker"].upper() == t:
            return str(row["cik_str"]).zfill(10)
    return None


def form4_purchases_in_window(t: str, start: str, end: str) -> list[str]:
    """Return filingDates of Form 4 purchases (code P) between start and end."""
    cik = get_cik(t)
    if not cik: return []
    try:
        r = SESS.get(f"https://data.sec.gov/submissions/CIK{cik}.json", timeout=15)
        recent = r.json().get("filings", {}).get("recent", {})
        forms = recent.get("form", []); dates = recent.get("filingDate", []); accs = recent.get("accessionNumber", [])
        candidates = [(d, a) for i, (f, d, a) in enumerate(zip(forms, dates, accs))
                     if f == "4" and start <= d <= end]
    except Exception:
        return []
    purchases = []
    for d, a in candidates:
        acc_clean = a.replace("-", "")
        base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_clean}"
        try:
            idx = SESS.get(f"{base}/", timeout=15)
            if idx.status_code != 200: continue
            m = re.search(r'href="([^"]+\.xml)"', idx.text, re.IGNORECASE)
            if not m: continue
            xml_url = m.group(1)
            if not xml_url.startswith("http"):
                xml_url = "https://www.sec.gov" + (xml_url if xml_url.startswith("/")
                                                   else f"/Archives/edgar/data/{int(cik)}/{acc_clean}/{xml_url}")
            x = SESS.get(xml_url, timeout=15)
            if "<transactionCode>P</transactionCode>" not in x.text: continue
            try:
                root = ET.fromstring(x.text)
                for tx in root.iter("nonDerivativeTransaction"):
                    for code in tx.iter("transactionCode"):
                        if (code.text or "").strip() == "P":
                            purchases.append(d)
                            break
                    else:
                        continue
                    break
            except ET.ParseError:
                pass
        except Exception:
            continue
        time.sleep(0.12)
    return sorted(set(purchases))


def analyze_winner(t: str) -> dict:
    print(f"  fetching {t}…", flush=True)
    df = fetch_ohlcv_12mo(t)
    if df is None:
        print(f"    {t}: no OHLCV"); return {"ticker": t, "error": "no_ohlcv"}
    close = df["Close"]; vol = df["Volume"]; high = df["High"]; low = df["Low"]

    # peak: day of highest close in the 12-month window
    peak_idx = close.idxmax()
    peak_pos = df.index.get_loc(peak_idx)
    peak_close = float(close.loc[peak_idx])

    # run-start: lowest close in the 60 trading days before the peak.
    # Defines "the floor the run started from".
    look_start = max(0, peak_pos - 60)
    pre = close.iloc[look_start:peak_pos+1]
    base_idx = pre.idxmin()
    base_pos = df.index.get_loc(base_idx)
    base_close = float(close.loc[base_idx])

    # biggest single-day gain in 12mo
    daily_ret = close.pct_change()
    biggest_idx = daily_ret.idxmax() if daily_ret.dropna().shape[0] else None
    biggest_pct = float(daily_ret.max() * 100) if biggest_idx is not None else None

    # 30-days-before-run-start snapshot
    snap_pos = max(0, base_pos - 1)            # day before run start (last day of "before" period)
    pre30_start_pos = max(0, snap_pos - 30)
    pre30 = df.iloc[pre30_start_pos:snap_pos+1]
    if len(pre30) >= 2:
        first_c = float(pre30["Close"].iloc[0])
        last_c  = float(pre30["Close"].iloc[-1])
        pre30_pct = (last_c / first_c - 1) * 100
        if pre30_pct < -3:   pre30_trend = "declining"
        elif pre30_pct > 3:  pre30_trend = "building"
        else:                pre30_trend = "flat"
    else:
        pre30_pct = None; pre30_trend = None

    # 52w high proximity at run-start
    h52 = float(close.iloc[:base_pos+1].rolling(min(252, base_pos+1)).max().iloc[-1]) if base_pos > 0 else float(close.iloc[0])
    l52 = float(close.iloc[:base_pos+1].rolling(min(252, base_pos+1)).min().iloc[-1]) if base_pos > 0 else float(close.iloc[0])
    proximity_52w_high = base_close / h52 if h52 > 0 else None
    proximity_52w_low  = base_close / l52 if l52 > 0 else None

    # volume: 30d avg before run, 5d avg before run, ratio
    vol30 = float(df["Volume"].iloc[max(0,base_pos-30):base_pos].mean()) if base_pos > 0 else None
    vol5  = float(df["Volume"].iloc[max(0,base_pos-5):base_pos].mean())  if base_pos > 0 else None
    vol_ratio = (vol5 / vol30) if (vol5 and vol30) else None

    # earnings beat in quarter before run-start
    ed = fetch_earnings_dates(t)
    beat_before_run = None
    last_eps_surprise_before_run = None
    last_eps_date_before_run = None
    if ed is not None and len(ed):
        ed = ed.copy()
        ed_index = pd.to_datetime(ed.index)
        try: ed_index = ed_index.tz_convert(None)
        except Exception: pass
        ed["dt"] = ed_index.normalize()
        prior = ed[ed["dt"] < pd.Timestamp(base_idx)].copy()
        if len(prior):
            row = prior.iloc[0]  # most recent
            sp = row.get("Surprise(%)")
            if pd.notna(sp):
                last_eps_surprise_before_run = float(sp)
                last_eps_date_before_run = row["dt"].date().isoformat()
                beat_before_run = bool(sp > 0)

    # SEC Form 4 purchases in 60 calendar days before run-start
    win_start = (pd.Timestamp(base_idx) - pd.Timedelta(days=60)).date().isoformat()
    win_end = pd.Timestamp(base_idx).date().isoformat()
    insider_buys = form4_purchases_in_window(t, win_start, win_end)

    # fundamentals
    info = fetch_info(t)
    out = {
        "ticker": t,
        "peak_date": peak_idx.date().isoformat(),
        "peak_close": peak_close,
        "run_start_date": base_idx.date().isoformat(),
        "run_start_close": base_close,
        "run_total_pct": (peak_close / base_close - 1) * 100 if base_close > 0 else None,
        "biggest_single_day_date": biggest_idx.date().isoformat() if biggest_idx is not None else None,
        "biggest_single_day_pct": biggest_pct,
        # 30 days before run
        "pre30_pct": round(pre30_pct, 2) if pre30_pct is not None else None,
        "pre30_trend": pre30_trend,
        "proximity_52w_high_at_run_start": round(proximity_52w_high, 3) if proximity_52w_high is not None else None,
        "proximity_52w_low_at_run_start":  round(proximity_52w_low, 3) if proximity_52w_low is not None else None,
        "vol30_avg_before_run": vol30,
        "vol5_avg_before_run":  vol5,
        "vol_ratio_5_over_30":  round(vol_ratio, 2) if vol_ratio is not None else None,
        # earnings
        "beat_before_run": beat_before_run,
        "last_eps_surprise_pct_before_run": last_eps_surprise_before_run,
        "last_eps_date_before_run": last_eps_date_before_run,
        # insider
        "insider_p_purchases_in_60d_before_run": len(insider_buys),
        "insider_p_purchase_dates": insider_buys,
        # fundamentals (CURRENT snapshot — flagged)
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "marketCap": info.get("marketCap"),
        "floatShares": info.get("floatShares"),
        "sharesOutstanding": info.get("sharesOutstanding"),
        "shortPercentOfFloat": info.get("shortPercentOfFloat"),
        "sharesShort": info.get("sharesShort"),
        "shortRatio": info.get("shortRatio"),
        "revenueGrowth": info.get("revenueGrowth"),
        "earningsGrowth": info.get("earningsGrowth"),
        "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions"),
        "currentPrice": info.get("currentPrice") or info.get("regularMarketPrice"),
    }
    return out


def main():
    raw = []
    for t in WINNERS:
        try:
            raw.append(analyze_winner(t))
        except Exception as e:
            print(f"  ERROR {t}: {e}")
            raw.append({"ticker": t, "error": str(e)})
        time.sleep(0.3)
    with open(OUT / "winners_raw.json", "w") as f:
        json.dump(raw, f, indent=2, default=str)
    df = pd.DataFrame(raw)
    df.to_csv(OUT / "winners_profile.csv", index=False)
    # Print readable summary
    cols = ["ticker","run_start_date","run_start_close","peak_close","run_total_pct",
            "biggest_single_day_pct","pre30_trend","pre30_pct",
            "proximity_52w_high_at_run_start","proximity_52w_low_at_run_start",
            "vol_ratio_5_over_30","beat_before_run","last_eps_surprise_pct_before_run",
            "insider_p_purchases_in_60d_before_run","sector","industry","marketCap",
            "floatShares","shortPercentOfFloat","revenueGrowth","numberOfAnalystOpinions"]
    have = [c for c in cols if c in df.columns]
    print("\n=== WINNERS PROFILE ===")
    print(df[have].to_string(index=False))
    print(f"\nSaved {OUT/'winners_profile.csv'} and {OUT/'winners_raw.json'}")


if __name__ == "__main__":
    main()
