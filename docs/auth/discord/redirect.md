# GET /auth/discord/redirect

Redirect user to correct Discord OAuth link depending on specified domain and requested scopes.

## Parameters

**Location:** ``querystring``

Parameter | Type | Description
--------- | ---- | -----------
callback | ``Optional[str]`` | The URL to redirect to, after the Discord OAuth is passed. Default: ``http://127.0.0.1:5000/auth/discord/callback``

### Example request data

For a redirect to ``http://127.0.0.1:5000/auth/discord/callback``

```http
?callback=http%3A%2F%2F127.0.0.1%3A5000%2Fauth%2Fdiscord%2Fcallback
```

## Status codes

- ``302`` Moved temporarily  
  Redirect to the Discord OAuth portal succeeded.

- ``400`` Bad Request  
  Callback URL provided isn't a well formed redirect URL.
