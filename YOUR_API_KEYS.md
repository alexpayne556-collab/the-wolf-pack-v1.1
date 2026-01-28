# 🔑 YOUR API KEYS

**Created:** January 27, 2026

---

## 📋 ACTIVE API KEYS

### 1. ALPACA PAPER TRADING (FREE)
```
APCA_API_KEY_ID=PKW2ON6GMKIUXKBC7L3GY4MJ2A
APCA_API_SECRET_KEY=9S25KmeAhaRPzXg4LFqcsh9YBuxQ3whzp5LavrPvSrTN
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```
**Purpose:** Paper trading execution (fake money, real market data)  
**Dashboard:** https://paper-api.alpaca.markets/  
**Cost:** FREE  
**Usage:** Currently used by terminal_brain.py, wolf_pack_trader.py

---

### 2. FINNHUB (FREE TIER)
```
FINNHUB_API_KEY=d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0
```
**Purpose:** Earnings data, company fundamentals, news  
**Dashboard:** https://finnhub.io/dashboard  
**Cost:** FREE (60 API calls/minute)  
**Usage:** Used for earnings calendar, company metrics

---

### 3. NEWSAPI (FREE DEVELOPER)
```
NEWSAPI_KEY=e6f793dfd61f473786f69466f9313fe8
```
**Purpose:** News sentiment analysis  
**Dashboard:** https://newsapi.org/account  
**Cost:** FREE (100 requests/day developer tier)  
**Usage:** Scraping headlines for sentiment scoring

---

## 📝 HOW TO USE THESE

### Option 1: Environment Variables (Windows)
```bat
set APCA_API_KEY_ID=PKW2ON6GMKIUXKBC7L3GY4MJ2A
set APCA_API_SECRET_KEY=9S25KmeAhaRPzXg4LFqcsh9YBuxQ3whzp5LavrPvSrTN
set FINNHUB_API_KEY=d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0
set NEWSAPI_KEY=e6f793dfd61f473786f69466f9313fe8
```

### Option 2: Create .env File
Copy `.env.example` to `.env` and paste these values.

### Option 3: Direct Python Usage
```python
import os

os.environ['APCA_API_KEY_ID'] = 'PKW2ON6GMKIUXKBC7L3GY4MJ2A'
os.environ['APCA_API_SECRET_KEY'] = '9S25KmeAhaRPzXg4LFqcsh9YBuxQ3whzp5LavrPvSrTN'
os.environ['FINNHUB_API_KEY'] = 'd5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0'
os.environ['NEWSAPI_KEY'] = 'e6f793dfd61f473786f69466f9313fe8'
```

---

## 🚨 SECURITY NOTES

1. **NEVER** commit these to GitHub (they're in your .bat files - be careful!)
2. These are PAPER TRADING keys only (no real money at risk)
3. Consider regenerating if you accidentally expose them
4. The .gitignore should already exclude .env files

---

## 📊 RATE LIMITS

| Service | Free Tier Limit | Notes |
|---------|----------------|-------|
| Alpaca Paper | Unlimited | Paper trading only |
| Finnhub | 60 calls/min | More than enough for scanning |
| NewsAPI | 100 calls/day | Limit to critical scans only |

---

## 🔄 WHERE THESE ARE USED

1. **wolf_brain_4am.bat** - Sets these for automated morning scans
2. **terminal_brain.py** - Uses Alpaca for paper trading
3. **autonomous_brain.py** - Full system uses all three
4. **wolfpack/** - Research system uses Finnhub + NewsAPI
