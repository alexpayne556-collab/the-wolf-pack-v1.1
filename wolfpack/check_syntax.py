#!/usr/bin/env python3
import ast

try:
    with open('wolf_pack_trader.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count triple quotes
    count = content.count('"""')
    print(f"Triple quote count: {count} {'(EVEN - OK)' if count % 2 == 0 else '(ODD - PROBLEM!)'}")
    
    # Try to parse
    try:
        ast.parse(content)
        print("✅ File parses successfully!")
    except SyntaxError as e:
        print(f"❌ Syntax error at line {e.lineno}: {e.msg}")
        
        # Show context around error
        lines = content.split('\n')
        start = max(0, e.lineno - 10)
        end = min(len(lines), e.lineno + 5)
        
        print("\nContext around error:")
        for i in range(start, end):
            prefix = ">>>" if i == e.lineno - 1 else "   "
            print(f"{prefix} {i+1}: {lines[i][:80]}")
            
except Exception as e:
    print(f"Error: {e}")
