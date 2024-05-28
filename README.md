# iso3166-updates 🌎

[![iso3166_updates](https://img.shields.io/pypi/v/iso3166-updates)](https://pypi.org/project/iso3166-updates/)
[![pytest](https://github.com/amckenna41/iso3166-updates/workflows/Building%20and%20Testing/badge.svg)](https://github.com/amckenna41/iso3166-updates/actions?query=workflowBuilding%20and%20Testing)
[![CircleCI](https://dl.circleci.com/status-badge/img/gh/amckenna41/iso3166-updates/tree/main.svg?style=svg&circle-token=9b0c0a9f6cc032f255dc28842c95600401aa4426)](https://dl.circleci.com/status-badge/redirect/gh/amckenna41/iso3166-updates/tree/main)
[![PythonV](https://img.shields.io/pypi/pyversions/iso3166-updates?logo=2)](https://pypi.org/project/iso3166-updates/)
[![Platforms](https://img.shields.io/badge/platforms-linux%2C%20macOS%2C%20Windows-green)](https://pypi.org/project/iso3166-updates/)
[![Documentation Status](https://readthedocs.org/projects/iso3166-updates/badge/?version=latest)](https://iso3166-updates.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/github/license/amckenna41/iso3166-updates)](https://opensource.org/licenses/MIT)
[![Issues](https://img.shields.io/github/issues/amckenna41/iso3166-updates)](https://github.com/amckenna41/iso3166-updates/issues)
<!-- [![Size](https://img.shields.io/github/repo-size/amckenna41/iso3166-updates)](https://github.com/amckenna41/iso3166-updates) -->
<!-- [![Commits](https://img.shields.io/github/commit-activity/w/amckenna41/iso3166-updates)](https://github.com/iso3166-updates) -->
<!-- [![codecov](https://codecov.io/gh/amckenna41/iso3166-updates/graph/badge.svg?token=XOBSBVH8XA)](https://codecov.io/gh/amckenna41/iso3166-updates) -->

<div alt="images" style="justify-content: center; display:flex; margin-left=10px;">
  <img src="https://upload.wikimedia.org/wikipedia/commons/3/3d/Flag-map_of_the_world_%282017%29.png" alt="globe" height="300" width="600"/>
  <!-- <img src="https://upload.wikimedia.org/wikipedia/commons/e/e3/ISO_Logo_%28Red_square%29.svg" alt="iso" height="300" width="400"/> -->
</div>

> Software and accompanying API that checks for any updates/changes to the ISO 3166-1 and ISO 3166-2 country codes and subdivision naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui). Available via a lightweight Python software package as well as an API. 

* A <b>demo</b> of the software and API is available [here][demo_iso3166_updates].
* A <b>demo</b> of the script used to pull and export all the latest updates is available [here][demo_get_all_iso3166_updates].
* A <b>Medium</b> article that dives deeper into `iso3166-updates` is available [here][medium].
* The front-end <b>API</b> is available [here][api].
* The **documentation** for the software is available [here](https://iso3166-updates.readthedocs.io/en/latest/).

Table of Contents
-----------------
- [Introduction](#introduction)
- [API](#api)
- [Documentation](#documentation)
- [Staying up to date](#staying-up-to-date)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage (iso3166-updates)](#usage-iso3166-updates-Python-package)
- [Usage (get_all_iso3166_updates.py script)](#usage-get_all_iso3166_updates.py-script)
- [Directories](#Directories)
- [Issues](#Issues)
- [Contact](#contact)
- [References](#references)

Introduction
------------
`iso3166-updates` is a software and accompanying API that consists of a series of scripts that check for any updates/changes to the ISO 3166 country codes and subdivision naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui).

The ISO 3166 standard by the ISO (International Organization for Standardisation) defines codes for the names of countries, dependent territories, special areas of geographical interest, consolidated into the ISO 3166-1 standard [[1]](#references), and their principal subdivisions (e.g., provinces, states, departments, regions etc), which comprise the ISO 3166-2 standard [[2]](#references). The ISO 3166-1 was first published in 1974 and currently comprises 249 countries, 193 of which are sovereign states that are members of the United Nations 🇺🇳 [[1]](#references). The ISO 3166-2 was first published in 1998 and as of November 2023 there are **5,039** codes defined in it [[2]](#references).

### Problem Statement:

The ISO is a very dynamic organisation and regularly change, update and or remove entries within its library of standards, including the ISO 3166. Additions, changes and or deletions to country/territorial codes occur less often in the ISO 3166-1, but changes are more frequent for the ISO 3166-2 codes due to there being thousands more entries, thus it can be difficult to keep up with and track these changes. These changes can occur for a variety of geopolitical and administrative reasons. Previously these changes were communicated via newsletters; but as of July 2013 these changes are now communicated via their online catalogue/Online Browsing Platform (OBP), or via a database, which usually costs money to subscribe to (**up to $300**) [[3]](#references). Usually these updates are conveyed at the end of the year, with amendments and updates occasionally published at various times throughout the year [[4]](#references). 

This software and accompanying API make it extremely easy to check for any new or historic updates to a country or set of country's ISO 3166-2 codes for free; with an easy-to-use interface and Python package and API, ensuring that you get the most up-to-date and accurate ISO 3166-2 codes and naming conventions.

### Intended Audience:

This software and accompanying API is for anyone working with country data at the ISO 3166 level. It's of high importance that the data you are working with is correct and up-to-date, especially with consistent changes being posted every year since 2000 (excluding 2001 and 2006). Also, it's aimed not just at developers of ISO 3166 applications but for anyone working in that space, hence the creation of an easy-to-use API (https://iso3166-updates.com). 

Last Updated
------------
The list of ISO 3166 updates was last updated on **March 2024**, with over **~950** individual published updates. A log of the latest ISO 3166 updates can be seen in the [UPDATES.md][updates_md]. 

<!-- <strong> The earliest date for any ISO 3166 updates is 2000-06-21, and the most recent is 2024-02-29. </strong> -->

API
---
The main API endpoint is:

> https://iso3166-updates.com/api

The other endpoints available in the API are:
* https://iso3166-updates.com/api/all
* https://iso3166-updates.com/api/alpha/<input_alpha>
* https://iso3166-updates.com/api/name/<input_name>
* https://iso3166-updates.com/api/year/<input_year>
* https://iso3166-updates.com/api/alpha/<input_alpha>/year/<input_year>
* https://iso3166-updates.com/api/name/<input_name>/year/<input_year>
* https://iso3166-updates.com/api/months/<input_month>
* https://iso3166-updates.com/api/months/<input_month>/alpha/<input_alpha>
* https://iso3166-updates.com/api/months/<input_month>/name/<input_name>

The main paths/endpoints available in the API are - `/api/all`, `/api/alpha`, `/api/name`, `/api/year` and `/api/months`. 

* `/api/all`: get all of the ISO 3166 updates/changes data for all countries.

* `/api/alpha`: get all the ISO 3166 updates/changes data for one or more countries according to their ISO 3166-1 alpha-2, alpha-3 or numeric country codes. A single alpha code or a list of them can be passed to the API e.g. `/api/alpha/AL`, `/api/alpha/BW`, `/api/alpha/FR,DE,HUN,IDN,504`. If an invalid alpha code is input then an error will be returned. This endpoint can be used in conjunction with the **year** and **month** endpoints to get the country updates for a specific country and year, and the country updates for a specific country over the past number of months, respectively. This will be in the format: `/api/alpha/<input_alpha>/year/<input_year>` and `/api/alpha/<input_alpha>/months/<input_month>`, respectively.

* `/api/name`: get all the ISO 3166 updates/changes data for one or more countries according to their country name, as listed in the ISO 3166-1. A single country name or list of them can be passed to the API e.g. `/api/name/Brazil`, `/api/name/Colombia`, `/api/name/Benin,France,Moldova`. A closeness function is used to get the most approximate available country from the one input, e.g. Sweden will be used if the input is `/api/name/Swede`. If no matching country is found from the closeness function or an invalid name is input then an error will be returned. This endpoint can be used in conjunction with the **year** and **months** endpoint to get the country updates for a specific country name and year and the country updates for a specific country over the past number of months, respectively. This will be in the format: `/api/name/<input_name>/year/<input_year>` and `/api/name/<input_name>/months/<input_month>`, respectively. 

* `/api/year`: get all the ISO 3166 updates/changes data for one or more countries according to a specific year, year range, or a cut-off year to get updates less than/more than a year, e.g. `/api/year/2017`, `/api/year/2010-2015`, `/api/year/<2009`, `/api/year/>2002`. If an invalid year is input then an error will be returned. This endpoint can be used in conjunction with the **alpha** and **name** endpoints to get the country updates for a specific country and year. This will be in in the format `/api/alpha/<input_alpha>/year/<input_year>` and `/api/name/<input_name>/year/<input_year>`, respectively. 

* `/api/months`: get all the ISO 3166 updates/changes data for one or more countries from an input number of months from the present day, e.g. `/api/months/12`, `/api/months/24`, `/api/months/50`. A month range can also be input to get the updates published within a specified range of months, with the start and end month separated by a '-' e.g. `/api/months/12-24`, `/api/months/36-50`. If an invalid month value is input then an error will be returned. This endpoint can be used in conjunction with the **alpha** and **name** endpoints to get the country updates for a specific country over the past number of months using their ISO 3166-1 alpha code or country name, respectively. This will be in the format: `/api/months/<input_month>/alpha/<input_alpha>` and `/api/months/<input_month>/name/<input_name>`, respectively.

* `/api`: main homepage and API documentation.

The API was originally hosted and built using GCP, with a Cloud Function being used in the backend, fronted by an api gateway and load balancer. The function calls a GCP Storage bucket to access the back-end JSON where all ISO 3166 updates are stored. <i>Although, due to the cost of infrastructure, the hosting was switched to Vercel (https://vercel.com/).</i>

The full list of attributes available for each country are:

* Code/Subdivision change: overall summary of change/update made.
* Description of change: more in-depth info about the change/update that was made, including any remarks listed on the official ISO page.
* Date Issued: date that the change was communicated.
* Edition/Newsletter: name and or edition of newsletter that the ISO 3166 change/update was communicated in (pre 2013), or the link to the country's ISO Online Browsing Platform page.

Documentation
-------------
Documentation for the software and accompanying API is available on the software's [readthedocs](https://iso3166-updates.readthedocs.io/en/latest/) page. Additionally the API's documentation is available on the API [homepage](https://iso3166-updates.com/api). A demo of both is also available [here][demo_iso3166_updates].

<!-- <p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166-updates-api/gcp_architecture.png?raw=true" alt="gcp_arch" height="500" width="750"/>
</p> -->

Staying up to date
------------------
The list of ISO 3166 updates was last updated on <strong>March 2024</strong>.

The object storing all updates - iso3166-updates.json - for the software package is consistently checked for the latest updates using a Google Cloud Run microservice ([iso3166-check-for-updates](https://github.com/amckenna41/iso3166-updates/tree/main/iso3166-check-for-updates)). The application is built using a custom Docker container that uses the `iso3166-updates` Python software to pull all the latest updates/changes from the various data sources, to check for the latest updates within a certain period e.g. the past 6-12 months (this month range is used as the ISO usually publishes their updates at the end of the year with occasional mid-year updates). The app compares the generated output with that of the updates JSON currently in the software package and will replace this json to integrate the latest updates found, such that the API will have the most **up-to-date** and **accurate** data. A Cloud Scheduler is used to call the application on the aforementioned schedule. 

Additionally, a GitHub Issue in the custom-built [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates), [`iso3166-2`](https://github.com/amckenna41/iso3166-2) and [`iso3166-flag-icons`](https://github.com/amckenna41/iso3166-flag-icons) repositories will be automatically created that formats and tabulates all updates/changes that need to be implemented into the JSONs on the aforementioned repos.

Ultimately, this Cloud Run microservice ensures that the software and associated APIs are up-to-date with the **most latest, accurate** and **reliable** ISO 3166-2 information for all countries/territories/subdivisions etc.

Requirements
------------
* [python][python] >= 3.8
* [iso3166][iso3166] >= 2.1.1 
* [python-dateutil][python-dateutil] >= 2.9.0

Installation
------------
Install the latest version of `iso3166-updates` via [PyPi][PyPi] using pip:

```bash
pip3 install iso3166-updates --upgrade
```

Usage (iso3166-updates Python package)
--------------------------------------
Below are some examples of using the custom-built `iso3166-updates` Python package. 

**Import package:**
```python
from iso3166_updates import *
```

**Create instance of ISO3166_Updates() class**
```python
iso = ISO3166_Updates()
```

**Get all listed changes/updates for all countries and years:**
```python
iso.all
```

**Get all listed ISO 3166 changes/updates for Andorra (AD):**
```python
iso["AD"]
```

**Get all listed ISO 3166 changes/updates for BA, DE, FR, HU, PY:**
```python
iso["BA","DE","FRA","HUN","600"]
```

**Get all listed ISO 3166 changes/updates for all countries, for years 2002, 2005 and 2009:**
```python
iso.year("2002, 2005, 2009")
```

**Get all listed ISO 3166 changes/updates for all countries, for year range 2013-2016, inclusive:**
```python
iso.year("2013-2016")
```

**Get all listed ISO 3166 changes/updates for all countries, for all years after 2017, inclusive:**
```python
iso.year(">2017")
```

**Get any listed ISO 3166 changes/updates for Ireland, between years 2012 and 2021:**
```python
iso.year("2012-2021").IE
```

**Get any listed ISO 3166 changes/updates for Tanzania, with updates with year >= 2015:**
```python
iso.year(">2015").TA
```

**Get any listed ISO 3166 changes/updates for Romania, with updates with year < 2007:**
```python
iso.year("<2007").RO
```

**Get any listed ISO 3166 changes/updates for Yemen, with updates with year < 2010:**
```python
iso.year("<2010")["YE"]
```

**Get any listed ISO 3166 changes/updates published over the past 12 months:**
```python
iso.months("12")
```

**Get any listed ISO 3166 changes/updates published over the past 36-48 months:**
```python
iso.months("36-48")
```

Usage (get_all_iso3166_updates.py script)
-----------------------------------------
Below are some examples of using the `get_all_iso3166_updates.py` script which is used to pull all the ISO 3166 updates
from the various data sources.

**Requirements:**
* [python][python] >= 3.8
* [iso3166-updates][iso3166-updates] >= 1.3.0
* [pandas][pandas] >= 1.4.4
* [requests][requests] >= 2.28.1
* [beautifulsoup4][beautifulsoup4] >= 4.11.1
* [iso3166][iso3166] >= 2.1.1
* [selenium][selenium] >= 4.10.0
* [flask][flask] >= 2.3.2
* [tqdm][tqdm] >= 4.64.0

**Input parameters to get_updates function:**
```python
  # -alpha_codes ALPHA_CODES, --alpha_codes ALPHA_CODES
  #                       ISO 3166-1 alpha-2, alpha-3 or numeric code/s of the ISO 3166 countries to get updates from (default=[]-meaning use all country codes).
  # -year YEAR, --year YEAR
  #                       Selected year/years, year ranges or year to check for updates greater
  #                       than or less than specified year (default=[]).
  # -export_filename EXPORT_FILENAME, --export_filename EXPORT_FILENAME
  #                       Filename for exported ISO 3166 updates for CSV and JSON files (default="iso3166-updates").
  # -export_folder EXPORT_FOLDER, --export_folder EXPORT_FOLDER
  #                       Folder where to store exported ISO 3166 files (default="iso3166-updates-output").
  # -concat_updates CONCAT_UPDATES, --concat_updates CONCAT_UPDATES
  #                       Whether to concatenate updates of individual countries into the same json file or separate
  #                       into separate files (default=True).
  # -export_json EXPORT_JSON, --export_json EXPORT_JSON
  #                       Whether to export all found updates to json in export folder (default=True).
  # -export_csv EXPORT_CSV, --export_csv EXPORT_CSV
  #                       Whether to export all found updates to csv files in export folder (default=True).
  # -verbose VERBOSE, --verbose VERBOSE
  #                       Set to 1 to print out progress of updates function, 0 will not print progress (default=True).
  # -use_selenium USE_SELENIUM, --use_selenium USE_SELENIUM
  #                       Gather all data for each country from its official page on the ISO website which 
  #                       requires Python Selenium and Chromedriver. If False then just use country data
  #                       from its wiki page (default=True).
```
<!-- **Get all the latest updates for all ISO 3166 countries:**
```bash
./get_all_updates.sh 

'''
--export_filename     Filename for exported JSON/CSV files containing updates data (default="iso3166-updates").
--export_folder       Folder name to store exported JSON/CSV files containing updates data (default="test-iso3166-updates).
'''
``` -->

<!-- **Import module:**
```python
import get_all_iso3166_updates as iso3166_updates
```

**Get all listed ISO 3166 changes/updates for BA, DE, FR, HU, PY, export only JSON of updates to export folder "iso3166-updates", print progress using verbose flag:**
```python
iso3166_updates.get_updates(["BA","DE","FR","HU","PY"], export_folder="iso3166-updates", export_json=1, export_csv=0, verbose=1)
#exported files: /iso3166-updates/iso3166-updates-BA,DE,FR,HU,PY.json
```

**Get any listed ISO 3166 changes/updates for HU, IT, JA, KE, in the year 2018, export only to JSON with filename "iso3166-updates.json" and separate updates into separate JSON files (concat_updates=False):**
```python
iso3166_updates.get_updates("HU, IT, JA, KE", year="2018", export_json=1, export_csv=0, export_filename="iso3166-updates", concat_updates=0)
#exported files: /iso3166-updates/iso3166-updates-HU,IT,JA,KE-2018.json
```

**Get any listed ISO 3166 changes/updates for Ireland, between years 2012 and 2021, use default parameters (export to json but not csv):**
```python
iso3166_updates.get_updates("IE", year="2012-2021")
#exported files: /iso3166-updates/iso3166-updates-IE_2012-2021.json
```

**Get any listed ISO 3166 changes/updates for Tanzania, with updates with year >= 2015, export only to CSV with filename "iso3166-output":**
```python
iso3166_updates.get_updates("TA", year=">2015", export_filename="iso3166-output", export_json=0, export_csv=1)
#exported files: /iso3166-updates/iso3166-output-TA_>2015.csv
```

**Get any listed ISO 3166 changes/updates for Yemen, with updates with year < 2010, use default parameters (export to json but not csv):**
```python
iso3166_updates.get_updates("YE", year="<2010")
#exported files: /iso3166-updates/iso3166-output-YE_<2010.json
``` -->

The output files from the <i>get_all_iso3166_updates.py</i> script for the updates/changes to an ISO 3166-2 country returns 4 columns: 
<b>Code/Subdivision Change, Description of Change, Date Issued</b> and <b>Edition/Newsletter.</b> For the CSV export, if more than one country input, then an additional primary key column <b>Country Code</b> will be prepended to the first column, which will be the 2 letter ISO 3166-1 country code. 

* Code/Subdivision Change: overall summary of change/update made.
* Description of Change: more in-depth info about the change/update that was made, including any remarks listed on the official ISO page.
* Date Issued: date that the change was communicated.
* Edition/Newsletter: name and or edition of newsletter that the ISO 3166 change/update was communicated in (pre 2013), or the link to the country's ISO Online Browsing Platform page.

E.g. The output format of the exported <b>CSV</b> for AD (Andorra) is:

| Code/Subdivision Change | Description of Change | Date Issued | Edition/Newsletter |   
|:-------------------|:------------|------------------------------------:|------------------------:|
| Subdivisions added: 7 parishes.   | Addition of the administrative subdivisions and of their code elements. | 2007-04-17 | Newsletter I-8. | 
| Update List Source. |  | 2014-11-03 | Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:AD) | 
| Update List Source. |  | 2015-11-27 | Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:AD) | 

E.g. The output format of the exported <b>JSON</b> for AD (Andorra) is:
```javascript
{
  "AD": [
      {
          "Code/Subdivision Change": "Update List Source.",
          "Description of Change": "",
          "Date Issued": "2015-11-27",
          "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD)."
      },
      {
          "Code/Subdivision Change": "Update List Source.",
          "Description of Change": "",
          "Date Issued": "2014-11-03",
          "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD)."
      },
      {
          "Code/Subdivision Change": "Subdivisions added: 7 parishes.",
          "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
          "Date Issued": "2007-04-17",
          "Edition/Newsletter": "Newsletter I-8 (https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)."

      }
  ]
}
```

Directories 
-----------
* `/iso3166_updates` - source code for `iso3166-updates` Python package.
* `/iso3166-check-for-updates` - all code and files related to the serverless Google Cloud Run microservice for the check-for-updates function which is a periodically called Cloud Run app that uses the Python software to check for the latest updates for all ISO 3166 countries, ensuring the API and jsons are reliable, accurate and up-to-date.
* `/docs` - documentation for `iso3166-updates`, available on [readthedocs](https://iso3166-updates.readthedocs.io/en/latest/).
* `/tests` - unit and integration tests for `iso3166-updates` software and API.
* `get_all_iso3166_updates.py` - python module that pulls and exports all the latest ISO 3166 data from the various data sources.
<!-- * `get_all_iso3166-updates.sh` - shell script created to call the get_all_iso3166_updates.py script to introduce some pseudo randomness required when using Python Selenium.  -->
* `UPDATES.md` - log of all the latest updates from 2022 onwards. 

Issues
------
Any issues, errors/bugs or enhancements can be raised via the [Issues][Issues] tab in the repository.

Contact 
-------
If you have any questions or comments, please contact amckenna41@qub.ac.uk or raise an issue on the [Issues][Issues] tab. <br><br>
<!-- [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/adam-mckenna-7a5b22151/) -->

Other ISO 3166 repositories
---------------------------
Below are some of my other custom-built repositories that relate to the ISO 3166 standard.

* [iso3166-updates-api](https://github.com/amckenna41/iso3166-updates-api): frontend API for iso3166-updates.
* [iso3166-2](https://github.com/amckenna41/iso3166-2): a lightweight custom-built Python package, and accompanying API, that can be used to access all of the world's ISO 3166-2 subdivision data. A plethora of data attributes are available per country and subdivision including: name, local name, code, parent code, type, lat/longitude and flag. Currently, the package and API supports data from 250 countries/territories, according to the ISO 3166-1 standard.
* [iso3166-2-api](https://github.com/amckenna41/iso3166-2-api): frontend API for iso3166-2.
* [iso3166-flag-icons](https://github.com/amckenna41/iso3166-flag-icons): a comprehensive library of over 3500 country and regional flags from the ISO 3166-1 and ISO 3166-2 standards.

References
----------
\[1\]: ISO 3166-1: https://en.wikipedia.org/wiki/ISO_3166-1 <br>
\[2\]: ISO 3166-2: https://en.wikipedia.org/wiki/ISO_3166-2 <br>
\[3\]: ISO Country Codes Collection: https://www.iso.org/publication/PUB500001 <br>
\[4\]: ISO Country Codes: https://www.iso.org/iso-3166-country-codes.html <br>
\[5\]: ISO 3166-1 flag-icons repo: https://github.com/lipis/flag-icons <br>
\[6\]: ISO 3166-2 flag-icons repo: https://github.com/amckenna41/iso3166-flag-icons <br>

Support
-------
<a href="https://www.buymeacoffee.com/amckenna41" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

[Back to top](#TOP)

[demo_iso3166_updates]: https://colab.research.google.com/drive/1oGF3j3_9b_g2qAmBtv3n-xO2GzTYRJjf?usp=sharing
[demo_get_all_iso3166_updates]: https://colab.research.google.com/drive/161aclDjGkWQJhis7KxBO1e6H_ghQOPRG?usp=sharing
[api]: https://www.iso3166-updates.com/api
[medium]: https://medium.com/@ajmckenna69/iso3166-updates-d06b817af3a7
[python]: https://www.python.org/downloads/release/python-360/
[iso3166-updates]: https://github.com/amckenna41/iso3166-updates
[python-dateutil]: https://pypi.org/project/python-dateutil/
[pandas]: https://pandas.pydata.org/
[tqdm]: https://github.com/tqdm/tqdm
[requests]: https://requests.readthedocs.io/
[beautifulsoup4]: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
[google-auth]: https://cloud.google.com/python/docs/reference
[google-cloud-storage]: https://cloud.google.com/python/docs/reference
[google-api-python-client]: https://cloud.google.com/python/docs/reference
[flask]: https://flask.palletsprojects.com/en/2.3.x/
[emoji-country-flag]: https://pypi.org/project/emoji-country-flag/
[gunicorn]: https://pypi.org/project/gunicorn/
[selenium]: https://selenium-python.readthedocs.io/index.html
[webdriver-manager]: https://pypi.org/project/webdriver-manager/
[lxml]: https://lxml.de/
[updates_md]: https://github.com/amckenna41/iso3166-updates/blob/main/UPDATES.MD
[iso3166]: https://github.com/deactivated/python-iso3166
[PyPi]: https://pypi.org/project/iso3166-updates/
[Issues]: https://github.com/amckenna41/iso3166-updates/issues