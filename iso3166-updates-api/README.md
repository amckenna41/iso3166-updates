# ISO3166 Updates API

![Vercel](https://therealsujitk-vercel-badge.vercel.app/?app=iso3166-updates-frontend)

An API is available that can be used to extract any applicable updates for a country via a URL. The API is available at the URL:

> https://www.iso3166-updates.com/api

Three query string parameters are available in the API - `alpha2`, `year` and `months`. 

* The 2 letter alpha-2 country code can be appended to the url as a query string parameter or as its own path ("?alpha2=JP" or /alpha2/JP). A single alpha-2 or list of them can be passed to the API (e.g "?alpha2="FR, DE, HU, ID, MA" or /alpha2/FR,DE,HU,ID,MA). The 3 letter alpha-3 counterpart for each country's alpha-2 code can also be passed into the `alpha2` parameter (e.g "?alpha2="FRA, DEU, HUN, IDN, MAR" or /alpha2/FRA,DEU,HUN,IDN,MAR). 

* The year parameter can be a specific year, year range, or a cut-off year to get updates less than/more than a year (e.g "/year/2017", "2010-2015", "<2009", ">2002"). 

* Finally, the months parameter will gather all updates for 1 or more alpha-2 codes from a number of months from the present day (e.g "?months=2", "/months/6", "/months/48").

* If no input parameter values specified then all ISO 3166-2 updates for all countries and years will be gotten.

The API was hosted and built using GCP, with a Cloud Function being used in the backend which is fronted by an api gateway and load balancer. The function calls a GCP Storage bucket to access the back-end JSON where all ISO 3166 updates are stored. A complete diagram of the architecture is shown below. Although, due to the cost of infrastructure the hosting was switched to Vercel (https://vercel.com/).

The API documentation and usage with all useful commands and examples to the API is available on the [README](https://github.com/amckenna41/iso3166-updates/blob/main/iso3166-updates-api/README.md) of the iso3166-updates-api folder. 

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

Get updates for a specific country for a specified year e.g Andorra, Dominica for 2007
--------------------------------------------------------------------------------------

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

Get updates for a specific country for a specified year range e.g Bosnia, Haiti for 2009-2015
---------------------------------------------------------------------------------------------

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

Get updates for a specific country less than/greater than a specified year e.g Israel, Lithuania <2010 or >2012
---------------------------------------------------------------------------------------------------------------

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