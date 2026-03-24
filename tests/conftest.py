"""
pytest fixtures - 使用 FastMCP Client in-memory transport 测试。
"""
from __future__ import annotations

from typing import Any

import pytest
from fastmcp import Client

from src.xtdata_mcp.server import mcp


@pytest.fixture(scope="session")
async def mcp_client() -> Any:
    """Session 级连接，所有测试复用同一 xtdata 连接。"""
    async with Client(mcp) as client:
        yield client


async def call_tool(client: Client, tool_name: str, arguments: dict) -> dict[str, Any]:
    """
    通过 FastMCP Client 调用 tool，返回 {"ok": True/False, "data"/"error": ...} 格式。
    """
    result = await client.call_tool(tool_name, arguments)
    return result.data
