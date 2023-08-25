# iso3166-updates 🌎

[![iso3166_updates](https://img.shields.io/pypi/v/iso3166-updates)](https://pypi.org/project/iso3166-updates/)
[![pytest](https://github.com/amckenna41/iso3166-updates/workflows/Building%20and%20Testing/badge.svg)](https://github.com/amckenna41/iso3166-updates/actions?query=workflowBuilding%20and%20Testing)
[![CircleCI](https://dl.circleci.com/status-badge/img/gh/amckenna41/iso3166-updates/tree/main.svg?style=svg&circle-token=9b0c0a9f6cc032f255dc28842c95600401aa4426)](https://dl.circleci.com/status-badge/redirect/gh/amckenna41/iso3166-updates/tree/main)
[![Platforms](https://img.shields.io/badge/platforms-linux%2C%20macOS%2C%20Windows-green)](https://pypi.org/project/iso3166-updates/)
<!-- [![codecov](https://codecov.io/gh/amckenna41/iso3166-updates/branch/main/graph/badge.svg?token=XOBSBVH8XA)](https://codecov.io/gh/amckenna41/iso3166-updates) -->
[![License: MIT](https://img.shields.io/github/license/amckenna41/iso3166-updates)](https://opensource.org/licenses/MIT)
[![Issues](https://img.shields.io/github/issues/amckenna41/iso3166-updates)](https://github.com/amckenna41/iso3166-updates/issues)
<!-- [![Size](https://img.shields.io/github/repo-size/amckenna41/iso3166-updates)](https://github.com/amckenna41/iso3166-updates) -->
<!-- [![Commits](https://img.shields.io/github/commit-activity/w/amckenna41/iso3166-updates)](https://github.com/iso3166-updates) -->

<div alt="images" style="justify-content: center; display:flex; margin-left=50px;">
  <img src="https://upload.wikimedia.org/wikipedia/commons/3/3d/Flag-map_of_the_world_%282017%29.png" alt="globe" height="200" width="500"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/e/e3/ISO_Logo_%28Red_square%29.svg" alt="iso" height="200" width="300"/>
</div>

> Automated scripts and API that check for any updates/changes to the ISO 3166-1 and ISO 3166-2 country codes and subdivision naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui). Available via a lightweight Python software package and API; a demo of both is available [here][demo_iso3166_updates]. There is also a demo of the script used to pull and export all the latest updates, available [here][demo_get_all_iso3166_updates].

Table of Contents
-----------------
  * [Introduction](#introduction)
  * [API](#api)
  * [Staying up to date](#staying-up-to-date)
  * [Requirements](#requirements)
  * [Installation](#installation)
  * [Usage (iso3166-updates-Python-package)](#usage-iso3166-updates-Python-package)
  * [Usage (get_all_iso3166_updates.py script)](#usage-get_all_iso3166_updates.py-script)
  * [Directories](#Directories)
  * [Issues](#Issues)
  * [Contact](#contact)
  * [References](#references)

Introduction
------------
`iso3166-updates` is a repo that consists of a series of scripts that check for any updates/changes to the ISO 3166-2 country codes and subdivision naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui). The ISO 3166 standard by the ISO (International Organization for Standardisation) defines codes for the names of countries, dependent territories, special areas of geographical interest, consolidated into the ISO 3166-1 standard [[1]](#references), and their principal subdivisions (e.g., provinces, states, departments, regions), which comprise the ISO 3166-2 standard [[2]](#references). 

The ISO 3166-1 was first published in 1974 and currently comprises 249 countries, 193 of which are sovereign states that are members of the United Nations 🇺🇳 [[1]](#references). The ISO 3166-2 was first published in 1998 and as of 29 November 2022 there are 5,043 codes defined in it [[2]](#references).

### Problem Statement:

The ISO is a very dynamic organisation and regularly change/update/remove entries within its library of standards, including the ISO 3166. Additions/changes/deletions to country/territorial codes occur less often in the ISO 3166-1, but changes are more frequent for the ISO 3166-2 codes due to there being thousands more entries, thus it can be difficult to keep up with any changes to these codes. These changes can occur for a variety of geopolitical and bureaucratic reasons and are usually communicated via Newsletters on the ISO platform, their Online Browsing Platform (OBP) or via a database, which usually costs money to subscribe to [[3]](#references). Typically these updates are conveyed at the end of the year, with amendments and updates occasionally published at various times throughout the year [[4]](#references). 

This software and accompanying API makes it extremely easy to check for any new or historic updates to a country or set of country's ISO 3166-2 codes for free, with an easy-to-use interface and Python package and API, ensuring that you get the most up-to-date and accurate ISO 3166-2 codes and naming conventions.

<strong> The earliest date for any ISO 3166-2 update is 2000-06-21, and the most recent is 2022-11-29. </strong>

### Intended Audience:

This software and accompanying API is for anyone working with country data at the ISO 3166 level. It's of high importance that the data that you are working with is correct and up-to-date, especially with consistent changes being posted every year since 2000 (excluding 2001 and 2006). Also, it's aimed not just at developers of ISO 3166 applications but for anyone working in that space, hence the creation of an easy-to-use API (https://iso3166-updates.com). 

API
---
An API is available that can be used to extract any applicable updates for a country via an API endpoint. The API is available at the URL:

> https://www.iso3166-updates.com/api

The other endpoints available in the API are:

* https://iso3166-updates.com/api/alpha2/<input_alpha2>
* https://iso3166-updates.com/api/name/<input_name>
* https://iso3166-updates.com/api/year/<input_year>
* https://iso3166-updates.com/api/alpha2/<input_alpha2>/year/<input_year>
* https://iso3166-updates.com/api/name/<input_name>/year/<input_year>
* https://iso3166-updates.com/api/month/<input_month>

Four query string parameters/paths are available in the API - `alpha2`, `name`, `year` and `months`. 

* The 2 letter `alpha2` country code can be appended to the URL as a query string parameter or as its own path (e.g ?alpha2=JP or /alpha2/JP). A single alpha-2 or list of them can be passed to the API (e.g ?alpha2=FR, DE, HU, ID, MA or /alpha2/FR,DE,HU,ID,MA). For redudancy, the 3 letter alpha-3 counterpart for each country's alpha-2 code can also be passed into the `alpha2` parameter (e.g ?alpha2=FRA, DEU, HUN, IDN, MAR or /alpha2/FRA,DEU,HUN,IDN,MAR). 

* The `name` parameter takes in a country's name as it is commonly known in English. The country name can be appended to the URL as a query string parameter or as its own path (e.g ?name=France or /name/France). A single country name or list of them can be passed into the API (e.g ?name=France,Moldova,Benin or /name/France,Moldova,Benin). A closeness function is used to get the most approximate available country from the one the user input; if one is not found then an error is raised.

* The `year` parameter can be a specific year, year range, or a cut-off year to get updates less than/more than a year. The year value can be appended to the URL as a query string parameter or as its own path (e.g ?year=2017 or /year/2017, ?year=2010-2015 or /year/2010-2015, ?year=<2009 or /year/<2009, ?year=2002 or /year/>2002). 

* Finally, the `months` parameter will gather all updates for 1 or more alpha-2 codes from a number of months from the present day. The month value can be appended to the URL as a query string parameter or as its own path (e.g ?months=2 or /months/12, ?months=24 or /months/24).

* If no input parameter values specified then all ISO 3166-2 updates for all countries and years will be returned.

The API was hosted and built using GCP, with a Cloud Function being used in the backend which is fronted by an api gateway and load balancer. The function calls a GCP Storage bucket to access the back-end JSON where all ISO 3166 updates are stored. A complete diagram of the architecture is shown below. <i>Although, due to the cost of infrastructure, the hosting was switched to Vercel (https://vercel.com/).</i>

The API documentation and usage with all useful commands and examples to the API is available on the [README](https://github.com/amckenna41/iso3166-updates/blob/main/iso3166-updates-api/README.md) of the iso3166-updates-api folder. 

<p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166-updates-api/gcp_architecture.png?raw=true" alt="gcp_arch" height="500" width="750"/>
</p>

Staying up to date
------------------
The list of ISO 3166-2 updates was last updated on <strong>Nov 2022</strong>.

The object storing all updates, both locally (iso3166-updates.json) for the software pacakge and on the API in GCP Storage bucket, are consistenly checked for the latest updates using a Google Cloud Run microservice ([iso3166-check-for-updates](https://github.com/amckenna41/iso3166-updates/tree/main/iso3166-check-for-updates)). The application is built using a custom Docker container that uses the `iso3166-updates` Python software to pull all the latest updates/changes, from all ISO 3166-2 wiki's and each country's ISO website page, to check for the latest updates within a certain period e.g. the past 6-12 months (this month range is used as the ISO usually publishes their newsletter at the end of the year with occasional mid-year updates published). The app compares the generated output with that of the updates JSON currently in the Google Cloud Storage bucket and will replace this json to integrate the latest updates found, such that the API will have the most up-to-date data. A Cloud Scheduler is used to periodically call the application.

Additionally, a GitHub Issue in the custom-built `iso3166-updates`, `iso3166-2` and `iso3166-flag-icons` repositories will be automatically created that formats and tabulates all updates/changes that need to be implemented into the `iso3166-updates`, `iso3166-2` and `iso3166-flag-icons` JSONs and repos.

Ultimately, this Cloud Run microservice ensures that the software and assoicated APIs are up-to-date with the latest ISO 3166-2 information for all countries/territories/subdivisions etc.

Requirements
------------
* [python][python] >= 3.8
* [iso3166][iso3166] >= 2.1.1 

Installation
------------
Install the latest version of `iso3166-updates` via [PyPi][PyPi] using pip:

```bash
pip3 install iso3166-updates --upgrade
```

Installation from source:
```bash
git clone -b master https://github.com/amckenna41/iso3166-updates.git
cd iso3166_updates
python3 setup.py install
```

Usage (iso3166-updates Python package)
--------------------------------------
Below are some examples of using the custom-built `iso3166-updates` Python package. 

**Import package:**
```python
import iso3166_updates as iso
```

**Get all listed changes/updates for all countries and years:**
```python
iso.updates.all
```

**Get all listed ISO 3166-2 changes/updates for Andorra (AD):**
```python
iso.updates["AD"]
```

**Get all listed ISO 3166-2 changes/updates for BA, DE, FR, HU, PY:**
```python
iso.updates["BA","DE","FR","HU","PY"]
```

**Get any listed ISO 3166-2 changes/updates for Ireland, between years 2012 and 2021:**
```python
iso.updates.year("2012-2021").IE
```

**Get any listed ISO 3166-2 changes/updates for Tanzania, with updates with year >= 2015:**
```python
iso.updates.year(">2015").TA
```

**Get any listed ISO 3166-2 changes/updates for Romania, with updates with year < 2007:**
```python
iso.updates.year("<2007").RO
```

**Get any listed ISO 3166-2 changes/updates for Yemen, with updates with year < 2010:**
```python
iso.updates.year("<2010")["YE"]
```
Usage (get_all_iso3166_updates.py script)
-----------------------------------------
Below are some examples of using the `get_all_iso3166_updates.py` script which is used to pull all the ISO 3166 updates
from the various data sources.

**Requirements:**
* [python][python] >= 3.8
* [iso3166-updates][iso3166-updates] >= 1.3.0
* [pandas][pandas] >= 1.4.3
* [numpy][numpy] >= 1.23.2
* [requests][requests] >= 2.28.1
* [beautifulsoup4][beautifulsoup4] >= 4.11.1
* [iso3166][iso3166] >= 2.1.1
* [selenium][selenium] >= 4.10.0
* [flask][flask] >= 2.3.2

def get_updates(alpha2_codes=[], year=[], export_filename="iso3166-updates", export_folder="test_iso3166-updates",
        concat_updates=True, export_json=True, export_csv=False, verbose=True, use_selenium=True):
**Input parameters to get_updates function:**
```python
  # -alpha2 ALPHA2, --alpha2 ALPHA2
  #                       Alpha-2 code/s of ISO 3166 countries to check for updates (default=[]).
  # -year YEAR, --year YEAR
  #                       Selected year/years, year ranges or year to check for updates greater
  #                       than or less than specified year (default=[]).
  # -export_filename EXPORT_FILENAME, --export_filename EXPORT_FILENAME
  #                       Filename for exported ISO 3166 updates for CSV and JSON files (default="iso3166-updates").
  # -export_folder EXPORT_FOLDER, --export_folder EXPORT_FOLDER
  #                       Folder where to store exported ISO 3166 files (default="iso3166-updates-output").
  # -concat_updates CONCAT_UPDATES, --concat_updates CONCAT_UPDATES
  #                       Whether to concatenate updates of individual countrys into the same json file or seperate
  #                       into seperate files (default=True).
  # -export_json EXPORT_JSON, --export_json EXPORT_JSON
  #                       Whether to export all found updates to json (default=True).
  # -export_csv EXPORT_CSV, --export_csv EXPORT_CSV
  #                       Whether to export all found updates to csv files in export folder (default=True).
  # -verbose VERBOSE, --verbose VERBOSE
  #                       Set to 1 to print out progress of updates function, 0 will not print progress (default=True).
  # -use_selenium USE_SELENIUM, --use_selenium USE_SELENIUM
  #                       Gather all data for each country from its official page on the ISO website which 
  #                       requires Python Selenium and chromedriver. If False then just use country data
  #                       from its wiki page (default=True).
```
**Get all the latest updates for all ISO 3166 countries**
```bash
./get_all_updates.sh 

'''
--export_filename     Filename for exported JSON/CSV files containing updates data (default="iso3166-updates.json").
--export_folder       Folder name to store exported JSON/CSV files containing updates data (default="test-iso3166-updates).
'''
```

**Import module:**
```python
import get_all_iso3166_updates as iso3166_updates
```

**Get all listed ISO 3166-2 changes/updates for BA, DE, FR, HU, PY, export only JSON of updates to export folder "iso3166-updates", print progress using verbose flag:**
```python
iso3166_updates.get_updates(["BA","DE","FR","HU","PY"], export_folder="iso3166-updates", export_json=1, export_csv=0, verbose=1)
#exported files: /iso3166-updates/iso3166-updates-BA,DE,FR,HU,PY.json
```

**Get any listed ISO 3166-2 changes/updates for HU, IT, JA, KE, in the year 2018, export only to JSON with filename "iso3166-updates.json" and seperate updates into seperate JSON files (concat_updates=False):**
```python
iso3166_updates.get_updates("HU, IT, JA, KE", year="2018", export_json=1, export_csv=0, export_filename="iso3166-updates", concat_updates=0)
#exported files: /iso3166-updates/iso3166-updates-HU,IT,JA,KE-2018.json
```

**Get any listed ISO 3166-2 changes/updates for Ireland, between years 2012 and 2021, use default parameters (export to json but not csv):**
```python
iso3166_updates.get_updates("IE", year="2012-2021")
#exported files: /iso3166-updates/iso3166-updates-IE_2012-2021.json
```

**Get any listed ISO 3166-2 changes/updates for Tanzania, with updates with year >= 2015, export only to CSV with filename "iso3166-output":**
```python
iso3166_updates.get_updates("TA", year=">2015", export_filename="iso3166-output", export_json=0, export_csv=1)
#exported files: /iso3166-updates/iso3166-output-TA_>2015.csv
```

**Get any listed ISO 3166-2 changes/updates for Yemen, with updates with year < 2010, use default parameters (export to json but not csv):**
```python
iso3166_updates.get_updates("YE", year="<2010")
#exported files: /iso3166-updates/iso3166-output-YE_<2010.json
```

The output to the above functions for the updates/changes to an ISO 3166-2 country returns 4 columns: 
<b>Edition/Newsletter, Date Issued, Code/Subdivision Change</b> and <b>Description of Change in Newsletter.</b> For the CSV export, if more than one country input, then an additional primary key column <b>Country Code</b> will be prepended to the first column, which will be the 2 letter ISO 3166-1 country code. 

* Edition/Newsletter: Name and or edition of newsletter that the ISO 3166-2 change/update was communicated in.
* Date Issued: Date that the change was communicated.
* Code/Subdivision Change: Overall summary of change/update made.
* Description of Change in Newsletter: More in-depth info about the change/update that was made.

E.g. The output format of the exported <b>CSV</b> for AD (Andorra) is:

| Edition/Newsletter | Date Issued | Code/Subdivision Change | Description of Change in Newsletter |   
|:-------------------|:------------|------------------------------------:|------------------------:|
| Newsletter I-8.    | 2007-04-17  | Subdivisions added: 7 parishes.   | Addition of the administrative subdivisions and of their code elements.                 | 
| Online Browsing Platform (OBP). | 2014-11-03 | | Update List Source |
| Online Browsing Platform (OBP). | 2015-11-27 | | Update List Source | 

E.g. The output format of the exported <b>JSON</b> for AD (Andorra) is:
```javascript
{
  "AD": [
      {
          "Date Issued": "2015-11-27",
          "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD).",
          "Code/Subdivision Change": "",
          "Description of Change in Newsletter": "Update List Source."
      },
      {
          "Date Issued": "2014-11-03",
          "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD).",
          "Code/Subdivision Change": "",
          "Description of Change in Newsletter": "Update List Source."
      },
      {
          "Date Issued": "2007-04-17",
          "Edition/Newsletter": "Newsletter I-8 (https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf).",
          "Code/Subdivision Change": "Subdivisions added: 7 parishes.",
          "Description of Change in Newsletter": "Addition of the administrative subdivisions and of their code elements."
      }
  ]
}
```

Directories
-----------
* `/docs` - documentation for `iso3166-updates` Python package.
* `/iso3166_updates` - source code for `iso3166-updates` Python package.
* `/iso3166-updates-api` - all code and files related to the serverless Google Cloud Function for the `iso3166-updates` API, including the main.py, requirements.txt and API config file (Update: API moved to serverless app on Vercel platform to save resources).
* `/iso3166-check-for-updates` - all code and files related to the serverless Google Cloud Run microservice for the check-for-updates function which is a periodically called Cloud Run app that uses the Python software to check for the latest updates for all country's, ensuring the API and jsons are reliable and up-to-date.
* `/tests` - unit and integration tests for `iso3166-updates` software and API.
* `get_all_iso3166_updates.py` - python module that pulls and exports all the latest ISO 3166 data from the various data sources.
* `get_all_iso3166-updates.sh` - shell script created to call the get_all_iso3166_updates.py script to introduce some pseudo randomness required when using Python Selenium. 
* `iso3166_updates_demo.ipynb` - demo Python Colab notebook with a demo of the `iso3166-updates` software and accompanying API. The demo is also available on Google Colab [here][demo_iso3166_updates].
* `get_latest_iso3166_updates_demo.ipynb` -  demo Python Colab notebook with a demo of the get_all_iso3166_updates.py script that pulls all the latest ISO 3166 updates/changes from the data sources. The demo is also available on Google Colab [here][demo_get_all_iso3166_updates].

Issues
------
Any issues, errors/bugs or enhancements can be raised via the [Issues](Issues) tab in the repository.

Contact
-------
If you have any questions or comments, please contact amckenna41@qub.ac.uk or raise an issue on the [Issues][Issues] tab. <br><br>
<!-- [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/adam-mckenna-7a5b22151/) -->

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
[python]: https://www.python.org/downloads/release/python-360/
[iso3166-updates]: https://github.com/amckenna41/iso3166-updates
[pandas]: https://pandas.pydata.org/
[numpy]: https://numpy.org/
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
[iso3166]: https://github.com/deactivated/python-iso3166
[PyPi]: https://pypi.org/project/iso3166-updates/
[Issues]: https://github.com/amckenna41/iso3166-updates/issues