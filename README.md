# app

After cloning the repository, please follow the instructions below to run the app:

## Running locally
### Install Poetry (for Python package management)
See this [link](https://python-poetry.org/docs/#installation) for how to install poetry for your platform.

### Install requirements
```bash
# in the root directory of the repo
poetry update
```

### Set env variable
This app requires the setting the `MODEL_SERVICE_URL` environment variable that points to the url of the model service including the port. Please run the [model service](https://github.com/remla23-team06/model-service) first, to be able to obtain the url from the `flask` app.

In Bash:
```sh
export MODEL_SERVICE_URL=<url>
```

In Powershell:
```powershell
$env:MODEL_SERVICE_URL=<url>
```

### Run the app server
In Bash:
```sh
poetry run flask --app app --port 8080 --host 0.0.0.0
```

In Powershell:
```powershell
poetry run flask --app app --port 8080 --host 0.0.0.0
```

## Running in Docker
Firstly, build the Docker image locally.
```docker
docker build . -t app-local
```
Secondly, run the docker image with the `MODEL_SERVICE_URL` variable set to the url of the [model service](https://github.com/remla23-team06/model-service) (see above).
```docker
docker run --rm -e MODEL_SERVICE_URL=<url> app-local
```
