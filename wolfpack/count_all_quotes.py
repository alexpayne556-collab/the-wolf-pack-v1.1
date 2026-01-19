#!/usr/bin/env python3
with open('wolf_pack_trader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Count ALL occurrences
count = content.count('"""')
print(f"Total '\"\"\"' in file: {count}")

# Now find them
import re
matches = list(re.finditer(r'"""', content))
print(f"Found {len(matches)} matches with regex")

# Show them
for i, match in enumerate(matches, 1):
    start = max(0, match.start() - 20)
    end = min(len(content), match.end() + 20)
    context = content[start:end].replace('\n', '\\n')
    print(f"{i}. Position {match.start()}: ...{context}...")
