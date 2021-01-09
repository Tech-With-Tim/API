<img align="right" width=200px height=200px src="https://cdn.discordapp.com/attachments/776153365452554301/786297555415859220/Tech-With-Tim.png" alt="Project logo">

<h1>Tech With Tim - API</h1>

<div>

[![Status](https://img.shields.io/website?url=https%3A%2F%2Fapi.dev.twtcodejam.net)](https://api.dev.twtcodejam.net) <!-- TODO: Switch to main API link. -->
[![GitHub Issues](https://img.shields.io/github/issues/Tech-With-Tim/API.svg)](https://github.com/Tech-With-Tim/API/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/Tech-With-Tim/API.svg)](https://github.com/Tech-With-Tim/API/pulls)
[![Licence](https://img.shields.io/badge/licence-MIT-blue.svg)](/LICENCE)
[![Discord](https://discord.com/api/guilds/501090983539245061/widget.png?style=shield)](https://discord.gg/twt)
[![Test and deploy](https://github.com/Tech-With-Tim/API/workflows/Release%20-%20Test%2C%20Build%20%26%20Redeploy/badge.svg)](https://github.com/Tech-With-Tim/API/actions?query=workflow%3A%22Release+-+Test%2C+Build+%26+Redeploy%22)
<!-- TODO: Lint & Test status -->

</div>

API for the Tech With Tim website using [Quart](https://pgjones.gitlab.io/quart/).

## 📝 Table of Contents

<!-- - [🧐 About](#-about) -->
- [🏁 Getting Started](#-getting-started)
  - [Discord application](#discord-application)
  - [Prerequisites](#prerequisites)
  - [Environment variables](#environment-variables)
  - [Running](#running)
- [🐳 Running with Docker](#-running-with-docker)
- [🚨 Tests](#-tests)
- [📜 Licence](/LICENCE)
- [⛏️ Built Using](#️-built-using)
- [✍️ Authors](#️-authors)

<!-- ## 🧐 About

TODO: Write about 1-2 paragraphs describing the purpose of your project. -->

## 🏁 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [Running with Docker](#-running-with-docker) if you want to setup the API faster with Docker.

### Discord application

Create a new Discord application [here](https://discord.com/developers/applications) by clicking the `New application` button and name it whatever you want.

![New application](https://cdn.discordapp.com/attachments/721750194797936823/794646477505822730/unknown.png)

Now that you have an application, go to the OAuth2 tab.

![OAuth2 tab](https://cdn.discordapp.com/attachments/721750194797936823/794648158272487435/unknown.png)

And add `http://localhost:5000/auth/discord/code` to the redirects.

![Redirects](https://cdn.discordapp.com/attachments/721750194797936823/794648574150836224/unknown.png)

### Prerequisites

Install Pipenv:

```sh
pip install pipenv
```

Install the required packages with Pipenv:

```sh
pipenv install
```

### Environment variables

Set the environment variables:

> You can do this with a file named `local.env` or directly through the console. We recomend the `local.env` file as it won't be deleted when you open the console again.

#### `local.env` file

```prolog
SECRET_KEY=some_random_characters_here
DB_URI=postgresql://user:password@db:5432/twt
DISCORD_CLIENT_ID=
DISCORD_CLIENT_SECRET=
```

- `SECRET_KEY` is the key used for the JWT token encoding.
- `DB_URI` is the PostgreSQL database URI.
- `DISCORD_CLIENT_ID` is the Discord application ID. Copy it from your Discord application page (see below).
- `DISCORD_CLIENT_SECRET` is the Discord application secret. Copy it from your Discord application page (see below).

![Client ID and secret](https://cdn.discordapp.com/attachments/721750194797936823/794646777840140298/unknown.png)

#### Console

- For cmd:

    ```cmd
    set SECRET_KEY=some_random_characters_here
    set DB_URI=postgresql://user:password@db:5432/twt
    set DISCORD_CLIENT_ID=
    set DISCORD_CLIENT_SECRET=
    ```

- For shell:

    ```sh
    export SECRET_KEY=some_random_characters_here
    export DB_URI=postgresql://user:password@db:5432/twt
    export DISCORD_CLIENT_ID=
    export DISCORD_CLIENT_SECRET=
    ```

### Running

Run the API and initialise the database:

```sh
pipenv run python launch.py runserver --initdb
```

The API should run at [http://127.0.0.1:5000](http://127.0.0.1:5000).

## 🐳 Running with Docker

Both the API and the [frontend](https://github.com/Tech-With-Tim/Frontend) can be started using Docker. Using Docker is generally recommended (but not stricly required) because it abstracts away some additional set up work.

- Setup the discord app like done [here](#discord-application).

- Make a file named `.env` like done [here](#environment-variables).

- Then make sure you have `docker` and `docker-compose` installed, if not read [this for docker](https://docs.docker.com/engine/install/) and [this for docker compose](https://docs.docker.com/compose/install/).

- Deploy the API:

    ```sh
    docker-compose up
    ```

## 🚨 Tests

To test the API, we use the [pytest](https://docs.pytest.org/en/stable/) framework to make sure that the code we write works.

Run the tests:

```sh
pipenv run pytest
```

**When you contribute, you need to add tests on the features you add.** An example can be seen in [tests/test_index.py](/tests/test_index.py).

## ⛏️ Built Using

- [Python](https://www.python.org/) - Language
- [Quart](https://pgjones.gitlab.io/quart/) - Backend module
- [PostDB](https://github.com/SylteA/postDB) - Database module
- [pytest](https://docs.pytest.org/en/stable/) - Test framework

## ✍️ Authors

- [@SylteA](https://github.com/SylteA) - Most of the backend
- [@Shubhaankar-sharma](https://github.com/Shubhaankar-sharma) - Docker deployment
- [@takos22](https://github.com/takos22) - Markdown files

See also the list of [contributors](https://github.com/Tech-With-Tim/API/contributors) who participated in this project.
