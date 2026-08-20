"""天气显示专用组件。"""

from __future__ import annotations

from rich.text import Text

from textual.widgets import Static

from ..weather import weather_icons


class CurrentWeather(Static):
    """当前天气的大号摘要：图标 + 温度 + 描述。"""

    DEFAULT_CSS = """
    CurrentWeather {
        height: auto;
        padding: 1 2;
    }
    """

    def update_weather(self, current: dict) -> None:
        code = current.get("weather_code")
        icon, en_desc, cn_desc = weather_icons.get_weather_icon(code)
        temp = current.get("temperature_2m", "—")
        text = Text()
        text.append(f"{icon}  ", style="bold")
        text.append(f"{temp}°", style="bold #f5c542")
        text.append(f"  {cn_desc}", style="bold #f0f4fa")
        text.append(f" ({en_desc})", style="italic #8a9aa8")
        self.update(text)
