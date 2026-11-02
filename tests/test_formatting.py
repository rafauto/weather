import pytest

from weather_app.formatting import (
    format_temperature,
    icon_url,
    speed_unit,
    temperature_unit,
    wind_direction,
)


def test_units():
    assert temperature_unit("metric") == "°C"
    assert temperature_unit("imperial") == "°F"
    assert speed_unit("metric") == "m/s"
    assert speed_unit("imperial") == "mph"


def test_format_temperature_rounds():
    assert format_temperature(23.6, "metric") == "24°C"
    assert format_temperature(-0.4, "imperial") == "0°F"


@pytest.mark.parametrize(
    ("degrees", "expected"),
    [(0, "N"), (44, "NE"), (90, "E"), (140, "SE"), (180, "S"), (270, "W"), (350, "N"), (360, "N")],
)
def test_wind_direction(degrees, expected):
    assert wind_direction(degrees) == expected


def test_icon_url():
    assert icon_url("10d") == "https://openweathermap.org/img/wn/10d@2x.png"
    assert icon_url("01n", size=4).endswith("01n@4x.png")
