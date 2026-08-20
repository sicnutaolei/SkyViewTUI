"""WMO 天气代码 → 图标 / 英文描述 / 中文描述 / 背景色 映射。

参考 Open-Meteo 文档：
https://open-meteo.com/en/docs  (WMO Weather interpretation codes)

v1.1：WEATHER_MAP 升级为三元组 (icon, en_desc, cn_desc)，并新增柔和背景色
（十六进制），以及 get_cn_desc() / get_en_desc() / get_icon() 辅助函数。
"""

from __future__ import annotations

# (code) -> (icon, en_desc, cn_desc)
WEATHER_MAP: dict[int, tuple[str, str, str]] = {
    0: ("☀️", "Clear sky", "晴"),
    1: ("🌤️", "Mainly clear", "晴间多云"),
    2: ("⛅", "Partly cloudy", "多云"),
    3: ("☁️", "Overcast", "阴"),
    45: ("🌫️", "Fog", "雾"),
    48: ("🌫️", "Rime fog", "雾凇"),
    51: ("🌦️", "Light drizzle", "小毛毛雨"),
    53: ("🌦️", "Moderate drizzle", "中毛毛雨"),
    55: ("🌧️", "Dense drizzle", "大毛毛雨"),
    56: ("🌧️", "Freezing drizzle", "冻毛毛雨"),
    57: ("🌧️", "Heavy freezing drizzle", "强冻毛毛雨"),
    61: ("🌦️", "Slight rain", "小雨"),
    63: ("🌧️", "Moderate rain", "中雨"),
    65: ("🌧️", "Heavy rain", "大雨"),
    66: ("🌧️", "Freezing rain", "冻雨"),
    67: ("🌧️", "Heavy freezing rain", "强冻雨"),
    71: ("🌨️", "Slight snow", "小雪"),
    73: ("🌨️", "Moderate snow", "中雪"),
    75: ("❄️", "Heavy snow", "大雪"),
    77: ("🌨️", "Snow grains", "雪粒"),
    80: ("🌦️", "Rain showers", "阵雨"),
    81: ("🌧️", "Moderate showers", "中阵雨"),
    82: ("🌧️", "Violent showers", "强阵雨"),
    85: ("🌨️", "Light snow shower", "小阵雪"),
    86: ("❄️", "Heavy snow shower", "大阵雪"),
    95: ("⛈️", "Thunderstorm", "雷暴"),
    96: ("⛈️", "Thunderstorm with hail", "雷暴伴冰雹"),
    99: ("⛈️", "Thunderstorm with hail", "雷暴伴冰雹"),
}

# 向后兼容别名
WEATHER_ICON_MAP = WEATHER_MAP

DEFAULT = ("🌡️", "Unknown", "未知")

# 柔和背景色（十六进制），随天气类型变化。
# 相比于 v1.0 的高饱和色名，这里采用深色专业调色板，对比舒适不刺眼。
_BG_SUNNY = "#1a3a5a"   # 晴：深蓝
_BG_CLOUDY = "#3a3a3a"  # 多云/阴/雾：深灰
_BG_RAIN = "#1a2a3a"    # 雨/冻雨/阵雨：墨蓝
_BG_SNOW = "#3a4a5a"    # 雪：暗蓝灰
_BG_STORM = "#4a1a1a"   # 雷暴：暗红
_BG_DEFAULT = "#0b0e14"  # 全局深空底色


def _to_int(code):
    try:
        return int(code)
    except (TypeError, ValueError):
        return None


def get_weather_icon(code) -> tuple[str, str, str]:
    """返回 (图标, 英文描述, 中文描述)。未知代码返回默认图标。"""
    code = _to_int(code)
    if code is None:
        return DEFAULT
    return WEATHER_MAP.get(code, DEFAULT)


def get_icon(code) -> str:
    """返回天气图标字符。"""
    return get_weather_icon(code)[0]


def get_en_desc(code) -> str:
    """返回英文天气描述。"""
    return get_weather_icon(code)[1]


def get_cn_desc(code) -> str:
    """返回中文天气描述（中文为主）。"""
    return get_weather_icon(code)[2]


def get_background_color(code) -> str:
    """依据 WMO 代码返回柔和的十六进制背景色。"""
    code = _to_int(code)
    if code is None:
        return _BG_DEFAULT
    if code in (0, 1):
        return _BG_SUNNY
    if code in (2, 3, 45, 48):
        return _BG_CLOUDY
    # 雨 / 冻雨 / 阵雨：51-57, 61-67, 80-82
    if (51 <= code <= 57) or (61 <= code <= 67) or (80 <= code <= 82):
        return _BG_RAIN
    # 雪：71-77, 85, 86
    if (71 <= code <= 77) or code in (85, 86):
        return _BG_SNOW
    # 雷暴：95, 96, 99
    if code in (95, 96, 99):
        return _BG_STORM
    return _BG_DEFAULT
