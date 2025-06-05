# ✅ 任务：使 `api_cn.py` 与 `api.py` 接口完全一致

目标是为了兼容 `api_router.py` 的统一调度逻辑，确保 `api_cn.py` 所有函数签名和返回值与 `api.py` 对齐，避免运行时参数或类型错误。

---

## 🧩 1. 修改 `search_line_items` 签名和返回类型

### ✅ 目标签名：
```python
def search_line_items(
    ticker: str,
    line_items: list[str],
    end_date: str,
    period: str = "annual",
    limit: int = 5,
) -> list[LineItem]:
```

### ✅ 返回值格式：
- 返回 `List[LineItem]`，每个包含：`name`, `value`, `date`, `period`

---

## 🧩 2. 修改 `get_financial_metrics` 签名和返回类型

### ✅ 目标签名：
```python
def get_financial_metrics(
    ticker: str,
    end_date: str,
    period: str = "annual",
    limit: int = 5,
) -> list[FinancialMetrics]:
```

### ✅ 返回值格式：
- 返回 `List[FinancialMetrics]`
- 可从 `pd.DataFrame` 转换为模型：

```python
[FinancialMetrics(**row.dropna().to_dict()) for _, row in df.iterrows()]
```

---

## ✅ 建议命名适配字段映射（如字段不一致时）

例如：

```python
{
    "revenue": "TOTAL_OPERATE_INCOME",
    "net_income": "NETPROFIT",
    "total_assets": "TOTAL_ASSETS",
    "total_equity": "TOTAL_EQUITY",
}
```

---

## 🔄 测试验证建议

在修改完成后运行以下语句验证：

```bash
python src/main.py
# 或
pytest tests/
```

观察是否仍然有 `TypeError` 或返回类型异常。

---

## ☑️ 目标完成条件

- `api_cn.py` 中所有函数与 `api.py` 对齐
- 运行中无 `TypeError`、字段缺失或类型错误
- 兼容 `api_router.py` 调度策略