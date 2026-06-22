"""
Enhanced Signal Formatter for Phase 4
Provides detailed timeframes, exit strategies, and interactive buttons
"""
from typing import Dict, List
from datetime import datetime, timedelta
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class SignalFormatter:
    """
    Format trading signals with enhanced details
    
    Features:
    - Precise timeframe guidance
    - Multiple take profit levels with expected timing
    - Exit strategy details
    - Review dates and reminders
    - Interactive buttons for user feedback
    """
    
    def __init__(self):
        """Initialize formatter"""
        self.timeframe_details = {
            'day': {
                'name': 'Day Trade',
                'hold_range': '1-3 days',
                'hold_days': 2,
                'review_days': 1,
                'max_days': 3,
                'tp1_days': 1,
                'tp2_days': 2,
                'tp3_days': 3
            },
            'swing': {
                'name': 'Swing Trade',
                'hold_range': '3-7 days',
                'hold_days': 5,
                'review_days': 3,
                'max_days': 8,
                'tp1_days': 2,
                'tp2_days': 4,
                'tp3_days': 6
            },
            'position': {
                'name': 'Position Trade',
                'hold_range': '2-4 weeks',
                'hold_days': 21,
                'review_days': 14,
                'max_days': 30,
                'tp1_days': 10,
                'tp2_days': 18,
                'tp3_days': 25
            },
            'long': {
                'name': 'Long-term Investment',
                'hold_range': '1-6 months',
                'hold_days': 90,
                'review_days': 60,
                'max_days': 180,
                'tp1_days': 45,
                'tp2_days': 90,
                'tp3_days': 150
            }
        }
    
    def format_signal(self, signal: Dict, signal_id: int = None) -> str:
        """
        Format a trading signal with enhanced details
        
        Args:
            signal: Signal dictionary
            signal_id: Optional signal ID for tracking
            
        Returns:
            Formatted message string
        """
        ticker = signal['ticker']
        action = signal['action']
        strategy = signal.get('strategy', 'Unknown')
        confidence = signal.get('confidence', 0)
        entry_price = signal.get('entry_price', 0)
        stop_loss = signal.get('stop_loss', 0)
        
        # Get take profit levels
        tp1 = signal.get('take_profit_1', 0)
        tp2 = signal.get('take_profit_2', 0)
        tp3 = signal.get('take_profit_3', 0)
        
        # Determine timeframe
        timeframe = self._determine_timeframe(strategy)
        tf_details = self.timeframe_details[timeframe]
        
        # Calculate percentages
        sl_percent = abs((stop_loss - entry_price) / entry_price * 100) if stop_loss else 0
        tp1_percent = abs((tp1 - entry_price) / entry_price * 100) if tp1 else 0
        tp2_percent = abs((tp2 - entry_price) / entry_price * 100) if tp2 else 0
        tp3_percent = abs((tp3 - entry_price) / entry_price * 100) if tp3 else 0
        
        # Calculate risk/reward
        risk_reward = tp1_percent / sl_percent if sl_percent > 0 else 0
        
        # Calculate dates
        now = datetime.now()
        entry_window = now + timedelta(hours=24)
        review_date = now + timedelta(days=tf_details['review_days'])
        max_hold_date = now + timedelta(days=tf_details['max_days'])
        exit_by_date = now + timedelta(days=tf_details['max_days'] + 1)
        
        # Build message with clear action header
        message = f"""
🚀 <b>TRADING SIGNAL #{signal_id if signal_id else 'NEW'}</b>

⚡ <b>CFD TRADE - BUY NOW!</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 <b>{action} {ticker}</b>
💰 <b>Entry Price:</b> ${entry_price:.2f}
🛑 <b>Stop Loss:</b> ${stop_loss:.2f} (-{sl_percent:.1f}%)

✅ <b>Take Profit Targets:</b>
"""
        
        if tp1:
            message += f"• <b>TP1:</b> ${tp1:.2f} (+{tp1_percent:.1f}%) - Expected: {tf_details['tp1_days']} days\n"
        if tp2:
            message += f"• <b>TP2:</b> ${tp2:.2f} (+{tp2_percent:.1f}%) - Expected: {tf_details['tp2_days']} days\n"
        if tp3:
            message += f"• <b>TP3:</b> ${tp3:.2f} (+{tp3_percent:.1f}%) - Expected: {tf_details['tp3_days']} days\n"
        
        message += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ <b>WHEN TO BUY:</b>
🔴 <b>IMMEDIATELY</b> - Enter within next 24 hours
⏱️ Deadline: {entry_window.strftime('%b %d at %H:%M UK')}

⏰ <b>WHEN TO SELL:</b>
• <b>TP1 Target:</b> {review_date.strftime('%b %d')} (Day {tf_details['tp1_days']})
• <b>TP2 Target:</b> Around Day {tf_details['tp2_days']}
• <b>TP3 Target:</b> Around Day {tf_details['tp3_days']}
• <b>Max Hold:</b> {max_hold_date.strftime('%b %d')} - EXIT if no TP hit

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>TRADE INFO:</b>
• <b>Confidence:</b> {confidence}%
• <b>Risk/Reward:</b> {risk_reward:.1f}:1
• <b>Strategy:</b> {strategy} ({tf_details['name']})
• <b>Hold Period:</b> {tf_details['hold_range']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 <b>EXIT STRATEGY:</b>
"""
        
        # Add exit strategy based on timeframe
        exit_strategy = self._get_exit_strategy(timeframe, tf_details)
        message += exit_strategy
        
        # Add reasoning if available
        if signal.get('reasoning'):
            reasoning = signal['reasoning']
            if isinstance(reasoning, list):
                message += "\n📋 <b>REASONING:</b>\n"
                for reason in reasoning[:3]:  # Limit to 3 reasons
                    message += f"• {reason}\n"
        
        message += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 <b>AUTOMATIC REMINDERS:</b>
✅ Day {tf_details['review_days']}: Check progress and adjust stops
✅ Day {tf_details['max_days']}: Consider trailing stop
✅ Day {tf_details['max_days'] + 1}: EXIT if still open

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 <b>QUICK ACTION CHECKLIST:</b>
☐ Open Trading 212 CFD account
☐ Search for {ticker}
☐ Set BUY order at ${entry_price:.2f}
☐ Set STOP LOSS at ${stop_loss:.2f}
☐ Set TAKE PROFIT at ${tp1:.2f}
☐ Place order NOW (within 24 hours)
☐ Click ✅ below when done

<i>Did you take this trade?</i>
"""
        
        return message
    
    def _determine_timeframe(self, strategy: str) -> str:
        """Determine timeframe based on strategy"""
        strategy_lower = strategy.lower()
        
        if 'value' in strategy_lower or 'investment' in strategy_lower:
            return 'long'
        elif 'position' in strategy_lower:
            return 'position'
        elif 'swing' in strategy_lower or 'trend' in strategy_lower:
            return 'swing'
        elif 'day' in strategy_lower or 'scalp' in strategy_lower:
            return 'day'
        else:
            return 'swing'  # Default
    
    def _get_exit_strategy(self, timeframe: str, tf_details: Dict) -> str:
        """Get exit strategy text based on timeframe"""
        if timeframe == 'day':
            return """1. If TP1 hit same day → Take 50% profit, move SL to breakeven
2. If TP2 hit next day → Take 30% profit, trail SL
3. Let 20% run to TP3 or trailing stop
4. Exit all positions by end of day {max_days}
""".format(max_days=tf_details['max_days'])
        
        elif timeframe == 'swing':
            return """1. If TP1 hit in 2-3 days → Take 50% profit, move SL to breakeven
2. If TP2 hit in 4-5 days → Take 30% profit, trail SL
3. Let 20% run to TP3 or trailing stop
4. If no TP hit by day {max_days} → Exit at market
""".format(max_days=tf_details['max_days'])
        
        elif timeframe == 'position':
            return """1. If TP1 hit in 1-2 weeks → Take 40% profit, move SL to breakeven
2. If TP2 hit in 2-3 weeks → Take 30% profit, trail SL
3. Let 30% run to TP3 or trailing stop
4. Review weekly and adjust stops as needed
5. Exit if no progress after {max_days} days
""".format(max_days=tf_details['max_days'])
        
        else:  # long-term
            return """1. If TP1 hit in 1-2 months → Take 30% profit, hold rest
2. If TP2 hit in 3-4 months → Take 30% profit, trail SL
3. Let 40% run to TP3 or long-term trailing stop
4. Review monthly and adjust based on fundamentals
5. Hold for full timeframe unless fundamentals change
"""
    
    def format_reminder(self, trade: Dict, reminder_type: str, current_price: float = None) -> str:
        """
        Format a trade reminder message
        
        Args:
            trade: Trade dictionary
            reminder_type: Type of reminder
            current_price: Current stock price
            
        Returns:
            Formatted reminder message
        """
        ticker = trade['ticker']
        entry_price = trade['entry_price']
        action = trade['action']
        days_held = trade.get('hold_days', 0)
        
        # Calculate current P&L if price provided
        pnl_text = ""
        if current_price:
            if action == 'BUY':
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
            else:
                pnl_percent = ((entry_price - current_price) / entry_price) * 100
            
            pnl_emoji = "📈" if pnl_percent > 0 else "📉"
            pnl_text = f"\n\n{pnl_emoji} <b>Current P&L:</b> {pnl_percent:+.2f}%"
        
        if reminder_type == 'review':
            tp1 = trade.get('take_profit_1', 0)
            message = f"""
🔔 <b>TRADE REMINDER - {ticker}</b>

Day {days_held} - Time to review your trade!

<b>Entry:</b> ${entry_price:.2f}
<b>Current:</b> ${current_price:.2f} if current_price else 'Check price'
<b>TP1 Target:</b> ${tp1:.2f}
{pnl_text}

<b>Action:</b> Check if TP1 hit. If yes, take 50% profit and move stop to breakeven.
"""
        
        elif reminder_type == 'max_hold':
            message = f"""
⚠️ <b>TRADE ALERT - {ticker}</b>

Day {days_held} - Maximum hold period approaching!

<b>Entry:</b> ${entry_price:.2f}
<b>Current:</b> ${current_price:.2f} if current_price else 'Check price'
{pnl_text}

<b>Action:</b> Consider using a trailing stop or taking profits. Review your exit strategy.
"""
        
        elif reminder_type == 'exit_warning':
            message = f"""
🚨 <b>EXIT REMINDER - {ticker}</b>

Day {days_held} - Time to exit if no targets hit!

<b>Entry:</b> ${entry_price:.2f}
<b>Current:</b> ${current_price:.2f} if current_price else 'Check price'
{pnl_text}

<b>Action:</b> Exit at market if no take profit levels have been hit. Don't let winners turn into losers!
"""
        
        else:
            message = f"🔔 Trade reminder for {ticker}"
        
        return message
    
    def format_trade_status(self, trade: Dict, current_price: float = None) -> str:
        """
        Format trade status message
        
        Args:
            trade: Trade dictionary
            current_price: Current stock price
            
        Returns:
            Formatted status message
        """
        ticker = trade['ticker']
        action = trade['action']
        entry_price = trade['entry_price']
        entry_date = datetime.fromisoformat(trade['entry_date'])
        stop_loss = trade.get('stop_loss', 0)
        tp1 = trade.get('take_profit_1', 0)
        tp2 = trade.get('take_profit_2', 0)
        tp3 = trade.get('take_profit_3', 0)
        days_held = (datetime.now() - entry_date).days
        
        # Calculate P&L
        if current_price:
            if action == 'BUY':
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
            else:
                pnl_percent = ((entry_price - current_price) / entry_price) * 100
            
            pnl_emoji = "📈" if pnl_percent > 0 else "📉"
            status_emoji = "✅" if pnl_percent > 0 else "⚠️"
        else:
            pnl_percent = 0
            pnl_emoji = "📊"
            status_emoji = "📊"
        
        message = f"""
{status_emoji} <b>TRADE STATUS - {ticker}</b>

<b>Action:</b> {action}
<b>Entry:</b> ${entry_price:.2f} ({entry_date.strftime('%b %d, %Y')})
<b>Current:</b> ${current_price:.2f} if current_price else 'N/A'
<b>Days Held:</b> {days_held}

{pnl_emoji} <b>P&L:</b> {pnl_percent:+.2f}%

<b>Targets:</b>
• Stop Loss: ${stop_loss:.2f}
• TP1: ${tp1:.2f}
• TP2: ${tp2:.2f}
• TP3: ${tp3:.2f}

<b>Strategy:</b> {trade.get('strategy', 'Unknown')}
<b>Confidence:</b> {trade.get('confidence', 0)}%
"""
        
        return message
    
    def format_performance_summary(self, stats: Dict) -> str:
        """
        Format performance summary
        
        Args:
            stats: Performance statistics dictionary
            
        Returns:
            Formatted summary message
        """
        message = f"""
📊 <b>PERFORMANCE SUMMARY</b>

💰 <b>TRADING STATS:</b>
• Total Trades: {stats.get('total_trades', 0)}
• Open Trades: {stats.get('open_trades', 0)}
• Win Rate: {stats.get('win_rate', 0):.1f}%

📈 <b>RESULTS:</b>
• Winning Trades: {stats.get('winning_trades', 0)}
• Losing Trades: {stats.get('losing_trades', 0)}
• Total P&L: {stats.get('total_pnl', 0):+.2f}%

💡 <b>AVERAGES:</b>
• Avg Profit: +{stats.get('avg_profit', 0):.2f}%
• Avg Loss: {stats.get('avg_loss', 0):.2f}%
• Profit Factor: {stats.get('profit_factor', 0):.2f}
"""
        
        return message
    
    def format_strategy_breakdown(self, strategies: List[Dict]) -> str:
        """
        Format strategy performance breakdown
        
        Args:
            strategies: List of strategy performance dictionaries
            
        Returns:
            Formatted breakdown message
        """
        if not strategies:
            return "No strategy data available yet."
        
        message = "📊 <b>STRATEGY BREAKDOWN:</b>\n\n"
        
        for strat in strategies:
            message += f"""<b>{strat['strategy']}</b>
• Trades: {strat['total_trades']}
• Win Rate: {strat['win_rate']:.1f}%
• Avg P&L: {strat['avg_pnl']:+.2f}%
• Total P&L: {strat['total_pnl']:+.2f}%

"""
        
        return message
    
    def get_feedback_buttons(self, signal_id: int) -> List[List[Dict]]:
        """
        Get inline keyboard buttons for user feedback
        
        Args:
            signal_id: Signal ID
            
        Returns:
            Button layout for telegram inline keyboard
        """
        return [
            [
                {"text": "✅ I'm Taking This Trade", "callback_data": f"trade_taken_{signal_id}"},
                {"text": "❌ Skip This Trade", "callback_data": f"trade_skip_{signal_id}"}
            ]
        ]
    
    def get_trade_outcome_buttons(self, trade_id: int) -> List[List[Dict]]:
        """
        Get buttons for reporting trade outcome
        
        Args:
            trade_id: Trade ID
            
        Returns:
            Button layout for outcome reporting
        """
        return [
            [
                {"text": "🎯 Hit TP1", "callback_data": f"outcome_tp1_{trade_id}"},
                {"text": "🎯 Hit TP2", "callback_data": f"outcome_tp2_{trade_id}"},
                {"text": "🎯 Hit TP3", "callback_data": f"outcome_tp3_{trade_id}"}
            ],
            [
                {"text": "🛑 Hit Stop Loss", "callback_data": f"outcome_sl_{trade_id}"},
                {"text": "⏰ Time Exit", "callback_data": f"outcome_time_{trade_id}"},
                {"text": "📝 Manual Exit", "callback_data": f"outcome_manual_{trade_id}"}
            ]
        ]
