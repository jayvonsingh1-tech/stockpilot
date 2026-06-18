"""
Stock Screener - Finds new investment opportunities
Enhanced with persistent tracking and expanded universe
"""
from typing import Dict, List, Optional
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..data.fetcher import MarketDataFetcher
from ..analysis.technical import TechnicalAnalysis
from ..engine.screening_tracker import ScreeningTracker
from ..utils.logger import setup_logger
from ..utils.config import get_config


logger = setup_logger(__name__)


class StockScreener:
    """Screens stocks for investment opportunities with persistent tracking"""
    
    def __init__(self):
        """Initialize stock screener"""
        self.config = get_config()
        self.data_fetcher = MarketDataFetcher()
        self.ta = TechnicalAnalysis()
        self.tracker = ScreeningTracker()
        
        # Expanded stock universe - 150+ stocks
        self.us_stocks = [
            # Mega Cap Tech (15)
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'NVDA', 'TSLA', 'AMD', 'INTC',
            'CRM', 'ORCL', 'ADBE', 'CSCO', 'AVGO',
            
            # Finance & Payments (20)
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'V', 'MA', 'PYPL',
            'SPGI', 'CME', 'ICE', 'COF', 'USB', 'PNC', 'TFC', 'BK',
            
            # Healthcare & Pharma (20)
            'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT', 'MRK', 'LLY', 'BMY', 'AMGN',
            'DHR', 'CVS', 'CI', 'HUM', 'GILD', 'REGN', 'VRTX', 'ISRG', 'SYK', 'BSX',
            
            # Consumer & Retail (20)
            'WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'COST', 'LOW', 'DIS', 'NFLX',
            'TJX', 'ROST', 'BKNG', 'MAR', 'YUM', 'CMG', 'LULU', 'ULTA', 'DG', 'DLTR',
            
            # Industrial & Manufacturing (20)
            'BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'RTX', 'LMT', 'DE', 'EMR',
            'FDX', 'NSC', 'UNP', 'CSX', 'WM', 'RSG', 'ITW', 'ETN', 'PH', 'ROK',
            
            # Energy & Utilities (15)
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL',
            'NEE', 'DUK', 'SO', 'D', 'AEP',
            
            # Semiconductors & Hardware (15)
            'QCOM', 'TXN', 'ADI', 'MU', 'AMAT', 'LRCX', 'KLAC', 'MCHP', 'NXPI', 'MRVL',
            'ON', 'SWKS', 'QRVO', 'MPWR', 'ENTG',
            
            # Software & Cloud (15)
            'NOW', 'SNOW', 'DDOG', 'NET', 'ZS', 'CRWD', 'PANW', 'FTNT', 'WDAY', 'TEAM',
            'ZM', 'DOCU', 'TWLO', 'OKTA', 'VEEV',
            
            # Telecom & Media (10)
            'T', 'VZ', 'TMUS', 'CMCSA', 'CHTR', 'PARA', 'WBD', 'FOXA', 'NWSA', 'OMC',
            
            # Materials & Chemicals (10)
            'LIN', 'APD', 'ECL', 'SHW', 'DD', 'DOW', 'NEM', 'FCX', 'NUE', 'STLD'
        ]
        
        self.uk_stocks = [
            # FTSE 100 Major Stocks (30)
            'SHEL.L', 'AZN.L', 'HSBA.L', 'ULVR.L', 'BP.L', 'GSK.L', 'DGE.L', 'RIO.L',
            'LSEG.L', 'NG.L', 'REL.L', 'BARC.L', 'LLOY.L', 'VOD.L', 'TSCO.L', 'PRU.L',
            'BT-A.L', 'IMB.L', 'BATS.L', 'AAL.L', 'CRH.L', 'GLEN.L', 'BA.L', 'RKT.L',
            'EXPN.L', 'FLTR.L', 'INF.L', 'OCDO.L', 'SBRY.L', 'SSE.L'
        ]
    
    def screen_daily(self, max_results: int = 20, research_top: int = 5) -> Dict:
        """
        Run daily stock screen to find new opportunities with persistent tracking
        
        Args:
            max_results: Maximum number of stocks to screen and return
            research_top: Number of top stocks to research in detail
            
        Returns:
            Dictionary with screening results and tracking info
        """
        logger.info("=" * 60)
        logger.info("DAILY STOCK SCREENING - ENHANCED")
        logger.info("=" * 60)
        
        # Get previously tracked stocks
        active_performers = self.tracker.get_active_top_performers()
        monitoring_list = self.tracker.get_monitoring_list(days=30)
        
        logger.info(f"Active top performers: {len(active_performers)}")
        logger.info(f"Monitoring list: {len(monitoring_list)}")
        
        candidates = []
        total_stocks = len(self.us_stocks) + len(self.uk_stocks)
        all_tickers = self.us_stocks + self.uk_stocks
        
        # Screen stocks concurrently with rate limiting
        logger.info(f"Screening {total_stocks} stocks (US: {len(self.us_stocks)}, UK: {len(self.uk_stocks)})...")
        candidates = self._screen_concurrent(all_tickers, max_workers=5)
        
        # Sort by total score
        candidates.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Save all screening results
        self.tracker.save_screening_results(candidates)
        
        # Get top candidates
        top_candidates = candidates[:max_results]
        
        # Update top performers tracking
        self.tracker.update_top_performers(top_candidates)
        
        # Get updated active performers (may have changed)
        updated_active = self.tracker.get_active_top_performers()
        
        # Prepare result with tracking info
        result = {
            'new_opportunities': top_candidates[:research_top],  # Top N for detailed research
            'top_20': top_candidates,  # Top 20 for overview
            'active_top_10': updated_active,  # Currently tracked top performers
            'monitoring': monitoring_list[:10],  # Recently dropped from top 10
            'total_screened': len(candidates),
            'screening_date': datetime.now().strftime('%Y-%m-%d'),
            'statistics': self.tracker.get_statistics()
        }
        
        logger.info("=" * 60)
        logger.info(f"SCREENING COMPLETE:")
        logger.info(f"  • Total screened: {len(candidates)}")
        logger.info(f"  • New opportunities (for research): {len(result['new_opportunities'])}")
        logger.info(f"  • Active top 10: {len(updated_active)}")
        logger.info(f"  • Monitoring: {len(monitoring_list)}")
        logger.info("=" * 60)
        
        return result
    
    def _screen_concurrent(self, tickers: List[str], max_workers: int = 5) -> List[Dict]:
        """
        Screen stocks concurrently with rate limiting
        
        Args:
            tickers: List of tickers to screen
            max_workers: Maximum concurrent workers
            
        Returns:
            List of candidate stocks
        """
        candidates = []
        processed = 0
        total = len(tickers)
        
        def evaluate_with_delay(ticker: str) -> Optional[Dict]:
            """Evaluate stock with rate limiting delay"""
            time.sleep(0.3)  # Rate limiting: ~3 requests per second
            return self._evaluate_stock(ticker)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_ticker = {
                executor.submit(evaluate_with_delay, ticker): ticker
                for ticker in tickers
            }
            
            # Process completed tasks
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                processed += 1
                
                # Progress update
                if processed % 10 == 0:
                    logger.info(f"Progress: {processed}/{total} stocks ({(processed/total)*100:.1f}%)")
                
                try:
                    score = future.result(timeout=30)  # 30 second timeout per stock
                    if score and score['total_score'] >= 70:
                        candidates.append(score)
                        logger.info(f"✓ {ticker}: {score['total_score']:.1f}/100 - {score['recommendation']}")
                except Exception as e:
                    logger.debug(f"Error screening {ticker}: {e}")
        
        logger.info(f"Screening complete: {len(candidates)} candidates found")
        return candidates
    
    def _evaluate_stock(self, ticker: str) -> Optional[Dict]:
        """
        Evaluate a stock across multiple dimensions
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Dictionary with scores or None
        """
        try:
            # Fetch data with timeout protection
            df = self.data_fetcher.fetch_ohlcv(ticker, period='6mo', interval='1d')
            if df is None or len(df) < 100:
                logger.debug(f"Insufficient data for {ticker}: {len(df) if df is not None else 0} candles")
                return None
            
            # Get full stock info from yfinance with timeout protection
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
            except Exception as e:
                logger.debug(f"Error fetching info for {ticker}: {e}")
                return None
            
            if not info or 'longName' not in info:
                logger.debug(f"No info available for {ticker}")
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
            if len(df) < 200:
                logger.debug(f"Insufficient data for full technical analysis: {len(df)} candles")
                return score
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
