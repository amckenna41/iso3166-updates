# iso3166-updates

[![iso3166_updates](https://img.shields.io/pypi/v/iso3166-updates)](https://pypi.org/project/iso3166-updates/)
[![pytest](https://github.com/amckenna41/iso3166-updates/workflows/Building%20and%20Testing/badge.svg)](https://github.com/amckenna41/iso3166-updates/actions?query=workflowBuilding%20and%20Testing)
[![Platforms](https://img.shields.io/badge/platforms-linux%2C%20macOS%2C%20Windows-green)](https://pypi.org/project/iso3166-updates/)
[![License: MIT](https://img.shields.io/github/license/amckenna41/iso3166-updates)](https://opensource.org/licenses/MIT)
<!-- [![CircleCI](https://circleci.com/gh/amckenna41/iso3166-updates.svg?style=svg&circle-token=d860bb64668be19d44f106841b80eb47a8b7e7e8)](https://app.circleci.com/pipelines/github/amckenna41/iso3166-updates) -->
[![Issues](https://img.shields.io/github/issues/amckenna41/iso3166-updates)](https://github.com/amckenna41/iso3166-updates/issues)
[![Size](https://img.shields.io/github/repo-size/amckenna41/iso3166-updates)](https://github.com/amckenna41/iso3166-updates)
[![Commits](https://img.shields.io/github/commit-activity/w/amckenna41/iso3166-updates)](https://github.com/iso3166-updates)

<div alt="images" style="justify-content: center; display:flex; margin-left=50px;">
  <img src="https://upload.wikimedia.org/wikipedia/commons/3/3d/Flag-map_of_the_world_%282017%29.png" alt="globe" height="200" width="500"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/e/e3/ISO_Logo_%28Red_square%29.svg" alt="iso" height="200" width="300"/>
</div>

> Automated scripts that check for any updates/changes to the ISO 3166-1 and ISO 3166-2 country codes and naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui). Available via a Python software package and API; a demo of both is available [here][demo].

Table of Contents
-----------------
  * [Introduction](#introduction)
  * [Requirements](#requirements)
  * [Installation](#installation)
  * [Usage](#usage)
  * [Directories](#Directories)
  * [Issues](#Issues)
  * [Contact](#contact)
  * [References](#references)

Introduction
------------
`iso3166-updates` is a repo that consists of a series of scripts that check for any updates/changes to the ISO 3166-2 country codes and subdivision naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html). The ISO 3166 standard by the ISO defines codes for the names of countries, dependent territories, special areas of geographical interest, consolidated into the ISO 3166-1 standard [[1]](#references), and their principal subdivisions (e.g., provinces, states, departments, regions), which comprise the ISO 3166-2 standard [[2]](#references). 

The ISO 3166-1 was first published in 1974 and currently comprises 249 countries, 193 of which are sovereign states that are members of the United Nations [[1]](#references). The ISO 3166-2 was first published in 1998 and as of 29 November 2022 there are 5,043 codes defined in it [[2]](#references).

## Problem Statement:

The ISO is a very dynamic organisation and regularly change/update/remove entries within its library of standards, including the ISO 3166. Additions/changes/deletions to country/territorial codes occur less often in the ISO 3166-1, but changes are more frequent for the ISO 3166-2 codes due to there being thousands more entries, thus it can be difficult to keep up with any changes to these codes. These changes can occur for a variety of geopolitical and bureaucratic reasons and are usually communicated via Newsletters on the ISO platform, their Online Browsing Platform (OBP) or via a database, which usually costs money to subscribe to [[3]](#references). Usually these updates are conveyed at the end of the year, with amendments and updates sometimes being published at various times throughout the year [[4]](#references). 

This software and accompanying API makes it extremely easy to check for any new or historic updates to a country or set of country's ISO 3166-2 codes for free, with an easy-to-use interface and Python package and API, ensuring that you get the most up-to-date and accurate ISO 3166-2 codes and naming conventions.

## Intended Audience:

This software and accompanying API is for anyone working with country data at the ISO 3166 level. It's of high importance that the data that you are working with is correct and up-to-date, especially with consistent changes being posted every year since 2000 (except 2001 and 2006). Also, it's aimed not just at developers of ISO 3166 applications but for anyone working in that space, hence the creation of an easy-to-use API. 

<strong> The earliest date for any ISO 3166 updates is 2000-06-21, and the most recent is 2022-11-29. </strong>

Updates
-------
**Last Updated:**

The list of ISO 3166-2 updates was last updated on <strong>Nov 2022</strong>. 
The object storing all updates both locally (iso3166-updates.json) and on the API are consistenly checked for the latest updates using a Cloud Function ([iso3166-check-for-updates](https://github.com/amckenna41/iso3166-updates/tree/main/iso3166-check-for-updates)). The function uses the `iso3166-updates` Python software to pull all the latest updates/changes from all ISO3166-2 wiki's to check for the latest updates within a certain period e.g the past 3 months. The function compares the generated output with that of the updates json currently in the Google Cloud Storage bucket and will replace this json to integrate the latest updates found such that the main GCP Cloud Function returns the latest data. Additionally, a GitHub Issue in the `iso3166-2` repository will be automatically created that outlines all updates/changes that need to be implemented into the `iso3166-2` JSONs and repo.
Ultimately, this function ensures that the software and assoicated APIs are up-to-date with the latest ISO3166-2 information for all countries/territories/subdivisions etc.

API
---
An API is available that can be used to extract any applicable updates for a country via a URL. The API is available at the URL:

> https://www.iso3166-updates.com/api

Two query string parameters/paths are available in the API. The 2 letter alpha2 country code can be appeneded to the url as a query string parameter - "?alpha2=JP" - or appended to the base url - "/alpha2/YE". A single alpha2 or list of them can be passed to the API (e.g "FR", "DE", "GY", "HU", "ID"). The year parameter can be a specific year, year range, or a cut-off year to get updates less than/more than a year (e.g "2017", "2010-2015", "<2009", ">2002"). The API is hosted and built using GCP, with a Cloud Function being used in the backend which is fronted by an api gateway and load balancer. The function calls a GCP Storage bucket to access the back-end JSON with all ISO 3166 updates. A complete diagram of the architecture is shown below.

The API documentation and usage with all useful commands and examples to the API is available on the [README](https://github.com/amckenna41/iso3166-updates/blob/main/iso3166-updates-api/README.md) of the iso3166-updates-api folder. 

 <!-- "?year" can be a specific year or year range to get updates for (e.g "2017", "2010-2015"), you can also get updates less than or greater than a year (e.g ">2004", "<2020") and "?months" which allows you to get the updates of the past X months. If months and year input params are set then months will take precedence. -->
<p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166-updates-api/gcp_arch.png" alt="gcp_arch" height="200" width="400"/>
</p>

Requirements
------------
* [python][python] >= 3.7
* [pandas][pandas] >= 1.4.3
* [numpy][numpy] >= 1.23.2
* [requests][requests] >= 2.28.1
* [beautifulsoup4][beautifulsoup4] >= 4.11.1
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

Usage
-----
**Import package:**
```python
import iso3166_updates as iso3166_updates
```

**Input parameters to get_updates function:**
```python
  # -alpha2 ALPHA2, --alpha2 ALPHA2
  #                       Alpha2 code/s of ISO3166 countries to check for updates.
  # -export_filename EXPORT_FILENAME, --export_filename EXPORT_FILENAME
  #                       Filename for exported ISO3166 updates csv file.
  # -export_json_filename EXPORT_JSON_FILENAME, --export_json_filename EXPORT_JSON_FILENAME
  #                       Filename for exported ISO3166 updates json file.
  # -export_folder EXPORT_FOLDER, --export_folder EXPORT_FOLDER
  #                       Folder where to store exported ISO files.
  # -export_json, --export_json
  #                       Whether to export all found updates to json.
  # -export_csv, --export_csv
  #                       Whether to export all found updates to csv files in export folder.
  # -year YEAR, --year YEAR
  #                       Selected year to check for updates.
  # -concat_updates, --concat_updates
  #                       Whether to concatenate updates of individual countrys into the same json file or seperate.
```

**Get all listed changes/updates for all countries which happens by default if no alpha2 codes specified in input param, export csv and json to folder "iso3166-updates":**
```python
iso3166_updates.get_updates(export_folder="iso3166-updates", export_json=1, export_csv=1)
```

**Get all listed changes/updates for Andorra from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:AD), export csv and json to folder "iso3166-updates":**
```python
iso3166_updates.get_updates("AD", export_folder="iso3166-updates", export_json=1, export_csv=1)
```

**Get all listed changes/updates for BA, DE, FR, HU, PY, export only JSON of updates to export folder "iso3166-updates":**
```python
iso3166_updates.get_updates(["BA","DE","FR","HU","PY"], export_folder="iso3166-updates", export_json=1, export_csv=0))
```

**Get any listed changes/updates for HU, IT, JA, KE from wiki, in the year 2018, export only to JSON with filename "iso3166-updates.json" and seperate updates into sepetate JSON files:**
```python
iso3166_updates.get_updates("HU, IT, JA, KE", year="2018", export_json=1, export_csv=0, export_json_filename="iso3166-updates", concat_updates=0)
```

**Get any listed changes/updates for Ireland from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:IE), between years of 2012 and 2021, use default parameters:**
```python
iso3166_updates.get_updates("IE", year="2012-2021")
```

**Get any listed changes/updates for Tanzania from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:TZ), with updates years >=2015, export only to CSV with filename "iso3166-output.csv":**
```python
iso3166_updates.get_updates("TA", year=">2015", export_filename="iso3166-output.csv")
```

**Get any listed changes/updates for Yemen from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:YE), with updates years < 2010, use default parameters:**
```python
iso3166_updates.get_updates("YE", year="<2010")
```

The output to the above functions for the updates/changes to a ISO 3166-2 country returns 4 columns: 
Edition/Newsletter, Date Issued, Description of change in newsletter and Code/Subdivision change. 

* Edition/Newsletter: Name and or edition of newsletter that ISO 3166-2 change/update was communicated in.
* Date Issued: Date that the change was communicated.
* Description of change in newsletter: More in-depth info about the change/update that was made.
* Code/Subdivision change: Overall summary of change/update made.

E.g. The output format of the exported CSV for AD (Andorra) is:

| Edition/Newsletter | Date Issued | Description of change in newsletter | Code/Subdivision change |   
|:-------------------|:------------|------------------------------------:|------------------------:|
| Newsletter I-8     | 2007-04-17  | Addition of the administrative subdivisions...   | Subdivisions added: 7 parishes...                 | 
| Online Browsing Platform (OBP) | 2014-11-03 | Update List Source | No subdivision changes listed |
| Online Browsing Platform (OBP) | 2015-11-27 | Update List Source | No subdivision changes listed | 

E.g. The output format of the exported JSON for AD (Andorra) is:
```javascript
{
  AD: [
      {
        "Code/Subdivision change": "",
        "Date Issued": "2015-11-27",
        "Description of change in newsletter": "Update List Source",
        "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD)"
      },
      {
        "Code/Subdivision change": "",
        "Date Issued": "2014-11-03",
        "Description of change in newsletter": "Update List Source",
        "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD)"
      },
      {
        "Code/Subdivision change:" "Subdivisions added:7 parishes",
        "Date Issued": "2007-04-17",
        "Description of change in newsletter": "Addition of the administrative subdivisions and of their code elements",
        "Edition/Newsletter": "Newsletter I-8 (https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)"
      }
  ]
}
```

Directories
-----------
* `/docs` - documentation for `iso3166-updates` Python package.
* `/iso3166_updates` - source code for `iso3166-updates` Python package.
* `/iso3166-updates-api` - all code and files related to the serverless Google Cloud Function for the `iso3166-updates` API, including the main.py, requirements.txt and API config file.
* `/iso3166-check-for-updates` - all code and files related to the serverless Google Cloud Function for the check-for-updates function which is a periodically called Cloud Func that uses the Python software to check for the latest updates for all country's, ensuring the API and jsons are reliable and up-to-date. Includes the main.py and requirements.txt.
* `/tests` - unit and integration tests for `iso3166-updates`.

Issues
------
Any issues, errors or bugs can be raised via the [Issues](Issues) tab in the repository. Also if there are any missing or incorrect data in the updates json, this should also be raised by creating an issue. 

Contact
-------
If you have any questions or comments, please contact amckenna41@qub.ac.uk or raise an issue on the [Issues][Issues] tab. <br><br>
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/adam-mckenna-7a5b22151/)

References
----------
\[1\]: ISO3166-1: https://en.wikipedia.org/wiki/ISO_3166-1 <br>
\[2\]: ISO3166-2: https://en.wikipedia.org/wiki/ISO_3166-2 <br>
\[3\]: ISO Country Codes Collection: https://www.iso.org/publication/PUB500001 <br>
\[4\]: ISO Country Codes: https://www.iso.org/iso-3166-country-codes.html <br>
\[5\]: ISO3166-1 flag-icons repo: https://github.com/lipis/flag-icons <br>

Support
-------
<a href="https://www.buymeacoffee.com/amckenna41" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

[Back to top](#TOP)

[demo]: https://colab.research.google.com/drive/1oGF3j3_9b_g2qAmBtv3n-xO2GzTYRJjf?usp=sharing
[python]: https://www.python.org/downloads/release/python-360/
[pandas]: https://pandas.pydata.org/
[numpy]: https://numpy.org/
[requests]: https://requests.readthedocs.io/
[beautifulsoup4]: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
[iso3166]: https://github.com/deactivated/python-iso3166
[PyPi]: https://pypi.org/project/iso3166-updates/
[Issues]: https://github.com/amckenna41/iso3166-updates/issues