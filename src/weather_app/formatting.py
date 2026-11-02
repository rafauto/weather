"""Small helpers that turn raw values into user-friendly strings."""

from __future__ import annotations

from weather_app.api import Units

COMPASS_POINTS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def temperature_unit(units: Units) -> str:
    """Return the temperature symbol for the selected unit system."""
    return "°C" if units == "metric" else "°F"


def speed_unit(units: Units) -> str:
    """Return the wind-speed unit used by OpenWeatherMap for the unit system."""
    return "m/s" if units == "metric" else "mph"


def format_temperature(value: float, units: Units) -> str:
    """Format a temperature rounded to whole degrees, e.g. ``23°C``."""
    return f"{round(value)}{temperature_unit(units)}"


def wind_direction(degrees: float) -> str:
    """Convert a meteorological wind direction in degrees to an 8-point compass label."""
    index = round((degrees % 360) / 45) % len(COMPASS_POINTS)
    return COMPASS_POINTS[index]


def icon_url(icon_code: str, size: int = 2) -> str:
    """Return the OpenWeatherMap icon URL (``size`` 2 or 4 for @2x / @4x)."""
    return f"https://openweathermap.org/img/wn/{icon_code}@{size}x.png"
