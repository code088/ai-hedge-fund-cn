import datetime
import os
import pandas as pd
import akshare as ak
import re

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

# Global cache instance
_cache = get_cache()

def normalize_field_name(field_name: str) -> str:
    """Normalize field names by removing special characters and converting to uppercase."""
    # Remove special characters and spaces
    normalized = re.sub(r'[^a-zA-Z0-9]', '', field_name)
    # Convert to uppercase
    return normalized.upper()

def find_matching_field(df: pd.DataFrame, target_field: str) -> str:
    """Find the matching field name in the DataFrame columns."""
    # 先直接匹配原始字段名
    if target_field in df.columns:
        return target_field
    # 再用 normalize 匹配
    normalized_target = normalize_field_name(target_field)
    for col in df.columns:
        if normalize_field_name(col) == normalized_target:
            return col
    # 如果都找不到，返回原始字段名
    return target_field

def format_date(date_str: str) -> str:
    """Convert date from YYYY-MM-DD to YYYYMMDD format."""
    return date_str.replace("-", "")

def format_date_back(date_str: str) -> str:
    """Convert date from YYYYMMDD to YYYY-MM-DD format."""
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

def get_prices(ticker: str, start_date: str, end_date: str) -> list[Price]:
    """Get historical prices for a Chinese stock"""
    try:
        stock_code = ticker.split('.')[0]
        # 修正日期格式
        start_date_fmt = start_date.replace('-', '')
        end_date_fmt = end_date.replace('-', '')
        df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date_fmt, end_date=end_date_fmt, adjust="qfq")
        print("[DEBUG] stock_zh_a_hist columns:", df.columns)
        print("[DEBUG] stock_zh_a_hist head:\n", df.head())
        
        # 自动识别字段名
        date_field = find_matching_field(df, '日期')
        open_field = find_matching_field(df, '开盘')
        high_field = find_matching_field(df, '最高')
        low_field = find_matching_field(df, '最低')
        close_field = find_matching_field(df, '收盘')
        volume_field = find_matching_field(df, '成交量')
        amount_field = find_matching_field(df, '成交额')
        print(f"[DEBUG] 字段映射: date={date_field}, open={open_field}, high={high_field}, low={low_field}, close={close_field}, volume={volume_field}, amount={amount_field}")
        
        prices = []
        for idx, row in df.iterrows():
            # 确保所有字段都转为字符串再转为 float/int
            date_str = str(row[date_field])
            open_raw = row[open_field]
            high_raw = row[high_field]
            low_raw = row[low_field]
            close_raw = row[close_field]
            volume_raw = row[volume_field]
            amount_raw = row[amount_field]
            print(f"[DEBUG] row {idx}: date={date_str}, open={open_raw}, high={high_raw}, low={low_raw}, close={close_raw}, volume={volume_raw}, amount={amount_raw}")
            open_val = float(str(open_raw))
            high_val = float(str(high_raw))
            low_val = float(str(low_raw))
            close_val = float(str(close_raw))
            volume_val = int(float(str(volume_raw)))
            amount_val = float(str(amount_raw))
            price = Price(
                date=date_str,
                open=open_val,
                high=high_val,
                low=low_val,
                close=close_val,
                volume=volume_val,
                amount=amount_val,
                time=date_str  # 使用相同的日期字符串
            )
            prices.append(price)
        return prices
    except Exception as e:
        print(f"Error fetching prices for {ticker}: {str(e)}")
        return []


def get_financial_metrics(ticker: str, end_date: str, period: str = "annual", limit: int = 5) -> list[FinancialMetrics]:
    try:
        stock_code = ticker.split('.')[0]

        # 获取财务报表
        income = ak.stock_profit_sheet_by_report_em(symbol=f"{stock_code}.SH")
        balance = ak.stock_balance_sheet_by_report_em(symbol=f"{stock_code}.SH")
        cash = ak.stock_cash_flow_sheet_by_report_em(symbol=f"{stock_code}.SH")
        market_df = ak.stock_zh_a_spot_em()

        if income.empty or balance.empty or cash.empty:
            return []

        latest_income = income.iloc[0]
        latest_balance = balance.iloc[0]
        latest_cash = cash.iloc[0]

        stock_info = market_df[market_df['代码'] == stock_code]
        market_cap = float(stock_info['总市值'].iloc[0]) if not stock_info.empty else None

        # 安全字段提取函数
        def safe(field, source):
            return float(source[field]) if field in source and source[field] not in ('--', None) else None

        def match(source, key):
            # 简化版映射查找，建议你自定义字段对照
            for col in source.keys():
                if key.lower() in col.lower():
                    return col
            return None

        # 基础字段提取
        revenue = safe(match(income, '营业总收入'), latest_income)
        net_profit = safe(match(income, '净利润'), latest_income)
        gross_profit = safe(match(income, '营业总收入'), latest_income) - safe(match(income, '营业总成本'), latest_income)
        gross_margin = gross_profit / revenue if revenue and gross_profit else None
        net_margin = net_profit / revenue if net_profit and revenue else None
        eps = safe(match(income, '基本每股收益'), latest_income)

        total_equity = safe(match(balance, '所有者权益合计'), latest_balance)
        total_assets = safe(match(balance, '资产总计'), latest_balance)
        current_liabilities = safe(match(balance, '流动负债合计'), latest_balance)
        cash_and_equivalents = safe(match(balance, '货币资金'), latest_balance)
        total_liabilities = safe(match(balance, '负债合计'), latest_balance)
        shares_outstanding = safe(match(balance, '股本'), latest_balance)
        book_value_per_share = total_equity / shares_outstanding if total_equity and shares_outstanding else None
        roe = net_profit / total_equity if net_profit and total_equity else None
        roic = net_profit / (total_assets - current_liabilities) if net_profit and total_assets and current_liabilities else None
        pe_ratio = market_cap / net_profit if market_cap and net_profit else None
        pb_ratio = market_cap / (book_value_per_share * shares_outstanding) if market_cap and book_value_per_share and shares_outstanding else None

        # Enterprise value 粗略估算
        enterprise_value = market_cap + total_liabilities - cash_and_equivalents if market_cap and total_liabilities and cash_and_equivalents else None

        # 自由现金流与收益率
        fcf = safe(match(cash, '自由现金流'), latest_cash)
        free_cash_flow_yield = fcf / market_cap if fcf and market_cap else None

        # 构建 FinancialMetrics 字段
        metrics = {
            'ticker': ticker,
            'report_period': end_date,
            'period': period,
            'currency': 'CNY',
            'market_cap': market_cap,
            'enterprise_value': enterprise_value,
            'price_to_earnings_ratio': pe_ratio,
            'price_to_book_ratio': pb_ratio,
            'free_cash_flow_yield': free_cash_flow_yield,
            'gross_margin': gross_margin,
            'net_margin': net_margin,
            'return_on_equity': roe,
            'return_on_invested_capital': roic,
            'earnings_per_share': eps,
            'book_value_per_share': book_value_per_share,
            'revenue': revenue,
            'net_income': net_profit,
        }

        full_data = {field: metrics.get(field, None) for field in FinancialMetrics.model_fields.keys()}
        return [FinancialMetrics(**full_data)]

    except Exception as e:
        print(f"[ERROR] Failed to get financial metrics for {ticker}: {e}")
        return []


def search_line_items(
    ticker: str,
    line_items: list[str],
    end_date: str,
    period: str = "annual",
    limit: int = 5,
) -> list[LineItem]:
    try:
        stock_code = ticker.split('.')[0]

        # 获取财报数据
        income = ak.stock_profit_sheet_by_report_em(symbol=f"{stock_code}.SH")
        balance = ak.stock_balance_sheet_by_report_em(symbol=f"{stock_code}.SH")
        cash = ak.stock_cash_flow_sheet_by_report_em(symbol=f"{stock_code}.SH")
        if income.empty or balance.empty or cash.empty:
            return []

        latest_income = income.iloc[0]
        latest_balance = balance.iloc[0]
        latest_cash = cash.iloc[0]

        # 所有字段集中到一起便于查找
        all_sources = [latest_income, latest_balance, latest_cash]

        result_fields = {}

        for item in line_items:
            value_found = None
            for df in all_sources:
                match = find_matching_field(df.to_frame().T, item)
                if match and match in df and df[match] not in ('--', None):
                    try:
                        value_found = float(df[match])
                        break
                    except:
                        continue
            result_fields[item] = value_found

        return [
            LineItem(
                ticker=ticker,
                report_period=end_date,
                period=period,
                currency="CNY",
                **result_fields
            )
        ]
    except Exception as e:
        print(f"[ERROR] Failed to search line items for {ticker}: {e}")
        return []


def get_insider_trades(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 1000,
) -> list[InsiderTrade]:
    """Akshare does not support insider trades data."""
    return []

def get_company_news(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 1000,
) -> list[CompanyNews]:
    """Akshare does not support company news data."""
    return []

def get_market_cap(ticker: str, end_date: str) -> float | None:
    """Fetch market cap from Akshare."""
    try:
        df = ak.stock_zh_a_spot_em()
        df = df[df["代码"] == ticker.split('.')[0]]
        if df.empty:
            return None
        return float(df["总市值"].values[0]) * 1e8  # 单位为亿元
    except Exception as e:
        print(f"[akshare] Market cap fetch error: {e}")
        return None

def prices_to_df(prices: list[Price]) -> pd.DataFrame:
    """Convert prices to a DataFrame."""
    df = pd.DataFrame([p.model_dump() for p in prices])
    # 使用 time 字段作为日期，因为 time 和 date 字段内容相同
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