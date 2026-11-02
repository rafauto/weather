"""Data models and parsers for OpenWeatherMap API responses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any


@dataclass(frozen=True)
class CurrentWeather:
    """Current conditions for a single city."""

    city: str
    country: str
    description: str
    icon: str
    temperature: float
    feels_like: float
    temp_min: float
    temp_max: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_deg: int
    visibility_m: int | None
    sunrise: datetime
    sunset: datetime
    observed_at: datetime


@dataclass(frozen=True)
class ForecastEntry:
    """A single 3-hour step of the 5-day forecast."""

    time: datetime
    temperature: float
    feels_like: float
    humidity: int
    description: str
    icon: str
    wind_speed: float
    rain_probability: float


@dataclass(frozen=True)
class Forecast:
    """The full 5-day / 3-hour forecast for a city."""

    city: str
    country: str
    entries: list[ForecastEntry]


def _local_time(unix_ts: int, utc_offset_s: int) -> datetime:
    """Convert a UNIX timestamp to a timezone-aware datetime in the city's local time."""
    tz = timezone(timedelta(seconds=utc_offset_s))
    return datetime.fromtimestamp(unix_ts, tz=tz)


def parse_current_weather(data: dict[str, Any]) -> CurrentWeather:
    """Build a CurrentWeather from the /data/2.5/weather JSON payload."""
    offset = data.get("timezone", 0)
    weather = data["weather"][0]
    main = data["main"]
    wind = data.get("wind", {})
    sys_info = data.get("sys", {})

    return CurrentWeather(
        city=data["name"],
        country=sys_info.get("country", ""),
        description=weather["description"].capitalize(),
        icon=weather["icon"],
        temperature=main["temp"],
        feels_like=main["feels_like"],
        temp_min=main["temp_min"],
        temp_max=main["temp_max"],
        humidity=main["humidity"],
        pressure=main["pressure"],
        wind_speed=wind.get("speed", 0.0),
        wind_deg=wind.get("deg", 0),
        visibility_m=data.get("visibility"),
        sunrise=_local_time(sys_info.get("sunrise", data["dt"]), offset),
        sunset=_local_time(sys_info.get("sunset", data["dt"]), offset),
        observed_at=_local_time(data["dt"], offset),
    )


def parse_forecast(data: dict[str, Any]) -> Forecast:
    """Build a Forecast from the /data/2.5/forecast JSON payload."""
    city_info = data["city"]
    offset = city_info.get("timezone", 0)

    entries = [
        ForecastEntry(
            time=_local_time(item["dt"], offset),
            temperature=item["main"]["temp"],
            feels_like=item["main"]["feels_like"],
            humidity=item["main"]["humidity"],
            description=item["weather"][0]["description"].capitalize(),
            icon=item["weather"][0]["icon"],
            wind_speed=item.get("wind", {}).get("speed", 0.0),
            rain_probability=item.get("pop", 0.0),
        )
        for item in data["list"]
    ]

    return Forecast(
        city=city_info["name"],
        country=city_info.get("country", ""),
        entries=entries,
    )
