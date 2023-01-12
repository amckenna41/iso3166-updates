# ISO3166 Updates API

As well as the Python software package, an API is also available to access any updates to a country's ISO3166-2 codes. You can search for a particular country via it's name or its 2 letter alpha 2 code (e.g EG, FR, DE) via the 'name' and 'alpha2' query parameters appended to the API URL. Additionally, the 'year' query parameter allows you to search for updates to 1 or more countries via the updates for a selected year, multiple years or a year range. If no query parameters are included then the whole dataset with all updates for all countries will be returned. The API endpoint is:

> https://www.iso3166-updates.com

GCP Cloud Architecture 
------------------------

<p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/gcp_cloud_arch.png" alt="gcp_arch" height="200" width="400"/>
</p>


Python
------

# Python Requests Library 
python
```
import requests

base_url = "https://www.iso3166-updates.com"

all_request = requests.get(base_url)
all_request.json() 

algeria_request = requests.get(base_url + "/alpha2/" + "DZ").json()
jamaica_request = requests.get(base_url + "/alpha2/" + "JM").json()
libya_request = requests.get(base_url + "/alpha2/" + "LY").json()
```
## Get All ISO3166-2 updates for all countries



Javascript
----------
```javascript
// Create a request variable and assign a new XMLHttpRequest object to it.
var request = new XMLHttpRequest()

// Open a new connection, using the GET request on the URL endpoint
request.open('GET', 'https://www.iso3166-updates.com', true)

request.onload = function () {
  // Begin accessing JSON data here
}

// Send request
request.send()

function getData() {
  const response = await fetch('https://www.iso3166-updates.com')
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)

data.forEach(alpha2 => {
  // Log each countrys updates
  console.log(alpha2)
})
```


curl command
------------------

### Request

`GET /`

    curl -i https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates

### Response

HTTP/2 200 
content-type: application/json
date: Tue, 20 Dec 2022 17:29:39 GMT
server: Google Frontend
content-length: 202273

{"AD":...}

## Get updates for a specific country e.g France, Germany, Hondurus


```python
import requests

base_url = "https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates"

all_request = requests.get(base_url + "?alpha2=FR")
# all_request = requests.get(base_url + "?alpha2=DE")
# all_request = requests.get(base_url + "?alpha2=HN")
all_request.json() 
```

### Request

`GET ?alpha2=FR`

    curl -i https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates?alpha2=FR

### Response

    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:30:27 GMT
    server: Google Frontend
    content-length: 4513

    "FR":[{"Code/Subdivision change":"Codes...}

`GET ?alpha2=DE`

    curl -i https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates?alpha2=DE

### Response

    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:31:19 GMT
    server: Google Frontend
    content-length: 10

    {"DE":{}}

`GET ?alpha2=HN`

    curl -i https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates?alpha2=HN

### Response

    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:31:53 GMT
    server: Google Frontend
    content-length: 479

    {"HN":[{"Code/Subdivision change":""...}

## Get updates for a specific country for specified year e.g Andorra, Dominica for 2014 & 2007

### Request

`GET ?alpha2=AD&year=2014`

    curl -i 'https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates?alpha2=AD&year=2014'

### Response

    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:34:31 GMT
    server: Google Frontend
    content-length: 227

    {"AD":[{"Code/Subdivision change":"","Date Issued":"2014-11-03"...}

`GET ?alpha2=DM&year=2014`

    curl -i 'https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates?alpha2=DM&year=2007'

### Response

    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:38:20 GMT
    server: Google Frontend
    content-length: 348

    {"DM":[{"Code/Subdivision change":"Subdivisions added:...}


## Get updates for a specific country for specified year range e.g Bosnia, Haiti for 2009-2015

### Request

`GET ?alpha2=BA&year=2009-2015`

    curl -i https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates?alpha2=BA&year=2009-2015

### Response

    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 20:19:23 GMT
    server: Google Frontend
    content-length: 1111

    {"BA":[{"Code/Subdivision change":"","Date Issued":"2015-11-27"...}

`GET ?alpha2=HT&year=2009-2015`

    curl -i https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates?alpha2=HT&year=2009-2015

### Response

    HTTP/1.1 404 Not Found
    Date: Thu, 24 Feb 2011 12:36:30 GMT
    Status: 404 Not Found
    Connection: close
    Content-Type: application/json
    Content-Length: 35

    {"status":404,"reason":"Not found"}


## Get updates for a specific country less than/greater than specified year e.g Israel, Lithuania <2010 or >2012

### Request

`GET ?alpha2=IL&year=<2010`

    curl -i https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates?alpha2=IL&year=<2010

### Response

    HTTP/1.1 404 Not Found
    Date: Thu, 24 Feb 2011 12:36:30 GMT
    Status: 404 Not Found
    Connection: close
    Content-Type: application/json
    Content-Length: 35

    {"status":404,"reason":"Not found"}

`GET ?alpha2=LT&year=>2012`

    curl -i https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates?alpha2=LT&year=>2012

### Response

    HTTP/1.1 404 Not Found
    Date: Thu, 24 Feb 2011 12:36:30 GMT
    Status: 404 Not Found
    Connection: close
    Content-Type: application/json
    Content-Length: 35

    {"status":404,"reason":"Not found"}