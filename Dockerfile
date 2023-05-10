# Use an official Python runtime as a parent image
FROM python:3.10

# Configure Poetry
ENV POETRY_VERSION=1.2.0
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

# Install poetry separated from system interpreter
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Set the working directory to /app
WORKDIR /app

# Install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install

# Copy the current directory contents into the container at /app
COPY . /app

# Run the Django app when the container launches
CMD ["pipenv", "run", "python", "manage.py", "runserver", "0.0.0.0:8080"]
