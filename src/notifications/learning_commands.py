"""
Learning Commands - Telegram commands for Phase 4 learning features
"""
from telegram import Update
from telegram.ext import ContextTypes
from typing import Dict
from ..learning.performance_tracker import PerformanceTracker
from ..learning.confidence_calibrator import ConfidenceCalibrator
from ..learning.preference_learner import PreferenceLearner
from ..learning.strategy_optimizer import StrategyOptimizer
from ..backtesting.backtest_engine import BacktestEngine
from ..backtesting.backtest_report import BacktestReport
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class LearningCommands:
    """Telegram commands for learning and optimization features"""
    
    def __init__(self):
        """Initialize learning commands"""
        self.performance_tracker = PerformanceTracker()
        self.confidence_calibrator = ConfidenceCalibrator()
        self.preference_learner = PreferenceLearner()
        self.strategy_optimizer = StrategyOptimizer()
        self.backtest_report = BacktestReport()
    
    async def cmd_learn(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /learn command - trigger learning process"""
        await update.message.reply_text("🧠 Starting learning process...\nThis may take a moment.")
        
        try:
            # Import signal generator
            from ..engine.signals import SignalGenerator
            signal_gen = SignalGenerator()
            
            # Run learning
            signal_gen.learn_from_trades(min_trades=10)
            
            await update.message.reply_text(
                "✅ <b>Learning Complete!</b>\n\n"
                "The bot has analyzed your trading history and updated:\n"
                "• Confidence calibration\n"
                "• Strategy performance\n"
                "• User preferences\n\n"
                "Use /learning_report to see insights.",
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error in learn command: {e}")
            await update.message.reply_text(f"❌ Error during learning: {str(e)}")
    
    async def cmd_optimize(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /optimize command - optimize strategies"""
        await update.message.reply_text("⚙️ Starting strategy optimization...\nThis may take several minutes.")
        
        try:
            from ..engine.signals import SignalGenerator
            signal_gen = SignalGenerator()
            
            # Run optimization
            signal_gen.optimize_strategies(min_trades=20)
            
            await update.message.reply_text(
                "✅ <b>Optimization Complete!</b>\n\n"
                "Strategies have been optimized for maximum performance.\n"
                "Use /learning_report to see optimal parameters.",
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error in optimize command: {e}")
            await update.message.reply_text(f"❌ Error during optimization: {str(e)}")
    
    async def cmd_learning_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /learning_report command - show learning insights"""
        try:
            from ..engine.signals import SignalGenerator
            signal_gen = SignalGenerator()
            
            report = signal_gen.get_learning_report()
            
            if 'error' in report:
                await update.message.reply_text(f"❌ {report['error']}")
                return
            
            # Format report
            message = "🧠 <b>LEARNING REPORT</b>\n\n"
            
            # Performance summary
            perf = report.get('performance', {})
            message += "📊 <b>PERFORMANCE</b>\n"
            message += f"• Win Rate: {perf.get('win_rate', 0):.1f}%\n"
            message += f"• Sharpe Ratio: {perf.get('sharpe_ratio', 0):.2f}\n"
            message += f"• Profit Factor: {perf.get('profit_factor', 0):.2f}\n"
            message += f"• Max Drawdown: {perf.get('max_drawdown', 0):.2f}%\n\n"
            
            # Preferences
            prefs = report.get('preferences', {})
            if prefs.get('confidence'):
                message += "🎯 <b>YOUR PREFERENCES</b>\n"
                for key, value in prefs['confidence'].items():
                    message += f"• {key.replace('_', ' ').title()}: {value}%\n"
                message += "\n"
            
            # Strategy performance
            strategies = perf.get('strategies', [])
            if strategies:
                message += "📈 <b>STRATEGY PERFORMANCE</b>\n"
                for strat in strategies[:3]:  # Top 3
                    message += f"• {strat['strategy']}: {strat['win_rate']:.1f}% win rate\n"
                message += "\n"
            
            # Calibration
            message += "🎓 <b>CONFIDENCE CALIBRATION</b>\n"
            for strategy_name, cal_data in report.get('calibration', {}).items():
                if cal_data.get('bias'):
                    bias = cal_data['bias']
                    message += f"• {strategy_name}: {bias['bias']}\n"
            
            await update.message.reply_text(message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error in learning_report command: {e}")
            await update.message.reply_text(f"❌ Error generating report: {str(e)}")
    
    async def cmd_backtest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /backtest command - run backtest"""
        if not context.args or len(context.args) < 1:
            await update.message.reply_text(
                "📊 <b>Backtest Command</b>\n\n"
                "Usage: /backtest [strategy] [period]\n\n"
                "Examples:\n"
                "• /backtest TrendFollowing 6mo\n"
                "• /backtest all 1y\n\n"
                "Strategies: TrendFollowing, MeanReversion, Breakout, ValueInvestment, all",
                parse_mode='HTML'
            )
            return
        
        strategy_name = context.args[0]
        period = context.args[1] if len(context.args) > 1 else '6mo'
        
        await update.message.reply_text(
            f"🔄 Running backtest for {strategy_name} ({period})...\n"
            "This may take a few minutes."
        )
        
        try:
            # This is a simplified version - full implementation would run actual backtest
            await update.message.reply_text(
                "⚠️ <b>Backtest Feature</b>\n\n"
                "Full backtesting requires historical data download.\n"
                "This feature will be available in the next update.\n\n"
                "For now, use /learning_report to see performance based on actual trades.",
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error in backtest command: {e}")
            await update.message.reply_text(f"❌ Error running backtest: {str(e)}")
    
    async def cmd_calibration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /calibration command - show confidence calibration"""
        try:
            report = self.confidence_calibrator.get_calibration_report()
            
            message = "🎓 <b>CONFIDENCE CALIBRATION REPORT</b>\n\n"
            message += f"Overall Accuracy: {report['overall_accuracy']:.1f}%\n"
            message += f"Calibrated Buckets: {report['total_buckets']}\n\n"
            
            if report['calibrations']:
                message += "<b>Strategy Calibrations:</b>\n"
                for cal in report['calibrations'][:5]:  # Show top 5
                    message += f"\n• {cal['strategy']} ({cal['confidence_bucket']}%)\n"
                    message += f"  Predicted: {cal['predicted_win_rate']:.1f}%\n"
                    message += f"  Actual: {cal['actual_win_rate']:.1f}%\n"
                    message += f"  Factor: {cal['calibration_factor']:.2f}\n"
            else:
                message += "No calibration data yet. Need more trades!"
            
            await update.message.reply_text(message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error in calibration command: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def cmd_preferences(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /preferences command - show learned preferences"""
        try:
            prefs = self.preference_learner.get_all_preferences()
            
            if not prefs:
                await update.message.reply_text(
                    "📊 <b>No Preferences Learned Yet</b>\n\n"
                    "Take some trades and the bot will learn your preferences!\n\n"
                    "The bot learns:\n"
                    "• Which strategies you prefer\n"
                    "• Your confidence threshold\n"
                    "• Preferred timeframes\n"
                    "• Risk tolerance",
                    parse_mode='HTML'
                )
                return
            
            message = "🎯 <b>YOUR TRADING PREFERENCES</b>\n\n"
            
            # Group by category
            strategies = {}
            timeframes = {}
            other = {}
            
            for key, data in prefs.items():
                if key.startswith('strategy_'):
                    strategies[key] = data
                elif key.startswith('timeframe_'):
                    timeframes[key] = data
                else:
                    other[key] = data
            
            if strategies:
                message += "<b>Strategy Preferences:</b>\n"
                for key, data in strategies.items():
                    name = key.replace('strategy_', '')
                    pref = float(data['value']) * 100
                    message += f"• {name}: {pref:.0f}% ({data['sample_size']} trades)\n"
                message += "\n"
            
            if timeframes:
                message += "<b>Timeframe Preferences:</b>\n"
                for key, data in timeframes.items():
                    name = key.replace('timeframe_', '')
                    pref = float(data['value']) * 100
                    message += f"• {name}: {pref:.0f}% ({data['sample_size']} trades)\n"
                message += "\n"
            
            if other:
                message += "<b>Other Preferences:</b>\n"
                for key, data in other.items():
                    message += f"• {key.replace('_', ' ').title()}: {data['value']}\n"
            
            await update.message.reply_text(message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error in preferences command: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def cmd_reset_learning(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reset_learning command - reset all learned data"""
        await update.message.reply_text(
            "⚠️ <b>Reset Learning Data?</b>\n\n"
            "This will delete all learned preferences and calibrations.\n"
            "Your trade history will NOT be deleted.\n\n"
            "Reply 'CONFIRM RESET' to proceed.",
            parse_mode='HTML'
        )
        
        # Note: Full implementation would wait for confirmation
        # For now, just show warning
