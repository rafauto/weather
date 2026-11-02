from unittest.mock import MagicMock

import pytest
import requests

from weather_app.api import (
    CityNotFoundError,
    InvalidApiKeyError,
    WeatherClient,
    WeatherServiceError,
)


def make_client(status_code: int = 200, payload: dict | None = None, exc: Exception | None = None):
    session = MagicMock(spec=requests.Session)
    if exc is not None:
        session.get.side_effect = exc
    else:
        response = MagicMock()
        response.status_code = status_code
        response.ok = 200 <= status_code < 300
        response.json.return_value = payload or {}
        session.get.return_value = response
    return WeatherClient("test-key", session=session), session


def test_current_weather_is_parsed(current_payload):
    client, session = make_client(payload=current_payload)

    weather = client.get_current_weather("Rio de Janeiro")

    assert weather.city == "Rio de Janeiro"
    assert weather.temperature == 24.6
    _, kwargs = session.get.call_args
    assert kwargs["params"] == {
        "q": "Rio de Janeiro",
        "appid": "test-key",
        "units": "metric",
        "lang": "en",
    }


def test_forecast_uses_requested_units(forecast_payload):
    client, session = make_client(payload=forecast_payload)

    forecast = client.get_forecast("Rio de Janeiro", units="imperial")

    assert len(forecast.entries) == 6
    assert session.get.call_args.kwargs["params"]["units"] == "imperial"
    assert session.get.call_args.args[0].endswith("/forecast")


def test_city_name_is_trimmed(current_payload):
    client, session = make_client(payload=current_payload)

    client.get_current_weather("  London  ")

    assert session.get.call_args.kwargs["params"]["q"] == "London"


def test_empty_city_raises_without_calling_api():
    client, session = make_client()

    with pytest.raises(CityNotFoundError):
        client.get_current_weather("   ")
    session.get.assert_not_called()


def test_missing_api_key_raises():
    with pytest.raises(InvalidApiKeyError):
        WeatherClient("")


@pytest.mark.parametrize(
    ("status", "error"),
    [
        (401, InvalidApiKeyError),
        (404, CityNotFoundError),
        (429, WeatherServiceError),
        (500, WeatherServiceError),
    ],
)
def test_http_errors_map_to_exceptions(status, error):
    client, _ = make_client(status_code=status)

    with pytest.raises(error):
        client.get_current_weather("Atlantis")


def test_network_failure_raises_service_error():
    client, _ = make_client(exc=requests.ConnectionError("offline"))

    with pytest.raises(WeatherServiceError, match="Could not reach"):
        client.get_current_weather("Rio de Janeiro")


def test_timeout_raises_service_error():
    client, _ = make_client(exc=requests.Timeout())

    with pytest.raises(WeatherServiceError, match="too long"):
        client.get_current_weather("Rio de Janeiro")
