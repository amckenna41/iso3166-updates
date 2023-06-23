# iso3166-updates

[![iso3166_updates](https://img.shields.io/pypi/v/iso3166-updates)](https://pypi.org/project/iso3166-updates/)
[![Platforms](https://img.shields.io/badge/platforms-linux%2C%20macOS%2C%20Windows-green)](https://pypi.org/project/iso3166-updates/)
[![PythonV](https://img.shields.io/pypi/pyversions/iso3166-updates?logo=2)](https://pypi.org/project/iso3166-updates/)
[![License: MIT](https://img.shields.io/github/license/amckenna41/iso3166-updates)](https://opensource.org/licenses/MIT)

Usage
-----
**Import package:**
```python
import iso3166_updates as iso3166_updates
```

**Input parameters to get_updates function:**
```python
  # -alpha2 ALPHA2, --alpha2 ALPHA2
  #                       Alpha-2 code/s of ISO3166 countries to check for updates.
  # -export_filename EXPORT_FILENAME, --export_filename EXPORT_FILENAME
  #                       Filename for exported ISO3166 updates for CSV and JSON files.
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

**Get all listed changes/updates for all countries which happens by default if no alpha-2 codes specified in input param, export csv and json to folder "iso3166-updates":**
```python
iso3166_updates.get_updates(export_folder="iso3166-updates", export_json=1, export_csv=1)
#exported files: /iso3166-updates/iso3166-updates.json and /iso3166-updates/iso3166-updates.csv
```

**Get all listed changes/updates for Andorra from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:AD), export csv and json to folder "iso3166-updates":**
```python
iso3166_updates.get_updates("AD", export_folder="iso3166-updates", export_json=1, export_csv=1)
#exported files: /iso3166-updates/iso3166-updates-AD.json and /iso3166-updates/iso3166-updates-AD.csv
```

**Get all listed changes/updates for BA, DE, FR, HU, PY, export only JSON of updates to export folder "iso3166-updates":**
```python
iso3166_updates.get_updates(["BA","DE","FR","HU","PY"], export_folder="iso3166-updates", export_json=1, export_csv=0)
#exported files: /iso3166-updates/iso3166-updates-BA,DE,FR,HU,PY.json
```

**Get any listed changes/updates for HU, IT, JA, KE from wiki, in the year 2018, export only to JSON with filename "iso3166-updates.json" and seperate updates into sepetate JSON files:**
```python
iso3166_updates.get_updates("HU, IT, JA, KE", year="2018", export_json=1, export_csv=0, export_filename="iso3166-updates", concat_updates=0)
#exported files: /iso3166-updates/iso3166-updates-HU,IT,JA,KE-2018.json
```

**Get any listed changes/updates for Ireland from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:IE), between years of 2012 and 2021, use default parameters:**
```python
iso3166_updates.get_updates("IE", year="2012-2021")
#exported files: /iso3166-updates/iso3166-updates-IE_2012-2021.json
```

**Get any listed changes/updates for Tanzania from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:TZ), with updates years >=2015, export only to CSV with filename iso3166-output":**
```python
iso3166_updates.get_updates("TA", year=">2015", export_filename="iso3166-output", export_json=0, export_csv=1)
#exported files: /iso3166-updates/iso3166-output-TA_>2015.csv
```

**Get any listed changes/updates for Yemen from wiki (https://en.wikipedia.org/wiki/ISO_3166-2:YE), with updates years < 2010, use default parameters:**
```python
iso3166_updates.get_updates("YE", year="<2010")
#exported files: /iso3166-updates/iso3166-output-YE_<2010.json
```

The output to the above functions for the updates/changes to a ISO 3166-2 country returns 4 columns: 
<b>Edition/Newsletter, Date Issued, Code/Subdivision change</b> and <b>Description of change in newsletter.</b> 

* Edition/Newsletter: Name and or edition of newsletter that ISO 3166-2 change/update was communicated in.
* Date Issued: Date that the change was communicated.
* Code/Subdivision change: Overall summary of change/update made.
* Description of change in newsletter: More in-depth info about the change/update that was made.

E.g. The output format of the exported CSV for AD (Andorra) is:

| Edition/Newsletter | Date Issued | Code/Subdivision change | Description of change in newsletter |   
|:-------------------|:------------|------------------------------------:|------------------------:|
| Newsletter I-8     | 2007-04-17  | Subdivisions added: 7 parishes...   | Addition of the administrative subdivisions...                 | 
| Online Browsing Platform (OBP) | 2014-11-03 | No subdivision changes listed | Update List Source |
| Online Browsing Platform (OBP) | 2015-11-27 | No subdivision changes listed | Update List Source | 

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