"""Thin client for the OpenWeatherMap free-tier API."""

from __future__ import annotations

from typing import Any, Literal

import requests

from weather_app.models import CurrentWeather, Forecast, parse_current_weather, parse_forecast

BASE_URL = "https://api.openweathermap.org/data/2.5"
DEFAULT_TIMEOUT_S = 10

Units = Literal["metric", "imperial"]


class WeatherServiceError(Exception):
    """Base error for anything that goes wrong while talking to the weather API."""


class CityNotFoundError(WeatherServiceError):
    """Raised when the API does not recognise the requested city."""


class InvalidApiKeyError(WeatherServiceError):
    """Raised when the API key is missing, wrong or not yet activated."""


class WeatherClient:
    """Fetches current conditions and forecasts from OpenWeatherMap."""

    def __init__(
        self,
        api_key: str,
        *,
        session: requests.Session | None = None,
        timeout: float = DEFAULT_TIMEOUT_S,
        base_url: str = BASE_URL,
    ) -> None:
        if not api_key:
            raise InvalidApiKeyError("An OpenWeatherMap API key is required.")
        self._api_key = api_key
        self._session = session or requests.Session()
        self._timeout = timeout
        self._base_url = base_url.rstrip("/")

    def get_current_weather(self, city: str, units: Units = "metric") -> CurrentWeather:
        """Return the current weather for ``city``."""
        return parse_current_weather(self._get("weather", city, units))

    def get_forecast(self, city: str, units: Units = "metric") -> Forecast:
        """Return the 5-day / 3-hour forecast for ``city``."""
        return parse_forecast(self._get("forecast", city, units))

    def _get(self, endpoint: str, city: str, units: Units) -> dict[str, Any]:
        city = city.strip()
        if not city:
            raise CityNotFoundError("Please enter a city name.")

        params = {"q": city, "appid": self._api_key, "units": units, "lang": "en"}
        try:
            response = self._session.get(
                f"{self._base_url}/{endpoint}", params=params, timeout=self._timeout
            )
        except requests.Timeout as exc:
            raise WeatherServiceError("The weather service took too long to respond.") from exc
        except requests.RequestException as exc:
            raise WeatherServiceError("Could not reach the weather service.") from exc

        if response.status_code == 401:
            raise InvalidApiKeyError(
                "The API key was rejected. New keys can take up to 2 hours to activate."
            )
        if response.status_code == 404:
            raise CityNotFoundError(f"City '{city}' was not found.")
        if response.status_code == 429:
            raise WeatherServiceError("API rate limit reached. Please try again in a minute.")
        if not response.ok:
            raise WeatherServiceError(
                f"Weather service returned an unexpected error (HTTP {response.status_code})."
            )

        return response.json()
