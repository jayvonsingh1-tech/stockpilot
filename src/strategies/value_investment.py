"""
Value Investment Strategy - Find undervalued companies for long-term holds
Optimized for efficiency and accuracy
"""
from typing import Dict, Optional
import pandas as pd
import yfinance as yf
from ..analysis.technical import TechnicalAnalysis
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class ValueInvestmentStrategy:
    """
    Value investing strategy for long-term positions
    
    Identifies undervalued companies with:
    - Low P/E ratios (< 15)
    - Low P/B ratios (< 1.5)
    - Strong fundamentals
    - Positive cash flow
    - Growing revenue
    """
    
    def __init__(self):
        """Initialize value investment strategy"""
        self.ta = TechnicalAnalysis()
        self.name = "Value Investment"
        
        # Cached stock info to avoid repeated API calls
        self._info_cache = {}
        
    def analyze(self, df: pd.DataFrame, ticker: str) -> Optional[Dict]:
        """
        Analyze for value investment opportunities
        
        Args:
            df: DataFrame with OHLCV data
            ticker: Stock ticker
            
        Returns:
            Signal dictionary or None
        """
        try:
            if len(df) < 200:  # Need enough data for long-term analysis
                return None
            
            # Get fundamental data (with caching)
            info = self._get_stock_info(ticker)
            if not info:
                return None
            
            # Check if meets value criteria
            if not self._meets_value_criteria(info):
                return None
            
            # Calculate fair value
            fair_value = self._calculate_fair_value(info, df)
            if not fair_value:
                return None
            
            current_price = df['Close'].iloc[-1]
            
            # Only signal if significantly undervalued (20%+ discount)
            discount = ((fair_value - current_price) / fair_value) * 100
            if discount < 20:
                logger.debug(f"{ticker} not undervalued enough: {discount:.1f}% discount")
                return None
            
            # Technical confirmation - should be in uptrend or consolidating
            if not self._technical_confirmation(df):
                logger.debug(f"{ticker} failed technical confirmation")
                return None
            
            # Create long-term investment signal
            return self._create_investment_signal(
                ticker, current_price, fair_value, info, df
            )
            
        except Exception as e:
            logger.error(f"Error in value investment analysis for {ticker}: {e}")
            return None
    
    def _get_stock_info(self, ticker: str) -> Optional[Dict]:
        """Get stock info with caching to reduce API calls"""
        if ticker in self._info_cache:
            return self._info_cache[ticker]
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Validate we have required data
            required_fields = ['trailingPE', 'priceToBook', 'marketCap']
            if not all(field in info for field in required_fields):
                return None
            
            self._info_cache[ticker] = info
            return info
            
        except Exception as e:
            logger.error(f"Error fetching info for {ticker}: {e}")
            return None
    
    def _meets_value_criteria(self, info: Dict) -> bool:
        """
        Check if stock meets value investment criteria
        
        Criteria:
        - P/E < 15 (undervalued)
        - P/B < 1.5 (trading below book value)
        - Debt/Equity < 1.0 (manageable debt)
        - Profit Margin > 5% (profitable)
        - Revenue Growth > 0% (growing)
        - Market Cap > $1B (established company)
        """
        try:
            # P/E Ratio
            pe_ratio = info.get('trailingPE', 999)
            if pe_ratio <= 0 or pe_ratio > 15:
                return False
            
            # P/B Ratio
            pb_ratio = info.get('priceToBook', 999)
            if pb_ratio <= 0 or pb_ratio > 1.5:
                return False
            
            # Debt to Equity
            debt_to_equity = info.get('debtToEquity', 999)
            if debt_to_equity > 100:  # > 1.0
                return False
            
            # Profit Margin
            profit_margin = info.get('profitMargins', 0)
            if profit_margin < 0.05:  # < 5%
                return False
            
            # Revenue Growth
            revenue_growth = info.get('revenueGrowth', -1)
            if revenue_growth < 0:
                return False
            
            # Market Cap (min $1B)
            market_cap = info.get('marketCap', 0)
            if market_cap < 1_000_000_000:
                return False
            
            # Free Cash Flow (must be positive)
            free_cash_flow = info.get('freeCashflow', 0)
            if free_cash_flow <= 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking value criteria: {e}")
            return False
    
    def _calculate_fair_value(self, info: Dict, df: pd.DataFrame) -> Optional[float]:
        """
        Calculate fair value using simplified DCF
        
        Uses:
        - Free Cash Flow
        - Growth rate
        - Discount rate (10%)
        - Terminal growth (3%)
        """
        try:
            # Get free cash flow
            fcf = info.get('freeCashflow', 0)
            if fcf <= 0:
                return None
            
            # Estimate growth rate from revenue growth
            growth_rate = info.get('revenueGrowth', 0.05)
            growth_rate = min(growth_rate, 0.15)  # Cap at 15%
            
            # Project 5 years of cash flows
            discount_rate = 0.10  # 10% required return
            terminal_growth = 0.03  # 3% perpetual growth
            
            projected_fcf = []
            for year in range(1, 6):
                fcf_year = fcf * ((1 + growth_rate) ** year)
                pv = fcf_year / ((1 + discount_rate) ** year)
                projected_fcf.append(pv)
            
            # Terminal value
            terminal_fcf = fcf * ((1 + growth_rate) ** 5) * (1 + terminal_growth)
            terminal_value = terminal_fcf / (discount_rate - terminal_growth)
            terminal_pv = terminal_value / ((1 + discount_rate) ** 5)
            
            # Enterprise value
            enterprise_value = sum(projected_fcf) + terminal_pv
            
            # Adjust for debt and cash
            total_debt = info.get('totalDebt', 0)
            total_cash = info.get('totalCash', 0)
            equity_value = enterprise_value - total_debt + total_cash
            
            # Fair value per share
            shares_outstanding = info.get('sharesOutstanding', 1)
            fair_value = equity_value / shares_outstanding
            
            return max(fair_value, 0)
            
        except Exception as e:
            logger.error(f"Error calculating fair value: {e}")
            return None
    
    def _technical_confirmation(self, df: pd.DataFrame) -> bool:
        """
        Technical confirmation for entry
        
        Requirements:
        - Price above SMA 200 (long-term uptrend) OR
        - Price consolidating near support
        - RSI not overbought (< 70)
        """
        try:
            sma200 = self.ta.calculate_sma(df, 200)
            rsi = self.ta.calculate_rsi(df)
            
            if sma200.empty or rsi.empty:
                return False
            
            current_price = df['Close'].iloc[-1]
            sma200_val = sma200.iloc[-1]
            rsi_val = rsi.iloc[-1]
            
            # Check RSI not overbought
            if rsi_val > 70:
                return False
            
            # Price above SMA 200 (uptrend) or within 10% below (consolidation)
            price_vs_sma = ((current_price - sma200_val) / sma200_val) * 100
            if price_vs_sma < -10:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error in technical confirmation: {e}")
            return False
    
    def _create_investment_signal(self, ticker: str, current_price: float,
                                  fair_value: float, info: Dict, 
                                  df: pd.DataFrame) -> Dict:
        """Create long-term investment signal"""
        
        # Calculate targets
        target_price = fair_value * 1.2  # 20% above fair value
        stop_loss = current_price * 0.90  # 10% stop (wider for long-term)
        
        # Calculate ATR for position sizing
        atr = self.ta.calculate_atr(df)
        atr_val = atr.iloc[-1] if not atr.empty else current_price * 0.02
        
        # Calculate expected return
        expected_return = ((target_price - current_price) / current_price) * 100
        
        # Build investment thesis
        pe_ratio = info.get('trailingPE', 0)
        pb_ratio = info.get('priceToBook', 0)
        profit_margin = info.get('profitMargins', 0) * 100
        revenue_growth = info.get('revenueGrowth', 0) * 100
        
        reasoning = [
            f'Undervalued: Trading at ${current_price:.2f}, fair value ${fair_value:.2f}',
            f'Low P/E ratio: {pe_ratio:.1f} (market avg ~20)',
            f'Low P/B ratio: {pb_ratio:.2f} (below book value)',
            f'Strong margins: {profit_margin:.1f}% profit margin',
            f'Growing revenue: +{revenue_growth:.1f}% YoY',
            'Positive free cash flow',
            'Manageable debt levels',
            'Long-term uptrend confirmed'
        ]
        
        return {
            'ticker': ticker,
            'action': 'BUY',
            'strategy': self.name,
            'trading_type': 'LONG_TERM_INVESTMENT',
            
            # Entry
            'entry_price': round(current_price, 2),
            'fair_value': round(fair_value, 2),
            'target_price': round(target_price, 2),
            'stop_loss': round(stop_loss, 2),
            
            # Investment details
            'timeframe': '6-12 months',
            'expected_return': round(expected_return, 1),
            'discount_to_fair_value': round(((fair_value - current_price) / fair_value) * 100, 1),
            
            # Exit strategy
            'exit_strategy': {
                'type': 'value_based',
                'fair_value_exit': round(fair_value, 2),
                'target_exit': round(target_price, 2),
                'stop_loss': round(stop_loss, 2),
                'review_period': '6 months',
                'exit_conditions': [
                    f'Sell 50% at fair value (${fair_value:.2f})',
                    f'Sell remaining 50% at target (${target_price:.2f})',
                    'Exit if fundamentals deteriorate',
                    'Exit if better opportunity found'
                ]
            },
            
            # Fundamentals
            'fundamentals': {
                'pe_ratio': round(pe_ratio, 1),
                'pb_ratio': round(pb_ratio, 2),
                'profit_margin': round(profit_margin, 1),
                'revenue_growth': round(revenue_growth, 1),
                'debt_to_equity': round(info.get('debtToEquity', 0) / 100, 2),
            },
            
            # Risk management
            'risk_type': 'long_term',
            'max_loss_percent': 10,
            'position_sizing_method': 'value_based',
            
            # Reasoning
            'reasoning': reasoning,
            'investment_thesis': f"Undervalued {info.get('sector', 'company')} leader trading at {((fair_value - current_price) / fair_value) * 100:.0f}% discount to fair value"
        }
    
    def clear_cache(self):
        """Clear the info cache"""
        self._info_cache.clear()
        logger.debug("Value investment cache cleared")
