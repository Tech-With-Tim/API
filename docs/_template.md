# <!-- Base URL -->

- [<!-- Request type --> <!-- URL -->](#)

## <!-- Request type --> <!-- URL -->

<!-- Description -->

### Parameters

**Location:** <!-- Where the data is, can be ``body`` for json in the request body or ``querystring`` for url query string arguments -->

Parameter | Type | Description
--------- | ---- | -----------
<!-- Parameter name --> | <!-- Parameter type, for example ``str`` --> |  <!-- Short parameter description -->

#### Example request data

<!-- for ``body`` location -->

```json
{
    "parameter_name": "example_parameter_value"
}
```

<!-- for ``querystring`` location -->

```http
/url?parameter_name=example_parameter_value
```

### Returned data

<!-- Describe what is returned, remove the section if nothing is returned. For the case of a dict: -->

Parameter | Type | Description
--------- | ---- | -----------
<!-- Parameter name --> | <!-- Parameter type, for example ``str`` --> |  <!-- Short parameter description -->

#### Example response data

```json
{
    "parameter_name": "example_parameter_value"
}
```

### Status codes

<!-- List every possible status code that is returned by the endpoint, the status codes below are examples -->

- ``200`` Success  
  <!-- Description -->

- ``400`` Bad Request  
  <!-- Description -->
