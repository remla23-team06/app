# Use an official Python runtime as a parent image
FROM python:3.10.7

# Set the working directory to /app
WORKDIR /app

# Copy the Pipfile and Pipfile.lock to the container
COPY Pipfile Pipfile.lock /app/

# Install Pipenv
RUN pip install pipenv

# Install dependencies
RUN pipenv install --deploy --ignore-pipfile

# Copy the current directory contents into the container at /app
COPY . /app

# Set the environment variable for Django
ENV DJANGO_SETTINGS_MODULE=webservice.settings

# Expose the port that the Django app will run on
EXPOSE 8080

# Run the Django app when the container launches
CMD ["pipenv", "run", "manage.py", "runserver", "0.0.0.0:8080"]
