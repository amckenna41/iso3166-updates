# iso3166-updates

[![iso3166_updates](https://img.shields.io/pypi/v/iso3166-updates)](https://pypi.org/project/iso3166-updates/)
[![pytest](https://github.com/amckenna41/iso3166-updates/workflows/Building%20and%20Testing/badge.svg)](https://github.com/amckenna41/iso3166-updates/actions?query=workflowBuilding%20and%20Testing)
[![CircleCI](https://dl.circleci.com/status-badge/img/gh/amckenna41/iso3166-updates/tree/main.svg?style=svg&circle-token=9b0c0a9f6cc032f255dc28842c95600401aa4426)](https://dl.circleci.com/status-badge/redirect/gh/amckenna41/iso3166-updates/tree/main)
[![PythonV](https://img.shields.io/pypi/pyversions/iso3166-updates?logo=2)](https://pypi.org/project/iso3166-updates/)
[![Platforms](https://img.shields.io/badge/platforms-linux%2C%20macOS%2C%20Windows-green)](https://pypi.org/project/iso3166-updates/)
[![License: MIT](https://img.shields.io/github/license/amckenna41/iso3166-updates)](https://opensource.org/licenses/MIT)

Usage
-----
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

**Get all listed ISO 3166 changes/updates for BA, DE, FRA, HUN, PY (600):**
```python
iso["BA","DE","FRA","HUN","600"]
```

**Get all listed ISO 3166 changes/updates for all countries, for years 2002, 2003 and 2004:**
```python
iso.year("2002, 2003, 2004")
```

**Get all listed ISO 3166 changes/updates for all countries, for year range 2013-2016:**
```python
iso.year("2013-2016")
```

**Get all listed ISO 3166 changes/updates for all countries, for all years after 2017 inclusive:**
```python
iso.year(">2017")
```

**Get all listed ISO 3166 changes/updates for all countries, for all years before 2010:**
```python
iso.year("<2010")
```

**Get all listed ISO 3166 changes/updates published from the past 12 months:**
```python
iso.months("12")
```

**Get all listed ISO 3166 changes/updates published from the past 36-48 months:**
```python
iso.months("36-48")
```

The output to the above functions for the updates/changes to an ISO 3166 country returns 4 attributes: 

* Edition/Newsletter: name and or edition of newsletter that the ISO 3166 change/update was communicated in (pre 2013), or the link to the country's ISO Online Browsing Platform page.
* Date Issued: date that the change was communicated.
* Code/Subdivision change: overall summary of change/update made.
* Description of Change: more in-depth info about the change/update that was made, including any remarks listed on the official ISO page.