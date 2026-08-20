import pytest

from weather_tui.config import manager


@pytest.fixture
def config_file(tmp_path, monkeypatch):
    path = tmp_path / ".weather-config.toml"
    monkeypatch.setattr(manager, "CONFIG_PATH", path)
    return path


def test_defaults_when_missing(config_file):
    cfg = manager.load_config()
    assert cfg["city"] is None
    assert cfg["units"] == "celsius"
    assert cfg["theme"] == "default"
    assert cfg["webdav"]["sync_enabled"] is False


def test_roundtrip(config_file):
    manager.save_config({"city": "Deyang", "units": "fahrenheit"})
    cfg = manager.load_config()
    assert cfg["city"] == "Deyang"
    assert cfg["units"] == "fahrenheit"
    # 未显式设置的字段应有默认值
    assert cfg["webdav"]["sync_enabled"] is False


def test_set_city(config_file):
    manager.set_city("Chengdu")
    assert manager.get_city() == "Chengdu"


def test_load_merges_partial(config_file):
    config_file.write_text('city = "Tokyo"\n', encoding="utf-8")
    cfg = manager.load_config()
    assert cfg["city"] == "Tokyo"
    assert cfg["units"] == "celsius"


def test_corrupt_config_falls_back(config_file):
    config_file.write_text("this is = not valid toml [[[", encoding="utf-8")
    cfg = manager.load_config()
    assert cfg["units"] == "celsius"
