# iso3166-updates

[![iso3166_updates](https://img.shields.io/pypi/v/iso3166-updates)](https://pypi.org/project/iso3166-updates/)
[![Build](https://img.shields.io/github/workflow/status/amckenna41/iso3166-updates/Deploy%20to%20PyPI%20📦)](https://github.com/amckenna41/iso3166-updates/actions)
[![Platforms](https://img.shields.io/badge/platforms-linux%2C%20macOS%2C%20Windows-green)](https://pypi.org/project/iso3166-updates/)
[![License: MIT](https://img.shields.io/github/license/amckenna41/iso3166-updates)](https://opensource.org/licenses/MIT)
[![Issues](https://img.shields.io/github/issues/amckenna41/iso3166-flag-icons)](https://github.com/amckenna41/iso3166-updates/issues)
[![Size](https://img.shields.io/github/repo-size/amckenna41/iso3166-updates)](https://github.com/amckenna41/iso3166-updates)
[![Commits](https://img.shields.io/github/commit-activity/w/amckenna41/iso3166-updates)](https://github.com/iso3166-updates)

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/e/e3/ISO_Logo_%28Red_square%29.svg" alt="iso" height="200" width="400"/>
</p>

> Automated scripts that check for any updates/changes to the ISO3166-1 and ISO3166-2 country codes and naming conventions, as per the ISO3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui). Available via a Python software package and API; a demo of both is available [here](https://colab.research.google.com/drive/1oGF3j3_9b_g2qAmBtv3n-xO2GzTYRJjf?usp=sharing).

Table of Contents
-----------------

  * [Introduction](#introduction)
  * [Requirements](#requirements)
  * [Installation](#installation)
  * [Usage](#usage)
  * [Issues](#Issues)
  * [Contact](#contact)
  * [References](#references)

Introduction
------------
iso3166-updates is a repo that consists of a series of scripts that check for any updates/changes to the ISO3166-1 and ISO3166-2 country codes and naming conventions, as per the ISO3166 newsletter (https://www.iso.org/iso-3166-country-codes.html). The ISO3166 standard by the ISO defines codes for the names of countries, dependent territories, special areas of geographical interest, consolidated into the ISO3166-1 standard [[1]](#references), and their principal subdivisions (e.g., provinces, states, departments, regions), which compromise the ISO3166-2 standard [[2]](#references). 

**Problem Statement**

The ISO is a very dynamic organisation and regularly change/update/remove entries within its library of standards, this includes the ISO3166. Additions/changes/deletions to country/territorial codes in the ISO3166-1 are a lot less frequent than for the ISO3166-2 codes due to there being thousands more entries, thus it can be difficult to keep up with any changes to these codes. These changes are usually communicated via Newsletters on the ISO platform or Online Browsing Platform or via a database which usually costs money to subscribe to [[3]](#references).
This software and accompanying API makes it extremely easy to check for any new or historic updates to a country or set of countrys' ISO3166-2 codes for free with an easy to use interface and Python package.
This software is for anyone working on projects working directly with country codes and who want up-to-date and accurate ISO3166-2 codes and naming conventions.

API
---
An API is available that can be used to extract any applicable updates for a country via a URL. The API is in alpha stage so is just available via a Google Function at URL: 

> https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates

The API documentation and usage with all useful commands and inputs to the API is available on the [README](https://github.com/amckenna41/iso3166-updates/blob/main/iso3166-updates-api/README.md) of the iso3166-updates-api folder. The API was built using GCP utilsing a Cloud Function backed by an API Gateway that can be called via a http trigger at the above url, the Function calls GCP Storage to access the back-end JSON with all ISO3166 updates. This JSON is updated regularly using a CRON job that is called every X months. 

Requirements
------------
* [python][python] >= 3.7
* [pandas][pandas] >= 1.4.3
* [requests][requests] >= 2.28.1
* [beautifulsoup4][beautifulsoup4] >= 4.11.1
* [iso3166][iso3166] >= 2.1.1

Installation
------------
Install the latest version of iso3166-updates using pip:

```bash
pip3 install iso3166-updates
```

Installation from source:
```bash
git clone -b master https://github.com/amckenna41/iso3166-updates.git
cd iso3166_updates
python3 setup.py install
```

Usage
-----
Import package
```python
import iso3166_updates as iso3166_updates
```

Get all listed changes/updates for Andorra from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:AD)
```python
iso3166_updates.get_updates("AD")
```

Get all listed changes/updates for BA, DE, FR, HU, PY
```python
iso3166_updates.get_updates(["BA","DE","FR","HU","PY"])
```

Get any listed changes/updates for HU, IT, JA, KE from wiki, in the year 2018
```python
iso3166_updates.get_updates("HU, IT, JA, KE", year="2018")
```

Get any listed changes/updates for Ireland from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:IE), between years of 2012 and 2021
```python
iso3166_updates.get_updates("IE", year="2012-2021")
```

Get any listed changes/updates for Tanzania from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:TZ), with updates years > 2015 
```python
iso3166_updates.get_updates("TA", year=">2015")
```

Get any listed changes/updates for Yemen from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:YE), with updates years < 2010
```python
iso3166_updates.get_updates("YE", year=">2010")
```

The output to the above functions for the updates/changes to a ISO3166-2 country returns 4 columns: 
Edition/Newsletter, Date Issued, Description of change in newsletter and Code/Subdivision change. 
E.g the output csv format for AD (Andorra) is:

| Edition/Newsletter | Date Issued | Description of change in newsletter | Code/Subdivision change |   
|:-------------------|:------------|------------------------------------:|------------------------:|
| Newsletter I-8     | 2007-04-17  | Addition of the administrative subdivisions...   | Subdivisions added: 7 parishes...                 | 
| Online Browsing Platform (OBP) | 2014-11-03 | Update List Source | No subdivision changes listed |
| Online Browsing Platform (OBP) | 2015-11-27 | Update List Source | No subdivision changes listed | 

Issues
------
Any issues, errors or bugs can be raised via the [Issues](https://github.com/amckenna41/iso3166_updates/issues) tab in the repository.

Contact
-------
If you have any questions or comments, please contact amckenna41@qub.ac.uk or raise an issue on the [Issues][Issues] tab. <br><br>
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/adam-mckenna-7a5b22151/)

References
----------
\[1\]: https://en.wikipedia.org/wiki/ISO_3166-1 <br>
\[2\]: https://en.wikipedia.org/wiki/ISO_3166-2 <br>
\[3\]: ISO Country Codes Collection: https://www.iso.org/publication/PUB500001 <br>
\[4\]: https://github.com/lipis/flag-icons <br>

Support
-------
<a href="https://www.buymeacoffee.com/amckenna41" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

[Back to top](#TOP)

[python]: https://www.python.org/downloads/release/python-360/
[pandas]: https://pandas.pydata.org/
[requests]: https://requests.readthedocs.io/
[beautifulsoup4]: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
[iso3166]: https://github.com/deactivated/python-iso3166
