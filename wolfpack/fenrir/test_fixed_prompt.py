#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test of the fixed Ollama prompt
"""
import sys
import os

# Fix Windows console encoding
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, 'C:\\Users\\alexp\\Desktop\\brokkr\\wolfpack\\fenrir')

from ollama_secretary import ask_ollama, get_enhanced_portfolio_context

print("=" * 60)
print("TESTING FIXED OLLAMA PROMPT")
print("=" * 60)
print("\nLoading portfolio data...")

# Get portfolio context
context = get_enhanced_portfolio_context()

print(f"Loaded {len(context['positions'])} positions")
print(f"   Dead money: {len(context['dead_money'])} positions")
print(f"   Weak theses: {len(context['weak_theses'])} positions")
print(f"   Strong runners: {len(context['strong_runners'])} positions")

print("\nAsking: 'any dead money?'\n")

# Test the query
response = ask_ollama("any dead money?", context, verbose=False)

print("\nFenrir's response:")
print("-" * 60)
print(response)
print("-" * 60)

print("\nTest complete!")
print("\nCORRECT ANSWER (for validation):")
print("   NO dead money (all positions > -5)")
print("   All theses 8-10/10 STRONG")
print("   WATCH positions: UUUU (-2), KTOS (-1), MU (-3)")
print("   RUNNING: IBRX (+5)")
