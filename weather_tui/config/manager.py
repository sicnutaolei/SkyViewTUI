"""配置读写：加载 / 保存 ~/.weather-config.toml，并提供默认值与便捷接口。

跨平台路径使用 pathlib.Path.home()；读取优先用内置 tomllib (3.11+)，
旧版本回退到 tomli；写入优先用 tomli_w，缺失时回退到内置的最小 TOML 序列化。
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any

try:  # Python 3.11+
    import tomllib  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - 仅旧版本
    import tomli as tomllib  # type: ignore

try:
    import tomli_w  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - 有回退实现
    tomli_w = None  # type: ignore

CONFIG_FILENAME = ".weather-config.toml"
CONFIG_PATH = Path.home() / CONFIG_FILENAME

DEFAULT_CONFIG: dict[str, Any] = {
    "city": None,
    "units": "celsius",
    "theme": "default",
    "webdav": {
        "url": "",
        "username": "",
        "password": "",
        "sync_enabled": False,
    },
}

_lock = threading.Lock()
_log = logging.getLogger(__name__)


def _merge_defaults(data: dict) -> dict:
    """将一个（可能不完整的）配置与默认值合并，保证字段齐全。"""
    config = {
        "city": data.get("city", DEFAULT_CONFIG["city"]),
        "units": data.get("units", DEFAULT_CONFIG["units"]),
        "theme": data.get("theme", DEFAULT_CONFIG["theme"]),
    }
    wd = data.get("webdav", {}) or {}
    config["webdav"] = {
        "url": wd.get("url", ""),
        "username": wd.get("username", ""),
        "password": wd.get("password", ""),
        "sync_enabled": bool(wd.get("sync_enabled", False)),
    }
    return config


def load_config(path: Path | None = None) -> dict:
    """加载配置。文件不存在或损坏时返回默认值。"""
    cfg_path = path or CONFIG_PATH
    if not cfg_path.exists():
        return _merge_defaults({})
    try:
        with open(cfg_path, "rb") as f:
            data = tomllib.load(f)
        return _merge_defaults(data)
    except Exception as exc:  # 损坏的配置文件不应导致崩溃
        _log.warning("读取配置文件失败，使用默认值: %s", exc)
        return _merge_defaults({})


def save_config(config: dict, path: Path | None = None) -> None:
    """保存配置（与默认值合并后写入）。线程安全。"""
    cfg_path = path or CONFIG_PATH
    merged = _merge_defaults(config)
    with _lock:
        try:
            cfg_path.parent.mkdir(parents=True, exist_ok=True)
            if tomli_w is not None:
                with open(cfg_path, "wb") as f:
                    tomli_w.dump(merged, f)
            else:  # 回退：最小 TOML 序列化
                cfg_path.write_text(_dump_toml(merged), encoding="utf-8")
        except Exception as exc:
            _log.warning("保存配置文件失败: %s", exc)


def _dump_toml(config: dict) -> str:
    """极简 TOML 序列化，仅覆盖本应用所需结构（flat + [webdav]）。"""
    lines: list[str] = []
    for key in ("city", "units", "theme"):
        lines.append(f"{key} = {_toml_value(config.get(key))}")
    wd = config.get("webdav", {})
    lines.append("")
    lines.append("[webdav]")
    for key in ("url", "username", "password", "sync_enabled"):
        lines.append(f"{key} = {_toml_value(wd.get(key))}")
    return "\n".join(lines) + "\n"


def _toml_value(value: Any) -> str:
    if value is None:
        return '""'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def get_city() -> str | None:
    return load_config().get("city")


def set_city(city: str) -> None:
    config = load_config()
    config["city"] = city
    save_config(config)


def get_units() -> str:
    return load_config().get("units", "celsius")
