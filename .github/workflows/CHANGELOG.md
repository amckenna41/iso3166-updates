# Change Log

> Finish this...

## v1.7.1 - May 2024


### Added 
- New version of updates JSON and CSV files exported with newly reordered attributes
- Added Chromedriver installation to workflow so the Selenium elements in get_all_iso3166_updates script can be tested
- Add export CSV functionality in check-for-updates code


### Changed
- Changed order of attributes per updates object. New order: Code/Subdivision change, Description of change, Date issued, Edition/Newsletter
- Transitioned to f strings
- Removed get_all_iso3166_update shell script which was previously used to pull all updates but no longer needed


### Fixed
- Country output keys not in alphabetical order after exporting in get_all_iso3166_updates script
- In check-for-updates workflow, create, call and delete Cloud run app


## v1.7.0 - April 2024


### Added
- All new updates from 2024 added to updates object
- Added total number of updates currently in object to README and comments
- Added tqdm loop to get_all_iso3166_updates script to keep track of progress
- Additional error messages and success messages for some functionalities in check-for-updates code
- When exporting all data using get_all_iso3166_updates script, added the country name as well as its alpha-2 code to the print export
- In check-for-updates code, programmatically get the last updated date of the updates object on the repo, print out to logs
- Software and API can now accept a month range to search for e.g updates published from the last 12-36 months etc


### Changed
- Changed authentication method for using GCP in Github workflow
- Raise error if invalid alpha code input rather than just skipping and returning all data


### Fixed
- In get_all_iso3166_updates script, some country's ISO pages weren't being parsed and scraped by Chromedriver correctly, repositioned the recursive loop so that the page's html is pulled and after 3 failed attempts will raise error
- Error in check-for-updates for year parameter not being evaluated correctly, changed if year!=[] to if year!=['']
- Coverage report not working/uploading correctly
- Rewording on some function docstrings 
- Spell check on code
- Add platform module to software and unit tests so they can be run on Windows as well as Mac/Linux
- TestPyPI and PyPI workflows were executed even if the test workflow failed


## v1.6.0 - Dec 2023


### Added
- In get_all_iso3166_updates script, added any "remarks" listed in the summary table on a country's ISO page, these are added to the "Description of change" attribute for each subdivision, if applicable
- All new updates from 2023 added to updates object
- Software and API can now accept a number of months to get the published updated from, e.g get all updates from the past 24 months etc
- Add support for other ISO 3166-1 alpha codes in functions that take alpha codes as input, including alpha-2, alpha-3 and numeric


### Changed
- Moved from using setup.py to pyproject.toml for software package distribution
- Reordered jobs in github workflow file
- Append OBP (Online Browsing Platform) URL for country's ISO page to Edition/Newsletter attribute
- Validate that all current updates object have some form of update change listed in attributes, else remove
- In check-for-updates return any missing data in general and not just missing data within the specified month/date range

### Fixed
- When inputting year range parameter, add extra validation such that the lesser number is on the left hand side of the '-' so that error not thrown
- Incorrect output JSON and CSV file names when duplicate alpha code input as parameter e.g python get_all_iso3166_updates.py --alpha=AD,AD, would export iso3166-updates-AD,AD.json rather than iso3166-updates-AD.json
- Runtime Error when occasionally running Selenium, added a recursive element to it such that the Selenium code is retried up to 3 times before an error is thrown
- Bug fix on year parameter for ISO3166_Updates class
- Drop rows of updates object if "Description of Change" and "Code/Subdivision Change" are duplicate
- When searching for an update by a year, some updates that had a "corrected" publication date weren't being returned
- For each attribute value in object, any double spacing removed

## v1.5.0 - Dec 2023


### Added 
- Add paths-ignore to github workflow


### Changed
- Change "Description of change in newsletter" -> "Description of change" in updates object
- More info added to each error message


### Fixed
- When inputting less than year parameter, the year input itself should not be included in the output, only updates that are less than year

## v1.4.5 - Oct 2023

### Added

### Changed

### Fixed

<!-- .. Latest Version: **1.6.1**.
.. ******
.. v1.6.1
.. ******
.. * Updating class instance encapsulation structure
.. * Update API index file class import
.. * Update package dependencies
.. * Update software and API docs to reflect new class import structure
.. * Update workflow actions to have validation that previous workflow created

.. ******
.. v1.6.0
.. ******
.. * Add readthedocs documentation
.. * Add remarks from ISO page to each update's description, if applicable
.. * Add tqdm loop in get_all script
.. * Adding demo, medium article and documentation links to readme
.. * Update library requirements
.. * Update workflow timeouts

.. ******
.. v1.5.0
.. ******
.. * Add UPDATES.md file that keeps track of all the ISO 3166 updates 
.. * Adding additional env vars (EXPORT, CREATE_ISSUE) to check_for_updates functionality
.. * Add OBP link to each update description
.. * Update usage examples in comments and readme's
.. * Update software package description
.. * Add additional unit tests for software and API
.. * Fix gcloud error in check_for_updates.yml workflow
.. * Rerun get_all script with latest data

.. ******
.. v1.4.5
.. ******
.. * Add API frontend with documentation and description about software & API
.. * Update check_for_updates functionality with archive folder create_issue functionality
.. * https://github.com/amckenna41/iso3166-updates/commit/2c5f6d0dc33939d7401efc27e725fedbad2ab27d#diff-28bf033b5cb718463e74964422b5de9a0ab07436c3a765363e7c6ceb8a421e8b -->