"""XtData MCP SSE 服务入口。直接调用 uvicorn 启动，不走 subprocess 递归。"""
from __future__ import annotations

import os

host = os.getenv("MCP_HOST", "127.0.0.1")
port = int(os.getenv("MCP_PORT", "8000"))

if __name__ == "__main__":
    import uvicorn
    from src.xtdata_mcp.server import get_app

    uvicorn.run(get_app(), host=host, port=port)
