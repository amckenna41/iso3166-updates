# ISO3166 Updates API

![Vercel](https://therealsujitk-vercel-badge.vercel.app/?app=iso3166-updates-frontend)

As well as the Python software package, an API is also available to access any updates to a country's ISO 3166-2 codes via a URL endpoint. You can search for a particular country using its 2 letter alpha-2 code or 3 letter alpha-3 code (e.g EG, FR, DE or EGY, FRA, DEU) via the 'alpha2' query parameter appended to the API URL. Additionally, the 'year' query parameter allows you to search for updates to 1 or more countries for a selected year, multiple years or a year range (e.g 2008, 2000-2010, <2016). The 'month' query parameter accepts an integer representing the number of months of past updates to be returned (e.g 6, 9, 24) from the current date. If no query parameters are included then the whole dataset with all updates for all countries will be returned. 

The main API endpoint is:

> https://www.iso3166-updates.com/api

GCP Cloud Architecture 
------------------------

<p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166-updates-api/gcp_cloud_arch.png" alt="gcp_arch" height="200" width="400"/>
</p>

Requirements
------------
* [python][python] >= 3.7
* [flask][flask] >= 2.3.2
* [requests][requests] >= 2.28.1
* [iso3166][iso3166] >= 2.1.1
* [python-dateutil][python-dateutil] >= 2.8.2
* [google-auth][google-auth] >= 2.17.3
* [google-cloud-storage][google-cloud-storage] >= 2.8.0
* [google-api-python-client][google-api-python-client] >= 2.86.0


Get All ISO 3166-2 updates for all countries
-------------------------------------------
### Request
`GET /`

    curl -i https://www.iso3166-updates.com/api

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:29:39 GMT
    server: Google Frontend
    content-length: 202273

    {"AD":...}

### Python
```python
import requests

base_url = "https://www.iso3166-updates.com/api"

all_request = requests.get(base_url)
all_request.json() 
```

### Javascript
```javascript
function getData() {
  const response = await fetch('https://www.iso3166-updates.com/api')
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country e.g France, Germany, Hondurus
----------------------------------------------------------------

### Request
`GET /alpha2/FR`

    curl -i https://iso3166-updates.com/api?alpha2=FR
    curl -i https://iso3166-updates.com/api/alpha2/FR

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:30:27 GMT
    server: Google Frontend
    content-length: 4513

    "FR":[{"Code/Subdivision change":"Codes...}

### Request
`GET /alpha2/DE`

    curl -i https://iso3166-updates.com/api?alpha2=DE
    curl -i https://iso3166-updates.com/api/alpha2/DE

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:31:19 GMT
    server: Google Frontend
    content-length: 10

    {"DE":{}}

### Request
`GET /alpha2/HN`

    curl -i https://iso3166-updates.com/api?alpha2=HN
    curl -i https://iso3166-updates.com/api/alpha2/HN

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:31:53 GMT
    server: Google Frontend
    content-length: 479

    {"HN":[{"Code/Subdivision change":""...}

### Python
```python
import requests

base_url = "https://iso3166-updates/api"

all_request = requests.get(base_url, params={"alpha2": "FR"})
# all_request = requests.get(base_url, params={"alpha2": "DE"})
# all_request = requests.get(base_url, params={"alpha2": "HN"})
all_request.json() 
```

### Javascript
```javascript
function getData() {
  const response = 
    await fetch('https://iso3166-updates/api' + 
        new URLSearchParams({
            alpha2: 'FR'
  }));
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all updates for a specified year e.g 2004, 2007
---------------------------------------------------

### Request
`GET /year/2004`

    curl -i https://iso3166-updates.com/api?year=2004
    curl -i https://iso3166-updates.com/api/year/2004

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:40:19 GMT
    server: Google Frontend
    content-length: 10

    {"AF":[{"Code/Subdivision change":""...}

### Request
`GET /year/2007`

    curl -i https://iso3166-updates.com/api?year=2007
    curl -i https://iso3166-updates.com/api/year/2007

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:41:53 GMT
    server: Google Frontend
    content-length: 479

    {"AD":[{"Code/Subdivision change":""...}

### Python
```python
import requests

base_url = "https://iso3166-updates/api"

all_request = requests.get(base_url, params={"year": "2004"})
# all_request = requests.get(base_url, params={"year": "2007"})
all_request.json() 
```

### Javascript
```javascript
function getData() {
  const response = 
    await fetch('https://iso3166-updates/api' + 
        new URLSearchParams({
            year: '2004'
  }));
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country for specified year e.g Andorra, Dominica for 2007
------------------------------------------------------------------------------------

### Request
`GET /alpha2/AD/year/2007`

    curl -i https://iso3166-updates.com/api?alpha2=AD&year=2007
    curl -i https://iso3166-updates.com/api/alpha2/AD/year/2007

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:34:31 GMT
    server: Google Frontend
    content-length: 227

    {"AD":[{"Code/Subdivision change":"","Date Issued":"2007-04-17"...}

### Request
`GET /alpha2/DM/year/2007`

    curl -i https://iso3166-updates.com/api?alpha2=DM&year=2007
    curl -i https://iso3166-updates.com/api/alpha2/DM/year/2007

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:38:20 GMT
    server: Google Frontend
    content-length: 348

    {"DM":[{"Code/Subdivision change":"Subdivisions added:..., "Date Issued": "2007-04-17"}

### Python
```python
import requests

base_url = "https://iso3166-updates.com/api"

all_request = requests.get(base_url, params={"alpha2": "AD", "year": "2007"}) 
# all_request = requests.get(base_url, params={"alpha2": "DM", "year": "2007"}) 
all_request.json() 
```

### Javascript
```javascript
function getData() {
  const response = 
    await fetch('https://iso3166-updates.com/api' + 
        new URLSearchParams({
            alpha2: 'AD',
            year: '2007'
  }));
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country for specified year range e.g Bosnia, Haiti for 2009-2015
-------------------------------------------------------------------------------------------

### Request
`GET /alpha2/BA/year/2009-2015`

    curl -i https://iso3166-updates.com/api?alpha2=BA&year=2009-2015
    curl -i https://iso3166-updates.com/api/alpha2/BA/year/2009-2015

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 20:19:23 GMT
    server: Google Frontend
    content-length: 1111

    {"BA":[{"Code/Subdivision change":"","Date Issued":"2015-11-27"...}

### Request
`GET /alpha2/HT/year/2009-2015`

    curl -i https://iso3166-updates.com/api?alpha2=HT&year=2009-2015
    curl -i https://iso3166-updates.com/api/alpha2/HT/year/2009-2015

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 07 Jan 2023 17:19:23 GMT
    server: Google Frontend
    content-length: 476

    {"HT":[{"Code/Subdivision change":"",...}

### Python
```python
import requests

base_url = "https://iso3166-updates.com/api"

all_request = requests.get(base_url, params={"alpha2": "BA", "year": "2009-2015"}) 
# all_request = requests.get(base_url, params={"alpha2": "HT", "year": "2009-2015"}) 
all_request.json() 
```

### Javascript
```javascript
function getData() {
  const response = 
    await fetch('https://iso3166-updates.com/api' + 
        new URLSearchParams({
            alpha2: 'BA',
            year: '2009-2015'
  }));
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country less than/greater than specified year e.g Israel, Lithuania <2010 or >2012
-------------------------------------------------------------------------------------------------------------

### Request
`GET /alpha2/IL/year/<2010`

    curl -i https://iso3166-updates.com/api?alpha2=IL&year=<2010
    curl -i https://iso3166-updates.com/api/alpha2/IL/year/<2010

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 05 Mar 2023 17:19:23 GMT
    server: Google Frontend
    content-length: 3

    {}

### Request
`GET /alpha2/LT/year/<2012`

    curl -i https://iso3166-updates.com/api?alpha2=LT&year=>2012
    curl -i https://iso3166-updates.com/api/alpha2/LT/year/>2012

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 07 Jan 2023 17:19:23 GMT
    server: Google Frontend
    content-length: 637

    {"LT":[{"Code/Subdivision change":...}

### Python
```python
import requests

base_url = "https://iso3166-updates.com"

all_request = requests.get(base_url, params={"alpha2": "IL", "year": "<2010"}) 
# all_request = requests.get(base_url, params={"alpha2": "LT", "year": ">2012"}) 
all_request.json() 
```

### Javascript
```javascript
function getData() {
  const response = 
    await fetch('https://iso3166-updates.com' + 
        new URLSearchParams({
            alpha2: 'IL',
            year: '<2010'
  }));
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all updates for all countries from the past 3 or 6 months
-------------------------------------------------------------

### Request
`GET /months/3`

    curl -i https://iso3166-updates.com/api?months=3
    curl -i https://iso3166-updates.com/api/months/3

### Response
    HTTP/2 200 
    Date: Thu, 06 Apr 2023 12:36:30 GMT
    Connection: close
    Content-Type: application/json
    Content-Length: 3

    {}

### Python
```python
import requests

base_url = "https://iso3166-updates.com"

all_request = requests.get(base_url, params={"months": "3"}) 
all_request.json() 
```

### Javascript
```javascript
function getData() {
  const response = 
    await fetch('https://iso3166-updates.com' + 
        new URLSearchParams({
            months: 3
  }));
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

### Request
`GET /months/6`

    curl -i https://iso3166-updates.com/api?months=6
    curl -i https://iso3166-updates.com/api/months/6

### Response
    HTTP/2 200 
    Date: Thu, 06 Apr 2023 14:36:30 GMT
    Connection: close
    Content-Type: application/json
    Content-Length: 4818

    {"DZ":[{"Code/Subdivision change":""...}

### Python
```python
import requests

base_url = "https://iso3166-updates.com"

all_request = requests.get(base_url, params={"months": "6"}) 
all_request.json() 
```

### Javascript
```javascript
function getData() {
  const response = 
    await fetch('https://iso3166-updates.com' + 
        new URLSearchParams({
            months: 6
  }));
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

[flask]: https://flask.palletsprojects.com/en/2.3.x/
[python]: https://www.python.org/downloads/release/python-360/
[requests]: https://requests.readthedocs.io/
[iso3166]: https://github.com/deactivated/python-iso3166
[python-dateutil]: https://pypi.org/project/python-dateutil/
[google-auth]: https://cloud.google.com/python/docs/reference
[google-cloud-storage]: https://cloud.google.com/python/docs/reference
[google-api-python-client]: https://cloud.google.com/python/docs/reference