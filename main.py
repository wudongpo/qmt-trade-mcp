"""XtData MCP + XtTrader MCP 合并服务入口。"""
from __future__ import annotations

import os

host = os.getenv("MCP_HOST", "127.0.0.1")
port = int(os.getenv("MCP_PORT", "8000"))

if __name__ == "__main__":
    import uvicorn
    from src.xtdata_mcp.server import mcp as xtdata_mcp
    from src.xttrade_mcp.server import mcp as xttrade_mcp

    # 将 xttrade_mcp 挂载到 xtdata_mcp 上，所有工具合并到同一服务
    xtdata_mcp.mount(xttrade_mcp)

    uvicorn.run(xtdata_mcp.http_app(transport="sse"), host=host, port=port)
