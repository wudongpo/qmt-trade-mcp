"""并发限制与请求耗时日志中间件测试。"""
from __future__ import annotations

import asyncio
import logging

import httpx
import pytest
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from starlette.routing import Route

from main import ConcurrencyLimitMiddleware, RequestTimingMiddleware

_HEALTH_PATH = "/health"


async def health(request):
    return JSONResponse({"status": "ok"})


async def slow(request):
    """模拟慢速工具调用。"""
    await asyncio.sleep(0.3)
    return JSONResponse({"status": "ok"})


async def echo(request):
    """回显请求体，用于验证中间件读取 body 后下游仍能收到。"""
    body = await request.body()
    return JSONResponse({"received": body.decode()})


def _make_app(*middlewares) -> Starlette:
    return Starlette(
        routes=[
            Route(_HEALTH_PATH, health, methods=["GET"]),
            Route("/slow", slow, methods=["GET"]),
            Route("/echo", echo, methods=["POST"]),
        ],
        middleware=list(middlewares),
    )


@pytest.fixture
async def concurrency_client():
    app = _make_app(Middleware(ConcurrencyLimitMiddleware, max_concurrency=1))
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def unlimited_client():
    app = _make_app(Middleware(ConcurrencyLimitMiddleware, max_concurrency=0))
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def timing_client():
    app = _make_app(Middleware(RequestTimingMiddleware))
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


class TestConcurrencyLimit:
    """并发限制中间件。"""

    async def test_excess_concurrency_returns_503(self, concurrency_client):
        """max=1 时 3 个并发请求中超出的请求快速失败 503。"""
        async def get_slow():
            return await concurrency_client.get("/slow")

        results = await asyncio.gather(*[get_slow() for _ in range(3)])
        statuses = sorted(r.status_code for r in results)
        assert 200 in statuses
        assert 503 in statuses

    async def test_503_has_retry_after_header(self, concurrency_client):
        """503 响应携带 Retry-After 头。"""
        async def get_slow():
            return await concurrency_client.get("/slow")

        results = await asyncio.gather(*[get_slow() for _ in range(2)])
        rejected = [r for r in results if r.status_code == 503]
        assert rejected, "应当至少有一个请求被 503 拒绝"
        assert rejected[0].headers.get("Retry-After") == "2"
        assert rejected[0].json() == {"detail": "Server busy, please retry later"}

    async def test_health_not_counted(self, concurrency_client):
        """/health 不占用并发额度，限流时仍可访问。"""
        async def get_slow():
            return await concurrency_client.get("/slow")

        slow_task = asyncio.create_task(get_slow())
        await asyncio.sleep(0.05)  # 确保 /slow 已占用唯一个并发位

        health_resp = await concurrency_client.get(_HEALTH_PATH)
        assert health_resp.status_code == 200

        slow_resp = await slow_task
        assert slow_resp.status_code == 200

    async def test_unlimited_when_max_zero(self, unlimited_client):
        """max_concurrency=0 时不限制，所有并发请求均成功。"""
        results = await asyncio.gather(*[unlimited_client.get("/slow") for _ in range(3)])
        assert all(r.status_code == 200 for r in results)


class TestRequestTiming:
    """请求耗时日志中间件。"""

    async def test_logs_duration_with_mcp_method(self, timing_client, caplog):
        """POST /mcp 风格请求记录耗时与 JSON-RPC 方法名、工具名。"""
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "get_stock_data", "arguments": {"code": "000001"}},
            "id": 1,
        }
        with caplog.at_level(logging.INFO, logger="qmt.request"):
            resp = await timing_client.post("/echo", json=payload)

        assert resp.status_code == 200
        # 下游仍能收到完整请求体（中间件读取后回放）
        assert "get_stock_data" in resp.json()["received"]

        log_text = caplog.text
        assert "POST /echo" in log_text
        assert "mcp=tools/call:get_stock_data" in log_text
        assert "200" in log_text
        assert "ms" in log_text

    async def test_health_not_logged(self, timing_client, caplog):
        """/health 探活不记录耗时日志。"""
        with caplog.at_level(logging.INFO, logger="qmt.request"):
            resp = await timing_client.get(_HEALTH_PATH)

        assert resp.status_code == 200
        assert "/health" not in caplog.text

    async def test_non_json_body_degrades_gracefully(self, timing_client, caplog):
        """非 JSON 请求体不影响请求处理，日志中无 mcp 标签。"""
        with caplog.at_level(logging.INFO, logger="qmt.request"):
            resp = await timing_client.post("/echo", content=b"not-json")

        assert resp.status_code == 200
        assert "mcp=" not in caplog.text
        assert "POST /echo" in caplog.text

    async def test_batch_request_logs_all_methods(self, timing_client, caplog):
        """JSON-RPC 批量请求记录所有方法名。"""
        payload = [
            {"jsonrpc": "2.0", "method": "initialize", "id": 1},
            {"jsonrpc": "2.0", "method": "tools/list", "id": 2},
        ]
        with caplog.at_level(logging.INFO, logger="qmt.request"):
            resp = await timing_client.post("/echo", json=payload)

        assert resp.status_code == 200
        assert "mcp=initialize,tools/list" in caplog.text
