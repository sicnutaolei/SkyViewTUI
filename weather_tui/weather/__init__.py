"""天气相关子包：API 调用、地理编码、IP 定位、图标映射。

公开 API（推荐从包级别导入）：
    from weather_tui.weather import fetch_weather, geocode, get_location_by_ip
    from weather_tui.weather import weather_icons
"""

from .api import fetch_weather
from .geocode import geocode
from .ip_location import get_location_by_ip
from . import weather_icons

__all__ = [
    "fetch_weather",
    "geocode",
    "get_location_by_ip",
    "weather_icons",
]
