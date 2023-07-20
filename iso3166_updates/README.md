# iso3166-updates

[![iso3166_updates](https://img.shields.io/pypi/v/iso3166-updates)](https://pypi.org/project/iso3166-updates/)
[![pytest](https://github.com/amckenna41/iso3166-updates/workflows/Building%20and%20Testing/badge.svg)](https://github.com/amckenna41/iso3166-updates/actions?query=workflowBuilding%20and%20Testing)
<!-- [![codecov](https://codecov.io/gh/amckenna41/pySAR/branch/master/graph/badge.svg?token=4PQDVGKGYN)](https://codecov.io/gh/amckenna41/pySAR) -->
[![Platforms](https://img.shields.io/badge/platforms-linux%2C%20macOS%2C%20Windows-green)](https://pypi.org/project/iso3166-updates/)
[![PythonV](https://img.shields.io/pypi/pyversions/iso3166-updates?logo=2)](https://pypi.org/project/iso3166-updates/)
[![License: MIT](https://img.shields.io/github/license/amckenna41/iso3166-updates)](https://opensource.org/licenses/MIT)

Usage
-----
**Import package:**
```python
import iso3166_updates as iso
```

**Get all listed changes/updates for all countries and years which happens by default if no alpha-2 codes or years specified in input paramaters, export csv and json to folder "iso3166-updates", print progress via verbose flag:**
```python
iso3166_updates.get_updates(export_folder="iso3166-updates", export_json=1, export_csv=1, verbose=1)
#exported files: /iso3166-updates.json and /iso3166-updates/iso3166-updates.csv
```

**Get all listed ISO 3166-2 changes/updates for Andorra, export csv and json to folder "iso3166-updates":**
```python
iso3166_updates.get_updates("AD", export_folder="iso3166-updates", export_json=1, export_csv=1)
#exported files: /iso3166-updates-AD.json and /iso3166-updates/iso3166-updates-AD.csv
```

**Get all listed ISO 3166-2 changes/updates for BA, DE, FR, HU, PY, export only JSON of updates to export folder "iso3166-updates", print progress using verbose flag:**
```python
iso3166_updates.get_updates(["BA","DE","FR","HU","PY"], export_folder="iso3166-updates", export_json=1, export_csv=0, verbose=1)
#exported files: /iso3166-updates/iso3166-updates-BA,DE,FR,HU,PY.json
```

**Get any listed ISO 3166-2 changes/updates for HU, IT, JA, KE, in the year 2018, export only to JSON with filename "iso3166-updates.json" and seperate updates into sepetate JSON files (concat_updates=False):**
```python
iso3166_updates.get_updates("HU, IT, JA, KE", year="2018", export_json=1, export_csv=0, export_filename="iso3166-updates", concat_updates=0)
#exported files: /iso3166-updates/iso3166-updates-HU,IT,JA,KE-2018.json
```

**Get any listed ISO 3166-2 changes/updates for Ireland, between years 2012 and 2021, use default parameters (export to json but not csv):**
```python
iso3166_updates.get_updates("IE", year="2012-2021")
#exported files: /iso3166-updates/iso3166-updates-IE_2012-2021.json
```

**Get any listed ISO 3166-2 changes/updates for Tanzania, with updates with year >=2015, export only to CSV with filename iso3166-output":**
```python
iso3166_updates.get_updates("TA", year=">2015", export_filename="iso3166-output", export_json=0, export_csv=1)
#exported files: /iso3166-updates/iso3166-output-TA_>2015.csv
```

**Get any listed ISO 3166-2 changes/updates for Yemen, with updates with year < 2010, use default parameters (export to json but not csv):**
```python
iso3166_updates.get_updates("YE", year="<2010")
#exported files: /iso3166-updates/iso3166-output-YE_<2010.json
```
## Terminal/Command Line

The software functions can also be run from the cmd/terminal interface, when the script is called the get_updates() function will be called. The script accepts the same parameter names as the get_updates() function.

**Get all listed ISO 3166-2 changes/updates for all countries, export csv and json to folder "iso3166-updates", print progress using verbose flag:** 
```bash
python3 iso3166_updates.py --export_folder="iso3166-updates" --export_csv --export_json --verbose
```

**Get all listed ISO 3166-2 changes/updates for BY, DJ, ET, LY, PA for year range 2005-2010, export only CSV of updates to export folder "iso3166-updates", print progress using verbose flag:**
```bash
python3 iso3166_updates.py --alpha2="BY, DJ, ET, LY, PA" --year="2005-2010" --export_folder="iso3166-updates" --export_csv --no-export_json --verbose
```

The output to the above functions for the updates/changes to an ISO 3166-2 country returns 4 columns: 
<b>Edition/Newsletter, Date Issued, Code/Subdivision change</b> and <b>Description of change in newsletter.</b> For the CSV export, if more than one country input, then an additional primary key column <b>Country Code</b> will be prepended to the first column, which will be the 2 letter ISO 3166-1 country code. 

* Edition/Newsletter: Name and or edition of newsletter that the ISO 3166-2 change/update was communicated in.
* Date Issued: Date that the change was communicated.
* Code/Subdivision change: Overall summary of change/update made.
* Description of change in newsletter: More in-depth info about the change/update that was made.

E.g. The output format of the exported <b>CSV</b> for AD (Andorra) is:

| Edition/Newsletter | Date Issued | Code/Subdivision change | Description of change in newsletter |   
|:-------------------|:------------|------------------------------------:|------------------------:|
| Newsletter I-8     | 2007-04-17  | Subdivisions added: 7 parishes...   | Addition of the administrative subdivisions...                 | 
| Online Browsing Platform (OBP) | 2014-11-03 | No subdivision changes listed | Update List Source |
| Online Browsing Platform (OBP) | 2015-11-27 | No subdivision changes listed | Update List Source | 

E.g. The output format of the exported <b>JSON</b> for AD (Andorra) is:
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