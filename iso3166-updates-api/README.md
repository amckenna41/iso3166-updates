# ISO 3166 Updates API

![Vercel](https://therealsujitk-vercel-badge.vercel.app/?app=iso3166-updates-frontend)

The main API endpoint is:

> https://iso3166-updates.com/api

The other endpoints available in the API are:
* https://iso3166-updates.com/api/all
* https://iso3166-updates.com/api/alpha2/<input_alpha2>
* https://iso3166-updates.com/api/name/<input_name>
* https://iso3166-updates.com/api/year/<input_year>
* https://iso3166-updates.com/api/alpha2/<input_alpha2>/year/<input_year>
* https://iso3166-updates.com/api/name/<input_name>/year/<input_year>
* https://iso3166-updates.com/api/months/<input_month>

The paths/endpoints available in the API are - `/api/all`, `/api/alpha2`, `/api/name`, `/api/year` and `/api/months`. 

* The `/api/all` path/endpoint returns all of the ISO 3166-2 updates/changes data for all countries.

* The 2 letter alpha-2 country code can be appended to the **alpha2** path/endpoint e.g. <i>/api/alpha2/JP</i>. A single alpha-2 code or a list of them can be passed to the API e.g. <i>/api/alpha2/FR,DE,HU,ID,MA</i>. For redundancy, the 3 letter alpha-3 counterpart for each country's alpha-2 code can also be appened to the path e.g. <i>/api/alpha2/FRA,DEU,HUN,IDN,MAR</i>. The **alpha2** endpoint can be used in conjunction with the **year** endpoint to get the country updates for a specific country and year, in the format `api/alpha2/<input_alpha2>/year/<input_year>` or `api/year/<input_year>/alpha2/<input_alpha2>`. If an invalid alpha-2 code is input then an error will be returned.

* The name parameter can be a country name as it is most commonly known in English, according to the ISO 3166-1. The name can similarly be appended to the **name** path/endpoint e.g. <i>/api/name/Denmark</i>. A single country name or list of them can be passed into the API e.g. <i>/name/France,Moldova,Benin</i>. A closeness function is used to get the most approximate available country from the one input, e.g. Sweden will be used if the input is <i>/api/name/Swede</i>. The **name** endpoint can be used in conjunction with the **year** endpoint to get the country updates for a specific country name and year, in the format `api/name/<input_name>/year/<input_year>`. If no country is found from the closeness function or an invalid name is input then an error will be returned.

* The **year** parameter can be a specific year, year range, or a cut-off year to get updates less than/more than a year. The year value can be appended to the **year** path/endpoint e.g. <i>/api/year/2017, /api/year/2010-2015, /api/year/<2009, /api/year/>2002</i>. The **year** endpoint can be used in conjunction with the **alpha2** and **name** endpoints to get the country updates for a specific country and year, in the format `api/alpha2/<input_alpha2>/year/<input_year>` and `api/name/<input_name>/year/<input_year>`, respectively. If an invalid year is input then an error will be returned. 

* The **months** parameter will gather all updates for 1 or more countries from an input number of months from the present day. The month value can be appended to the **months** path/endpoint, e.g. <i>/api/months/12, /api/months/24</i> will return all updates/changes from the past 12 and 24 months, respectively. If an invalid month value is input then an error will be returned.

* The main API endpoint (`/` or `/api`) will return the homepage and API documentation.

The API was hosted and built using GCP, with a Cloud Function being used in the backend which is fronted by an api gateway and load balancer. The function calls a GCP Storage bucket to access the back-end JSON where all ISO 3166 updates are stored. <i>Although, due to the cost of infrastructure, the hosting was switched to Vercel (https://vercel.com/).</i>

The full list of attributes available for each country are:

* Edition/Newsletter: name and or edition of newsletter that the ISO 3166 change/update was communicated in.
* Date Issued: date that the change was communicated.
* Code/Subdivision change: overall summary of change/update made.
* Description of change in newsletter: more in-depth info about the change/update that was made.

The API documentation and usage with all useful commands and examples to the API is available below. A demo of the software and API are available [here][demo_iso3166_updates].

<!-- <p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166-updates-api/gcp_architecture.png?raw=true" alt="gcp_arch" height="500" width="750"/>
</p> -->

Get All ISO 3166 updates for all countries
------------------------------------------
### Request
`GET /api/all`

    curl -i https://www.iso3166-updates.com/api/all

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

base_url = "https://iso3166-updates.com/api/"

request_url = base_url + "all"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
function getData() {
  const response = 
    await fetch('https://iso3166-updates.com/api/all');
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country e.g. France, Germany, Hondurus
----------------------------------------------------------------

### Request
`GET /api/alpha2/FR`

    curl -i https://iso3166-updates.com/api/alpha2/FR

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:30:27 GMT
    server: Google Frontend
    content-length: 4513

    "FR":[{"Code/Subdivision change":"Codes...}]

### Request
`GET /api/alpha2/DE`

    curl -i https://iso3166-updates.com/api/alpha2/DE

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:31:19 GMT
    server: Google Frontend
    content-length: 10

    {"DE":{}}

### Request
`GET /api/alpha2/HN`

    curl -i https://iso3166-updates.com/api/alpha2/HN

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:31:53 GMT
    server: Google Frontend
    content-length: 479

    {"HN":[{"Code/Subdivision change":""...}]}

### Python
```python
import requests

base_url = "https://iso3166-updates.com/api/"
input_alpha2 = "FR" #DE, HN

request_url = base_url + f"alpha2/{input_alpha2}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_alpha2 = "FR"; //DE, HN

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.com/api/alpha2/${input_alpha2}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all updates for a specified year e.g. 2004, 2007
---------------------------------------------------

### Request
`GET /api/year/2004`

    curl -i https://iso3166-updates.com/api/year/2004

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:40:19 GMT
    server: Google Frontend
    content-length: 10

    {"AF":[{"Code/Subdivision change":""...}]}

### Request
`GET /api/year/2007`

    curl -i https://iso3166-updates.com/api/year/2007

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:41:53 GMT
    server: Google Frontend
    content-length: 479

    {"AD":[{"Code/Subdivision change":""...}]}

### Python
```python
import requests

base_url = "https://iso3166-updates.com/api/"
input_year = "2004" #2007 

request_url = base_url + f"year/{input_year}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_year = "2004"; //2007

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.com/api/year/${input_year}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country for a specified year e.g. Andorra, Dominica for 2007
--------------------------------------------------------------------------------------

### Request
`GET /api/alpha2/AD/year/2007`

    curl -i https://iso3166-updates.com/api/alpha2/AD/year/2007

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:34:31 GMT
    server: Google Frontend
    content-length: 227

    {"AD":[{"Code/Subdivision change":"","Date Issued":"2007-04-17"...}]}

### Request
`GET /api/alpha2/DM/year/2007`

    curl -i https://iso3166-updates.com/api/alpha2/DM/year/2007

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:38:20 GMT
    server: Google Frontend
    content-length: 348

    {"DM":[{"Code/Subdivision change":"Subdivisions added:..., "Date Issued": "2007-04-17"}]}

### Python
```python
import requests

base_url = "https://iso3166-updates.com/api/"
input_alpha2 = "AD" #DM
input_year = "2007"

request_url = base_url + f"alpha2/{input_alpha2}/year/{input_year}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_alpha2 = "AD"; //DM
let input_year = "2007";

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.com/api/alpha2/${input_alpha2}/year/${input_year}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country for a specified year range e.g. Bosnia, Haiti for 2009-2015, using country name
-----------------------------------------------------------------------------------------------------------------

### Request
`GET /api/name/Bosnia/year/2009-2015`

    curl -i https://iso3166-updates.com/api/name/Bosnia/year/2009-2015

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 20:19:23 GMT
    server: Google Frontend
    content-length: 1111

    {"BA":[{"Code/Subdivision change":"","Date Issued":"2015-11-27"...}]}

### Request
`GET /api/name/Haiti/year/2009-2015`

    curl -i https://iso3166-updates.com/api/name/haiti/year/2009-2015

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 07 Jan 2023 17:19:23 GMT
    server: Google Frontend
    content-length: 476

    {"HT":[{"Code/Subdivision change":"",...}]}

### Python
```python
import requests

base_url = "https://iso3166-updates.com/api/"
input_name = "Bosnia" #Haiti
input_year = "2009-2015"

request_url = base_url + f"name/{input_name}/year/{input_year}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_name = "Bosnia"; //Haiti
let input_year = "2007";

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.com/api/name/${input_name}/year/${input_year}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country less than/greater than a specified year e.g. Israel, Lithuania <2010 or >2012
---------------------------------------------------------------------------------------------------------------

### Request
`GET /api/alpha2/IL/year/<2010`

    curl -i https://iso3166-updates.com/api/alpha2/IL/year/<2010

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 05 Mar 2023 17:19:23 GMT
    server: Google Frontend
    content-length: 3

    {}

### Request
`GET /api/alpha2/LT/year/<2012`

    curl -i https://iso3166-updates.com/api/alpha2/LT/year/>2012

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 07 Jan 2023 17:19:23 GMT
    server: Google Frontend
    content-length: 637

    {"LT":[{"Code/Subdivision change":...}]}

### Python
```python
import requests

base_url = "https://iso3166-updates.com/api/"
input_alpha2 = "IL" #LT
input_year = ">2012"

request_url = base_url + f"alpha2/{input_alpha2}/year/{input_year}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_alpha2 = "IL"; //LT
let input_year = ">2012";

function getData() {
  const response = await fetch(`https://iso3166-updates.com/api/alpha2/${input_alpha2}/year/${input_year}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all ISO 3166 updates data for a specific country, using country name, e.g.. Tajikistan, Seychelles, Uganda
-------------------------------------------------------------------------------------------------------------

### Request
`GET /api/name/Tajikistan`

    curl -i https://iso3166-updates.com/api/name/Tajikistan

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:40:19 GMT
    server: Google Frontend
    content-length: 10

    {"TJ":[{"Code/Subdivision change":...}]}

### Request
`GET /api/name/Seychelles`

    curl -i https://iso3166-updates.com/api/name/Seychelles

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:41:53 GMT
    server: Google Frontend
    content-length: 479

    {"SC":[{"Code/Subdivision change":...}]}

### Request
`GET /api/name/Uganda`

    curl -i https://iso3166-updates.com/api/name/Uganda

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 21 Dec 2022 19:43:19 GMT
    server: Google Frontend
    content-length: 10

    {"UG":[{"Code/Subdivision change":...}]}

### Python
```python
import requests

base_url = "https://iso3166-updates.com/api/"
input_name = "Tajikistan" #Seychelles, Uganda

request_url = base_url + f"name/{input_name}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_name = "Tajikistan"; //Seychelles, Uganda

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.com/api/name/${input_name}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```
Get all updates for all countries from the past 3 or 6 months
-------------------------------------------------------------

### Request
`GET /api/months/3`

    curl -i https://iso3166-updates.com/api/months/3

### Response
    HTTP/2 200 
    Date: Thu, 06 Apr 2023 12:36:30 GMT
    Connection: close
    Content-Type: application/json
    Content-Length: 3

    {}
### Request
`GET /api/months/6`

    curl -i https://iso3166-updates.com/api/months/6

### Response
    HTTP/2 200 
    Date: Thu, 06 Apr 2023 14:36:30 GMT
    Connection: close
    Content-Type: application/json
    Content-Length: 4818

    {"DZ":[{"Code/Subdivision change":""...}]}
### Python
```python
import requests

base_url = "https://iso3166-updates.com/api/"
input_month = "3" #6

request_url = base_url + f"months/{input_month}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_month = "3"; //6

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.com/api/months/${input_month}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

[Back to top](#TOP)

[demo_iso3166_updates]: https://colab.research.google.com/drive/1oGF3j3_9b_g2qAmBtv3n-xO2GzTYRJjf?usp=sharing