# iso3166-updates

[![iso3166_updates](https://img.shields.io/pypi/v/iso3166-updates)](https://pypi.org/project/iso3166-updates/)
[![pytest](https://github.com/amckenna41/iso3166-updates/workflows/Building%20and%20Testing/badge.svg)](https://github.com/amckenna41/iso3166-updates/actions?query=workflowBuilding%20and%20Testing)
[![CircleCI](https://dl.circleci.com/status-badge/img/gh/amckenna41/iso3166-updates/tree/main.svg?style=svg&circle-token=9b0c0a9f6cc032f255dc28842c95600401aa4426)](https://dl.circleci.com/status-badge/redirect/gh/amckenna41/iso3166-updates/tree/main)
[![PythonV](https://img.shields.io/pypi/pyversions/iso3166-updates?logo=2)](https://pypi.org/project/iso3166-updates/)
[![Platforms](https://img.shields.io/badge/platforms-linux%2C%20macOS%2C%20Windows-green)](https://pypi.org/project/iso3166-updates/)
[![License: MIT](https://img.shields.io/github/license/amckenna41/iso3166-updates)](https://opensource.org/licenses/MIT)

Requirements
------------
* [python][python] >= 3.9
* [iso3166][iso3166] >= 2.1.1 
* [python-dateutil][python-dateutil] >= 2.9.0
* [thefuzz][thefuzz] >= 0.22.1
* [requests][requests] >= 2.28.1

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

**Get any listed ISO 3166 changes/updates published from the date range 2021-10-02, inclusive:**
```python
iso.date_range("2021-10-02")
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

The output to the above functions for the updates/changes to an ISO 3166 country returns 4 attributes: 

* Change: overall summary of change/update made.
* Description of Change: more in-depth info about the change/update that was made, including any remarks listed on the official ISO page.
* Date Issued: date that the change was communicated.
* Source: name and or edition of newsletter that the ISO 3166 change/update was communicated in (pre 2013), or the link to the country's ISO Online Browsing Platform page.

[python]: https://www.python.org/downloads/release/python-360/
[iso3166]: https://github.com/deactivated/python-iso3166
[python-dateutil]: https://pypi.org/project/python-dateutil/
[requests]: https://requests.readthedocs.io/
[thefuzz]: https://pypi.org/project/thefuzz/