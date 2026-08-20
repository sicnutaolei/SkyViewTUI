import asyncio

from weather_tui.weather import api, geocode, ip_location
from weather_tui.weather.geocode import geocode as geocode_fn
from conftest import patch_async_client


def test_geocode_success(monkeypatch):
    routes = {
        "geocoding-api": {
            "results": [
                {
                    "name": "Deyang",
                    "country": "China",
                    "latitude": 31.13,
                    "longitude": 104.4,
                }
            ]
        }
    }
    patch_async_client(monkeypatch, routes)
    result = asyncio.run(geocode("Deyang"))
    assert result["name"] == "Deyang"
    assert result["country"] == "China"
    assert result["lat"] == 31.13
    assert result["lon"] == 104.4
    assert result["cn_name"] == "德阳"  # Deyang 命中 CITY_CN


def test_geocode_not_found(monkeypatch):
    patch_async_client(monkeypatch, {"geocoding-api": {}})
    assert asyncio.run(geocode("NowhereLand")) is None


def test_ip_location_success(monkeypatch):
    routes = {
        "ip-api.com": {
            "status": "success",
            "city": "Chengdu",
            "country": "China",
            "lat": 30.6,
            "lon": 104.0,
        }
    }
    patch_async_client(monkeypatch, routes)
    loc = asyncio.run(ip_location.get_location_by_ip())
    assert loc["city"] == "Chengdu"
    assert loc["lat"] == 30.6


def test_ip_location_failure(monkeypatch):
    patch_async_client(monkeypatch, {"ip-api.com": {"status": "fail"}})
    assert asyncio.run(ip_location.get_location_by_ip()) is None


def test_fetch_weather(monkeypatch):
    sample = {
        "current": {"temperature_2m": 20, "weather_code": 1},
        "hourly": {"time": ["2026-08-20T00:00"], "temperature_2m": [20]},
        "daily": {"time": ["2026-08-20"], "weather_code": [1]},
        "timezone": "Asia/Shanghai",
    }
    patch_async_client(monkeypatch, {"api.open-meteo.com": sample})
    data = asyncio.run(api.fetch_weather(31.13, 104.4, "celsius"))
    assert data["current"]["temperature_2m"] == 20
    assert data["timezone"] == "Asia/Shanghai"
