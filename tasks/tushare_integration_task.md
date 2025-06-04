# 📌 任务文档：集成 Tushare 并实现中美股票 API 自动切换

---

## 🎯 任务目标

1. 使用 Poetry 管理并安装 `tushare` 库。
2. 新建或修改接口文件 `api_cn.py` 支持中国 A 股。
3. 自动识别股票代码（如 `.SH`, `.SZ`）并路由到正确的数据源。

---

## ✅ 第一步：添加 tushare 到 Poetry 项目

在项目根目录运行以下命令：

```bash
poetry add tushare
```

这将安装最新版本的 tushare 并写入 `pyproject.toml`。

---

## ✅ 第二步：配置 `.env` 文件

```env
TUSHARE_TOKEN=your_token_here
```

在 `api_cn.py` 中加入：

```python
import tushare as ts
ts.set_token(os.getenv("TUSHARE_TOKEN"))
pro = ts.pro_api()
```

---

## ✅ 第三步：新增 Tushare 数据接口（`api_cn.py`）

你已经完成，确保其接口函数如下：

- `get_prices(...)`
- `get_financial_metrics(...)`
- `get_price_data(...)`
- 其他函数可返回空（或提示不支持）

---

## ✅ 第四步：根据 ticker 自动切换 API 源

你可以创建一个统一数据路由器，如 `src/tools/api_router.py`：

```python
def is_china_stock(ticker: str) -> bool:
    return ticker.endswith(".SH") or ticker.endswith(".SZ")


if is_china_stock(ticker):
    from src.tools import api_cn as api
else:
    from src.tools import api as api
```

然后在所有代理中统一改用：

```python
from src.tools.api_router import api
```

---

## ✅ 补充：可加入断言确保格式正确

```python
assert ticker.count('.') == 1 and ticker.split('.')[1] in ['SH', 'SZ'], "Invalid Chinese stock ticker format."
```

---

## ✅ 测试建议

```bash
poetry run python src/main.py --ticker 600519.SH --show-reasoning
poetry run python src/main.py --ticker AAPL --show-reasoning
```

---

任务完成后你将实现：

- 🇨🇳 中国 A 股数据对接（Tushare）
- 🇺🇸 美股数据保留（Financial Datasets API）
- 🤖 代理层代码无需改动，统一接口调用

