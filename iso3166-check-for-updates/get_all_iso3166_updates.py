from itertools import product
import pandas as pd
import iso3166
from bs4 import BeautifulSoup, Tag
import re
import time
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait 
import random
from importlib import metadata
import getpass
import random
import requests
from tqdm import tqdm
import pandas as pd
pd.options.mode.chained_assignment = None

#get current software version
__version__ = metadata.metadata('iso3166_updates')['version']

#initalise User-agent header for requests library 
USER_AGENT_HEADER = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(__version__,
                                       'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}

#base URL for ISO3 166-2 wiki and ISO website
wiki_base_url = "https://en.wikipedia.org/wiki/ISO_3166-2:"
iso_base_url = "https://www.iso.org/obp/ui/#iso:code:3166:"

#path to chromedriver executable
chromedriver_executable_path = '/usr/local/bin/chromedriver'

def create_driver():
    """
    Create instance of Selenium Chromedriver for each country's individual page on the 
    official ISO website. The site requires a session to be created and Javascript to
    be run, therefore the page's data cannot be directly webscraped. For some countries 
    their ISO page contains extra data not on the country's wiki page. 

    Parameters
    ==========
    None

    Returns
    =======
    :driver: selenium.webdriver.chrome.webdriver.WebDriver
        instance of Python Selenium using chromedriver webdriver.
    
    References
    ==========
    [1]: https://chromedriver.chromium.org/getting-started
    [2]: https://www.geeksforgeeks.org/how-to-install-selenium-in-python/
    [3]: https://www.scrapingbee.com/webscraping-questions/selenium/chromedriver-executable-needs-to-be-in-path/
    [4]: https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json
    """
    #verify Chromedriver is found on path, raise exception if not
    if not (os.path.isfile(chromedriver_executable_path)):
      raise WebDriverException("Chromedriver not found at path: " + chromedriver_executable_path + \
                               ". Verify it's installed in path by executing 'ls /usr/bin/' or 'ls /usr/lib'.")

    #create instance of Service class and get executable path of chromedriver
    #execute "which chromedriver" to see path where it is installed
    # service = Service(executable_path='/usr/lib/chromium-browser/chromedriver')
    # service = Service(executable_path='/usr/bin/chromium-browser/chromedriver')
    service = Service(executable_path=chromedriver_executable_path)

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
    #when testing locally need to specify the binary location of Google Chrome: find / -type d -name "*Chrome.app"
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

def get_updates(alpha_codes: str="", year: str="", export_filename: str="iso3166-updates", export_folder: str="iso3166-updates-output",
        concat_updates: bool=True, export_json: bool=True, export_csv: bool=False, verbose: bool=True, use_selenium: bool=True) -> dict:
    """
    Get all listed changes/updates to a country's ISO 3166-2 subdivision codes/names. The two data
    sources for the updates data are via the "Changes" section on its wiki page as well as any listed
    updates on the official ISO website. A country's wiki page and section on ISO website follow the
    convention https://en.wikipedia.org/wiki/ISO_3166-2:XX and https://www.iso.org/obp/ui#iso:code:3166:XX,
    respectively, where XX is the 2 letter alpha-2 code for a country listed in the ISO 3166-1. The
    "Changes" section lists updates or changes to any ISO 3166-2 codes, including historical changes,
    according to the ISO newsletters which were released up until July 2013 but now are communicated
    via their online catalogue/Online Browsing Platform (OBP), or via a database, which usually costs
    money to subscribe to. The ISO newsletters are not easily discoverable and accessible
    online and may require a subscription to the ISO 3166-2 database
    (https://www.iso.org/iso/updating_information.pdf), with the ISO 3166 dataset itself
    costing around $330!

    Some countries have missing and or not up-to-date updates data on their wiki pages, so the
    country data from the official ISO website is also gathered using Selenium Chromedriver, prior
    to being scraped using BeautifulSoup, as the page requires Javascript to be run on page load.
    Some country updates mention a change to their remarks which are additional notes/supplementary
    info about changes to a country. These remarks are appended to the country description from
    the ISO page.

    The earliest available changes are from the year 2000 and the latest changes are from 2024.

    The updates data from the wiki page and ISO website are converted to a DataFrame with the
    columns: Code/Subdivision Change and Description of Change, Date Issued and Edition/Newsletter.
    These are concatenated before being exported to a CSV and or JSON for further analysis. You
    can also get the updates from a particular year, list of years, year range or updates greater
    than or less than a specified year, using the year parameter. All of the updates are ordered
    alphabetically by their 2 letter ISO 3166-1 country code.

    Parameters
    ==========
    :alpha_codes: str (default="")
        single string or comma separated list of ISO 3166-1 alpha-2, alpha-3 or numeric country codes,
        to get the latest ISO 3166 updates from. Any alpha-3 or numeric codes input are converted to their
        alpha-2 equivalent. If no value passed into param then all updates for all ISO 3166-1 countries are retrieved.
    :year: str (default="")
        single string or comma separated list of 1 or more years to get the specific ISO 3166 updates from,
        per country. By default the year param will be empty meaning all changes/updates for all years
        will be retrieved. You can also pass in a year range (e.g 2010-2015) or a year to get all updates
        less than or greater than that specified year (e.g >2007, <2021).
    :export_filename: str (default="iso3166-updates")
        filename for JSON and CSV output files of inputted country's ISO 3166 updates.
    :export_folder: str (default="iso3166-updates-output")
        folder name to store all csv and json outputs for all country's ISO 3166 updates.
    :concat_updates: bool (default=True)
        if multiple alpha codes input, concatenate updates into one JSON and or CSV file
        (concat_updates=True) or into separately named files in export folder
        (concat_updates=False). By default all country's updates will be compiled into the
        same file.
    :export_json: bool (default=True)
        export all ISO 3166 updates for inputted countries into json format in export folder.
    :export_csv: bool (default=False)
        export all ISO 3166 updates for inputted countries into csv format in export folder.
    :verbose: bool (default=False)
        Set to 1 to print out progress of updates functionality, 0 will not print progress.
    :use_selenium: bool (default=True)
        Gather all data for each country from its official page on the ISO website which
        requires Python Selenium and Chromedriver. If False then just use country data
        from its wiki page.

    Returns
    =======
    :all_iso3166_updates: dict
        dictionary of all found ISO 3166 updates from user's inputted alpha codes and or year
        parameter values.
    """
    year_range = False
    greater_than = False
    less_than = False

    def convert_to_alpha2(alpha_code: str):
        """
        Auxillary function that converts an ISO 3166 country's 3 letter alpha-3
        or numeric code into its 2 letter alpha-2 counterpart.

        Parameters
        ==========
        :alpha_code: str
            3 letter ISO 3166-1 alpha-3 or numeric country code.

        Returns
        =======
        :iso3166.countries_by_alpha3[alpha3_code].alpha2: str
            2 letter ISO 3166 alpha-2 country code.
        """
        if (alpha_code.isdigit()):
            #return error if numeric code not found
            if not (alpha_code in list(iso3166.countries_by_numeric.keys())):
                return None
            else:
                #use iso3166 package to find corresponding alpha-2 code from its numeric code
                return iso3166.countries_by_numeric[alpha_code].alpha2

        #return error if 3 letter alpha-3 code not found
        if not (alpha_code in list(iso3166.countries_by_alpha3.keys())):
            return None
        else:
            #use iso3166 package to find corresponding alpha-2 code from its alpha-3 code
            return iso3166.countries_by_alpha3[alpha_code].alpha2

    #raise error if input alpha codes param is not a str
    if not (isinstance(alpha_codes, str)):
      raise TypeError(f"Expected input alpha_codes parameter to be a string, got {type(alpha_codes)}.")

    #split multiple alpha codes into list, remove any whitespace and empty strings
    alpha_codes = alpha_codes.replace(' ', '').upper().split(',')
    alpha_codes = list(filter(None, alpha_codes))

    #var to keep track of original alpha-2 and year parameter inputs
    input_alpha_codes = alpha_codes

    #parse input alpha_codes parameter, use all alpha-2 codes if parameter not set
    if (alpha_codes == []):
        #use list of all 2 letter alpha-2 codes, according to ISO 3166-1
        alpha_codes = sorted(list(iso3166.countries_by_alpha2.keys()))
    else:
        #iterate over all codes, checking they're valid, convert alpha-3 to alpha-2 if applicable
        for code in range(0, len(alpha_codes)):

            #convert 3 letter alpha-3 or numeric code into its 2 letter alpha-2 counterpart
            if len(alpha_codes[code]) == 3:
                alpha_codes[code] = convert_to_alpha2(alpha_codes[code])

            #raise error if invalid alpha-2 code found
            if (alpha_codes[code] not in list(iso3166.countries_by_alpha2.keys())):
                raise ValueError("Invalid alpha country code input: {}.".format(alpha_codes[code]))

    #uppercase, remove duplicate codes and sort into alphabetical order
    alpha_codes = [code.upper() for code in alpha_codes]
    alpha_codes = list(set(alpha_codes))
    alpha_codes.sort()

    #remove XK (Kosovo) from list if applicable
    if ("XK" in alpha_codes):
        alpha_codes.remove("XK")

    #split multiple years into list, remove any whitespace
    year = year.replace(' ', '').split(',')

    #a '-' separating 2 years implies a year range of sought country updates
    #a ',' separating 2 years implies a list of years
    #a '>' before year means get all country updates greater than or equal to specified year
    #a '<' before year means get all country updates less than specified year
    if (year != ['']):
        if ('-' in year[0]):
            year_range = True
            year = year[0].split('-')
            #if year range years are wrong way around then swap them
            if (year[0] > year[1]):
                year[0], year[1] = year[1], year[0]
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
            #split years into comma separated list of multiple years if multiple years are input
            year = year[0].split(',')
    #validate each year's format using regex
    for year_ in year:
        #skip to next iteration if < or > symbol
        if (year_ == '<' or year_ == '>' or year_ == '-' or year_ == ""):
            continue
        #raise error if invalid year input
        if not (bool(re.match(r"^1[0-9][0-9][0-9]$|^2[0-9][0-9][0-9]$", year_))):
            raise ValueError("Invalid year input, must be a year >= 1999, got {}.".format(year_))

    #object to store all country updates/changes
    all_iso3166_updates = {}

    #temp filename export var
    temp_filename = os.path.splitext(export_filename)[0]

    ###Â Get JSON and CSV filenames based on alpha-2 and year input parameters - concat_updates=True ###

    #append 2 letter alpha-2 codes to export filenames if less than 10 input, append year as well if applicable
    if (len(alpha_codes) <= 10 and not (any(code in export_filename for code in alpha_codes)) and \
        concat_updates==True and (year != ['']) and len(year) <= 10 and not (greater_than or less_than or year_range)):

        #separate alpha-2 codes and years into comma separated lists
        alpha2_str = ','.join(alpha_codes)
        year_str = ','.join(year)

        #append list of alpha-2 codes and or years to json and csv filenames
        temp_filename = temp_filename + "-" + alpha2_str + "_" + year_str

    else:
        #append 2 letter alpha-2 codes to export filename, year parameter not appended
        if (len(alpha_codes) <= 10 and not (any(code in export_filename for code in alpha_codes)) \
                and (year == ['']) and concat_updates==True):

            #separate alpha-2 codes into comma separated list
            alpha2_str = ','.join(alpha_codes)

            #append list of alpha-2 codes to json and csv filenames
            temp_filename = temp_filename + "-" + alpha2_str

        #append greater than/less than/year range symbols to filenames
        elif ((greater_than or less_than or year_range) and concat_updates==True):

            #separate alpha-2 codes and years into comma separated lists
            alpha2_str = ','.join(alpha_codes)
            year_str = ','.join(year)

            #append alpha-2 codes to filename if less than 10 input
            if (len(alpha_codes) <= 10):
                temp_filename = temp_filename + "-" + alpha2_str

            #append list of years and gt/lt/year range symbols to json and csv filenames, if applicable
            if (greater_than):
                temp_filename = temp_filename + "_>" + year_str
            elif (less_than):
                temp_filename = temp_filename + "_<" + year_str
            elif (year_range):
                temp_filename = temp_filename + "_" + year[0] + "-" + year[1]

        #append year param to filename if alpha-2 input param is empty
        elif ((input_alpha_codes == [] or input_alpha_codes == ['']) and (year != [''] and year != ['']) and \
              concat_updates==True and len(year) <= 10 and not (greater_than or less_than or year_range)):

            #separate years into comma separated list
            year_str = ','.join(year)

            #append list of years to json and csv filenames
            temp_filename = temp_filename + "-" + year_str

    #file export filename
    export_filename_concat_updates = temp_filename

    #dataframe for csv export
    csv_iso3166_df = pd.DataFrame()

    #start elapsed time counter
    start = time.time()

    #if less than 5 alpha-2 codes input then don't display progress bar, or print elapsed time
    tqdm_disable = False
    if (len(alpha_codes) < 5):
        tqdm_disable = True

    #iterate over all input ISO 3166-1 country codes
    for alpha2 in tqdm(alpha_codes, ncols=50, disable=tqdm_disable):

        #skip to next iteration if alpha-2 not valid
        if (alpha2 not in list(iso3166.countries_by_alpha2.keys())):
            continue

        #print out progress if verbose set to true
        if (verbose):
            if (tqdm_disable):
                print(f"ISO 3166-1 Code: {alpha2} ({wiki_base_url + alpha2}, {iso_base_url + alpha2}).")
            else:
                print(f" - {iso3166.countries_by_alpha2[alpha2].name.title()} ({alpha2})".format(alpha2))

        all_iso3166_updates[alpha2] = {}

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

            def is_corrected_date(row: pd.Series):
                """ return true/false if row in dataframes has a "corrected" publication date in Date Issued col. """
                return True if ("corrected" in row) else False

            #column tracks if ISO 3166 updates have a "corrected" publication date
            iso3166_df["Corrected Date"] = iso3166_df["Corrected Date Issued"].apply(is_corrected_date)

            #temporary dataframe to track row with "corrected" publication date
            corrected_date_iso3166_df = iso3166_df[iso3166_df["Corrected Date"] == True]

            #if applicable, merge temporary df with main df, reset index & override original df with "corrected" publication date row
            if not (corrected_date_iso3166_df.empty):
              iso3166_df.set_index('Date Issued', inplace=True)
              iso3166_df.update(corrected_date_iso3166_df.set_index('Date Issued'), overwrite=True)
              iso3166_df.reset_index(inplace=True)

            #reindex/reorder columns in dataframe
            iso3166_df = iso3166_df.reindex(columns=['Code/Subdivision Change', 'Description of Change', 
                                                    'Date Issued', 'Corrected Date Issued', 'Edition/Newsletter'])
            
            #convert date column to datetime object
            iso3166_df['Date Issued'] = pd.to_datetime(iso3166_df["Date Issued"])

            #sort and order by date, newest to oldest
            iso3166_df = iso3166_df.sort_values(by=['Date Issued'], ascending=False)

            #convert date column back to string
            iso3166_df['Date Issued'] = iso3166_df['Date Issued'].astype(str)

            #drop duplicates by Date Issued column
            iso3166_df = iso3166_df.drop_duplicates("Date Issued")

            #append "corrected" date to Date Issued column, if applicable
            iso3166_df['Date Issued'] = iso3166_df['Date Issued'] + iso3166_df['Corrected Date Issued']

            #drop unneeded date columns
            iso3166_df.drop(["Corrected Date Issued"], axis=1, inplace=True)

            #swap data in Code/Subdivision change & Description of change... columns if Code/Subdivision column has no value but the latter does
            for index, row in iso3166_df.iterrows():
                if (row["Code/Subdivision Change"] == ""):
                    iso3166_df.at[index, "Code/Subdivision Change"] = row["Description of Change"]
                    iso3166_df.at[index, "Description of Change"] = ""

            #create dataframe for csv export with updates concatenated in same file
            if (export_csv and concat_updates):
                if len(alpha_codes) > 1:
                    #insert Country Code primary key column in dataframe if more than 1 country exported
                    iso3166_df.insert(0, "Country Code", alpha2, True)
                    #concatenate original dataframe with csv dataframe with new primary key column
                    csv_iso3166_df = pd.concat([iso3166_df, csv_iso3166_df], axis=0)
                    #drop Country Code column from original dataframe
                    iso3166_df.drop('Country Code', axis=1, inplace=True)
                else:
                    csv_iso3166_df = iso3166_df

            #add ISO updates to object of all ISO 3166 updates, convert to json
            all_iso3166_updates[alpha2] = json.loads(iso3166_df.to_json(orient='records'))

    #end elapsed time counter and calculate
    end = time.time()
    elapsed = end - start

    #create output folder if doesn't exist and files are set to be exported (export_csv, export_json)
    if (export_csv or export_json) and not (os.path.isdir(export_folder)):
        os.mkdir(export_folder)

    #auxillary function to remove all empty nested dicts within object
    def _del(_d: dict):
        return {a:_del(b) if isinstance(b, dict) else b for a, b in _d.items() if b and not a.startswith('_')}

    #remove any empty nested updates dict if gathering all country updates, keep empty dicts if list of alpha-2 codes input
    if (year != [''] and input_alpha_codes == []):
        all_iso3166_updates = _del(all_iso3166_updates)

    #temp filename export var
    temp_filename = os.path.splitext(export_filename)[0]

    #export all ISO 3166 updates to json, store in export folder dir
    if (export_json):
        all_iso3166_updates_json = all_iso3166_updates
        #checking if all_iso3166_updates object isn't empty
        if (all_iso3166_updates_json):
            #if singular country code input and it's contents are empty, set to empty dict
            if (len(alpha_codes) == 1 and not (any(all_iso3166_updates_json.values()))):
                all_iso3166_updates_json = {}
            if (concat_updates):
                #export updates into the same json
                with open(os.path.join(export_folder, os.path.splitext(export_filename_concat_updates)[0] + ".json"), "w") as write_file:
                    json.dump(all_iso3166_updates_json, write_file, indent=4, ensure_ascii=False)
            else:
                #separate country updates into individual json files
                for update in all_iso3166_updates_json:
                    #append alpha-2 codes and list of years or gt/lt/range symbols, if applicable, to separate exported json files
                    if (year != ['']):
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

                    #export updates object to separate json files
                    with open(os.path.join(export_folder, export_filename_no_concat_updates), "w") as write_file:
                        json.dump(all_iso3166_updates_json[update], write_file, indent=4, ensure_ascii=False)

            #if verbose flag set, print export completion message
            if (verbose):
                print("\nAll ISO 3166 updates exported to folder {}.".format(export_folder))

    #export all ISO 3166 updates to csv, store in export folder dir
    if (export_csv):
        #checking if all_iso3166_updates object isn't empty
        if (all_iso3166_updates):
            #validate all_iso3166_updates object contains at least one non-empty dict, don't export if all empty dicts
            if (any(all_iso3166_updates.values())):
                if (concat_updates):
                    #append Country Code column if more than one country input
                    if len(alpha_codes) > 1:
                        #sort dataframe alphabetically using country code column
                        csv_iso3166_df.sort_values('Country Code', inplace=True)
                    #export updates object to same concatenated csv file
                    csv_iso3166_df.to_csv(os.path.join(export_folder, os.path.splitext(export_filename_concat_updates)[0] + ".csv"), index=False)
                else:
                    #separate country updates into individual csv files
                    for update in all_iso3166_updates:
                        #convert updates object into dataframe
                        temp_updates = pd.DataFrame(all_iso3166_updates[update])
                        #skip to next updates object if dataframe is empty
                        if (temp_updates.empty):
                            continue
                        #append alpha-2 codes and list of years or gt/lt/range symbol, if applicable, to separate exported csv files
                        if (year != ['']):
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

                        #export updates object to separate csv files
                        temp_updates.to_csv(os.path.join(export_folder, export_filename_no_concat_updates), index=False)

    if (verbose):
        print("Total elapsed time for executing script: {} minutes.".format(round(elapsed/60, 2)))

    return all_iso3166_updates

def get_updates_df_selenium(alpha2: str, year: list=[], year_range: bool=False, less_than: bool=False, greater_than: bool=False) -> pd.DataFrame:
    """
    Pull all related ISO 3166 updates/changes for a given input country from the official ISO
    website. The Selenium Chromedriver tool is utilised prior to the BS4 web scraper as JavaScript
    has to run on the site to get the data. Various random steps are implemented during execution
    of the Chromedriver to avoid requests being blocked. The changes section for each country is
    parsed and converted into a 2D table and then a DataFrame.

    Parameters
    ==========
    :alpha2: str
        single string of an alpha-2 ISO 3166-1 code to get the latest ISO 3166 updates for.
    :year: list
        array/list of year(s). If not empty only the ISO 3166 updates for the selected
        year for a particular country will be returned. If empty then all years of
        updates are returned.
    :year_range: bool
        set to True if a range of years are input into year parameter e.g "2002-2010" etc.
        Function will remove all rows in Dataframe that aren't in specified year range.
    :less_than: bool
        set to True if less than symbol is input into year parameter e.g "<2018" etc.
        Function will remove all rows in Dataframe that are greater than or equal to
        specified year.
    :greater_than: bool
        set to True if greater than symbol is input into year parameter e.g ">2005" etc.
        Function will remove all rows in Dataframe that are less than specified year.

    Returns
    =======
    :iso3166_df_selenium: pd.DataFrame
        converted pandas dataframe of all ISO 3166 changes for particular country/countries
        from official ISO website.
    """
    #counter that determines the max number of retries for the Selenium function, retry required if an error occurs when accessing the html of a country's ISO page
    recursive_selenium_count = 3

    #initialise dataframe to hold updates data obtained from ISO pages
    iso3166_df_selenium = pd.DataFrame()

    #raise error if invalid alpha-2 code input
    if not(alpha2.upper() in list(iso3166.countries_by_alpha2.keys())):
        raise ValueError(f"Invalid alpha-2 input: {alpha2}.")

    #parse Changes section table on webpage, using the header of the section
    changes_html = ""

    while (recursive_selenium_count != 0 and changes_html == ""):

      #create instance of chromedriver
      driver = create_driver()

      #create session for input country's ISO section
      driver.get(iso_base_url + alpha2.upper())

      #pause for 4 seconds
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

      for h3 in soup.find_all('h3'):
          if (('change history of country code' in h3.text.lower()) or ('historique des modifications des codes de pays' in h3.text.lower())):
              changes_html = str(soup).split(str(h3))[1]
              break

      #break to next while loop iteration if Changes html table data is blank
      if (changes_html == ""):
          break

      #create soup object from changes section, get html table
      changes_table_soup = BeautifulSoup(changes_html, "lxml")
      changes_table = changes_table_soup.find('table')

      #convert html table into 2D array
      changes_table_converted = table_to_array(changes_table)

      #add remarks table html, if applicable
      country_summary_table = soup.find(class_='core-view-summary')

      #convert 2D array of updates into dataframe, fix columns, remove duplicate rows etc
      iso3166_df_selenium = parse_updates_table(alpha2, changes_table_converted, year, year_range, less_than, greater_than)

      #get any listed remarks from ISO page, if applicable
      iso3166_df_selenium = parse_remarks_table(iso3166_df_selenium, country_summary_table)

      #decrement the recursive counter
      recursive_selenium_count-=1

    #raise error if max number of recursive tries have been done
    if (recursive_selenium_count == 0):
        driver.quit()
        raise RuntimeError("Runtime error that occurs when Selenium hasn't properly parsed ISO website after 3 attempts, may need to rerun script again.")

    #delete chromedriver session
    driver.quit()

    return iso3166_df_selenium

def get_updates_df_wiki(alpha2: str, year: list=[], year_range: bool=False, less_than: bool=False, greater_than: bool=False) -> pd.DataFrame:
    """
    Pull all related ISO 3166 updates/changes for a given input country from the country's
    respective wiki page. Selenium is not a requirement for web scraping wiki pages. Convert
    parsed html table, from the Changes/Updates Section into a pandas dataframe.

    Parameters
    ==========
    :alpha2: str
        single string of an alpha-2 ISO 3166-1 code to get the latest ISO 3166 updates for.
    :year: array
        array/list of year(s). Only the ISO 3166 updates for the selected year for a particular
        country will be returned. If empty then all years of updates are returned.
    :year_range: bool
        set to True if a range of years are input into year parameter e.g "2002-2010" etc.
        Function will remove all rows in Dataframe that aren't in specified year range.
    :less_than: bool
        set to True if less than symbol is input into year parameter e.g "<2018" etc.
        Function will remove all rows in Dataframe that are greater than or equal to
        specified year.
    :greater_than: bool
        set to True if greater than symbol is input into year parameter e.g ">2005" etc.
        Function will remove all rows in Dataframe that are less than specified year.

    Returns
    =======
    :iso3166_df_wiki: pd.DataFrame
        converted pandas dataframe of all ISO 3166 changes for particular country/countries
        from respective wiki pages.
    """
    #get html content from wiki of ISO 3166 page, raise exception if status code != 200
    try:
        page = requests.get(wiki_base_url + alpha2, headers=USER_AGENT_HEADER)
        page.raise_for_status()
    except:
        raise requests.exceptions.HTTPError(f"Invalid alpha-2 country code for URL: {wiki_base_url + alpha2}.")

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
    iso3166_df_wiki = parse_updates_table(alpha2, iso3166_table_wiki, year, year_range, less_than, greater_than)

    #some wiki pages have multiple Changes/Updates tables
    iso3166_table_2 = table.findNext('table', {"class": "wikitable"})

    #concatenate both updates table to 1 dataframe, if applicable
    if (iso3166_table_2 != None):
        #convert secondary table into 2D array
        temp_iso3166_table = table_to_array(iso3166_table_2)
        #several tables have extra unwanted cols meaning we ignore those tables
        if ('former code' not in [col.lower() for col in temp_iso3166_table[0]] and
            'in region' not in [col.lower() for col in temp_iso3166_table[0]] and
            'before' not in [col.lower() for col in temp_iso3166_table[0]]):
            temp_iso3166_df_wiki = parse_updates_table(alpha2, temp_iso3166_table, year, year_range, less_than, greater_than)
            #concat two dataframes together
            iso3166_df_wiki = pd.concat([iso3166_df_wiki, temp_iso3166_df_wiki], axis=0)

    return iso3166_df_wiki

def parse_remarks_table(iso3166_df_: pd.DataFrame, country_summary_table) -> pd.DataFrame:
    """
    Parsing country summary table on ISO page which contains a selection of info
    about the country. Here we are just parsing the "Remarks" column which
    contains supplementary info/remarks about the ISO 3166 entry. The remarks
    are split into remarks part 1, 2, 3 and 4, with the majority only having part
    1 and 2.

    For any countries that have remarks listed, they are appended to the country
    update's description. If the remark has been mentioned in multiple updates
    then the remark will only be added to the latest entry. For any countries
    that don't have any remarks listed the original input object will be
    returned.

    Parameters
    ==========
    :iso3166_df_: pd.DataFrame
        object with all the pulled ISO 3166 updates data for inputted country.
    :country_summary_table: bs4.element.Tag
        bs4 soup object for summary table element on country's ISO page.

    Returns
    =======
    :iso3166_df_: pd.DataFrame
        object with all the pulled ISO 3166 updates data for inputted country,
        with any remarks data appended to description. If no remarks are listed
        for input country then the original input object will be returned.
    """
    #object to store all remarks - part 1, 2 and 3, if applicable
    remarks_ = {"part1": "", "part2": "", "part3": "", "part4": ""}

    #iterate through data columns on ISO summary table, append any remarks to object, if applicable
    for elem in country_summary_table:
        #check if html element is a bs4.Tag element, get its column name
        if isinstance(elem, Tag):
            column_name = elem.find(class_="core-view-field-name").text.lower()

            def parse_remarks_column_value(col_elem):
                """ Parse remarks from column class element. """
                #get column value from html class element, remove whitespace
                column_value = re.sub(' +', ' ', col_elem.find(class_="core-view-field-value").text.replace("\n", "").strip())
                if (column_value != "" and column_value != None):
                    #remove full stop at end of string, if applicable
                    if (column_value[-1] == "."):
                        column_value = column_value[:-1]
                return column_value

            #parse remarks data from column in ISO page
            column_value = parse_remarks_column_value(elem)

            #append remark part 1 column value to array
            if (column_name == "remark part 1"):
                remarks_["part1"] = column_value

            #append remark part 2 column value to array
            if (column_name == "remark part 2"):
                remarks_["part2"] = column_value

            #append remark part 3 column value to array
            if (column_name == "remark part 3"):
                remarks_["part3"] = column_value

            #append remark part 4 column value to array
            if (column_name == "remark part 4"):
                remarks_["part4"] = column_value

    #if no remarks found, return original input object
    if (all(value == "" for value in remarks_.values())):
        return iso3166_df_

    #sort dataframe via the date column
    iso3166_df_ = iso3166_df_.sort_values(by=['Date Issued'], ascending=False)

    #bools to check if remark has been appended to country updates description,
    #which means the same remark isn't being added to multiple descriptions and only the most recent update
    remark_part1_added = False
    remark_part2_added = False
    remark_part3_added = False
    remark_part4_added = False

    #iterate over all updates in dataframe, add remarks to description attribute, if applicable
    for index, row in iso3166_df_.iterrows():
        if ("remark part 1" in row["Description of Change"].lower() and not remark_part1_added):
            if (remarks_["part1"] != ''):
                iso3166_df_.at[index, "Description of Change"] = row["Description of Change"][:-1] + " (" + remarks_["part1"][0].lower() + remarks_["part1"][1:] + ")."
                remark_part1_added = True
        if ("remark part 2" in row["Description of Change"].lower() and not remark_part2_added):
            if (remarks_["part2"] != ''):
                iso3166_df_.at[index, "Description of Change"] = row["Description of Change"][:-1] + " (" + remarks_["part2"][0].lower() + remarks_["part2"][1:] + ")."
                remark_part2_added = True
        if ("remark part 3" in row["Description of Change"].lower() and not remark_part3_added):
            if (remarks_["part3"] != ''):
                iso3166_df_.at[index, "Description of Change"] = row["Description of Change"][:-1] + " (" + remarks_["part3"][0].lower() + remarks_["part3"][1:] + ")."
                remark_part3_added = True
        if ("remark part 4" in row["Description of Change"].lower() and not remark_part4_added):
            if (remarks_["part4"] != ''):
                iso3166_df_.at[index, "Description of Change"] = row["Description of Change"][:-1] + " (" + remarks_["part4"][0].lower() + remarks_["part4"][1:] + ")."
                remark_part4_added = True

    return iso3166_df_

def parse_updates_table(alpha2: str, iso3166_updates_table: list, year: list, year_range: bool, less_than: bool, greater_than: bool) -> pd.DataFrame:
    """
    Convert columns/headers using correct naming conventions, correct Date column into correct
    format, translate any unicode arrows in the text to normal arrow (->), fill any null rows.
    Some listed updates are "corrected" at a later date after publication; to keep track of
    these corrections the "Corrected Date Issued" and "Corrected Date" columns are used but
    later removed from the output dataframe. If year param not empty then remove any rows that
    don't have specified input year(s). If year range, less than or greater than parameters
    set to True then get all updates from year range or all updates less than or all updates
    greater than input year, respectively.

    Parameters
    ==========
    :alpha2: str
        2 letter ISO 3166-1 alpha-2 country code.
    :iso3166_updates_table: list
        2D array updates/changes table from wiki page or official ISO website.
    :year: list
        array/list of year(s). If not empty only the ISO 3166 updates for the selected
        year for a particular country will be returned. If empty then all years of
        updates are returned.
    :year_range: bool
        set to True if a range of years are input into year parameter e.g "2002-2010" etc.
        Function will remove all rows in Dataframe that aren't in specified year range.
    :less_than: bool
        set to True if less than symbol is input into year parameter e.g "<2018" etc.
        Function will remove all rows in Dataframe that are greater than or equal to
        specified year.
    :greater_than: bool
        set to True if greater than symbol is input into year parameter e.g ">2005" etc.
        Function will remove all rows in Dataframe that are less than specified year.

    Returns
    =======
    :iso3166_df: pd.DataFrame
        converted pandas dataframe of all ISO 3166 changes for particular country/countries
        from respective wiki or ISO pages.
    """
    #raise error if input updates table isn't an array/list
    if not isinstance(iso3166_updates_table, list):
        raise TypeError(f"Input ISO 3166 updates table parameter must be an array/list, got {type(iso3166_updates_table)}.")

    #update column names to correct naming conventions, catch error if array empty
    try:
      cols = correct_columns(iso3166_updates_table[0])
    except:
      raise ValueError(f"Error parsing columns from {alpha2} updates table, table should not be emtpy: {iso3166_updates_table}.")

    #lambda function to translate any occurrences of unicode arrow â†’ to normal arrow ->
    correct_arrow_lambda = lambda table: [[elem.replace('â†’', '->') for elem in entry if isinstance(elem, str)] for entry in table]

    #translate unicode arrow â†’ to normal arrow -> in table text, using lambda function
    iso3166_updates_table = correct_arrow_lambda(iso3166_updates_table)

    #convert 2D array into dataframe
    iso3166_df = pd.DataFrame(iso3166_updates_table[1:], columns=cols)

    def add_corrected_date(row: pd.Series):
        """ parse new date from row if date of changes has been "corrected", remove any full stops/punctuation and whitespace. """
        if ("corrected" in row):
            return " (corrected " + row[row.index("corrected") + len("corrected"):].strip().replace(')', '').replace('.', '').replace(' ', '') + ")"
        else:
            return ""

    #set column if update has been "corrected" at a later date after publication, set to "" otherwise
    iso3166_df["Corrected Date Issued"] = iso3166_df["Date Issued"].apply(add_corrected_date)

    def corrected_date(row: pd.Series):
        """ if update has been "corrected" after publication, parse original date and temporarily remove new "corrected" date,
            remove any full stops/punctuation and whitespace. """
        return re.sub("[(].*[)]", "", row).replace(' ', "").replace(".", '')

    #set Date Issued column to the original date of publication
    iso3166_df["Date Issued"] = iso3166_df["Date Issued"].apply(corrected_date)

    def get_year(row: pd.Series):
        """ convert string date in rows of dataframe into yyyy-mm-dd data format from date object, parse "corrected" date if applicable """
        if ("corrected" in row):
            return datetime.strptime(re.sub("[(].*[)]", "", row).replace(' ', "").replace(".", ''),'%Y-%m-%d').year
        else:
            return datetime.strptime(row, '%Y-%m-%d').year

    #drop rows of dataframe where Date Issued column isn't same as year parameter, if greater_than,
    #less_than or year_range bools set then drop any rows that don't meet condition
    if (year != ['']):
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

    #if edition/newsletter=OBP, set to empty string before appending its OBP link to column
    iso3166_df['Edition/Newsletter'] = iso3166_df['Edition/Newsletter'].apply(lambda val: "" if 'Online Browsing Platform (OBP) ' in val else val)

    #set Edition/Newsletter to OBP URl if no value/empty string
    if ((iso3166_df["Edition/Newsletter"] == "").any()):
        iso3166_df["Edition/Newsletter"] = iso3166_df["Edition/Newsletter"].replace('',
            "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:" + alpha2 + ").", regex=True)

    #separate 'Browsing' and 'Platform' string if they are concatenated in column
    iso3166_df["Edition/Newsletter"] = iso3166_df["Edition/Newsletter"].str.replace('BrowsingPlatform', "Browsing Platform")

    def remove_doublespacing(row: pd.Series):
        """ remove double spacing from string. """
        return re.sub(' +', ' ', row)

    #replace all null/nan with empty string
    iso3166_df.fillna("", inplace=True)

    #remove any double spacing from all columns, except Date Issued, using lambda function
    iso3166_df['Code/Subdivision Change'] = iso3166_df['Code/Subdivision Change'].apply(remove_doublespacing)
    iso3166_df['Description of Change'] = iso3166_df['Description of Change'].apply(remove_doublespacing)
    iso3166_df['Edition/Newsletter'] = iso3166_df['Edition/Newsletter'].apply(remove_doublespacing)

    #drop any rows that have no listed changes in them
    iso3166_df.drop(iso3166_df[(iso3166_df['Code/Subdivision Change'] == "") & (iso3166_df['Description of Change'] == "")].index, inplace=True)

    #reindex/reorder columns in dataframe
    iso3166_df = iso3166_df.reindex(columns=['Date Issued', 'Corrected Date Issued', 'Code/Subdivision Change', 
                                             'Description of Change', 'Edition/Newsletter'])

    return iso3166_df

def correct_columns(cols: list) -> list:
    """
    Update column names so all dataframes follow the column format of: ["Date Issued",
    "Edition/Newsletter", "Code/Subdivision Change", "Description of Change"].

    Parameters
    ==========
    :cols: list
        list of column names from header of parsed Changes table on wiki.

    Returns
    =======
    :cols: list
        list of columns updated to correct naming conventions.
    """
    if ("Newsletter" in cols):
        cols = list(map(lambda x: x.replace("Newsletter", 'Edition/Newsletter'), cols))
    cols = list(map(lambda x: x.replace("Newsletter/OBP", 'Edition/Newsletter'), cols))
    cols = list(map(lambda x: x.replace("Source", 'Edition/Newsletter'), cols))
    cols = list(map(lambda x: x.replace("Date issued", 'Date Issued'), cols))
    cols = list(map(lambda x: x.replace("Effective date of change", 'Date Issued'), cols))
    cols = list(map(lambda x: x.replace("Effective date", 'Date Issued'), cols))
    cols = list(map(lambda x: x.replace("Short description of change (en)", 'Description of Change'), cols))
    cols = list(map(lambda x: x.replace("Short description of change", 'Description of Change'), cols))
    cols = list(map(lambda x: x.replace("Description of change", 'Description of Change'), cols)) #**
    cols = list(map(lambda x: x.replace("Changes made", 'Description of Change'), cols))
    cols = list(map(lambda x: x.replace("Code/Subdivision change", 'Code/Subdivision Change'), cols))
    cols = list(map(lambda x: x.replace("Description of Change", 'Description of Change'), cols))
    cols = list(map(lambda x: x.replace("Description of Change in newsletter", 'Description of Change'), cols))

    return cols

def table_to_array(table_tag) -> tuple:
    """
    Convert html table into 2D array. Much of the function code was inspired from [1] which
    provides an optimal and working solution for handling tables with different rowspans &
    colspans.

    Parameters
    ==========
    :table_tag: bs4.element.Tag
      BS4 Tag object of table element.

    Returns
    =======
    :table: tuple
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
    #a colspan of 0 means â€œfill until the endâ€ but can really only apply
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