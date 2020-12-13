FROM python:3.8-slim

# left to be done after project structure
WORKDIR /app

ADD . /app

RUN pip install pipenv
RUN pipenv install --system --deploy
RUN python launch.py initdb
CMD sh /app/runfile.sh