# ISO 3166 Updates Export 📦

This directory has all the associated scripts and functionality for exporting all the ISO 3166 updates from the various data sources. Below are a description of each of the scripts:

* `driver.py` - initialise the Selenium Chromedriver instance for exporting data from the country ISO pages.
* `get_updates_data.py` - export the updates data from the ISO and wiki data sources.
* `main.py` - main entry script for full exporting pipeline.
* `parse_updates_data.py` - functionality to parse and validate the data exported from the get_updates_data module.
* `utils.py` - several utility functions used throughout the exporting pipeline.
* `requirements.txt` - list of packages required for export functionality. 

Requirements
------------
* [python][python] >= 3.8
* [iso3166-updates][iso3166-updates] >= 1.7.0
* [pandas][pandas] >= 1.4.4
* [requests][requests] >= 2.28.1
* [beautifulsoup4][beautifulsoup4] >= 4.11.1
* [iso3166][iso3166] >= 2.1.1
* [selenium][selenium] >= 4.10.0
* [tqdm][tqdm] >= 4.64.0
* [fake_useragent][fake_useragent] >= 1.5.0

Usage
-----
Below are some examples of using the export scripts for exporting the ISO 3166 updates data:

**Input parameters to main export get_iso3166_updates function in main.py script:**
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

**Export all the latest changes/updates for all ISO 3166 countries, using all default parameters:**
```bash
python3 iso3166_updates_export/main.py
```

**Export all the latest changes/updates for all ISO 3166 countries, export to CSV and JSON with verbose output:**
```bash
python3 iso3166_updates_export/main.py --export_json --export_csv --verbose
```

**Export all the latest changes/updates for subset of alpha country codes (BA,DE,FR,HU,PY), export only JSON of updates to export folder "iso3166-updates", print progress using verbose flag:**
```python
from iso3166_updates_export import *

get_iso3166_updates(alpha_codes="BA","DE","FR","HU","PY", export_folder="iso3166-updates", export_json=1, export_csv=0, verbose=1)
#exported files: /iso3166-updates/iso3166-updates_BA,DE,FR,HU,PY.json
```

**Export all listed changes/updates for subset of alpha country codes (HU,IT,JA,KE), in the year 2018, export to JSON and XML with filename "iso3166-updates.json" and separate updates into separate JSON files (concat_updates=False):**
```python
from iso3166_updates_export import *

get_iso3166_updates(alpha_codes="HU,IT,JA,KE", year="2018", export_json=1, export_csv=0, export_xml=1, export_filename="iso3166-updates", concat_updates=0)
#exported files: /iso3166-updates/iso3166-updates_HU,IT,JA,KE_2018.json
#exported files: /iso3166-updates/iso3166-updates_HU,IT,JA,KE_2018.xml
```

**Export all listed changes/updates for Ireland, between years 2012 and 2021, use default parameters (export to XML and csv):**
```python
from iso3166_updates_export import *

get_iso3166_updates(alpha_codes="IE", year="2012-2021", export_csv=1, export_xml=1)
#exported files: /iso3166-updates/iso3166-updates_IE_2012-2021.csv
#exported files: /iso3166-updates/iso3166-updates_IE_2012-2021.xml
```

**Get all the latest updates for subset of alpha country codes (HU, IQ, VC) after 2006, export to CSV, JSON and XML with verbose output:**
```python
from iso3166_updates_export import *

get_iso3166_updates(alpha_codes="HU,IQ,VC", year=">2006", export_json=True, export_csv=True, export_xml=True, verbose=True)
#exported files: /iso3166-updates/iso3166-updates_HU_IQ_VC_>2006.json
```

**Get all the latest updates for subset of alpha country codes (MO, PA, RW) excluding 2009 and 2021, export to CSV, JSON and XML with verbose output:**
```python
from iso3166_updates_export import *

get_iso3166_updates(alpha_codes="MO,PA,RW", year="<>2009,2021", export_json=True, export_csv=True, export_xml=True, verbose=True)
#exported files: /iso3166-updates/iso3166-updates_MO_PA_RW_<>2009,2021.json
```
    
**Get all the latest updates for all alpha country codes in range DJ-TA, alphabetically, export to CSV and JSON with verbose output:**
```python
from iso3166_updates_export import *

get_iso3166_updates(alpha_codes_range="DJ-TA", export_json=True, export_csv=True, verbose=True)
#exported files: /iso3166-updates/iso3166-updates_DJ-TA.json
#exported files: /iso3166-updates/iso3166-updates_DJ-TA.csv
```


<!-- **Import module:**
```python
import get_all_iso3166_updates as iso3166_updates
```


**Get any listed ISO 3166 changes/updates for Tanzania, with updates with year >= 2015, export only to CSV with filename "iso3166-output":**
```python
iso3166_updates.get_updates("TA", year=">2015", export_filename="iso3166-output", export_json=0, export_csv=1)
#exported files: /iso3166-updates/iso3166-output-TA_>2015.csv
```

**Get any listed ISO 3166 changes/updates for Yemen, with updates with year < 2010, use default parameters (export to json but not csv):**
```python
iso3166_updates.get_updates("YE", year="<2010")
#exported files: /iso3166-updates/iso3166-output-YE_<2010.json
``` -->

The output files from the <i>get_all_iso3166_updates.py</i> script for the updates/changes to an ISO 3166-2 country returns 4 columns: 
<b>Change, Description of Change, Date Issued</b> and <b>Source.</b> For the CSV export, if more than one country input, then an additional primary key column <b>Country Code</b> will be prepended to the first column, which will be the 2 letter ISO 3166-1 country code. 

* **Change**: overall summary of change/update made.
* **Description of Change**: more in-depth info about the change/update that was made, including any remarks listed on the official ISO page.
* **Date Issued**: date that the change was communicated.
* **Source**: name and or edition of newsletter that the ISO 3166 change/update was communicated in (pre 2013), or the link to the country's ISO Online Browsing Platform page.

E.g. The output format of the exported <b>CSV</b> for AD (Andorra) is:

| Change | Description of Change | Date Issued | Source |   
|:-------------------|:------------|------------------------------------:|------------------------:|
| Subdivisions added: 7 parishes.   | Addition of the administrative subdivisions and of their code elements. | 2007-04-17 | Newsletter I-8 - https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf. | 
| Update List Source. |  | 2014-11-03 | Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD. | 
| Update List Source. |  | 2015-11-27 | Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD. | 

E.g. The output format of the exported <b>JSON</b> for AD (Andorra) is:
```javascript
{
  "AD": [
      {
          "Change": "Update List Source.",
          "Description of Change": "",
          "Date Issued": "2015-11-27",
          "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD."
      },
      {
          "Change": "Update List Source.",
          "Description of Change": "",
          "Date Issued": "2014-11-03",
          "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD."
      },
      {
          "Change": "Subdivisions added: 7 parishes.",
          "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
          "Date Issued": "2007-04-17",
          "Source": "Newsletter I-8 - https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf."

      }
  ]
}
```

E.g. The output format of the exported <b>XML</b> for AD (Andorra) is:

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

[python]: https://www.python.org/downloads/release/python-360/
[python-dateutil]: https://pypi.org/project/python-dateutil/
[pandas]: https://pandas.pydata.org/
[tqdm]: https://github.com/tqdm/tqdm
[requests]: https://requests.readthedocs.io/
[beautifulsoup4]: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
[selenium]: https://selenium-python.readthedocs.io/index.html
[iso3166]: https://github.com/deactivated/python-iso3166
[fake_useragent]: https://pypi.org/project/fake-useragent/
[iso3166-updates]: https://github.com/amckenna41/iso3166-updates