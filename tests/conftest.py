"""
pytest fixtures - 使用 FastMCP Client HTTP/SSE 传输测试运行中的 MCP 服务。
"""
from __future__ import annotations

import json
from typing import Any

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

# MCP 服务地址
MCP_SERVER_URL = "http://127.0.0.1:8000/sse"


@pytest.fixture
async def mcp_client() -> Any:
    """每个测试创建新连接。"""
    async with Client(MCP_SERVER_URL) as client:
        yield client


async def call_tool(client: Client, tool_name: str, arguments: dict) -> dict[str, Any]:
    """
    通过 FastMCP Client HTTP/SSE 传输调用 tool。
    返回 {"ok": True/False, "data"/"error": ...} 格式。
    某些工具可能因数据序列化问题返回错误，这是 xtquant 数据本身的限制。
    """
    try:
        result = await client.call_tool(tool_name, arguments, raise_on_error=False)
    except ToolError as e:
        # 工具执行出错（可能是 xtquant 未配置或数据序列化问题）
        return {"ok": False, "error": str(e)}

    # 如果返回了数据
    if result.data is not None:
        return result.data

    # 如果 is_error 标志被设置
    if result.is_error:
        error_msg = "Unknown error"
        if result.content and len(result.content) > 0:
            text = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
            error_msg = text
        return {"ok": False, "error": error_msg}

    # 数据为 None 且没有错误标志
    if result.content and len(result.content) > 0:
        text = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"ok": False, "error": f"Non-JSON response: {text[:200]}"}

    return {"ok": False, "error": "No data returned"}