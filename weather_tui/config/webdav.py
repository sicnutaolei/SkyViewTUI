"""WebDAV 同步：将配置文件上传到（或下载自）坚果云等 WebDAV 服务器。"""

from __future__ import annotations

import logging
from pathlib import Path

from .manager import CONFIG_PATH

REMOTE_PATH = "/weather-config.toml"
_log = logging.getLogger(__name__)


def _build_client(config: dict):
    """根据配置中的 webdav 子项创建 webdav3 客户端；依赖缺失时返回 None。"""
    try:
        from webdav3.client import Client
    except ImportError:
        _log.warning("未安装 webdavclient3，无法使用 WebDAV 同步。")
        return None

    wd = config.get("webdav", {}) or {}
    url = wd.get("url")
    if not url:
        _log.warning("WebDAV url 为空，跳过同步。")
        return None

    options = {
        "webdav_hostname": url,
        "webdav_login": wd.get("username", ""),
        "webdav_password": wd.get("password", ""),
    }
    return Client(options)


def sync_to_webdav(config: dict, local_path: Path | None = None) -> bool:
    """上传本地配置到 WebDAV。失败返回 False（静默忽略）。"""
    client = _build_client(config)
    if client is None:
        return False
    try:
        client.upload(REMOTE_PATH, str(local_path or CONFIG_PATH))
        _log.info("配置已上传到 WebDAV: %s", REMOTE_PATH)
        return True
    except Exception as exc:
        _log.warning("WebDAV 上传失败: %s", exc)
        return False


def sync_from_webdav(config: dict, local_path: Path | None = None) -> bool:
    """从 WebDAV 下载配置到本地。成功返回 True，远程不存在或失败返回 False。"""
    client = _build_client(config)
    if client is None:
        return False
    try:
        if not client.check(REMOTE_PATH):
            _log.info("远程配置不存在: %s", REMOTE_PATH)
            return False
        client.download(REMOTE_PATH, str(local_path or CONFIG_PATH))
        _log.info("配置已从 WebDAV 拉取: %s", REMOTE_PATH)
        return True
    except Exception as exc:
        _log.warning("WebDAV 下载失败: %s", exc)
        return False
