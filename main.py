"""XtData MCP + XtTrader MCP 合并服务入口。"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time

from dotenv import load_dotenv
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from src.logging_setup import make_log_config

load_dotenv()

host = os.getenv("MCP_HOST", "127.0.0.1")
port = int(os.getenv("MCP_PORT", "8000"))
auth_enabled = os.getenv("MCP_AUTH_ENABLED", "false").strip().lower() in ("true", "1", "yes")
auth_token = os.getenv("MCP_AUTH_TOKEN", "")
trade_enabled = os.getenv("MCP_TRADE_ENABLED", "true").strip().lower() in ("true", "1", "yes")
log_dir = os.getenv("MCP_LOG_DIR", "logs")
log_level = os.getenv("MCP_LOG_LEVEL", "INFO").upper()
# 同时在途请求的最大并发数，保护 xtquant/QMT 后端；<=0 表示不限制
max_concurrency = int(os.getenv("MCP_MAX_CONCURRENCY", "8"))

_HEALTH_PATH = "/health"

# 应用日志统一使用 qmt.* 命名空间，与 MCP SDK 自身的 mcp.* logger 区分开
logger = logging.getLogger("qmt.request")


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


class ConcurrencyLimitMiddleware(BaseHTTPMiddleware):
    """在途请求并发数限制中间件。

    xtquant 背后是单个 QMT 终端，并发过高不会更快反而可能拖垮终端。
    超出上限时快速失败（503 + Retry-After），由客户端重试，避免长连接排队堆积。
    通过构造参数接收配置，便于测试时直接注入。
    """

    def __init__(self, app, *, max_concurrency: int = 8):
        super().__init__(app)
        self._max_concurrency = max_concurrency
        self._sem: asyncio.Semaphore | None = (
            asyncio.Semaphore(max_concurrency) if max_concurrency > 0 else None
        )
        self._in_flight = 0

    async def dispatch(self, request: Request, call_next) -> Response:
        # /health 探活不占用并发额度
        if request.url.path == _HEALTH_PATH or self._sem is None:
            return await call_next(request)

        if self._sem.locked():
            logger.warning(
                "concurrency limit reached (max=%s, in_flight=%s), rejecting %s %s",
                self._max_concurrency,
                self._in_flight,
                request.method,
                request.url.path,
            )
            return JSONResponse(
                {"detail": "Server busy, please retry later"},
                status_code=503,
                headers={"Retry-After": "2"},
            )

        async with self._sem:
            self._in_flight += 1
            try:
                return await call_next(request)
            finally:
                self._in_flight -= 1


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """请求耗时日志中间件。

    记录每个请求的 HTTP 方法、路径、状态码和总耗时（含流式响应体发送完成）；
    对 /mcp 的 POST 请求额外解析 JSON-RPC，记录 MCP 方法名与工具名，例如
    ``mcp=tools/call:get_stock_data``。/health 探活不记录，避免刷屏。
    """

    # 请求体超过该大小（字节）时跳过 MCP 方法解析，避免大报文解析开销
    _MAX_BODY_FOR_METHOD_PARSE = 256 * 1024

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path == _HEALTH_PATH:
            return await call_next(request)

        start = time.perf_counter()
        mcp_label = ""
        if request.method == "POST":
            mcp_label = await self._extract_mcp_label(request)

        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "%s %s%s | 500 | %.1fms (unhandled error)",
                request.method,
                request.url.path,
                mcp_label,
                elapsed_ms,
            )
            raise

        # call_next 返回的是流式响应，包装 body_iterator 以统计完整耗时
        # （工具执行时间主要体现在响应体生成阶段），客户端断开时 finally 也会记录
        response.body_iterator = self._timed_body_iterator(
            response.body_iterator, start, request, mcp_label, response.status_code
        )
        return response

    async def _timed_body_iterator(
        self, body_iterator, start: float, request: Request, mcp_label: str, status_code: int
    ):
        try:
            async for chunk in body_iterator:
                yield chunk
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "%s %s%s | %s | %.1fms",
                request.method,
                request.url.path,
                mcp_label,
                status_code,
                elapsed_ms,
            )

    async def _extract_mcp_label(self, request: Request) -> str:
        """解析 JSON-RPC 请求体，提取 MCP 方法名（及 tools/call 的工具名）。

        BaseHTTPMiddleware 会缓存已读取的请求体并回放给下游，不影响正常处理。
        任何解析失败都静默降级为空标签。
        """
        try:
            body = await request.body()
        except Exception:
            return ""
        if not body or len(body) > self._MAX_BODY_FOR_METHOD_PARSE:
            return ""
        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return ""

        messages = payload if isinstance(payload, list) else [payload]
        labels = []
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            method = msg.get("method")
            if not method:
                continue
            tool = ""
            params = msg.get("params")
            if isinstance(params, dict) and method == "tools/call" and params.get("name"):
                tool = f":{params['name']}"
            labels.append(f"{method}{tool}")

        return f" | mcp={','.join(labels)}" if labels else ""


async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    import uvicorn
    from src.xtdata_mcp.server import mcp as xtdata_mcp

    log_config = make_log_config(log_dir, log_level)

    if trade_enabled:
        from src.xttrade_mcp.server import mcp as xttrade_mcp
        # 将 xttrade_mcp 挂载到 xtdata_mcp 上，所有工具合并到同一服务
        xtdata_mcp.mount(xttrade_mcp)

    app = xtdata_mcp.http_app(
        transport="streamable-http",
        stateless_http=True,
        middleware=[
            # 顺序即洋葱模型外→内：耗时统计（最外层，度量完整链路）
            # → 鉴权（未授权请求不占用并发额度）→ 并发限制（最内层，保护 QMT 后端）
            Middleware(RequestTimingMiddleware),
            Middleware(BearerAuthMiddleware, auth_enabled=auth_enabled, auth_token=auth_token),
            Middleware(ConcurrencyLimitMiddleware, max_concurrency=max_concurrency),
        ],
    )

    # 通过 Starlette 底层路由注入 /health 端点
    app.routes.insert(0, Route("/health", health, methods=["GET"]))

    concurrency_desc = str(max_concurrency) if max_concurrency > 0 else "unlimited"
    print(
        f"Starting MCP server on {host}:{port} "
        f"(python: {sys.executable}, log dir: {log_dir}, "
        f"max concurrency: {concurrency_desc})",
        flush=True,
    )
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_config=log_config,
    )
