"""
Backtest Engine - Test trading strategies on historical data
Simulates trades to evaluate strategy performance before going live
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from ..data.fetcher import MarketDataFetcher
from ..analysis.technical import TechnicalAnalysis
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class BacktestEngine:
    """
    Backtest trading strategies on historical data
    
    Features:
    - Realistic trade simulation
    - Commission and slippage modeling
    - Multiple strategies
    - Performance metrics
    - Trade-by-trade analysis
    """
    
    def __init__(self, initial_capital: float = 50000, commission: float = 0.0,
                 slippage: float = 0.001):
        """
        Initialize backtest engine
        
        Args:
            initial_capital: Starting capital
            commission: Commission per trade (0.0 = no commission)
            slippage: Slippage percentage (0.001 = 0.1%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.data_fetcher = MarketDataFetcher()
        self.ta = TechnicalAnalysis()
        
        # Backtest state
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        
    def run_backtest(self, strategy, tickers: List[str], start_date: str,
                    end_date: str, timeframe: str = '1d') -> Dict:
        """
        Run backtest for a strategy
        
        Args:
            strategy: Strategy instance with generate_signal() method
            tickers: List of tickers to trade
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            timeframe: Timeframe ('1d', '1h', etc.)
            
        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Starting backtest: {start_date} to {end_date}")
        logger.info(f"Tickers: {len(tickers)}, Initial capital: ${self.initial_capital:,.2f}")
        
        # Reset state
        self._reset_state()
        
        # Get historical data for all tickers
        historical_data = {}
        for ticker in tickers:
            try:
                df = self.data_fetcher.fetch_ohlcv(
                    ticker,
                    start=start_date,
                    end=end_date,
                    interval=timeframe
                )
                if df is not None and len(df) > 0:
                    historical_data[ticker] = df
                    logger.info(f"Loaded {len(df)} bars for {ticker}")
            except Exception as e:
                logger.error(f"Error loading data for {ticker}: {e}")
        
        if not historical_data:
            logger.error("No historical data loaded")
            return None
        
        # Get all unique dates
        all_dates = set()
        for df in historical_data.values():
            all_dates.update(df.index)
        all_dates = sorted(list(all_dates))
        
        logger.info(f"Backtesting {len(all_dates)} trading days...")
        
        # Simulate trading day by day
        for i, date in enumerate(all_dates):
            # Update equity curve
            self._update_equity(date, historical_data)
            
            # Check for exits first
            self._check_exits(date, historical_data)
            
            # Generate signals for each ticker
            for ticker in tickers:
                if ticker not in historical_data:
                    continue
                
                df = historical_data[ticker]
                
                # Get data up to current date
                current_data = df[df.index <= date]
                
                if len(current_data) < 50:  # Need minimum data for indicators
                    continue
                
                # Generate signal
                try:
                    signal = strategy.generate_signal(ticker, current_data)
                    
                    if signal and signal.get('action') in ['BUY', 'SELL']:
                        # Execute trade
                        self._execute_trade(signal, date, current_data)
                        
                except Exception as e:
                    logger.debug(f"Error generating signal for {ticker}: {e}")
            
            # Progress update
            if (i + 1) % 50 == 0:
                progress = ((i + 1) / len(all_dates)) * 100
                logger.info(f"Progress: {progress:.1f}% ({i+1}/{len(all_dates)} days)")
        
        # Close any remaining positions
        self._close_all_positions(all_dates[-1], historical_data)
        
        # Calculate results
        results = self._calculate_results()
        
        logger.info(f"Backtest complete! Final capital: ${self.capital:,.2f}")
        logger.info(f"Total return: {results['total_return']:.2f}%")
        logger.info(f"Total trades: {results['total_trades']}")
        logger.info(f"Win rate: {results['win_rate']:.2f}%")
        
        return results
    
    def _execute_trade(self, signal: Dict, date, df: pd.DataFrame):
        """Execute a trade based on signal"""
        ticker = signal['ticker']
        action = signal['action']
        
        # Check if already in position
        if ticker in self.positions:
            return
        
        # Get entry price (with slippage)
        entry_price = signal['entry_price']
        if action == 'BUY':
            entry_price *= (1 + self.slippage)
        else:
            entry_price *= (1 - self.slippage)
        
        # Calculate position size (risk 1% of capital per trade)
        risk_amount = self.capital * 0.01
        stop_loss = signal.get('stop_loss', entry_price * 0.97)
        risk_per_share = abs(entry_price - stop_loss)
        
        if risk_per_share == 0:
            return
        
        shares = int(risk_amount / risk_per_share)
        
        if shares <= 0:
            return
        
        position_value = shares * entry_price
        
        # Check if we have enough capital
        if position_value > self.capital * 0.2:  # Max 20% per position
            shares = int((self.capital * 0.2) / entry_price)
            position_value = shares * entry_price
        
        if position_value > self.capital:
            return
        
        # Apply commission
        commission_cost = position_value * self.commission
        
        # Open position
        self.positions[ticker] = {
            'ticker': ticker,
            'action': action,
            'entry_price': entry_price,
            'entry_date': date,
            'shares': shares,
            'stop_loss': stop_loss,
            'take_profit_1': signal.get('take_profit_1'),
            'take_profit_2': signal.get('take_profit_2'),
            'take_profit_3': signal.get('take_profit_3'),
            'strategy': signal.get('strategy'),
            'confidence': signal.get('confidence'),
            'cost': position_value + commission_cost
        }
        
        self.capital -= (position_value + commission_cost)
        
        logger.debug(f"Opened {action} position: {ticker} @ ${entry_price:.2f} x {shares} shares")
    
    def _check_exits(self, date, historical_data: Dict):
        """Check if any positions should be closed"""
        positions_to_close = []
        
        for ticker, position in self.positions.items():
            if ticker not in historical_data:
                continue
            
            df = historical_data[ticker]
            current_data = df[df.index <= date]
            
            if len(current_data) == 0:
                continue
            
            current_price = current_data['Close'].iloc[-1]
            entry_price = position['entry_price']
            action = position['action']
            
            # Check stop loss
            if action == 'BUY':
                if current_price <= position['stop_loss']:
                    positions_to_close.append((ticker, current_price, 'stop_loss'))
                    continue
                
                # Check take profits
                if position.get('take_profit_1') and current_price >= position['take_profit_1']:
                    positions_to_close.append((ticker, current_price, 'take_profit_1'))
                    continue
                elif position.get('take_profit_2') and current_price >= position['take_profit_2']:
                    positions_to_close.append((ticker, current_price, 'take_profit_2'))
                    continue
                elif position.get('take_profit_3') and current_price >= position['take_profit_3']:
                    positions_to_close.append((ticker, current_price, 'take_profit_3'))
                    continue
            
            else:  # SELL
                if current_price >= position['stop_loss']:
                    positions_to_close.append((ticker, current_price, 'stop_loss'))
                    continue
                
                if position.get('take_profit_1') and current_price <= position['take_profit_1']:
                    positions_to_close.append((ticker, current_price, 'take_profit_1'))
                    continue
            
            # Check max hold time (30 days)
            hold_days = (date - position['entry_date']).days
            if hold_days >= 30:
                positions_to_close.append((ticker, current_price, 'time_exit'))
        
        # Close positions
        for ticker, exit_price, exit_reason in positions_to_close:
            self._close_position(ticker, exit_price, date, exit_reason)
    
    def _close_position(self, ticker: str, exit_price: float, exit_date, reason: str):
        """Close a position"""
        if ticker not in self.positions:
            return
        
        position = self.positions[ticker]
        
        # Apply slippage
        if position['action'] == 'BUY':
            exit_price *= (1 - self.slippage)
        else:
            exit_price *= (1 + self.slippage)
        
        # Calculate P&L
        if position['action'] == 'BUY':
            pnl = (exit_price - position['entry_price']) * position['shares']
        else:
            pnl = (position['entry_price'] - exit_price) * position['shares']
        
        # Apply commission
        exit_value = exit_price * position['shares']
        commission_cost = exit_value * self.commission
        pnl -= commission_cost
        
        # Update capital
        self.capital += exit_value - commission_cost
        
        # Calculate metrics
        pnl_percent = (pnl / position['cost']) * 100
        hold_days = (exit_date - position['entry_date']).days
        
        # Record trade
        trade = {
            'ticker': ticker,
            'action': position['action'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'entry_date': position['entry_date'],
            'exit_date': exit_date,
            'shares': position['shares'],
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'hold_days': hold_days,
            'exit_reason': reason,
            'strategy': position.get('strategy'),
            'confidence': position.get('confidence')
        }
        
        self.trades.append(trade)
        
        # Remove position
        del self.positions[ticker]
        
        logger.debug(f"Closed {ticker}: ${pnl:+,.2f} ({pnl_percent:+.2f}%) - {reason}")
    
    def _close_all_positions(self, date, historical_data: Dict):
        """Close all remaining positions"""
        for ticker in list(self.positions.keys()):
            if ticker in historical_data:
                df = historical_data[ticker]
                current_data = df[df.index <= date]
                if len(current_data) > 0:
                    exit_price = current_data['Close'].iloc[-1]
                    self._close_position(ticker, exit_price, date, 'backtest_end')
    
    def _update_equity(self, date, historical_data: Dict):
        """Update equity curve"""
        # Calculate current portfolio value
        portfolio_value = self.capital
        
        for ticker, position in self.positions.items():
            if ticker in historical_data:
                df = historical_data[ticker]
                current_data = df[df.index <= date]
                if len(current_data) > 0:
                    current_price = current_data['Close'].iloc[-1]
                    position_value = current_price * position['shares']
                    portfolio_value += position_value
        
        self.equity_curve.append({
            'date': date,
            'equity': portfolio_value
        })
    
    def _calculate_results(self) -> Dict:
        """Calculate backtest results"""
        if not self.trades:
            return self._empty_results()
        
        # Basic metrics
        total_trades = len(self.trades)
        wins = [t for t in self.trades if t['pnl'] > 0]
        losses = [t for t in self.trades if t['pnl'] < 0]
        
        win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
        
        total_profit = sum(t['pnl'] for t in wins)
        total_loss = abs(sum(t['pnl'] for t in losses))
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100
        
        # Calculate Sharpe ratio
        returns = [t['pnl_percent'] for t in self.trades]
        if returns:
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = (mean_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Calculate max drawdown
        max_dd = self._calculate_max_drawdown()
        
        # Average metrics
        avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss = np.mean([t['pnl'] for t in losses]) if losses else 0
        avg_hold_days = np.mean([t['hold_days'] for t in self.trades])
        
        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_return': round(total_return, 2),
            'total_trades': total_trades,
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': round(win_rate, 2),
            'profit_factor': round(profit_factor, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_dd, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'largest_win': round(max([t['pnl'] for t in wins]), 2) if wins else 0,
            'largest_loss': round(min([t['pnl'] for t in losses]), 2) if losses else 0,
            'avg_hold_days': round(avg_hold_days, 1),
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown from equity curve"""
        if not self.equity_curve:
            return 0
        
        equity_values = [e['equity'] for e in self.equity_curve]
        peak = equity_values[0]
        max_dd = 0
        
        for equity in equity_values:
            if equity > peak:
                peak = equity
            dd = ((peak - equity) / peak) * 100 if peak > 0 else 0
            max_dd = max(max_dd, dd)
        
        return max_dd
    
    def _reset_state(self):
        """Reset backtest state"""
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
    
    def _empty_results(self) -> Dict:
        """Return empty results"""
        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_return': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'avg_hold_days': 0,
            'trades': [],
            'equity_curve': []
        }
