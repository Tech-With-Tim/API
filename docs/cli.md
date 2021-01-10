# Command line interface docs

Documentation for the CLI commands of the [launch.py](../launch.py) file.

Each command needs to be run from inside the pipenv environment:

```sh
pipenv run python launch.py [args]
```

## ``initdb``

Creates all tables defined in the app.

```sh
pipenv run python launch.py initdb
```

### Options

- ``-v`` | ``--verbose`` : Print SQL statements when creating models.

## ``dropdb``

Drops all tables defined in the app.

```sh
pipenv run python launch.py dropdb
```

### Options

- ``-v`` | ``--verbose`` : Print SQL statements when dropping models.

## ``runserver``

Run the API.

```sh
pipenv run python launch.py runserver
```

### Options

- ``-h {host}`` | ``--host {host}`` : Host to run the API on. Default: `127.0.0.1`.
- ``-p {port}`` | ``--port {port}`` : Port to run the API on. Default: `5000`.
- ``-i`` | ``--initdb`` : Create models before running the API. Equivalent of running the ``initdb`` command.
- ``-v`` | ``--verbose`` : Set logging to DEBUG instead of INFO.
