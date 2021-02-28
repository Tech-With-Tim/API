# ``/guilds``

- [POST ``/guilds``](#post-guilds)
- [GET ``/guilds/<id>``](#get-guildsid)
- [PATCH ``/guilds/<id>``](#patch-guildsid)
- [DELETE ``/guilds/<id>``](#delete-guildsid)
- [GET ``/guilds/<id>/icon``](#get-guildsidicon)
- [POST ``/guilds/<id>/config``](#post-guildsidconfig)
- [GET ``/guilds/<id>/config``](#get-guildsidconfig)
- [PATCH ``/guilds/<id>/config``](#patch-guildsidconfig)
- [DELETE ``/guilds/<id>/config``](#delete-guildsidconfig)

## POST ``/guilds``

Create a guild from the request body.

### Parameters

**Location:** ``body``

Parameter | Type | Description
--------- | ---- | -----------
id | ``str`` or ``int`` | The guild's ID
name | ``str`` | The guild's name
owner_id | ``str`` or ``int`` | The guild's owner's ID
icon_hash | Optional ``str`` | The guild's icon's hash (default: `null`)

#### Example request data

```json
{
    "id": 501090983539245061,
    "name": "Tech With Tim",
    "owner_id": 501089409379205161,
    "icon_hash": "a_5aa83d87a200585758846a075ffc52ba"
}
```

### Returned data

Returns the created guild.

Parameter | Type | Description
--------- | ---- | -----------
id | ``str`` | The guild's ID
name | ``str`` | The guild's name
owner_id | ``str`` | The guild's owner's ID
icon_hash | ``str`` or ``null`` | The guild's icon's hash

#### Example response data

```json
{
    "id": 501090983539245061,
    "name": "Tech With Tim",
    "owner_id": 501089409379205161,
    "icon_hash": "a_5aa83d87a200585758846a075ffc52ba"
}
```

### Status codes

- ``201`` Created  
  The guild was created in the database.

- ``400`` Bad Request  
  Missing a required parameter.

- ``409`` Conflict  
  A guild with the provided ID already exists.

## GET ``/guilds/<id>``

Get a guild from its ID.

### Parameters

**Location:** ``url``

Parameter | Type | Description
--------- | ---- | -----------
id | ``int`` | The guild's ID

#### Example request data

```http
/guild/501090983539245061
```

### Returned data

Returns the guild.

Parameter | Type | Description
--------- | ---- | -----------
id | ``str`` | The guild's ID
name | ``str`` | The guild's name
owner_id | ``str`` | The guild's owner's ID
icon_hash | ``str`` or ``null`` | The guild's icon's hash

#### Example response data

```json
{
    "id": 501090983539245061,
    "name": "Tech With Tim",
    "owner_id": 501089409379205161,
    "icon_hash": "a_5aa83d87a200585758846a075ffc52ba"
}
```

### Status codes

- ``200`` Success  
  The guild is returned.

- ``404`` Not found  
  Guild with provided ID doesn't exist.

## PATCH ``/guilds/<id>``

Update elements of a guild from the request body.

### Parameters

**Location:** ``url``

Parameter | Type | Description
--------- | ---- | -----------
id | ``int`` | The guild's ID

**Location:** ``body``

Parameter | Type | Description
--------- | ---- | -----------
name | Optional ``str`` | The guild's new name
owner_id | Optional ``str`` or ``int`` | The guild's new owner's ID
icon_hash | Optional ``str`` | The guild's new icon's hash

#### Example request data

```http
/guild/501090983539245061
```

```json
{
    "name": "Tech With Tom",
}
```

### Returned data

Returns the updated guild.

Parameter | Type | Description
--------- | ---- | -----------
id | ``str`` | The guild's ID
name | ``str`` | The guild's name
owner_id | ``str`` | The guild's owner's ID
icon_hash | ``str`` or ``null`` | The guild's icon's hash

#### Example response data

```json
{
    "id": 501090983539245061,
    "name": "Tech With Tom",
    "owner_id": 501089409379205161,
    "icon_hash": "a_5aa83d87a200585758846a075ffc52ba"
}
```

### Status codes

- ``200`` Success  
  The guild was updated and is returned.

- ``404`` Not found  
  Guild with provided ID doesn't exist.

## DELETE ``/guilds/<id>``

Delete a guild from its ID.

### Parameters

**Location:** ``url``

Parameter | Type | Description
--------- | ---- | -----------
id | ``int`` | The guild's ID

#### Example request data

```http
/guild/501090983539245061
```

### Returned data

Returns the deleted guild.

Parameter | Type | Description
--------- | ---- | -----------
id | ``str`` | The guild's ID
name | ``str`` | The guild's name
owner_id | ``str`` | The guild's owner's ID
icon_hash | ``str`` or ``null`` | The guild's icon's hash

#### Example response data

```json
{
    "id": 501090983539245061,
    "name": "Tech With Tim",
    "owner_id": 501089409379205161,
    "icon_hash": "a_5aa83d87a200585758846a075ffc52ba"
}
```

### Status codes

- ``200`` Success  
  The guild was deleted and is returned.

- ``404`` Not found  
  Guild with provided ID doesn't exist.

## GET ``/guilds/<id>/icon``

Get a guild's icon from its ID.

### Parameters

**Location:** ``url``

Parameter | Type | Description
--------- | ---- | -----------
id | ``int`` | The guild's ID

**Location:** ``querystring``

Parameter | Type | Description | Options
--------- | ---- | ----------- | -------
format | Optional ``str`` | The desired icon format (default: `gif` if animated or `static_format` parameter) | `png`, `jpeg`, `jpg`, `webp`, `gif` only if animated
static_format | Optional ``str`` | The desired static icon format if `format` parameter isn't provided (default: `webp`) | `png`, `jpeg`, `jpg`, `webp`
size | Optional ``int`` | The desired icon size, needs to be a power of 2 between 16 and 4096 (default: `128`) | `16`, `32`, `64`, `128`, `256`, `512`, `1024`, `2048`, `4096`

#### Example request data

```http
/guild/501090983539245061/icon?format=png&size=2048
```

### Returned data

Redirect to Discord's icon CDN.

### Status codes

- ``302`` Found  
  Redirect to Discord's icon CDN.

- ``400`` Bad Request  
  `size` parameter must be an integer.  
  `size` parameter must be a power of 2 between 16 and 4096.  
  `format` parameter must be one of `png`, `jpeg`, `jpg`, `webp`, `gif` only if animated.  
  `static_format` parameter must be one of `png`, `jpeg`, `jpg`, `webp`.
  Non animated guild avatars do not support `gif` format.

- ``404`` Not found  
  Guild with provided ID doesn't exist.

## POST ``/guilds/<id>/config``

Create a guild configuration from the request body.

### Parameters

**Location:** ``url``

Parameter | Type | Description
--------- | ---- | -----------
id | ``int`` | The guild's ID

**Location:** ``body``

Parameter | Type | Description
--------- | ---- | -----------
xp_enabled | Optional ``bool`` | Whether there's is XP for every message sent in the guild (default: `false`)
xp_multiplier | Optional ``float`` | The multiplier of the XP for the guild (default: `1.0`)
eco_enabled | Optional ``bool`` | Whether the economy commands are enabled for the guild (default: `false`)
muted_role_id | Optional ``str`` | The guild's muted role's ID (default: `null`)
do_logging | Optional ``bool`` | Whether to do message logging for the guild (default: `false`)
log_channel_id | Optional ``str`` | The guild's log channel's ID (default: `null`)
do_logging | Optional ``bool`` | Whether to do new member verifictaion for the guild (default: `false`)
verification_type | Optional ``str`` | The guild's verification type, must be one of [these](#verification-types) (default: `DISCORD_INTEGRATED`)
verification_channel_id | Optional ``str`` | The guild's verification channel's ID (default: `null`)

#### Verification types

Name | Description
---- | -----------
``DISCORD_INTEGRATED`` | [Discord's integrated verification.](https://support.discord.com/hc/fr/articles/1500000466882-Rules-Screening-FAQ)
``DISCORD_CODE`` | Send a code to the user in DMs and make him send it in a channel.
``DISCORD_INTEGRATED_CODE`` | Combination of `DISCORD_INTEGRATED` and `DISCORD_CODE`.
``DISCORD_CAPTCHA`` | Send a picture with letters and numbers to the user in DMs then make him write those characters in a channel.
``DISCORD_INTEGRATED_CAPTCHA`` | Combination of `DISCORD_INTEGRATED` and `DISCORD_CAPTCHA`.
``DISCORD_REACTION`` | Make the user react to a message in a channel.
``DISCORD_INTEGRATED_REACTION`` |Combination of `DISCORD_INTEGRATED` and `DISCORD_REACTION`.

#### Example request data

```http
/guild/501090983539245061/config
```

```json
{
    "xp_enabled": true,
    "eco_enabled": true,
    "muted_role_id": 583350495117312010,
    "do_logging": true,
    "log_channel_id": 536617175369121802
}
```

### Returned data

Returns the created guild configuration.

Parameter | Type | Description
--------- | ---- | -----------
guild_id | ``str`` | The guild's ID
xp_enabled | ``bool`` | Whether there's is XP for every message sent in the guild
xp_multiplier | ``float`` | The multiplier of the XP for the guild
eco_enabled | ``bool`` | Whether the economy commands are enabled for the guild
muted_role_id | ``str`` or ``null`` | The guild's muted role's ID
do_logging | ``bool`` | Whether to do message logging for the guild
log_channel_id | ``str`` or ``null`` | The guild's log channel's ID
do_logging | ``bool`` | Whether to do new member verifictaion for the guild
verification_type | ``str`` | The guild's verification type
verification_channel_id | ``str`` or ``null`` | The guild's verification channel's ID

#### Example response data

```json
{
    "guild_id": "501090983539245061",
    "xp_enabled": true,
    "xp_multiplier": 1.0,
    "eco_enabled": true,
    "muted_role_id": "583350495117312010",
    "do_logging": true,
    "log_channel_id": "536617175369121802",
    "do_verification": false,
    "verification_type": "DISCORD_INTEGRATED",
    "verification_channel_id": null,
}
```

### Status codes

- ``201`` Created  
  The guild configuration was created in the database.

- ``400`` Bad request  
  `verification_type` parameter must be one of [these](#verification-types).

- ``404`` Not found  
  Guild with provided ID doesn't exist.

- ``409`` Conflict  
  The guild already has a configuration.

## GET ``/guilds/<id>/config``

Get a guild configuration.

### Parameters

**Location:** ``url``

Parameter | Type | Description
--------- | ---- | -----------
id | ``int`` | The guild's ID

#### Example request data

```http
/guild/501090983539245061/config
```

### Returned data

Returns the guild configuration.

Parameter | Type | Description
--------- | ---- | -----------
guild_id | ``str`` | The guild's ID
xp_enabled | ``bool`` | Whether there's is XP for every message sent in the guild
xp_multiplier | ``float`` | The multiplier of the XP for the guild
eco_enabled | ``bool`` | Whether the economy commands are enabled for the guild
muted_role_id | ``str`` or ``null`` | The guild's muted role's ID
do_logging | ``bool`` | Whether to do message logging for the guild
log_channel_id | ``str`` or ``null`` | The guild's log channel's ID
do_logging | ``bool`` | Whether to do new member verifictaion for the guild
verification_type | ``str`` | The guild's verification type
verification_channel_id | ``str`` or ``null`` | The guild's verification channel's ID

#### Example response data

```json
{
    "guild_id": "501090983539245061",
    "xp_enabled": true,
    "xp_multiplier": 1.0,
    "eco_enabled": true,
    "muted_role_id": "583350495117312010",
    "do_logging": true,
    "log_channel_id": "536617175369121802",
    "do_verification": false,
    "verification_type": "DISCORD_INTEGRATED",
    "verification_channel_id": null,
}
```

### Status codes

- ``200`` Success  
  The guild is returned.

- ``404`` Not found  
  Guild with provided ID doesn't exist.  
  Guild with provided ID doesn't have a configuration.

## PATCH ``/guilds/<id>/config``

Update a guild configuration from the request body.

### Parameters

**Location:** ``url``

Parameter | Type | Description
--------- | ---- | -----------
id | ``int`` | The guild's ID

**Location:** ``body``

Parameter | Type | Description
--------- | ---- | -----------
xp_enabled | Optional ``bool`` | Whether there's is XP for every message sent in the guild
xp_multiplier | Optional ``float`` | The new multiplier of the XP for the guild
eco_enabled | Optional ``bool`` | Whether the economy commands are enabled for the guild
muted_role_id | Optional ``str`` | The guild's new muted role's ID
do_logging | Optional ``bool`` | Whether to do message logging for the guild
log_channel_id | Optional ``str`` | The guild's new log channel's ID
do_logging | Optional ``bool`` | Whether to do new member verifictaion for the guild
verification_type | Optional ``str`` | The guild's new verification type, must be one of [these](#verification-types)
verification_channel_id | Optional ``str`` | The guild's new verification channel's ID

#### Example request data

```http
/guild/501090983539245061
```

```json
{
    "xp_multiplier": 2.0,
}
```

### Returned data

Returns the updated guild configuration.

Parameter | Type | Description
--------- | ---- | -----------
guild_id | ``str`` | The guild's ID
xp_enabled | ``bool`` | Whether there's is XP for every message sent in the guild
xp_multiplier | ``float`` | The multiplier of the XP for the guild
eco_enabled | ``bool`` | Whether the economy commands are enabled for the guild
muted_role_id | ``str`` or ``null`` | The guild's muted role's ID
do_logging | ``bool`` | Whether to do message logging for the guild
log_channel_id | ``str`` or ``null`` | The guild's log channel's ID
do_logging | ``bool`` | Whether to do new member verifictaion for the guild
verification_type | ``str`` | The guild's verification type
verification_channel_id | ``str`` or ``null`` | The guild's verification channel's ID

#### Example response data

```json
{
    "guild_id": "501090983539245061",
    "xp_enabled": true,
    "xp_multiplier": 2.0,
    "eco_enabled": true,
    "muted_role_id": "583350495117312010",
    "do_logging": true,
    "log_channel_id": "536617175369121802",
    "do_verification": false,
    "verification_type": "DISCORD_INTEGRATED",
    "verification_channel_id": null,
}
```

### Status codes

- ``200`` Success  
  The guild configuration was updated and is returned.

- ``400`` Bad request  
  `verification_type` parameter must be one of [these](#verification-types).

- ``404`` Not found  
  Guild with provided ID doesn't exist.  
  Guild with provided ID doesn't have a configuration.

## DELETE ``/guilds/<id>/config``

Delete a guild configuration.

### Parameters

**Location:** ``url``

Parameter | Type | Description
--------- | ---- | -----------
id | ``int`` | The guild's ID

#### Example request data

```http
/guild/501090983539245061
```

### Returned data

Returns the deleted guild configuration.

Parameter | Type | Description
--------- | ---- | -----------
guild_id | ``str`` | The guild's ID
xp_enabled | ``bool`` | Whether there's is XP for every message sent in the guild
xp_multiplier | ``float`` | The multiplier of the XP for the guild
eco_enabled | ``bool`` | Whether the economy commands are enabled for the guild
muted_role_id | ``str`` or ``null`` | The guild's muted role's ID
do_logging | ``bool`` | Whether to do message logging for the guild
log_channel_id | ``str`` or ``null`` | The guild's log channel's ID
do_logging | ``bool`` | Whether to do new member verifictaion for the guild
verification_type | ``str`` | The guild's verification type
verification_channel_id | ``str`` or ``null`` | The guild's verification channel's ID

#### Example response data

```json
{
    "guild_id": "501090983539245061",
    "xp_enabled": true,
    "xp_multiplier": 1.0,
    "eco_enabled": true,
    "muted_role_id": "583350495117312010",
    "do_logging": true,
    "log_channel_id": "536617175369121802",
    "do_verification": false,
    "verification_type": "DISCORD_INTEGRATED",
    "verification_channel_id": null,
}
```

### Status codes

- ``200`` Success  
  The guild configuration was deleted and is returned.

- ``404`` Not found  
  Guild with provided ID doesn't exist.  
  Guild with provided ID doesn't have a configuration.
