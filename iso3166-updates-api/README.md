# ISO3166 Updates API

As well as the Python software package, an API is also available to access any updates to a country's ISO3166-2 codes. You can search for a particular country via it's name or its 2 letter alpha 2 code (e.g EG, FR, DE) via the 'name' and 'alpha2' query parameters appended to the API URL. Additionally, the 'year' query parameter allows you to search for updates to 1 or more countries via the updates for a selected year, multiple years or a year range. If no query parameters are included then the whole dataset with all updates for all countries will be returned. The API endpoint is:

> https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates2

Usage
-----

## Get All ISO3166-2 updates for all countries

### Request

`GET /`

curl -i https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates2

### Response

HTTP/2 200 
content-type: application/json
date: Sun, 04 Dec 2022 15:06:16 GMT
server: Google Frontend
content-length: 130923

{"AD":...}

## Get a specific country

### Request

`GET ?alpha2=FR`

    curl -i -H 'Accept: application/json' http://localhost:7000/thing/1

### Response

    HTTP/1.1 200 OK
    Date: Thu, 24 Feb 2011 12:36:30 GMT
    Status: 200 OK
    Connection: close
    Content-Type: application/json
    Content-Length: 36

    {"id":1,"name":"Foo","status":"new"}

## Get a non-existent Thing

### Request

`GET /thing/id`

    curl -i -H 'Accept: application/json' http://localhost:7000/thing/9999

### Response

    HTTP/1.1 404 Not Found
    Date: Thu, 24 Feb 2011 12:36:30 GMT
    Status: 404 Not Found
    Connection: close
    Content-Type: application/json
    Content-Length: 35

    {"status":404,"reason":"Not found"}