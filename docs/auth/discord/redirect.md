# GET /auth/discord/redirect

Redirect user to correct Discord OAuth link depending on specified domain and requested scopes.

## Parameters

**Location:** ``querystring``

Parameter | Type | Description
--------- | ---- | -----------
callback | ``Optional[str]`` | The url to redirect to, after the Discord OAuth is passed.

## Status codes

- ``302`` Moved temporarily  
  Redirect to the Discord OAuth portal succeeded.

- ``400`` Bad Request  
  Callback URL provided isn't a well formed redirect URL.
