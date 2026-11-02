"""Streamlit entry point for the Weather App."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from weather_app.api import (  # noqa: E402
    CityNotFoundError,
    InvalidApiKeyError,
    Units,
    WeatherClient,
    WeatherServiceError,
)
from weather_app.forecast import summarize_by_day  # noqa: E402
from weather_app.formatting import (  # noqa: E402
    format_temperature,
    icon_url,
    speed_unit,
    temperature_unit,
    wind_direction,
)
from weather_app.models import CurrentWeather, Forecast  # noqa: E402

CACHE_TTL_S = 600
DEFAULT_CITY = "Rio de Janeiro"


def get_api_key() -> str | None:
    """Read the API key from Streamlit secrets, falling back to an environment variable."""
    try:
        key = st.secrets.get("OPENWEATHER_API_KEY")
    except Exception:  # no secrets.toml available
        key = None
    return key or os.environ.get("OPENWEATHER_API_KEY")


@st.cache_data(ttl=CACHE_TTL_S, show_spinner=False)
def fetch_weather(api_key: str, city: str, units: Units) -> tuple[CurrentWeather, Forecast]:
    """Fetch current weather and forecast, cached for 10 minutes per city/unit pair."""
    client = WeatherClient(api_key)
    return client.get_current_weather(city, units), client.get_forecast(city, units)


def render_current(current: CurrentWeather, units: Units) -> None:
    st.subheader(f"{current.city}, {current.country}")
    st.caption(f"Updated {current.observed_at:%a, %d %b %Y · %H:%M} (local time)")

    icon_col, temp_col = st.columns([1, 3])
    with icon_col:
        st.image(icon_url(current.icon, size=4), width=120)
    with temp_col:
        st.metric(
            label=current.description,
            value=format_temperature(current.temperature, units),
        )
        st.write(
            f"Feels like **{format_temperature(current.feels_like, units)}** · "
            f"Low **{format_temperature(current.temp_min, units)}** · "
            f"High **{format_temperature(current.temp_max, units)}**"
        )

    cols = st.columns(4)
    cols[0].metric("Humidity", f"{current.humidity}%")
    cols[1].metric(
        "Wind", f"{current.wind_speed:.1f} {speed_unit(units)} {wind_direction(current.wind_deg)}"
    )
    cols[2].metric("Pressure", f"{current.pressure} hPa")
    visibility = f"{current.visibility_m / 1000:.1f} km" if current.visibility_m else "n/a"
    cols[3].metric("Visibility", visibility)

    st.caption(f"🌅 Sunrise {current.sunrise:%H:%M} · 🌇 Sunset {current.sunset:%H:%M}")


def render_forecast(forecast: Forecast, units: Units) -> None:
    st.subheader("5-day forecast")

    # The API returns 40 steps of 3 h, which can touch 6 calendar days; show the first 5.
    days = summarize_by_day(forecast.entries)[:5]
    if not days:
        st.info("No forecast data available for this city.")
        return

    cols = st.columns(len(days))
    for col, day in zip(cols, days, strict=True):
        with col:
            st.markdown(f"**{day.day:%a %d}**")
            st.image(icon_url(day.icon), width=64)
            st.write(
                f"{format_temperature(day.temp_max, units)} / "
                f"{format_temperature(day.temp_min, units)}"
            )
            st.caption(f"{day.description} · 💧 {day.max_rain_probability:.0%}")

    unit = temperature_unit(units)
    chart_data = pd.DataFrame(
        {
            "Time": [e.time.replace(tzinfo=None) for e in forecast.entries],
            f"Temperature ({unit})": [e.temperature for e in forecast.entries],
            f"Feels like ({unit})": [e.feels_like for e in forecast.entries],
        }
    )
    st.markdown("**Temperature over the next 5 days**")
    st.line_chart(chart_data, x="Time", y=[f"Temperature ({unit})", f"Feels like ({unit})"])


def main() -> None:
    st.set_page_config(page_title="Weather App", page_icon="🌤️", layout="centered")
    st.title("🌤️ Weather App")
    st.write("Search any city to see current conditions and a 5-day forecast.")

    api_key = get_api_key()
    if not api_key:
        st.error(
            "No API key configured. Add `OPENWEATHER_API_KEY` to `.streamlit/secrets.toml` "
            "(see the README) and restart the app."
        )
        st.stop()

    with st.form("search"):
        city_col, unit_col = st.columns([3, 1])
        city = city_col.text_input("City", value=DEFAULT_CITY, placeholder="e.g. London, GB")
        unit_label = unit_col.radio("Units", ["°C", "°F"], horizontal=True)
        st.form_submit_button("Search", type="primary")

    units: Units = "metric" if unit_label == "°C" else "imperial"

    try:
        with st.spinner("Fetching weather..."):
            current, forecast = fetch_weather(api_key, city, units)
    except CityNotFoundError as exc:
        st.warning(f"{exc} Try adding the country code, e.g. 'Paris, FR'.")
        st.stop()
    except InvalidApiKeyError as exc:
        st.error(str(exc))
        st.stop()
    except WeatherServiceError as exc:
        st.error(str(exc))
        st.stop()

    render_current(current, units)
    st.divider()
    render_forecast(forecast, units)

    st.caption("Data provided by [OpenWeatherMap](https://openweathermap.org/).")


if __name__ == "__main__":
    main()
