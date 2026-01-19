import sys
sys.path.insert(0, 'C:\\Users\\alexp\\Desktop\\brokkr\\wolfpack\\fenrir')

from ollama_secretary import ask_ollama, get_enhanced_portfolio_context

print("Loading portfolio...")
context = get_enhanced_portfolio_context()

print(f"Positions: {len(context['positions'])}")
print(f"Dead money positions (score <=-5): {len(context['dead_money'])}")
print("")
print("Asking Ollama: 'any dead money?'")
print("")

response = ask_ollama("any dead money?", context, verbose=False)

print("RESPONSE:")
print(response)
print("")
print("EXPECTED: Should say NO dead money (all positions > -5)")
