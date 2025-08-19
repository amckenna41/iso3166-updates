<a name="TOP"></a>

# iso3166-updates 🌎

[![iso3166_updates](https://img.shields.io/pypi/v/iso3166-updates)](https://pypi.org/project/iso3166-updates/)
[![pytest](https://github.com/amckenna41/iso3166-updates/workflows/Building%20and%20Testing/badge.svg)](https://github.com/amckenna41/iso3166-updates/actions?query=workflow=Building%20and%20Testing)
<!-- [![CircleCI](https://dl.circleci.com/status-badge/img/gh/amckenna41/iso3166-updates/tree/main.svg?style=svg&circle-token=9b0c0a9f6cc032f255dc28842c95600401aa4426)](https://dl.circleci.com/status-badge/redirect/gh/amckenna41/iso3166-updates/tree/main) -->
[![PythonV](https://img.shields.io/pypi/pyversions/iso3166-updates?logo=2)](https://pypi.org/project/iso3166-updates/)
[![Platforms](https://img.shields.io/badge/platforms-linux%2C%20macOS%2C%20Windows-green)](https://pypi.org/project/iso3166-updates/)
[![Documentation Status](https://readthedocs.org/projects/iso3166-updates/badge/?version=latest)](https://iso3166-updates.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/github/license/amckenna41/iso3166-updates)](https://opensource.org/licenses/MIT)
[![Issues](https://img.shields.io/github/issues/amckenna41/iso3166-updates)](https://github.com/amckenna41/iso3166-updates/issues)
<!-- [![Size](https://img.shields.io/github/repo-size/amckenna41/iso3166-updates)](https://github.com/amckenna41/iso3166-updates) -->
<!-- [![Commits](https://img.shields.io/github/commit-activity/w/amckenna41/iso3166-updates)](https://github.com/iso3166-updates) -->
<!-- [![codecov](https://codecov.io/gh/amckenna41/iso3166-updates/branch/main/graph/badge.svg)](https://codecov.io/gh/amckenna41/iso3166-updates) -->

<div alt="images" style="justify-content: center; display:flex; margin-left=10px;">
  <img src="https://upload.wikimedia.org/wikipedia/commons/3/3d/Flag-map_of_the_world_%282017%29.png" alt="globe" height="300" width="600"/>
  <!-- <img src="https://upload.wikimedia.org/wikipedia/commons/e/e3/ISO_Logo_%28Red_square%29.svg" alt="iso" height="300" width="400"/> -->
</div>

> Software and accompanying RESTful API that checks for any updates/changes to the ISO 3166-1 and ISO 3166-2 country codes and subdivision naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui). Available via a lightweight Python software package & REST API. 

Quick Start 🏃
-------------
* A **demo** of the software and API is available [here][demo_iso3166_updates].
* The front-end **API** is available [here][api].
* The **documentation** for the software & API is available [here](https://iso3166-updates.readthedocs.io/en/latest/).
* A **Medium** article that dives deeper into `iso3166-updates` is available [here][medium].
* A **demo** of the script used to pull and export all the latest updates is available [here][demo_get_all_iso3166_updates].

Table of Contents
-----------------
- [Introduction](#introduction)
- [Requirements](#requirements)
- [Installation](#installation)
- [Documentation](#documentation)
- [API](#api)
- [Usage](#usage)
- [Staying up to date](#staying-up-to-date)
- [Directories](#Directories)
- [Issues](#Issues)
- [Contact](#contact)
- [References](#references)
- [Support](#support)
<!-- - [Usage (iso3166_updates_export scripts)](#usage-iso3166_updates_export-scripts) -->

Introduction
------------
`iso3166-updates` is a software and accompanying API that consists of a series of scripts that check for any updates/changes to the ISO 3166 country codes and subdivision naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui).

The ISO 3166 standard by the ISO (International Organization for Standardisation) defines codes for the names of countries, dependent territories, special areas of geographical interest, consolidated into the ISO 3166-1 standard [[1]](#references), and their principal subdivisions (e.g., provinces, states, departments, regions etc), which comprise the ISO 3166-2 standard [[2]](#references). Additionally, the ISO 3166-3 part of the standard represents codes formerly used for countries/territories etc which have been removed from the ISO 3166-1. The ISO 3166-1 was first published in 1974 and currently comprises 249 countries, 193 of which are sovereign states that are members of the United Nations 🇺🇳 [[1]](#references). The ISO 3166-2 was first published in 1998 and as of November 2023 there are **5,039** codes defined in it [[2]](#references). The ISO 3166-3 was first published in 1974 and as of April 2024 there are **73** codes defined in it [[1]]. In the software, <i>only</i> the ISO 3166-1 and ISO 3166-2 are used. 

### Problem Statement:

The ISO is a very dynamic organisation and regularly change, update, and/or remove entries within its library of standards, including the ISO 3166. Additions, changes and or deletions to country/territorial codes occur less often in the ISO 3166-1, but changes are more frequent for the ISO 3166-2 codes due to there being thousands more entries, thus it can be difficult to keep up with and track these changes. These changes can occur for a variety of geopolitical and administrative reasons. Previously these changes were communicated via newsletters; but as of July 2013 these changes are now communicated via their online catalogue/Online Browsing Platform (OBP), or via a database, which usually costs money to subscribe to (**up to $300**) [[3]](#references). Usually these updates are conveyed at the end of the year, with amendments and updates occasionally published at various times throughout the year [[4]](#references). 

This software and accompanying API make it extremely easy to check for any new or historic updates to a country or set of country's ISO 3166-2 codes for free; with an easy-to-use interface and Python package and API, ensuring that you get the most up-to-date and accurate ISO 3166-2 codes and naming conventions.

### Intended Audience:

This software and accompanying API is for anyone working with country data at the ISO 3166 level. It's of high importance that the data you are working with is correct and up-to-date, especially with consistent changes being posted every year since 1996 (excluding 1997, 1998, 1999, 2001 and 2006). Also, it's aimed not just at developers of ISO 3166 applications but for anyone working in that space, hence the creation of an easy-to-use API (https://iso3166-updates.vercel.app/). 

Last Updated
------------
The list of ISO 3166 updates was last updated on **August 2025**, with **911** individual published updates. A log of the latest ISO 3166 updates can be seen in the [UPDATES.md][updates_md]. 

<!-- <strong> The earliest date for any ISO 3166 updates is 1996-03-04, and the most recent is 2024-11-11. </strong> -->

Requirements
------------
* [python][python] >= 3.9
* [iso3166][iso3166] >= 2.1.1 
* [python-dateutil][python-dateutil] >= 2.9.0
* [thefuzz][thefuzz] >= 0.22.1
* [requests][requests] >= 2.28.1

Installation
------------
Install the latest version of `iso3166-updates` via [PyPi][PyPi] using pip:

```bash
pip3 install iso3166-updates
```

Documentation
-------------
Documentation for the software and accompanying API is available on the software's [readthedocs](https://iso3166-updates.readthedocs.io/en/latest/) page. Additionally the API's documentation is available on the API [homepage](https://iso3166-updates.vercel.app/api). A demo of both is also available [here][demo_iso3166_updates].

API
---
The main API endpoint and homepage is:

> https://iso3166-updates.vercel.app/

The other endpoints available in the API are `/api/all`, `/api/alpha/<input_alpha>`, `/api/year/<input_year>`, `/api/country_name/<input_country_name>`, `/api/search/<input_search>` and `/api/date_range/<input_date_range>`.

* `/api`: main homepage and API documentation.

* `/api/all`: get all of the ISO 3166 updates/changes data for all countries and publication years.

* `/api/alpha`: get all the ISO 3166 updates/changes data for one or more countries according to their ISO 3166-1 alpha-2, alpha-3 or numeric country codes. A single alpha code or a list of them can be passed to the API e.g. `/api/alpha/AL`, `/api/alpha/BWA`, `/api/alpha/FR,DE,HUN,IDN,504`. If an invalid alpha code is input then an error will be returned. This endpoint can be used in conjunction with the **year** and **date_range** endpoints to get the country updates for a specific country and year, and the country updates over a specific date range, respectively. This will be in the format: `/api/alpha/<input_alpha>/year/<input_year>` and `/api/alpha/<input_alpha>/date_range/<input_date_range>`, respectively.

* `/api/year`: get all the ISO 3166 updates/changes data for one or more countries according to a specific year, year range, a cut-off year to get updates less than/more than a year or all updates except for a year, e.g. `/api/year/2017`, `/api/year/2010-2015`, `/api/year/<2009`, `/api/year/>2002` and `/api/year/<>2020`. If an invalid year is input then an error will be returned. This endpoint can be used in conjunction with the **alpha** endpoint to get the country updates for a specific country and year. This will be in in the format `/api/alpha/<input_alpha>/year/<input_year>`.

* `/api/country_name`: get all the ISO 3166 updates/changes data for one or more countries according to their name, as it is commonly known in English, e.g. `/api/country_name/Tajikistan`, `/api/country_name/Benin,Togo`, `/api/country_name/Russia,Sudan,Swaziland`. If an invalid country name is input then an error will be returned. This endpoint can be used in conjunction with the **year** endpoint to get the country updates for a specific country and year. This will be in in the format `/api/country_name/<input_country_name>/year/<input_year>`.

* `/api/search`: get all the ISO 3166 updates/changes data for one or more countries that match the inputted search terms. A single keyword/term or list of them can be passed to the API e.g. `/api/search/Brazil`, `/api/search/Addition,deletion`, `/api/search/2017-11-23`. A closeness function is used to search through the updates objects, finding any applicable matches to the keywords input via the Change and Description of Change attributes. If a date is explicitly input then the Date Issued attributes will also be searched. If no matching objects found then an error will be returned. 

* `/api/date_range`: get all the ISO 3166 updates/changes data for one or more countries that were published within a specified input date range e.g. `/api/date_range/2011-12-09,2014-01-10`, `/api/date_range/2013-08-02,2015-07-10`, `/api/date_range/2018-05-12`. If a single date is input it will act as the starting date within the date range, with the end of the range being the current day. If an invalid date type/format value is input then an error will be returned. This endpoint can be used in conjunction with the **alpha** endpoint to get the country updates for a specific country and date range. This will be in in the format `/api/alpha/<input_alpha>/date_range/<input_date_range>`.

### Attributes
There are three main query string parameters that can be passed through several of the endpoints of the API:

* <b>Change</b>: overall summary of change/update made.
* <b>Description of Change</b>: more in-depth info about the change/update that was made, including any remarks listed on the official ISO page.
* <b>Date Issue</b>: date that the change was communicated.
* <b>Source</b>: name and or edition of newsletter that the ISO 3166 change/update was communicated in (pre 2013), or the link to the country's ISO Online Browsing Platform page.

### Query String Parameters
There are three main query string parameters that can be passed through several of the endpoints of the API:

* <b>sortBy</b>: sort the output results by publication date (Date Issued), either descending or ascending. By default, 
the updates data will be returned alphabetically, according to ISO 3166 2 letter country code, but you can order 
by date. The parameter accepts two values: dateDesc and dateAsc - sorting the output by date descending or 
ascending, respectively. If an invalid value input then the output is sorted by country code. This can be appended 
to all of the endpoints, e.g ``/api/all?sortBy=dateDesc``, ``/api/year/2010-2015?sortBy=dateAsc``, 
``/api/date_range/2019-01-01?sortBy=""`` (sorted by country code).
* <b>likeness</b>: this is a value between 1 and 100 that increases or reduces the % of similarity/likeness that the 
inputted search terms have to match to the updates data in the Change and Desc of Change attributes. This can 
only be used in the `/api/search` endpoint. Having a higher value should return more exact and less matches and 
having a lower value will return less exact but more matches, e.g ``/api/search/Paris?likeness=50``, 
``/api/search/canton?likeness=90`` (default=100).
* <b>excludeMatchScore</b>: exclude the matchScore` attribute from the search results when using the /api/search endpoint. 
The match score is the % of a match each returned updates data object is to the search terms, with 100% being an 
exact match. By default the match score is returned for each object, e.g ``/api/search/addition?excludeMatchScore=1``, 
``/api/search/New York?excludeMatchScore=1`` (default=0).


<!-- <p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166-updates-api/gcp_architecture.png?raw=true" alt="gcp_arch" height="500" width="750"/>
</p> -->

Staying up to date
------------------
The list of ISO 3166 updates was last updated on <strong>May 2025</strong>.

The object storing all updates - iso3166-updates.json - for the software package is consistently checked for the latest updates using a Google Cloud Run microservice ([iso3166-check-for-updates](https://github.com/amckenna41/iso3166-updates/tree/main/iso3166-check-for-updates)). The application is built using a custom Docker container that uses the `iso3166-updates` Python software to pull all the latest updates/changes from the various data sources, to check for the latest updates within a certain period e.g. the past 6-12 months (this month range is used as the ISO usually publishes their updates at the end of the year with occasional mid-year updates). The app compares the generated output with that of the updates JSON currently in the software package and will replace this json to integrate the latest updates found, such that the API will have the most **up-to-date** and **accurate** data. A Cloud Scheduler is used to call the application on the aforementioned schedule. 

Additionally, a GitHub Issue in the custom-built [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates), [`iso3166-2`](https://github.com/amckenna41/iso3166-2) and [`iso3166-flag-icons`](https://github.com/amckenna41/iso3166-flag-icons) repositories will be automatically created that formats and tabulates all updates/changes that need to be implemented into the JSONs on the aforementioned repos.

Ultimately, this Cloud Run microservice ensures that the software and associated APIs are up-to-date with the **latest, accurate** and **reliable** ISO 3166-2 information for all countries/territories/subdivisions etc.

Usage 
-----
Below are some examples of using the custom-built `iso3166-updates` Python package. 

**Import package:**
```python
from iso3166_updates import *
```

**Create instance of Updates() class:**
```python
iso = Updates()
```

**Create instance of Updates() class with custom updates filepath:**
```python
iso = Updates(custom_updates_filepath="custom_updates_path.json")
```

**Get all listed changes/updates for all countries and years:**
```python
iso.all
```

**Get all listed ISO 3166 changes/updates for Andorra (AD):**
```python
iso["AD"]
#iso["AND"]
#iso["020"]
```

**Get all listed ISO 3166 changes/updates for BA, DE, FRA, HUN, PY (600):**
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

**Get all listed ISO 3166 changes/updates for all countries, for all years before 2010:**
```python
iso.year("<2010")
```

**Get all listed ISO 3166 changes/updates for all countries, excluding years 2010 & 2019:**
```python
iso.year("<>2010,2019")
```

**Get all listed ISO 3166 changes/updates published that have London or Edinburgh in them via searching:**
```python
iso.search("London, Edinburgh")
```

**Get all listed ISO 3166 changes/updates published that have Addition or Deletion in them via searching, using a likeness score of 0.8:**
```python
iso.search("addition, deletion", likeness_score=0.8)
```

**Get any listed ISO 3166 changes/updates published within the date range 2012-03-12 to 2015-06-25, inclusive:**
```python
iso.date_range("2012-03-12,2015-06-25")
```

**Get any listed ISO 3166 changes/updates published from the date range 2021-10-02, inclusive, sort by date descending rather than country code:**
```python
iso.date_range("2021-10-02", sort_by_date="dateDesc")
```

**Add custom ISO 3166 change/update to main iso3166-updates.json object:**
```python
iso.custom_update("LI", change="Brand new LI subdivision", date_issued="2025-01-01", description_of_change="Short description here.")
iso.custom_update("IE", change="Brand new Belfast subdivision", date_issued="2020-05-12", description_of_change="", source="https:...")
```

**Delete custom ISO 3166 change/update to main iso3166-updates.json object:**
```python
iso.custom_update("LI", change="Brand new LI subdivision", date_issued="2025-01-01", delete=1)
iso.custom_update("IE", change="Brand new Belfast subdivision", date_issued="2020-05-12", delete=1)
```

**Get total number of individual ISO 3166 country updates:**
```python
len(iso)
```

**Get size of dataset in MB:**
```python
iso.__sizeof__()
```

**Check for the latest updates data from the repository:**
```python
iso.check_for_updates()  #compares local dataset with the latest version in the repository
```
<!-- 
Usage (iso3166_updates_export scripts)
-----------------------------------------
Below are some examples of using the `iso3166_updates_export` scripts which are used to pull all the ISO 3166 updates
from the various data sources.

**Requirements:**
* [python][python] >= 3.8
* [iso3166-updates][iso3166-updates] >= 1.7.0
* [pandas][pandas] >= 1.4.4
* [requests][requests] >= 2.28.1
* [beautifulsoup4][beautifulsoup4] >= 4.11.1
* [iso3166][iso3166] >= 2.1.1
* [selenium][selenium] >= 4.10.0
* [tqdm][tqdm] >= 4.64.0
* [fake_useragent][fake_useragent] >= 1.5.0


**Input parameters for main get_iso3166_updates function:**
```python
  # -alpha_codes ALPHA_CODES, --alpha_codes ALPHA_CODES
  #                       ISO 3166-1 alpha-2, alpha-3 or numeric code/s of the ISO 3166 countries to get updates from (default=[]-meaning use all country codes).
  # -year YEAR, --year YEAR
  #                       Selected year/years, year ranges,year to check for updates greater than or less than specified year or not equal to a                       year (default=[]).
  # -export_filename EXPORT_FILENAME, --export_filename EXPORT_FILENAME
  #                       Filename for exported ISO 3166 updates for CSV and JSON files (default="iso3166-updates").
  # -export_folder EXPORT_FOLDER, --export_folder EXPORT_FOLDER
  #                       Folder where to store exported ISO 3166 files (default="iso3166-updates-output").
  # -alpha_codes_range ALPHA_CODES_RANGE, --alpha_codes_range ALPHA_CODES_RANGE
  #                       Range of ISO 3166 alpha codes to export updates data from. If only a single alpha code input
  #                       then it will serve as the starting point of the extract, alphabetically.
  # -concat_updates CONCAT_UPDATES, --concat_updates CONCAT_UPDATES
  #                       Whether to concatenate updates of individual countries into the same json/csv file or split
  #                       into separate files (default=True).
  # -export_json EXPORT_JSON, --export_json EXPORT_JSON
  #                       Whether to export all found updates to json in export folder (default=True).
  # -export_csv EXPORT_CSV, --export_csv EXPORT_CSV
  #                       Whether to export all found updates to csv files in export folder (default=True).
  # -export_xml EXPORT_XML, --export_xml EXPORT_XML
  #                       Whether to export all found updates to xml files in export folder (default=True).
  # -verbose VERBOSE, --verbose VERBOSE
  #                       Set to 1 to print out progress of updates function, 0 will not print progress (default=True).
  # -use_selenium USE_SELENIUM, --use_selenium USE_SELENIUM
  #                       Gather all data for each country from its official page on the ISO website which 
  #                       requires Python Selenium and Chromedriver (default=True).
  # -use_wiki USE_WIKI, --use_wiki USE_WIKI
  #                       Gather all data for each country from its official wiki page (default=True).
  # -save_each_iteration SAVE_EACH_ITERATION --save_each_iteration SAVE_EACH_ITERATION
  #                       After each iteration of country updates data export to JSON/CSV rather than just once at the
  #                       end after each country's data processed. This is useful in the case where the Selenium instance
  #                       might timeout and export progress would be lost.
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
from iso3166_updates_export import *
```

**Get all listed ISO 3166 changes/updates for BA, DE, FR, HU, PY, export only JSON of updates to export folder "iso3166-updates", print progress using verbose flag:**
```python
get_iso3166_updates(alpha_codes="BA,DE,FR,HU,PY", export_folder="iso3166-updates", export_json=1, export_csv=0, verbose=1)
#exported files: /iso3166-updates/iso3166-updates_BA,DE,FR,HU,PY.json
```

**Get any listed ISO 3166 changes/updates for HU, IT, JA, KE, in the years 2018 and 2022, export only to JSON with filename "iso3166-updates.json" and split updates into separate JSON files (concat_updates=False):**
```python
get_iso3166_updates(alpha_codes="HU, IT, JA, KE", year="2018,2022", export_json=1, export_csv=0, export_xml=0, export_filename="iso3166-updates", concat_updates=0)
#exported files: /iso3166-updates/iso3166-updates_HU,IT,JA,KE_2018,2022.json
```

**Get any listed ISO 3166 changes/updates for Ireland, between years 2012 and 2021, use default parameters (export to json and XML not csv):**
```python
get_iso3166_updates(alpha_codes="IE", year="2012-2021", export_xml=1)
#exported files: /iso3166-updates/iso3166-updates_IE_2012-2021.json
```

**Get any listed ISO 3166 changes/updates for Tanzania, with updates with year >= 2015, export only to CSV and XML with filename "iso3166-output":**
```python
get_iso3166_updates(alpha_codes="TA", year=">2015", export_filename="iso3166-output", export_json=0, export_csv=1, export_xml=1)
#exported files: /iso3166-updates/iso3166-output_TA_>2015.csv
```

**Get any listed ISO 3166 changes/updates for Yemen, with updates that have year not equal to 2008, use default parameters (export to json but not csv):**
```python
get_iso3166_updates(alpha_codes="YE", year="<>2008")
#exported files: /iso3166-updates/iso3166-output_YE_<>2008.json
``` 

The output files from the <i>get_iso3166_updates.py</i> script for the updates/changes to an ISO 3166-2 country returns 4 columns: 
**Change, Description of Change, Date Issued** and **Source.** For the CSV export, if more than one country input, then an additional primary key column **Country Code** will be prepended to the first column, which will be the 2 letter ISO 3166-1 country code. 

* Change: overall summary of change/update made.
* Description of Change: more in-depth info about the change/update that was made, including any remarks listed on the official ISO page.
* Date Issued: date that the change was communicated/published.
* Source: name and or edition of newsletter that the ISO 3166 change/update was communicated in (pre 2013), or the link to the country's ISO Online Browsing Platform (OBP) page.

E.g. The output format of the exported **CSV** for AD (Andorra) is:

| Change | Description of Change | Date Issued | Source |   
|:-------------------|:------------|------------------------------------:|------------------------:|
| Subdivisions added: 7 parishes.   | Addition of the administrative subdivisions and of their code elements. | 2007-04-17 | Newsletter I-8 - https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf. | 
| Update List Source. |  | 2014-11-03 | Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD. | 
| Update List Source. |  | 2015-11-27 | Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD. | 

E.g. The output format of the exported **JSON** for AD (Andorra) is:
```javascript
{
  "AD": [
      {
          "Change": "Update List Source.",
          "Description of Change": "",
          "Date Issued": "2015-11-27",
          "Source": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD)."
      },
      {
          "Change": "Update List Source.",
          "Description of Change": "",
          "Date Issued": "2014-11-03",
          "Source": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD)."
      },
      {
          "Change": "Subdivisions added: 7 parishes.",
          "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
          "Date Issued": "2007-04-17",
          "Source": "Newsletter I-8 - https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf."

      }
  ]
}

E.g. The output format of the exported **XML** for AD (Andorra) is:

```xml
<?xml version="1.0" ?>
<ISO3166Updates>
  <Country code="AD">
    <Update>
      <Change>Update List Source.</Change>
      <Description_of_Change/>
      <Date_Issued>2015-11-27</Date_Issued>
      <Source>Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD.</Source>
    </Update>
    <Update>
      <Change>Update List Source.</Change>
      <Description_of_Change/>
      <Date_Issued>2014-11-03</Date_Issued>
      <Source>Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD.</Source>
    </Update>
    <Update>
      <Change>Subdivisions added: 7 parishes.</Change>
      <Description_of_Change>Addition of the administrative subdivisions and of their code elements.</Description_of_Change>
      <Date_Issued>2007-04-17</Date_Issued>
      <Source>Newsletter I-8 - https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf.</Source>
    </Update>
  </Country>
</ISO3166Updates>
```
```
-->

Directories 
-----------
* `/iso3166_updates` - source code for `iso3166-updates` Python package.
* `/iso3166-check-for-updates` - all code and files related to the serverless Google Cloud Run microservice for the check-for-updates function which is a periodically called Cloud Run app that uses the Python software to check for the latest updates for all ISO 3166 countries, ensuring the API and jsons are reliable, accurate and up-to-date.
* `/docs` - documentation for `iso3166-updates`, available on [readthedocs](https://iso3166-updates.readthedocs.io/en/latest/).
* `/tests` - unit and integration tests for `iso3166-updates` software and API.
* `/iso3166_updates_export` - directory of scripts that pull and export all the latest ISO 3166 data from the various data sources.
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
* [iso3166-2](https://github.com/amckenna41/iso3166-2): a lightweight bespoke custom-built Python package and dataset, and accompanying API, that can be used to access all of the world's ISO 3166-2 subdivision data. A plethora of data attributes are available per country and subdivision including: name, local name, code, parent code, type, lat/longitude and flag. Currently, the package and API supports data from 250 countries/territories, according to the ISO 3166-1 standard and >5000 subdivisions, according to the ISO 3166-2 standard.
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
[<img src="https://img.shields.io/github/stars/amckenna41/iso3166-updates?color=green&label=star%20it%20on%20GitHub" width="132" height="20" alt="Star it on GitHub">](https://github.com/amckenna41/iso3166-updates) <br><br>
<a href="https://www.buymeacoffee.com/amckenna41" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

[Back to top](#TOP)

[demo_iso3166_updates]: https://colab.research.google.com/drive/1oGF3j3_9b_g2qAmBtv3n-xO2GzTYRJjf?usp=sharing
[demo_get_all_iso3166_updates]: https://colab.research.google.com/drive/161aclDjGkWQJhis7KxBO1e6H_ghQOPRG?usp=sharing
[api]: https://iso3166-updates.vercel.app/api
[medium]: https://medium.com/@ajmckenna69/iso3166-updates-d06b817af3a7
[python]: https://www.python.org/downloads/release/python-360/
[iso3166-updates]: https://github.com/amckenna41/iso3166-updates
[python-dateutil]: https://pypi.org/project/python-dateutil/
[thefuzz]: https://pypi.org/project/thefuzz/
[fake_useragent]: https://pypi.org/project/fake-useragent/
[pandas]: https://pandas.pydata.org/
[tqdm]: https://github.com/tqdm/tqdm
[requests]: https://requests.readthedocs.io/
[beautifulsoup4]: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
[google-auth]: https://cloud.google.com/python/docs/reference
[google-cloud-storage]: https://cloud.google.com/python/docs/reference
[google-api-python-client]: https://cloud.google.com/python/docs/reference
[emoji-country-flag]: https://pypi.org/project/emoji-country-flag/
[gunicorn]: https://pypi.org/project/gunicorn/
[selenium]: https://selenium-python.readthedocs.io/index.html
[webdriver-manager]: https://pypi.org/project/webdriver-manager/
[lxml]: https://lxml.de/
[updates_md]: https://github.com/amckenna41/iso3166-updates/blob/main/UPDATES.md
[iso3166]: https://github.com/deactivated/python-iso3166
[PyPi]: https://pypi.org/project/iso3166-updates/
[Issues]: https://github.com/amckenna41/iso3166-updates/issues