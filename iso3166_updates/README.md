# iso3166-updates

[![iso3166_updates](https://img.shields.io/pypi/v/iso3166-updates)](https://pypi.org/project/iso3166-updates/)
[![Platforms](https://img.shields.io/badge/platforms-linux%2C%20macOS%2C%20Windows-green)](https://pypi.org/project/iso3166-updates/)
[![PythonV](https://img.shields.io/pypi/pyversions/iso3166-updates?logo=2)](https://pypi.org/project/iso3166-updates/)
[![License: MIT](https://img.shields.io/github/license/amckenna41/iso3166-updates)](https://opensource.org/licenses/MIT)

Usage
-----
## Import package
```python
import iso3166_updates as iso3166_updates
```

## Get all listed changes/updates for Andorra from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:AD)
```python
iso3166_updates.get_updates("AD")
```

## Get all listed changes/updates for BA, DE, FR, HU, PY
```python
iso3166_updates.get_updates(["BA","DE","FR","HU","PY"])
```

## Get any listed changes/updates for HU, IT, JA, KE from wiki, in the year 2018
```python
iso3166_updates.get_updates("HU, IT, JA, KE", year="2018")
```

## Get any listed changes/updates for Ireland from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:IE), between years of 2012 and 2021
```python
iso3166_updates.get_updates("IE", year="2012-2021")
```

## Get any listed changes/updates for Tanzania from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:TZ), with updates years > 2015 
```python
iso3166_updates.get_updates("TA", year=">2015")
```

## Get any listed changes/updates for Yemen from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:YE), with updates years < 2010
```python
iso3166_updates.get_updates("YE", year=">2010")
```