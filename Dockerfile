FROM python:3.8-slim

# left to be done after project structure
WORKDIR /app

ADD . /app

RUN pip install pipenv

RUN pipenv install
RUN pipenv run pip freeze >> requirements.txt
RUN pip install -r requirements.txt
RUN echo from api.__main__ import app >> asgi.py
CMD ["python","asgi.py","initdb"]
CMD ["hypercorn","asgi:app","-b","0.0.0.0:8000"]
