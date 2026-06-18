"""
Utility functions for error handling and retry logic
"""
import time
import functools
from typing import Callable, Any, Optional
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry a function on failure with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {e}"
                        )
            
            # If all retries failed, raise the last exception
            raise last_exception
        
        return wrapper
    return decorator


def safe_execute(func: Callable, default: Any = None, log_error: bool = True) -> Any:
    """
    Safely execute a function and return default value on error
    
    Args:
        func: Function to execute
        default: Default value to return on error
        log_error: Whether to log errors
        
    Returns:
        Function result or default value
    """
    try:
        return func()
    except Exception as e:
        if log_error:
            logger.error(f"Error in {func.__name__}: {e}")
        return default


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds before attempting to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == "open":
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = "half-open"
                logger.info(f"Circuit breaker for {func.__name__} entering half-open state")
            else:
                raise Exception(f"Circuit breaker open for {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
                logger.info(f"Circuit breaker for {func.__name__} closed")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error(
                    f"Circuit breaker opened for {func.__name__} "
                    f"after {self.failure_count} failures"
                )
            
            raise e
    
    def reset(self):
        """Reset circuit breaker to closed state"""
        self.state = "closed"
        self.failure_count = 0
        self.last_failure_time = None
