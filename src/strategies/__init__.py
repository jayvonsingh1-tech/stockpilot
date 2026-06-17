"""Strategies package"""
from .trend_following import TrendFollowingStrategy
from .mean_reversion import MeanReversionStrategy
from .breakout import BreakoutStrategy

__all__ = [
    'TrendFollowingStrategy',
    'MeanReversionStrategy',
    'BreakoutStrategy'
]
