# Python Learning Project

A personal Python learning project focused on data science and web development.

## Features

- Data Science exercises (Pandas, NumPy, Matplotlib, Seaborn)
- Web scraping (BeautifulSoup)
- API development (FastAPI)
- Database operations (PostgreSQL with psycopg2, SQLAlchemy)
- Data visualization (Plotly)

## Setup

This project uses UV for fast dependency management with Python 3.11.

```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate
```

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Add a new package
uv add package-name

# Remove a package
uv remove package-name
```

## Python Version

This project requires Python 3.11.x (see `.python-version`).
