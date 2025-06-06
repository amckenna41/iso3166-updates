import re
import os 
from itertools import product
from datetime import datetime
import iso3166
from bs4 import BeautifulSoup, Tag
import pandas as pd
import time
import requests
import random
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm

def get_iso3166_updates(alpha_codes_range: str="") -> dict:
    """
    Get all listed changes/updates to a country's ISO 3166-2 subdivision codes/names. The two data
    sources for the updates data are via the "Changes" section on its wiki page as well as any listed
    updates on the official ISO website. A country's wiki page and section on ISO website follow the
    convention https://en.wikipedia.org/wiki/ISO_3166-2:XX and https://www.iso.org/obp/ui#iso:code:3166:XX,
    respectively, where XX is the 2 letter alpha-2 code for a country listed in the ISO 3166-1. The
    "Changes" section lists updates or changes to any ISO 3166-2 codes, including historical changes,
    according to the ISO newsletters which were released up until July 2013 but now are communicated
    via their online catalogue/Online Browsing Platform (OBP), or via a database, which usually costs
    money to subscribe to. The ISO newsletters are not easily discoverable and accessible online and 
    may require a subscription to the ISO 3166-2 database (https://www.iso.org/iso/updating_information.pdf), 
    with the ISO 3166 dataset itself costing around $330!

    Some countries have missing and or not up-to-date updates data on their wiki pages, so the
    country data from the official ISO website is also gathered using Selenium Chromedriver, prior
    to being scraped using BeautifulSoup, as the page requires Javascript to be run on page load.
    Some country updates mention a change to their remarks which are additional notes/supplementary
    info about changes to a country. These remarks are appended to the country description from
    the ISO page, depending on the value of the include_remarks_data parameter. Similarly, not all 
    the historic updates for a code are listed on the ISO site hence the combination of the wiki 
    and ISO pages, to get a full comprehensive dataset. 

    The earliest available changes are from the year 1996 and the latest changes are from the 
    current year.

    The updates data from the wiki page and ISO website are converted to a DataFrame with the
    columns: Change, Description of Change, Date Issued, and Source. These are concatenated before 
    being exported to a CSV and or JSON for further analysis. You can also get the updates from a 
    particular year, list of years, year range or updates greater than or less than a specified 
    year or not equal to a year, using the year parameter. All of the updates are ordered 
    alphabetically by their 2 letter ISO 3166-1 country code.

    Parameters
    ==========
    :alpha_codes_range: str (default="")
        a range of 2 ISO 3166-1 alpha-2, alpha-3 or numeric country codes to export the updates data from, 
        separated by a '-'. The code on the left hand side will be the starting alpha code and the code on 
        the right hand side will be the final alpha code to which the data is exported from, e.g AD-LV, 
        will export all updates data from Andorra to Latvia, alphabetically. Useful if a subset of codes 
        are required. If only a single alpha code input then it will serve as the starting country.

    Returns
    =======
    :all_iso3166_updates: dict
        dictionary of all found ISO 3166 updates from user's inputted alpha codes and or year
        parameter values.

    Raises
    ======
    TypeError:
        Invalid data types for input parameters.
    """
    #
    alpha_codes_list = sorted(iso3166.countries_by_alpha2.keys())
    alpha_codes_list = ["AD", "FR", "DE", "GY", "PY", "ZA"]

    #object to store all country updates/changes
    all_iso3166_updates = {}
    
    #initalise tqdm progress bar, if less than 5 alpha-2 codes input then don't display progress bar, or print elapsed time
    progress_bar = tqdm(alpha_codes_list, ncols=80, disable=(len(alpha_codes_list) < 5))

    #iterate over all input ISO 3166-1 country codes
    for alpha2 in progress_bar:
        progress_bar.set_description(f"{iso3166.countries_by_alpha2[alpha2].name.title()} ({alpha2})")        

        #initialise object of updates for current alpha-2 code
        all_iso3166_updates[alpha2] = []

        #web scrape country's wiki data, convert html table/2D array to dataframe
        iso3166_df_wiki = get_updates_df_wiki(alpha2)

        #use Selenium Chromedriver to parse country's updates data from official ISO website
        iso_website_df, remarks_data = get_updates_df_selenium(alpha2)

        #add the remarks data to each updates object, where applicable 
        iso_website_df = add_remarks_data(iso_website_df, remarks_data)

        #concatenate two updates dataframes
        iso3166_df = pd.concat([iso3166_df_wiki, iso_website_df], ignore_index=True, sort=False)

        #if updates dataframe is empty, skip to next iteration
        if (iso3166_df.empty):
            continue

        #drop any duplicate rows in object, e.g rows that have the same publication date and change/description of change attribute values
        iso3166_df = remove_duplicates(iso3166_df)

        #create a mask of rows where the "Change" column is empty
        empty_change_mask = iso3166_df["Change"] == ""

        #swap Change and Description of Change if Change is empty
        iso3166_df.loc[empty_change_mask, "Change"] = iso3166_df["Description of Change"]

        #for rows that have been swapped, set Description of Change to empty
        iso3166_df.loc[empty_change_mask, "Description of Change"] = ""

        #sort rows by publication date descending
        iso3166_df = iso3166_df.assign(
            SortDate=pd.to_datetime(iso3166_df['Date Issued'].str.extract(r'^(\d{4}-\d{2}-\d{2})')[0], errors='coerce')
        ).sort_values(by='SortDate', ascending=False).drop(columns=['SortDate']).reset_index(drop=True)

        #add ISO updates to object of all ISO 3166 updates, convert to json
        all_iso3166_updates[alpha2] = iso3166_df.to_dict(orient="records")

    print("all_iso3166_updates")
    print(all_iso3166_updates)
    #add manual updates data to the output object, filter by year if applicable - temporary function
    all_iso3166_updates = manual_updates(all_iso3166_updates)

    return all_iso3166_updates
    
def create_driver() -> webdriver.Chrome:
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
    [5]: https://googlechromelabs.github.io/chrome-for-testing/

    Notes
    =====
    - If Chrome Binary and Chromedriver versions are incompatible, remove chromedriver and reinstall: 
        find / -name chromedriver 2>/dev/null (find chromedriver)
        sudo rm /usr/local/bin/chromedriver (remove)
        chromedriver --version (verify uninstall)
        brew install chromedriver (reinstall)
        chromedriver --version (verify install)
    - If there is a Runtime Error in the function that is calling create_driver(), the error might be in this
        function. For example syntax errors in this function might not be highlighted if a Runtime Error is thrown
        from the calling function.
    - If there is a runtime error with initialising the instance, double check the version of chromedriver & update:
        brew install chromedriver
    - Find where chromedriver is installed:
        which chromedriver
    
    Raises
    ======
    WebDriverException:
        Chromedriver not found at list of paths.
    FileNotFoundError:
        Chrome binary not found at list of possible locations.
    RuntimeError:
        Issue initialising the Chromedriver instance. 
    """
    #list of paths chromedriver might be stored in
    chromedriver_executable_paths = [
        '/usr/local/bin/chromedriver', 
        '/usr/bin/chromedriver', 
        '/usr/lib/chromedriver'
        ]
    chromedriver_executable_path = ""
    chromedriver_path_found = False

    #iterate over potential likely paths for chromedriver executable 
    for path in chromedriver_executable_paths:
        if (os.path.isfile(path)):
            chromedriver_path_found = True
            chromedriver_executable_path = path

    #verify Chromedriver is found on one of the paths, raise exception if not
    if not (chromedriver_path_found):
      raise WebDriverException(f"Chromedriver not found, verify it's installed in one of the paths: {', '.join(chromedriver_executable_paths)}")

    #create instance of Service class and get executable path of chromedriver
    service = Service(executable_path=chromedriver_executable_path)

    #create instance of Options class, add below options to Chromedriver instance
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    # chrome_options.headless = False
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--window-size=1920,1080") 
    chrome_options.add_argument("--disable-popup-blocking")  
    chrome_options.add_argument("--ignore-certificate-errors") 
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    chrome_options.add_experimental_option("useAutomationExtension", False) 

    #list of possible Chrome binary paths
    possible_binary_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",   # macOS
        "/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome", # macOS
        "/usr/bin/google-chrome",                                         # Linux
        "/usr/bin/google-chrome-stable",                                  # Linux
        "/usr/local/bin/google-chrome",                                   # Linux alternative
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",     # Windows
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"  # Windows (32-bit)
    ]

    chrome_binary_path = ""
    
    #iterate through possible Chrome binary paths, raise error if not found via paths
    for path in possible_binary_paths:
        if (os.path.exists(path)):
            chrome_binary_path = path
            break
    else:
        raise FileNotFoundError(f"Chrome binary not found at list of possible locations:\n{', '.join(possible_binary_paths)}.")
    
    #when testing locally need to specify the binary location of Google Chrome: find / -type d -name "*Chrome.app"
    chrome_options.binary_location = chrome_binary_path

    #initialise driver object before try block
    driver = None

    try:
        #create webdriver instance
        driver = webdriver.Chrome(service=service, options=chrome_options)

        #set object to undefined, helps avoid bot detection
        # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
        
        #set random user-agent string for WebDriver to avoid detection, using fake_useragent package
        user_agent_header = UserAgent().random
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent_header}) 

    #raise exception if issue creating chromedriver, always close chromedriver with finally statement
    except Exception as e:
        raise RuntimeError(f"Failed to initialize WebDriver: {e}")

    return driver

def get_updates_df_wiki(alpha_code: str) -> pd.DataFrame:
    """
    Pull all related ISO 3166 updates/changes for a given input country from the country's
    respective wiki page. Selenium is not a requirement for web scraping wiki pages. Convert
    the parsed html table, from the Changes/Updates Section, into a pandas dataframe.

    Parameters
    ==========
    :alpha_code: str
        single string of an alpha ISO 3166-1 country code to get the latest ISO 3166 updates 
        for. If the 3 letter alpha-3 or numeric code are input then convert to alpha-2.

    Returns
    =======
    :iso3166_df_wiki: pd.DataFrame
        converted pandas dataframe of all ISO 3166 changes for particular country/countries
        from respective wiki pages.
    
    Raises
    ======
    requests.exceptions.HTTPError:
        Wiki URL content can't be retrieved, probably due to invalid alpha-2 country code.
    ValueError:
        If the "Changes" section or table cannot be found on page.
    """
    #validate alpha code, convert to alpha-2 if required
    alpha2 = convert_to_alpha2(alpha_code)

    #set random user-agent string for requests library to avoid detection, using fake-useragent package
    user_agent = UserAgent()
    user_agent_header = user_agent.random

    #base URL for country wiki pages
    wiki_base_url = "https://en.wikipedia.org/wiki/ISO_3166-2:"

    #get html content from wiki of ISO 3166 page, raise exception if status code != 200
    try:
        response = requests.get(wiki_base_url + alpha2, headers={"User-Agent": user_agent_header}, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.HTTPError(f"Error retrieving Wikipedia page for {alpha2} ({wiki_base_url + alpha2}): {e}")

    #convert html content into BS4 object
    soup = BeautifulSoup(response.content, "html.parser")

    #Changes section can be in a span, h1 or h2 html element 
    possible_changes_section_tags = ["span", "h1", "h2"]

    #initialize changes_section to None
    changes_section = None

    #iterate over possible tags to find the Changes section, loop in order of element preference
    for tag in possible_changes_section_tags:
        changes_section = soup.find(tag, {"id": "Changes"})
        if changes_section:
            break  #break out of loop if a valid tag is found

    #validate if any Changes section was found, if not return empty dataframe
    if not (changes_section):
        # print(f"\nNo 'Changes' section found for {alpha2} at URL {wiki_base_url + alpha2}.")
        return pd.DataFrame()

    #get table element in Changes Section, raise error if table not found
    changes_section = changes_section.find_next('table')
    if not changes_section:
        raise ValueError(f"No table found in the 'Changes' section for {alpha2} at {wiki_base_url + alpha2}.")

    #convert html table to 2D array
    iso3166_table_wiki = table_to_array(changes_section, soup)

    #convert 2D array of updates into dataframe, fix columns, remove duplicate rows etc
    iso3166_df_wiki = parse_updates_table(alpha2, iso3166_table_wiki)

    #some wiki pages have multiple Changes/Updates tables
    additional_changes_table = changes_section.find_next('table', {"class": "wikitable"})

    #concatenate both updates table to 1 dataframe, if applicable
    if (additional_changes_table != None):
        #convert secondary table into 2D array
        temp_iso3166_table = table_to_array(additional_changes_table, soup)
        #several tables have extra unwanted cols meaning we ignore those tables
        if not any(col.lower().rstrip(".") in ['former code', 'in region', 'before'] for col in temp_iso3166_table[0]):
            temp_iso3166_df_wiki = parse_updates_table(alpha2, temp_iso3166_table)
            #concat two dataframes together
            iso3166_df_wiki = pd.concat([iso3166_df_wiki, temp_iso3166_df_wiki], axis=0)

        #dataframe might need resorted by Date after concatenation with second Changes table
        iso3166_df_wiki = iso3166_df_wiki.assign(
            SortDate=pd.to_datetime(iso3166_df_wiki['Date Issued'].str.extract(r'^(\d{4}-\d{2}-\d{2})')[0], errors='coerce')
        ).sort_values(by='SortDate', ascending=False).drop(columns=['SortDate']).reset_index(drop=True)

    #convert columns in dataframe to string
    iso3166_df_wiki = iso3166_df_wiki.astype(str)

    return iso3166_df_wiki

def get_updates_df_selenium(alpha_code: str, include_remarks_data: bool=True) -> pd.DataFrame:
    """
    Pull all related ISO 3166 updates/changes for a given input country from the official ISO
    website. The Selenium Chromedriver tool is utilised prior to the BS4 web scraper as JavaScript
    has to run on the site to get the data. Various random steps are implemented during execution
    of the Chromedriver to avoid requests being blocked. The changes section for each country is
    parsed and converted into a 2D table and then a DataFrame. Additional info may be pulled from
    the ISO page, including any "remarks" in the country summary table.

    Parameters
    ==========
    :alpha_code: str
        single string of an alpha ISO 3166-1 country code to get the latest ISO 3166 updates for. 
        If the 3 letter alpha-3 or numeric code are input then convert to alpha-2.
    :include_remarks_data: bool (default=True)
        whether to include the remarks text in country updates export. Remarks are additional 
        notes on the change published by the ISO and are prevalent throughout the ISO pages;
        sometimes the remarks may be split up until parts (1 to 4). If True then the remarks 
        data will be parsed and added in brackets after their mention. By default the remarks
        are added to ensure all the info is captured from the updates data.

    Returns
    =======
    :iso3166_df_selenium: pd.DataFrame
        converted pandas dataframe of all ISO 3166 changes for particular country/countries
        from official ISO website.
    :remarks_data: dict
        country updates remarks data from ISO page, parts 1 to 4, where applicable. 
    
    Raises
    ======
    ValueError:
        Invalid alpha-2 country code input.
    RuntimeError:
        Error when parsing country's ISO updates data.
    """
    #initialise dataframe to hold updates data obtained from ISO pages
    iso3166_df_selenium = pd.DataFrame()
    
    #validate alpha code, convert to alpha-2 if required
    alpha2 = convert_to_alpha2(alpha_code)
    
    #parse Changes section table on webpage, using the header of the section
    changes_section = None

    #counter that determines the max number of retries for the Selenium function, retry required if an error occurs when accessing the html of a country's ISO page
    selenium_retry_attempts = 3

    #selenium factor by which the wait time increases after each retry of create driver function
    backoff_factor = 2
    
    #base URL for country ISO pages
    iso_base_url = "https://www.iso.org/obp/ui/en/#iso:code:3166:"

    #try parsing the updates data on the page, with multiple retries, if retry limit reached then raise error 
    while (selenium_retry_attempts > 0 and changes_section == None):
      #initialise driver object before try block
      driver = None
      try:
        #add recursive backoff on multiple attempts 
        if (selenium_retry_attempts != 3):
            wait_time = backoff_factor * (2 ** (selenium_retry_attempts - 1)) + random.uniform(0, 1)
            print(f"Attempt {selenium_retry_attempts} failed: {e}. Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)

        #create instance of chromedriver
        driver = create_driver()

        #create session for input country's ISO section
        driver.get(iso_base_url + alpha2.upper())

        #pause for 4 seconds
        # WebDriverWait(driver, 4)
        # WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        #pause for 20 seconds before searching for h3 element
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Change history of country code')] | //h3[contains(text(), 'Historique des modifications des codes de pays')]"))
            # EC.presence_of_element_located((By.XPATH, "//h3[normalize-space(text())='Change history of country code']"))
        )

        #get page html source and create parsed BeautifulSoup object
        table_html = driver.page_source
        soup = BeautifulSoup(table_html, 'html.parser')

        #random scrolling on page from 200-700px
        for i in range(3):
            driver.execute_script('window.scrollTo(0, ' + random.choice(["200", "300", "400", "500", "600", "700"]) + ')')
            time.sleep(1)

        #pause for 2.5 seconds
        # time.sleep(2.5)

        #have to run below code again to get page html source and create parsed BeautifulSoup object, seems to be error in page loading time
        table_html = driver.page_source
        soup = BeautifulSoup(table_html, 'html.parser')

        #extract embedded table element in h3/h2 headers
        for header in soup.find_all(["h3", "h2"]):
            if (('change history of country code' in header.text.lower()) or ('historique des modifications des codes de pays' in header.text.lower())):
                changes_section = header.find_next("table")
                break

        #break to next while loop iteration if Changes html table data is blank
        if not (changes_section):
            print (f"No Changes section found for {alpha2} on page: {iso_base_url + alpha2.upper()}.")
            return pd.DataFrame

        #convert html table into 2D array
        changes_section_converted = table_to_array(changes_section, soup)
        
        #convert 2D array of updates into dataframe, fix columns, remove duplicate rows etc
        iso3166_df_selenium = parse_updates_table(alpha2, changes_section_converted)

      #decrement counter, raise exception if recursive threshold has been reached
      except Exception as e:
        selenium_retry_attempts -= 1
        if selenium_retry_attempts == 0:
            raise RuntimeError(f"Failed to parse ISO page for {alpha2} at URL {iso_base_url + alpha2.upper()} after 3 attempts:\n\n{e}.")
      finally:
        #always close the WebDriver session, raise an error if driver is None which means error when creating it
        if ('driver' in locals() and driver is not None):
            driver.quit()
        else:
            raise RuntimeError(f"Failed to initialise a Chromedriver instance for {alpha2} at URL {iso_base_url + alpha2.upper()}.")

    #swapping the Change and Description of Change values from ISO page
    if not (iso3166_df_selenium.empty):
        #create a mask of rows where the "Change" column is empty
        empty_change_mask = iso3166_df_selenium["Change"] == ""

        #swap Change and Description of Change if Change is empty
        iso3166_df_selenium.loc[empty_change_mask, "Change"] = iso3166_df_selenium["Description of Change"]

        #for rows that have been swapped, set Description of Change to empty
        iso3166_df_selenium.loc[empty_change_mask, "Description of Change"] = ""

    #initialise remarks object
    remarks_data = {}

    if (include_remarks_data):
        if not (iso3166_df_selenium.empty):
            #find remarks table html, if applicable
            country_summary_table = soup.find(class_='core-view-summary')
            iso3166_df_selenium, remarks_data = parse_remarks_table(iso3166_df_selenium, country_summary_table)

    return iso3166_df_selenium, remarks_data

def parse_updates_table(alpha2: str, iso3166_updates_table: list) -> pd.DataFrame:
    """
    Convert columns/headers using correct naming conventions, correct Date column into correct
    format, translate any unicode arrows in the text to normal arrow (->), fill any null rows.
    Some listed updates are "corrected" at a later date after publication; to keep track of
    these corrections the "Corrected Date Issued" and "Corrected Date" columns are used but
    later removed from the output dataframe. Correct Source attribute into correct format. If
    the Change attribute is empty, swap the data from the Desc of Change attribute to it.

    Parameters
    ==========
    :alpha2: str
        2 letter ISO 3166-1 alpha-2 country code.
    :iso3166_updates_table: list
        2D array updates/changes table from wiki page or official ISO website.

    Returns
    =======
    :iso3166_df: pd.DataFrame
        converted pandas dataframe of all ISO 3166 changes for particular country/countries
        from respective wiki or ISO pages.
    
    Raises
    ====== 
    TypeError:
        If an empty list for the updates table parameter input.
    """
    #raise error if input updates table isn't an array/list or empty
    if not isinstance(iso3166_updates_table, list) or not iso3166_updates_table:
        raise TypeError(f"Expected a non-empty list for updates table, got {type(iso3166_updates_table)}.")

    #lambda function to translate any occurrences of unicode arrow â†’ to normal arrow ->
    correct_arrow_lambda = lambda table: [[elem.replace('→', '->') for elem in entry if isinstance(elem, str)] for entry in table]

    #translate unicode arrow â†’ to normal arrow -> in table text, using lambda function
    iso3166_updates_table = correct_arrow_lambda(iso3166_updates_table)

    #update column names to correct naming conventions
    cols = correct_columns(iso3166_updates_table[0])

    #convert 2D array into dataframe
    iso3166_df = pd.DataFrame(iso3166_updates_table[1:], columns=cols)

    #add temporary column that has the "corrected" date for the update, if applicable
    iso3166_df["Corrected Date Issued"] = iso3166_df["Date Issued"].apply(extract_corrected_date)

    #remove "corrected" date from main Date Issued column, if applicable 
    iso3166_df["Date Issued"] = iso3166_df["Date Issued"].apply(remove_corrected_date)

    #parse main date in Date Issued column into '%Y-%m-%d' format
    iso3166_df["Date Issued"] = iso3166_df["Date Issued"].apply(parse_date)

    #fill any None/Null entries in dataframe with ""
    iso3166_df.fillna("", inplace=True)

    #sort dataframe by publication date descending
    iso3166_df.sort_values(by=['Date Issued'], ascending=False, inplace=True)
    
    #convert date attributes from datetime object to a str
    iso3166_df["Date Issued"] = iso3166_df["Date Issued"].astype(str)
    iso3166_df["Corrected Date Issued"] = iso3166_df["Corrected Date Issued"].astype(str)

    #concatenate Corrected Date Issued to Date Issued column if not empty
    iso3166_df["Date Issued"] = iso3166_df.apply(
        lambda row: f"{row['Date Issued']} {row['Corrected Date Issued']}".strip()
        if row["Corrected Date Issued"] else row["Date Issued"],
        axis=1
    )

    #add below columns if not present so all dataframes follow same format
    if ("Source" not in iso3166_df):
        iso3166_df["Source"] = ""
    if ("Change" not in iso3166_df):
        iso3166_df["Change"] = ""
    if ("Description of Change" not in iso3166_df):
        iso3166_df["Description of Change"] = ""

    #if source column empty or not in correct format, add link to country's OBP source 
    iso3166_df['Source'] = iso3166_df['Source'].apply(lambda val: "" if 'Online Browsing Platform (OBP)' in val else val)
    iso3166_df["Source"] = iso3166_df["Source"].replace('', f"Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:{alpha2}.", regex=True)
    # iso3166_df["Source"] = iso3166_df["Source"].str.replace('Browsing.', "Browsing")
    iso3166_df["Source"] = iso3166_df["Source"].str.replace('Browsing.', "Browsing", regex=False)
    iso3166_df["Source"] = iso3166_df["Source"].str.replace('BrowsingPlatform', "Browsing Platform", regex=False)
    iso3166_df["Source"] = iso3166_df["Source"].str.replace('Platform (OBP).', f"Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:{alpha2}.", regex=False)

    #remove any double spacing from all columns
    iso3166_df['Change'] = iso3166_df['Change'].apply(remove_extra_spacing)
    iso3166_df['Description of Change'] = iso3166_df['Description of Change'].apply(remove_extra_spacing)
    iso3166_df['Source'] = iso3166_df['Source'].apply(remove_extra_spacing)

    #create a mask of rows where the "Change" column is == (TBD) as seen on several wiki pages
    tbd_change_mask = iso3166_df["Change"] == "(TBD)."

    #swap Change and Description of Change if Change is empty
    iso3166_df.loc[tbd_change_mask, "Change"] = iso3166_df["Description of Change"]

    #for rows that have been swapped, set Description of Change to empty
    iso3166_df.loc[tbd_change_mask, "Description of Change"] = ""

    #reorder/reindex the columns
    iso3166_df = iso3166_df.reindex(columns=['Change', 'Description of Change', 'Date Issued', 'Source'])

    return iso3166_df

def parse_remarks_table(iso3166_df_: pd.DataFrame, country_summary_table: Tag) -> pd.DataFrame:
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
    
    Raises
    ======
    TypeError:
        Input parameter isn't a DataFrame. 
    """
    #return main original dataframe if summary table empty
    if (country_summary_table) is None:
        return iso3166_df_

    #raise error if input parameter isn't a dataframe
    if not (isinstance(iso3166_df_, pd.DataFrame)):
        raise TypeError(f"Input updates data object should be a DataFrame, got {type(iso3166_df_)}.")
    
    #object to store all remarks - part 1, 2, 3 and 4 if applicable
    remarks_ = {"part1": "", "part2": "", "part3": "", "part4": ""}

    #iterate through data columns on ISO summary table, append any remarks to object, if applicable
    for elem in country_summary_table:
        #check if html element is a bs4.Tag element, get its column name
        if isinstance(elem, Tag):
            column_name = elem.find(class_="core-view-field-name").text.lower()

            def parse_remarks_column_value(col_elem):
                """ Parse remarks from column class element. """
                #get column value from html class element, remove whitespace
                column_value = re.sub(' +', ' ', col_elem.find(class_="core-view-field-value").text.replace("\n", "").replace('"', "'").strip())
                if (column_value != "" and column_value != None):
                    #remove full stop at end of string, if applicable
                    if (column_value[-1] == "."):
                        column_value = column_value[:-1]
                return column_value

            #parse remarks data from column in ISO page
            column_value = parse_remarks_column_value(elem)

            #iterate overall all potential remarks from summary table, adding each to dict 
            for part_num in range(1, 5):  
                if column_name == f"remark part {part_num}":
                    remarks_[f"part{part_num}"] = column_value

    #if no remarks found, return original input object
    if (all(value == "" for value in remarks_.values())):
        return iso3166_df_, remarks_

    #sort dataframe via the date column
    iso3166_df_.sort_values(by=['Date Issued'], ascending=False, inplace=True)

    return iso3166_df_, remarks_

def remove_duplicates(iso3166_updates_df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate update objects rows. There is 3 criterion for what objects are
    regarded as duplicates in the output object:
    1. Matching 'Change' + 'Description of Change' + 'Date Issued'
    2. Matching 'Change' + 'Date Issued'
    3. Matching 'Description of Change' + 'Date Issued'

    If a corrected date exists and overlaps with another Date Issued value,
    the record with the corrected date is retained, and the other is removed.

    Parameters:
    ==========
    :iso3166_updates_df: pd.DataFrame:
        The DataFrame containing ISO 3166 updates data.

    Returns:
    ========
    :pd.DataFrame:
        DataFrame with duplicates removed based on the corrected date logic.
    """
    #object to store duplicate records 
    records_by_key = {}

    def extract_dates(date_str):
        """ Auxiliary function for extracting all date values from 'Date Issued', including corrected ones. """
        return re.findall(r"\d{4}-\d{2}-\d{2}", date_str)

    def get_completeness_score(row):
        """ Auxiliary function that returns a score based on how complete the row is (more fields = higher score). """
        return sum(bool(str(row[col]).strip()) for col in ["Change", "Description of Change", "Source", "Date Issued"])

    #iterate over rows and search for duplicates using removal logic
    for _, row in iso3166_updates_df.iterrows():
        change = row["Change"].strip().lower()
        desc_change = row["Description of Change"].strip().lower()
        date_issued = row["Date Issued"].strip()

        #keys for duplicate detection
        key1 = (change, desc_change, date_issued)  #Change + Desc Change + Date
        key2 = (change, date_issued)  #Change + Date
        key3 = (desc_change, date_issued)  #Desc Change + Date

        def store_record(key):
            """ Stores or updates record based on completeness. """
            if key in records_by_key:
                existing_entry = records_by_key[key]
                #keep the most complete entry
                if get_completeness_score(row) > get_completeness_score(existing_entry):
                    records_by_key[key] = row  
            else:
                records_by_key[key] = row

        #pass current row to store most completed row 
        store_record(key1)
        store_record(key2)
        store_record(key3)

    #convert to DataFrame
    deduplicated_df = pd.DataFrame(records_by_key.values())

    #object to store duplicate records by date 
    records_by_date = {}

    #iterate over all rows, searching for duplicates based on similar dates + corrected dates
    for _, row in deduplicated_df.iterrows():
        date_issued = row["Date Issued"]
        date_list = extract_dates(date_issued)

        #check if any date in this row already exists in our records
        existing_key = None
        for key, existing_entry in records_by_date.items():
            existing_dates = extract_dates(existing_entry["Date Issued"])
            if any(date in existing_dates for date in date_list):
                existing_key = key
                break
        
        #duplicate date found 
        if existing_key:
            existing_entry = records_by_date[existing_key]

            #prefer the entry with "corrected" in its Date Issued field, meaning it has more complete date data
            if "corrected" in date_issued.lower() and "corrected" not in existing_entry["Date Issued"].lower():
                records_by_date[existing_key] = row 
            elif "corrected" not in date_issued.lower() and "corrected" in existing_entry["Date Issued"].lower():
                pass 
            else:
                #keep the more complete entry (fewer empty fields)
                if row.count() > existing_entry.count():
                    records_by_date[existing_key] = row
        else:
            records_by_date[tuple(date_list)] = row  
    
    return pd.DataFrame(records_by_date.values())

def convert_to_alpha2(alpha_code: str) -> str:
    """ 
    Auxiliary function that converts an ISO 3166 country's 3 letter alpha-3 
    or numeric country code into its 2 letter alpha-2 counterpart. The 
    function also validates the input alpha-2 or converted alpha-2 code, 
    raising an error if it is invalid. 

    Parameters 
    ==========
    :alpha_code: str
        3 letter ISO 3166-1 alpha-3 or numeric country code.
    
    Returns
    =======
    :iso3166.countries_by_alpha3[alpha_code].alpha2|iso3166.countries_by_numeric[alpha_code].alpha: str
        2 letter ISO 3166 alpha-2 country code. 
    
    Raises
    ======
    TypeError:
        Invalid data type for alpha code parameter input.
    ValueError:
        Issue converting the inputted alpha code into alpha-2 code.
    """
    #raise error if invalid type input
    if not (isinstance(alpha_code, str)):
        raise TypeError(f"Expected input alpha code to be a string, got {type(alpha_code)}.")

    #uppercase alpha code, remove leading/trailing whitespace
    alpha_code = alpha_code.upper().strip()
    
    #use iso3166 package to find corresponding alpha-2 code from its numeric code, return error if numeric code not found
    if (alpha_code.isdigit()):
        if not (alpha_code in list(iso3166.countries_by_numeric.keys())):
            raise ValueError(f"Invalid alpha numeric country code input {alpha_code}.")
        return iso3166.countries_by_numeric[alpha_code].alpha2

    #return input alpha code if its valid, return error if alpha-2 code not found
    if len(alpha_code) == 2:
        if not (alpha_code in list(iso3166.countries_by_alpha2.keys())):
            raise ValueError(f"Invalid alpha-2 country code input {alpha_code}.")
        return alpha_code

    #use iso3166 package to find corresponding alpha-2 code from its alpha-3 code, return error if code not found
    if len(alpha_code) == 3:
        if not (alpha_code in list(iso3166.countries_by_alpha3.keys())):
            raise ValueError(f"Invalid alpha-3 country code: {alpha_code}.")
        return iso3166.countries_by_alpha3[alpha_code].alpha2
    
    #return error by default if input code not returned already
    raise ValueError(f"Invalid alpha country code input {alpha_code}.")                      

def correct_columns(cols: list) -> list:
    """
    Update column names so all dataframes follow the column format of: ["Change", 
    "Description of Change", "Date Issued", "Source"].

    Parameters
    ==========
    :cols: list
        list of column names from header of parsed Changes table on wiki.

    Returns
    =======
    :renamed_cols: list
        list of columns updated to correct naming conventions.
    
    Raises
    ======
    TypeError:
        Input columns parameter isn't of type list.
    """
    #raise error if input columns are not in a list
    if not (isinstance(cols, list)):
        raise TypeError("Input column variable should be a list.")

    #return empty list if input list is empty
    if not cols:
        return cols

    #renaming rules in order of precedence
    rename_rules = {
        "Edition/newsletter": "Source",
        "Edition/Newsletter": "Source",
        "Newsletter/OBP": "Source",
        "Newsletter": "Source",
        "newsletter": "Source",
        "Edition": "Source",
        "Publication": "Source",
        "Date issued": "Date Issued",
        "Description": "Description of Change", 
        "Effective date of change": "Date Issued",
        "effective date of change": "Date Issued",
        "Effective date": "Date Issued",
        "Date of change": "Date Issued",
        "Date of Change": "Date Issued",
        "date issued": "Date Issued",
        "Short description of change (en)": "Description of Change",
        "Short description of change": "Description of Change",
        "Description of change": "Description of Change",
        "Description of Change in newsletter": "Description of Change",
        "Description of change in newsletter": "Description of Change",
        "description of change in newsletter": "Description of Change",
        "short description of change (en-gb)": "Description of Change",
        "Changes made": "Change",
        "Changes Made": "Change",
        "change": "Change",
        "Changes": "Change",
        "Code/Subdivision Change": "Change",
        "Code/Subdivision change": "Change",
        "Code/subdivision change": "Change",
        "Code/subdivision Change": "Change",
        "code/subdivision change": "Change",
        "code / subdivision change": "Change"
    }

    #apply column renaming rules in order
    renamed_cols = []
    for col in cols:
        col_cleaned = col.strip().rstrip(".")  # Remove full stop at end
        renamed_cols.append(rename_rules.get(col_cleaned, col_cleaned))  

    return renamed_cols

def table_to_array(table_tag: Tag, soup: BeautifulSoup) -> tuple:
    """
    Convert HTML table into 2D array, including any embedded links and citations.

    Parameters
    ==========
    :table_tag: bs4.element.Tag
        BS4 Tag object of table element.
    :soup: bs4.BeautifulSoup
        The parsed BeautifulSoup object of the entire page, used to resolve citation links.

    Returns
    =======
    :table: tuple
        2D list of parsed rows and cell values from the HTML table.

    Raises
    ======
    TypeError
        Invalid type for input html table object.
    """
    #return empty array if table tag empty
    if table_tag is None:
        return []

    #raise error if invalid html table type input
    if not isinstance(table_tag, Tag):
        raise TypeError(f"Input table object must be of type bs4.element.Tag, got {type(table_tag)}.")

    #iterate over all rows (<tr>) and calculate and resolve rowspans/colspans
    rowspans = []
    rows = table_tag.find_all('tr')
    colcount = 0
    for r, row in enumerate(rows):
        cells = row.find_all(['td', 'th'], recursive=False)
        colcount = max(
            colcount,
            sum(int(c.get('colspan', 1)) or 1 for c in cells[:-1]) + len(cells[-1:]) + len(rowspans))
        rowspans += [int(c.get('rowspan', 1)) or len(rows) - r for c in cells]
        rowspans = [s - 1 for s in rowspans if s > 1]

    #initialize the 2D array to hold table data
    table = [[None] * colcount for _ in rows]
    rowspans = {}

    #iterate over all table rows (<tr>), extract cell values from tr td table elements 
    for row, row_elem in enumerate(rows):
        span_offset = 0
        for col, cell in enumerate(row_elem.find_all(['td', 'th'], recursive=False)):
            col += span_offset
            while rowspans.get(col, 0):
                span_offset += 1
                col += 1

            #get rowspan and colspan values, default to full span if not specified
            rowspan = rowspans[col] = int(cell.get('rowspan', 1)) or len(rows) - row
            colspan = int(cell.get('colspan', 1)) or colcount - col
            span_offset += colspan - 1

            ## Replace breakpoints <br> at end of lines with a full stop for continuity ##

            # convert <br>, </br> and <br/> tags to a unique placeholder before extracting text
            for br in cell.find_all("br"):
                br.replace_with("|||") 

            #extract text after replacing <br> tags
            value = cell.get_text().strip()

            #use regex to ensure <br> placeholders are replaced with ". " only after sentences, they shouldn't appear after ":", replace remaining ||| placeholders with space
            value = re.sub(r'(\w[^\.\n:])\|\|\|', r'\1. ', value) 
            value = re.sub(r':\s*\|\|\|', ': ', value) 
            value = value.replace("|||", " ")  


            #clean up spaces and double punctuation during regex conversion
            value = re.sub(r'\.\s*\.', '.', value)  
            value = re.sub(r'\s+', ' ', value).strip()  
            
            #add full stop to end of sentences
            if value and not value.endswith("."):
                value += "."

            #extract links from the cell
            links = cell.find_all('a', href=True)

            #add links to the cell text data
            link_texts = []
            for link in links:
                href = link['href']
                if not href.startswith('/wiki/'):  #ignore internal wiki links
                    link_texts.append(href)

            #remove citation brackets from text, if applicable
            value = re.sub(r'\[\s*\d+\s*\]', '', value).strip()

            #check for citation links and extract, if applicable (e.g., #cite-note-3)
            citation_link = next((link for link in links if link['href'].startswith('#cite_note')), None)
            if citation_link:
                citation_id = citation_link['href'].lstrip('#')

                #find the corresponding citation element in the References section
                citation_elem = soup.find(id=citation_id)
                if citation_elem:
                    link_texts.clear()

                    #look for all links within the citation element
                    citation_links = citation_elem.find_all('a', href=True)
                    link_texts = [
                        f"{citation_link.get_text(strip=True)} - {citation_link['href']}"
                        for citation_link in citation_links if citation_link['href'].startswith('http')
                    ]
        
            #append links to the value if applicable, strip brackets and "-""
            if link_texts:
                value = value.lstrip(" (")
                value += " - " + ", ".join(link_texts)
                value = value.lstrip(" - ")

            #remove any brackets, single or double quotations, any instances of "." before hyphen, "." before open bracket or "->"
            # value = value.strip("()").replace('""', '').replace('"', '').replace(". -", " -").replace(".-", " -") \
            #     .replace(".-", " -").replace(". (", " (").replace(". →", " →")
            value = value.strip("[]").replace('""', '').replace('"', "'").replace(". -", " -").replace(".-", " -") \
                .replace(".-", " -").replace(". (", " (").replace(". →", " →").replace(" :", ":").replace(" ;", ";")\
                    .replace(" .", ".").replace("(see below)", '')

            def ensure_balanced_parentheses(value: str) -> str:
                """
                Auxiliary function that ensures parentheses in the text are balanced. 
                Add a closing parenthesis if needed.
                """
                #count number of open & close brackets
                open_count = value.count("(")
                close_count = value.count(")")
                
                #add closing parenthesis if there's an unmatched opening one
                if open_count > close_count:
                    return value + ")"
                return value
            
            #ensure open brackets have matching closed one
            value = ensure_balanced_parentheses(value)

            #add full stop at the end of text, if applicable
            if row != 0 and value and not value.endswith('.'):
                value += "."

            #fill the table array with the cell content, accounting for rowspan and colspan
            for drow, dcol in product(range(rowspan), range(colspan)):
                try:
                    table[row + drow][col + dcol] = value
                    rowspans[col + dcol] = rowspan
                except IndexError:
                    pass

        #update rowspan values for the next row
        rowspans = {c: s - 1 for c, s in rowspans.items() if s > 1}

    #clean up table content by removing newline characters
    for row in range(len(table)):
        for col in range(len(table[row])):
            if table[row][col]:
                table[row][col] = table[row][col].replace('\n', "")

    #remove any "." from end of first embedded list which is the list of columns
    if (table):
        table[0] = [item.rstrip('.') for item in table[0]]

    return table

def parse_date(date_str: str) -> str:
    """ 
    Convert a string date into '%Y-%m-%d' (YYYY-MM-DD) format. Handles multiple date formats, 
    including e.g. 20 August 2002, 20/08/2002, 2014-05-09 etc. 
    
    Parameters
    ========== 
    :date_str: str
        input date string to be converted into YYYY-MM-DD format.
    
    Returns
    ====== 
    :date_str: str
        inputted date, converted into YYYY-MM-DD format.
    
    Raises
    ======
    ValueError:
        Unsupported date format.
    """
    #remove any date suffixes (st, nd, rd, th), if applicable for '%d %B %Y' format, remove leading/trailing spaces and trailing full stops
    # if any(suffix in date_str for suffix in ["st", "nd", "rd", "th"]):
    # date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str.strip().rstrip("."))

    #list of accepted data formats
    date_formats = ['%Y-%m-%d', '%d %B %Y', '%Y-%d-%m', '%d/%m/%Y', '%d-%m-%Y']

    #iterate over each date format, identifying which format the input date str is
    for fmt in date_formats:
        try:
            #parse the date
            parsed_date = datetime.strptime(date_str, fmt)
            
            #handle potential '%Y-%d-%m' ambiguity (month in day position, vice versa)
            if fmt == '%Y-%d-%m':
                day = int(date_str.split('-')[1])  
                #if day is greater than 12, swap day and month
                if day > 12: 
                    return parsed_date.strftime('%Y-%m-%d')
                else:
                    raise ValueError(f"Invalid %Y-%d-%m date format: {date_str}.")
            
            #return the date in '%Y-%m-%d' for other formats
            return parsed_date.strftime('%Y-%m-%d')
        #go to next date format and try converting again
        except ValueError:
            continue
    raise ValueError(f"Date format not recognized: {date_str}.")

def extract_corrected_date(row: str) -> str:
    """ 
    Extract new date from row if date of changes has been "corrected", remove any 
    full stops/punctuation and whitespace. 

    Parameters
    ========= 
    :row: str
        row/string to parse corrected date value from.

    Returns
    =======
    :match.group(1).strip()|"": str
        "corrected" date from publication date in row. If no "corrected" date in
        string then an empty string is returned.
    """
    match = re.search(r"\(corrected ([^)]+)\)", row.replace(".", ''))
    return f"(corrected {match.group(1).strip()})" if match else ""

def remove_corrected_date(row: str) -> str:
    """ 
    Parse original date and temporarily remove "corrected" date, remove any full 
    stops/punctuation and whitespace. 

    Parameters
    ========= 
    :row: str
        row/string to remove corrected date value from.

    Returns
    =======
    :re.sub(r'\s+', ' ', cleaned_row.replace('.', '').strip()): str
        row date string with corrected date removed.
    """
    #remove corrected date text within parentheses (e.g., "(corrected ...)")
    cleaned_row = re.sub(r"\(.*?\)", "", row.replace(".", ''))
    #remove punctuation, full stops and normalize whitespace
    return re.sub(r'\s+', ' ', cleaned_row.strip())

def remove_extra_spacing(row: str):
    """ 
    Remove extra spacing from string. 
    
    Parameters
    ==========
    :row: str
        input string.
        
    Returns
    =======
    :re.sub(' +', ' ', row): str
        string with extra spacing removed. 
    """
    return re.sub(' +', ' ', row)

def add_remarks_data(iso3166_df: pd.DataFrame, remarks_data: dict, add_once_per_part: bool=False) -> pd.DataFrame:
    """
    Append any remarks for a country's updates to their Change or Description of 
    Change attribute, as per the country's ISO page. These remarks are supplementary 
    info on the specific update and are split into parts, usually 1 to 3. By default, 
    the remarks are appended to the end of each update where they are mentioned but 
    if the parameter add_once_per_part is set to True, the individual remarks will 
    only be appended once per country updates object. The remarks data is separately 
    parsed from the get_updates_df_selenium function.

    Parameters
    ==========
    :iso3166_df: pd.DataFrame
        input dataframe of individual country ISO 3166 updates.
    :remarks_data: dict
        parsed remarks data parts for individual country, if applicable.
    :add_once_per_part: bool (default=False)
        if True, only add the individual remarks data once per country
        updates object, otherwise they will be appended to each instance
        of the remarks. 

    Returns
    =======
    :iso3166_df: pd.DataFrame
        input dataframe of individual country ISO 3166 updates, with 
        the remarks data appended, if applicable.

    Raises
    ======
    TypeError:
        Input updates data isn't a dataframe.
    """
    #set that maintains if the current remarks part has been added
    globally_added_parts = set()

    #iterate over each row in dataframe, append remarks data to each applicable attribute 
    for index, row in iso3166_df.iterrows():
        #parse change attribute values for current row
        change_text = (row.get("Change") or "").strip().rstrip('.')
        desc_of_change_text = (row.get("Description of Change") or "").strip().rstrip('.')

        updated_change = change_text
        updated_desc = desc_of_change_text

        #iterate over each remark part (1 to 4), add remarks data where individual remark part found
        for part_num in range(1, 5):
            part_key = f"part{part_num}"
            remark_key = f"remark part {part_num}"
            #search for current remark part using regex
            pattern = rf"{re.escape(remark_key)}(?=[\s;:.,)]|$)"
            remark_value = remarks_data.get(part_key)

            #skip to next remark part if current one not found
            if not remark_value:
                continue
            
            #remark text to be appended to attribute
            remark_text = f"(Remark part {part_num}: {remark_value})"

            #add once globally if flag is set, go to next iterationj
            if (add_once_per_part and part_key in globally_added_parts):
                continue
            
            #if remark found in current Change attribute value, append to it
            if re.search(pattern, change_text.lower()) and remark_text not in updated_change:
                updated_change += f". {remark_text}"
                if add_once_per_part:
                    globally_added_parts.add(part_key)

            #if remark found in current Desc of Change attribute value, append to it
            if re.search(pattern, desc_of_change_text.lower()) and remark_text not in updated_desc:
                updated_desc += f". {remark_text}"
                if add_once_per_part:
                    globally_added_parts.add(part_key)

        #add final full stop to attribute if needed
        if (updated_change and not updated_change.endswith('.')):
            updated_change += '.'
        if (updated_desc and not updated_desc.endswith('.') and updated_desc != ""):
            updated_desc += '.'

        #add new Change or Desc of Change value to dataframe
        iso3166_df.at[index, "Change"] = updated_change
        iso3166_df.at[index, "Description of Change"] = updated_desc

    return iso3166_df

def manual_updates(iso3166_updates: dict) -> dict:
    """
    Nothing's perfect, and that includes the data on the wiki and ISO page. 
    This is a temporary function that completes several manual data fixes to 
    the updates data, due to a spelling, grammar or format mistakes on the 
    exported data from the data sources. The function will be removed in  
    a later version of the software.  

    Parameters
    ==========
    :iso3166_updates: dict
        exported updates dict to add manual changes to. 

    Returns
    =======
    :iso3166_updates: dict
        exported updates dict with manual changes added to it.
    """
    #updates data that needs to be manually added to object, if there is an Add attribute the full object needs to be added, if there is Delete the object will be deleted, otherwise just the individual attribute values per object will be changed
    manual_updates = {"AE": [{"Date Issued": "2015-11-27", "Change": "Change of spelling of AE-AJ, AE-RK; addition of local variation of AE-FU, AE-RK, AE-UQ; update List Source."}],
                            "CN": [{"Date Issued": "2017-11-23", "Description of Change": "Change of subdivision code from CN-15 to CN-NM, CN-45 to CN-GX, CN-54 to CN-XZ, CN-64 to CN-NX, CN-65 to CN-XJ, CN-11 to CN-BJ, CN-12 to CN-TJ, CN-31 to CN-SH, CN-50 to CN-CQ, CN-13 to CN-HE, CN-14 to CN-SX, CN-21 to CN-LN, CN-22 to CN-JL, CN-23 to CN-HL, CN-32 to CN-JS, CN-33 to CN-ZJ, CN-34 to CN-AH, CN-35 to CN-FJ, CN-36 to CN-JX, CN-37 to CN-SD, CN-41 to CN-HA, CN-42 to CN-HB, CN-43 to CN-HN, CN-44 to CN-GD, CN-46 to CN-HI, CN-51 to CN-SC, CN-52 to CN-GZ, CN-53 to CN-YN, CN-61 to CN-SN, CN-62 to CN-GS, CN-63 to CN-QH, CN-71 to CN-TW, CN-91 to CN-HK, CN-92 to CN-MO; change of subdivision name of CN-NM, CN-GX, CN-XZ, CN-NX, CN-XJ, CN-BJ, CN-TJ, CN-SH, CN-CQ, CN-HE, CN-SX, CN-LN, CN-JL, CN-HL, CN-JS, CN-ZJ, CN-AH, CN-FJ, CN-JX, CN-SD, CN-HA, CN-HB, CN-HN, CN-GD, CN-HI, CN-SC, CN-GZ, CN-YN, CN-SN, CN-GS, CN-QH, CN-TW, CN-HK, CN-MO; addition of remark in parentheses to subdivision name for CN-HK, CN-MO in eng; addition of region CN-MO in por; update Code Source; update List Source."}],
                            "CZ": [{"Date Issued": "2016-11-15", "Description of Change": "Addition of category name of “capital city” in eng, fra, ces; change of subdivision category of CZ-10 from region to capital city; change of spelling of CZ-802, CZ-806, CZ-63; typographical correction of CZ-615; addition of districts CZ-116 to CZ-122; change of parent subdivision from CZ-JC to CZ-31, CZ-JM to CZ-64, CZ-KA to CZ-41, CZ-KR to CZ-52, CZ-LI to CZ-51, Z-O to CZ-80, CZ-OL to CZ-71, CZ-PA to CZ-53, CZ-PL to CZ-32, CZ-ST to CZ-20, CZ-US to CZ-42, CZ-VY to CZ-63, CZ-ZL to CZ-72; change of subdivision code from CZ-621 to CZ 641, CZ-624 to CZ 644; CZ-622 to CZ 642, CZ-623 to CZ 643, CZ‐625 to 645, CZ-611 to CZ 631, CZ-612 to CZ 632, CZ-613 to CZ 633, CZ-10A to CZ 110, CZ-10B to CZ 111, CZ-10C to CZ 112, CZ-10D to CZ 113, CZ-10E to CZ 114, CZ-10F to CZ 115, CZ-614 to CZ 634, CZ-626 to CZ 646, CZ-615 to CZ 635, CZ-627 to CZ 647, CZ-PR to CZ-10; update List Source."}],
                            "GB": [{"Date Issued": "2014-10-30", "Change": "Add GB-IOS."}, {"Date Issued": "2015-11-27", "Change": "Deletion of district council areas GB-ANT, GB-ARD, GB-ARM, GB-BLA, GB-BLY, GB-BNB, GB-CKF, GB-CSR, GB-CLR, GB-CKT, GB-CGV, GB-DRY, GB-DOW, GB-DGN, GB-FER, GB-LRN, GB-LMV, GB-LSB, GB-MFT, GB-MYL, GB-NYM, GB-NTA, GB-NDN, GB-OMH, GB-STB; change of subdivision category from district council area to district GB-BFS; addition of districts GB-ANN, GB-AND, GB-ABC, GB-CCG, GB-DRS, GB-FMO, GB-LBC, GB-MEA, GB-MUL, GB-NMD; update List Source."}],                            
                            "FR": [{"Date Issued": "2021-11-25", "Description of Change": "Addition of category European collectivity in eng & fra; Addition of European collectivity FR-6AE; Addition of metropolitan collectivity with special status FR-69M; Change of category name from metropolitan department to metropolitan collectivity with special status for FR-75; Change of subdivision code from FR-75 to FR-75C; Addition of category overseas departemental collectivity in eng & fra; Change of category name from overseas department to overseas departemental collectivity for FR-971, FR-974, FR-976; Addition of category overseas unique territorial collectivity in eng & fra; Change of category name from overseas department to overseas unique territorial collectivity for FR-972, FR-973; Deletion of category name overseas department; Deletion of overseas region FR-GF, FR-GP, FR-MQ, FR-RE, FR-YT; Deletion of category name overseas region; Change of parent subdivision of FR-67, FR-68; Deletion of parent subdivision of FR-971, FR-972, FR-973, FR-974, FR-976; Modification of Remark part 2; Update List Source and Code Source."}, {"Date Issued": "2016-11-15", "Change": "Correction of the OBP entry error as follows: deletion of Clipperton Island, France, Metropolitan in the name field for Territory.", "Add": 1}],
                            "IQ": [{"Date Issued": "2016-11-15", "Change": "Addition of romanization system BGN/PCGN 2007 (kur); addition of the remark; addition of governorate IQ-SU, IQ-DA, IQ-AR in kur, update list source.", "Add": 1}],
                            "ME": [{"Date Issued": "2018-03-26", "Change": "Deletion of remark part 2. (Remark part 2: Montenegro was formerly part of former entries: YUGOSLAVIA (YU, YUG, 891) then SERBIA AND MONTENEGRO (CS, SCG, 891)).", "Add": 1}],
                            "MK": [{"Date Issued": "2020-03-02", "Change": "Addition of the article 'the' before the full name.", "Add": 1}, {"Date Issued": "2020-03-02", "Change": "Deletion of municipality MK-85; Change of subdivision code from MK-02 to MK-802, MK-03 to MK-201, MK-04 to MK-501, MK-05 to MK-401, MK-06 to MK-601, MK-07 to MK-402, MK-08 to MK-602, MK-10 to MK-403, MK-11 to MK-404, MK-12 to MK-301, MK-13 to MK-101, MK-14 to MK-202, MK-16 to MK-603, MK-18 to MK-405, MK-19 to MK-604, MK-20 to MK-102, MK-21 to MK-303, MK-22 to MK-304, MK-23 to MK-203, MK-24 to MK-103, MK-25 to MK-502, MK-26 to MK-406, MK-27 to MK-503, MK-30 to MK-605, MK-32 to MK-806, MK-33 to MK-204, MK-34 to MK-807, MK-35 to MK-606, MK-36 to MK-104, MK-37 to MK-205, MK-40 to MK-307, MK-41 to MK-407, MK-42 to MK-206, MK-43 to MK-701, MK-44 to MK-702, MK-45 to MK-504, MK-46 to MK-505, MK-47 to MK-703, MK-48 to MK-704, MK-49 to MK-105, MK-50 to MK-607, MK-51 to MK-207, MK-52 to MK-308, MK-53 to MK-506, MK-54 to MK-106, MK-55 to MK-507, MK-56 to MK-408, MK-58 to MK-310, MK-59 to MK-810, MK-60 to MK-208, MK-61 to MK-311, MK-62 to MK-508, MK-63 to MK-209, MK-64 to MK-409, MK-65 to MK-705, MK-66 to MK-509, MK-67 to MK-107, MK-69 to MK-108, MK-70 to MK-812, MK-71 to MK-706, MK-72 to MK-312, MK-73 to MK-410, MK-74 to MK-813, MK-75 to MK-608, MK-76 to MK-609, MK-78 to MK-313, MK-80 to MK-109, MK-81 to MK-210, MK-82 to MK-816, MK-83 to MK-211; Typographical correction of subdivision name of MK-816, addition of municipality MK-801, MK-803, MK-804, MK-805, MK-808, MK-809, MK-811, MK-814, MK-815, MK-817; Change of subdivision name of MK-304, MK-607; Update List Source; Update Code Source."}],                            
                            "NO": [{"Date Issued": "2019-04-09", "Change": "Change of subdivision code from NO-23 to NO-50."}],
                            "SI": [{"Date Issued": "2010-06-30", "Change": "Subdivisions added: SI-195 Apače. SI-196 Cirkulane. SI-207 Gorje. SI-197 Kostanjevica na Krki. SI-208 Log-Dragomer. SI-198 Makole. SI-199 Mokronog-Trebelno. SI-200 Poljčane. SI-209 Rečica ob Savinji. SI-201 Renče-Vogrsko. SI-202 Središče ob Dravi. SI-203 Straža. SI-204 Sveta Trojica v Slovenskih goricah. SI-210 Sveti Jurij v Slovenskih goricah. SI-205 Sveti Tomaž. SI-211 Šentrupert. SI-206 Šmarješke Toplice.", "Description of Change": "Update of the administrative structure and languages and update of the list source", "Source": "Newsletter II-2 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf."}],
                            "SS": [{"Date Issued": "2011-12-13 (corrected 2011-12-15)", "Description of Change": "Addition of code and its administrative subdivisions to align ISO 3166-1 and ISO 3166-2."}],
                            "TD": [{"Date Issued": "2020-11-24", "Description of Change": "Change of subdivision category region to province; Modification of spelling for TD-BA, TD-LO, TD-LR, TD-TA, TD-WF in ara; Addition of local variation for TD-BG in fra; Addition of subdivision name of TD-EE, TD-EO in ara; Update List Source."}],
                            "TZ": [{"Date Issued": "2019-02-14", "Delete": 1}]}

    #manual updates for India, error with parsing Indian data from wiki - updated in next version release 
    manual_updates_in = [{"Change": "IN-DH Dadra and Nagar Haveli and IN-DD Diu and Daman; Addition of Indian system of transliteration.", "Description of Change": "Deletion of Union territory; Addition of Union territory; Correction of spelling; Update list source and correction of the code source.", "Date Issued": "2024-11-11", "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:IN."},
                        {"Change": "Change of subdivision code from IN-OR to IN-OD, from IN-CT to IN-CG, from IN-TG to IN-TS, from IN-UT to IN-UK; Deletion of the asterisk from IN-JH; Update Code Source.", "Description of Change": "", "Date Issued": "2023-11-23", "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:IN."},
                        {"Change": "Deletion of Union territory IN-DD, IN-DN; Addition of Union territory IN-DH; Correction of spelling for IN-AR, IN-BR, IN-CH, IN-CT, IN-DH, IN-GJ, IN-HP, IN-HR, IN-JH, IN-JK, IN-KA, IN-LA, IN-MH, IN-ML, IN-NL, IN-RJ, IN-TG, IN-TN, IN-UT; Addition of romanization system 'Indian System of Transliteration'; Update List Source; Correction of the Code Source.", "Description of Change": "", "Date Issued": "2020-11-24", "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:IN."},
                        {"Change": "Change of subdivision category from state to Union territory for IN-JK; Addition of Union territory IN-LA; Update List Source.", "Description of Change": "", "Date Issued": "2019-11-22", "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:IN."},
                        {"Change": "Add 1 state IN-TG; change spelling of IN-OR; update List Source and Code Source.", "Description of Change": "", "Date Issued": "2014-10-30", "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:IN."},
                        {"Change": "Addition of local generic administrative terms, update of the official languages according to ISO 3166-2, addition of a comment and source list update.", "Description of Change": "", "Date Issued": "2011-12-13", "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:IN."},
                        {"Change": "IN-WB West Bengal/Banga → IN-WB West Bengal.", "Description of Change": "Error correction: Reintroduction of old name form in IN-WB.", "Date Issued": "2002-12-10", "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:IN."},
                        {"Change": "IN-RJ Rajasthan → IN-RJ Rājasthān; IN-CH Chhattīsgarh → IN-CT Chhattīsgarh.", "Description of Change": "Spelling correction; Error correction: Duplicate use of IN-CH corrected.", "Date Issued": "2002-08-20", "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:IN."},
                        {"Change": "IN-CH Chhattīsgarh. IN-JH Jhārkhand. IN-UL Uttarānchal; IN-WB West Bengal → IN-WB West Bengal/Banga; As per the Indian system of transliteration; ISO 3166 Maintenance Agency.", "Description of Change": "Partial reorganization of subdivision layout with the addition of three new states; Addition of an alternative name for one state; Spelling corrections; New list source.", "Date Issued": "2002-05-21", "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:IN."}]

    def extract_date(date_str):
        """ Extract original date from Date Issued attribute in YYYY-MM-DD format. """
        #extract the original date (YYYY-MM-DD) 
        match = re.search(r"\d{4}-\d{2}-\d{2}", date_str)
        return datetime.strptime(match.group(), "%Y-%m-%d")

    #iterate over main updates object, making the changes, additions or deletions to the existing updates object 
    for country_code, updates_list in manual_updates.items():
        for update in updates_list:
            #parse individual attributes from updates object, including addition/deletion flags
            date_issued = update.get("Date Issued")
            add_flag = update.get("Add", 0)
            delete_flag = update.get("Delete", 0)
            change = update.get("Change", "")
            description = update.get("Description of Change", "")
            #create default value for Source attribute when adding a manual update
            source = update.get("Source", f"Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:{country_code}.")

            #skip to next iteration if current country code of updates isn't in the main dict
            if country_code not in iso3166_updates:
                continue
            
            #updates per country
            entries = iso3166_updates[country_code]

            #delete object from country's updates if delete attribute is set, using its date
            if delete_flag:
                iso3166_updates[country_code] = [entry for entry in entries if entry.get("Date Issued") != date_issued]
                continue

            #append new update to country updates
            if add_flag:
                iso3166_updates[country_code].append({
                    "Change": change,
                    "Description of Change": description,
                    "Date Issued": date_issued,
                    "Source": source
                })
                #skip to next iteration
                continue
            
            #iterate over individual updates, search using date, make change to relevant attribute (Change, Desc of Change or Source)
            for entry in entries:
                if entry.get("Date Issued") == date_issued:
                    if change:
                        entry["Change"] = change
                    if description:
                        entry["Description of Change"] = description
                    if source:
                        entry["Source"] = source
                    break
    
    #iterate over updates dict, resort objects by date
    for country_code, updates in iso3166_updates.items():
        updates.sort(key=lambda entry: extract_date(entry.get("Date Issued", "")), reverse=True)

    #add manual updates data for India to object
    if ("IN" in iso3166_updates):    
        iso3166_updates["IN"] = manual_updates_in

    return iso3166_updates