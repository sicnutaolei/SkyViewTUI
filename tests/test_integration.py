"""集成测试：用 Textual 的 run_test（无头驱动）验证界面组合与交互。

不依赖真实终端；网络请求通过 mock 替换，避免外部依赖。
"""

import asyncio
from unittest.mock import patch

from rich.text import Text

from weather_tui.app import WeatherApp
from weather_tui.widgets.gif_player import GifPlayer

SAMPLE = {
    "current": {
        "temperature_2m": 25,
        "weather_code": 1,
        "apparent_temperature": 24,
        "relative_humidity_2m": 60,
        "wind_speed_10m": 5,
        "time": "2026-08-20T12:00",
    },
    "hourly": {
        "time": ["2026-08-20T12:00", "2026-08-20T13:00"],
        "temperature_2m": [25, 24],
        "weather_code": [1, 2],
        "precipitation_probability": [10, 20],
    },
    "daily": {
        "time": ["2026-08-20", "2026-08-21", "2026-08-22"],
        "weather_code": [1, 2, 3],
        "temperature_2m_max": [30, 29, 28],
        "temperature_2m_min": [20, 19, 18],
    },
    "timezone": "Asia/Shanghai",
}


def test_app_success_flow():
    async def run():
        async def noop_load(self):
            self._frames = [Text("GIF")]

        with patch("weather_tui.app.geocode") as m_geo, patch(
            "weather_tui.app.fetch_weather_safe"
        ) as m_fetch, patch(
            "weather_tui.screens.main.GifPlayer._start_playback", new=noop_load
        ):
            m_geo.return_value = {
                "name": "Deyang",
                "country": "China",
                "lat": 31.13,
                "lon": 104.4,
                "cn_name": "德阳",
            }
            m_fetch.return_value = SAMPLE

            app = WeatherApp(city="Deyang", gif_path="dummy.gif")
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause()
                await app.workers.wait_for_complete()
                await pilot.pause()

                screen = app.screen
                assert screen.__class__.__name__ == "MainScreen"

                # 左右分栏布局
                screen.query_one("#weather-panel")
                screen.query_one("#gif-player")
                assert list(screen.query("#side-panel")) == []

                cur = screen.query_one("#view-current")
                hourly = screen.query_one("#view-hourly")
                daily = screen.query_one("#view-daily")

                # 默认显示当前视图
                assert "hidden" not in cur.classes
                assert "hidden" in hourly.classes
                assert "hidden" in daily.classes

                # 切换到逐小时
                await pilot.press("2")
                await pilot.pause()
                assert "hidden" not in hourly.classes
                assert "hidden" in cur.classes

                # 切换到每日（文本布局，非表格）
                await pilot.press("3")
                await pilot.pause()
                assert "hidden" not in daily.classes
                assert "hidden" in hourly.classes
                daily_text = screen.query_one("#daily-text")
                assert "08-20" in str(daily_text.render())

                # 顶部栏包含中文城市名，且不应再重复显示温度/天气描述
                loc = screen.query_one("#location-bar")
                loc_str = str(loc.render())
                assert "德阳" in loc_str
                assert "Deyang" in loc_str
                assert "25°" not in loc_str
                assert "晴间多云" not in loc_str

                # 底部状态栏格式
                status = screen.query_one("#status-bar")
                status_str = str(status.render())
                assert "1" in status_str and "当前" in status_str
                assert "2" in status_str and "逐小时" in status_str
                assert "3" in status_str and "每日" in status_str
                assert "r" in status_str and "刷新" in status_str
                assert "q" in status_str and "退出" in status_str

    asyncio.run(run())


def test_gif_switching():
    """验证按 n / → 切换下一张 GIF，索引循环推进且 load_gif 被调用。"""
    async def run():
        async def noop_load(self):
            self._frames = [Text("GIF")]

        with patch("weather_tui.app.geocode") as m_geo, patch(
            "weather_tui.app.fetch_weather_safe"
        ) as m_fetch, patch(
            "weather_tui.screens.main.GifPlayer._start_playback", new=noop_load
        ), patch.object(GifPlayer, "load_gif") as m_load:
            m_geo.return_value = {
                "name": "Deyang",
                "country": "China",
                "lat": 31.13,
                "lon": 104.4,
                "cn_name": "德阳",
            }
            m_fetch.return_value = SAMPLE

            app = WeatherApp(city="Deyang")  # 不指定 --gif，使用 img/ 下第一个
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause()
                await app.workers.wait_for_complete()
                await pilot.pause()

                screen = app.screen
                # img/ 目录存在多个 gif
                assert len(screen.gif_files) >= 2
                start = screen.current_gif_index
                expected = (start + 1) % len(screen.gif_files)

                # 按 n 切换
                await pilot.press("n")
                await pilot.pause()
                m_load.assert_called_once()
                assert screen.current_gif_index == expected

                # 按右箭头再切换一次
                await pilot.press("right")
                await pilot.pause()
                assert m_load.call_count == 2
                assert screen.current_gif_index == (expected + 1) % len(
                    screen.gif_files
                )

    asyncio.run(run())


def test_app_city_not_found():
    async def run():
        with patch("weather_tui.app.geocode") as m_geo, patch(
            "weather_tui.app.fetch_weather_safe"
        ) as m_fetch:
            m_geo.return_value = None  # 未找到城市

            app = WeatherApp(city="NowhereLand")
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause()
                await app.workers.wait_for_complete()
                await pilot.pause()

                screen = app.screen
                assert screen.__class__.__name__ == "ErrorScreen"
                assert "NowhereLand" in str(screen.query_one("#error-message").render())

    asyncio.run(run())
