# ``/auth``

- [GET ``/auth/discord/redirect``](#get-authdiscordredirect)
- [POST (or GET) ``/auth/discord/callback``](#post-or-get-authdiscordcallback)

## GET ``/auth/discord/redirect``

Redirect user to correct Discord OAuth link depending on specified domain.

### Parameters

**Location:** ``querystring``

Parameter | Type | Description
--------- | ---- | -----------
callback | Optional ``str`` | The URL to redirect to, after the Discord OAuth is passed (default: `http://127.0.0.1:5000/auth/discord/callback`)

#### Example request data

For a redirect to ``http://127.0.0.1:5000/auth/discord/callback``

```http
/auth/discord/callback?callback=http%3A%2F%2F127.0.0.1%3A5000%2Fauth%2Fdiscord%2Fcallback
```

### Status codes

- ``302`` Moved temporarily  
  Redirect to the Discord OAuth portal succeeded.

- ``400`` Bad Request  
  Callback URL provided isn't a well formed redirect URL.

## POST (or GET) ``/auth/discord/callback``

Callback endpoint for finished discord authorization flow. ``GET`` method only allowed in debug mode, gets the code from the querystring.

### Parameters

**Location:** ``body`` (or ``querystring`` with ``GET`` in debug mode)

Parameter | Type | Description
--------- | ---- | -----------
code | ``str`` | The code from the Discord OAuth
callback | ``str`` | The same callback URL as provided in [/auth/discord/redirect](./redirect.md#parameters). Optional with ``GET`` method

#### Example request data

```json
{
    "code": "VQkVO7eHGom6GYRcUR0hNA9WFrbPVF",
    "callback": "http://127.0.0.1:5000/auth/discord/callback"
}
```

### Returned data

Returns the token and its expire date.

Parameter | Type | Description
--------- | ---- | -----------
token | ``str`` |  Access token for the API
exp | ``str`` |  Expire datetime of the token in [ISO 8601](https://wikipedia.org/wiki/ISO_8601) format

#### Example response data

```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGcuOiJIVzI1NiJ9.eyJ1aWQiOjQwATM0NjA3OZczMzMxNzYzNQwiZXhwIcoxNjExMDc3MDcvLCJpYXQiUjE2MTA0NzEyNyF9.UN7o5giVI_xLcSAS-6QGumvTXv0Q-wpYU00Xsjcd-_U",
    "exp": "2021-01-19T17:07:51.313285"
}
```

### Status codes

- ``200`` Success  
  Returns the token and its expiry date.

- ``400`` Bad Request  
  Code is missing in JSON data or querystring arguments.  
  Callback URL provided isn't a well formed redirect URL.  
  Discord returned a `400` status.
