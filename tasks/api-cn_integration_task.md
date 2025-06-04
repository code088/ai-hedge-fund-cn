# 🧾 任务文档：将 `api.py` 改写为 `api-cn.py` 以支持中国股票（Tushare）

## 🎯 任务目标

创建一个 `api-cn.py` 文件，用于通过 Tushare 查询中国A股数据，并与当前 `api.py` 接口保持完全一致，以便于无缝替换在 AI 投资代理中的数据调用。

---

## 📁 新文件位置

```bash
src/tools/api-cn.py
```

---

## 🛠 修改内容详解

### ✅ 使用 Tushare 替代 API 数据源

- 依赖库：
  ```bash
  pip install tushare
  ```

- `.env` 文件中添加：
  ```env
  TUSHARE_TOKEN=your_token_here
  ```

- 初始化 Tushare 接口：

  ```python
  import tushare as ts
  ts.set_token(os.getenv("TUSHARE_TOKEN"))
  pro = ts.pro_api()
  ```

---

## 🧱 函数替换说明

### 1. `get_prices`（替代）

```python
def get_prices(ticker: str, start_date: str, end_date: str) -> list[Price]:
    df = pro.daily(ts_code=ticker, start_date=start_date.replace("-", ""), end_date=end_date.replace("-", ""))
    df = df.sort_values("trade_date")
    return [
        Price(
            time=row["trade_date"],
            open=row["open"],
            high=row["high"],
            low=row["low"],
            close=row["close"],
            volume=row["vol"]
        )
        for _, row in df.iterrows()
    ]
```

---

### 2. `get_financial_metrics`（替代）

```python
def get_financial_metrics(ticker: str, end_date: str, period: str = "ttm", limit: int = 10) -> list[FinancialMetrics]:
    df = pro.fina_indicator(ts_code=ticker, end_date=end_date.replace("-", ""), limit=limit)
    return [
        FinancialMetrics(
            pe_ratio=row["pe_ttm"],
            pb_ratio=row["pb"],
            roe=row["roe"],
            roa=row["roa"],
            net_margin=row["netprofit_margin"],
            gross_margin=row["grossprofit_margin"],
            report_period=row["end_date"]
        )
        for _, row in df.iterrows()
    ]
```

---

### 3. 其它函数

由于 Tushare 暂无直接支持的接口：

- `get_insider_trades`
- `get_company_news`
- `search_line_items`
- `get_market_cap`

可先返回占位空结果或提示不支持：

```python
def get_insider_trades(...):
    return []

def get_company_news(...):
    return []

def search_line_items(...):
    return []

def get_market_cap(...):
    return None
```

---

## 🤖 使用方式（示例）

你可以在代理中添加判断逻辑：

```python
if ticker.endswith(".SH") or ticker.endswith(".SZ"):
    from src.tools import api_cn as api
else:
    from src.tools import api as api
```

---

## 📌 注意事项

- 返回的模型需兼容 `pydantic` 类如 `Price`, `FinancialMetrics`。
- Tushare 股票代码必须是 `XXXXXX.SZ` 或 `XXXXXX.SH`。
- 可选：将 `api.py` 中的公共数据接口改为策略分发，根据 ticker 自动切换调用源。

---

