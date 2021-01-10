# URL: /auth/discord/redirect

Redirect user to correct Discord OAuth link depending on specified domain and requested scopes.

## Method

``GET``

## Expected data

### Optional ``callback``

The url to redirect to, after the Discord OAuth is passed.

> **This argument is optional**

**Location:** ``query``

**Type:** ``Optional[str]``

**Default:** ``/auth/discord/redirect``

## Returned data

None

## Status codes

### 302

Moved temporarily, redirect to the Discord OAuth portal succeeded.

### 400

Bad Request, callback URL provided isn't a well formed redirect URL.
