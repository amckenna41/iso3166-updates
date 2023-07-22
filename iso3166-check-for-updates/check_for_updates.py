from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait 
import random
from itertools import product
import pandas as pd
import iso3166
from bs4 import BeautifulSoup, Tag
import re
from importlib import metadata
import os
import getpass
import json
import time
import flag
from datetime import datetime
from operator import itemgetter
from dateutil.relativedelta import relativedelta
import requests
from google.cloud import storage
from flask import jsonify

#initialise Flask app
app = Flask(__name__)

#get current software version
__version__ = metadata.metadata('iso3166_updates')['version']

#initalise User-agent header for requests library 
USER_AGENT_HEADER = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(__version__,
                                       'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}

#base URL for ISO3 166-2 wiki and ISO website
wiki_base_url = "https://en.wikipedia.org/wiki/ISO_3166-2:"
iso_base_url = "https://www.iso.org/obp/ui/#iso:code:3166:"

#json object storing the error message and status code 
error_message = {}
error_message["status"] = 400

#json object storing the success message and status code
success_message = {}
success_message["status"] = 200

#get current date and time on function execution
current_datetime = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d")

def create_driver():
    """
    Create instance of Selenium chromedriver for each country's individual page on the 
    official ISO website. The site requires a session to be created and Javascript to
    be ran so the page's data cannot be directly webscraped. For some countries their
    ISO page contains extra data not on the country's wiki page. 

    Parameters
    ----------
    None

    Returns
    -------
    :driver : selenium.webdriver.chrome.webdriver.WebDriver
        instance of Python Selenium using chromedriver webdriver.
    """
    #create instance of Service class and get executeable path of chromedriver
    service = Service(executable_path='/usr/lib/chromium-browser/chromedriver')

    #create instance of Options class, add below options to ensure everything works as desired
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    chrome_options.add_experimental_option("useAutomationExtension", False) 

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

@app.route("/")
def check_for_updates_main():
    """
    Google Cloud Run main entry script that checks for any updates within specified 
    date range for the iso3166-updates API. It uses the get_all_iso3166_updates.py
    script to web scrape all country's ISO 3166-2 data from the various data sources,
    checking for any updates in a date range. The Cloud run app is built using a docker 
    container that contains all the required dependancies and binaries required to run 
    the script. 
    
    If any updates are found that are not already present in the JSON object
    within the GCP Storage bucket then a GitHub Issue is automatically created in the 
    iso3166-updates, iso3166-2 repository that itself stores all the latest info 
    and data relating to the ISO3166-2 standard. A similar Issue will also be raised 
    in the iso3166-flag-icons repo which is another custom repo that stores all the 
    flag icons of all countries and subdivisions in the ISO 3166-1 and ISO 3166-2.
    Additionally, if changes are found then the ISO 3166 updates JSON file in the 
    GCP Storage bucket is updated which is the data source for the iso3166-updates 
    Python package and accompanying API.

    Parameters
    ----------
    None
    
    Returns
    -------
    :success_message/error_message : json
       jsonified response indicating whether the application has completed successfully or
       an error has arose during execution.
    """
    #default month cutoff for checking for updates
    months = 6

    #object containing current iso3166-2 updates after month range date filter applied
    latest_iso3166_updates_after_date_filter = {}

    #get list of all country's 2 letter alpha-2 codes
    alpha2_codes = sorted(list(iso3166.countries_by_alpha2.keys()))

    #sort codes in alphabetical order and uppercase
    alpha2_codes.sort()
    alpha2_codes = [code.upper() for code in alpha2_codes]

    #call get_updates function to scrape all country updates from data sources
    latest_iso3166_updates = get_updates(export_json=False, export_csv=False, verbose=True)

    #iterate over all alpha-2 codes, check for any updates in specified months range in updates json 
    for alpha2 in list(latest_iso3166_updates.keys()):
        latest_iso3166_updates_after_date_filter[alpha2] = []
        for row in range(0, len(latest_iso3166_updates[alpha2])):
            if (latest_iso3166_updates[alpha2][row]["Date Issued"] != ""): #go to next iteration if no Date Issued in row
                #convert str date into date object
                row_date = (datetime.strptime(latest_iso3166_updates[alpha2][row]["Date Issued"], "%Y-%m-%d"))
                #compare date difference from current row to current date
                date_diff = relativedelta(current_datetime, row_date)
                #calculate date difference in months
                diff_months = date_diff.months + (date_diff.years * 12)

                #if month difference is within months range, append to updates json object
                if (diff_months <= months):
                    latest_iso3166_updates_after_date_filter[alpha2].append(latest_iso3166_updates[alpha2][row])

        #if current alpha-2 has no rows in date range, remove from temp object
        if (latest_iso3166_updates_after_date_filter[alpha2] == []):
            latest_iso3166_updates_after_date_filter.pop(alpha2, None)

    #bool to track if any ISO 3166 updates found
    updates_found = False
    
    #if update object not empty (i.e there are updates), call update_json and create_issue functions
    if (latest_iso3166_updates_after_date_filter != {}):
        updates_found, filtered_updates = update_json(latest_iso3166_updates_after_date_filter)
    if (updates_found):
        create_issue(filtered_updates, months)
        print("ISO 3166-2 updates found and successfully exported.")
        success_message["message"] = "ISO 3166-2 updates found and successfully exported to bucket and GitHub Issues created."
    else:
        print("No ISO 3166-2 updates found.")
        success_message["message"] = "No ISO 3166-2 updates found."

    return jsonify(success_message), 200

def update_json(latest_iso3166_updates_after_date_filter):
    """
    If changes have been found for any countrys in the ISO3166-2 within the
    specified date range using the check_iso3166_updates_main function then 
    the JSON in the storage bucket is updated with the new JSON and the old 
    one is stored in an archive folder on the same bucket.

    Parameters
    ----------
    :latest_iso3166_updates_after_date_filter : json
        json object with all listed iso3166-2 updates after month date filter
        applied.

    Returns
    -------
    :updates_found : bool
        bool to track if updates/changes have been found in JSON object.
    :individual_updates_json: dict
        dictionary of individual ISO 3166 updates that aren't in existing 
        updates object on JSON.
    """
    #initialise storage client
    storage_client = storage.Client()
    try:
        #create a bucket object for the bucket
        bucket = storage_client.get_bucket(os.environ["BUCKET_NAME"])
    except google.cloud.exceptions.NotFound:
        error_message["message"] = "Error retrieving updates data json storage bucket: {}.".format(os.environ["BUCKET_NAME"])
        return jsonify(error_message), 400
    #create a blob object from the filepath
    blob = bucket.blob(os.environ["BLOB_NAME"])  
    
    print("bucket-name", os.environ["BUCKET_NAME"])
    print("bucket-name", os.environ["BLOB_NAME"])
    print("blob", blob)

    #raise error if updates file not found in bucket
    if not (blob.exists()):
        raise ValueError("Error retrieving updates data json: {}.".format(os.environ["BLOB_NAME"]))
    
    #download current ISO 3166 updates JSON file from storage bucket 
    current_updates_data = json.loads(blob.download_as_string(client=None))

    #set new json object to original one imported from gcp storage
    updated_json = current_updates_data
    updates_found = False

    #seperate object that holds individual updates that were found, used in create_issue function
    individual_updates_json = {}

    #iterate over all updates in json, if update/row not found in original json, pulled from GCP storage, 
    # append to new updated_json object
    for code in latest_iso3166_updates_after_date_filter:   
        individual_updates_json[code] = []
        for update in latest_iso3166_updates_after_date_filter[code]:
            if not (update in current_updates_data[code]):
                updated_json[code].append(update)
                updates_found = True
                individual_updates_json[code].append(update)

        #updates are appended to end of updates json, need to reorder by Date Issued, latest first
        updated_json[code] = sorted(updated_json[code], key=itemgetter('Date Issued'), reverse=True)

        #if current alpha-2 code has no updates associated with it, remove from temp object
        if (individual_updates_json[code] == []):
            individual_updates_json.pop(code, None)

    #if updates found in new updates json compared to current one
    if (updates_found):

        #temp path for exported json
        tmp_updated_json_path = os.path.join("/tmp", os.environ["BLOB_NAME"])
        
        #export updated json to temp folder
        with open(tmp_updated_json_path, 'w', encoding='utf-8') as output_json:
            json.dump(updated_json, output_json, ensure_ascii=False, indent=4)
        
        #create blob for updated JSON
        blob = bucket.blob(os.environ["BLOB_NAME"])

        #move current updates json in bucket to an archive folder, append datetime to it
        archive_filepath = os.environ["ARCHIVE_FOLDER"] + "/" + os.path.splitext(os.environ["BLOB_NAME"])[0] \
            + "_" + str(current_datetime.strftime('%Y-%m-%d')) + ".json"
        
        #create blob for archive updates json 
        archive_blob = bucket.blob(archive_filepath)
        
        #upload old updates json to archive folder 
        archive_blob.upload_from_filename(tmp_updated_json_path)

        #upload new updated json using gcp sdk, replacing current updates json 
        blob.upload_from_filename(tmp_updated_json_path)

    return updates_found, individual_updates_json
    
def create_issue(latest_iso3166_updates_after_date_filter, month_range):
    """
    Create a GitHub issue on the iso3166-2, iso3166-updates and 
    iso3166-flag-icons repository, using the GitHub api, if any updates/changes 
    are made to any entries in the ISO 3166-2. The Issue will be formatted in 
    a way to clearly outline any of the updates/changes to be made to the JSONs 
    in the iso3166-2, iso3166-updates and iso3166-flag-icons repos. 

    Parameters
    ----------
    :latest_iso3166_updates_after_date_filter : json
        json object with all listed iso3166-2 updates after month date filter
        applied.
    :month_range : int
        number of past months updates were pulled from.

    Returns
    -------
    :message : str
        response message from GitHub api post request.

    References
    ----------
    [1]: https://developer.github.com/v3/issues/#create-an-issue
    """
    issue_json = {}
    issue_json["title"] = "ISO 3166-2 Updates: " + str(current_datetime.strftime('%Y-%m-%d')) + " (" + ', '.join(list(latest_iso3166_updates_after_date_filter)) + ")" 
    
    #body of Github Issue
    body = "# ISO 3166-2 Updates\n"

    #get total sum of updates for all countrys in json
    total_updates = sum([len(latest_iso3166_updates_after_date_filter[code]) for code in latest_iso3166_updates_after_date_filter])
    total_countries = len(latest_iso3166_updates_after_date_filter)
    
    #change body text if more than 1 country 
    if (total_countries == 1):
        body += "### " + str(total_updates) + " updates found for " + str(total_countries) + " country between the "
    else:
        body += "### " + str(total_updates) + " updates found for " + str(total_countries) + " countries between the "

    #display number of updates for countrys and the date period
    body += "### " + str(total_updates) + " updates found for " + str(total_countries) + " countries between the " + str(month_range) + " month period of " + \
        str((current_datetime + relativedelta(months=-month_range)).strftime('%Y-%m-%d')) + " to " + str(current_datetime.strftime('%d-%m-%Y')) + ".\n"

    #iterate over updates in json, append to updates object
    for code in list(latest_iso3166_updates_after_date_filter.keys()):
        
        #header displaying current country name, code and flag icon using emoji-country-flag library
        body += "\n### " + "Country - " + iso3166.countries_by_alpha2[code].name + " (" + code + ") " + flag.flag(code) + ":\n"

        row_count = 0

        #iterate over all update rows for each country in object, appending to html body
        for row in latest_iso3166_updates_after_date_filter[code]:
            
            #increment row count which numbers each country's updates if more than 1
            if (len(latest_iso3166_updates_after_date_filter[code]) > 1):
                row_count = row_count + 1
                body += str(row_count) + ".)"

            #output all row field values 
            for key, val in row.items():
                body += "<ins>" + str(key) + ":</ins> " + str(val) + "<br>"

    #add attributes to data json 
    issue_json["body"] = body
    issue_json["assignee"] = "amckenna41"
    issue_json["labels"] = ["iso3166-updates", "iso3166", "iso366-2", "subdivisions", "iso3166-flag-icons", str(current_datetime.strftime('%Y-%m-%d'))]

    #api url and headers
    issue_url = "https://api.github.com/repos/" + os.environ["github-owner"] + "/" + os.environ["github-repo-1"] + "/issues"
    issue_url_2 = "https://api.github.com/repos/" + os.environ["github-owner"] + "/" + os.environ["github-repo-2"] + "/issues"
    issue_url_3 = "https://api.github.com/repos/" + os.environ["github-owner"] + "/" + os.environ["github-repo-3"] + "/issues"
    headers = {'Content-Type': "application/vnd.github+json", 
        "Authorization": "token " + os.environ["github-api-token"]}

    #make post request to github repos using api
    requests.post(issue_url, data=json.dumps(issue_json), headers=headers)
    requests.post(issue_url_2, data=json.dumps(issue_json), headers=headers)
    requests.post(issue_url_3, data=json.dumps(issue_json), headers=headers)
    
def get_updates(alpha2_codes=[], year=[], export_filename="iso3166-updates", export_folder="test_iso3166-updates", 
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
    ----------
    :alpha2_codes : str / list (default=[])
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
    :export_folder : str (default="../iso3166-updates")
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
        requires Python Selenium and chromedriver. If False then just use country data
        from its wiki page.

    Returns
    -------
    :all_changes : dict
        dictionary of all found ISO 3166 updates from user's inputted alpha2 codes and or year
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
    
    #raise error if invalid data types input for year parameter
    for year_ in year:
        if not isinstance(year_, str):
            raise TypeError("Invalid data type for year parameter, expected str, got {}.".format(type(year_)))

    #if list with 1 string of multiple alpha-2 codes, convert to multiple list elements e.g ['HI, LA'] will be converted to ['HI', 'LA']
    if (isinstance(alpha2_codes, list) and len(alpha2_codes) == 1 and ',' in alpha2_codes[0]):
        alpha2_codes = alpha2_codes[0].replace(' ', '').split(',')

    #if single str of 1 or more years input then convert to array, remove whitespace, seperate using comma
    if (isinstance(year, str)):
        year = year.replace(' ', '').split(',')
    
    def convert_to_alpha2(alpha3_code):
        """ 
        Convert an ISO 3166 country's 3 letter alpha-3 code into its 2 letter
        alpha-2 counterpart. 

        Parameters 
        ----------
        :alpha3_code: str
            3 letter ISO 3166-1 country code.
        
        Returns
        -------
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
    
    #var to keep track of original alpha2 parameter input
    input_alpha2_codes = alpha2_codes

    #use all ISO 3166-1 codes if no input alpha-2 parameter input
    if ((alpha2_codes == [''] or alpha2_codes == [])):
        alpha2_codes = sorted(list(iso3166.countries_by_alpha2.keys()))

    #sort codes in alphabetical order, uppercase each
    alpha2_codes.sort()
    alpha2_codes = [code.upper() for code in alpha2_codes]

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
            #split years into multiple years, if multiple are input
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

    #iterate over all input ISO 3166-1 country codes
    for alpha2 in alpha2_codes:
        
        #skip to next iteration if alpha-2 not valid, add XK (Kosovo manually to object)
        if (alpha2 not in list(iso3166.countries_by_alpha2.keys())):
            continue

        #print out progress of function
        if (verbose):
            print("ISO 3166-1 Code: {} ({}, {})".format(alpha2, wiki_base_url + alpha2, iso_base_url + alpha2))

        all_changes[alpha2] = {}

        #web scrape country's wiki data, convert html table/2D array to dataframe 
        iso3166_df_wiki = get_updates_df_wiki(alpha2, year, year_range, less_than, greater_than)
        
        print("alpha2", alpha2)
        # print("iso3166_df_wiki")
        # print(iso3166_df_wiki)
        #use Selenium Chromedriver to parse country's updates data from official ISO website
        if (use_selenium):
            iso_website_df = get_updates_df_selenium(alpha2, year, year_range, less_than, greater_than)

            #concatenate two updates dataframes
            iso3166_df = pd.concat([iso3166_df_wiki, iso_website_df], ignore_index=True, sort=False)
        else:
            iso3166_df = iso3166_df_wiki

        # print("iso3166_df")
        # print(iso3166_df)
        # if not (iso3166_df is None):
        #only export non-empty dataframes         
        if not (iso3166_df.empty):

            #remove any duplicate rows using Date Issued column
            iso3166_df = iso3166_df.drop_duplicates("Date Issued", keep='first')
        
            #set Edition/Newsletter to OBP if no value/empty string
            if ((iso3166_df["Edition/Newsletter"] == "").any()):
                iso3166_df["Edition/Newsletter"] = iso3166_df["Edition/Newsletter"].replace('', 
                    "Online Browsing Platform (OBP).", regex=True)

            #seperate 'Browsing' and 'Platform' string if they are concatenated in column
            iso3166_df["Edition/Newsletter"] = iso3166_df["Edition/Newsletter"].str.replace('BrowsingPlatform', "Browsing Platform")
                        
            #convert date column to datetime object
            iso3166_df['Date Issued'] = pd.to_datetime(iso3166_df["Date Issued"])
            #sort and order by date, newest to oldest
            iso3166_df = iso3166_df.sort_values(by=['Date Issued'], ascending=False)
            #convert date column back to string 
            iso3166_df['Date Issued'] = iso3166_df['Date Issued'].astype(str)

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

    #create output folder if doesn't exist and files are set to be exported
    if (export_csv or export_json) and not (os.path.isdir(export_folder)):
        os.mkdir(export_folder)
            
    #auxillary function to remove all empty nested dicts within object
    def _del(_d):
        return {a:_del(b) if isinstance(b, dict) else b for a, b in _d.items() if b and not a.startswith('_')}
    
    #remove any empty country updates dict if year parameter input set and no alpha-2 codes passed into parameter
    # if (year != [] and (input_alpha2_codes == [] or input_alpha2_codes == [''])):
    #     all_changes = _del(all_changes)

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
                    #append alpha-2 codes and list of years or gt/lt/year range symbols, if applicable, to seperate exported json files
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

    return all_changes

def get_updates_df_selenium(alpha2, year=[], year_range=False, less_than=False, greater_than=False):    
    """
    Pull all related ISO 3166-2 updates/changes for a given input country from the official ISO 
    website. The Selenium Chromedriver tool is utilised prior to the BS4 web scraper as javascript
    has to run on the site to get the data. Various random steps are implemented during exection
    of the Chromedriver to avoid requests being blocked. The changes section for each country is 
    parsed and, converted into a 2D table and then a DataFrame.

    Parameters
    ----------
    :alpha2 : str / list
        single string or list of alpha-2 ISO 3166-1 codes to get the latest ISO 3166-2 updates 
        from. If a single alpha-2 code passed in then it is converted to an iterable list. If 
        no value passed into param then all updates for all ISO 3166-1 countries are retrieved. 
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
    -------
    :iso3166_df_selenium : pd.DataFrame
        converted pandas dataframe of all ISO 3166-2 changes for particular country/countries
        from official ISO website.
    """
    #create instance of chromedriver
    driver = create_driver()

    #create session for input country's ISO section
    driver.get(iso_base_url + alpha2)
    
    #pause for 3 seconds
    WebDriverWait(driver, 3) 

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
        if ('change history of country code' or 'historique des modifications des Codes de pays' in h3.text.lower()):
            changes_html = str(soup).split(str(h3))[1]
            break

    #create soup object from changes section, get html table 
    changes_table_soup = BeautifulSoup(changes_html, "lxml")
    changes_table = changes_table_soup.find('table')

    #if no Changes section with updates found in wiki, return empty dataframe
    if (changes_table is None):
        driver.quit()
        return pd.DataFrame()
    
    # print("changes_table")
    # print(changes_table)
    #convert html table into 2d array
    changes_table_converted = table_to_array(changes_table)

    # print("changes_table_converted")
    # print(changes_table_converted)
    #convert 2d array of updates into dataframe, fix columns, remove duplicate rows etc
    iso3166_df_selenium = parse_updates_table(changes_table_converted, year, year_range, less_than, greater_than)
    
    driver.quit()

    return iso3166_df_selenium

def get_updates_df_wiki(alpha2, year=[], year_range=False, less_than=False, greater_than=False):
    """
    Pull all related ISO 3166-2 updates/changes for a given input country from the country's
    respective wiki page. Selenium is not a requirement for web scraping wiki pages. Convert
    parsed html table, from the Changes/Updates Section into a pandas dataframe. 

    Parameters
    ----------
    :alpha2 : str / list
        single string or list of alpha-2 ISO 3166-1 codes to get the latest ISO 3166-2 updates 
        from. If a single alpha-2 code passed in then it is converted to an iterable list. If 
        no value passed into param then all updates for all ISO 3166-1 countries are retrieved. 
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
    -------
    :iso3166_df_wiki : pd.DataFrame
        converted pandas dataframe of all ISO 3166-2 changes for particular country/countries
        from respective wiki pages.
    """
    #get html content from wiki of ISO 3166 page, raise exception if status code != 200
    try:
        page = requests.get(wiki_base_url + alpha2, headers=USER_AGENT_HEADER)
        page.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    #convert html content into BS4 object
    soup = BeautifulSoup(page.content, "html.parser")

    #get Changes Section/Heading from soup 
    changesSection = soup.find("span", {"id": "Changes"})

    #if no Changes section with updates found in wiki, return empty dataframe
    if (changesSection is None):
        return pd.DataFrame()

    #get table element in Changes Section 
    table = changesSection.findNext('table')
    
    #convert html table to 2D array 
    iso3166_table_wiki = table_to_array(table)

    #convert 2d array of updates into dataframe, fix columns, remove duplicate rows etc
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
    format and translate any unicode arrows in the text to normal arrow (->), fill any null
    rows. If year param not empty then remove any rows that don't have specified year(s). If 
    year range, less than or greater than parameters set to True then get all updates from 
    year range or all updates less than or all updates greater than a year, respectively. 
    
    Parameters
    ----------
    :iso3166_updates_table : list
        2d array updates/changes table from wiki page or official ISO website.
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
    -------
    :iso3166_df : pd.DataFrame
        converted pandas dataframe of all ISO 3166-2 changes for particular country/countries
        from respective wiki pages.
    """
    #raise error if input updates table isnt an array/list
    if not isinstance(iso3166_updates_table, list):
        raise TypeError("Input ISO 3166 updates table parameter must be a array/list, got {}.".format(type(iso3166_updates_table)))

    #update column names to correct naming conventions
    cols = correct_columns(iso3166_updates_table[0])

    #lambda function to translate any occurences of unicode arrow → to normal arrow ->
    correct_arrow_lambda = lambda table: [[elem.replace('→', '->') for elem in entry if isinstance(elem, str)] for entry in table]

    #translate unicode arrow → to normal arrow -> in table text
    iso3166_updates_table = correct_arrow_lambda(iso3166_updates_table)

    #convert 2D array into dataframe    
    iso3166_df = pd.DataFrame(iso3166_updates_table[1:], columns=cols)

    #get index and name of Date column in DataFrame, i.e the column that has 'date' in it
    date_col_index = [idx for idx, s in enumerate(list(map(lambda x: x.lower(), iso3166_df.columns))) if 'date' in s]
    date_col_name = list(iso3166_df.columns)[date_col_index[0]]

    def corrected_date(row):
        """ parse new date from row if date of changes has been "corrected", remove any full stops/punctation and whitespace. """
        if ("corrected" in row):
            return row[row.index("corrected") + len("corrected"):].strip().replace(')', '').replace('.', '').replace(' ', '')
        else:
            return row.replace('.', '').strip().replace(' ', '')    
            
    #reformat date column if date has been corrected
    iso3166_df[date_col_name] = iso3166_df[date_col_name].apply(corrected_date)
        
    def get_year(row):
        """ convert string date in rows of df into yyyy-mm-dd data format from date object. """
        return datetime.datetime.strptime(row, '%Y-%m-%d').year

    #drop rows of dataframe where Date Issued column isn't same as year parameter, if greater_than, 
    #less_than or year_range bools set then drop any rows that don't meet condition
    if (year != []): 
        #create temp year column to get year of updates from date column, convert to str
        iso3166_df['Year'] = iso3166_df[date_col_name].apply(get_year)     
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

    if ("Code/Subdivision change" not in iso3166_df):
        iso3166_df["Code/Subdivision change"] = ""

    #reindex/reorder columns in dataframe
    iso3166_df = iso3166_df.reindex(columns=['Date Issued', 'Edition/Newsletter', 
        'Code/Subdivision change', 'Description of change in newsletter'])

    #replace all null/nan with empty string
    iso3166_df.fillna("", inplace=True)

    return iso3166_df

def correct_columns(cols):
    """ 
    Update column names so all dataframes follow the column format of: ["Date Issued", 
    "Edition/Newsletter", "Code/Subdivision change", "Description of change in newsletter"].

    Parameters
    ----------
    :cols : list
        list of column names from header of parsed Changes table on wiki.
    
    Returns
    -------
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
    cols = list(map(lambda x: x.replace("Short description of change (en)", 'Description of change in newsletter'), cols))
    cols = list(map(lambda x: x.replace("Short description of change", 'Description of change in newsletter'), cols))

    return cols     

def table_to_array(table_tag):
    """
    Convert html table into 2D array. Much of the function code was inspired from [1] which 
    provides an optimal and working solution for handling tables with different rowspans & 
    colspans. 

    Parameters
    ----------
    :table_tag : bs4.element.Tag
      bs4 Tag object of table element.
    
    Returns
    -------
    :table : tuple
      tuple of parsed data from html table in Changes section of ISO 3166 wiki.
    
    Reference
    ---------
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