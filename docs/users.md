# ``/users``

- [GET ``/users``](#get-users)
- [GET ``/users/@me``](#get-users-me)
- [GET ``/users/<user_id>``](#get-users-user_id)

## Model
Parameter       | Type                  | Description
--------------- | --------------------- | -----------
id              |   ``Union[int, str]`` | Discord ID -> `int` internally, but `str` when transferred.
username        |   ``str``             | Discord username.
discriminator   |   ``str``             | Discord discriminator.
avatar          |   ``Optional[str]``   | Discord avatar.
type            |   ``str``             | The type of user this is.


## GET ``/users``
> GET `User` objects by bulk.

### Parameters

**Location:** ``querystring``

Parameter       | Type                  | Description
--------------- | --------------------- | -----------
type            |   ``Optional[str]``   | Only fetch users of this type.
username        |   ``Optional[str]``   | Only fetch users with this username.
discriminator   |   ``Optional[str]``   | Only fetch users with this discriminator
page            |   ``Optional[int]``   | Pagination page.
limit           |   ``Optional[int]``   | Max number of records to return.

#### Example request:

To only fetch users with the `1606` discriminator.
```http
GET /users?discriminator?1606
```

### Status codes
 - ``200`` Success\
   Returns: ``List[``[``User``](#model)``]``
 - ``400`` Bad Request

## GET ``/users/@me``
> Returns the currently authorized `User` object.

#### Example request:
```http
GET /users/@me
```

### Status codes
 - ``200`` Success\
   Returns: [``User``](#model)

## GET ``/users/<user_id>``
> Returns the provided user if it exists.

#### Example request:
```http
GET /users/144112966176997376
```

### Status codes'
 - ``200`` Success\
   Returns: [``User``](#model)
 - ``404`` Not Found
