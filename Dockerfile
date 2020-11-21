FROM python:3.8-slim

# left to be done after project structure
WORKDIR /app

ADD . /app

RUN pip install pipenv

RUN pipenv install
RUN echo from api.__main__ import app >> asgi.py
#RUN pipenv run pip freeze >> requirements.txt
#RUN pip install -r requirements.txt
CMD sh /app/runfile.sh