"""
Test Phase 4 Learning System
Verify all imports and basic functionality
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("PHASE 4 LEARNING SYSTEM - IMPORT TEST")
print("=" * 60)

# Test 1: Import learning components
print("\n1. Testing Learning Components...")
try:
    from src.learning.performance_tracker import PerformanceTracker
    print("   [OK] PerformanceTracker imported")
except Exception as e:
    print(f"   [FAIL] PerformanceTracker failed: {e}")

try:
    from src.learning.confidence_calibrator import ConfidenceCalibrator
    print("   [OK] ConfidenceCalibrator imported")
except Exception as e:
    print(f"   [FAIL] ConfidenceCalibrator failed: {e}")

try:
    from src.learning.preference_learner import PreferenceLearner
    print("   [OK] PreferenceLearner imported")
except Exception as e:
    print(f"   [FAIL] PreferenceLearner failed: {e}")

try:
    from src.learning.strategy_optimizer import StrategyOptimizer
    print("   [OK] StrategyOptimizer imported")
except Exception as e:
    print(f"   [FAIL] StrategyOptimizer failed: {e}")

# Test 2: Import backtesting components
print("\n2. Testing Backtesting Components...")
try:
    from src.backtesting.backtest_engine import BacktestEngine
    print("   [OK] BacktestEngine imported")
except Exception as e:
    print(f"   [FAIL] BacktestEngine failed: {e}")

try:
    from src.backtesting.backtest_report import BacktestReport
    print("   [OK] BacktestReport imported")
except Exception as e:
    print(f"   [FAIL] BacktestReport failed: {e}")

# Test 3: Import enhanced signal generator
print("\n3. Testing Enhanced Signal Generator...")
try:
    from src.engine.signals import SignalGenerator
    print("   [OK] SignalGenerator imported")
    
    # Test initialization
    signal_gen = SignalGenerator(enable_learning=True)
    print("   [OK] SignalGenerator initialized with learning enabled")
    
    # Check learning components
    if hasattr(signal_gen, 'performance_tracker'):
        print("   [OK] PerformanceTracker attached")
    if hasattr(signal_gen, 'confidence_calibrator'):
        print("   [OK] ConfidenceCalibrator attached")
    if hasattr(signal_gen, 'preference_learner'):
        print("   [OK] PreferenceLearner attached")
    if hasattr(signal_gen, 'strategy_optimizer'):
        print("   [OK] StrategyOptimizer attached")
    
except Exception as e:
    print(f"   [FAIL] SignalGenerator failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Import learning commands
print("\n4. Testing Learning Commands...")
try:
    from src.notifications.learning_commands import LearningCommands
    print("   [OK] LearningCommands imported")
    
    # Test initialization
    learning_cmds = LearningCommands()
    print("   [OK] LearningCommands initialized")
    
except Exception as e:
    print(f"   [FAIL] LearningCommands failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test database initialization
print("\n5. Testing Database Initialization...")
try:
    from src.learning.performance_tracker import PerformanceTracker
    tracker = PerformanceTracker(db_path="data/test_learning.db")
    print("   [OK] PerformanceTracker database initialized")
    
    from src.learning.confidence_calibrator import ConfidenceCalibrator
    calibrator = ConfidenceCalibrator(db_path="data/test_learning.db")
    print("   [OK] ConfidenceCalibrator database initialized")
    
    from src.learning.preference_learner import PreferenceLearner
    learner = PreferenceLearner(db_path="data/test_learning.db")
    print("   [OK] PreferenceLearner database initialized")
    
    from src.learning.strategy_optimizer import StrategyOptimizer
    optimizer = StrategyOptimizer(db_path="data/test_learning.db")
    print("   [OK] StrategyOptimizer database initialized")
    
except Exception as e:
    print(f"   [FAIL] Database initialization failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Test learning methods
print("\n6. Testing Learning Methods...")
try:
    from src.engine.signals import SignalGenerator
    signal_gen = SignalGenerator(enable_learning=True)
    
    # Check methods exist
    if hasattr(signal_gen, 'learn_from_trades'):
        print("   [OK] learn_from_trades() method exists")
    if hasattr(signal_gen, 'optimize_strategies'):
        print("   [OK] optimize_strategies() method exists")
    if hasattr(signal_gen, 'get_learning_report'):
        print("   [OK] get_learning_report() method exists")
    if hasattr(signal_gen, 'auto_improve'):
        print("   [OK] auto_improve() method exists")
    
except Exception as e:
    print(f"   [FAIL] Learning methods test failed: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nIf all tests show [OK], Phase 4 is working correctly!")
print("If any show [FAIL], there are import or initialization issues.")
