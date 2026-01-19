#!/usr/bin/env python3
with open('wolf_pack_trader.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

count = 0
for i, line in enumerate(lines):
    if '"""' in line:
        count += 1
        print(f"{count}. Line {i+1}: {line.strip()[:80]}")
        
print(f"\nTotal: {count} triple quotes")
if count % 2 != 0:
    print("❌ ODD number - one docstring is not closed!")
