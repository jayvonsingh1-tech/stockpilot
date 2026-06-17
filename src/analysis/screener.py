"""
Stock Screener - Finds new investment opportunities
"""
from typing import Dict, List, Optional
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from ..data.fetcher import MarketDataFetcher
from ..analysis.technical import TechnicalAnalysis
from ..utils.logger import setup_logger
from ..utils.config import get_config


logger = setup_logger(__name__)


class StockScreener:
    """Screens stocks for investment opportunities"""
    
    def __init__(self):
        """Initialize stock screener"""
        self.config = get_config()
        self.data_fetcher = MarketDataFetcher()
        self.ta = TechnicalAnalysis()
        
        # Popular stock universes to screen
        self.us_stocks = [
            # Tech Giants
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'AMD', 'INTC', 'CRM',
            # Finance
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'V', 'MA', 'PYPL',
            # Healthcare
            'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT', 'MRK', 'LLY', 'BMY', 'AMGN',
            # Consumer
            'WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'COST', 'LOW', 'DIS', 'NFLX',
            # Industrial
            'BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'RTX', 'LMT', 'DE', 'EMR',
            # Energy
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL',
            # Telecom
            'T', 'VZ', 'TMUS', 'CMCSA',
            # Retail
            'AMZN', 'WMT', 'TGT', 'COST', 'HD', 'LOW', 'TJX', 'ROST',
            # Semiconductors
            'NVDA', 'AMD', 'INTC', 'QCOM', 'AVGO', 'TXN', 'ADI', 'MU', 'AMAT', 'LRCX'
        ]
        
        self.uk_stocks = [
            # FTSE 100 Major Stocks
            'SHEL.L', 'AZN.L', 'HSBA.L', 'ULVR.L', 'BP.L', 'GSK.L', 'DGE.L', 'RIO.L',
            'LSEG.L', 'NG.L', 'REL.L', 'BARC.L', 'LLOY.L', 'VOD.L', 'TSCO.L', 'PRU.L',
            'BT-A.L', 'IMB.L', 'BATS.L', 'AAL.L', 'CRH.L', 'GLEN.L', 'BA.L', 'RKT.L'
        ]
    
    def screen_daily(self, max_results: int = 10) -> List[Dict]:
        """
        Run daily stock screen to find new opportunities
        
        Args:
            max_results: Maximum number of stocks to return
            
        Returns:
            List of recommended stocks with scores
        """
        logger.info("Starting daily stock screening...")
        
        candidates = []
        
        # Screen US stocks
        logger.info(f"Screening {len(self.us_stocks)} US stocks...")
        for ticker in self.us_stocks:
            try:
                score = self._evaluate_stock(ticker)
                if score and score['total_score'] >= 70:  # Minimum 70/100 score
                    candidates.append(score)
            except Exception as e:
                logger.debug(f"Error screening {ticker}: {e}")
                continue
        
        # Screen UK stocks
        logger.info(f"Screening {len(self.uk_stocks)} UK stocks...")
        for ticker in self.uk_stocks:
            try:
                score = self._evaluate_stock(ticker)
                if score and score['total_score'] >= 70:
                    candidates.append(score)
            except Exception as e:
                logger.debug(f"Error screening {ticker}: {e}")
                continue
        
        # Sort by total score
        candidates.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Return top results
        top_candidates = candidates[:max_results]
        
        logger.info(f"Found {len(top_candidates)} high-quality investment opportunities")
        
        return top_candidates
    
    def _evaluate_stock(self, ticker: str) -> Optional[Dict]:
        """
        Evaluate a stock across multiple dimensions
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Dictionary with scores or None
        """
        try:
            # Fetch data
            df = self.data_fetcher.fetch_ohlcv(ticker, period='6mo', interval='1d')
            if df is None or len(df) < 100:
                return None
            
            # Get stock info
            info = self.data_fetcher.get_stock_info(ticker)
            if not info:
                return None
            
            # Calculate scores
            technical_score = self._calculate_technical_score(df)
            fundamental_score = self._calculate_fundamental_score(info)
            momentum_score = self._calculate_momentum_score(df)
            value_score = self._calculate_value_score(info)
            
            # Calculate total score (weighted average)
            total_score = (
                technical_score * 0.30 +
                fundamental_score * 0.30 +
                momentum_score * 0.25 +
                value_score * 0.15
            )
            
            return {
                'ticker': ticker,
                'name': info.get('longName', ticker),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'current_price': df['Close'].iloc[-1],
                'total_score': round(total_score, 1),
                'technical_score': round(technical_score, 1),
                'fundamental_score': round(fundamental_score, 1),
                'momentum_score': round(momentum_score, 1),
                'value_score': round(value_score, 1),
                'recommendation': self._get_recommendation(total_score),
                'reasons': self._get_reasons(technical_score, fundamental_score, momentum_score, value_score)
            }
            
        except Exception as e:
            logger.debug(f"Error evaluating {ticker}: {e}")
            return None
    
    def _calculate_technical_score(self, df: pd.DataFrame) -> float:
        """Calculate technical analysis score (0-100)"""
        score = 50  # Base score
        
        try:
            # Calculate indicators
            ema20 = self.ta.calculate_ema(df, 20)
            ema50 = self.ta.calculate_ema(df, 50)
            sma200 = self.ta.calculate_sma(df, 200)
            rsi = self.ta.calculate_rsi(df)
            macd, macd_signal, _ = self.ta.calculate_macd(df)
            adx = self.ta.calculate_adx(df)
            
            if ema20.empty or ema50.empty or sma200.empty:
                return score
            
            current_price = df['Close'].iloc[-1]
            ema20_val = ema20.iloc[-1]
            ema50_val = ema50.iloc[-1]
            sma200_val = sma200.iloc[-1]
            rsi_val = rsi.iloc[-1] if not rsi.empty else 50
            adx_val = adx.iloc[-1] if not adx.empty else 20
            
            # Trend alignment (30 points)
            if current_price > ema20_val > ema50_val > sma200_val:
                score += 30  # Perfect uptrend
            elif current_price > ema20_val > ema50_val:
                score += 20  # Good uptrend
            elif current_price > ema50_val:
                score += 10  # Moderate uptrend
            
            # RSI (15 points)
            if 40 < rsi_val < 60:
                score += 15  # Neutral - good for entry
            elif 30 < rsi_val < 70:
                score += 10  # Acceptable range
            
            # Trend strength (15 points)
            if adx_val > 30:
                score += 15  # Strong trend
            elif adx_val > 25:
                score += 10  # Moderate trend
            elif adx_val > 20:
                score += 5  # Weak trend
            
            # MACD (10 points)
            if not macd.empty and not macd_signal.empty:
                if macd.iloc[-1] > macd_signal.iloc[-1]:
                    score += 10  # Bullish MACD
            
            return min(score, 100)
            
        except Exception as e:
            logger.debug(f"Error calculating technical score: {e}")
            return 50
    
    def _calculate_fundamental_score(self, info: Dict) -> float:
        """Calculate fundamental analysis score (0-100)"""
        score = 50  # Base score
        
        try:
            # P/E Ratio (20 points)
            pe_ratio = info.get('trailingPE', 0)
            if 0 < pe_ratio < 15:
                score += 20  # Undervalued
            elif 15 <= pe_ratio < 25:
                score += 15  # Fair value
            elif 25 <= pe_ratio < 35:
                score += 5  # Slightly expensive
            
            # Profit Margin (15 points)
            profit_margin = info.get('profitMargins', 0)
            if profit_margin > 0.20:
                score += 15  # Excellent margins
            elif profit_margin > 0.10:
                score += 10  # Good margins
            elif profit_margin > 0.05:
                score += 5  # Acceptable margins
            
            # Revenue Growth (15 points)
            revenue_growth = info.get('revenueGrowth', 0)
            if revenue_growth > 0.20:
                score += 15  # High growth
            elif revenue_growth > 0.10:
                score += 10  # Good growth
            elif revenue_growth > 0:
                score += 5  # Positive growth
            
            # Debt to Equity (10 points)
            debt_to_equity = info.get('debtToEquity', 100)
            if debt_to_equity < 30:
                score += 10  # Low debt
            elif debt_to_equity < 60:
                score += 7  # Moderate debt
            elif debt_to_equity < 100:
                score += 3  # Acceptable debt
            
            # Return on Equity (10 points)
            roe = info.get('returnOnEquity', 0)
            if roe > 0.20:
                score += 10  # Excellent ROE
            elif roe > 0.15:
                score += 7  # Good ROE
            elif roe > 0.10:
                score += 4  # Acceptable ROE
            
            return min(score, 100)
            
        except Exception as e:
            logger.debug(f"Error calculating fundamental score: {e}")
            return 50
    
    def _calculate_momentum_score(self, df: pd.DataFrame) -> float:
        """Calculate momentum score (0-100)"""
        score = 50  # Base score
        
        try:
            current_price = df['Close'].iloc[-1]
            
            # 1-month performance (25 points)
            if len(df) >= 20:
                month_ago_price = df['Close'].iloc[-20]
                month_return = ((current_price - month_ago_price) / month_ago_price) * 100
                
                if month_return > 10:
                    score += 25
                elif month_return > 5:
                    score += 20
                elif month_return > 0:
                    score += 10
            
            # 3-month performance (25 points)
            if len(df) >= 60:
                three_month_ago_price = df['Close'].iloc[-60]
                three_month_return = ((current_price - three_month_ago_price) / three_month_ago_price) * 100
                
                if three_month_return > 20:
                    score += 25
                elif three_month_return > 10:
                    score += 20
                elif three_month_return > 0:
                    score += 10
            
            return min(score, 100)
            
        except Exception as e:
            logger.debug(f"Error calculating momentum score: {e}")
            return 50
    
    def _calculate_value_score(self, info: Dict) -> float:
        """Calculate value score (0-100)"""
        score = 50  # Base score
        
        try:
            # P/B Ratio (25 points)
            pb_ratio = info.get('priceToBook', 0)
            if 0 < pb_ratio < 1:
                score += 25  # Undervalued
            elif 1 <= pb_ratio < 3:
                score += 15  # Fair value
            elif 3 <= pb_ratio < 5:
                score += 5  # Slightly expensive
            
            # Dividend Yield (25 points)
            dividend_yield = info.get('dividendYield', 0)
            if dividend_yield > 0.04:
                score += 25  # Good dividend
            elif dividend_yield > 0.02:
                score += 15  # Moderate dividend
            elif dividend_yield > 0:
                score += 5  # Some dividend
            
            return min(score, 100)
            
        except Exception as e:
            logger.debug(f"Error calculating value score: {e}")
            return 50
    
    def _get_recommendation(self, total_score: float) -> str:
        """Get recommendation based on total score"""
        if total_score >= 85:
            return "STRONG BUY - Add to watchlist immediately"
        elif total_score >= 75:
            return "BUY - Strong candidate for watchlist"
        elif total_score >= 70:
            return "CONSIDER - Worth monitoring"
        else:
            return "PASS - Not recommended at this time"
    
    def _get_reasons(self, tech: float, fund: float, mom: float, val: float) -> List[str]:
        """Get reasons for recommendation"""
        reasons = []
        
        if tech >= 75:
            reasons.append("Strong technical setup")
        if fund >= 75:
            reasons.append("Solid fundamentals")
        if mom >= 75:
            reasons.append("Positive momentum")
        if val >= 75:
            reasons.append("Good value")
        
        if not reasons:
            reasons.append("Balanced across all metrics")
        
        return reasons
