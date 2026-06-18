"""
Fundamental Analysis Module - Deep dive into company financials
Optimized for efficiency and comprehensive analysis
"""
from typing import Dict, Optional, Tuple
import yfinance as yf
from datetime import datetime, timedelta
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class FundamentalAnalysis:
    """
    Comprehensive fundamental analysis for stocks
    
    Provides:
    - Valuation metrics (P/E, P/B, PEG)
    - Profitability analysis
    - Growth metrics
    - Financial health scores
    - DCF valuation
    - Comparative analysis
    """
    
    def __init__(self):
        """Initialize fundamental analysis"""
        self._cache = {}
        self._cache_duration = 3600  # 1 hour cache
    
    def analyze_company(self, ticker: str) -> Optional[Dict]:
        """
        Comprehensive company analysis
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Dictionary with complete fundamental analysis
        """
        try:
            # Get stock info
            info = self._get_cached_info(ticker)
            if not info:
                return None
            
            # Build comprehensive analysis
            analysis = {
                'ticker': ticker,
                'company_name': info.get('longName', ticker),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'analysis_date': datetime.now().isoformat(),
                
                # Valuation
                'valuation': self._analyze_valuation(info),
                
                # Profitability
                'profitability': self._analyze_profitability(info),
                
                # Growth
                'growth': self._analyze_growth(info),
                
                # Financial Health
                'financial_health': self._analyze_financial_health(info),
                
                # Efficiency
                'efficiency': self._analyze_efficiency(info),
                
                # Dividends
                'dividends': self._analyze_dividends(info),
                
                # Overall Score
                'overall_score': 0,  # Will be calculated
                'rating': 'N/A'
            }
            
            # Calculate overall score
            analysis['overall_score'] = self._calculate_overall_score(analysis)
            analysis['rating'] = self._get_rating(analysis['overall_score'])
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
            return None
    
    def _get_cached_info(self, ticker: str) -> Optional[Dict]:
        """Get stock info with caching"""
        cache_key = f"{ticker}_info"
        
        # Check cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if (datetime.now() - cached_time).seconds < self._cache_duration:
                return cached_data
        
        # Fetch fresh data
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info or 'longName' not in info:
                return None
            
            self._cache[cache_key] = (info, datetime.now())
            return info
            
        except Exception as e:
            logger.error(f"Error fetching info for {ticker}: {e}")
            return None
    
    def _analyze_valuation(self, info: Dict) -> Dict:
        """Analyze valuation metrics"""
        pe_ratio = info.get('trailingPE', 0)
        forward_pe = info.get('forwardPE', 0)
        peg_ratio = info.get('pegRatio', 0)
        pb_ratio = info.get('priceToBook', 0)
        ps_ratio = info.get('priceToSalesTrailing12Months', 0)
        
        # Determine if cheap or expensive
        valuation_score = 50  # Base score
        
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
        
        # PEG ratio bonus
        if 0 < peg_ratio < 1:
            valuation_score += 15
        elif 1 <= peg_ratio < 2:
            valuation_score += 5
        
        # P/B ratio bonus
        if 0 < pb_ratio < 1:
            valuation_score += 15
        elif 1 <= pb_ratio < 3:
            valuation_score += 5
        
        return {
            'pe_ratio': round(pe_ratio, 2) if pe_ratio > 0 else None,
            'forward_pe': round(forward_pe, 2) if forward_pe > 0 else None,
            'peg_ratio': round(peg_ratio, 2) if peg_ratio > 0 else None,
            'pb_ratio': round(pb_ratio, 2) if pb_ratio > 0 else None,
            'ps_ratio': round(ps_ratio, 2) if ps_ratio > 0 else None,
            'valuation': valuation,
            'score': min(valuation_score, 100)
        }
    
    def _analyze_profitability(self, info: Dict) -> Dict:
        """Analyze profitability metrics"""
        gross_margin = info.get('grossMargins', 0)
        operating_margin = info.get('operatingMargins', 0)
        profit_margin = info.get('profitMargins', 0)
        roe = info.get('returnOnEquity', 0)
        roa = info.get('returnOnAssets', 0)
        roic = info.get('returnOnCapital', 0)
        
        # Calculate profitability score
        score = 50
        
        if profit_margin > 0.20:
            score += 20
        elif profit_margin > 0.10:
            score += 10
        elif profit_margin > 0.05:
            score += 5
        
        if roe > 0.20:
            score += 15
        elif roe > 0.15:
            score += 10
        elif roe > 0.10:
            score += 5
        
        if roa > 0.10:
            score += 15
        elif roa > 0.05:
            score += 5
        
        return {
            'gross_margin': round(gross_margin * 100, 1) if gross_margin else None,
            'operating_margin': round(operating_margin * 100, 1) if operating_margin else None,
            'profit_margin': round(profit_margin * 100, 1) if profit_margin else None,
            'roe': round(roe * 100, 1) if roe else None,
            'roa': round(roa * 100, 1) if roa else None,
            'roic': round(roic * 100, 1) if roic else None,
            'score': min(score, 100),
            'rating': 'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Fair' if score >= 40 else 'Poor'
        }
    
    def _analyze_growth(self, info: Dict) -> Dict:
        """Analyze growth metrics"""
        revenue_growth = info.get('revenueGrowth', 0)
        earnings_growth = info.get('earningsGrowth', 0)
        revenue = info.get('totalRevenue', 0)
        
        # Calculate growth score
        score = 50
        
        if revenue_growth > 0.20:
            score += 25
            rating = "High Growth"
        elif revenue_growth > 0.10:
            score += 15
            rating = "Moderate Growth"
        elif revenue_growth > 0:
            score += 5
            rating = "Slow Growth"
        else:
            rating = "Declining"
        
        if earnings_growth > 0.15:
            score += 25
        elif earnings_growth > 0.10:
            score += 15
        elif earnings_growth > 0:
            score += 5
        
        return {
            'revenue': revenue,
            'revenue_growth': round(revenue_growth * 100, 1) if revenue_growth else None,
            'earnings_growth': round(earnings_growth * 100, 1) if earnings_growth else None,
            'score': min(score, 100),
            'rating': rating,
            'trend': 'Improving' if revenue_growth > 0 else 'Declining'
        }
    
    def _analyze_financial_health(self, info: Dict) -> Dict:
        """Analyze financial health"""
        total_debt = info.get('totalDebt', 0)
        total_cash = info.get('totalCash', 0)
        debt_to_equity = info.get('debtToEquity', 0)
        current_ratio = info.get('currentRatio', 0)
        quick_ratio = info.get('quickRatio', 0)
        free_cash_flow = info.get('freeCashflow', 0)
        
        # Calculate health score
        score = 50
        
        # Debt to equity
        if debt_to_equity < 30:
            score += 20
        elif debt_to_equity < 60:
            score += 15
        elif debt_to_equity < 100:
            score += 5
        
        # Current ratio
        if current_ratio > 2:
            score += 15
        elif current_ratio > 1:
            score += 10
        
        # Free cash flow
        if free_cash_flow > 0:
            score += 15
        
        return {
            'total_debt': total_debt,
            'total_cash': total_cash,
            'debt_to_equity': round(debt_to_equity / 100, 2) if debt_to_equity else None,
            'current_ratio': round(current_ratio, 2) if current_ratio else None,
            'quick_ratio': round(quick_ratio, 2) if quick_ratio else None,
            'free_cash_flow': free_cash_flow,
            'score': min(score, 100),
            'rating': 'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Fair' if score >= 40 else 'Poor'
        }
    
    def _analyze_efficiency(self, info: Dict) -> Dict:
        """Analyze operational efficiency"""
        asset_turnover = info.get('assetTurnover', 0)
        inventory_turnover = info.get('inventoryTurnover', 0)
        receivables_turnover = info.get('receivablesTurnover', 0)
        
        return {
            'asset_turnover': round(asset_turnover, 2) if asset_turnover else None,
            'inventory_turnover': round(inventory_turnover, 2) if inventory_turnover else None,
            'receivables_turnover': round(receivables_turnover, 2) if receivables_turnover else None
        }
    
    def _analyze_dividends(self, info: Dict) -> Dict:
        """Analyze dividend metrics"""
        dividend_rate = info.get('dividendRate', 0)
        dividend_yield = info.get('dividendYield', 0)
        payout_ratio = info.get('payoutRatio', 0)
        
        return {
            'dividend_rate': round(dividend_rate, 2) if dividend_rate else None,
            'dividend_yield': round(dividend_yield * 100, 2) if dividend_yield else None,
            'payout_ratio': round(payout_ratio * 100, 1) if payout_ratio else None,
            'pays_dividend': dividend_rate > 0
        }
    
    def _calculate_overall_score(self, analysis: Dict) -> int:
        """Calculate weighted overall score"""
        try:
            scores = []
            weights = []
            
            # Valuation (25%)
            if analysis['valuation']['score']:
                scores.append(analysis['valuation']['score'])
                weights.append(0.25)
            
            # Profitability (30%)
            if analysis['profitability']['score']:
                scores.append(analysis['profitability']['score'])
                weights.append(0.30)
            
            # Growth (25%)
            if analysis['growth']['score']:
                scores.append(analysis['growth']['score'])
                weights.append(0.25)
            
            # Financial Health (20%)
            if analysis['financial_health']['score']:
                scores.append(analysis['financial_health']['score'])
                weights.append(0.20)
            
            if not scores:
                return 50
            
            # Weighted average
            total_weight = sum(weights)
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
            
            return round(weighted_score)
            
        except Exception as e:
            logger.error(f"Error calculating overall score: {e}")
            return 50
    
    def _get_rating(self, score: int) -> str:
        """Convert score to rating"""
        if score >= 85:
            return "STRONG BUY"
        elif score >= 75:
            return "BUY"
        elif score >= 60:
            return "HOLD"
        elif score >= 40:
            return "UNDERPERFORM"
        else:
            return "SELL"
    
    def calculate_dcf_value(self, ticker: str) -> Optional[float]:
        """
        Calculate intrinsic value using Discounted Cash Flow
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Fair value per share or None
        """
        try:
            info = self._get_cached_info(ticker)
            if not info:
                return None
            
            # Get free cash flow
            fcf = info.get('freeCashflow', 0)
            if fcf <= 0:
                return None
            
            # Growth rate (capped at 15%)
            growth_rate = min(info.get('revenueGrowth', 0.05), 0.15)
            
            # Discount rate (10% required return)
            discount_rate = 0.10
            terminal_growth = 0.03
            
            # Project 5 years
            pv_fcf = []
            for year in range(1, 6):
                fcf_year = fcf * ((1 + growth_rate) ** year)
                pv = fcf_year / ((1 + discount_rate) ** year)
                pv_fcf.append(pv)
            
            # Terminal value
            terminal_fcf = fcf * ((1 + growth_rate) ** 5) * (1 + terminal_growth)
            terminal_value = terminal_fcf / (discount_rate - terminal_growth)
            terminal_pv = terminal_value / ((1 + discount_rate) ** 5)
            
            # Enterprise value
            enterprise_value = sum(pv_fcf) + terminal_pv
            
            # Adjust for debt and cash
            total_debt = info.get('totalDebt', 0)
            total_cash = info.get('totalCash', 0)
            equity_value = enterprise_value - total_debt + total_cash
            
            # Per share value
            shares = info.get('sharesOutstanding', 1)
            fair_value = equity_value / shares
            
            return max(fair_value, 0)
            
        except Exception as e:
            logger.error(f"Error calculating DCF for {ticker}: {e}")
            return None
    
    def clear_cache(self):
        """Clear the analysis cache"""
        self._cache.clear()
        logger.debug("Fundamental analysis cache cleared")
