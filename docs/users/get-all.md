# GET : /users/get-all

Takes queries to filter, sort, paginate users. None of the parameters are required

## Parameters

Parameter | Type | Description
--------- | ---- | -----------
sort_by | ``str`` | The key to sort by.
order | ``str`` | The order to sort in. This should only be equal to `ASC` or `DESC`.
username | ``str`` | Filter usernames that start with or match the username provided. Case sensitive
discriminator | ``str`` | Filter discriminators that start with or match the discriminator provided. Case sensitive
type | ``str`` | Filter users by the type provided. Case sensitive
page | ``int`` | The number of the page. Remember that this starts with 0 and goes ahead like so.
limit | ``int`` | The number of users per page.


### Example request data

```json
[
  {
    "avatar": "some",
    "discriminator": "110",
    "id": 110,
    "type": "USER",
    "username": "DemoUser110"
  },
  {
    "avatar": "some",
    "discriminator": "109",
    "id": 109,
    "type": "USER",
    "username": "DemoUser109"
  },
  {
    "avatar": "some",
    "discriminator": "108",
    "id": 108,
    "type": "USER",
    "username": "DemoUser108"
  },
  {
    "avatar": "some",
    "discriminator": "107",
    "id": 107,
    "type": "USER",
    "username": "DemoUser107"
  },
  {
    "avatar": "some",
    "discriminator": "106",
    "id": 106,
    "type": "USER",
    "username": "DemoUser106"
  }
]
```

```http
?limit=5&page=2&username=DemoUser&order=DESC
```

## Returned data

Returns a list of users. Each element in the list has this data:

Parameter | Type | Description
--------- | ---- | -----------
id | ``str`` |  Discord ID of the user
username | ``str`` |  Discord username of the user
discriminator | ``str`` |  Discord discriminator of the user
avatar | ``str`` or ``null`` |  Discord avatar hash of the user

### Example response data

```json
[
  {
    "avatar": "some",
    "discriminator": "1",
    "id": "1",
    "type": "USER",
    "username": "DemoUser1"
  },
  {
    "avatar": "some",
    "discriminator": "2",
    "id": "2",
    "type": "USER",
    "username": "DemoUser2"
  },
  {
    "avatar": "some",
    "discriminator": "3",
    "id": "3",
    "type": "USER",
    "username": "DemoUser3"
  },
  {
    "avatar": "some",
    "discriminator": "4",
    "id": "4",
    "type": "USER",
    "username": "DemoUser4"
  },
  {
    "avatar": "some",
    "discriminator": "5",
    "id": "5",
    "type": "USER",
    "username": "DemoUser5"
  }
]
```

## Status codes

<!-- List every possible status code that is returned by the endpoint, the status codes below are examples -->

- ``200`` Success  
  You provided correct parameters and no errors occurred

- ``400`` Bad Request  
  If page is set to an integer and limit is set to NoneType/None/null (this will rarely happen as there are default types.)
