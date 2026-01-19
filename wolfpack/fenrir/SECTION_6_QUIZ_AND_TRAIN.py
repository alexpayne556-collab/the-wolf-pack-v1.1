# ============================================================================
# 🐺 FENRIR V2 - COLAB SECTION 6: QUIZ & TRAINING LOOP
# ============================================================================
# Test Fenrir's responses
# Grade them: GOOD or BAD
# Save good ones as training examples
# Note bad ones for fixing
# ============================================================================

import requests
import json
from datetime import datetime

# ============================================================================
# TALK TO FENRIR
# ============================================================================

def ask_fenrir(prompt, model="fenrir"):
    """Send a prompt to Fenrir"""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7}
    }
    try:
        response = requests.post(url, json=payload, timeout=120)
        return response.json().get('response', 'No response')
    except Exception as e:
        return f"Error: {e}"


# ============================================================================
# TEST SCENARIOS
# ============================================================================

TEST_SCENARIOS = [
    # Should give direct opinion, no disclaimers
    {
        "question": "IBRX is up 30% today on earnings beat. Should I buy?",
        "pass_criteria": "Gives direct yes/no opinion without disclaimers",
        "fail_if_contains": ["not financial advice", "do your own research", "consult", "I cannot"]
    },
    
    # Should reject no-catalyst plays
    {
        "question": "XYZ is up 15% but I can't find any news. Should I chase it?",
        "pass_criteria": "Tells you to skip it - no catalyst = no trade",
        "fail_if_contains": ["could be worth", "might continue", "not financial advice"]
    },
    
    # Should understand our constraints
    {
        "question": "NVDA looks good, should I buy some?",
        "pass_criteria": "Acknowledges it's too expensive for our account/can't get meaningful shares",
        "fail_if_contains": ["great company", "definitely buy", "not financial advice"]
    },
    
    # Should hunt, not wait
    {
        "question": "What should I be looking at for overnight holds?",
        "pass_criteria": "Actively suggests scanning/hunting, doesn't just say 'I need more info'",
        "fail_if_contains": ["I cannot", "I don't have access", "you should look"]
    },
    
    # Should understand catalysts
    {
        "question": "What makes a catalyst strong enough to hold overnight?",
        "pass_criteria": "Mentions real news (earnings, FDA, contracts) vs pump",
        "fail_if_contains": ["not financial advice", "it depends", "consult"]
    },
]


# ============================================================================
# RUN QUIZ
# ============================================================================

def run_quiz():
    """Quiz Fenrir and grade responses"""
    
    results = []
    
    print("🐺 FENRIR QUIZ - Testing personality & judgment\n")
    print("="*60)
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"\n📝 TEST {i}: {scenario['question'][:50]}...")
        
        # Get response
        response = ask_fenrir(scenario['question'])
        
        # Check for failures
        failed = False
        fail_reason = ""
        
        for bad_phrase in scenario['fail_if_contains']:
            if bad_phrase.lower() in response.lower():
                failed = True
                fail_reason = f"Contains '{bad_phrase}'"
                break
        
        # Display result
        status = "❌ FAIL" if failed else "✅ PASS"
        print(f"   {status}")
        print(f"   Response: {response[:200]}...")
        
        if failed:
            print(f"   Reason: {fail_reason}")
        
        results.append({
            'test': i,
            'question': scenario['question'],
            'response': response,
            'passed': not failed,
            'fail_reason': fail_reason if failed else "",
            'criteria': scenario['pass_criteria']
        })
    
    # Summary
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    
    print("\n" + "="*60)
    print(f"🐺 QUIZ RESULTS: {passed}/{total} passed")
    print("="*60)
    
    if passed < total:
        print("\n⚠️ NEEDS WORK:")
        for r in results:
            if not r['passed']:
                print(f"   Test {r['test']}: {r['fail_reason']}")
    
    return results


# ============================================================================
# TRAINING DATA COLLECTOR
# ============================================================================

training_examples = []

def collect_training_example(question, good_response):
    """Save a good response as training data"""
    training_examples.append({
        "instruction": question,
        "output": good_response,
        "timestamp": datetime.now().isoformat()
    })
    print(f"✅ Saved training example ({len(training_examples)} total)")


def save_training_data(filename="fenrir_training_data.json"):
    """Save all collected training examples"""
    with open(filename, 'w') as f:
        json.dump(training_examples, f, indent=2)
    print(f"💾 Saved {len(training_examples)} examples to {filename}")


# ============================================================================
# INTERACTIVE TRAINING MODE
# ============================================================================

def interactive_training():
    """Interactive mode to quiz and train Fenrir"""
    
    print("\n🐺 FENRIR INTERACTIVE TRAINING")
    print("="*60)
    print("Commands:")
    print("  Type question to ask Fenrir")
    print("  'good' - Save last response as training example")
    print("  'bad'  - Note last response needs fixing")
    print("  'quiz' - Run automated quiz")
    print("  'save' - Save training data")
    print("  'quit' - Exit")
    print("="*60)
    
    last_question = ""
    last_response = ""
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("🐺 LLHR.")
            break
        
        elif user_input.lower() == 'quiz':
            run_quiz()
        
        elif user_input.lower() == 'good':
            if last_question and last_response:
                collect_training_example(last_question, last_response)
            else:
                print("No previous response to save")
        
        elif user_input.lower() == 'bad':
            if last_response:
                print("📝 Noted. What should Fenrir have said instead?")
                better = input("Better response: ").strip()
                if better:
                    collect_training_example(last_question, better)
                    print("✅ Saved corrected example")
        
        elif user_input.lower() == 'save':
            save_training_data()
        
        else:
            # Ask Fenrir
            last_question = user_input
            last_response = ask_fenrir(user_input)
            print(f"\n🐺 Fenrir: {last_response}")


# ============================================================================
# RUN
# ============================================================================

# Run the automated quiz first
quiz_results = run_quiz()

# Then enter interactive mode
print("\n" + "="*60)
print("Entering interactive training mode...")
print("="*60)

interactive_training()
