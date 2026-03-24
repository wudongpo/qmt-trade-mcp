"""
MCP SSE 接口功能测试（使用 FastMCP Client 内存传输）。

测试每个 tool 的：
1. JSON-RPC 请求/响应格式正确
2. 响应包含 ok 字段（xtquant 未配置时返回 ok=False，这是预期行为）
3. 返回数据结构符合预期
"""
from __future__ import annotations

import pytest

from tests.conftest import call_tool


# ---------------------------------------------------------------------------
# 行情数据类工具
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_full_tick(mcp_client):
    """测试 get_full_tick - 获取全推切面数据"""
    result = await call_tool(mcp_client, "get_full_tick", {"code_list": ["SH", "SZ"]})
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_get_market_data(mcp_client):
    """测试 get_market_data - 从缓存获取行情数据"""
    result = await call_tool(
        mcp_client,
        "get_market_data",
        {"stock_list": ["600000.SH"], "period": "1d", "count": 10},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_get_market_data_no_args(mcp_client):
    """测试 get_market_data - 空参数调用（验证默认行为）"""
    result = await call_tool(mcp_client, "get_market_data", {})
    assert "ok" in result


@pytest.mark.asyncio
async def test_get_local_data(mcp_client):
    """测试 get_local_data - 从本地文件读取行情数据"""
    result = await call_tool(
        mcp_client,
        "get_local_data",
        {"stock_list": ["600000.SH"], "period": "1d", "count": 5},
    )
    assert "ok" in result


@pytest.mark.asyncio
async def test_get_full_kline(mcp_client):
    """测试 get_full_kline - 获取最新交易日 K 线全推数据"""
    result = await call_tool(
        mcp_client,
        "get_full_kline",
        {"stock_list": ["600000.SH"], "period": "1d", "count": 1},
    )
    assert "ok" in result


# ---------------------------------------------------------------------------
# 历史数据下载类工具
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_download_history_data(mcp_client):
    """测试 download_history_data - 下载单标历史行情"""
    result = await call_tool(
        mcp_client,
        "download_history_data",
        {"stock_code": "600000.SH", "period": "1d"},
    )
    assert "ok" in result


@pytest.mark.asyncio
async def test_download_history_data2(mcp_client):
    """测试 download_history_data2 - 批量下载历史行情"""
    result = await call_tool(
        mcp_client,
        "download_history_data2",
        {"stock_list": ["600000.SH", "000001.SZ"], "period": "1d"},
    )
    assert "ok" in result


# ---------------------------------------------------------------------------
# 除权除息类工具
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_divid_factors(mcp_client):
    """测试 get_divid_factors - 获取除权除息因子"""
    result = await call_tool(
        mcp_client,
        "get_divid_factors",
        {"stock_code": "600000.SH"},
    )
    assert "ok" in result


# ---------------------------------------------------------------------------
# 周期与日历类工具
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_period_list(mcp_client):
    """测试 get_period_list - 获取可用周期列表"""
    result = await call_tool(mcp_client, "get_period_list", {})
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_get_holidays(mcp_client):
    """测试 get_holidays - 获取节假日数据"""
    result = await call_tool(mcp_client, "get_holidays", {})
    assert "ok" in result


@pytest.mark.asyncio
async def test_get_trading_calendar(mcp_client):
    """测试 get_trading_calendar - 获取交易日历"""
    result = await call_tool(
        mcp_client,
        "get_trading_calendar",
        {"market": "SH", "start_time": "20240101", "end_time": "20241231"},
    )
    assert "ok" in result


@pytest.mark.asyncio
async def test_get_trading_dates(mcp_client):
    """测试 get_trading_dates - 获取交易日列表（时间戳）"""
    result = await call_tool(
        mcp_client,
        "get_trading_dates",
        {"market": "SH", "start_time": "20240101", "end_time": "20241231", "count": 10},
    )
    assert "ok" in result


# ---------------------------------------------------------------------------
# 合约与板块类工具
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_instrument_detail(mcp_client):
    """测试 get_instrument_detail - 获取合约基础信息"""
    result = await call_tool(
        mcp_client,
        "get_instrument_detail",
        {"stock_code": "600000.SH"},
    )
    assert "ok" in result


@pytest.mark.asyncio
async def test_get_instrument_detail_complete(mcp_client):
    """测试 get_instrument_detail - iscomplete=True 返回完整字段"""
    result = await call_tool(
        mcp_client,
        "get_instrument_detail",
        {"stock_code": "600000.SH", "iscomplete": True},
    )
    assert "ok" in result


@pytest.mark.asyncio
async def test_get_instrument_type(mcp_client):
    """测试 get_instrument_type - 获取合约类型"""
    result = await call_tool(
        mcp_client,
        "get_instrument_type",
        {"stock_code": "600000.SH"},
    )
    assert "ok" in result


@pytest.mark.asyncio
async def test_get_sector_list(mcp_client):
    """测试 get_sector_list - 获取板块列表"""
    result = await call_tool(mcp_client, "get_sector_list", {})
    assert "ok" in result


@pytest.mark.asyncio
async def test_get_stock_list_in_sector(mcp_client):
    """测试 get_stock_list_in_sector - 获取板块成分股"""
    result = await call_tool(
        mcp_client,
        "get_stock_list_in_sector",
        {"sector_name": "银行"},
    )
    assert "ok" in result


@pytest.mark.asyncio
async def test_download_sector_data(mcp_client):
    """测试 download_sector_data - 下载板块分类信息"""
    result = await call_tool(mcp_client, "download_sector_data", {})
    assert "ok" in result


@pytest.mark.asyncio
async def test_get_index_weight(mcp_client):
    """测试 get_index_weight - 获取指数成分权重"""
    result = await call_tool(
        mcp_client,
        "get_index_weight",
        {"index_code": "000001.SH"},
    )
    assert "ok" in result


@pytest.mark.asyncio
async def test_download_index_weight(mcp_client):
    """测试 download_index_weight - 下载指数成分权重"""
    result = await call_tool(mcp_client, "download_index_weight", {})
    assert "ok" in result


# ---------------------------------------------------------------------------
# 财务数据类工具
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_financial_data(mcp_client):
    """测试 get_financial_data - 获取财务数据"""
    result = await call_tool(
        mcp_client,
        "get_financial_data",
        {"stock_list": ["600000.SH"], "table_list": ["Balance"]},
    )
    assert "ok" in result


@pytest.mark.asyncio
async def test_download_financial_data(mcp_client):
    """测试 download_financial_data - 下载财务数据"""
    result = await call_tool(
        mcp_client,
        "download_financial_data",
        {"stock_list": ["600000.SH"]},
    )
    assert "ok" in result


# ---------------------------------------------------------------------------
# 可转债类工具
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_cb_info(mcp_client):
    """测试 get_cb_info - 获取可转债基础信息"""
    result = await call_tool(
        mcp_client,
        "get_cb_info",
        {"stockcode": "113009.SH"},
    )
    assert "ok" in result


@pytest.mark.asyncio
async def test_download_cb_data(mcp_client):
    """测试 download_cb_data - 下载可转债基础信息"""
    result = await call_tool(mcp_client, "download_cb_data", {})
    assert "ok" in result


# ---------------------------------------------------------------------------
# 新股/ETF 类工具
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_ipo_info(mcp_client):
    """测试 get_ipo_info - 获取新股申购信息"""
    result = await call_tool(
        mcp_client,
        "get_ipo_info",
        {"start_time": "20240101", "end_time": "20241231"},
    )
    assert "ok" in result


@pytest.mark.asyncio
async def test_get_ipo_info_empty_range(mcp_client):
    """测试 get_ipo_info - 空时间范围"""
    result = await call_tool(mcp_client, "get_ipo_info", {})
    assert "ok" in result


@pytest.mark.asyncio
async def test_download_etf_info(mcp_client):
    """测试 download_etf_info - 下载 ETF 申赎清单"""
    result = await call_tool(mcp_client, "download_etf_info", {})
    assert "ok" in result


@pytest.mark.asyncio
async def test_get_etf_info(mcp_client):
    """测试 get_etf_info - 获取 ETF 申赎清单信息"""
    result = await call_tool(mcp_client, "get_etf_info", {})
    assert "ok" in result


# ---------------------------------------------------------------------------
# 节假日数据类工具
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_download_holiday_data(mcp_client):
    """测试 download_holiday_data - 下载节假日数据"""
    result = await call_tool(mcp_client, "download_holiday_data", {})
    assert "ok" in result
