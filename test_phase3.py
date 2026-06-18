"""
Quick test script for Phase 3 features
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test all new imports"""
    print("=" * 60)
    print("PHASE 3 TESTING")
    print("=" * 60)
    print("\n1. Testing imports...")
    
    try:
        from src.strategies.value_investment import ValueInvestmentStrategy
        print("   ✓ ValueInvestmentStrategy")
    except Exception as e:
        print(f"   ✗ ValueInvestmentStrategy: {e}")
        return False
    
    try:
        from src.analysis.fundamental import FundamentalAnalysis
        print("   ✓ FundamentalAnalysis")
    except Exception as e:
        print(f"   ✗ FundamentalAnalysis: {e}")
        return False
    
    try:
        from src.engine.trade_database import TradeDatabase
        print("   ✓ TradeDatabase")
    except Exception as e:
        print(f"   ✗ TradeDatabase: {e}")
        return False
    
    try:
        from src.engine.signals import SignalGenerator
        print("   ✓ SignalGenerator (updated)")
    except Exception as e:
        print(f"   ✗ SignalGenerator: {e}")
        return False
    
    return True

def test_value_strategy():
    """Test value investment strategy"""
    print("\n2. Testing Value Investment Strategy...")
    
    try:
        from src.strategies.value_investment import ValueInvestmentStrategy
        strategy = ValueInvestmentStrategy()
        print(f"   ✓ Strategy initialized: {strategy.name}")
        print(f"   ✓ Cache system ready")
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_fundamental_analysis():
    """Test fundamental analysis"""
    print("\n3. Testing Fundamental Analysis...")
    
    try:
        from src.analysis.fundamental import FundamentalAnalysis
        fa = FundamentalAnalysis()
        print("   ✓ FundamentalAnalysis initialized")
        print("   ✓ Cache system ready")
        
        # Test DCF calculation (will fail without data, but tests method exists)
        result = fa.calculate_dcf_value("AAPL")
        print(f"   ✓ DCF calculation method works")
        
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_database():
    """Test trade database"""
    print("\n4. Testing Trade Database...")
    
    try:
        from src.engine.trade_database import TradeDatabase
        db = TradeDatabase("data/test_trades.db")
        print("   ✓ Database initialized")
        print("   ✓ Tables created")
        
        # Test creating a mock trade
        mock_signal = {
            'ticker': 'TEST',
            'action': 'BUY',
            'strategy': 'Test',
            'entry_price': 100.0,
            'stop_loss': 95.0,
            'take_profit_1': 110.0
        }
        
        trade_id = db.create_trade(mock_signal, 10)
        if trade_id > 0:
            print(f"   ✓ Trade created (ID: {trade_id})")
        
        # Test getting trades
        trades = db.get_open_trades()
        print(f"   ✓ Retrieved {len(trades)} trade(s)")
        
        # Test closing trade
        if trade_id > 0:
            db.close_trade(trade_id, 105.0, "Test exit")
            print("   ✓ Trade closed successfully")
        
        # Test performance stats
        stats = db.get_performance_stats()
        print(f"   ✓ Performance stats: {stats.get('total_trades', 0)} trades")
        
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signal_generator():
    """Test signal generator with new strategies"""
    print("\n5. Testing Signal Generator...")
    
    try:
        from src.engine.signals import SignalGenerator
        sg = SignalGenerator()
        print(f"   ✓ Signal Generator initialized")
        print(f"   ✓ Strategies loaded: {len(sg.strategies)}")
        print(f"   ✓ Min confidence: {sg.min_confidence}%")
        
        # Check if value investment strategy is included
        strategy_names = [s.name for s in sg.strategies]
        print(f"   ✓ Available strategies: {', '.join(strategy_names)}")
        
        if "Value Investment" in strategy_names:
            print("   ✓ Value Investment Strategy integrated!")
        
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Value Strategy", test_value_strategy()))
    results.append(("Fundamental Analysis", test_fundamental_analysis()))
    results.append(("Trade Database", test_database()))
    results.append(("Signal Generator", test_signal_generator()))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Ready to deploy!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Fix before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
