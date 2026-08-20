"""测试公共工具：用假 AsyncClient 模拟 httpx 网络请求。"""

import httpx


class FakeResponse:
    def __init__(self, json_data, status: int = 200):
        self._json = json_data
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("http error", request=None, response=None)

    def json(self):
        return self._json


def make_async_client(routes: dict):
    """根据 URL 子串 -> 返回 JSON 的映射，构造一个假的 AsyncClient 类。"""

    class _FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def get(self, url: str, params=None):
            for key, payload in routes.items():
                if key in url:
                    status = 200
                    if isinstance(payload, tuple):
                        payload, status = payload
                    return FakeResponse(payload, status)
            return FakeResponse({}, 404)

    return _FakeClient


def patch_async_client(monkeypatch, routes: dict):
    """把 httpx.AsyncClient 替换成假实现（按 routes 路由）。"""
    monkeypatch.setattr(httpx, "AsyncClient", make_async_client(routes))
