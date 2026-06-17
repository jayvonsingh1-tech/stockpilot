"""
Helper utilities for StockPilot
"""
from datetime import datetime, time
from typing import Optional
import pytz


def is_market_open(market: str = "NYSE") -> bool:
    """
    Check if a market is currently open
    
    Args:
        market: Market code (NYSE, NASDAQ, LSE)
        
    Returns:
        True if market is open, False otherwise
    """
    now = datetime.now(pytz.UTC)
    
    # Market hours (in local timezone)
    market_hours = {
        "NYSE": {
            "timezone": "America/New_York",
            "open": time(9, 30),
            "close": time(16, 0),
            "days": [0, 1, 2, 3, 4]  # Monday-Friday
        },
        "NASDAQ": {
            "timezone": "America/New_York",
            "open": time(9, 30),
            "close": time(16, 0),
            "days": [0, 1, 2, 3, 4]
        },
        "LSE": {
            "timezone": "Europe/London",
            "open": time(8, 0),
            "close": time(16, 30),
            "days": [0, 1, 2, 3, 4]
        }
    }
    
    if market not in market_hours:
        return False
    
    config = market_hours[market]
    tz = pytz.timezone(config["timezone"])
    local_time = now.astimezone(tz)
    
    # Check if it's a trading day
    if local_time.weekday() not in config["days"]:
        return False
    
    # Check if within trading hours
    current_time = local_time.time()
    return config["open"] <= current_time <= config["close"]


def format_currency(value: float, currency: str = "USD") -> str:
    """
    Format a value as currency
    
    Args:
        value: Numeric value
        currency: Currency code (USD, GBP)
        
    Returns:
        Formatted currency string
    """
    symbols = {
        "USD": "$",
        "GBP": "£",
        "EUR": "€"
    }
    
    symbol = symbols.get(currency, currency)
    return f"{symbol}{value:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a value as percentage
    
    Args:
        value: Numeric value (e.g., 0.05 for 5%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def calculate_position_size(portfolio_value: float, risk_percent: float, 
                           entry_price: float, stop_loss: float) -> int:
    """
    Calculate position size based on risk management
    
    Args:
        portfolio_value: Total portfolio value
        risk_percent: Percentage of portfolio to risk (e.g., 0.02 for 2%)
        entry_price: Entry price per share
        stop_loss: Stop loss price per share
        
    Returns:
        Number of shares to buy
    """
    risk_amount = portfolio_value * risk_percent
    risk_per_share = abs(entry_price - stop_loss)
    
    if risk_per_share == 0:
        return 0
    
    shares = int(risk_amount / risk_per_share)
    return max(0, shares)


def calculate_risk_reward_ratio(entry: float, stop_loss: float, 
                                take_profit: float) -> float:
    """
    Calculate risk/reward ratio
    
    Args:
        entry: Entry price
        stop_loss: Stop loss price
        take_profit: Take profit price
        
    Returns:
        Risk/reward ratio
    """
    risk = abs(entry - stop_loss)
    reward = abs(take_profit - entry)
    
    if risk == 0:
        return 0
    
    return reward / risk


def get_market_for_ticker(ticker: str) -> str:
    """
    Determine market from ticker symbol
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Market code (LSE, NYSE, NASDAQ)
    """
    if ticker.endswith('.L'):
        return "LSE"
    else:
        # Default to NASDAQ for US stocks
        # In a real implementation, you'd query this from a database
        return "NASDAQ"


def validate_ticker(ticker: str) -> bool:
    """
    Validate ticker format
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if valid, False otherwise
    """
    if not ticker:
        return False
    
    # Basic validation
    ticker = ticker.upper()
    
    # LSE tickers end with .L
    if ticker.endswith('.L'):
        return len(ticker) > 2
    
    # US tickers are 1-5 characters
    return 1 <= len(ticker) <= 5


def truncate_string(text: str, max_length: int = 100, 
                    suffix: str = "...") -> str:
    """
    Truncate a string to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
