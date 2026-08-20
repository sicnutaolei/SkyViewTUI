"""SkyViewTUI 主应用：解析参数、定位、抓取天气、管理界面与配置同步。"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from textual.app import App

from .config.manager import load_config, save_config
from .config.webdav import sync_from_webdav, sync_to_webdav
from .weather.geocode import geocode
from .weather.ip_location import get_location_by_ip
from .screens.main import ErrorScreen, MainScreen

logging.basicConfig(level=logging.WARNING)
_log = logging.getLogger(__name__)

CSS_PATH = str(Path(__file__).resolve().parent.parent / "app.tcss")


def _default_gif_path() -> str | None:
    """默认使用 weather_tui/img 目录下的第一个 GIF 文件。"""
    img_dir = Path(__file__).resolve().parent / "img"
    if not img_dir.exists():
        return None
    gifs = sorted(img_dir.glob("*.gif"))
    return str(gifs[0]) if gifs else None


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="skyviewtui",
        description="Terminal weather dashboard with live GIF animations (SkyViewTUI)",
    )
    parser.add_argument("--city", help="指定城市名，例如 --city \"Deyang\"")
    parser.add_argument(
        "--gif",
        help="指定右侧播放的 GIF 文件路径；省略则使用 weather_tui/img 下第一个 gif",
    )
    parser.add_argument(
        "--sync-pull",
        action="store_true",
        help="启动时从 WebDAV 拉取最新配置",
    )
    return parser.parse_args(argv)


class WeatherApp(App):
    """SkyViewTUI 主应用。"""

    CSS_PATH = CSS_PATH
    TITLE = "SkyViewTUI"
    SUB_TITLE = "Terminal Weather Dashboard"

    def __init__(
        self,
        city: str | None = None,
        sync_pull: bool = False,
        gif_path: str | None = None,
    ):
        super().__init__()
        self.city_arg = city
        self.sync_pull = sync_pull
        self.gif_path = gif_path or _default_gif_path()
        self.config = load_config()
        self.resolved_city: str | None = None
        self.lat: float | None = None
        self.lon: float | None = None

    def on_mount(self) -> None:
        # 在 worker 中执行所有异步 I/O，避免阻塞界面挂载
        self.run_worker(self._bootstrap(), exclusive=True)

    async def _bootstrap(self) -> None:
        # 1) 可选：从 WebDAV 拉取配置
        if self.sync_pull and self.config.get("webdav", {}).get("sync_enabled"):
            try:
                if sync_from_webdav(self.config):
                    self.config = load_config()
            except Exception as exc:  # 同步失败不应阻塞主流程
                _log.warning("WebDAV 拉取失败: %s", exc)

        # 2) 确定城市与坐标
        city = self.city_arg or self.config.get("city")
        coords: dict | None = None
        resolved_name: str | None = city

        if city:
            geo = await geocode(city)
            if geo:
                coords = geo
                name = geo.get("name")
                country = geo.get("country", "")
                resolved_name = f"{name}, {country}".rstrip(", ")
                resolved_cn = geo.get("cn_name")
            else:
                self.push_screen(
                    ErrorScreen(f"未找到城市：{city}\n请检查拼写，或不指定城市改用 IP 定位。")
                )
                return
        else:
            loc = await get_location_by_ip()
            if loc and loc.get("lat") is not None:
                coords = loc
                resolved_name = loc.get("city")
            else:
                self.push_screen(
                    ErrorScreen(
                        "无法定位，也未指定城市。\n请使用 --city <城市名> 重试。"
                    )
                )
                return

        # 3) 抓取天气
        try:
            data = await fetch_weather_safe(
                coords["lat"], coords["lon"], self.config.get("units", "celsius")
            )
        except Exception as exc:
            self.push_screen(ErrorScreen(f"获取天气失败：{exc}"))
            return

        # 4) 持久化最后使用的城市
        if resolved_name:
            self.config["city"] = resolved_name
            save_config(self.config)

        self.resolved_city = resolved_name
        self.lat = coords["lat"]
        self.lon = coords["lon"]
        self.push_screen(
            MainScreen(
                data,
                resolved_name,
                coords["lat"],
                coords["lon"],
                city_cn=resolved_cn,
                gif_path=self.gif_path,
            )
        )

    def on_unmount(self) -> None:
        # 退出时保存配置（确保 units 等最新）
        try:
            save_config(self.config)
        except Exception as exc:
            _log.warning("退出时保存配置失败: %s", exc)
        # 若启用 WebDAV，上传配置
        if self.config.get("webdav", {}).get("sync_enabled"):
            try:
                sync_to_webdav(self.config)
            except Exception as exc:
                _log.warning("退出时 WebDAV 上传失败: %s", exc)


async def fetch_weather_safe(lat, lon, units):
    """包装 fetch_weather，让错误信息更友好。"""
    from .weather.api import fetch_weather

    try:
        return await fetch_weather(lat, lon, units)
    except Exception as exc:
        msg = str(exc) or exc.__class__.__name__
        raise RuntimeError(f"网络请求出错（{msg}）") from exc


def main(argv=None) -> None:
    args = parse_args(argv)
    app = WeatherApp(
        city=args.city,
        sync_pull=args.sync_pull,
        gif_path=args.gif,
    )
    app.run()


if __name__ == "__main__":
    main()
