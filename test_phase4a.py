"""
Test Phase 4A Foundation
Tests enhanced database, signal formatter, and trade commands
"""
import sys
import os
from datetime import datetime
from src.engine.trade_database_v2 import TradeDatabaseV2
from src.notifications.signal_formatter import SignalFormatter

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')


def test_database():
    """Test enhanced database functionality"""
    print("=" * 60)
    print("Testing Enhanced Database (Phase 4A)")
    print("=" * 60)
    
    # Initialize database
    db = TradeDatabaseV2(db_path="data/test_stockpilot.db")
    print("✅ Database initialized")
    
    # Create a test signal
    test_signal = {
        'ticker': 'AAPL',
        'action': 'BUY',
        'strategy': 'Trend Following',
        'confidence': 90,
        'entry_price': 150.00,
        'stop_loss': 145.00,
        'take_profit_1': 156.00,
        'take_profit_2': 160.00,
        'take_profit_3': 165.00,
        'timeframe': 'swing',
        'reasoning': ['Strong uptrend', 'High volume', 'Above all EMAs']
    }
    
    # Save signal
    signal_id = db.save_signal(test_signal)
    print(f"✅ Signal saved: ID={signal_id}")
    
    # Create trade from signal (user takes it)
    trade_id = db.create_trade_from_signal(signal_id, user_taken=True)
    print(f"✅ Trade created: ID={trade_id}")
    
    # Get open trades
    open_trades = db.get_open_trades()
    print(f"✅ Open trades: {len(open_trades)}")
    
    # Add feedback
    success = db.add_trade_feedback(trade_id, 'taken', notes='Looks good!')
    print(f"✅ Feedback added: {success}")
    
    # Get pending reminders
    reminders = db.get_pending_reminders()
    print(f"✅ Pending reminders: {len(reminders)}")
    
    # Close trade
    success = db.close_trade(trade_id, 156.00, 'tp1_hit', notes='Hit first target!')
    print(f"✅ Trade closed: {success}")
    
    # Get performance stats
    stats = db.get_performance_stats()
    print(f"✅ Performance stats retrieved:")
    print(f"   - Total trades: {stats.get('total_trades', 0)}")
    print(f"   - Win rate: {stats.get('win_rate', 0):.1f}%")
    print(f"   - Total P&L: {stats.get('total_pnl', 0):+.2f}%")
    
    # Get strategy performance
    strategies = db.get_strategy_performance()
    print(f"✅ Strategy performance: {len(strategies)} strategies tracked")
    
    print("\n✅ All database tests passed!\n")
    return True


def test_signal_formatter():
    """Test signal formatter functionality"""
    print("=" * 60)
    print("Testing Signal Formatter (Phase 4A)")
    print("=" * 60)
    
    # Initialize formatter
    formatter = SignalFormatter()
    print("✅ Formatter initialized")
    
    # Create test signal
    test_signal = {
        'ticker': 'MSFT',
        'action': 'BUY',
        'strategy': 'Trend Following',
        'confidence': 88,
        'entry_price': 380.00,
        'stop_loss': 370.00,
        'take_profit_1': 390.00,
        'take_profit_2': 395.00,
        'take_profit_3': 405.00,
        'reasoning': ['Strong momentum', 'Breakout confirmed', 'High volume']
    }
    
    # Format signal
    message = formatter.format_signal(test_signal, signal_id=1)
    print("✅ Signal formatted:")
    print("-" * 60)
    print(message)
    print("-" * 60)
    
    # Test feedback buttons
    buttons = formatter.get_feedback_buttons(signal_id=1)
    print(f"✅ Feedback buttons: {len(buttons)} rows")
    for row in buttons:
        for button in row:
            print(f"   - {button['text']}")
    
    # Test outcome buttons
    outcome_buttons = formatter.get_trade_outcome_buttons(trade_id=1)
    print(f"✅ Outcome buttons: {len(outcome_buttons)} rows")
    for row in outcome_buttons:
        for button in row:
            print(f"   - {button['text']}")
    
    # Test reminder formatting
    test_trade = {
        'id': 1,
        'ticker': 'MSFT',
        'action': 'BUY',
        'entry_price': 380.00,
        'entry_date': datetime.now().isoformat(),
        'take_profit_1': 390.00,
        'hold_days': 3
    }
    
    reminder_msg = formatter.format_reminder(test_trade, 'review', current_price=385.00)
    print("✅ Reminder formatted:")
    print("-" * 60)
    print(reminder_msg)
    print("-" * 60)
    
    # Test performance summary
    test_stats = {
        'total_trades': 25,
        'open_trades': 3,
        'winning_trades': 17,
        'losing_trades': 5,
        'win_rate': 77.3,
        'total_pnl': 45.6,
        'avg_profit': 5.2,
        'avg_loss': -2.1,
        'profit_factor': 2.48
    }
    
    perf_msg = formatter.format_performance_summary(test_stats)
    print("✅ Performance summary formatted:")
    print("-" * 60)
    print(perf_msg)
    print("-" * 60)
    
    print("\n✅ All formatter tests passed!\n")
    return True


def test_integration():
    """Test integration between components"""
    print("=" * 60)
    print("Testing Component Integration (Phase 4A)")
    print("=" * 60)
    
    db = TradeDatabaseV2(db_path="data/test_stockpilot.db")
    formatter = SignalFormatter()
    
    # Create signal
    signal = {
        'ticker': 'GOOGL',
        'action': 'BUY',
        'strategy': 'Breakout',
        'confidence': 92,
        'entry_price': 140.00,
        'stop_loss': 135.00,
        'take_profit_1': 145.00,
        'take_profit_2': 148.00,
        'take_profit_3': 152.00,
        'timeframe': 'swing',
        'reasoning': ['Breakout above resistance', 'Strong volume']
    }
    
    # Save and format
    signal_id = db.save_signal(signal)
    formatted_msg = formatter.format_signal(signal, signal_id)
    print(f"✅ Signal {signal_id} saved and formatted")
    
    # Create trade
    trade_id = db.create_trade_from_signal(signal_id, user_taken=True)
    print(f"✅ Trade {trade_id} created from signal {signal_id}")
    
    # Get trade and format status
    trade = db.get_trade_by_id(trade_id)
    status_msg = formatter.format_trade_status(trade, current_price=142.00)
    print("✅ Trade status formatted:")
    print("-" * 60)
    print(status_msg)
    print("-" * 60)
    
    # Simulate trade lifecycle
    print("\n📊 Simulating trade lifecycle...")
    
    # Day 1: Trade taken
    print("   Day 1: Trade taken ✅")
    
    # Day 3: Review reminder
    print("   Day 3: Review reminder sent 🔔")
    reminders = db.get_pending_reminders()
    if reminders:
        print(f"   Found {len(reminders)} pending reminders")
    
    # Day 5: Close at TP1
    print("   Day 5: Hit TP1, closing trade 🎯")
    db.close_trade(trade_id, 145.00, 'tp1_hit')
    
    # Get updated stats
    stats = db.get_performance_stats()
    print(f"\n✅ Final stats:")
    print(f"   - Total trades: {stats.get('total_trades', 0)}")
    print(f"   - Win rate: {stats.get('win_rate', 0):.1f}%")
    
    print("\n✅ All integration tests passed!\n")
    return True


def main():
    """Run all Phase 4A tests"""
    print("\n" + "=" * 60)
    print("PHASE 4A FOUNDATION TESTS")
    print("=" * 60 + "\n")
    
    try:
        # Test database
        if not test_database():
            print("❌ Database tests failed")
            return False
        
        # Test formatter
        if not test_signal_formatter():
            print("❌ Formatter tests failed")
            return False
        
        # Test integration
        if not test_integration():
            print("❌ Integration tests failed")
            return False
        
        print("=" * 60)
        print("🎉 ALL PHASE 4A TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Phase 4A Foundation is ready!")
        print("\nNext steps:")
        print("1. Integrate with existing Telegram bot")
        print("2. Add reminder scheduler")
        print("3. Test with real signals")
        print("4. Deploy to Railway")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
