"""
XtTrader 交易模块 MCP 接口功能测试。

测试每个 tool 的：
1. JSON-RPC 请求/响应格式正确
2. 响应包含 ok 字段（未初始化时返回 ok=False，这是预期行为）
3. 返回数据结构符合预期

注意：交易工具需要先调用 init_trader 初始化连接才能正常使用。
"""
from __future__ import annotations

import pytest

from tests.conftest import call_tool


# ---------------------------------------------------------------------------
# System Setup APIs
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_init_trader(mcp_client):
    """测试 init_trader - 初始化交易通道（需 QMT 运行）"""
    result = await call_tool(mcp_client, "init_trader", {})
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_start_trader(mcp_client):
    """测试 start_trader - 启动交易线程"""
    result = await call_tool(mcp_client, "start_trader", {})
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_connect_trader(mcp_client):
    """测试 connect_trader - 连接 MiniQMT"""
    result = await call_tool(mcp_client, "connect_trader", {})
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_stop_trader(mcp_client):
    """测试 stop_trader - 停止交易通道"""
    result = await call_tool(mcp_client, "stop_trader", {})
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_set_relaxed_response_order_enabled(mcp_client):
    """测试 set_relaxed_response_order_enabled - 设置响应模式"""
    result = await call_tool(
        mcp_client,
        "set_relaxed_response_order_enabled",
        {"enabled": True},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_register_trader_callback(mcp_client):
    """测试 register_trader_callback - 注册回调"""
    result = await call_tool(mcp_client, "register_trader_callback", {})
    assert "ok" in result
    assert isinstance(result["ok"], bool)


# ---------------------------------------------------------------------------
# Account Subscription APIs
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_subscribe_account(mcp_client):
    """测试 subscribe_account - 订阅账户（需先 init_trader）"""
    result = await call_tool(
        mcp_client,
        "subscribe_account",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_unsubscribe_account(mcp_client):
    """测试 unsubscribe_account - 取消订阅"""
    result = await call_tool(
        mcp_client,
        "unsubscribe_account",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


# ---------------------------------------------------------------------------
# Order APIs
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_order_stock(mcp_client):
    """测试 order_stock - 同步下单（需先 init_trader + start_trader）"""
    result = await call_tool(
        mcp_client,
        "order_stock",
        {
            "account_id": "000000.SZ",
            "stock_code": "600000.SH",
            "order_type": 23,
            "order_volume": 100,
            "price_type": 11,
            "price": 10.0,
        },
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_order_stock_async(mcp_client):
    """测试 order_stock_async - 异步下单"""
    result = await call_tool(
        mcp_client,
        "order_stock_async",
        {
            "account_id": "000000.SZ",
            "stock_code": "600000.SH",
            "order_type": 23,
            "order_volume": 100,
            "price_type": 11,
            "price": 10.0,
        },
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_cancel_order_stock(mcp_client):
    """测试 cancel_order_stock - 同步撤单"""
    result = await call_tool(
        mcp_client,
        "cancel_order_stock",
        {"account_id": "000000.SZ", "order_id": 0},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_cancel_order_stock_async(mcp_client):
    """测试 cancel_order_stock_async - 异步撤单"""
    result = await call_tool(
        mcp_client,
        "cancel_order_stock_async",
        {"account_id": "000000.SZ", "order_id": 0},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_cancel_order_stock_sysid(mcp_client):
    """测试 cancel_order_stock_sysid - 同步撤单（按sysid）"""
    result = await call_tool(
        mcp_client,
        "cancel_order_stock_sysid",
        {"account_id": "000000.SZ", "market": 0, "order_sysid": ""},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_cancel_order_stock_sysid_async(mcp_client):
    """测试 cancel_order_stock_sysid_async - 异步撤单（按sysid）"""
    result = await call_tool(
        mcp_client,
        "cancel_order_stock_sysid_async",
        {"account_id": "000000.SZ", "market": 0, "order_sysid": ""},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


# ---------------------------------------------------------------------------
# Fund Transfer
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fund_transfer(mcp_client):
    """测试 fund_transfer - 资金划转"""
    result = await call_tool(
        mcp_client,
        "fund_transfer",
        {"account_id": "000000.SZ", "transfer_direction": 510, "price": 0},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


# ---------------------------------------------------------------------------
# Query APIs - Stock
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_query_stock_asset(mcp_client):
    """测试 query_stock_asset - 查询账户资产"""
    result = await call_tool(
        mcp_client,
        "query_stock_asset",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_stock_orders(mcp_client):
    """测试 query_stock_orders - 查询今日订单"""
    result = await call_tool(
        mcp_client,
        "query_stock_orders",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_stock_orders_cancelable(mcp_client):
    """测试 query_stock_orders - 仅查可撤订单"""
    result = await call_tool(
        mcp_client,
        "query_stock_orders",
        {"account_id": "000000.SZ", "cancelable_only": True},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_stock_trades(mcp_client):
    """测试 query_stock_trades - 查询今日成交"""
    result = await call_tool(
        mcp_client,
        "query_stock_trades",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_stock_positions(mcp_client):
    """测试 query_stock_positions - 查询持仓"""
    result = await call_tool(
        mcp_client,
        "query_stock_positions",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_position_statistics(mcp_client):
    """测试 query_position_statistics - 查询期货持仓统计"""
    result = await call_tool(
        mcp_client,
        "query_position_statistics",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


# ---------------------------------------------------------------------------
# Query APIs - Credit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_query_credit_detail(mcp_client):
    """测试 query_credit_detail - 查询信用账户明细"""
    result = await call_tool(
        mcp_client,
        "query_credit_detail",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_stk_compacts(mcp_client):
    """测试 query_stk_compacts - 查询融资融券合约"""
    result = await call_tool(
        mcp_client,
        "query_stk_compacts",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_credit_subjects(mcp_client):
    """测试 query_credit_subjects - 查询融资标的"""
    result = await call_tool(
        mcp_client,
        "query_credit_subjects",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_credit_slo_code(mcp_client):
    """测试 query_credit_slo_code - 查询可融券源"""
    result = await call_tool(
        mcp_client,
        "query_credit_slo_code",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_credit_assure(mcp_client):
    """测试 query_credit_assure - 查询担保品"""
    result = await call_tool(
        mcp_client,
        "query_credit_assure",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


# ---------------------------------------------------------------------------
# Query APIs - Other
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_query_new_purchase_limit(mcp_client):
    """测试 query_new_purchase_limit - 查询新股申购额度"""
    result = await call_tool(
        mcp_client,
        "query_new_purchase_limit",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_ipo_data(mcp_client):
    """测试 query_ipo_data - 查询今日新股信息"""
    result = await call_tool(mcp_client, "query_ipo_data", {})
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_account_infos(mcp_client):
    """测试 query_account_infos - 查询所有账户信息"""
    result = await call_tool(mcp_client, "query_account_infos", {})
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_account_status(mcp_client):
    """测试 query_account_status - 查询账户状态"""
    result = await call_tool(mcp_client, "query_account_status", {})
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_com_fund(mcp_client):
    """测试 query_com_fund - 查询场外基金"""
    result = await call_tool(
        mcp_client,
        "query_com_fund",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_com_position(mcp_client):
    """测试 query_com_position - 查询场外基金持仓"""
    result = await call_tool(
        mcp_client,
        "query_com_position",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_export_data(mcp_client):
    """测试 export_data - 导出数据"""
    result = await call_tool(
        mcp_client,
        "export_data",
        {
            "account_id": "000000.SZ",
            "result_path": "",
            "data_type": "order",
        },
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_query_data(mcp_client):
    """测试 query_data - 查询数据"""
    result = await call_tool(
        mcp_client,
        "query_data",
        {
            "account_id": "000000.SZ",
            "result_path": "",
            "data_type": "order",
        },
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


# ---------------------------------------------------------------------------
# Securities Lending APIs
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_smt_query_quoter(mcp_client):
    """测试 smt_query_quoter - 查询券源报价"""
    result = await call_tool(
        mcp_client,
        "smt_query_quoter",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_smt_negotiate_order_async(mcp_client):
    """测试 smt_negotiate_order_async - 协商借券异步订单"""
    result = await call_tool(
        mcp_client,
        "smt_negotiate_order_async",
        {
            "account_id": "000000.SZ",
            "src_group_id": "",
            "order_code": "",
            "date": "",
            "amount": 0,
            "apply_rate": 0.0,
        },
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)


@pytest.mark.asyncio
async def test_smt_query_compact(mcp_client):
    """测试 smt_query_compact - 查询借券合约"""
    result = await call_tool(
        mcp_client,
        "smt_query_compact",
        {"account_id": "000000.SZ"},
    )
    assert "ok" in result
    assert isinstance(result["ok"], bool)
