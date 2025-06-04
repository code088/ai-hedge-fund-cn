from typing import TYPE_CHECKING, Any
import importlib

if TYPE_CHECKING:
    from src.tools import api, api_cn

def is_china_stock(ticker: str) -> bool:
    """Check if the ticker is a Chinese stock."""
    if not ticker.count('.') == 1:
        return False
    suffix = ticker.split('.')[1]
    return suffix in ['SH', 'SZ']

def get_api_module(ticker: str):
    """Get the appropriate API module based on the ticker."""
    if is_china_stock(ticker):
        return importlib.import_module('src.tools.api_cn')
    return importlib.import_module('src.tools.api')

# Create a proxy class to handle all API calls
class APIProxy:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self._api_module = get_api_module(ticker)

    def __getattr__(self, name: str) -> Any:
        """Dynamically get attributes from the appropriate API module."""
        return getattr(self._api_module, name)

# Create a function to get the API proxy
def get_api(ticker: str) -> APIProxy:
    """Get an API proxy for the given ticker."""
    return APIProxy(ticker)

# Export commonly used functions for convenience
def get_prices(ticker: str, *args, **kwargs):
    """Get prices using the appropriate API."""
    return get_api(ticker).get_prices(ticker, *args, **kwargs)

def get_financial_metrics(ticker: str, *args, **kwargs):
    """Get financial metrics using the appropriate API."""
    return get_api(ticker).get_financial_metrics(ticker, *args, **kwargs)

def get_price_data(ticker: str, *args, **kwargs):
    """Get price data using the appropriate API."""
    return get_api(ticker).get_price_data(ticker, *args, **kwargs)

def get_market_cap(ticker: str, *args, **kwargs):
    """Get market cap using the appropriate API."""
    return get_api(ticker).get_market_cap(ticker, *args, **kwargs)

def get_insider_trades(ticker: str, *args, **kwargs):
    """Get insider trades using the appropriate API."""
    return get_api(ticker).get_insider_trades(ticker, *args, **kwargs)

def get_company_news(ticker: str, *args, **kwargs):
    """Get company news using the appropriate API."""
    return get_api(ticker).get_company_news(ticker, *args, **kwargs)

def search_line_items(ticker: str, *args, **kwargs):
    """Search line items using the appropriate API."""
    return get_api(ticker).search_line_items(ticker, *args, **kwargs)

def prices_to_df(prices, *args, **kwargs):
    """Convert prices to DataFrame using the appropriate API (US or CN)."""
    # Use the first ticker to determine the API
    if not prices:
        import pandas as pd
        return pd.DataFrame()
    # Try to get ticker from the first Price object
    ticker = getattr(prices[0], 'ticker', None)
    if ticker is None and hasattr(prices[0], 'model_fields') and 'ticker' in prices[0].model_fields:
        ticker = prices[0].ticker
    # fallback: just use US API's prices_to_df
    if ticker and is_china_stock(ticker):
        return get_api(ticker).prices_to_df(prices, *args, **kwargs)
    else:
        from src.tools import api
        return api.prices_to_df(prices, *args, **kwargs) 