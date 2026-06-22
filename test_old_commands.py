"""
Test script to verify all old Telegram bot commands still work
Tests: /status, /help, /start, /portfolio, /performance, /trades, /research, /watchlist
"""
import asyncio
import sys
import os
from datetime import datetime
from src.notifications.telegram_bot import create_bot
from src.utils.config import get_config
from src.utils.logger import setup_logger

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logger = setup_logger(__name__)


async def test_bot_initialization():
    """Test that bot initializes correctly"""
    print("\n" + "="*60)
    print("TEST 1: Bot Initialization")
    print("="*60)
    
    try:
        config = get_config()
        telegram_config = config.get_telegram_config()
        
        if not telegram_config.get('bot_token') or not telegram_config.get('chat_id'):
            print("❌ FAILED: Telegram credentials not configured")
            return False
        
        bot = create_bot()
        await bot.initialize()
        
        print("✅ PASSED: Bot initialized successfully")
        print(f"   - Bot token: {'*' * 20}{telegram_config.get('bot_token')[-10:]}")
        print(f"   - Chat ID: {telegram_config.get('chat_id')}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_send_message():
    """Test basic message sending"""
    print("\n" + "="*60)
    print("TEST 2: Send Basic Message")
    print("="*60)
    
    try:
        bot = create_bot()
        await bot.initialize()
        
        test_message = f"""
🧪 **COMMAND TEST STARTED**
Time: {datetime.now().strftime('%H:%M:%S')}

Testing all old commands to ensure backward compatibility...
"""
        
        success = await bot.send_message(test_message, parse_mode="Markdown")
        
        if success:
            print("✅ PASSED: Message sent successfully")
            return True
        else:
            print("❌ FAILED: Message sending failed")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_status_command():
    """Test /status command functionality"""
    print("\n" + "="*60)
    print("TEST 3: /status Command")
    print("="*60)
    
    try:
        bot = create_bot()
        await bot.initialize()
        
        # Simulate status command
        from telegram import Update
        from unittest.mock import MagicMock, AsyncMock
        
        # Create mock update
        update = MagicMock(spec=Update)
        update.message = MagicMock()
        update.message.reply_text = AsyncMock()
        
        # Create mock context
        context = MagicMock()
        
        # Call the command
        await bot.cmd_status(update, context)
        
        # Check if reply was called
        if update.message.reply_text.called:
            call_args = update.message.reply_text.call_args
            message = call_args[0][0] if call_args[0] else ""
            
            # Verify message contains expected content
            if "STOCKPILOT STATUS" in message and "Running" in message:
                print("✅ PASSED: /status command works")
                print(f"   - Message preview: {message[:100]}...")
                return True
            else:
                print("❌ FAILED: /status message format incorrect")
                return False
        else:
            print("❌ FAILED: /status did not send reply")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_help_command():
    """Test /help command functionality"""
    print("\n" + "="*60)
    print("TEST 4: /help Command")
    print("="*60)
    
    try:
        bot = create_bot()
        await bot.initialize()
        
        from telegram import Update
        from unittest.mock import MagicMock, AsyncMock
        
        update = MagicMock(spec=Update)
        update.message = MagicMock()
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        
        await bot.cmd_help(update, context)
        
        if update.message.reply_text.called:
            call_args = update.message.reply_text.call_args
            message = call_args[0][0] if call_args[0] else ""
            
            # Check for key commands in help text
            required_commands = ['/start', '/status', '/help', '/portfolio', '/trades', '/research']
            missing_commands = [cmd for cmd in required_commands if cmd not in message]
            
            if not missing_commands:
                print("✅ PASSED: /help command works")
                print(f"   - All {len(required_commands)} core commands documented")
                return True
            else:
                print(f"❌ FAILED: Missing commands in help: {missing_commands}")
                return False
        else:
            print("❌ FAILED: /help did not send reply")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_start_command():
    """Test /start command functionality"""
    print("\n" + "="*60)
    print("TEST 5: /start Command")
    print("="*60)
    
    try:
        bot = create_bot()
        await bot.initialize()
        
        from telegram import Update
        from unittest.mock import MagicMock, AsyncMock
        
        update = MagicMock(spec=Update)
        update.message = MagicMock()
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        
        await bot.cmd_start(update, context)
        
        if update.message.reply_text.called:
            call_args = update.message.reply_text.call_args
            message = call_args[0][0] if call_args[0] else ""
            
            if "StockPilot" in message and "Started" in message:
                print("✅ PASSED: /start command works")
                return True
            else:
                print("❌ FAILED: /start message format incorrect")
                return False
        else:
            print("❌ FAILED: /start did not send reply")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_portfolio_command():
    """Test /portfolio command functionality"""
    print("\n" + "="*60)
    print("TEST 6: /portfolio Command")
    print("="*60)
    
    try:
        bot = create_bot()
        await bot.initialize()
        
        from telegram import Update
        from unittest.mock import MagicMock, AsyncMock
        
        update = MagicMock(spec=Update)
        update.message = MagicMock()
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        
        await bot.cmd_portfolio(update, context)
        
        if update.message.reply_text.called:
            call_args = update.message.reply_text.call_args
            message = call_args[0][0] if call_args[0] else ""
            
            # Check for key portfolio elements
            if "PORTFOLIO" in message and ("Open Trades" in message or "Total Value" in message):
                print("✅ PASSED: /portfolio command works")
                print("   - Shows portfolio summary with trades and performance")
                return True
            else:
                print("❌ FAILED: /portfolio message format incorrect")
                return False
        else:
            print("❌ FAILED: /portfolio did not send reply")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_performance_command():
    """Test /performance command functionality"""
    print("\n" + "="*60)
    print("TEST 7: /performance Command")
    print("="*60)
    
    try:
        bot = create_bot()
        await bot.initialize()
        
        from telegram import Update
        from unittest.mock import MagicMock, AsyncMock
        
        update = MagicMock(spec=Update)
        update.message = MagicMock()
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        
        await bot.cmd_performance(update, context)
        
        if update.message.reply_text.called:
            call_args = update.message.reply_text.call_args
            message = call_args[0][0] if call_args[0] else ""
            
            # Check for key performance metrics
            if "PERFORMANCE" in message and "Win Rate" in message:
                print("✅ PASSED: /performance command works")
                print("   - Shows trading statistics and P&L")
                return True
            else:
                print("❌ FAILED: /performance message format incorrect")
                return False
        else:
            print("❌ FAILED: /performance did not send reply")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_trades_command():
    """Test /trades command functionality"""
    print("\n" + "="*60)
    print("TEST 8: /trades Command")
    print("="*60)
    
    try:
        bot = create_bot()
        await bot.initialize()
        
        from telegram import Update
        from unittest.mock import MagicMock, AsyncMock
        
        update = MagicMock(spec=Update)
        update.message = MagicMock()
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        
        await bot.cmd_trades(update, context)
        
        if update.message.reply_text.called:
            call_args = update.message.reply_text.call_args
            message = call_args[0][0] if call_args[0] else ""
            
            # Should show either open trades or "no open trades"
            if "OPEN TRADES" in message or "Open Trades" in message:
                print("✅ PASSED: /trades command works")
                print("   - Shows list of open trades")
                return True
            else:
                print("❌ FAILED: /trades message format incorrect")
                return False
        else:
            print("❌ FAILED: /trades did not send reply")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_watchlist_command():
    """Test /watchlist command functionality"""
    print("\n" + "="*60)
    print("TEST 9: /watchlist Command")
    print("="*60)
    
    try:
        bot = create_bot()
        await bot.initialize()
        
        from telegram import Update
        from unittest.mock import MagicMock, AsyncMock
        
        update = MagicMock(spec=Update)
        update.message = MagicMock()
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        
        await bot.cmd_watchlist(update, context)
        
        if update.message.reply_text.called:
            call_args = update.message.reply_text.call_args
            message = call_args[0][0] if call_args[0] else ""
            
            # Should show watchlist or empty message
            if "Watchlist" in message or "WATCHLIST" in message:
                print("✅ PASSED: /watchlist command works")
                print("   - Shows user's watchlist")
                return True
            else:
                print("❌ FAILED: /watchlist message format incorrect")
                return False
        else:
            print("❌ FAILED: /watchlist did not send reply")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_research_command():
    """Test /research command functionality"""
    print("\n" + "="*60)
    print("TEST 10: /research Command (without ticker)")
    print("="*60)
    
    try:
        bot = create_bot()
        await bot.initialize()
        
        from telegram import Update
        from unittest.mock import MagicMock, AsyncMock
        
        update = MagicMock(spec=Update)
        update.message = MagicMock()
        update.message.reply_text = AsyncMock()
        
        context = MagicMock()
        context.args = []  # No ticker provided
        
        await bot.cmd_research(update, context)
        
        if update.message.reply_text.called:
            call_args = update.message.reply_text.call_args
            message = call_args[0][0] if call_args[0] else ""
            
            # Should show usage instructions
            if "research" in message.lower() and ("usage" in message.lower() or "ticker" in message.lower()):
                print("✅ PASSED: /research command works")
                print("   - Shows usage instructions when no ticker provided")
                return True
            else:
                print("❌ FAILED: /research message format incorrect")
                return False
        else:
            print("❌ FAILED: /research did not send reply")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def send_test_summary(results):
    """Send test summary to Telegram"""
    print("\n" + "="*60)
    print("Sending Test Summary to Telegram")
    print("="*60)
    
    try:
        bot = create_bot()
        await bot.initialize()
        
        passed = sum(results.values())
        total = len(results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        status_emoji = "✅" if passed == total else "⚠️" if passed >= total * 0.7 else "❌"
        
        summary = f"""
{status_emoji} **OLD COMMANDS TEST RESULTS**

**Summary:** {passed}/{total} tests passed ({success_rate:.0f}%)

**Test Results:**
"""
        
        for test_name, passed_test in results.items():
            emoji = "✅" if passed_test else "❌"
            summary += f"{emoji} {test_name}\n"
        
        summary += f"""
**Status:** {'All commands working!' if passed == total else 'Some commands need attention'}

**Tested Commands:**
• /start - Bot initialization
• /status - System status
• /help - Command list
• /portfolio - Portfolio summary
• /performance - Trading stats
• /trades - Open positions
• /watchlist - User watchlist
• /research - Stock analysis

**Backward Compatibility:** {'✅ CONFIRMED' if passed == total else '⚠️ ISSUES FOUND'}

Test completed at {datetime.now().strftime('%H:%M:%S')}
"""
        
        await bot.send_message(summary, parse_mode="Markdown")
        print("✅ Test summary sent to Telegram")
        
    except Exception as e:
        print(f"❌ Failed to send summary: {e}")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("STOCKPILOT - OLD COMMANDS TEST SUITE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = {}
    
    # Run all tests
    results["Bot Initialization"] = await test_bot_initialization()
    results["Send Message"] = await test_send_message()
    results["/status"] = await test_status_command()
    results["/help"] = await test_help_command()
    results["/start"] = await test_start_command()
    results["/portfolio"] = await test_portfolio_command()
    results["/performance"] = await test_performance_command()
    results["/trades"] = await test_trades_command()
    results["/watchlist"] = await test_watchlist_command()
    results["/research"] = await test_research_command()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("="*60)
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("="*60)
    
    # Send summary to Telegram
    await send_test_summary(results)
    
    # Return exit code
    return 0 if passed == total else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
