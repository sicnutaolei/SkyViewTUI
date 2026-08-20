"""地名 → 经纬度（Open-Meteo Geocoding API，异步）。

v1.1：新增 CITY_CN 城市中英映射，在返回结果中附带 cn_name（中文名）。
"""

from __future__ import annotations

import httpx

_TIMEOUT = 15.0
_BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"

# 常见城市英文名 → 中文名（可扩展；未命中则仅显示英文）。
CITY_CN: dict[str, str] = {
    "Deyang": "德阳",
    "Chengdu": "成都",
    "Beijing": "北京",
    "Shanghai": "上海",
    "Guangzhou": "广州",
    "Shenzhen": "深圳",
    "Hangzhou": "杭州",
    "Nanjing": "南京",
    "Wuhan": "武汉",
    "Chongqing": "重庆",
    "Xian": "西安",
    "Tianjin": "天津",
    "Suzhou": "苏州",
    "Changsha": "长沙",
    "Kunming": "昆明",
    "Qingdao": "青岛",
    "Xiamen": "厦门",
    "Dalian": "大连",
    "Hong Kong": "香港",
    "Macao": "澳门",
    "Taipei": "台北",
    # 国际常见城市
    "Tokyo": "东京",
    "New York": "纽约",
    "London": "伦敦",
    "Paris": "巴黎",
    "Singapore": "新加坡",
    "Sydney": "悉尼",
    "Los Angeles": "洛杉矶",
    "Berlin": "柏林",
    "Moscow": "莫斯科",
    "Dubai": "迪拜",
    "Bangkok": "曼谷",
    "Seoul": "首尔",
}


def get_city_cn(name: str | None) -> str | None:
    """将英文城市名转换为中文名；未命中返回 None。"""
    if not name:
        return None
    return CITY_CN.get(name)


async def geocode(city_name: str) -> dict | None:
    """将城市名解析为经纬度。

    成功返回 {"name", "country", "lat", "lon", "cn_name?"}，
    失败 / 未找到返回 None。cn_name 仅在命中 CITY_CN 时附带。
    """
    if not city_name:
        return None
    params = {"name": city_name, "count": 1, "language": "en"}
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(_BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return None

    results = data.get("results")
    if not results:
        return None
    r = results[0]
    result = {
        "name": r.get("name"),
        "country": r.get("country"),
        "lat": r.get("latitude"),
        "lon": r.get("longitude"),
    }
    cn = CITY_CN.get(r.get("name"))
    if cn:
        result["cn_name"] = cn
    return result
