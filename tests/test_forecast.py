from datetime import date

from weather_app.forecast import summarize_by_day
from weather_app.models import parse_forecast


def test_entries_are_grouped_by_local_day(forecast_payload):
    days = summarize_by_day(parse_forecast(forecast_payload).entries)

    assert [d.day for d in days] == [date(2023, 11, 14), date(2023, 11, 15)]


def test_daily_min_max_and_rain(forecast_payload):
    first, second = summarize_by_day(parse_forecast(forecast_payload).entries)

    assert (first.temp_min, first.temp_max) == (22.5, 24.0)
    assert first.max_rain_probability == 0.6
    assert (second.temp_min, second.temp_max) == (20.4, 28.1)


def test_dominant_condition_uses_daytime_icon(forecast_payload):
    _, second = summarize_by_day(parse_forecast(forecast_payload).entries)

    assert second.description == "Overcast clouds"
    assert second.icon == "04d"


def test_empty_forecast_returns_no_days():
    assert summarize_by_day([]) == []
