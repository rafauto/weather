"""Aggregate the 3-hour forecast into daily summaries."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from itertools import groupby

from weather_app.models import ForecastEntry


@dataclass(frozen=True)
class DailySummary:
    """Min/max temperature and dominant condition for one calendar day."""

    day: date
    temp_min: float
    temp_max: float
    description: str
    icon: str
    max_rain_probability: float


def _day_icon(icons: list[str]) -> str:
    """Pick the most common icon, preferring the daytime ('d') variant."""
    most_common = Counter(icon[:-1] for icon in icons).most_common(1)[0][0]
    return f"{most_common}d"


def summarize_by_day(entries: list[ForecastEntry]) -> list[DailySummary]:
    """Group forecast entries by local calendar day and summarise each day."""
    ordered = sorted(entries, key=lambda e: e.time)
    summaries: list[DailySummary] = []

    for day, group in groupby(ordered, key=lambda e: e.time.date()):
        items = list(group)
        description = Counter(e.description for e in items).most_common(1)[0][0]
        summaries.append(
            DailySummary(
                day=day,
                temp_min=min(e.temperature for e in items),
                temp_max=max(e.temperature for e in items),
                description=description,
                icon=_day_icon([e.icon for e in items]),
                max_rain_probability=max(e.rain_probability for e in items),
            )
        )

    return summaries
