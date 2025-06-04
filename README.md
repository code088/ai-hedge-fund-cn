# 特别说明 / Special Note

本项目是基于原始的 [ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) 项目，增加了对中国A股的支持。今后可能会进一步汉化，使其更适合中国用户使用。目前使用的是免费API，数据可能不够完善，但未来计划支持 Tushare、JoinQuant 等更专业的中国金融市场数据源。

This project is a fork of the original [ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) with added support for Chinese A-shares. Future plans include further localization to better serve Chinese users. Currently using free APIs with limited data coverage, but we plan to integrate more comprehensive Chinese market data sources like Tushare and JoinQuant in the future.

---

# AI 对冲基金 / AI Hedge Fund

这是一个由AI驱动的对冲基金概念验证项目。该项目的目标是探索使用AI来做出交易决策。本项目仅用于**教育**目的，不用于实际交易或投资。

This is a proof of concept for an AI-powered hedge fund. The goal of this project is to explore the use of AI to make trading decisions. This project is for **educational** purposes only and is not intended for real trading or investment.

本系统由多个协同工作的智能体组成：

1. 阿斯沃斯·达摩达兰智能体 - 估值大师，专注于故事、数字和严谨的估值
2. 本杰明·格雷厄姆智能体 - 价值投资之父，只买入具有安全边际的隐藏宝石
3. 比尔·阿克曼智能体 - 激进投资者，采取大胆立场并推动变革
4. 凯茜·伍德智能体 - 成长投资女王，相信创新和颠覆的力量
5. 查理·芒格智能体 - 沃伦·巴菲特的搭档，只以合理价格买入优秀企业
6. 迈克尔·伯里智能体 - 大空头逆势投资者，寻找深度价值
7. 彼得·林奇智能体 - 实用投资者，在日常业务中寻找"十倍股"
8. 菲利普·费舍智能体 - 严谨的成长投资者，使用深入的"小道消息"研究
9. 拉克什·金君瓦拉智能体 - 印度大牛
10. 斯坦利·德鲁肯米勒智能体 - 宏观传奇，寻找具有增长潜力的不对称机会
11. 沃伦·巴菲特智能体 - 奥马哈先知，以合理价格寻找优秀公司
12. 估值智能体 - 计算股票内在价值并生成交易信号
13. 情绪智能体 - 分析市场情绪并生成交易信号
14. 基本面智能体 - 分析基本面数据并生成交易信号
15. 技术分析智能体 - 分析技术指标并生成交易信号
16. 风险管理智能体 - 计算风险指标并设置仓位限制
17. 投资组合管理智能体 - 做出最终交易决策并生成订单

This system employs several agents working together:

1. Aswath Damodaran Agent - The Dean of Valuation, focuses on story, numbers, and disciplined valuation
2. Ben Graham Agent - The godfather of value investing, only buys hidden gems with a margin of safety
3. Bill Ackman Agent - An activist investor, takes bold positions and pushes for change
4. Cathie Wood Agent - The queen of growth investing, believes in the power of innovation and disruption
5. Charlie Munger Agent - Warren Buffett's partner, only buys wonderful businesses at fair prices
6. Michael Burry Agent - The Big Short contrarian who hunts for deep value
7. Peter Lynch Agent - Practical investor who seeks "ten-baggers" in everyday businesses
8. Phil Fisher Agent - Meticulous growth investor who uses deep "scuttlebutt" research 
9. Rakesh Jhunjhunwala Agent - The Big Bull of India
10. Stanley Druckenmiller Agent - Macro legend who hunts for asymmetric opportunities with growth potential
11. Warren Buffett Agent - The oracle of Omaha, seeks wonderful companies at a fair price
12. Valuation Agent - Calculates the intrinsic value of a stock and generates trading signals
13. Sentiment Agent - Analyzes market sentiment and generates trading signals
14. Fundamentals Agent - Analyzes fundamental data and generates trading signals
15. Technicals Agent - Analyzes technical indicators and generates trading signals
16. Risk Manager - Calculates risk metrics and sets position limits
17. Portfolio Manager - Makes final trading decisions and generates orders

**注意**：该系统仅模拟交易决策，不进行实际交易。

**Note**: the system simulates trading decisions, it does not actually trade.

[![Twitter Follow](https://img.shields.io/twitter/follow/virattt?style=social)](https://twitter.com/virattt)

## 免责声明 / Disclaimer

本项目仅用于**教育和研究目的**。

This project is for **educational and research purposes only**.

- 不用于实际交易或投资
- 不提供投资建议或保证
- 创建者不对财务损失负责
- 投资决策请咨询财务顾问
- 过往业绩不代表未来表现

- Not intended for real trading or investment
- No investment advice or guarantees provided
- Creator assumes no liability for financial losses
- Consult a financial advisor for investment decisions
- Past performance does not indicate future results

使用本软件即表示您同意仅将其用于学习目的。

By using this software, you agree to use it solely for learning purposes.

## 目录 / Table of Contents
- [设置 / Setup](#setup)
  - [使用 Poetry / Using Poetry](#using-poetry)
  - [使用 Docker / Using Docker](#using-docker)
- [使用方法 / Usage](#usage)
  - [运行对冲基金 / Running the Hedge Fund](#running-the-hedge-fund)
  - [运行回测器 / Running the Backtester](#running-the-backtester)
- [贡献指南 / Contributing](#contributing)
- [功能请求 / Feature Requests](#feature-requests)
- [许可证 / License](#license)

## 设置 / Setup

### 使用 Poetry / Using Poetry

克隆仓库：
```bash
git clone https://github.com/virattt/ai-hedge-fund.git
cd ai-hedge-fund
```

Clone the repository:
```bash
git clone https://github.com/virattt/ai-hedge-fund.git
cd ai-hedge-fund
```

1. 安装 Poetry（如果尚未安装）：
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. 安装依赖：
```bash
poetry install
```

2. Install dependencies:
```bash
poetry install
```

3. 设置环境变量：
```bash
# 创建 .env 文件用于存储 API 密钥
cp .env.example .env
```

3. Set up your environment variables:
```bash
# Create .env file for your API keys
cp .env.example .env
```

4. 设置 API 密钥：
```bash
# 用于运行由 openai 托管的 LLM（gpt-4o, gpt-4o-mini 等）
# 从 https://platform.openai.com/ 获取 OpenAI API 密钥
OPENAI_API_KEY=your-openai-api-key

# 用于运行由 groq 托管的 LLM（deepseek, llama3 等）
# 从 https://groq.com/ 获取 Groq API 密钥
GROQ_API_KEY=your-groq-api-key

# 用于获取金融数据以支持对冲基金
# 从 https://financialdatasets.ai/ 获取 Financial Datasets API 密钥
FINANCIAL_DATASETS_API_KEY=your-financial-datasets-api-key
```

4. Set your API keys:
```bash
# For running LLMs hosted by openai (gpt-4o, gpt-4o-mini, etc.)
# Get your OpenAI API key from https://platform.openai.com/
OPENAI_API_KEY=your-openai-api-key

# For running LLMs hosted by groq (deepseek, llama3, etc.)
# Get your Groq API key from https://groq.com/
GROQ_API_KEY=your-groq-api-key

# For getting financial data to power the hedge fund
# Get your Financial Datasets API key from https://financialdatasets.ai/
FINANCIAL_DATASETS_API_KEY=your-financial-datasets-api-key
```

### 使用 Docker / Using Docker

1. 确保您的系统已安装 Docker。如果尚未安装，可以从 [Docker 官方网站](https://www.docker.com/get-started) 下载。

1. Make sure you have Docker installed on your system. If not, you can download it from [Docker's official website](https://www.docker.com/get-started).

2. 克隆仓库：
```bash
git clone https://github.com/virattt/ai-hedge-fund.git
cd ai-hedge-fund
```

2. Clone the repository:
```bash
git clone https://github.com/virattt/ai-hedge-fund.git
cd ai-hedge-fund
```

3. 设置环境变量：
```bash
# 创建 .env 文件用于存储 API 密钥
cp .env.example .env
```

3. Set up your environment variables:
```bash
# Create .env file for your API keys
cp .env.example .env
```

4. 编辑 .env 文件，添加上述 API 密钥。

4. Edit the .env file to add your API keys as described above.

5. 构建 Docker 镜像：
```bash
# Linux/Mac：
./run.sh build

# Windows：
run.bat build
```

5. Build the Docker image:
```bash
# On Linux/Mac:
./run.sh build

# On Windows:
run.bat build
```

**重要提示**：您必须设置 `OPENAI_API_KEY`、`GROQ_API_KEY`、`ANTHROPIC_API_KEY` 或 `DEEPSEEK_API_KEY` 才能使对冲基金正常工作。如果您想使用所有提供商的 LLM，则需要设置所有 API 密钥。

**Important**: You must set `OPENAI_API_KEY`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY`, or `DEEPSEEK_API_KEY` for the hedge fund to work. If you want to use LLMs from all providers, you will need to set all API keys.

AAPL、GOOGL、MSFT、NVDA 和 TSLA 的金融数据是免费的，不需要 API 密钥。

Financial data for AAPL, GOOGL, MSFT, NVDA, and TSLA is free and does not require an API key.

对于任何其他股票代码，您需要在 .env 文件中设置 `FINANCIAL_DATASETS_API_KEY`。

For any other ticker, you will need to set the `FINANCIAL_DATASETS_API_KEY` in the .env file.

## 使用方法 / Usage

### 运行对冲基金 / Running the Hedge Fund

#### 使用 Poetry
```bash
poetry run python src/main.py --ticker AAPL,MSFT,NVDA
```

#### With Poetry
```bash
poetry run python src/main.py --ticker AAPL,MSFT,NVDA
```

#### 使用 Docker
```bash
# Linux/Mac：
./run.sh --ticker AAPL,MSFT,NVDA main

# Windows：
run.bat --ticker AAPL,MSFT,NVDA main
```

#### With Docker
```bash
# On Linux/Mac:
./run.sh --ticker AAPL,MSFT,NVDA main

# On Windows:
run.bat --ticker AAPL,MSFT,NVDA main
```

**示例输出：**
<img width="992" alt="Screenshot 2025-01-06 at 5 50 17 PM" src="https://github.com/user-attachments/assets/e8ca04bf-9989-4a7d-a8b4-34e04666663b" />

您还可以指定 `--ollama` 标志来使用本地 LLM 运行 AI 对冲基金。

You can also specify a `--ollama` flag to run the AI hedge fund using local LLMs.

```bash
# 使用 Poetry：
poetry run python src/main.py --ticker AAPL,MSFT,NVDA --ollama

# 使用 Docker（Linux/Mac）：
./run.sh --ticker AAPL,MSFT,NVDA --ollama main

# 使用 Docker（Windows）：
run.bat --ticker AAPL,MSFT,NVDA --ollama main
```

您还可以指定 `--show-reasoning` 标志来在控制台打印每个智能体的推理过程。

You can also specify a `--show-reasoning` flag to print the reasoning of each agent to the console.

```bash
# 使用 Poetry：
poetry run python src/main.py --ticker AAPL,MSFT,NVDA --show-reasoning

# 使用 Docker（Linux/Mac）：
./run.sh --ticker AAPL,MSFT,NVDA --show-reasoning main

# 使用 Docker（Windows）：
run.bat --ticker AAPL,MSFT,NVDA --show-reasoning main
```

您可以选择性地指定开始和结束日期，以便在特定时间段内做出决策。

You can optionally specify the start and end dates to make decisions for a specific time period.

```bash
# 使用 Poetry：
poetry run python src/main.py --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01 

# 使用 Docker（Linux/Mac）：
./run.sh --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01 main

# 使用 Docker（Windows）：
run.bat --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01 main
```

### 运行回测器 / Running the Backtester

#### 使用 Poetry
```bash
poetry run python src/backtester.py --ticker AAPL,MSFT,NVDA
```

#### With Poetry
```bash
poetry run python src/backtester.py --ticker AAPL,MSFT,NVDA
```

#### 使用 Docker
```bash
# Linux/Mac：
./run.sh --ticker AAPL,MSFT,NVDA backtest

# Windows：
run.bat --ticker AAPL,MSFT,NVDA backtest
```

#### With Docker
```bash
# On Linux/Mac:
./run.sh --ticker AAPL,MSFT,NVDA backtest

# On Windows:
run.bat --ticker AAPL,MSFT,NVDA backtest
```

**示例输出：**
<img width="941" alt="Screenshot 2025-01-06 at 5 47 52 PM" src="https://github.com/user-attachments/assets/00e794ea-8628-44e6-9a84-8f8a31ad3b47" />

您可以选择性地指定开始和结束日期，以便在特定时间段内进行回测。

You can optionally specify the start and end dates to backtest over a specific time period.

```bash
# 使用 Poetry：
poetry run python src/backtester.py --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01

# 使用 Docker（Linux/Mac）：
./run.sh --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01 backtest

# 使用 Docker（Windows）：
run.bat --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01 backtest
```

您还可以指定 `--ollama` 标志来使用本地 LLM 运行回测器。

You can also specify a `--ollama` flag to run the backtester using local LLMs.
```bash
# 使用 Poetry：
poetry run python src/backtester.py --ticker AAPL,MSFT,NVDA --ollama

# 使用 Docker（Linux/Mac）：
./run.sh --ticker AAPL,MSFT,NVDA --ollama backtest

# 使用 Docker（Windows）：
run.bat --ticker AAPL,MSFT,NVDA --ollama backtest
```

## 贡献指南 / Contributing

1. Fork 仓库
2. 创建特性分支
3. 提交您的更改
4. 推送到分支
5. 创建 Pull Request

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

**重要提示**：请保持您的 pull requests 小而集中。这将使审查和合并更容易。

**Important**: Please keep your pull requests small and focused. This will make it easier to review and merge.

## 功能请求 / Feature Requests

如果您有功能请求，请创建一个[issue](https://github.com/virattt/ai-hedge-fund/issues)并确保它被标记为`enhancement`。

If you have a feature request, please open an [issue](https://github.com/virattt/ai-hedge-fund/issues) and make sure it is tagged with `enhancement`.

## 许可证 / License

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件。

This project is licensed under the MIT License - see the LICENSE file for details.
