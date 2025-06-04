import datetime
import os
import pandas as pd
import tushare as ts

from src.data.cache import get_cache
from src.data.models import (
    CompanyNews,
    CompanyNewsResponse,
    FinancialMetrics,
    FinancialMetricsResponse,
    Price,
    PriceResponse,
    LineItem,
    LineItemResponse,
    InsiderTrade,
    InsiderTradeResponse,
    CompanyFactsResponse,
)

# Initialize Tushare
ts.set_token(os.getenv("TUSHARE_TOKEN"))
pro = ts.pro_api()

# Global cache instance
_cache = get_cache()

def format_date(date_str: str) -> str:
    """Convert date from YYYY-MM-DD to YYYYMMDD format for Tushare."""
    return date_str.replace("-", "")

def format_date_back(date_str: str) -> str:
    """Convert date from YYYYMMDD to YYYY-MM-DD format."""
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

def get_prices(ticker: str, start_date: str, end_date: str) -> list[Price]:
    """Fetch price data from Tushare."""
    # Create a cache key that includes all parameters to ensure exact matches
    cache_key = f"{ticker}_{start_date}_{end_date}"
    
    # Check cache first - simple exact match
    if cached_data := _cache.get_prices(cache_key):
        return [Price(**price) for price in cached_data]

    # If not in cache, fetch from Tushare
    df = pro.daily(
        ts_code=ticker,
        start_date=format_date(start_date),
        end_date=format_date(end_date)
    )
    
    if df is None or df.empty:
        return []

    # Sort by trade date
    df = df.sort_values("trade_date")
    
    # Convert to Price objects
    prices = [
        Price(
            time=format_date_back(row["trade_date"]),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=int(round(row["vol"]))
        )
        for _, row in df.iterrows()
    ]

    # Cache the results
    _cache.set_prices(cache_key, [p.model_dump() for p in prices])
    return prices

def get_financial_metrics(ticker: str, end_date: str, period: str = "annual", limit: int = 5) -> pd.DataFrame:
    """Get financial metrics for a Chinese stock using Tushare's basic data APIs."""
    try:
        # Convert ticker format (e.g., 002357.SZ -> 002357)
        ts_code = ticker.split('.')[0]
        
        # Get basic financial data
        df_basic = pro.daily_basic(ts_code=ts_code, trade_date=end_date.replace('-', ''))
        if df_basic.empty:
            return pd.DataFrame()
            
        # Get income statement data
        df_income = pro.income(ts_code=ts_code, period=end_date.replace('-', '')[:6])
        if df_income.empty:
            return pd.DataFrame()
            
        # Get balance sheet data
        df_balance = pro.balancesheet(ts_code=ts_code, period=end_date.replace('-', '')[:6])
        if df_balance.empty:
            return pd.DataFrame()
            
        # Get cash flow data
        df_cashflow = pro.cashflow(ts_code=ts_code, period=end_date.replace('-', '')[:6])
        if df_cashflow.empty:
            return pd.DataFrame()
        
        # Combine all metrics
        metrics = {
            'market_cap': df_basic['total_mv'].iloc[0] * 10000,  # Convert to yuan
            'pe_ratio': df_basic['pe'].iloc[0],
            'pb_ratio': df_basic['pb'].iloc[0],
            'ps_ratio': df_basic['ps'].iloc[0],
            'revenue': df_income['revenue'].iloc[0],
            'net_income': df_income['n_income'].iloc[0],
            'total_assets': df_balance['total_assets'].iloc[0],
            'total_equity': df_balance['total_hldr_eqy_exc_min_int'].iloc[0],
            'operating_cash_flow': df_cashflow['n_cashflow_act'].iloc[0],
            'free_cash_flow': df_cashflow['free_cashflow'].iloc[0],
            'dividend_yield': df_basic['dv_ratio'].iloc[0],
            'debt_to_equity': df_balance['total_liab'].iloc[0] / df_balance['total_hldr_eqy_exc_min_int'].iloc[0] if df_balance['total_hldr_eqy_exc_min_int'].iloc[0] != 0 else 0,
            'current_ratio': df_balance['total_cur_assets'].iloc[0] / df_balance['total_cur_liab'].iloc[0] if df_balance['total_cur_liab'].iloc[0] != 0 else 0,
            'return_on_equity': df_income['n_income'].iloc[0] / df_balance['total_hldr_eqy_exc_min_int'].iloc[0] if df_balance['total_hldr_eqy_exc_min_int'].iloc[0] != 0 else 0,
            'profit_margin': df_income['n_income'].iloc[0] / df_income['revenue'].iloc[0] if df_income['revenue'].iloc[0] != 0 else 0
        }
        
        return pd.DataFrame([metrics])
        
    except Exception as e:
        print(f"Error fetching financial metrics for {ticker}: {str(e)}")
        return pd.DataFrame()

def search_line_items(
    ticker: str,
    line_items: list[str],
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
) -> list[LineItem]:
    """Tushare does not support direct line item search."""
    return []

def get_insider_trades(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 1000,
) -> list[InsiderTrade]:
    """Tushare does not support insider trades data."""
    return []

def get_company_news(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 1000,
) -> list[CompanyNews]:
    """Tushare does not support company news data."""
    return []

def get_market_cap(
    ticker: str,
    end_date: str,
) -> float | None:
    """Fetch market cap from Tushare."""
    try:
        # Get daily basic data which includes market cap
        df = pro.daily_basic(
            ts_code=ticker,
            trade_date=format_date(end_date),
            fields='ts_code,trade_date,total_mv'
        )
        
        if df is None or df.empty:
            return None
            
        return float(df.iloc[0]['total_mv']) * 10000  # Convert to actual market cap value
    except Exception as e:
        print(f"Error fetching market cap: {ticker} - {str(e)}")
        return None

def prices_to_df(prices: list[Price]) -> pd.DataFrame:
    """Convert prices to a DataFrame."""
    df = pd.DataFrame([p.model_dump() for p in prices])
    df["Date"] = pd.to_datetime(df["time"])
    df.set_index("Date", inplace=True)
    numeric_cols = ["open", "close", "high", "low", "volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.sort_index(inplace=True)
    return df

def get_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Get price data as DataFrame."""
    prices = get_prices(ticker, start_date, end_date)
    return prices_to_df(prices) 