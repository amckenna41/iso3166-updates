from itertools import product
import argparse
import requests
import iso3166
import os
import getpass
import json
import re
from bs4 import BeautifulSoup, Tag
from importlib import metadata
import time
import datetime
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait 
import pandas as pd
pd.options.mode.chained_assignment = None

#get current software version
__version__ = metadata.metadata('iso3166_updates')['version']

#initalise User-agent header for requests library 
USER_AGENT_HEADER = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(__version__,
                                       'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}

#base URL for ISO3 166-2 wiki and ISO website
wiki_base_url = "https://en.wikipedia.org/wiki/ISO_3166-2:"
iso_base_url = "https://www.iso.org/obp/ui/en/#iso:code:3166:"

#path to chromedriver executable
chromedriver_executeable_path = '/usr/local/bin/chromedriver'

def create_driver():
    """
    Create instance of Selenium chromedriver for each country's individual page on the 
    official ISO website. The site requires a session to be created and Javascript to
    be ran, therefore the page's data cannot be directly webscraped. For some countries 
    their ISO page contains extra data not on the country's wiki page. 

    Parameters
    ==========
    None

    Returns
    =======
    :driver : selenium.webdriver.chrome.webdriver.WebDriver
        instance of Python Selenium using chromedriver webdriver.
    
    References
    ==========
    [1]: https://chromedriver.chromium.org/getting-started
    [2]: https://www.geeksforgeeks.org/how-to-install-selenium-in-python/
    [3]: https://www.scrapingbee.com/webscraping-questions/selenium/chromedriver-executable-needs-to-be-in-path/
    [4]: https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json
    """
    #verify Chromedriver is found on path, raise exception if not
    if not (os.path.isfile(chromedriver_executeable_path)):
      raise WebDriverException("Chromedriver not found at path: " + chromedriver_executeable_path + ". Verify it's installed in path by executing 'ls /usr/bin/' or 'ls /usr/lib'.")

    #create instance of Service class and get executeable path of chromedriver
    #execute "which chromedriver" to see path where it is installed
    # service = Service(executable_path='/usr/lib/chromium-browser/chromedriver')
    # service = Service(executable_path='/usr/bin/chromium-browser/chromedriver')
    service = Service(executable_path=chromedriver_executeable_path)

    #create instance of Options class, add below options to ensure everything works as desired
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    chrome_options.add_experimental_option("useAutomationExtension", False) 
    #when testing locally need to specify the binary location of Google Chrome
    # chrome_options.binary_location = ""

    #create webdriver instance
    driver = webdriver.Chrome(service=service, options=chrome_options)

    #set object to undefined, helps avoid bot detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 

    #at each calling of Chromedriver, select random user agent from below list
    user_agents = [ 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36", 
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15"\
    ] 
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": random.choice(user_agents)}) 

    return driver

def get_updates(alpha2_codes=[], year=[], export_filename="iso3166-updates", export_folder="iso3166-updates-output",
        concat_updates=True, export_json=True, export_csv=False, verbose=True, use_selenium=True):
    """
    Get all listed changes/updates to a country/country's ISO 3166-2 subdivision codes/names.
    The two data sources for the updates data are via the "Changes" section on its wiki page as
    well as any listed updates on the official ISO website. A country's wiki page and section on
    ISO website follow the convention https://en.wikipedia.org/wiki/ISO_3166-2:XX and
    https://www.iso.org/obp/ui#iso:code:3166:XX, respectively, where XX is the 2 letter alpha-2 code
    for a country listed in the ISO 3166-1. The "Changes" section lists updates or changes to any
    ISO 3166-2 codes, including historical changes, according to the ISO newsletter which is released
    peridically by the ISO as well as its Online Browsing Platform (OBP). Some countries have missing
    and or not up-to-date updates data on their wiki pages, so the country data from the official ISO
    website is also gathered using Selenium Chromedriver, prior to being scraped using BeautifulSoup,
    as the page requires Javascript to be run on page load.

    The ISO newsletters are not easily discoverable and accessible online and may require a
    subscription to the ISO 3166-2 database (https://www.iso.org/iso/updating_information.pdf), with
    the ISO 3166 dataset itself costing around $330.

    The earliest available changes are from the year 2000 and the latest changes are from 2023.

    The updates data from the wiki page and ISO website are converted to a DataFrame and then
    exported to a CSV and or JSON for further analysis. You can also get the updates from a
    particular year, list of years, year range or updates greater than or less than a specified year,
    using the year parameter. All of the updates are ordered alphabetically by their 2 letter
    ISO 3166-1 country code and exported to a JSON and or CSV file.

    Parameters
    ==========
    :alpha2_codes : str/list (default=[])
        single string or list of alpha-2 ISO 3166-1 codes to get the latest ISO 3166-2 updates
        from. If a single alpha-2 code passed in then it is converted to an iterable list. If
        no value passed into param then all updates for all ISO 3166-1 countries are retrieved.
    :year : list (default = [])
        list of 1 or more years to get the specific ISO 3166-2 updates from, per country. By
        default, the year param will be empty meaning all changes/updates for all years will be
        retrieved. You can also pass in a year range (e.g 2010-2015) or a year to get all updates
        less than or greater than that specified year (e.g >2007, <2021).
    :export_filename : str (default="iso3166-updates")
        filename for JSON and CSV output files of inputted country's ISO 3166-2 updates.
    :export_folder : str (default="iso3166-updates-output")
        folder name to store all csv and json outputs for all country's ISO 3166-2 updates.
    :concat_updates : bool (default=True)
        if multiple alpha-2 codes input, concatenate updates into one JSON and or CSV file
        (concat_updates=True) or into seperately named files in export folder
        (concat_updates=False). By default all country's updates will be compiled into the
        same file.
    :export_json : bool (default=True)
        export all ISO 3166 updates for inputted countries into json format in export folder.
    :export_csv : bool (default=False)
        export all ISO 3166 updates for inputted countries into csv format in export folder.
    :verbose: bool (default=False)
        Set to 1 to print out progress of updates functionality, 0 will not print progress.
    :use_selenium : bool (default=True)
        Gather all data for each country from its official page on the ISO website which
        requires Python Selenium and Chromedriver. If False then just use country data
        from its wiki page.

    Returns
    =======
    :all_changes : dict
        dictionary of all found ISO 3166 updates from user's inputted alpha-2 codes and or year
        parameter values.
    """
    year_range = False
    greater_than = False
    less_than = False

    #if alpha-2 codes input param isn't str or list, raise type error
    if not isinstance(alpha2_codes, str) and not isinstance(alpha2_codes, list):
        raise TypeError('alpha2_codes input param should be a 2 letter '
            'ISO 3166-1 alpha-2 code or a list of the same, got input of type {}.'.format(type(alpha2_codes)))

    #if single str of 1 or more alpha-2 codes input then convert to array, remove whitespace, seperate using comma
    if (isinstance(alpha2_codes, str)):
        alpha2_codes = alpha2_codes.replace(' ', '').split(',')

    #convert year str to array
    if not (isinstance(year, list)):
        year = [year]

    #if single str of 1 or more years input then convert to array, remove whitespace, seperate using comma
    if (isinstance(year, str)):
        year = year.replace(' ', '').split(',')

    #raise error if invalid data types input for year parameter
    for year_ in year:
        if not isinstance(year_, str):
            raise TypeError("Invalid data type for year parameter, expected str, got {}.".format(type(year_)))

    #if list with 1 string of multiple alpha-2 codes, convert to multiple list elements e.g ['HI, LA'] will be converted to ['HI', 'LA']
    if (isinstance(alpha2_codes, list) and len(alpha2_codes) == 1 and ',' in alpha2_codes[0]):
        alpha2_codes = alpha2_codes[0].replace(' ', '').split(',')

    def convert_to_alpha2(alpha3_code):
        """
        Convert an ISO 3166 country's 3 letter alpha-3 code into its 2 letter
        alpha-2 counterpart.

        Parameters
        ==========
        :alpha3_code: str
            3 letter ISO 3166-1 country code.

        Returns
        =======
        :iso3166.countries_by_alpha3[alpha3_code].alpha2: str
            2 letter ISO 3166 country code.
        """
        #return None if 3 letter alpha-3 code not found
        if not (alpha3_code in list(iso3166.countries_by_alpha3.keys())):
            return None
        else:
            #use iso3166 package to find corresponding alpha-2 code from its alpha-3
            return iso3166.countries_by_alpha3[alpha3_code].alpha2

    #if 3 letter alpha-3 codes input then convert to corresponding alpha-2, else raise error
    if (alpha2_codes != [''] and alpha2_codes != []):
        for code in range(0, len(alpha2_codes)):
            if (len(alpha2_codes[code]) == 3):
                temp_alpha2_code = convert_to_alpha2(alpha2_codes[code])
                if not (temp_alpha2_code is None):
                    alpha2_codes[code] = temp_alpha2_code
                else:
                    raise ValueError("Invalid alpha-3 code input, cannot convert into corresponding alpha-2 code: {}.".format(alpha2_codes[code]))

    #var to keep track of original alpha-2 and year parameter inputs
    input_alpha2_codes = alpha2_codes
    input_year = year

    #use all ISO 3166-1 codes if no input alpha-2 parameter input
    if ((alpha2_codes == [''] or alpha2_codes == [])):
        alpha2_codes = sorted(list(iso3166.countries_by_alpha2.keys()))

    #sort codes in alphabetical order, uppercase each
    alpha2_codes.sort()
    alpha2_codes = [code.upper() for code in alpha2_codes]

    #remove XK (Kosovo) from list if applicable
    if ("XK" in alpha2_codes):
        alpha2_codes.remove("XK")

    #a '-' seperating 2 years implies a year range of sought country updates, validate format of years in range
    #a ',' seperating 2 year implies a list of years
    #a '>' before year means get all country updates greater than or equal to specified year
    #a '<' before year means get all country updates less than specified year
    if (year != []):
        if ('-' in year[0]):
            year_range = True
            year = year[0].split('-')
            #only 2 years should be included in input parameter
            if (len(year) > 2):
                year = []
                year_range = False
        #parse array for using greater than symbol
        elif ('>' in year[0]):
            year = list(year[0].rpartition(">")[1:])
            greater_than = True
            year.remove('>')
            if (len(year) > 2):
                year = []
                greater_than = False
        #parse array for using less than symbol
        elif ('<' in year[0]):
            year = list(year[0].rpartition("<")[1:])
            less_than = True
            year.remove('<')
            if (len(year) > 2):
                year = []
                less_than = False
        elif (',' in year[0]):
            #split years into comma seperated list of multiple years if multiple years are input
            year = year[0].split(',')
    #validate each year's format using regex
    for year_ in year:
        #skip to next iteration if < or > symbol
        if (year_ == '<' or year_ == '>' or year_ == '-'):
            continue
        if not (bool(re.match(r"^1[0-9][0-9][0-9]$|^2[0-9][0-9][0-9]$", year_))):
            year = []
            year_range = False
            break
    
    #object to store all country updates/changes
    all_changes = {}

    #temp filename export var
    temp_filename = os.path.splitext(export_filename)[0]

    ### Get JSON and CSV filenames based on alpha-2 and year input parameters - concat_updates=True ###

    #append 2 letter alpha-2 codes to export filenames if less than 10 input, append year as well if applicable
    if (len(alpha2_codes) <= 10 and not (any(code in export_filename for code in alpha2_codes)) and \
        concat_updates==True and (year != [''] and year != []) and len(year) <= 10 and not \
            (greater_than or less_than or year_range)):

        #seperate alpha-2 codes and years into comma seperated lists
        alpha2_str = ','.join(alpha2_codes)
        year_str = ','.join(year)

        #append list of alpha-2 codes and or years to json and csv filenames
        temp_filename = temp_filename + "-" + alpha2_str + "_" + year_str

    else:
        #append 2 letter alpha-2 codes to export filename, year parameter not appended
        if (len(alpha2_codes) <= 10 and not (any(code in export_filename for code in alpha2_codes)) \
                and (year == [''] or year == []) and concat_updates==True):

            #seperate alpha-2 codes into comma seperated lists
            alpha2_str = ','.join(alpha2_codes)

            #append list of alpha-2 codes to json and csv filenames
            temp_filename = temp_filename + "-" + alpha2_str

        #append greater than/less than/year range symbols to filenames
        elif ((greater_than or less_than or year_range) and concat_updates==True):

            #seperate alpha-2 codes and years into comma seperated lists
            alpha2_str = ','.join(alpha2_codes)
            year_str = ','.join(year)

            #append alpha-2 codes to filename if less than 10 input
            if (len(alpha2_codes) <= 10):
                temp_filename = temp_filename + "-" + alpha2_str

            #append list of years and gt/lt/year range symbols to json and csv filenames, if applicable
            if (greater_than):
                temp_filename = temp_filename + "_>" + year_str
            elif (less_than):
                temp_filename = temp_filename + "_<" + year_str
            elif (year_range):
                temp_filename = temp_filename + "_" + year[0] + "-" + year[1]

        #append year param to filename if alpha-2 input param is empty
        elif ((input_alpha2_codes == [] or input_alpha2_codes == ['']) and (year != [] and year != ['']) and \
              concat_updates==True and len(year) <= 10 and not (greater_than or less_than or year_range)):

            #seperate years into comma seperated lists
            year_str = ','.join(year)

            #append list of years to json and csv filenames
            temp_filename = temp_filename + "-" + year_str

    #file export filename
    export_filename_concat_updates = temp_filename

    #dataframe for csv export
    csv_iso3166_df = pd.DataFrame()

    #start elapsed time counter
    start = time.time()

    #iterate over all input ISO 3166-1 country codes
    for alpha2 in alpha2_codes:

        #skip to next iteration if alpha-2 not valid
        if (alpha2 not in list(iso3166.countries_by_alpha2.keys())):
            continue

        #print out progress of function
        if (verbose):
            print("ISO 3166-1 Code: {} ({}, {})".format(alpha2, wiki_base_url + alpha2, iso_base_url + alpha2))

        all_changes[alpha2] = {}    

        #web scrape country's wiki data, convert html table/2D array to dataframe
        iso3166_df_wiki = get_updates_df_wiki(alpha2, year, year_range, less_than, greater_than)

        #use Selenium Chromedriver to parse country's updates data from official ISO website
        if (use_selenium):
            iso_website_df = get_updates_df_selenium(alpha2, year, year_range, less_than, greater_than)

            #concatenate two updates dataframes
            iso3166_df = pd.concat([iso3166_df_wiki, iso_website_df], ignore_index=True, sort=False)
        else:
            iso3166_df = iso3166_df_wiki
        
        #only export non-empty dataframes
        if not (iso3166_df.empty):

            def is_corrected_date(row): 
                """ return true/false if row in dataframe has a "corrected" publication date in Date Issued col. """
                return True if ("corrected" in row) else False

            #column tracks if ISO 3166-2 updates have a "corrected" publication date
            iso3166_df["Corrected Date"] = iso3166_df["Corrected Date Issued"].apply(is_corrected_date)

            #temporary dataframe to track row with "corrected" publication date
            corrected_date_iso3166_df = iso3166_df[iso3166_df["Corrected Date"] == True]

            #if applicabale, merge temporary df with main df, reset index & override original df with "corrected" publication date row
            if not (corrected_date_iso3166_df.empty):
              iso3166_df.set_index('Date Issued', inplace=True)
              iso3166_df.update(corrected_date_iso3166_df.set_index('Date Issued'), overwrite=True)
              iso3166_df.reset_index(inplace=True)

            #convert date column to datetime object
            iso3166_df['Date Issued'] = pd.to_datetime(iso3166_df["Date Issued"])

            #sort and order by date, newest to oldest
            iso3166_df = iso3166_df.sort_values(by=['Date Issued'], ascending=False)

            #convert date column back to string 
            iso3166_df['Date Issued'] = iso3166_df['Date Issued'].astype(str)

            #drop duplicates by Date Issued column
            iso3166_df = iso3166_df.drop_duplicates("Date Issued")

            #append "corrected" date to Date Issued column, if applicabale 
            iso3166_df['Date Issued'] = iso3166_df['Date Issued'] + iso3166_df['Corrected Date Issued']

            #drop unrequired date columns
            iso3166_df.drop(["Corrected Date Issued", "Corrected Date"], axis=1, inplace=True)

            #create dataframe for csv export with updates concatenated in same file
            if (export_csv and concat_updates):
                if len(alpha2_codes) > 1:
                    #insert Country Code primary key column in dataframe if more than 1 country exported
                    iso3166_df.insert(0, "Country Code", alpha2, True)
                    #concatenate original dataframe with csv dataframe with new primary key column
                    csv_iso3166_df = pd.concat([iso3166_df, csv_iso3166_df], axis=0)
                    #drop Country Code column from original dataframe
                    iso3166_df.drop('Country Code', axis=1, inplace=True)
                else:
                    csv_iso3166_df = iso3166_df

            #add ISO updates to object of all ISO 3166 updates, convert to json
            all_changes[alpha2] = json.loads(iso3166_df.to_json(orient='records'))

    #end elapsed time counter and calculate
    end = time.time()
    elapsed = end - start

    #create output folder if doesn't exist and files are set to be exported
    if (export_csv or export_json) and not (os.path.isdir(export_folder)):
        os.mkdir(export_folder)

    #auxillary function to remove all empty nested dicts within object
    def _del(_d):
        return {a:_del(b) if isinstance(b, dict) else b for a, b in _d.items() if b and not a.startswith('_')}

    #remove any empty nested updates dict if gathering all country updates, keep empty dicts if list of alpha-2 codes input 
    if (year != [] and input_alpha2_codes == []):
        all_changes = _del(all_changes)

    #temp filename export var
    temp_filename = os.path.splitext(export_filename)[0]

    #export all ISO 3166 updates to json, store in export folder dir
    if (export_json):
        all_changes_json = all_changes
        #checking if all_changes object isn't empty
        if (all_changes_json):
            #if singular country code input and it's contents are empty, set to empty dict
            if (len(alpha2_codes) == 1 and not (any(all_changes_json.values()))):
                all_changes_json = {}
            if (concat_updates):
                #export updates into the same json
                with open(os.path.join(export_folder, os.path.splitext(export_filename_concat_updates)[0] + ".json"), "w") as write_file:
                    json.dump(all_changes_json, write_file, indent=4, ensure_ascii=False)
            else:
                #seperate country updates into individual json files
                for update in all_changes_json:
                    #append alpha-2 codes and list of years or gt/lt/6range symbols, if applicable, to seperate exported json files
                    if (year != [] and year != ['']):
                        if (greater_than):
                            export_filename_no_concat_updates = temp_filename + "-" + update + "_>" + ','.join(year) + ".json"
                        elif (less_than):
                            export_filename_no_concat_updates = temp_filename + "-" + update + "_<" + ','.join(year) + ".json"
                        elif (year_range):
                            export_filename_no_concat_updates = temp_filename+ "-" + update + "_" + year[0] + "-" + year[1] + ".json"
                        else:
                            export_filename_no_concat_updates = temp_filename + "-" + update + "-" + ','.join(year) + ".json"
                    else:
                        export_filename_no_concat_updates = temp_filename + "-" + update + ".json"

                    #export updates object to seperate json files
                    with open(os.path.join(export_folder, export_filename_no_concat_updates), "w") as write_file:
                        json.dump(all_changes_json[update], write_file, indent=4, ensure_ascii=False)

            #if verbose flag set, print export completion message
            if (verbose):
                print("All ISO 3166 updates exported to folder {}.".format(export_folder))

    #export all ISO 3166 updates to csv, store in export folder dir
    if (export_csv):
        #checking if all_changes object isn't empty
        if (all_changes):
            #validate all_changes object contains at least one non-empty dict, don't export if all empty dicts
            if (any(all_changes.values())):
                if (concat_updates):
                    #append Country Code column if more than one country input
                    if len(alpha2_codes) > 1:
                        #sort dataframe alphabetically using country code column
                        csv_iso3166_df.sort_values('Country Code', inplace=True)
                    #export updates object to same concatenated csv file
                    csv_iso3166_df.to_csv(os.path.join(export_folder, os.path.splitext(export_filename_concat_updates)[0] + ".csv"), index=False)
                else:
                    #seperate country updates into individual csv files
                    for update in all_changes:
                        #convert updates object into dataframe
                        temp_updates = pd.DataFrame(all_changes[update])
                        #skip to next updates object if dataframe is empty
                        if (temp_updates.empty):
                            continue
                        #append alpha-2 codes and list of years or gt/lt/year range symbol, if applicable, to seperate exported csv files
                        if (year != [] and year != ['']):
                            if (greater_than):
                                export_filename_no_concat_updates = temp_filename + "-" + update + "_>" + ','.join(year) + ".csv"
                            elif (less_than):
                                export_filename_no_concat_updates = temp_filename + "-" + update + "_<" + ','.join(year) + ".csv"
                            elif (year_range):
                                export_filename_no_concat_updates = temp_filename + "-" + update + "_" + year[0] + "-" + year[1] + ".csv"
                            else:
                                export_filename_no_concat_updates = temp_filename + "-" + update + "_" + ','.join(year) + ".csv"
                        else:
                            export_filename_no_concat_updates = temp_filename + "-" + update + ".csv"

                        #export updates object to seperate csv files
                        temp_updates.to_csv(os.path.join(export_folder, export_filename_no_concat_updates), index=False)

    if (verbose):
        print("Total elapsed time for executing script: {} minutes".format(round(elapsed/60, 2)))

    return all_changes

def get_updates_df_selenium(alpha2, year=[], year_range=False, less_than=False, greater_than=False):    
    """
    Pull all related ISO 3166-2 updates/changes for a given input country from the official ISO 
    website. The Selenium Chromedriver tool is utilised prior to the BS4 web scraper as JavaScript
    has to run on the site to get the data. Various random steps are implemented during exection
    of the Chromedriver to avoid requests being blocked. The changes section for each country is 
    parsed and, converted into a 2D table and then a DataFrame.

    Parameters
    ==========
    :alpha2 : str/list
        single string of an alpha-2 ISO 3166-1 codes to get the latest ISO 3166-2 updates for.
    :year : array
        array/list of year(s). If not empty only the ISO 3166 updates for the selected
        year for a particular country will be returned. If empty then all years of 
        updates are returned.
    :year_range: bool
        set to True if a range of years are input into year parameter e.g "2002-2010" etc.
        Function will remove all rows in Dataframe that aren't in specified year range.
    :less_than: bool
        set to True if less than symbol is input into year parameter e.g "<2018" etc.
        Function will remove all rows in Dataframe that are greater than specified year.
    :greater_than: bool
        set to True if greater than symbol is input into year parameter e.g ">2005" etc.
        Function will remove all rows in Dataframe that are less than specified year.

    Returns
    =======
    :iso3166_df_selenium : pd.DataFrame
        converted pandas dataframe of all ISO 3166-2 changes for particular country/countries
        from official ISO website.
    """
    #create instance of chromedriver
    driver = create_driver()

    #raise error if invalid alpha-2 code input
    if not(alpha2.upper() in list(iso3166.countries_by_alpha2.keys())):
        raise ValueError("Invalid alpha-2 input: {}.".format(alpha2))
    
    #create session for input country's ISO section
    driver.get(iso_base_url + alpha2.upper())
    
    #pause for 3 seconds
    WebDriverWait(driver, 4) 

    #get page html source and create parsed BeautifulSoup object
    table_html = driver.page_source
    soup = BeautifulSoup(table_html, 'html.parser')

    #randomly scroll down the page 200-700px
    driver.execute_script('window.scrollTo(0, ' + random.choice(["200", "300", "400", "500", "600", "700"]) + ')') 
    
    #pause for 2.5 seconds
    time.sleep(2.5)

    #have to run below code again to get page html source and create parsed BeautifulSoup object, seems to be error in page loading time
    table_html = driver.page_source
    soup = BeautifulSoup(table_html, 'html.parser')

    #parse Changes section table on webpage, using the header of the section
    changes_html = ""   
    for h3 in soup.find_all('h3'):
        if (('change history of country code' in h3.text.lower()) or ('historique des modifications des codes de pays' in h3.text.lower())):
            changes_html = str(soup).split(str(h3))[1]
            break

    #create soup object from changes section, get html table 
    changes_table_soup = BeautifulSoup(changes_html, "lxml")
    changes_table = changes_table_soup.find('table')

    #convert html table into 2D array
    changes_table_converted = table_to_array(changes_table)

    #convert 2D array of updates into dataframe, fix columns, remove duplicate rows etc
    iso3166_df_selenium = parse_updates_table(changes_table_converted, year, year_range, less_than, greater_than)
    
    #delete chromedriver session
    driver.quit()
    
    return iso3166_df_selenium

def get_updates_df_wiki(alpha2, year=[], year_range=False, less_than=False, greater_than=False):
    """
    Pull all related ISO 3166-2 updates/changes for a given input country from the country's
    respective wiki page. Selenium is not a requirement for web scraping wiki pages. Convert 
    parsed html table, from the Changes/Updates Section into a pandas dataframe. 

    Parameters
    ==========
    :alpha2 : str/list
        single string of an alpha-2 ISO 3166-1 codes to get the latest ISO 3166-2 updates for.
    :year : array
        array/list of year(s). If not empty only the ISO 3166 updates for the selected
        year for a particular country will be returned. If empty then all years of 
        updates are returned.
    :year_range: bool
        set to True if a range of years are input into year parameter e.g "2002-2010" etc.
        Function will remove all rows in Dataframe that aren't in specified year range.
    :less_than: bool
        set to True if less than symbol is input into year parameter e.g "<2018" etc.
        Function will remove all rows in Dataframe that are greater than specified year.
    :greater_than: bool
        set to True if greater than symbol is input into year parameter e.g ">2005" etc.
        Function will remove all rows in Dataframe that are less than specified year.

    Returns
    =======
    :iso3166_df_wiki : pd.DataFrame
        converted pandas dataframe of all ISO 3166-2 changes for particular country/countries
        from respective wiki pages.
    """
    #get html content from wiki of ISO 3166 page, raise exception if status code != 200
    try:
        page = requests.get(wiki_base_url + alpha2, headers=USER_AGENT_HEADER)
        page.raise_for_status()
    except:
        raise requests.exceptions.HTTPError("Invalid alpha-2 country code for URL: {}.".format(wiki_base_url + alpha2))

    #convert html content into BS4 object
    soup = BeautifulSoup(page.content, "html.parser")

    #get Changes Section/Heading from soup 
    changesSection = soup.find("span", {"id": "Changes"})

    #skip to next iteration if no changes for ISO code found
    if (changesSection is None):
        return pd.DataFrame()

    #get table element in Changes Section 
    table = changesSection.findNext('table')
    
    #convert html table to 2D array 
    iso3166_table_wiki = table_to_array(table)

    #convert 2D array of updates into dataframe, fix columns, remove duplicate rows etc
    iso3166_df_wiki = parse_updates_table(iso3166_table_wiki, year, year_range, less_than, greater_than)

    #some wiki pages have multiple Changes/Updates table
    iso3166_table_2 = table.findNext('table', {"class": "wikitable"})

    #concatenate both updates table to 1 dataframe, if applicable 
    if (iso3166_table_2 != None):
        #convert secondary table into 2D array
        temp_iso3166_table = table_to_array(iso3166_table_2)
        #several tables have extra unwanted cols meaning we ignore those tables
        if ('former code' not in [col.lower() for col in temp_iso3166_table[0]] and 
            'in region' not in [col.lower() for col in temp_iso3166_table[0]] and 
            'before' not in [col.lower() for col in temp_iso3166_table[0]]): 
            temp_iso3166_df_wiki = parse_updates_table(temp_iso3166_table, year, year_range, less_than, greater_than)
            #concat two dataframes together
            iso3166_df_wiki = pd.concat([iso3166_df_wiki, temp_iso3166_df_wiki], axis=0)

    return iso3166_df_wiki

def parse_updates_table(iso3166_updates_table, year, year_range, less_than, greater_than):
    """
    Convert columns/headers using correct naming conventions, correct Date column into correct
    format, translate any unicode arrows in the text to normal arrow (->), fill any null rows. 
    Some listed updates are "corrected" at a later date after publication, to keep track
    of these corrections the "Corrected Date Issued" and "Corrected Date" columns are used but 
    later removed from the output dataframe. If year param not empty then remove any rows that 
    don't have specified year(s). If year range, less than or greater than parameters set to True 
    then get all updates from year range or all updates less than or all updates greater than a 
    year, respectively.

    Parameters
    ==========
    :iso3166_updates_table : list
        2D array updates/changes table from wiki page or official ISO website.
    :year : array
        array/list of year(s). If not empty only the ISO 3166 updates for the selected
        year for a particular country will be returned. If empty then all years of
        updates are returned.
    :year_range: bool
        set to True if a range of years are input into year parameter e.g "2002-2010" etc.
        Function will remove all rows in Dataframe that aren't in specified year range.
    :less_than: bool
        set to True if less than symbol is input into year parameter e.g "<2018" etc.
        Function will remove all rows in Dataframe that are greater than specified year.
    :greater_than: bool
        set to True if greater than symbol is input into year parameter e.g ">2005" etc.
        Function will remove all rows in Dataframe that are less than specified year.
    
    Returns
    =======
    :iso3166_df : pd.DataFrame
        converted pandas dataframe of all ISO 3166-2 changes for particular country/countries
        from respective wiki or ISO pages.
    """
    #raise error if input updates table isn't an array/list
    if not isinstance(iso3166_updates_table, list):
        raise TypeError("Input ISO 3166 updates table parameter must be a array/list, got {}.".format(type(iso3166_updates_table)))

    #raise runtime error if input table is 0 which occassionally happens when Selenium hasn't properly parsed data on ISO page
    if (len(iso3166_updates_table) == 0):
        raise RuntimeError("Runtime error that occurs when Selenium hasn't properly parsed ISO website, may need to rerun script again.")

    #update column names to correct naming conventions
    cols = correct_columns(iso3166_updates_table[0])

    #lambda function to translate any occurences of unicode arrow → to normal arrow ->
    correct_arrow_lambda = lambda table: [[elem.replace('→', '->') for elem in entry if isinstance(elem, str)] for entry in table]

    #translate unicode arrow → to normal arrow -> in table text
    iso3166_updates_table = correct_arrow_lambda(iso3166_updates_table)

    #convert 2D array into dataframe
    iso3166_df = pd.DataFrame(iso3166_updates_table[1:], columns=cols)

    def add_corrected_date(row):
        """ parse new date from row if date of changes has been "corrected", remove any full stops/punctation and whitespace. """
        if ("corrected" in row):
            return " (corrected " + row[row.index("corrected") + len("corrected"):].strip().replace(')', '').replace('.', '').replace(' ', '') + ")"
        else:
            return ""

    #set column if update has been "corrected" at a later date after publication, set to "" otherwise
    iso3166_df["Corrected Date Issued"] = iso3166_df["Date Issued"].apply(add_corrected_date)

    def corrected_date(row):
        """ if update has been "corrected" after publication, parse original date and temporarily remove new "corrected" date,
            remove any full stops/punctation and whitespace. """
        return re.sub("[(].*[)]", "", row).replace(' ', "").replace(".", '')

    #set Date Issued column to the original date of publication 
    iso3166_df["Date Issued"] = iso3166_df["Date Issued"].apply(corrected_date)

    def get_year(row):
        """ convert string date in rows of dataframe into yyyy-mm-dd data format from date object,
            parse "corrected" date if applicabale """
        if ("corrected" in row):
            return datetime.datetime.strptime(re.sub("[(].*[)]", "", row).replace(' ', "").replace(".", ''),'%Y-%m-%d').year
        else:
            return datetime.datetime.strptime(row, '%Y-%m-%d').year

    #drop rows of dataframe where Date Issued column isn't same as year parameter, if greater_than,
    #less_than or year_range bools set then drop any rows that don't meet condition
    if (year != []):
        #create temp year column to get year of updates from date column, convert to str
        iso3166_df['Year'] = iso3166_df["Date Issued"].apply(get_year)
        iso3166_df['Year'] = iso3166_df['Year'].astype(str)
        
        #drop all rows in dataframe that are less than input year
        if (greater_than):
            iso3166_df = iso3166_df.drop(iso3166_df[iso3166_df.Year < year[0]].index)
        #drop all rows in dataframe that are greater than or equal to input year
        elif (less_than):
            iso3166_df = iso3166_df.drop(iso3166_df[iso3166_df.Year >= year[0]].index)
        #drop all rows in dataframe that are not within input year range
        elif (year_range):
            iso3166_df = iso3166_df.drop(iso3166_df[iso3166_df.Year < year[0]].index)
            iso3166_df = iso3166_df.drop(iso3166_df[iso3166_df.Year > year[1]].index)
        else:
            #drop all rows in dataframe that aren't equal to year/list of years in year parameter
            for year_ in year:
                iso3166_df = iso3166_df.drop(iso3166_df[iso3166_df.Year != year_].index)

        #drop Year column
        iso3166_df = iso3166_df.drop('Year', axis=1)

    #add below columns if not present so all dataframes follow same format
    if ("Edition/Newsletter" not in iso3166_df):
        iso3166_df["Edition/Newsletter"] = ""
    if ("Code/Subdivision Change" not in iso3166_df):
        iso3166_df["Code/Subdivision Change"] = ""

    #set Edition/Newsletter to OBP if no value/empty string
    if ((iso3166_df["Edition/Newsletter"] == "").any()):
        iso3166_df["Edition/Newsletter"] = iso3166_df["Edition/Newsletter"].replace('',
            "Online Browsing Platform (OBP).", regex=True)

    #seperate 'Browsing' and 'Platform' string if they are concatenated in column
    iso3166_df["Edition/Newsletter"] = iso3166_df["Edition/Newsletter"].str.replace('BrowsingPlatform', "Browsing Platform")
        
    def remove_doublespacing(row):
        """ remove double spacing from string. """
        return re.sub(' +', ' ', row)

    #replace all null/nan with empty string
    iso3166_df.fillna("", inplace=True)

    #remove any double spacing from all columns, except Date Issued
    iso3166_df['Code/Subdivision Change'] = iso3166_df['Code/Subdivision Change'].apply(remove_doublespacing)
    iso3166_df['Description of Change in Newsletter'] = iso3166_df['Description of Change in Newsletter'].apply(remove_doublespacing)
    iso3166_df['Edition/Newsletter'] = iso3166_df['Edition/Newsletter'].apply(remove_doublespacing)

    #drop any rows that have no listed changes in them
    iso3166_df.drop(iso3166_df[(iso3166_df['Code/Subdivision Change'] == "") & (iso3166_df['Description of Change in Newsletter'] == "")].index, inplace=True)

    #reindex/reorder columns in dataframe
    iso3166_df = iso3166_df.reindex(columns=['Date Issued', 'Corrected Date Issued', 'Edition/Newsletter',
        'Code/Subdivision Change', 'Description of Change in Newsletter'])

    return iso3166_df

def correct_columns(cols):
    """ 
    Update column names so all dataframes follow the column format of: ["Date Issued", 
    "Edition/Newsletter", "Code/Subdivision Change", "Description of Change in Newsletter"].

    Parameters
    ==========
    :cols : list
        list of column names from header of parsed Changes table on wiki.
    
    Returns
    =======
    :cols : list
        list of columns updated to correct naming conventions. 
    """
    if ("Newsletter" in cols):
        cols = list(map(lambda x: x.replace("Newsletter", 'Edition/Newsletter'), cols))
    cols = list(map(lambda x: x.replace("Newsletter/OBP", 'Edition/Newsletter'), cols))
    cols = list(map(lambda x: x.replace("Source", 'Edition/Newsletter'), cols))
    cols = list(map(lambda x: x.replace("Date issued", 'Date Issued'), cols))
    cols = list(map(lambda x: x.replace("Effective date of change", 'Date Issued'), cols))
    cols = list(map(lambda x: x.replace("Effective date", 'Date Issued'), cols))
    cols = list(map(lambda x: x.replace("Short description of change (en)", 'Description of Change in Newsletter'), cols))
    cols = list(map(lambda x: x.replace("Short description of change", 'Description of Change in Newsletter'), cols))
    cols = list(map(lambda x: x.replace("Description of change", 'Description of Change in Newsletter'), cols)) #**
    cols = list(map(lambda x: x.replace("Changes made", 'Description of Change in Newsletter'), cols))
    cols = list(map(lambda x: x.replace("Code/Subdivision change", 'Code/Subdivision Change'), cols))
    cols = list(map(lambda x: x.replace("Description of change in newsletter", 'Description of Change in Newsletter'), cols))
    cols = list(map(lambda x: x.replace("Description of Change in Newsletter in newsletter", 'Description of Change in Newsletter'), cols))

    return cols     

def table_to_array(table_tag):
    """
    Convert html table into 2D array. Much of the function code was inspired from [1] which 
    provides an optimal and working solution for handling tables with different rowspans & 
    colspans. 

    Parameters
    ==========
    :table_tag : bs4.element.Tag
      BS4 Tag object of table element.
    
    Returns
    =======
    :table : tuple
      tuple of parsed data from html table in Changes section of ISO 3166 wiki.
    
    References
    ==========
    [1]: https://stackoverflow.com/questions/48393253/how-to-parse-table-with-rowspan-and-colspan
    """
    #if invalid table tag input return empty array
    if (table_tag is None):
        return []
    
    #raise type error if input parameter not a BS4 tag type
    if not isinstance(table_tag, Tag):
        raise TypeError("Input table object must be of type bs4.element.Tag, got {}.".format(type(table_tag)))

    rowspans = []  #track pending rowspans
    rows = table_tag.find_all('tr') #all table rows

    #count columns (including spanned).
    #add active rowspans from preceding rows
    #we *ignore* the colspan value on the last cell, to prevent
    #creating 'phantom' columns with no actual cells, only extended
    #colspans. This is achieved by hardcoding the last cell width as 1. 
    #a colspan of 0 means “fill until the end” but can really only apply
    #to the last cell; ignore it elsewhere. 
    colcount = 0
    for r, row in enumerate(rows):
        cells = row.find_all(['td', 'th'], recursive=False)
        colcount = max(
            colcount,
            sum(int(c.get('colspan', 1)) or 1 for c in cells[:-1]) + len(cells[-1:]) + len(rowspans))
        # update rowspan bookkeeping; 0 is a span to the bottom. 
        rowspans += [int(c.get('rowspan', 1)) or len(rows) - r for c in cells]
        rowspans = [s - 1 for s in rowspans if s > 1]

    #it doesn't matter if there are still rowspan numbers 'active'; no extra
    #rows to show in the table means the larger than 1 rowspan numbers in the
    #last table row are ignored.

    #build an empty matrix for all possible cells
    table = [[None] * colcount for row in rows]

    #fill matrix from row data
    rowspans = {}  #track pending rowspans, column number mapping to count
    for row, row_elem in enumerate(rows):
        span_offset = 0  #how many columns are skipped due to row and colspans 
        for col, cell in enumerate(row_elem.find_all(['td', 'th'], recursive=False)):
            #adjust for preceding row and colspans
            col += span_offset
            while rowspans.get(col, 0):
                span_offset += 1
                col += 1

            #fill table data
            rowspan = rowspans[col] = int(cell.get('rowspan', 1)) or len(rows) - row
            colspan = int(cell.get('colspan', 1)) or colcount - col
            #next column is offset by the colspan
            span_offset += colspan - 1

            if (cell.get_text() == "\n"):
                # if table cell is a newline character set to empty string
                value = ""
            elif ("<br/>" in str(cell)):
                #if text has breakpoint (<br>), replace with space
                value = cell.get_text(separator=" ").strip()
            else:
                #remove empty space from start or end of cell text
                value = cell.get_text().strip()

            #remove any double spacing between words
            value = re.sub(' +', ' ', value)

            #remove any double spacing after commas, colons, semicolons or &nhbsp; unicode in cell text
            value = value.replace(" ,", ",").replace(" :", ":").replace(" ;", ";").replace(u'\xa0', ' ').replace(' )', ')').replace('( ', '()')

            #add href link to newsletter rows if applicable - ignore any wiki links            
            if not (cell.find('a') is None):
                if not (cell.find('a')['href'].startswith('/wiki/')):
                    value = value + " (" + cell.find('a')['href'] + ')'

            #add full-stop to end of data rows, if applicable
            if (row != 0 and value != ""):
                if (value[-1] != "."):
                    value = value + "."

            for drow, dcol in product(range(rowspan), range(colspan)):
                try:
                    table[row + drow][col + dcol] = value
                    rowspans[col + dcol] = rowspan
                except IndexError:
                    #rowspan or colspan outside the confines of the table
                    pass
        
        #update rowspan bookkeeping
        rowspans = {c: s - 1 for c, s in rowspans.items() if s > 1}

    #iterate through converted table, removing any newline characters
    for row in range(0, len(table)):
        for col in range(0, len(table[row])):
            if not (table[row][col] is None):
                table[row][col] = table[row][col].replace('\n', "")

    return table

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Get latest changes/updates for all countries in the ISO 3166-1/3166-2 standards.')
    parser.add_argument('-alpha2', '--alpha2', type=str, required=False, default="", 
        help='2 letter alpha-2 code(s) of ISO 3166-1 countries to check for updates.')
    parser.add_argument('-year', '--year', type=str, required=False, default="", 
        help='Selected year(s) to check for updates, can also be a year range or greater than/less than specific year.')
    parser.add_argument('-export_filename', '--export_filename', type=str, required=False, default="iso3166-updates", 
        help='Filename for exported ISO 3166 updates CSV and JSON files.')
    parser.add_argument('-export_folder', '--export_folder', type=str, required=False, default="test-iso3166-updates", 
        help='Folder where to store exported ISO files.')
    parser.add_argument('-export_json', '--export_json', required=False, action=argparse.BooleanOptionalAction, default=1,
        help='Whether to export all found updates to json.')
    parser.add_argument('-export_csv', '--export_csv', required=False, action=argparse.BooleanOptionalAction, default=0,
        help='Whether to export all found updates to csv files in export folder.')
    parser.add_argument('-concat_updates', '--concat_updates', required=False, action=argparse.BooleanOptionalAction, default=1,
        help='Whether to concatenate updates of individual countrys into the same json or csv files or to individual files.')
    parser.add_argument('-verbose', '--verbose', type=int, required=False, action=argparse.BooleanOptionalAction, default=1, 
        help='Set to 1 to print out progress of updates function, 0 will not print progress.')
    parser.add_argument('-use_selenium', '--use_selenium', type=int, required=False, action=argparse.BooleanOptionalAction, default=1, 
        help='Gather updates from official ISO website for each country using Selenium package, if False just gather data from wiki data source.')
    
    #parse input args
    args = parser.parse_args()
    alpha2_codes = args.alpha2
    year = args.year
    export_filename = args.export_filename
    export_folder = args.export_folder
    concat_updates = args.concat_updates
    export_json = args.export_json
    export_csv = args.export_csv
    verbose = args.verbose
    use_selenium = args.use_selenium

    #output ISO 3166 updates/changes for selected alpha-2 code(s) and year(s)
    get_updates(alpha2_codes, year, export_filename, export_folder, 
        concat_updates, export_json, export_csv, verbose, use_selenium)