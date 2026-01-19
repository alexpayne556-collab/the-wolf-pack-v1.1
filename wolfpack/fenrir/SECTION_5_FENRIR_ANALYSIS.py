# ============================================================================
# 🐺 FENRIR V2 - COLAB SECTION 5: FENRIR'S JUDGMENT
# ============================================================================
# Feed quality setups to Fenrir for analysis and ranking
# He gives his opinion on each, picks the best overnight holds
# ============================================================================

import requests
import json
import pandas as pd

# ============================================================================
# TALK TO FENRIR (OLLAMA)
# ============================================================================

def ask_fenrir(prompt, model="fenrir"):
    """Send a prompt to Fenrir and get response"""
    
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_ctx": 4096,
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        result = response.json()
        return result.get('response', 'No response')
    except Exception as e:
        return f"Error: {e}"


# ============================================================================
# BUILD CONTEXT FOR FENRIR
# ============================================================================

def build_hunt_report(quality_df):
    """Build the context for Fenrir to analyze"""
    
    report = """
FENRIR HUNT REPORT - TODAY'S QUALITY MOVERS

Your partner needs overnight swing trade candidates.
Constraints: ~$1,300 account, $2-50 price range, needs real catalyst.

MOVERS WITH CONFIRMED CATALYSTS:
"""
    
    for idx, row in quality_df.iterrows():
        direction = "UP" if row['change_pct'] > 0 else "DOWN"
        report += f"""
---
TICKER: {row['ticker']}
PRICE: ${row['price']}
MOVE: {row['change_pct']:+.1f}% {direction}
VOLUME: {row['volume_ratio']:.1f}x average
CATALYST: {row['catalyst']}
"""
    
    report += """
---

TASK: Analyze each setup. For overnight holds, we want:
1. Strong catalyst that could continue (not one-day news)
2. Not already too extended (room to run)
3. Volume confirms real interest
4. Price allows meaningful position size

Give your opinion on each, then rank your top 3 picks for overnight.
Be direct. No disclaimers. LLHR.
"""
    
    return report


# ============================================================================
# GET FENRIR'S ANALYSIS
# ============================================================================

# Load quality setups from Section 4
quality_df = pd.read_csv('quality_setups.csv')

if len(quality_df) == 0:
    print("❌ No quality setups found. Market might be quiet today.")
else:
    # Build the report
    hunt_report = build_hunt_report(quality_df)
    
    print("🐺 Asking Fenrir to analyze setups...\n")
    print("="*60)
    
    # Get Fenrir's analysis
    response = ask_fenrir(hunt_report)
    
    print("FENRIR'S ANALYSIS:")
    print("="*60)
    print(response)
    print("="*60)
    
    # Save the analysis
    with open('fenrir_analysis.txt', 'w') as f:
        f.write(f"DATE: Today's Hunt Report\n\n")
        f.write(f"MOVERS ANALYZED: {len(quality_df)}\n\n")
        f.write("FENRIR'S RESPONSE:\n")
        f.write(response)

print("\n✅ Section 5 Complete")
print("🐺 Fenrir has spoken")
