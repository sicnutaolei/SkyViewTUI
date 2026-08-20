"""主屏幕：左右分栏天气仪表盘 + 右侧 GIF 字符画。

v1.4：
- 左侧：城市栏、选项卡、当前/逐小时/每日三视图。
- 右侧：GifPlayer 循环播放 GIF。
- 顶部仅保留城市名与时间，避免与当前视图温度/天气重复。
- 底部自定义状态栏，数字高亮且间距舒适。
- 修复选项卡 Button 在深色主题下文字不可见的问题。
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from rich.text import Text
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Header, Static

from ..weather import weather_icons
from ..weather.api import fetch_weather
from ..widgets.gif_player import GifPlayer
from ..widgets.info_card import InfoCard
from ..widgets.weather_display import CurrentWeather


class ErrorScreen(Screen):
    """友好错误提示，可按键 / 点击退出。"""

    BINDINGS = [("q", "quit", "退出")]

    def __init__(self, message: str):
        super().__init__()
        self._message = message

    def compose(self):
        yield Header()
        yield Static(self._message, id="error-message")
        yield Button("退出 (q)", id="quit-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit-btn":
            self.app.exit()

    def action_quit(self) -> None:
        self.app.exit()


class MainScreen(Screen):
    BINDINGS = [
        ("1", "show_current", "当前"),
        ("2", "show_hourly", "逐小时"),
        ("3", "show_daily", "每日"),
        ("r", "refresh", "刷新"),
        ("q", "quit", "退出"),
        ("n", "next_gif", "下一张"),
        ("right", "next_gif", "下一张"),
    ]

    def __init__(
        self,
        data: dict,
        city_name: str | None,
        lat: float,
        lon: float,
        city_cn: str | None = None,
        gif_path: str | None = None,
    ):
        super().__init__()
        self.data = data
        self.city_name = city_name or "未知地点"
        self.city_cn = city_cn
        self.lat = lat
        self.lon = lon
        self.gif_path = gif_path
        self._current_view = "current"

        # GIF 列表管理：扫描 img/ 目录，建立升序列表与当前索引
        self.img_dir = Path(__file__).resolve().parent.parent / "img"
        self.gif_files = sorted(self.img_dir.glob("*.gif"))
        self.current_gif_index = 0
        if self.gif_files:
            if gif_path:
                given = Path(gif_path).resolve()
                try:
                    self.current_gif_index = next(
                        i for i, p in enumerate(self.gif_files)
                        if p.resolve() == given
                    )
                except StopIteration:
                    # 指定的文件不在列表中（如目录外），加入最前
                    self.gif_files.insert(0, Path(gif_path))
                    self.current_gif_index = 0
            self.gif_path = str(self.gif_files[self.current_gif_index])
        else:
            self.current_gif_index = -1
            self.gif_path = None

    def compose(self):
        yield Header()
        yield Static(id="location-bar")

        with Horizontal(id="tab-bar"):
            yield Button("1 当前", id="tab-current", classes="tab")
            yield Button("2 逐小时", id="tab-hourly", classes="tab")
            yield Button("3 每日", id="tab-daily", classes="tab")
            yield Button("r 刷新", id="tab-refresh", classes="tab")

        with Horizontal(id="main-layout"):
            with Container(id="weather-panel"):
                with Container(id="view-current", classes="view-card"):
                    yield CurrentWeather(id="current-summary")
                    with Horizontal(id="current-cards"):
                        yield InfoCard(label="体感温度", id="card-feels", classes="view-card")
                        yield InfoCard(label="湿度", id="card-humidity", classes="view-card")
                        yield InfoCard(label="风速", id="card-wind", classes="view-card")
                with Container(id="view-hourly", classes="view-card hidden"):
                    yield Static(id="hourly-table")
                with Container(id="view-daily", classes="view-card hidden"):
                    yield Static(id="daily-text")

            yield GifPlayer(id="gif-player", gif_path=self.gif_path, fps=5)

        yield Static(id="status-bar")

    def on_mount(self) -> None:
        self._render_all()
        self.action_show_current()

    def on_unmount(self) -> None:
        # 停止 GIF 播放器，避免后台定时器泄漏
        try:
            self.query_one("#gif-player", GifPlayer).stop()
        except Exception:
            pass

    # ---- 渲染 ----
    def _render_all(self) -> None:
        self._render_location_bar()
        self._render_current()
        self._render_hourly()
        self._render_daily()
        self._render_status_bar()

    def _render_location_bar(self) -> None:
        """顶部只显示城市名与当前时间，避免与当前视图重复。"""
        text = Text()
        # 城市名：中文大号加粗（蓝） + 英文小号斜体（灰）
        if self.city_cn:
            text.append(f"{self.city_cn}  ", style="bold #7fc1ff")
            text.append(f"{self.city_name}", style="italic #8a9aa8")
        else:
            text.append(f"{self.city_name}", style="bold #7fc1ff")
        text.append("\n")
        # 当前时间（金色加粗） + 数据更新时间（灰色斜体小字）
        text.append(f"{datetime.now().strftime('%H:%M')}", style="bold #f5c542")
        cur = self.data.get("current", {})
        updated = cur.get("time", "")
        tz = self.data.get("timezone", "")
        if updated:
            text.append(f"   更新于 {updated}", style="italic #8a9aa8")
        if tz:
            text.append(f"  ({tz})", style="italic #8a9aa8")
        self.query_one("#location-bar").update(text)

    def _render_current(self) -> None:
        cur = self.data.get("current", {})
        # 动态背景色（仅当前视图）
        color = weather_icons.get_background_color(cur.get("weather_code"))
        try:
            self.styles.background = color
        except Exception:
            pass
        self.query_one(CurrentWeather).update_weather(cur)
        self.query_one("#card-feels").set_value(f"{cur.get('apparent_temperature', '—')}°")
        self.query_one("#card-humidity").set_value(f"{cur.get('relative_humidity_2m', '—')}%")
        self.query_one("#card-wind").set_value(f"{cur.get('wind_speed_10m', '—')} km/h")

    def _render_hourly(self) -> None:
        hourly = self.data.get("hourly", {})
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        codes = hourly.get("weather_code", [])
        precip = hourly.get("precipitation_probability", [])
        table = Text()
        table.append("未来 12 小时\n", style="bold #7fc1ff")
        n = min(12, len(times))
        for i in range(n):
            icon, en_desc, cn_desc = weather_icons.get_weather_icon(
                codes[i] if i < len(codes) else None
            )
            t = times[i]
            t_label = t[11:16] if len(t) >= 16 else t
            p = precip[i] if i < len(precip) else 0
            temp = temps[i] if i < len(temps) else "—"
            table.append(f"{t_label}  {icon} ", style="bold #e0e8f0")
            table.append(f"{cn_desc} ", style="#b0c0d0")
            table.append(f"{temp}° ", style="bold #f5c542")
            table.append(f"{p}%\n", style="#8ab8d9")
        self.query_one("#hourly-table").update(table)

    def _render_daily(self) -> None:
        """富文本行布局（修复表格重叠 / 不可见问题）。

        每行格式：月-日  ☀️ 天气描述  最高°(金) / 最低°(蓝)
        """
        daily = self.data.get("daily", {})
        dates = daily.get("time", [])
        codes = daily.get("weather_code", [])
        tmax = daily.get("temperature_2m_max", [])
        tmin = daily.get("temperature_2m_min", [])
        text = Text()
        text.append("未来 3 天\n", style="bold #7fc1ff")
        n = min(3, len(dates))
        for i in range(n):
            icon, en_desc, cn_desc = weather_icons.get_weather_icon(
                codes[i] if i < len(codes) else None
            )
            d = dates[i]
            d_label = d[5:] if len(d) >= 10 else d  # 月-日
            hi = f"{tmax[i]}°" if i < len(tmax) else "—"
            lo = f"{tmin[i]}°" if i < len(tmin) else "—"
            text.append(f"{d_label}  ", style="bold #e0e8f0")
            text.append(f"{icon} {cn_desc}  ", style="bold #f0f4fa")
            text.append(f"{hi}", style="bold #f5c542")
            text.append(f" / ", style="#8a9aa8")
            text.append(f"{lo}", style="bold #8ab8d9")
            text.append("\n")
        self.query_one("#daily-text").update(text)

    def _render_status_bar(self) -> None:
        """自定义底部状态栏：数字高亮，命令之间留足空格。"""
        text = Text()
        items = [
            ("1", "当前"),
            ("2", "逐小时"),
            ("3", "每日"),
            ("n", "下一张"),
            ("r", "刷新"),
            ("q", "退出"),
        ]
        for idx, (key, label) in enumerate(items):
            if idx > 0:
                text.append("    ", style="")
            text.append(key, style="bold #f5c542")
            text.append(f" {label}", style="#b0c0d0")
        self.query_one("#status-bar").update(text)

    # ---- 视图切换 ----
    def _switch(self, view: str) -> None:
        self._current_view = view
        for name in ("current", "hourly", "daily"):
            widget = self.query_one(f"#view-{name}")
            if name == view:
                widget.remove_class("hidden")
            else:
                widget.add_class("hidden")

    def action_show_current(self) -> None:
        self._switch("current")

    def action_show_hourly(self) -> None:
        self._switch("hourly")

    def action_show_daily(self) -> None:
        self._switch("daily")

    def action_refresh(self) -> None:
        self.run_worker(self._refresh(), exclusive=True)

    def action_quit(self) -> None:
        self.app.exit()

    def action_next_gif(self) -> None:
        """按 n / → 切换到下一张 GIF（循环）。仅一张或无图时不做反应。"""
        if len(self.gif_files) <= 1:
            return
        self.current_gif_index = (self.current_gif_index + 1) % len(self.gif_files)
        new_path = self.gif_files[self.current_gif_index]
        self.gif_path = str(new_path)
        try:
            player = self.query_one("#gif-player", GifPlayer)
        except Exception:
            return
        player.load_gif(new_path)

    async def _refresh(self) -> None:
        self.query_one("#location-bar").update("⏳ 正在刷新数据…")
        try:
            units = self.app.config.get("units", "celsius")
            self.data = await fetch_weather(self.lat, self.lon, units)
            self._render_all()
            self._switch(self._current_view)
        except Exception as exc:
            self.query_one("#location-bar").update(f"❌ 刷新失败：{exc}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        mapping = {
            "tab-current": self.action_show_current,
            "tab-hourly": self.action_show_hourly,
            "tab-daily": self.action_show_daily,
            "tab-refresh": self.action_refresh,
        }
        action = mapping.get(event.button.id)
        if action:
            action()
