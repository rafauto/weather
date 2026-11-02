# Contributing to Weather App

Thanks for your interest in improving this project! Bug reports, feature ideas and pull requests are all welcome.

## Reporting bugs and suggesting features

Open an [issue](https://github.com/rafauto/Weather/issues) and include:

- **Bugs:** what you did, what you expected, what happened instead, and your Python/OS version. Screenshots help.
- **Features:** the problem you want to solve and how you imagine the solution.

Please search existing issues first to avoid duplicates.

## Development setup

```bash
git clone https://github.com/<your-username>/Weather.git
cd Weather
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then add your API key
```

## Pull request workflow

1. Fork the repository and create a branch from `main`:
   `git checkout -b feat/hourly-forecast`
2. Make your changes, keeping the existing structure:
   - API access in `src/weather_app/api.py`
   - Data parsing in `src/weather_app/models.py`
   - Pure helpers in `src/weather_app/forecast.py` / `formatting.py`
   - UI only in `app.py`
3. Add or update tests in `tests/`.
4. Make sure everything passes:

   ```bash
   ruff check .
   ruff format --check .
   pytest
   ```

5. Commit using the convention below, push, and open a pull request describing **what** changed and **why**.

## Commit messages

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short summary in the imperative mood>
```

| Type | Use it for |
| --- | --- |
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `test` | Adding or fixing tests |
| `refactor` | Code changes that neither fix a bug nor add a feature |
| `style` | Formatting, no logic change |
| `chore` | Tooling, dependencies, configuration |
| `ci` | CI workflow changes |

Examples: `feat: add hourly forecast view`, `fix: handle cities without visibility data`.

## Security

**Never commit API keys or other secrets.** Keep them in `.streamlit/secrets.toml` or environment variables, which are ignored by Git.
