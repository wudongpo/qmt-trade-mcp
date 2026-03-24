# qmt-trade-mcp

基于 [FastMCP](https://github.com/jlowin/fastmcp) 框架构建的 MCP（Model Context Protocol）服务，封装迅投 `xtquant.xtdata` 行情数据接口，通过 SSE 传输协议提供行情查询能力。

**联系方式（微信）：** gold98986868、15518184045

## 环境要求

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv) 包管理器
- 已安装并配置 QMT/xtquant 运行环境（需自行安装迅投 QMT 终端，并保持 QMT 客户端登录运行）

## 快速开始

### 克隆项目

```bash
git clone https://github.com/novaair026-dev/qmt-trade-mcp.git
cd qmt-trade-mcp
```

### 安装依赖

```bash
uv sync
```

### 启动服务

```bash
uv run python main.py
```

服务默认监听 `127.0.0.1:8000`，可通过环境变量自定义：

```bash
MCP_HOST=0.0.0.0 MCP_PORT=9000 uv run python main.py
```

### 验证服务

访问 `http://127.0.0.1:8000/sse` 建立 SSE 连接后，即可通过 MCP 协议调用各工具。

## 项目结构

```
qmt-trade-mcp/
├── main.py                     # 服务入口，uvicorn 加载 ASGI 应用
├── pyproject.toml              # 项目配置及依赖
├── src/
│   └── xtdata_mcp/
│       ├── __init__.py         # 包初始化
│       ├── __main__.py         # 模块级入口
│       └── server.py            # 核心实现，所有 MCP tools
└── tests/
    ├── __init__.py
    ├── conftest.py            # pytest fixtures（内存传输测试客户端）
    └── test_server.py         # 各 tool 功能测试
```

## 提供的 MCP Tools（共 25 个）

所有工具均支持通过 MCP 客户端调用，返回统一 JSON 格式。

### 行情数据

| Tool | 说明 |
|------|------|
| `get_full_tick` | 获取当前全推市场快照数据 |
| `get_market_data` | 从缓存获取行情数据（核心接口） |
| `get_local_data` | 从本地数据文件直接读取行情数据 |
| `get_full_kline` | 获取最新交易日 K 线全推数据 |

### 历史数据下载

| Tool | 说明 |
|------|------|
| `download_history_data` | 下载单个标的历史行情数据 |
| `download_history_data2` | 批量下载多个标的历史行情数据 |

### 除权除息

| Tool | 说明 |
|------|------|
| `get_divid_factors` | 获取除权除息因子（分红/送股/配股等） |

### 交易日历

| Tool | 说明 |
|------|------|
| `get_period_list` | 获取当前连接可用的行情周期列表 |
| `get_holidays` | 获取当前年度所有节假日日期 |
| `get_trading_calendar` | 获取指定市场的交易日历 |
| `get_trading_dates` | 获取交易日列表（时间戳格式） |
| `download_holiday_data` | 下载节假日数据到本地 |

### 合约与板块

| Tool | 说明 |
|------|------|
| `get_instrument_detail` | 获取合约详细基础信息 |
| `get_instrument_type` | 判断合约类型（股票/指数/基金/ETF） |
| `get_sector_list` | 获取所有可用板块列表 |
| `get_stock_list_in_sector` | 获取指定板块的成分股列表 |
| `download_sector_data` | 下载板块分类信息 |
| `get_index_weight` | 获取指数成分股及其权重 |
| `download_index_weight` | 下载指数成分权重数据 |

### 财务数据

| Tool | 说明 |
|------|------|
| `get_financial_data` | 获取财务数据（资产负债表/利润表等） |
| `download_financial_data` | 下载指定股票的财务数据 |

### 可转债

| Tool | 说明 |
|------|------|
| `get_cb_info` | 获取可转债基础信息 |
| `download_cb_data` | 下载全市场可转债信息 |

### 新股 / ETF

| Tool | 说明 |
|------|------|
| `get_ipo_info` | 获取新股申购信息 |
| `download_etf_info` | 下载 ETF 申赎清单信息 |
| `get_etf_info` | 获取 ETF 申赎清单信息 |

## 响应格式

所有 tool 均返回统一 JSON 格式：

```json
// 成功
{ "ok": true, "data": <结果> }

// 失败（如 xtquant 未配置）
{ "ok": false, "error": "<错误信息>" }
```

## 测试

```bash
# 运行所有 tool 的功能测试
uv run pytest tests/test_server.py -v
```

测试使用 FastMCP Client 内存传输，无需启动服务器，每个测试调用真实 xtquant 接口验证功能正常。

## 部署说明

本服务通过 SSE（Server-Sent Events）传输协议提供 MCP 接口，适用于兼容 SSE 的 MCP 客户端（如 Claude Desktop、Dify 等）。

推荐通过反向代理（如 Nginx）将服务暴露到指定路径或域名：

```nginx
location /mcp {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Connection '';
    proxy_buffering off;
    proxy_cache off;
}
```

SSE 端点：`GET /sse`（建立 SSE 连接）
消息端点：`POST /messages/?session_id=<id>`（调用工具）

## Claude Code 配置

本服务以 SSE 传输模式运行，Claude Code 可通过 HTTP URL 方式接入。

### 方式一：命令行添加（推荐）

先在后台启动服务，再将 SSE URL 注册到 Claude Code：

```bash
# 1. 启动服务（后台运行）
uv run python main.py &
sleep 3

# 2. 添加到 Claude Code（全局）
claude mcp add xtdata-mcp --url http://127.0.0.1:8000/sse

# 3. 验证是否添加成功
claude mcp list
```

### 方式二：手动编辑配置文件

在 `~/.claude.json`（全局）或项目根目录 `.mcp.json`（项目级）中添加：

```json
{
  "mcpServers": {
    "xtdata-mcp": {
      "url": "http://127.0.0.1:8000/sse",
      "description": "迅投 xtquant 行情数据"
    }
  }
}
```

### 方式三：直接启动 MCP 服务器

如果 Claude Code 支持 stdio 模式，也可以用 uvicorn 作为载体：

```bash
# 启动服务
uvicorn src.xtdata_mcp.server:get_app --host 127.0.0.1 --port 8000 --log-level warning
```

### 验证

添加成功后，在 Claude Code 中确认连接正常：

```bash
claude mcp list
# 应该看到 xtdata-mcp 显示 Connected
```

之后即可在对话中直接调用行情工具，例如：

```
帮我查询 600000.SH 的最新日线行情
获取银行板块的所有成分股
查看上证指数的最新成分股权重
```

## 注意事项

- 使用前需确保 QMT 客户端**已登录运行**，且登录时需**勾选"独立交易"选项**，否则所有工具返回 `ok: false`
- 首次使用需先调用 `download_*` 系列工具下载本地数据
- 部分工具（如财务数据下载）数据量较大，调用时可能耗时较长
