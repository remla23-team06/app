# Use an official Python runtime as a parent image
FROM python:3.10

# Configure Poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.5.0
ENV PATH="$PATH:$POETRY_HOME/bin"

# Set env variable for Flask App
ENV FLASK_APP=app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080

# Expose same port
EXPOSE $FLASK_RUN_PORT


# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set the working directory to /app
WORKDIR /app

# Copy the pyproject and lock file into app
COPY pyproject.toml /app

# Install dependencies
RUN poetry config installer.max-workers 10
RUN poetry update -vv --without dev

# Copy the current directory contents into the container at /app
COPY . /app

# Run poetry lock to ensure that lock file is updated
RUN poetry lock

# Run the Flask app when the container launches
CMD ["poetry", "run", "flask", "run"]
