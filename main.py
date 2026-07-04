"""XtData MCP + XtTrader MCP 合并服务入口。"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

load_dotenv()

host = os.getenv("MCP_HOST", "127.0.0.1")
port = int(os.getenv("MCP_PORT", "8000"))
auth_enabled = os.getenv("MCP_AUTH_ENABLED", "false").strip().lower() in ("true", "1", "yes")
auth_token = os.getenv("MCP_AUTH_TOKEN", "")
trade_enabled = os.getenv("MCP_TRADE_ENABLED", "true").strip().lower() in ("true", "1", "yes")

_HEALTH_PATH = "/health"


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Bearer Token 授权中间件。

    通过构造参数接收配置，便于测试时直接注入不同的 auth 设置。
    """

    def __init__(self, app, *, auth_enabled: bool = False, auth_token: str = ""):
        super().__init__(app)
        self._auth_enabled = auth_enabled
        self._auth_token = auth_token

    async def dispatch(self, request: Request, call_next) -> Response:
        # /health 端点免授权
        if request.url.path == _HEALTH_PATH:
            return await call_next(request)

        # 授权关闭时全部放行
        if not self._auth_enabled:
            return await call_next(request)

        # 验证 Bearer Token
        authorization: str = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Missing or invalid Authorization header"},
                status_code=401,
            )
        token = authorization[len("Bearer "):]
        if token != self._auth_token:
            return JSONResponse(
                {"detail": "Invalid token"},
                status_code=401,
            )

        return await call_next(request)


async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    import uvicorn
    from src.xtdata_mcp.server import mcp as xtdata_mcp

    if trade_enabled:
        from src.xttrade_mcp.server import mcp as xttrade_mcp
        # 将 xttrade_mcp 挂载到 xtdata_mcp 上，所有工具合并到同一服务
        xtdata_mcp.mount(xttrade_mcp)

    app = xtdata_mcp.http_app(
        transport="streamable-http",
        stateless_http=True,
        middleware=[
            Middleware(BearerAuthMiddleware, auth_enabled=auth_enabled, auth_token=auth_token)
        ],
    )

    # 通过 Starlette 底层路由注入 /health 端点
    app.routes.insert(0, Route("/health", health, methods=["GET"]))

    uvicorn.run(app, host=host, port=port)
