pipenv run python launch.py initdb
pipenv run hypercorn launch:app -b 0.0.0.0:5000