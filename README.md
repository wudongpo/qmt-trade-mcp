# qmt-trade-mcp

基于 [FastMCP](https://github.com/jlowin/fastmcp) 框架构建的 MCP（Model Context Protocol）服务，封装迅投 `xtquant` 行情数据接口和交易接口，通过 SSE 传输协议提供行情查询和交易能力。

**免责声明：AI 可能会犯错，用户需自行承担交易带来的损失。本服务仅提供接口封装，不对交易结果负责。**

**联系方式（微信）：** gold98986868、Az184114

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
├── main.py                     # 服务入口，uvicorn 加载合并后的 MCP 应用
├── pyproject.toml              # 项目配置及依赖
├── src/
│   ├── xtdata_mcp/             # 行情数据模块
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   └── server.py            # 21 个行情数据 tools
│   └── xttrade_mcp/            # 交易模块
│       ├── __init__.py
│       ├── __main__.py
│       └── server.py            # 37 个交易 tools
└── tests/
    ├── __init__.py
    ├── conftest.py            # pytest fixtures（HTTP/SSE 传输测试客户端）
    ├── test_server.py         # 行情 tool 功能测试
    └── test_trader.py         # 交易 tool 功能测试
```

## 提供的 MCP Tools（共 58 个）

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

### 合约与板块

| Tool | 说明 |
|------|------|
| `get_instrument_detail` | 获取合约详细基础信息 |
| `get_instrument_type` | 判断合约类型（股票/指数/基金/ETF） |
| `get_sector_list` | 获取所有可用板块列表 |
| `get_stock_list_in_sector` | 获取指定板块的成分股列表 |
| `get_index_weight` | 获取指数成分股及其权重 |
| `download_index_weight` | 下载指数成分权重数据 |

### 财务数据

| Tool | 说明 |
|------|------|
| `get_financial_data` | 获取财务数据（资产负债表/利润表等） |

### 可转债

| Tool | 说明 |
|------|------|
| `get_cb_info` | 获取可转债基础信息 |

### 新股 / ETF

| Tool | 说明 |
|------|------|
| `get_ipo_info` | 获取新股申购信息 |
| `get_etf_info` | 获取 ETF 申赎清单信息 |

---

## 交易模块 MCP Tools（37 个）

**注意：交易工具需要先调用 `init_trader` 初始化连接，并保持 QMT 客户端登录运行。**

### 系统设置

| Tool | 说明 |
|------|------|
| `init_trader` | 初始化交易通道并连接到 MiniQMT |
| `start_trader` | 启动交易线程 |
| `connect_trader` | 连接 MiniQMT |
| `stop_trader` | 停止交易通道 |
| `subscribe_account` | 订阅账户信息 |
| `unsubscribe_account` | 取消订阅账户 |
| `set_relaxed_response_order_enabled` | 设置是否启用专用线程处理订单响应 |
| `register_trader_callback` | 注册交易回调处理器 |

### 下单 / 撤单

| Tool | 说明 |
|------|------|
| `order_stock` | 同步下单（返回 order_id） |
| `order_stock_async` | 异步下单（返回 seq） |
| `cancel_order_stock` | 同步撤单（按 order_id） |
| `cancel_order_stock_async` | 异步撤单（按 order_id） |
| `cancel_order_stock_sysid` | 同步撤单（按 sysid） |
| `cancel_order_stock_sysid_async` | 异步撤单（按 sysid） |
| `fund_transfer` | 资金划转（普通/快速资金互转） |

### 查询 - 股票账户

| Tool | 说明 |
|------|------|
| `query_stock_asset` | 查询账户资产 |
| `query_stock_orders` | 查询今日订单 |
| `query_stock_trades` | 查询今日成交 |
| `query_stock_positions` | 查询持仓 |
| `query_position_statistics` | 查询期货持仓统计 |

### 查询 - 信用账户

| Tool | 说明 |
|------|------|
| `query_credit_detail` | 查询信用账户明细 |
| `query_stk_compacts` | 查询融资融券合约 |
| `query_credit_subjects` | 查询融资标的 |
| `query_credit_slo_code` | 查询可融券源 |
| `query_credit_assure` | 查询担保品 |

### 查询 - 其他

| Tool | 说明 |
|------|------|
| `query_new_purchase_limit` | 查询新股申购额度 |
| `query_ipo_data` | 查询今日新股信息 |
| `query_account_infos` | 查询所有账户信息 |
| `query_account_status` | 查询账户状态 |
| `query_com_fund` | 查询场外基金 |
| `query_com_position` | 查询场外基金持仓 |
| `export_data` | 导出数据到文件 |
| `query_data` | 查询并读取数据 |

### 券源借券

| Tool | 说明 |
|------|------|
| `smt_query_quoter` | 查询券源报价 |
| `smt_negotiate_order_async` | 协商借券异步订单 |
| `smt_query_compact` | 查询借券合约 |

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
# 运行行情 tool 功能测试（需先启动 MCP 服务）
uv run pytest tests/test_server.py -v

# 运行交易 tool 功能测试（需先启动 MCP 服务）
uv run pytest tests/test_trader.py -v

# 运行所有测试
uv run pytest tests/ -v
```

测试使用 FastMCP Client HTTP/SSE 传输连接运行中的 MCP 服务（`http://127.0.0.1:8000/sse`），每个测试调用真实 xtquant 接口验证功能正常。

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
    "xtquant-mcp": {
      "url": "http://127.0.0.1:8000/sse",
      "description": "迅投 xtquant 行情数据 + 交易接口"
    }
  }
}
```

### 方式三：直接启动 MCP 服务器

如果 Claude Code 支持 stdio 模式，也可以用 uvicorn 作为载体：

```bash
# 启动合并后的服务（行情+交易）
uvicorn main:app --host 127.0.0.1 --port 8000 --log-level warning
```

### 验证

添加成功后，在 Claude Code 中确认连接正常：

```bash
claude mcp list
# 应该看到 xtdata-mcp 显示 Connected
```

之后即可在对话中直接调用工具，例如：

```
帮我查询 600000.SH 的最新日线行情
获取银行板块的所有成分股
查看上证指数的最新成分股权重

帮我初始化交易通道
查询我的账户资产
买入 600000.SH 100股，价格 10.0元
```

## 注意事项

- 使用交易功能前需确保 QMT 客户端**已登录运行**，且登录时需**勾选"独立交易"选项**，否则交易工具返回 `ok: false`
- 首次使用需先调用 `download_*` 系列工具下载本地数据
- 部分工具（如 `download_history_data2`、`download_index_weight`）数据量较大，调用时可能耗时较长
- **交易为高风险操作，下单前请确认账户、股票代码、价格、数量等参数正确无误**
- 市价单仅在实盘交易有效，模拟交易不支持市价单
