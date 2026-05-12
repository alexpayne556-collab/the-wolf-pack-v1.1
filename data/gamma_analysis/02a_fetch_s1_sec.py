"""Signal 1 via SEC EDGAR — faster than Finnhub because most tickers have no Form 4 in window.

Strategy:
  1. Build ticker -> CIK map from company_tickers.json
  2. Per ticker, fetch /submissions/CIK{cik}.json (one call, ~3-15 KB)
  3. Filter recent filings to form == '4' with filingDate in 2025-09 to 2026-05
  4. For each Form 4 filing in window, fetch the index then the primary XML
  5. Parse XML for non-derivative transaction with transactionCode == 'P' (purchase)
"""
from __future__ import annotations
import json, pickle, re, time, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from xml.etree import ElementTree as ET

OUT = Path(__file__).parent
HDRS = {"User-Agent": "wolf-pack-research backtest@example.com"}
SESS = requests.Session()
SESS.headers.update(HDRS)

WINDOW_FROM = "2025-09-01"
WINDOW_TO   = "2026-05-15"

def get_ticker_cik_map() -> dict[str, str]:
    r = SESS.get("https://www.sec.gov/files/company_tickers.json", timeout=20)
    r.raise_for_status()
    data = r.json()
    out = {}
    for row in data.values():
        t = row["ticker"].upper()
        cik = str(row["cik_str"]).zfill(10)
        out[t] = cik
    return out

def list_form4_filings(cik: str) -> list[tuple[str, str]]:
    """Return list of (filingDate, accessionNumber) for Form 4 filings in window."""
    try:
        r = SESS.get(f"https://data.sec.gov/submissions/CIK{cik}.json", timeout=15)
        if r.status_code != 200: return []
        recent = r.json().get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accs  = recent.get("accessionNumber", [])
        out = []
        for i, f in enumerate(forms):
            if f != "4": continue
            d = dates[i]
            if d < WINDOW_FROM or d > WINDOW_TO: continue
            out.append((d, accs[i]))
        return out
    except Exception:
        return []

def is_purchase(cik: str, accession: str) -> bool:
    """Fetch Form 4 XML and check for any non-derivative transaction with code 'P'."""
    acc_clean = accession.replace("-", "")
    # Filing index lists files
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_clean}"
    try:
        r = SESS.get(f"{base}/", timeout=15)
        if r.status_code != 200: return False
        # Find primary XML file in index page
        m = re.search(r'href="([^"]+\.xml)"', r.text, re.IGNORECASE)
        if not m: return False
        xml_url = m.group(1)
        if not xml_url.startswith("http"):
            xml_url = "https://www.sec.gov" + (xml_url if xml_url.startswith("/") else f"/Archives/edgar/data/{int(cik)}/{acc_clean}/{xml_url}")
        r = SESS.get(xml_url, timeout=15)
        if r.status_code != 200: return False
        # Quick text search before XML parsing — most Form 4s won't have <transactionCode>P</transactionCode>
        if "<transactionCode>P</transactionCode>" not in r.text:
            return False
        # Confirm it's in a non-derivative transaction block
        try:
            root = ET.fromstring(r.text)
        except ET.ParseError:
            return False
        for tx in root.iter("nonDerivativeTransaction"):
            for code in tx.iter("transactionCode"):
                if (code.text or "").strip() == "P":
                    return True
        return False
    except Exception:
        return False


def process_ticker(ticker: str, cik: str) -> list[str]:
    filings = list_form4_filings(cik)
    if not filings: return []
    purchase_dates = []
    for fdate, acc in filings:
        if is_purchase(cik, acc):
            purchase_dates.append(fdate)
    return sorted(set(purchase_dates))


def main():
    with open(OUT / "ohlcv.pkl", "rb") as f:
        OHLCV = pickle.load(f)
    tickers = sorted(OHLCV.keys())

    print(f"[S1-SEC] mapping tickers to CIK…")
    t2cik = get_ticker_cik_map()
    pairs = [(t, t2cik.get(t)) for t in tickers]
    have_cik = [p for p in pairs if p[1]]
    print(f"  tickers with CIK: {len(have_cik)}/{len(tickers)}")

    out: dict = {}
    out_path = OUT / "signal1_insider_buys.json"
    t0 = time.time(); last = 0
    print(f"[S1-SEC] fetching submissions + per-filing XML, 8 workers")
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(process_ticker, t, c): t for t, c in have_cik}
        for i, f in enumerate(as_completed(futures), 1):
            t = futures[f]
            try:
                out[t] = f.result()
            except Exception:
                out[t] = []
            if time.time() - last > 5:
                n_with = sum(1 for v in out.values() if v)
                rate = i / (time.time() - t0)
                eta = (len(have_cik) - i) / rate / 60 if rate else 0
                print(f"  S1-SEC: {i}/{len(have_cik)}  with-buys={n_with}  rate={rate:.1f}/s  ETA={eta:.1f}m", flush=True)
                with open(out_path, "w") as fh:
                    json.dump(out, fh)
                last = time.time()
    # Fill in tickers without CIK as empty
    for t, c in pairs:
        if not c:
            out.setdefault(t, [])
    with open(out_path, "w") as fh:
        json.dump(out, fh)
    n_with = sum(1 for v in out.values() if v)
    print(f"[S1-SEC] done in {(time.time()-t0)/60:.1f}m — tickers with >=1 purchase: {n_with}")


if __name__ == "__main__":
    main()
