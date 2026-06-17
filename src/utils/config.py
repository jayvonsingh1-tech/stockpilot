"""
Configuration loader for StockPilot
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List
import os


class Config:
    """Configuration manager for StockPilot"""
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize configuration manager
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self._settings = None
        self._watchlist = None
        self._strategies = None
        self._criteria = None
        
    def load_settings(self) -> Dict[str, Any]:
        """Load main settings from settings.yaml"""
        if self._settings is None:
            settings_path = self.config_dir / "settings.yaml"
            with open(settings_path, 'r') as f:
                self._settings = yaml.safe_load(f)
        return self._settings
    
    def load_watchlist(self) -> List[Dict[str, Any]]:
        """Load watchlist from watchlist.yaml"""
        if self._watchlist is None:
            watchlist_path = self.config_dir / "watchlist.yaml"
            with open(watchlist_path, 'r') as f:
                data = yaml.safe_load(f)
                self._watchlist = data.get('watchlist', [])
        return self._watchlist
    
    def load_strategies(self) -> Dict[str, Any]:
        """Load strategy configuration from strategies.yaml"""
        if self._strategies is None:
            strategies_path = self.config_dir / "strategies.yaml"
            with open(strategies_path, 'r') as f:
                self._strategies = yaml.safe_load(f)
        return self._strategies
    
    def load_criteria(self) -> Dict[str, Any]:
        """Load signal criteria from criteria.yaml"""
        if self._criteria is None:
            criteria_path = self.config_dir / "criteria.yaml"
            with open(criteria_path, 'r') as f:
                self._criteria = yaml.safe_load(f)
        return self._criteria
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value using dot notation
        
        Args:
            key: Setting key (e.g., 'signals.min_confidence')
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        settings = self.load_settings()
        keys = key.split('.')
        value = settings
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_watchlist_tickers(self) -> List[str]:
        """Get list of all tickers in watchlist"""
        watchlist = self.load_watchlist()
        return [stock['ticker'] for stock in watchlist]
    
    def get_telegram_config(self) -> Dict[str, Any]:
        """Get Telegram configuration"""
        settings = self.load_settings()
        return settings.get('telegram', {})
    
    def get_enabled_strategies(self) -> List[str]:
        """Get list of enabled strategy names"""
        strategies = self.load_strategies()
        enabled = []
        for name, config in strategies.items():
            if isinstance(config, dict) and config.get('enabled', False):
                enabled.append(name)
        return enabled
    
    def save_settings(self, settings: Dict[str, Any]):
        """
        Save settings back to file
        
        Args:
            settings: Settings dictionary to save
        """
        settings_path = self.config_dir / "settings.yaml"
        with open(settings_path, 'w') as f:
            yaml.dump(settings, f, default_flow_style=False, sort_keys=False)
        self._settings = settings
    
    def update_setting(self, key: str, value: Any):
        """
        Update a specific setting
        
        Args:
            key: Setting key using dot notation
            value: New value
        """
        settings = self.load_settings()
        keys = key.split('.')
        
        # Navigate to the parent dict
        current = settings
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the value
        current[keys[-1]] = value
        
        # Save back to file
        self.save_settings(settings)


# Global config instance
_config = None


def get_config(config_dir: str = "config") -> Config:
    """
    Get global configuration instance
    
    Args:
        config_dir: Directory containing configuration files
        
    Returns:
        Config instance
    """
    global _config
    if _config is None:
        # Determine the correct config directory path
        if os.path.exists(config_dir):
            _config = Config(config_dir)
        elif os.path.exists(f"stockpilot/{config_dir}"):
            _config = Config(f"stockpilot/{config_dir}")
        else:
            raise FileNotFoundError(f"Config directory not found: {config_dir}")
    return _config
