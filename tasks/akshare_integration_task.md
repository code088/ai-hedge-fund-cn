# 📘 任务文档：将中国股票数据源从 Tushare 切换为 Akshare

---

## 🎯 任务目标

由于 Tushare 存在积分限制，现将中国 A 股数据源切换为 [Akshare](https://akshare.readthedocs.io/zh_CN/latest/index.html)，以继续支持 `api-cn.py` 的无障碍访问。

---

## ✅ 第一步：安装 Akshare

使用 Poetry 添加依赖：

```bash
poetry add akshare
```

---

## ✅ 第二步：修改 `get_prices` 函数

替换为使用 Akshare 的日线历史行情接口：

```python
import akshare as ak

def get_prices(ticker: str, start_date: str, end_date: str) -> list[Price]:
    cache_key = f"{ticker}_{start_date}_{end_date}"
    if cached_data := _cache.get_prices(cache_key):
        return [Price(**price) for price in cached_data]

    df = ak.stock_zh_a_hist(
        symbol=ticker.split('.')[0],  # 取前6位代码，如 '600519'
        period="daily",
        start_date=start_date.replace("-", ""),
        end_date=end_date.replace("-", ""),
        adjust="qfq"
    )

    df.rename(columns={
        "日期": "date", "开盘": "open", "收盘": "close", "最高": "high", "最低": "low", "成交量": "volume"
    }, inplace=True)

    prices = [
        Price(
            time=row["date"],
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=int(row["volume"])
        )
        for _, row in df.iterrows()
    ]

    _cache.set_prices(cache_key, [p.model_dump() for p in prices])
    return prices
```

---

## ✅ 第三步：修改 `get_market_cap`

```python
def get_market_cap(ticker: str, end_date: str) -> float | None:
    try:
        df = ak.stock_zh_a_spot_em()
        df = df[df["代码"] == ticker.split('.')[0]]
        if df.empty:
            return None
        return float(df["总市值"].values[0]) * 1e8  # 单位为亿元
    except Exception as e:
        print(f"[akshare] Market cap fetch error: {e}")
        return None
```

---

## ⚠️ 第四步：简化或跳过以下接口（Akshare 暂不支持）

| 函数名                | 说明               | 建议                    |
|-----------------------|--------------------|-------------------------|
| `get_financial_metrics` | 仅部分支持         | 可用静态数据或先返回空 |
| `get_company_news`    | 不支持新闻         | 返回空列表              |
| `get_insider_trades`  | 不支持高管交易     | 返回空列表              |
| `search_line_items`   | 不支持财报明细项   | 返回空列表              |

---

## ✅ 第五步：测试指令

```bash
poetry run python src/main.py --ticker 600519.SH --show-reasoning
```

---

## 💡 可选增强

如需实时行情或报价加速，可考虑结合 `easyquotation` 获取快照数据。

---
