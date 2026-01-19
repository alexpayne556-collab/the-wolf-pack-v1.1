#!/usr/bin/env python3
with open('wolf_pack_trader.py', 'rb') as f:
    content = f.read()

# Find line 511
lines_bytes = content.split(b'\n')
for i in range(508, 513):
    print(f"Line {i+1}: {lines_bytes[i]}")
    print(f"  Length: {len(lines_bytes[i])}")
    print(f"  Ends with: {lines_bytes[i][-10:]}")
    print()
