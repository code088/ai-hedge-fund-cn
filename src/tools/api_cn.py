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

def get_financial_metrics(ticker: str, end_date: str, period: str = "annual", limit: int = 5) -> pd.DataFrame:
    """Get financial metrics for a Chinese stock"""
    try:
        # Convert ticker format (e.g., 600519.SH -> 600519)
        stock_code = ticker.split('.')[0]
        
        # Get financial reports from Akshare using Eastmoney APIs
        income_statement = ak.stock_profit_sheet_by_report_em(symbol=f"{stock_code}.SH")
        balance_sheet = ak.stock_balance_sheet_by_report_em(symbol=f"{stock_code}.SH")
        cash_flow = ak.stock_cash_flow_sheet_by_report_em(symbol=f"{stock_code}.SH")
        print("[DEBUG] income_statement columns:", income_statement.columns)
        print("[DEBUG] income_statement head:\n", income_statement.head())
        print("[DEBUG] balance_sheet columns:", balance_sheet.columns)
        print("[DEBUG] balance_sheet head:\n", balance_sheet.head())
        print("[DEBUG] cash_flow columns:", cash_flow.columns)
        print("[DEBUG] cash_flow head:\n", cash_flow.head())
        
        if income_statement.empty or balance_sheet.empty or cash_flow.empty:
            return pd.DataFrame()
            
        # Get market cap
        market_data = ak.stock_zh_a_spot_em()
        stock_info = market_data[market_data['代码'] == stock_code]
        market_cap = float(stock_info['总市值'].iloc[0]) if not stock_info.empty else None
        
        # Get latest data
        latest_income = income_statement.iloc[0]
        latest_balance = balance_sheet.iloc[0]
        latest_cash = cash_flow.iloc[0]
        
        # 打印所有可用的字段名，帮助调试
        print("\n[DEBUG] Available fields in income statement:", list(income_statement.columns))
        print("[DEBUG] Available fields in balance sheet:", list(balance_sheet.columns))
        print("[DEBUG] Available fields in cash flow:", list(cash_flow.columns))
        
        # 自动识别字段名
        sales_field = find_matching_field(income_statement, 'TOTAL_OPERATE_INCOME')
        net_profit_field = find_matching_field(income_statement, 'NETPROFIT')
        total_assets_field = find_matching_field(balance_sheet, 'TOTAL_ASSETS')
        total_equity_field = find_matching_field(balance_sheet, 'TOTAL_EQUITY')
        net_operate_cash_flow_field = find_matching_field(cash_flow, 'NETCASH_OPERATE')
        net_invest_cash_flow_field = find_matching_field(cash_flow, 'NETCASH_INVEST')
        net_finance_cash_flow_field = find_matching_field(cash_flow, 'NETCASH_FINANCE')
        basic_eps_field = find_matching_field(income_statement, 'BASIC_EPS')
        share_capital_field = find_matching_field(balance_sheet, 'SHARE_CAPITAL')
        dividend_per_share_field = find_matching_field(income_statement, 'DIVIDEND_PER_SHARE')
        operating_cost_field = find_matching_field(income_statement, 'TOTAL_OPERATE_COST')
        inventory_field = find_matching_field(balance_sheet, 'INVENTORY')
        accounts_receivable_field = find_matching_field(balance_sheet, 'ACCOUNTS_RECE')
        accounts_payable_field = find_matching_field(balance_sheet, 'ACCOUNTS_PAYABLE')
        operating_profit_field = find_matching_field(income_statement, 'OPERATE_PROFIT')
        financial_expense_field = find_matching_field(income_statement, 'FINANCE_EXPENSE')
        fixed_assets_field = find_matching_field(balance_sheet, 'FIXED_ASSET')
        total_current_assets_field = find_matching_field(balance_sheet, 'TOTAL_CURRENT_ASSETS')
        total_current_liabilities_field = find_matching_field(balance_sheet, 'TOTAL_CURRENT_LIAB')
        retained_earnings_field = find_matching_field(balance_sheet, 'UNASSIGN_RPOFIT')
        fixed_assets_purchase_field = find_matching_field(cash_flow, 'CONSTRUCT_LONG_ASSET')
        depreciation_field = find_matching_field(income_statement, 'FA_IR_DEPR')
        
        print("\n[DEBUG] Field mappings:")
        print(f"sales_field: {sales_field}")
        print(f"net_profit_field: {net_profit_field}")
        print(f"total_assets_field: {total_assets_field}")
        print(f"total_equity_field: {total_equity_field}")
        
        # Map indicators to metrics
        metrics = {
            'revenue': float(latest_income[sales_field]) if sales_field in latest_income else None,
            'net_income': float(latest_income[net_profit_field]) if net_profit_field in latest_income else None,
            'total_assets': float(latest_balance[total_assets_field]) if total_assets_field in latest_balance else None,
            'total_equity': float(latest_balance[total_equity_field]) if total_equity_field in latest_balance else None,
            'market_cap': market_cap,
            'pe_ratio': market_cap / float(latest_income[net_profit_field]) if market_cap and net_profit_field in latest_income and float(latest_income[net_profit_field]) > 0 else None,
            'return_on_equity': float(latest_income[net_profit_field]) / float(latest_balance[total_equity_field]) if net_profit_field in latest_income and total_equity_field in latest_balance and float(latest_balance[total_equity_field]) > 0 else None,
            'operating_cash_flow': float(latest_cash[net_operate_cash_flow_field]) if net_operate_cash_flow_field in latest_cash else None,
            'investing_cash_flow': float(latest_cash[net_invest_cash_flow_field]) if net_invest_cash_flow_field in latest_cash else None,
            'financing_cash_flow': float(latest_cash[net_finance_cash_flow_field]) if net_finance_cash_flow_field in latest_cash else None,
            'free_cash_flow': float(latest_cash[net_operate_cash_flow_field]) - float(latest_cash[net_invest_cash_flow_field]) if net_operate_cash_flow_field in latest_cash and net_invest_cash_flow_field in latest_cash else None,
            'eps': float(latest_income[basic_eps_field]) if basic_eps_field in latest_income else None,
            'book_value': float(latest_balance[total_equity_field]) / float(latest_balance[share_capital_field]) if total_equity_field in latest_balance and share_capital_field in latest_balance and float(latest_balance[share_capital_field]) > 0 else None,
            'pb_ratio': market_cap / (float(latest_balance[total_equity_field]) / float(latest_balance[share_capital_field])) if market_cap and total_equity_field in latest_balance and share_capital_field in latest_balance and float(latest_balance[share_capital_field]) > 0 else None,
            'dividend_yield': float(latest_income[dividend_per_share_field]) / float(latest_income[basic_eps_field]) if dividend_per_share_field in latest_income and basic_eps_field in latest_income and float(latest_income[basic_eps_field]) > 0 else None,
            'asset_turnover': float(latest_income[sales_field]) / float(latest_balance[total_assets_field]) if sales_field in latest_income and total_assets_field in latest_balance and float(latest_balance[total_assets_field]) > 0 else None,
            'inventory_turnover': float(latest_income[operating_cost_field]) / float(latest_balance[inventory_field]) if operating_cost_field in latest_income and inventory_field in latest_balance and float(latest_balance[inventory_field]) > 0 else None,
            'receivables_turnover': float(latest_income[sales_field]) / float(latest_balance[accounts_receivable_field]) if sales_field in latest_income and accounts_receivable_field in latest_balance and float(latest_balance[accounts_receivable_field]) > 0 else None,
            'days_sales_outstanding': 365 / (float(latest_income[sales_field]) / float(latest_balance[accounts_receivable_field])) if sales_field in latest_income and accounts_receivable_field in latest_balance and float(latest_balance[accounts_receivable_field]) > 0 else None,
            'days_inventory': 365 / (float(latest_income[operating_cost_field]) / float(latest_balance[inventory_field])) if operating_cost_field in latest_income and inventory_field in latest_balance and float(latest_balance[inventory_field]) > 0 else None,
            'days_payable': 365 / (float(latest_income[operating_cost_field]) / float(latest_balance[accounts_payable_field])) if operating_cost_field in latest_income and accounts_payable_field in latest_balance and float(latest_balance[accounts_payable_field]) > 0 else None,
            'cash_conversion_cycle': (365 / (float(latest_income[sales_field]) / float(latest_balance[accounts_receivable_field])) if sales_field in latest_income and accounts_receivable_field in latest_balance and float(latest_balance[accounts_receivable_field]) > 0 else 0) + 
                                   (365 / (float(latest_income[operating_cost_field]) / float(latest_balance[inventory_field])) if operating_cost_field in latest_income and inventory_field in latest_balance and float(latest_balance[inventory_field]) > 0 else 0) - 
                                   (365 / (float(latest_income[operating_cost_field]) / float(latest_balance[accounts_payable_field])) if operating_cost_field in latest_income and accounts_payable_field in latest_balance and float(latest_balance[accounts_payable_field]) > 0 else 0),
            'interest_coverage': float(latest_income[operating_profit_field]) / float(latest_income[financial_expense_field]) if operating_profit_field in latest_income and financial_expense_field in latest_income and float(latest_income[financial_expense_field]) > 0 else None,
            'fixed_asset_turnover': float(latest_income[sales_field]) / float(latest_balance[fixed_assets_field]) if sales_field in latest_income and fixed_assets_field in latest_balance and float(latest_balance[fixed_assets_field]) > 0 else None,
            'total_asset_turnover': float(latest_income[sales_field]) / float(latest_balance[total_assets_field]) if sales_field in latest_income and total_assets_field in latest_balance and float(latest_balance[total_assets_field]) > 0 else None,
            'equity_turnover': float(latest_income[sales_field]) / float(latest_balance[total_equity_field]) if sales_field in latest_income and total_equity_field in latest_balance and float(latest_balance[total_equity_field]) > 0 else None,
            'working_capital': float(latest_balance[total_current_assets_field]) - float(latest_balance[total_current_liabilities_field]) if total_current_assets_field in latest_balance and total_current_liabilities_field in latest_balance else None,
            'working_capital_turnover': float(latest_income[sales_field]) / (float(latest_balance[total_current_assets_field]) - float(latest_balance[total_current_liabilities_field])) if sales_field in latest_income and total_current_assets_field in latest_balance and total_current_liabilities_field in latest_balance and (float(latest_balance[total_current_assets_field]) - float(latest_balance[total_current_liabilities_field])) > 0 else None,
            'retained_earnings': float(latest_balance[retained_earnings_field]) if retained_earnings_field in latest_balance else None,
            'retained_earnings_to_equity': float(latest_balance[retained_earnings_field]) / float(latest_balance[total_equity_field]) if retained_earnings_field in latest_balance and total_equity_field in latest_balance and float(latest_balance[total_equity_field]) > 0 else None,
            'capital_expenditure': float(latest_cash[fixed_assets_purchase_field]) if fixed_assets_purchase_field in latest_cash else None,
            'capital_expenditure_to_operating_cash_flow': float(latest_cash[fixed_assets_purchase_field]) / float(latest_cash[net_operate_cash_flow_field]) if fixed_assets_purchase_field in latest_cash and net_operate_cash_flow_field in latest_cash and float(latest_cash[net_operate_cash_flow_field]) > 0 else None,
            'capital_expenditure_to_depreciation': float(latest_cash[fixed_assets_purchase_field]) / float(latest_income[depreciation_field]) if fixed_assets_purchase_field in latest_cash and depreciation_field in latest_income and float(latest_income[depreciation_field]) > 0 else None,
            'capital_expenditure_to_revenue': float(latest_cash[fixed_assets_purchase_field]) / float(latest_income[sales_field]) if fixed_assets_purchase_field in latest_cash and sales_field in latest_income and float(latest_income[sales_field]) > 0 else None,
            'capital_expenditure_to_assets': float(latest_cash[fixed_assets_purchase_field]) / float(latest_balance[total_assets_field]) if fixed_assets_purchase_field in latest_cash and total_assets_field in latest_balance and float(latest_balance[total_assets_field]) > 0 else None,
            'capital_expenditure_to_equity': float(latest_cash[fixed_assets_purchase_field]) / float(latest_balance[total_equity_field]) if fixed_assets_purchase_field in latest_cash and total_equity_field in latest_balance and float(latest_balance[total_equity_field]) > 0 else None,
            'capital_expenditure_to_market_cap': float(latest_cash[fixed_assets_purchase_field]) / market_cap if fixed_assets_purchase_field in latest_cash and market_cap > 0 else None,
            'capital_expenditure_to_net_income': float(latest_cash[fixed_assets_purchase_field]) / float(latest_income[net_profit_field]) if fixed_assets_purchase_field in latest_cash and net_profit_field in latest_income and float(latest_income[net_profit_field]) > 0 else None,
            'capital_expenditure_to_free_cash_flow': float(latest_cash[fixed_assets_purchase_field]) / (float(latest_cash[net_operate_cash_flow_field]) - float(latest_cash[net_invest_cash_flow_field])) if fixed_assets_purchase_field in latest_cash and net_operate_cash_flow_field in latest_cash and net_invest_cash_flow_field in latest_cash and (float(latest_cash[net_operate_cash_flow_field]) - float(latest_cash[net_invest_cash_flow_field])) > 0 else None,
        }
        
        return pd.DataFrame([metrics])
    except Exception as e:
        print(f"Error fetching financial metrics for {ticker}: {str(e)}")
        return pd.DataFrame()

def search_line_items(ticker: str, end_date: str, period: str = "annual", limit: int = 5) -> dict:
    """Search for specific line items in financial statements"""
    try:
        # Convert ticker format (e.g., 600519.SH -> 600519)
        stock_code = ticker.split('.')[0]
        
        # Get financial reports from Akshare using Eastmoney APIs
        income_statement = ak.stock_profit_sheet_by_report_em(symbol=f"{stock_code}.SH")
        balance_sheet = ak.stock_balance_sheet_by_report_em(symbol=f"{stock_code}.SH")
        cash_flow = ak.stock_cash_flow_sheet_by_report_em(symbol=f"{stock_code}.SH")
        print("[DEBUG] income_statement columns:", income_statement.columns)
        print("[DEBUG] income_statement head:\n", income_statement.head())
        print("[DEBUG] balance_sheet columns:", balance_sheet.columns)
        print("[DEBUG] balance_sheet head:\n", balance_sheet.head())
        print("[DEBUG] cash_flow columns:", cash_flow.columns)
        print("[DEBUG] cash_flow head:\n", cash_flow.head())
        
        if income_statement.empty or balance_sheet.empty or cash_flow.empty:
            return {}
        
        # Get market cap
        market_data = ak.stock_zh_a_spot_em()
        stock_info = market_data[market_data['代码'] == stock_code]
        market_cap = float(stock_info['总市值'].iloc[0]) if not stock_info.empty else None
        
        # Get latest data
        latest_income = income_statement.iloc[0]
        latest_balance = balance_sheet.iloc[0]
        latest_cash = cash_flow.iloc[0]
        
        # 自动识别字段名
        sales_field = find_matching_field(income_statement, 'TOTAL_OPERATE_INCOME')
        net_profit_field = find_matching_field(income_statement, 'NETPROFIT')
        total_assets_field = find_matching_field(balance_sheet, 'TOTAL_ASSETS')
        total_equity_field = find_matching_field(balance_sheet, 'TOTAL_EQUITY')
        net_operate_cash_flow_field = find_matching_field(cash_flow, 'NETCASH_OPERATE')
        net_invest_cash_flow_field = find_matching_field(cash_flow, 'NETCASH_INVEST')
        net_finance_cash_flow_field = find_matching_field(cash_flow, 'NETCASH_FINANCE')
        basic_eps_field = find_matching_field(income_statement, 'BASIC_EPS')
        share_capital_field = find_matching_field(balance_sheet, 'SHARE_CAPITAL')
        dividend_per_share_field = find_matching_field(income_statement, 'DIVIDEND_PER_SHARE')
        operating_cost_field = find_matching_field(income_statement, 'TOTAL_OPERATE_COST')
        inventory_field = find_matching_field(balance_sheet, 'INVENTORY')
        accounts_receivable_field = find_matching_field(balance_sheet, 'ACCOUNTS_RECE')
        accounts_payable_field = find_matching_field(balance_sheet, 'ACCOUNTS_PAYABLE')
        operating_profit_field = find_matching_field(income_statement, 'OPERATE_PROFIT')
        financial_expense_field = find_matching_field(income_statement, 'FINANCE_EXPENSE')
        fixed_assets_field = find_matching_field(balance_sheet, 'FIXED_ASSET')
        total_current_assets_field = find_matching_field(balance_sheet, 'TOTAL_CURRENT_ASSETS')
        total_current_liabilities_field = find_matching_field(balance_sheet, 'TOTAL_CURRENT_LIAB')
        retained_earnings_field = find_matching_field(balance_sheet, 'UNASSIGN_RPOFIT')
        fixed_assets_purchase_field = find_matching_field(cash_flow, 'CONSTRUCT_LONG_ASSET')
        depreciation_field = find_matching_field(income_statement, 'FA_IR_DEPR')
        
        print("\n[DEBUG] Field mappings:")
        print(f"sales_field: {sales_field}")
        print(f"net_profit_field: {net_profit_field}")
        print(f"total_assets_field: {total_assets_field}")
        print(f"total_equity_field: {total_equity_field}")
        
        # Map indicators to line items
        line_items = {
            'revenue': float(latest_income[sales_field]) if sales_field in latest_income else None,
            'net_income': float(latest_income[net_profit_field]) if net_profit_field in latest_income else None,
            'total_assets': float(latest_balance[total_assets_field]) if total_assets_field in latest_balance else None,
            'total_equity': float(latest_balance[total_equity_field]) if total_equity_field in latest_balance else None,
            'operating_cash_flow': float(latest_cash[net_operate_cash_flow_field]) if net_operate_cash_flow_field in latest_cash else None,
            'investing_cash_flow': float(latest_cash[net_invest_cash_flow_field]) if net_invest_cash_flow_field in latest_cash else None,
            'financing_cash_flow': float(latest_cash[net_finance_cash_flow_field]) if net_finance_cash_flow_field in latest_cash else None,
            'free_cash_flow': float(latest_cash[net_operate_cash_flow_field]) - float(latest_cash[net_invest_cash_flow_field]) if net_operate_cash_flow_field in latest_cash and net_invest_cash_flow_field in latest_cash else None,
            'eps': float(latest_income[basic_eps_field]) if basic_eps_field in latest_income else None,
            'book_value': float(latest_balance[total_equity_field]) / float(latest_balance[share_capital_field]) if total_equity_field in latest_balance and share_capital_field in latest_balance and float(latest_balance[share_capital_field]) > 0 else None,
            'dividend_yield': float(latest_income[dividend_per_share_field]) / float(latest_income[basic_eps_field]) if dividend_per_share_field in latest_income and basic_eps_field in latest_income and float(latest_income[basic_eps_field]) > 0 else None,
            'asset_turnover': float(latest_income[sales_field]) / float(latest_balance[total_assets_field]) if sales_field in latest_income and total_assets_field in latest_balance and float(latest_balance[total_assets_field]) > 0 else None,
            'inventory_turnover': float(latest_income[operating_cost_field]) / float(latest_balance[inventory_field]) if operating_cost_field in latest_income and inventory_field in latest_balance and float(latest_balance[inventory_field]) > 0 else None,
            'receivables_turnover': float(latest_income[sales_field]) / float(latest_balance[accounts_receivable_field]) if sales_field in latest_income and accounts_receivable_field in latest_balance and float(latest_balance[accounts_receivable_field]) > 0 else None,
            'days_sales_outstanding': 365 / (float(latest_income[sales_field]) / float(latest_balance[accounts_receivable_field])) if sales_field in latest_income and accounts_receivable_field in latest_balance and float(latest_balance[accounts_receivable_field]) > 0 else None,
            'days_inventory': 365 / (float(latest_income[operating_cost_field]) / float(latest_balance[inventory_field])) if operating_cost_field in latest_income and inventory_field in latest_balance and float(latest_balance[inventory_field]) > 0 else None,
            'days_payable': 365 / (float(latest_income[operating_cost_field]) / float(latest_balance[accounts_payable_field])) if operating_cost_field in latest_income and accounts_payable_field in latest_balance and float(latest_balance[accounts_payable_field]) > 0 else None,
            'cash_conversion_cycle': (365 / (float(latest_income[sales_field]) / float(latest_balance[accounts_receivable_field])) if sales_field in latest_income and accounts_receivable_field in latest_balance and float(latest_balance[accounts_receivable_field]) > 0 else 0) + 
                                   (365 / (float(latest_income[operating_cost_field]) / float(latest_balance[inventory_field])) if operating_cost_field in latest_income and inventory_field in latest_balance and float(latest_balance[inventory_field]) > 0 else 0) - 
                                   (365 / (float(latest_income[operating_cost_field]) / float(latest_balance[accounts_payable_field])) if operating_cost_field in latest_income and accounts_payable_field in latest_balance and float(latest_balance[accounts_payable_field]) > 0 else 0),
            'interest_coverage': float(latest_income[operating_profit_field]) / float(latest_income[financial_expense_field]) if operating_profit_field in latest_income and financial_expense_field in latest_income and float(latest_income[financial_expense_field]) > 0 else None,
            'fixed_asset_turnover': float(latest_income[sales_field]) / float(latest_balance[fixed_assets_field]) if sales_field in latest_income and fixed_assets_field in latest_balance and float(latest_balance[fixed_assets_field]) > 0 else None,
            'total_asset_turnover': float(latest_income[sales_field]) / float(latest_balance[total_assets_field]) if sales_field in latest_income and total_assets_field in latest_balance and float(latest_balance[total_assets_field]) > 0 else None,
            'equity_turnover': float(latest_income[sales_field]) / float(latest_balance[total_equity_field]) if sales_field in latest_income and total_equity_field in latest_balance and float(latest_balance[total_equity_field]) > 0 else None,
            'working_capital': float(latest_balance[total_current_assets_field]) - float(latest_balance[total_current_liabilities_field]) if total_current_assets_field in latest_balance and total_current_liabilities_field in latest_balance else None,
            'working_capital_turnover': float(latest_income[sales_field]) / (float(latest_balance[total_current_assets_field]) - float(latest_balance[total_current_liabilities_field])) if sales_field in latest_income and total_current_assets_field in latest_balance and total_current_liabilities_field in latest_balance and (float(latest_balance[total_current_assets_field]) - float(latest_balance[total_current_liabilities_field])) > 0 else None,
            'retained_earnings': float(latest_balance[retained_earnings_field]) if retained_earnings_field in latest_balance else None,
            'retained_earnings_to_equity': float(latest_balance[retained_earnings_field]) / float(latest_balance[total_equity_field]) if retained_earnings_field in latest_balance and total_equity_field in latest_balance and float(latest_balance[total_equity_field]) > 0 else None,
            'capital_expenditure': float(latest_cash[fixed_assets_purchase_field]) if fixed_assets_purchase_field in latest_cash else None,
            'capital_expenditure_to_operating_cash_flow': float(latest_cash[fixed_assets_purchase_field]) / float(latest_cash[net_operate_cash_flow_field]) if fixed_assets_purchase_field in latest_cash and net_operate_cash_flow_field in latest_cash and float(latest_cash[net_operate_cash_flow_field]) > 0 else None,
            'capital_expenditure_to_depreciation': float(latest_cash[fixed_assets_purchase_field]) / float(latest_income[depreciation_field]) if fixed_assets_purchase_field in latest_cash and depreciation_field in latest_income and float(latest_income[depreciation_field]) > 0 else None,
            'capital_expenditure_to_revenue': float(latest_cash[fixed_assets_purchase_field]) / float(latest_income[sales_field]) if fixed_assets_purchase_field in latest_cash and sales_field in latest_income and float(latest_income[sales_field]) > 0 else None,
            'capital_expenditure_to_assets': float(latest_cash[fixed_assets_purchase_field]) / float(latest_balance[total_assets_field]) if fixed_assets_purchase_field in latest_cash and total_assets_field in latest_balance and float(latest_balance[total_assets_field]) > 0 else None,
            'capital_expenditure_to_equity': float(latest_cash[fixed_assets_purchase_field]) / float(latest_balance[total_equity_field]) if fixed_assets_purchase_field in latest_cash and total_equity_field in latest_balance and float(latest_balance[total_equity_field]) > 0 else None,
            'capital_expenditure_to_market_cap': float(latest_cash[fixed_assets_purchase_field]) / market_cap if fixed_assets_purchase_field in latest_cash and market_cap > 0 else None,
            'capital_expenditure_to_net_income': float(latest_cash[fixed_assets_purchase_field]) / float(latest_income[net_profit_field]) if fixed_assets_purchase_field in latest_cash and net_profit_field in latest_income and float(latest_income[net_profit_field]) > 0 else None,
            'capital_expenditure_to_free_cash_flow': float(latest_cash[fixed_assets_purchase_field]) / (float(latest_cash[net_operate_cash_flow_field]) - float(latest_cash[net_invest_cash_flow_field])) if fixed_assets_purchase_field in latest_cash and net_operate_cash_flow_field in latest_cash and net_invest_cash_flow_field in latest_cash and (float(latest_cash[net_operate_cash_flow_field]) - float(latest_cash[net_invest_cash_flow_field])) > 0 else None,
        }
        
        return line_items
    except Exception as e:
        print(f"Error searching line items for {ticker}: {str(e)}")
        return {}

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