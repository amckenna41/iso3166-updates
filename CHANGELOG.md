# Change Log

## v1.8.0/v1.8.1 - April 2025


### Added
- New function in Updates class that checks for any new updates to the updates object, comparing against the current version installed and outputting the difference between the two if any are found. 
- New function in Updates class that allows you to search for updates via country name
- Added iso3166-updates-export directory which is a dedicated folder with all the files/modules/scripts for exporting all the ISO 3166 updates. Previously they were in a single script that was growing to 1000+ lines
- Added unit test that validates each source URL in updates object
- Added custom updates function to software that allows for a custom update to be appended to a country's list of Updates
- Search functionality within the software that allows you to search for any updates using country/subdivision name or subdivision code
- Incorporated the Python package fake-useragent which is a database of user agents to pass into chromedriver, allows for a larger selection of user agents
- Added additional column conversions to the correct_columns function e.g Publication -> Source, Changes made -> Changes
- Added functionality to main export script as well as main software script where you can exclude data for an input year/list of years
- Added unit tests that test the JSON schema of the updates output
- thefuzz Python package added to pyproject dependancies 
- In packaged software, you can now search for updates based on publication date, via a date range, inclusive, e.g "2011-11-09,2013-01-09", if only one date passed in then all updates from that specific date will be gotten
- Additional parameter for Updates class, user can now input a custom filepath to the updates JSON object
- Added new parameter to the custom_update function in Updates class to not overwrite original object with new changes
- Added a parameter in the export scripts: save_each_iteration. After each iteration of country updates data being exported, the individual country data is exported to JSON/CSV. This was created after experiencing Selenium crashing and the export progress being lost
- Additional utility function to export directory that iterates over updates objects and finds objects that are duplicate or nearly duplicates
- Search endpoint added to API, allowing you to search for specific keywords in update objects
- Added unit test that tests the individual total number of updates per country
- Addded use_wiki bool parameter to main export pipeline function allowing user to just export the ISO page data by setting this to False
- Temporary manual updates function for get_script that temporary and manually makes changes to the output because of data source errors


### Changed
- Class name changed from ISO3166_Updates to Updates
- Changed Edition/Newsletter attribute to Source
- Changed Code/Subdivision attribute to Change
- All alpha country codes are passed through convert_to_alpha function rather than just alpha-3 and numeric, for validation 
- The correct_columns in the get script was rewritten to remove redundancy and ensure consistency
- Export JSON and export CSV functionaltiy now input into the same function with an input paramet er that specifies if its exporting csv or json
- Alpha codes range parameter alpha_codes_from_to changed to alpha_codes_range
- Remarks parsing function refactored to remove redundancy
- Any auxillary function used in the get scripts moved to outside the functions for resuablility and readibility 
- Reformatted some of the auxillary function in parse_updates_data script
- When exporting updates data, if Change attribute empty but Desc of Change not then swap the values such that Change is populated
- In the get script pipeline, the wiki parsing function no longer exports the Corrected Date Issued column, this is dropped before being returned
- The functionality that filters out input year/year ranges etc has been moved to a separate utilities function, rather than being in the parse functions
- For the export functionaltiies, they hasve been split up into individual modules/scripts, the unit tests have also been split up into their own test instances 
- Auxillary function that removed any double spacing from a row/string now updated to remove any instances of multiple spaces in string
- Months function in software, to get the updates over the past number of months, removed in place of the date range function which gets the updates over a specified date range
- Any exported updates with no data, exported as [] instead of {}
- Any instances of findNext in BS4 changed to find_next to avoid depracation error
- When calling the len() function on an object of the Updates class, it should return the number of individual updates objects not the number of country objects
- Made addition of the remarks data on the ISO pages optional with a parameter, by default they are added


### Fixed
- Errors when running the get_updates script from the cmd line/terminal
- In get script when parsing the wiki page of the country's updates, the Changes section can be wrapped in a "span", "h2" or "h3", code changed to fix any errors with differing elements
- Error when renaming/reformating the column names in the correct_cols function of the get script, reordered them such that they don't override each other
- Error with citations/reference links on the wiki pages not being parsed correctly and just the html selector name being exported
- Typing hints for some functions were incorrect type 
- During testing all exported files should be exported to a folder within tests dir, not within main dir 
- Error when concatenating mulitple Changes Section, the rows became out of order in terms of Date Issued column, need to resort after concatenation
- Error with some changes data exporting with "Changes" attribute empty and "Desc of Change" populated, it should be the other way around
- Some column names not being changed in correct_columns function, causing errors downstream in pipeline
- Any functions that accept a year input parameter would accept strings with multiple symbols in them e.g ">2009-2010<>" would be accepted with ">" symbol taking priority, an error is now raised if a similar input
- Error in export function where duplicate updates objects were being exported, they weren't being caught because the "corrected" date made it seem unique but the Change/Desc of change were the same
- In custom_update function in software, multiple duplicates of the new update being added to object
- In exported wiki updates table, newline/breakpoints replaced with full stops
- Better error handing in iso3166-updates module
- Issue with single & double quotes being excluded in the change text export
- Issue with the remarks info from the ISO page not being correctly added to all the attribute values
- Small fixes and changes to workflows
- Updates count total updated to 910
- Workflow throwing error when linting, bandit and or coverage checks executed on multiple versions

## v1.7.1 - May 2024


### Added 
- New version of updates JSON and CSV files exported with newly reordered attributes
- Added Chromedriver installation to workflow so the Selenium elements in get_all_iso3166_updates script can be tested
- Add export CSV functionality in check-for-updates code


### Changed
- Changed order of attributes per updates object. New order: Code/Subdivision change, Description of change, Date issued, Edition/Newsletter
- Transitioned to f strings
- Removed get_all_iso3166_update shell script which was previously used to pull all updates but no longer needed
- Upgrade checkout actions in workflows from @v3 to @v4


### Fixed
- Country output keys not in alphabetical order after exporting in get_all_iso3166_updates script
- In check-for-updates workflow, create, call and delete Cloud run app
- Fixed authentication issue in check-for-updates workflow


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

<!-- ## v1.5.0 - Dec 2023


### Added 
- Add paths-ignore to github workflow


### Changed
- Change "Description of change in newsletter" -> "Description of change" in updates object
- More info added to each error message


### Fixed
- When inputting less than year parameter, the year input itself should not be included in the output, only updates that are less than year -->

<!-- ## v1.4.5 - Oct 2023

### Added

### Changed

### Fixed -->

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