import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def current_payload() -> dict:
    return json.loads((FIXTURES / "current_weather.json").read_text())


@pytest.fixture
def forecast_payload() -> dict:
    return json.loads((FIXTURES / "forecast.json").read_text())
