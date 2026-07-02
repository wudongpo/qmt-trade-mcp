"""Bearer Auth 中间件和 /health 端点测试。"""
from __future__ import annotations

import pytest
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from main import BearerAuthMiddleware
from src.xtdata_mcp.server import mcp as xtdata_mcp


def _make_app(auth_enabled: bool, auth_token: str):
    """构建带 auth 中间件和 /health 端点的测试 app。"""
    app = xtdata_mcp.http_app(
        transport="streamable-http",
        middleware=[
            Middleware(BearerAuthMiddleware, auth_enabled=auth_enabled, auth_token=auth_token)
        ],
    )

    async def health(request):
        return JSONResponse({"status": "ok"})

    app.routes.insert(0, Route("/health", health, methods=["GET"]))
    return app


@pytest.fixture
def auth_enabled_client():
    """auth=enabled, token=test-secret 的 TestClient。"""
    app = _make_app(auth_enabled=True, auth_token="test-secret")
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture
def auth_disabled_client():
    """auth=disabled 的 TestClient。"""
    app = _make_app(auth_enabled=False, auth_token="")
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


class TestHealthEndpoint:
    """测试 /health 端点。"""

    def test_health_without_auth(self, auth_enabled_client):
        """auth 启用时 /health 无需 token 即可访问。"""
        response = auth_enabled_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_health_with_auth_disabled(self, auth_disabled_client):
        """auth 禁用时 /health 正常返回。"""
        response = auth_disabled_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestBearerAuth:
    """测试 Bearer Token 授权。"""

    def test_mcp_endpoint_no_token_returns_401(self, auth_enabled_client):
        """无 token 访问 /mcp 返回 401。"""
        response = auth_enabled_client.get("/mcp")
        assert response.status_code == 401
        assert response.json() == {"detail": "Missing or invalid Authorization header"}

    def test_mcp_endpoint_invalid_token_returns_401(self, auth_enabled_client):
        """无效 token 返回 401。"""
        response = auth_enabled_client.get(
            "/mcp", headers={"Authorization": "Bearer wrong-token"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid token"}

    def test_mcp_endpoint_valid_token_passes(self, auth_enabled_client):
        """有效 token 通过鉴权。"""
        response = auth_enabled_client.get(
            "/mcp", headers={"Authorization": "Bearer test-secret"}
        )
        # 鉴权通过后 MCP streamable-http 对 GET 返回 406，不是 401
        assert response.status_code != 401

    def test_mcp_endpoint_auth_disabled_passes(self, auth_disabled_client):
        """auth 禁用时无需 token 即可访问。"""
        response = auth_disabled_client.get("/mcp")
        assert response.status_code != 401
