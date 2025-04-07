import time
import pandas as pd
import requests
import random
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from iso3166_updates_export.driver import *
from iso3166_updates_export.parse_updates_data import *
from iso3166_updates_export.utils import *

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
    #validate alpha code, convert to alpha-2 if requried
    alpha2 = convert_to_alpha2(alpha_code)

    #set random user-agent string for requests library to avoid detection, using fake_useragent package
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
        notes on the change published by the ISO and are prevelant throughout the ISO pages;
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
    
    #validate alpha code, convert to alpha-2 if requried
    alpha2 = convert_to_alpha2(alpha_code)
    
    #parse Changes section table on webpage, using the header of the section
    changes_section = None

    #counter that determines the max number of retries for the Selenium function, retry required if an error occurs when accessing the html of a country's ISO page
    selenium_retry_attempts = 3

    #selenium factor by which the wait time increases after each retry of create driver function
    backoff_factor = 2
    
    #base URL for country ISO pages
    iso_base_url = "https://www.iso.org/obp/ui/en/#iso:code:3166:"

    #try parsing the updates data on the page, with mulitple retries, if retry limit reached then raise error 
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