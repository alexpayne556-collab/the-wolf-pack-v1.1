#!/usr/bin/env python3
with open('wolf_pack_trader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Show context around position 595
start = 550
end = 650
print(f"Content from {start} to {end}:")
print(content[start:end])
print("\n" + "="*70)
print("Around position 595 specifically:")
print(content[580:610])
