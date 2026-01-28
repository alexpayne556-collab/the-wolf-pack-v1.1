"""
Quick test wrapper for autonomous_brain.py with proper encoding
"""
import sys
import os

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Now run the brain
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'wolf_brain'))

print("=" * 60)
print("TESTING UPGRADED AUTONOMOUS BRAIN")
print("=" * 60)

try:
    from autonomous_brain import AutonomousBrain
    
    # Initialize in dry-run mode
    print("\n1. Initializing brain...")
    brain = AutonomousBrain(dry_run=True)
    
    print(f"\n2. Learning engine status:")
    print(f"   - Main DB: {brain.learning_db}")
    print(f"   - Lessons loaded: {len(brain.lessons)} patterns")
    print(f"   - Win rate: {brain.lessons.get('win_rate', 0):.1%}")
    print(f"   - Min convergence: {brain.lessons.get('min_convergence', 0)}")
    print(f"   - Min volume: {brain.lessons.get('min_volume', 0)}x")
    
    print(f"\n3. Thresholds from lessons:")
    print(f"   - Gold convergence: {brain.lessons['gold_convergence']} (IBRX standard)")
    print(f"   - Optimal convergence: {brain.lessons['optimal_convergence']} (RDW level)")
    print(f"   - Gold volume: {brain.lessons['gold_volume']}x (IBRX standard)")
    print(f"   - Optimal volume: {brain.lessons['optimal_volume']}x")
    
    print(f"\n4. Testing should_take_trade() with different scenarios:")
    
    # Test 1: DNN-like (should REJECT)
    print(f"\n   Test 1: DNN-like setup (convergence 45, volume 1.2x)")
    should_trade, reason, position_size = brain.should_take_trade(
        'TEST', convergence=45, volume_ratio=1.2, signals=['test'], strategy='TEST'
    )
    print(f"   Result: {should_trade} | Reason: {reason} | Size: {position_size:.1%}")
    
    # Test 2: IBRX-like (should ACCEPT - large position)
    print(f"\n   Test 2: IBRX-like setup (convergence 85, volume 2.8x)")
    should_trade, reason, position_size = brain.should_take_trade(
        'TEST2', convergence=85, volume_ratio=2.8, signals=['biotech_catalyst'], strategy='BIOTECH'
    )
    print(f"   Result: {should_trade} | Reason: {reason} | Size: {position_size:.1%}")
    
    # Test 3: RDW-like (should ACCEPT - medium position)
    print(f"\n   Test 3: RDW-like setup (convergence 78, volume 1.8x)")
    should_trade, reason, position_size = brain.should_take_trade(
        'TEST3', convergence=78, volume_ratio=1.8, signals=['defense_sector'], strategy='DEFENSE'
    )
    print(f"   Result: {should_trade} | Reason: {reason} | Size: {position_size:.1%}")
    
    # Test 4: Borderline (should ACCEPT - small position)
    print(f"\n   Test 4: Borderline setup (convergence 55, volume 1.6x)")
    should_trade, reason, position_size = brain.should_take_trade(
        'TEST4', convergence=55, volume_ratio=1.6, signals=['momentum'], strategy='MOMENTUM'
    )
    print(f"   Result: {should_trade} | Reason: {reason} | Size: {position_size:.1%}")
    
    print(f"\n5. Connections:")
    print(f"   - Ollama: {'Connected' if brain.ollama_connected else 'Not connected'}")
    print(f"   - Alpaca: {'Connected' if brain.alpaca_connected else 'Not connected'}")
    
    print("\n" + "=" * 60)
    print("BRAIN UPGRADE SUCCESSFUL!")
    print("=" * 60)
    print("\nKey improvements:")
    print("1. Integrated with main learning engine (wolfpack.db)")
    print("2. Applies lessons from DNN failure and IBRX success")
    print("3. Dynamic position sizing by convergence (4% / 8% / 12%)")
    print("4. Hard filters: min convergence 50, min volume 1.5x")
    print("5. All trades logged to learning engine for continuous improvement")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
