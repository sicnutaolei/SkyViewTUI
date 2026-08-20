"""Open-Meteo 预报 API 调用（异步）。"""

from __future__ import annotations

import httpx

_TIMEOUT = 15.0

_CURRENT_FIELDS = (
    "temperature_2m,weather_code,apparent_temperature,"
    "relative_humidity_2m,wind_speed_10m"
)
_HOURLY_FIELDS = "temperature_2m,weather_code,precipitation_probability"
_DAILY_FIELDS = "weather_code,temperature_2m_max,temperature_2m_min"

_BASE_URL = "https://api.open-meteo.com/v1/forecast"


async def fetch_weather(lat: float, lon: float, units: str = "celsius") -> dict:
    """获取指定经纬度的天气预报数据。

    返回 Open-Meteo 原始 JSON（dict），包含 current / hourly / daily 三部分。
    超时 15 秒；网络错误会向上抛出，由调用方处理。
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": _CURRENT_FIELDS,
        "hourly": _HOURLY_FIELDS,
        "daily": _DAILY_FIELDS,
        "timezone": "auto",
        "forecast_days": 3,
        "temperature_unit": units,
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(_BASE_URL, params=params)
        resp.raise_for_status()
        return resp.json()
