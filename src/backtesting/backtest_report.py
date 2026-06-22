"""
Backtest Report - Generate formatted backtest reports
"""
from typing import Dict, List
from datetime import datetime
import json
from pathlib import Path
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class BacktestReport:
    """Generate and format backtest reports"""
    
    def __init__(self):
        """Initialize report generator"""
        self.reports_dir = Path("data/backtest_results")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, results: Dict, strategy_name: str) -> str:
        """
        Generate formatted backtest report
        
        Args:
            results: Backtest results dictionary
            strategy_name: Name of strategy
            
        Returns:
            Formatted report string
        """
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║              BACKTEST REPORT - {strategy_name.upper()}              ║
╚══════════════════════════════════════════════════════════════╝

📊 PERFORMANCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Returns:
   Initial Capital:     ${results['initial_capital']:>15,.2f}
   Final Capital:       ${results['final_capital']:>15,.2f}
   Total Return:        {results['total_return']:>15.2f}%
   
📈 Trading Activity:
   Total Trades:        {results['total_trades']:>15}
   Winning Trades:      {results['winning_trades']:>15} ({results['win_rate']:.1f}%)
   Losing Trades:       {results['losing_trades']:>15}
   
🎯 Performance Metrics:
   Win Rate:            {results['win_rate']:>15.2f}%
   Profit Factor:       {results['profit_factor']:>15.2f}
   Sharpe Ratio:        {results['sharpe_ratio']:>15.2f}
   Max Drawdown:        {results['max_drawdown']:>15.2f}%
   
💵 Trade Statistics:
   Average Win:         ${results['avg_win']:>15,.2f}
   Average Loss:        ${results['avg_loss']:>15,.2f}
   Largest Win:         ${results['largest_win']:>15,.2f}
   Largest Loss:        ${results['largest_loss']:>15,.2f}
   Avg Hold Time:       {results['avg_hold_days']:>15.1f} days

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 TRADE BREAKDOWN
"""
        
        # Add top 5 winning trades
        if results['trades']:
            winning_trades = sorted(
                [t for t in results['trades'] if t['pnl'] > 0],
                key=lambda x: x['pnl'],
                reverse=True
            )[:5]
            
            if winning_trades:
                report += "\n🏆 Top 5 Winning Trades:\n"
                for i, trade in enumerate(winning_trades, 1):
                    report += f"   {i}. {trade['ticker']}: ${trade['pnl']:+,.2f} ({trade['pnl_percent']:+.2f}%) - {trade['hold_days']} days\n"
            
            # Add top 5 losing trades
            losing_trades = sorted(
                [t for t in results['trades'] if t['pnl'] < 0],
                key=lambda x: x['pnl']
            )[:5]
            
            if losing_trades:
                report += "\n⚠️ Top 5 Losing Trades:\n"
                for i, trade in enumerate(losing_trades, 1):
                    report += f"   {i}. {trade['ticker']}: ${trade['pnl']:+,.2f} ({trade['pnl_percent']:+.2f}%) - {trade['hold_days']} days\n"
        
        report += "\n" + "━" * 62 + "\n"
        
        # Add rating
        rating = self._calculate_rating(results)
        report += f"\n{rating['emoji']} OVERALL RATING: {rating['grade']} - {rating['description']}\n"
        
        report += "\n" + "═" * 62 + "\n"
        
        return report
    
    def generate_telegram_report(self, results: Dict, strategy_name: str) -> str:
        """
        Generate Telegram-friendly backtest report
        
        Args:
            results: Backtest results dictionary
            strategy_name: Name of strategy
            
        Returns:
            Formatted Telegram message
        """
        rating = self._calculate_rating(results)
        
        message = f"""
📊 <b>BACKTEST REPORT - {strategy_name.upper()}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 <b>RETURNS</b>
• Initial: ${results['initial_capital']:,.2f}
• Final: ${results['final_capital']:,.2f}
• Return: <b>{results['total_return']:+.2f}%</b>

📈 <b>TRADING</b>
• Total Trades: {results['total_trades']}
• Win Rate: <b>{results['win_rate']:.1f}%</b>
• Profit Factor: {results['profit_factor']:.2f}

🎯 <b>METRICS</b>
• Sharpe Ratio: {results['sharpe_ratio']:.2f}
• Max Drawdown: {results['max_drawdown']:.2f}%
• Avg Hold: {results['avg_hold_days']:.1f} days

💵 <b>TRADE STATS</b>
• Avg Win: ${results['avg_win']:,.2f}
• Avg Loss: ${results['avg_loss']:,.2f}
• Best: ${results['largest_win']:,.2f}
• Worst: ${results['largest_loss']:,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

{rating['emoji']} <b>RATING: {rating['grade']}</b>
{rating['description']}
"""
        
        return message
    
    def save_report(self, results: Dict, strategy_name: str, filename: str = None) -> str:
        """
        Save backtest report to file
        
        Args:
            results: Backtest results dictionary
            strategy_name: Name of strategy
            filename: Optional filename
            
        Returns:
            Path to saved report
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{strategy_name}_{timestamp}.txt"
        
        filepath = self.reports_dir / filename
        
        # Generate report
        report = self.generate_report(results, strategy_name)
        
        # Save to file
        with open(filepath, 'w') as f:
            f.write(report)
        
        # Also save JSON data
        json_filepath = filepath.with_suffix('.json')
        with open(json_filepath, 'w') as f:
            # Convert datetime objects to strings
            results_copy = results.copy()
            if 'trades' in results_copy:
                for trade in results_copy['trades']:
                    if 'entry_date' in trade:
                        trade['entry_date'] = str(trade['entry_date'])
                    if 'exit_date' in trade:
                        trade['exit_date'] = str(trade['exit_date'])
            if 'equity_curve' in results_copy:
                for point in results_copy['equity_curve']:
                    if 'date' in point:
                        point['date'] = str(point['date'])
            
            json.dump(results_copy, f, indent=2)
        
        logger.info(f"Backtest report saved: {filepath}")
        return str(filepath)
    
    def compare_strategies(self, results_list: List[Dict], strategy_names: List[str]) -> str:
        """
        Compare multiple strategy backtest results
        
        Args:
            results_list: List of backtest results
            strategy_names: List of strategy names
            
        Returns:
            Comparison report
        """
        report = """
╔══════════════════════════════════════════════════════════════╗
║                    STRATEGY COMPARISON                        ║
╚══════════════════════════════════════════════════════════════╝

"""
        
        # Create comparison table
        metrics = [
            ('Total Return', 'total_return', '%'),
            ('Win Rate', 'win_rate', '%'),
            ('Profit Factor', 'profit_factor', ''),
            ('Sharpe Ratio', 'sharpe_ratio', ''),
            ('Max Drawdown', 'max_drawdown', '%'),
            ('Total Trades', 'total_trades', ''),
        ]
        
        for metric_name, metric_key, unit in metrics:
            report += f"\n{metric_name}:\n"
            for i, (results, name) in enumerate(zip(results_list, strategy_names)):
                value = results.get(metric_key, 0)
                if unit == '%':
                    report += f"   {name:20s}: {value:>10.2f}%\n"
                else:
                    report += f"   {name:20s}: {value:>10.2f}\n"
        
        # Determine best strategy
        best_strategy_idx = max(
            range(len(results_list)),
            key=lambda i: results_list[i].get('sharpe_ratio', 0)
        )
        
        report += f"\n{'━' * 62}\n"
        report += f"\n🏆 BEST STRATEGY: {strategy_names[best_strategy_idx]}\n"
        report += f"   (Based on Sharpe Ratio)\n"
        
        return report
    
    def _calculate_rating(self, results: Dict) -> Dict:
        """Calculate overall rating for backtest"""
        score = 0
        max_score = 100
        
        # Return (30 points)
        if results['total_return'] > 50:
            score += 30
        elif results['total_return'] > 30:
            score += 25
        elif results['total_return'] > 20:
            score += 20
        elif results['total_return'] > 10:
            score += 15
        elif results['total_return'] > 0:
            score += 10
        
        # Win rate (25 points)
        if results['win_rate'] > 70:
            score += 25
        elif results['win_rate'] > 60:
            score += 20
        elif results['win_rate'] > 50:
            score += 15
        elif results['win_rate'] > 40:
            score += 10
        
        # Sharpe ratio (25 points)
        if results['sharpe_ratio'] > 2.0:
            score += 25
        elif results['sharpe_ratio'] > 1.5:
            score += 20
        elif results['sharpe_ratio'] > 1.0:
            score += 15
        elif results['sharpe_ratio'] > 0.5:
            score += 10
        
        # Max drawdown (20 points)
        if results['max_drawdown'] < 5:
            score += 20
        elif results['max_drawdown'] < 10:
            score += 15
        elif results['max_drawdown'] < 15:
            score += 10
        elif results['max_drawdown'] < 20:
            score += 5
        
        # Determine grade
        percentage = (score / max_score) * 100
        
        if percentage >= 90:
            grade = 'A+'
            emoji = '🌟'
            description = 'Excellent! Strategy shows strong performance.'
        elif percentage >= 80:
            grade = 'A'
            emoji = '⭐'
            description = 'Very good! Strategy is highly profitable.'
        elif percentage >= 70:
            grade = 'B+'
            emoji = '✅'
            description = 'Good! Strategy shows promise.'
        elif percentage >= 60:
            grade = 'B'
            emoji = '👍'
            description = 'Decent! Strategy is profitable but needs improvement.'
        elif percentage >= 50:
            grade = 'C'
            emoji = '⚠️'
            description = 'Average. Consider optimizing parameters.'
        else:
            grade = 'D'
            emoji = '❌'
            description = 'Poor. Strategy needs significant improvement.'
        
        return {
            'score': score,
            'percentage': percentage,
            'grade': grade,
            'emoji': emoji,
            'description': description
        }
