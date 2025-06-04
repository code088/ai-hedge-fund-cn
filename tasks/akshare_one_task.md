# 📘 任务文档：使用 `akshare-one` 替代 AkShare 原始接口获取中国财务数据

---

## 🎯 任务目标

由于 `akshare` 主包中的 `stock_financial_report_em` 接口不存在或已被移除，为实现稳定的财务数据获取，现采用 [`akshare-one`](https://pypi.org/project/akshare-one/) 封装库作为替代方案。

---

## ✅ 第一步：安装 `akshare-one`

在项目中使用 Poetry 安装：

```bash
poetry add akshare-one
```

---

## ✅ 第二步：可用接口一览

| 函数名 | 功能说明 |
|--------|----------|
| `get_income_statement(symbol)` | 获取利润表 |
| `get_balance_sheet(symbol)` | 获取资产负债表 |
| `get_cash_flow(symbol)` | 获取现金流量表 |
| `get_financial_summary(symbol)` | 获取标准化财务汇总数据（推荐） |

---

## ✅ 第三步：替换 `get_financial_metrics` 示例

```python
from akshare_one import get_financial_summary

def get_financial_metrics(ticker: str, end_date: str, period: str = "annual", limit: int = 5) -> pd.DataFrame:
    try:
        stock_code = ticker.split('.')[0]
        df = get_financial_summary(symbol=stock_code)
        if df.empty:
            return pd.DataFrame()

        # 可提取字段包括：营业收入、净利润、资产总计、所有者权益合计、ROE、毛利率等
        latest = df.iloc[0]  # 默认取最近一季度或一年的数据

        metrics = {
            'revenue': latest.get('营业收入'),
            'net_income': latest.get('净利润'),
            'total_assets': latest.get('资产总计'),
            'total_equity': latest.get('所有者权益合计'),
            'roe': latest.get('净资产收益率(%)'),
            'gross_margin': latest.get('毛利率(%)'),
            'profit_margin': latest.get('销售净利率(%)'),
            'return_on_equity': latest.get('净资产收益率(%)'),
        }

        return pd.DataFrame([metrics])
    except Exception as e:
        print(f"[akshare-one] Error fetching financial summary for {ticker}: {str(e)}")
        return pd.DataFrame()
```

---

## ✅ 第四步：替换 `search_line_items`（如需）

你也可以使用 `get_income_statement`, `get_balance_sheet`, `get_cash_flow` 结合字段映射，实现更强大的 `search_line_items` 支持。

---

## ✅ 第五步：测试验证

```bash
poetry run python src/main.py --ticker 600519.SH --show-reasoning
```

---

## 💡 小贴士

- `akshare-one` 默认返回最新报告期的数据，适合用于构建策略特征和估值分析
- 支持大部分主板/科创板股票，但对新三板或北交所支持可能有限
- 若有字段对不上，可通过 `df.columns` 查看实际返回内容

---
