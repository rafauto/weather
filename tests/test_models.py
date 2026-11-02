from datetime import timedelta

from weather_app.models import parse_current_weather, parse_forecast


def test_parse_current_weather(current_payload):
    weather = parse_current_weather(current_payload)

    assert weather.city == "Rio de Janeiro"
    assert weather.country == "BR"
    assert weather.description == "Scattered clouds"
    assert weather.humidity == 78
    assert weather.wind_deg == 140
    assert weather.visibility_m == 10000


def test_times_are_in_city_local_time(current_payload):
    weather = parse_current_weather(current_payload)

    assert weather.observed_at.utcoffset() == timedelta(hours=-3)
    assert weather.observed_at.hour == 19  # 22:13 UTC -> 19:13 in Rio


def test_parse_current_weather_tolerates_missing_optional_fields(current_payload):
    del current_payload["visibility"]
    del current_payload["wind"]

    weather = parse_current_weather(current_payload)

    assert weather.visibility_m is None
    assert weather.wind_speed == 0.0


def test_parse_forecast(forecast_payload):
    forecast = parse_forecast(forecast_payload)

    assert forecast.city == "Rio de Janeiro"
    assert len(forecast.entries) == 6
    first = forecast.entries[0]
    assert first.temperature == 24.0
    assert first.rain_probability == 0.6
    assert first.description == "Light rain"
