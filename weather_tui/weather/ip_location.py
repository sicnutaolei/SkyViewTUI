"""IP 定位（ip-api.com，异步）。"""

from __future__ import annotations

import httpx

_TIMEOUT = 5.0
_BASE_URL = "http://ip-api.com/json/"


async def get_location_by_ip() -> dict | None:
    """通过 IP 自动获取大致位置。

    成功返回 {"city", "country", "lat", "lon"}，失败返回 None。
    超时 5 秒。
    """
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(_BASE_URL)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return None

    if data.get("status") != "success":
        return None
    return {
        "city": data.get("city"),
        "country": data.get("country"),
        "lat": data.get("lat"),
        "lon": data.get("lon"),
    }
