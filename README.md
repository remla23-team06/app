# app

## Install Poetry (for Python package management)
See this [link](https://python-poetry.org/docs/#installation) for how to install poetry for your platform.

## Install requirements
```bash
# in the root directory of the repo
poetry update
```

## Run the app server
```bash
poetry run flask --app app --port 8000 --host 0.0.0.0
```