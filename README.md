# API

## Currently required environment variables:
 * SECRET_KEY: key used for jwt encoding
 * DB_URI: The PostgreSQL database URI.
 * ~~QUART_APP: Location of quart app to run (**`api:app`**)~~\
   This could be used to run the project as `quart runserver` instead of `python api runserver`

## To run the project:
It is recomended to use PyCharm configurations to run the project.

Dependencies are managed by Pipenv.
To install require dependencies run **`pipenv install`**

> The project uses CLI commands to setup.
 * **`python api initdb`** \
   Create all tables. 
 * **`python api runserver`** \
   Run the project. 