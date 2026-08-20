from weather_tui.weather import weather_icons


def test_known_code():
    # (icon, en_desc, cn_desc)
    assert weather_icons.get_weather_icon(0) == ("☀️", "Clear sky", "晴")
    assert weather_icons.get_weather_icon(95) == ("⛈️", "Thunderstorm", "雷暴")


def test_unknown_code_defaults():
    assert weather_icons.get_weather_icon(999) == ("🌡️", "Unknown", "未知")
    assert weather_icons.get_weather_icon(None) == ("🌡️", "Unknown", "未知")
    assert weather_icons.get_weather_icon("abc") == ("🌡️", "Unknown", "未知")


def test_cn_desc():
    assert weather_icons.get_cn_desc(0) == "晴"
    assert weather_icons.get_cn_desc(99) == "雷暴伴冰雹"
    assert weather_icons.get_cn_desc(999) == "未知"


def test_en_desc():
    assert weather_icons.get_en_desc(1) == "Mainly clear"
    assert weather_icons.get_en_desc(711) == "Unknown"


def test_background_color_ranges():
    # 柔和十六进制背景色
    assert weather_icons.get_background_color(0) == "#1a3a5a"
    assert weather_icons.get_background_color(1) == "#1a3a5a"
    assert weather_icons.get_background_color(3) == "#3a3a3a"
    assert weather_icons.get_background_color(45) == "#3a3a3a"
    assert weather_icons.get_background_color(61) == "#1a2a3a"
    assert weather_icons.get_background_color(82) == "#1a2a3a"
    assert weather_icons.get_background_color(75) == "#3a4a5a"
    assert weather_icons.get_background_color(86) == "#3a4a5a"
    assert weather_icons.get_background_color(95) == "#4a1a1a"
    assert weather_icons.get_background_color(99) == "#4a1a1a"
    assert weather_icons.get_background_color(123) == "#0b0e14"
    assert weather_icons.get_background_color(None) == "#0b0e14"
