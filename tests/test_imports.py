"""冒烟测试：确保各模块可正常导入，无语法 / 顶层错误。"""


def test_import_app():
    import weather_tui.app  # noqa: F401
    from weather_tui.app import WeatherApp, main, parse_args

    assert WeatherApp is not None
    assert callable(main)
    # parse_args 应能解析 --city
    ns = parse_args(["--city", "Deyang"])
    assert ns.city == "Deyang"


def test_import_screen():
    from weather_tui.screens.main import MainScreen, ErrorScreen  # noqa: F401

    assert MainScreen is not None
    assert ErrorScreen is not None
