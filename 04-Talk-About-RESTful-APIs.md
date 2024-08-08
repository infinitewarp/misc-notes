# REST APIs

## What is REST?

Textbook definition:

> REpresentational State Transfer

REST is not an official protocol or standard. REST is a design pattern for communicating information across servers in a lightweight, stateless manner. REST APIs use the standard HTTP methods (a.k.a "verbs") to determine what type of action to perform for a given request.

What does "stateless" mean here? This means that all requests can be made independently of each other and contain all the information necessary for the server to perform an operation. The server authenticates and authorizes a request and performs and data retrieval or storage operations independently of any other requests. In a "stateful" API, information about the session surrounding a request may need to be maintained in the server and client so that one request may reference or assume some in-memory state of a previous request.

## The HTTP Methods

What are the HTTP methods, and how are they used in REST APIs?

- `POST` = create a new resource
- `GET` = get a resource (should *never change* the data on the server)
- `PUT` = replace an existing resource
- `PATCH` = modify an existing resource
- `DELETE` = delete an existing resource
- `OPTIONS` = list allowed methods for an API, optionally describing its inputs and outputs
- `HEAD` = same as get, but without the actual response body

### Refresher: How does HTTP actually work as a protocol?

All HTTP/1.1 (the most common version) requests to a web server must include:

- The request line containing:
  - The method (e.g. `GET`).
  - The requested URI, usually as a path (e.g. `/api/users`).
  - The HTTP version (e.g. `HTTP/1.1`).
- A list of request headers:
  - `Host` header is always required (e.g. `localhost:8000`).
  - Other headers like `Accept` or `Cookie` are optional by the spec but may be required by certain APIs.
- A blank line to indicate that there are no more headers.

The protocol for sending requests is very simple: once a network socket has been established, the client sends its request in plain text separated by newline characters. After the request line, each request header gets its own line. The raw content of a request may look like this:

```
GET /api/v1/users HTTP/1.1
Host: 127.0.0.1:8000
Accept: application/json, text/plain, */*
Accept-Encoding: gzip, deflate, br, zstd

```

That's it!

The response from the server to the client mirrors a similar structure and includes:

- The status line containing:
  - The HTTP version (e.g. `HTTP/1.1`)
  - The numeric status code (e.g. `200`)
  - A short description of the status code (e.g. `OK`)
- A list of response headers. None are strictly required, but most include:
  - `Content-Type` specifying the media type of the response body (e.g. `text/html` or `application/json`)
  - `Content-Length` specifying how many bytes the response body will contain (e.g. `56`)
  - `Date` specifying when the response was generated.
  - `Server` identifying the server software name and version.
- A blank line to indicate that there are no more headers.
- The actual response message body, if any.

The raw content of a request may look like this:

```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 56
Date: Thu, 08 Aug 2024 15:33:59 GMT
Server: WSGIServer/0.2 CPython/3.12.1

{"id": 1, "name": "Jean-Luc Picard", "rank": "Captain"}
```

HTTP clients like `curl` typically hide request and status lines and headers from their default outputs, but most of them have also options to show them. Enabling their display can help troubleshoot unexpected behaviors.

### Create a Resource

`HTTP POST`:

```sh
curl -X POST -H "Content-Type: application/json" -d @- \
    http://localhost:8000/api/users <<EOF
{
    "name": "Jean-Luc Picard",
    "rank": "Captain"
}
EOF
```
Typically returns `HTTP/1.1 201 Created` with the resource in the body:
```json
{
    "id": 5,
    "name": "Jean-Luc Picard",
    "rank": "Captain"
}
```

### Get a Resource

`HTTP GET`:

```sh
curl -X GET http://localhost:8000/api/users/5
```
Typically returns `HTTP/1.1 200 OK` with the resource in the body:
```json
{
    "id": 5,
    "name": "Jean-Luc Picard",
    "rank": "Captain"
}
```

### Replace or Modify a Resource

`HTTP PUT`:

```sh
curl -X PUT -H "Content-Type: application/json" -d @- \
    http://localhost:8000/api/users/5 <<EOF
{
    "id": 5,
    "name": "Jean-Luc Picard",
    "rank": "Admiral"
}
```
Typically returns `HTTP/1.1 200 OK` with the resource in the body:
```json
{
    "id": 5,
    "name": "Jean-Luc Picard",
    "rank": "Admiral"
}
```

`HTTP PATCH`:

```sh
curl -X PATCH -H "Content-Type: application/json" -d @- \
    http://localhost:8000/api/users/5 <<EOF
{
    "rank": "Admiral"
}
```
Typically returns `HTTP/1.1 200 OK` with the resource in the body:
```json
{
    "id": 5,
    "name": "Jean-Luc Picard",
    "rank": "Admiral"
}
```

### Destroy a Resource

`HTTP DELETE`:

```sh
curl -v -X DELETE http://localhost:8000/api/users/5
```
Typically an empty response body with headers:
```
< HTTP/1.1 204 No Content
< Content-Type: application/json
< Content-Length: 0
```

### Get Information About a Resource or API

`HTTP OPTIONS`:

```sh
curl -v -X OPTIONS http://localhost:8000/api/users/5
```
Typically an empty response body with headers:
```
< HTTP/1.1 204 No Content
< Content-Type: application/json
< Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
```
Some frameworks like Django will include a response body that describes the API like:
```json
{
  "name": "User Instance",
  "description": "A view set for Sources.",
  "renders": [
    "application/json",
    "text/html"
  ],
  "parses": [
    "application/json",
    "application/x-www-form-urlencoded",
    "multipart/form-data"
  ],
  "actions": {
    "PUT": {
      "id": {
        "type": "integer",
        "required": false,
        "read_only": true,
        "label": "ID"
      },
      "name": {
        "type": "string",
        "required": true,
        "read_only": false,
        "label": "Name",
        "max_length": 64
      },
```

`HTTP HEAD`:

```sh
curl --head http://localhost:8000/api/users/5
```
Typically an empty response body with headers like a `GET` would return:
```
< HTTP/1.1 200 OK
< Content-Type: application/json
< Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
```

