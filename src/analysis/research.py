"""
Research Report Generator - Creates detailed company analysis reports
"""
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from ..data.fetcher import MarketDataFetcher
from ..analysis.technical import TechnicalAnalysis
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class ResearchReportGenerator:
    """Generates comprehensive company research reports"""
    
    def __init__(self):
        """Initialize research report generator"""
        self.data_fetcher = MarketDataFetcher()
        self.ta = TechnicalAnalysis()
    
    def generate_report(self, ticker: str) -> Optional[Dict]:
        """
        Generate comprehensive research report for a stock
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Dictionary with research report or None
        """
        try:
            logger.info(f"Generating research report for {ticker}...")
            
            # Fetch data
            df = self.data_fetcher.fetch_ohlcv(ticker, period='1y', interval='1d')
            if df is None or len(df) < 100:
                logger.warning(f"Insufficient price data for {ticker}")
                return None
            
            # Get full stock info from yfinance
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info or 'longName' not in info:
                logger.warning(f"No company info available for {ticker}")
                return None
            
            # Build report sections
            report = {
                'ticker': ticker,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'overview': self._generate_overview(info),
                'financial_health': self._analyze_financial_health(info),
                'valuation': self._analyze_valuation(info),
                'growth': self._analyze_growth(info),
                'technical_setup': self._analyze_technical_setup(df, info),
                'upcoming_events': self._get_upcoming_events(info),
                'news_summary': self._get_news_summary(ticker),
                'insider_activity': self._get_insider_activity(info),
                'risk_factors': self._identify_risk_factors(info, df),
                'bot_assessment': self._generate_bot_assessment(info, df)
            }
            
            logger.info(f"Research report generated for {ticker}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating research report for {ticker}: {e}")
            return None
    
    def _generate_overview(self, info: Dict) -> Dict:
        """Generate company overview section"""
        return {
            'name': info.get('longName', 'Unknown'),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'market_cap': info.get('marketCap', 0),
            'employees': info.get('fullTimeEmployees', 0),
            'description': info.get('longBusinessSummary', 'No description available')[:300] + '...',
            'website': info.get('website', 'N/A'),
            'country': info.get('country', 'Unknown')
        }
    
    def _analyze_financial_health(self, info: Dict) -> Dict:
        """Analyze financial health"""
        revenue = info.get('totalRevenue', 0)
        profit = info.get('netIncomeToCommon', 0)
        debt = info.get('totalDebt', 0)
        cash = info.get('totalCash', 0)
        
        # Calculate health score
        health_score = 50
        
        # Profit margin
        profit_margin = info.get('profitMargins', 0)
        if profit_margin > 0.20:
            health_score += 20
        elif profit_margin > 0.10:
            health_score += 10
        
        # Debt to equity
        debt_to_equity = info.get('debtToEquity', 100)
        if debt_to_equity < 50:
            health_score += 15
        elif debt_to_equity < 100:
            health_score += 7
        
        # Current ratio
        current_ratio = info.get('currentRatio', 1)
        if current_ratio > 2:
            health_score += 15
        elif current_ratio > 1:
            health_score += 7
        
        return {
            'revenue': revenue,
            'profit': profit,
            'debt': debt,
            'cash': cash,
            'profit_margin': profit_margin,
            'debt_to_equity': debt_to_equity,
            'current_ratio': current_ratio,
            'health_score': min(health_score, 100),
            'health_rating': self._get_health_rating(health_score)
        }
    
    def _analyze_valuation(self, info: Dict) -> Dict:
        """Analyze valuation metrics"""
        pe_ratio = info.get('trailingPE', 0)
        pb_ratio = info.get('priceToBook', 0)
        ps_ratio = info.get('priceToSalesTrailing12Months', 0)
        peg_ratio = info.get('pegRatio', 0)
        
        # Determine if cheap or expensive
        valuation_score = 50
        
        if 0 < pe_ratio < 15:
            valuation_score += 20
            valuation = "Undervalued"
        elif 15 <= pe_ratio < 25:
            valuation_score += 10
            valuation = "Fair Value"
        elif 25 <= pe_ratio < 40:
            valuation = "Slightly Expensive"
        else:
            valuation = "Expensive"
        
        return {
            'pe_ratio': pe_ratio,
            'pb_ratio': pb_ratio,
            'ps_ratio': ps_ratio,
            'peg_ratio': peg_ratio,
            'valuation_score': valuation_score,
            'valuation': valuation,
            'vs_sector': self._compare_to_sector(info)
        }
    
    def _analyze_growth(self, info: Dict) -> Dict:
        """Analyze growth metrics"""
        revenue_growth = info.get('revenueGrowth', 0)
        earnings_growth = info.get('earningsGrowth', 0)
        
        growth_score = 50
        
        if revenue_growth > 0.20:
            growth_score += 25
            growth_rating = "High Growth"
        elif revenue_growth > 0.10:
            growth_score += 15
            growth_rating = "Moderate Growth"
        elif revenue_growth > 0:
            growth_score += 5
            growth_rating = "Slow Growth"
        else:
            growth_rating = "Declining"
        
        return {
            'revenue_growth': revenue_growth,
            'earnings_growth': earnings_growth,
            'growth_score': growth_score,
            'growth_rating': growth_rating,
            'trend': 'Improving' if revenue_growth > 0 else 'Declining'
        }
    
    def _analyze_technical_setup(self, df: pd.DataFrame, info: Dict) -> Dict:
        """Analyze technical setup"""
        try:
            current_price = df['Close'].iloc[-1]
            
            # Calculate indicators
            ema20 = self.ta.calculate_ema(df, 20)
            ema50 = self.ta.calculate_ema(df, 50)
            sma200 = self.ta.calculate_sma(df, 200)
            rsi = self.ta.calculate_rsi(df)
            
            ema20_val = ema20.iloc[-1] if not ema20.empty else 0
            ema50_val = ema50.iloc[-1] if not ema50.empty else 0
            sma200_val = sma200.iloc[-1] if not sma200.empty else 0
            rsi_val = rsi.iloc[-1] if not rsi.empty else 50
            
            # Determine trend
            if current_price > ema20_val > ema50_val > sma200_val:
                trend = "Strong Uptrend"
            elif current_price > ema50_val > sma200_val:
                trend = "Uptrend"
            elif current_price > sma200_val:
                trend = "Weak Uptrend"
            elif current_price < sma200_val:
                trend = "Downtrend"
            else:
                trend = "Sideways"
            
            # Key levels
            recent_high = df['High'].tail(60).max()
            recent_low = df['Low'].tail(60).min()
            
            return {
                'current_price': current_price,
                'trend': trend,
                'rsi': rsi_val,
                'ema20': ema20_val,
                'ema50': ema50_val,
                'sma200': sma200_val,
                'support': recent_low,
                'resistance': recent_high,
                'position': self._get_position_in_range(current_price, recent_low, recent_high)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing technical setup: {e}")
            return {}
    
    def _get_upcoming_events(self, info: Dict) -> Dict:
        """Get upcoming events"""
        return {
            'earnings_date': info.get('earningsDate', 'Unknown'),
            'ex_dividend_date': info.get('exDividendDate', 'N/A'),
            'dividend_rate': info.get('dividendRate', 0),
            'dividend_yield': info.get('dividendYield', 0)
        }
    
    def _get_news_summary(self, ticker: str) -> str:
        """Get news summary (placeholder)"""
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if news and len(news) > 0:
                latest = news[0]
                return f"Latest: {latest.get('title', 'No title')} - {latest.get('publisher', 'Unknown')}"
            return "No recent news available"
        except Exception as e:
            logger.debug(f"Error fetching news for {ticker}: {e}")
            return "News unavailable"
    
    def _get_insider_activity(self, info: Dict) -> str:
        """Get insider activity (placeholder)"""
        try:
            # Check for insider ownership
            insider_percent = info.get('heldPercentInsiders', 0)
            institutional_percent = info.get('heldPercentInstitutions', 0)
            
            if insider_percent > 0 or institutional_percent > 0:
                return f"Insiders: {insider_percent*100:.1f}%, Institutions: {institutional_percent*100:.1f}%"
            return "No insider data available"
        except Exception as e:
            logger.debug(f"Error getting insider activity: {e}")
            return "Insider data unavailable"
    
    def _identify_risk_factors(self, info: Dict, df: pd.DataFrame) -> List[str]:
        """Identify risk factors"""
        risks = []
        
        # High debt
        debt_to_equity = info.get('debtToEquity', 0)
        if debt_to_equity > 100:
            risks.append(f"High debt levels (D/E: {debt_to_equity:.1f})")
        
        # Negative growth
        revenue_growth = info.get('revenueGrowth', 0)
        if revenue_growth < 0:
            risks.append(f"Declining revenue ({revenue_growth*100:.1f}%)")
        
        # High volatility
        volatility = df['Close'].pct_change().std() * 100
        if volatility > 3:
            risks.append(f"High price volatility ({volatility:.1f}%)")
        
        # Expensive valuation
        pe_ratio = info.get('trailingPE', 0)
        if pe_ratio > 40:
            risks.append(f"High P/E ratio ({pe_ratio:.1f})")
        
        if not risks:
            risks.append("No major risks identified")
        
        return risks
    
    def _generate_bot_assessment(self, info: Dict, df: pd.DataFrame) -> Dict:
        """Generate bot's overall assessment"""
        # Calculate overall score
        scores = []
        
        # Financial health
        profit_margin = info.get('profitMargins', 0)
        if profit_margin > 0.10:
            scores.append(75)
        else:
            scores.append(50)
        
        # Growth
        revenue_growth = info.get('revenueGrowth', 0)
        if revenue_growth > 0.10:
            scores.append(80)
        elif revenue_growth > 0:
            scores.append(60)
        else:
            scores.append(40)
        
        # Valuation
        pe_ratio = info.get('trailingPE', 0)
        if 0 < pe_ratio < 20:
            scores.append(85)
        elif 20 <= pe_ratio < 30:
            scores.append(70)
        else:
            scores.append(50)
        
        overall_score = sum(scores) / len(scores) if scores else 50
        
        # Generate recommendation
        if overall_score >= 80:
            recommendation = "STRONG BUY"
            action = "Add to watchlist immediately and consider for next trade"
        elif overall_score >= 70:
            recommendation = "BUY"
            action = "Add to watchlist for monitoring"
        elif overall_score >= 60:
            recommendation = "HOLD/WATCH"
            action = "Monitor but don't add to watchlist yet"
        else:
            recommendation = "AVOID"
            action = "Not recommended at this time"
        
        return {
            'overall_score': round(overall_score, 1),
            'recommendation': recommendation,
            'action': action,
            'confidence': round(overall_score, 0)
        }
    
    def _get_health_rating(self, score: int) -> str:
        """Get health rating from score"""
        if score >= 80:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Fair"
        else:
            return "Poor"
    
    def _compare_to_sector(self, info: Dict) -> str:
        """Compare valuation to sector (placeholder)"""
        # TODO: Implement sector comparison
        return "Sector comparison coming soon"
    
    def _get_position_in_range(self, price: float, low: float, high: float) -> str:
        """Get position in range"""
        if high == low:
            return "N/A"
        
        position = ((price - low) / (high - low)) * 100
        
        if position < 25:
            return "Near support (bottom 25%)"
        elif position < 50:
            return "Below midpoint"
        elif position < 75:
            return "Above midpoint"
        else:
            return "Near resistance (top 25%)"
