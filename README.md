# Automated scripts for receiving updates to ISO3166 country codes

[![iso3166_updates](https://img.shields.io/pypi/v/iso3166-updates)](https://pypi.org/project/iso3166-updates/)
[![Build](https://img.shields.io/github/workflow/status/amckenna41/iso3166-updates/Deploy%20and%20Testing)](https://github.com/amckenna41/iso3166-updates/actions)
[![Platforms](https://img.shields.io/badge/platforms-linux%2C%20macOS%2C%20Windows-green)](https://pypi.org/project/iso3166-updates/)
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT)
[![Issues](https://img.shields.io/github/issues/amckenna41/iso3166-flag-icons)](https://github.com/amckenna41/iso3166-updates/issues)
[![Size](https://img.shields.io/github/repo-size/amckenna41/iso3166-updates)](https://github.com/amckenna41/iso3166-updates)
[![Commits](https://img.shields.io/github/commit-activity/w/amckenna41/iso3166-updates)](https://github.com/iso3166-updates)

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/e/e3/ISO_Logo_%28Red_square%29.svg" alt="iso" height="200" width="400"/>
</p>

> Automated scripts that check for any updates/changes to the ISO3166-1 and ISO3166-2 country codes and naming conventions, as per the ISO3166 newsletter (https://www.iso.org/iso-3166-country-codes.html).

Table of Contents
-----------------

  * [Introduction](#introduction)
  * [Usage](#usage)
  * [Requirements](#requirements)
  * [Installation](#installation)
  * [Issues](#Issues)
  * [Contact](#contact)
  * [License](#license)
  * [References](#references)


Introduction
------------
iso3166-updates is a repo that consists of a series of scripts that check for any updates/changes to the ISO3166-1 and ISO3166-2 country codes and naming conventions, as per the ISO3166 newsletter (https://www.iso.org/iso-3166-country-codes.html). The ISO3166 standard by the ISO defines codes for the names of countries, dependent territories, special areas of geographical interest, and their principal subdivisions [1]. 

The <b>ISO 3166-1</b> icons are those of the names of countries and their subdivisions that can be broken into three sets of country codes:
* ISO 3166-1 alpha-2 – two-letter country codes which are the most widely used of the three, and used most prominently for the Internet's country code top-level domains (with a few exceptions).
* ISO 3166-1 alpha-3 – three-letter country codes which allow a better visual association between the codes and the country names than the alpha-2 codes.
* ISO 3166-1 numeric – three-digit country codes which are identical to those developed and maintained by the United Nations Statistics Division, with the advantage of script (writing system) independence, and hence useful for people or systems using non-Latin scripts.

The <b>ISO 3166-2</b> icons are those of the names of countries and their subdivisions – Part 2: Country subdivision code, defines codes for the names of the principal subdivisions (e.g., provinces, states, departments, regions) of all countries coded in ISO 3166-1 [[2]](#references). <br>

Problem Statement
-----------------

API
---
> In Development
An API is available that can be used to extract any applicable updates for a country via URL. The API is in alpha stage so is just available via a Google Function at URL: https://

The API documentation is with all useful commands and inputs to the API is available on the README of the iso3166-updates-api folder.  

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
python3 setup.py install
cd iso3166_updates
```

Usage 
-----

```python
import iso3166_updates as iso3166_updates

#get all listed changes/updated for Andorra from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:AD)
iso3166_updates.get_updates("AD")

#get all listed changes/updated for BA, DE, FR, HU, PY
iso3166_updates.get_updates(["BA","DE","FR","HU","PY"])

#get any listed changes/updated for Ireland from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:IE),
#between years of 2012 and 2021
iso3166_updates.get_updates("IE", year="2012-2021")
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
\[1\]: https://en.wikipedia.org/wiki/ISO_3166 <br>
\[2\]: https://en.wikipedia.org/wiki/ISO_3166-2 <br>
\[3\]: https://github.com/lipis/flag-icons <br>


[Back to top](#TOP)

[python]: https://www.python.org/downloads/release/python-360/
[pandas]: https://pandas.pydata.org/
[requests]: https://requests.readthedocs.io/
[beautifulsoup4]: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
[iso3166]: https://github.com/deactivated/python-iso3166
