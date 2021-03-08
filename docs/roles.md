# ``/roles``

- [POST ``/roles/``](#post-roles)

## POST ``/roles/``

Create a new role from request body

### Parameters

**Location:** ``body``

Parameter | Type | Description
--------- | ---- | -----------
name | ``str`` | The role's name
color | Optional ``int`` | The role's color (default: `0`)
permissions | Optional ``int`` | The role's permissions (default: `0`)

#### Example request data

```json
{
    "name": "Admon",
    "color": 1,
    "permissions": 1
}
```

### Returned data

Returns the created guild.

Parameter | Type | Description
--------- | ---- | -----------
id | ``str`` | The role's ID
name | ``str`` | The role's name
color | ``int`` | The role's color
permissions | ``int`` | The role's permissions

#### Example response data

```json
{
    "id": 760510623330598922,
    "name": "Admon",
    "color": 1,
    "permissions": 1
}
```

### Status codes

- ``201`` Created  
  The role was created in the database.

- ``400`` Bad Request  
  Missing a required parameter.
