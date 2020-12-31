FROM python:3.8-slim

# Let service stop gracefully
STOPSIGNAL SIGQUIT

# Copy project files into working directory
WORKDIR /app
ADD . /app

# Install project dependencies
RUN pip install -U pipenv
RUN pipenv install --system --deploy

# Run the API.
CMD python launch.py runserver --host 0.0.0.0 --port 5000 --initdb