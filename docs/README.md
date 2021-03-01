# API docs

## 📝 Table of Contents

- [CLI docs](./cli.md)
- [`/auth`](./auth.md)
- [`/guilds`](./guilds.md)
- [`/users`](./users.md)
- [`/roles`](./roles.md)

## 📚 Writing your own docs

Copy paste the [_template.md](./_template.md) file and rename it to your endpoint name. Fill in the sections with information about your endpoint:

> Note that each section is marked by a comment, for example ``<!-- URL -->`` needs to be replaced by the URL.

- The base URL, for example ``/auth``.

Repeat these for every endpoint:

- The request method, usually ``GET`` or ``POST``.
- The URL, for example ``/auth/discord/redirect``.
- A brief description of the endpoint, you can simply copy paste the docstring you wrote.
- The expected data, describe what everything is for and the data type.
- The returned data, describe what is returned and its type.
- The possible status codes, for example ``200`` for success or ``404`` for not found. A whole list of status codes can be found [here](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes).

You can then add it to the [table of contents](#-table-of-contents) and commit it.
