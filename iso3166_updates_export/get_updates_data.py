import time
import pandas as pd
import requests
import random
from typing import List, Dict
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from iso3166_updates_export.driver import *
from iso3166_updates_export.parse_updates_data import *
from iso3166_updates_export.utils import *

def get_updates_df_wiki(alpha_code: str, proxy: str=None, verbose: bool=False) -> pd.DataFrame:
    """
    Pull all related ISO 3166 updates/changes for a given input country from the country's
    respective wiki page. Selenium is not a requirement for web scraping wiki pages. Convert
    the parsed html table, from the Changes/Updates Section, into a pandas dataframe.

    Parameters
    ==========
    :alpha_code: str
        single string of an alpha ISO 3166-1 country code to get the latest ISO 3166 updates 
        for. If the 3 letter alpha-3 or numeric code are input then convert to alpha-2.
    :proxy: str (default=None)
        proxy IP to use when parsing data from wiki page via requests.get. This was implemented to 
        help the request stop getting blocked via 429 errors. By default no proxy is used.
    :verbose: bool (default=False)
        if True, display useful progress information throughout the function execution.

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

    def get_session_with_retries():
        """ Auxiliary function for creating retry/backoff factor for HTTP requests to Wiki
            in the case of 429 errors.
            
            Retry policy: up to 5 total attempts (1 initial + 4 retries) with an
            exponential backoff factor of 2 seconds (waits: 2 s, 4 s, 8 s, 16 s).
            Retries are triggered on HTTP status codes 429, 500, 502, 503 and 504.
            After the 5th failure the last exception is re-raised to the caller. """
        #crete instance of retry strategy
        retry_strategy = Retry(
            total=5,
            backoff_factor=2,  # Waits 2s, 4s, 8s, etc.
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        #create HTTP adaptor object and requests session object, mount adaptor and retry strategy 
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    #create requests session with backoff factor & retries
    session = get_session_with_retries()

    #set random user-agent string for requests library to avoid detection, using fake-useragent package
    if verbose:
        print("[Wiki] Setting up random user-agent for requests")
    user_agent = UserAgent()
    user_agent_header = user_agent.random
    
    #create proxy addresses for http & https, set to None if not using proxies
    proxy_ip = None
    if (proxy):
        proxy_ip = {"http": proxy, "https": proxy}

    #base URL for country wiki pages
    wiki_base_url = "https://en.wikipedia.org/wiki/ISO_3166-2:"

    #get html content from wiki of ISO 3166 page, raise exception if status code != 200, add proxies if using one
    try:
        time.sleep(2)
        if verbose:
            print(f"[Wiki] Fetching content from Wikipedia: {wiki_base_url + alpha2}")
        # response = session.get(wiki_base_url + alpha2, headers={"User-Agent": user_agent_header}, timeout=15)
        response = session.get(wiki_base_url + alpha2, headers={"User-Agent": user_agent_header, "Accept-Language": "en-US,en;q=0.9"}, proxies=proxy_ip, timeout=15)
        response.raise_for_status()
        # soup = BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        session.close()
        raise requests.exceptions.HTTPError(f"Error retrieving Wikipedia page for {alpha2} ({wiki_base_url + alpha2}): {e}")

    #convert html content into BS4 object
    if verbose:
        print("[Wiki] Parsing HTML content with BeautifulSoup")
    soup = BeautifulSoup(response.content, "html.parser")

    #Changes section can be in a span, h1 or h2 html element 
    possible_changes_section_tags = ["span", "h1", "h2"]

    #initialize changes_section to None
    changes_section = None

    #iterate over possible tags to find the Changes section, loop in order of element preference
    for tag in possible_changes_section_tags:
        changes_section = soup.find(tag, {"id": "Changes"})
        if changes_section:
            if verbose:
                print(f"[Wiki] Found Changes section in <{tag}> element")
            break  #break out of loop if a valid tag is found

    #validate if any Changes section was found, if not return empty dataframe
    if not (changes_section):
        if verbose:
            print(f"[Wiki] No 'Changes' section found for {alpha2}")
        # print(f"\nNo 'Changes' section found for {alpha2} at URL {wiki_base_url + alpha2}.")
        session.close()
        return pd.DataFrame()

    #get table element in Changes Section, raise error if table not found
    changes_section = changes_section.find_next('table')
    if not changes_section:
        if verbose:
            print(f"[Wiki] Error: No table found in Changes section for {alpha2}")
        session.close()
        raise ValueError(f"No table found in the 'Changes' section for {alpha2} at {wiki_base_url + alpha2}.")
    if verbose:
        print(f"[Wiki] Found table in Changes section")

    #convert html table to 2D array
    if verbose:
        print(f"[Wiki] Converting HTML table to array")
    iso3166_table_wiki = table_to_array(changes_section, soup)

    #convert 2D array of updates into dataframe, fix columns, remove duplicate rows etc
    if verbose:
        print(f"[Wiki] Parsing updates table to DataFrame")
    iso3166_df_wiki = parse_updates_table(alpha2, iso3166_table_wiki)

    #some wiki pages have multiple Changes/Updates tables
    additional_changes_table = changes_section.find_next('table', {"class": "wikitable"})

    #concatenate both updates table to 1 dataframe, if applicable
    if (additional_changes_table != None):
        if verbose:
            print(f"[Wiki] Found additional Changes table, processing...")
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
    
    #close the requests session to avoid resource warnings
    session.close()

    if verbose:
        print(f"[Wiki] Successfully retrieved {len(iso3166_df_wiki)} updates for {alpha2}")

    return iso3166_df_wiki

def get_updates_df_selenium(alpha_code: str, driver: webdriver=None, include_remarks_data: bool=True, verbose: bool=False) -> tuple:
    """
    Parse the ISO table from the official ISO.org website for a given country code.
    
    Parameters
    ==========
    :alpha_code: str
        ISO 3166-1 country code (alpha-2, alpha-3, or numeric). Will be converted to alpha-2.
    :driver: webdriver (optional)
        Selenium WebDriver instance to reuse. If not provided, a new driver will be created.
        If provided, the driver will NOT be closed after use (caller is responsible for cleanup).
    :verbose: bool (default=True)
        If True, display progress information during execution.
    
    Returns
    =======
    :tuple
        Tuple of (pd.DataFrame, dict):
        - DataFrame with columns: Date Issued, Change, Description of Change, Source
        - Empty dict for remarks (not available in this implementation)
    
    Raises
    ======
    ValueError:
        If alpha code cannot be converted to alpha-2 format or page parsing fails.
    TimeoutException:
        If page fails to load within timeout period.
    """
    
    # Convert to alpha-2 code if necessary
    try:
        alpha2 = convert_to_alpha2(alpha_code)
    except Exception as e:
        raise ValueError(f"Invalid country code: {alpha_code}. Error: {e}")
    
    if verbose:
        print(f"[ISO] Processing country code: {alpha2}")
    
    # Use provided driver or create a new one
    driver_instance = None
    driver_created_locally = False
    changes_data = []
    
    try:
        # Use provided driver if available, otherwise create new one
        if driver is not None:
            driver_instance = driver
            if verbose:
                print(f"[ISO] Using provided webdriver...")
        else:
            if verbose:
                print(f"[ISO] Initializing Selenium webdriver...")
            driver_instance = create_driver()
            driver_created_locally = True
        
        # Use /en/ path to guarantee English locale and correct rendering of the
        # "Change history of country code" h3 heading; the short URL (without /en/)
        # is still used for the Source field to match expected test/JSON output.
        iso_nav_url = "https://www.iso.org/obp/ui/en/#iso:code:3166:" + alpha2
        iso_source_url = "https://www.iso.org/obp/ui/#iso:code:3166:" + alpha2

        # Format the source field with OBP prefix and period
        source_field = f"Online Browsing Platform (OBP) - {iso_source_url}."

        if verbose:
            print(f"[ISO] Navigating to: {iso_nav_url}")

        # Navigate to the page (English locale)
        driver_instance.get(iso_nav_url)

        # Wait for complete page load
        if verbose:
            print(f"[ISO] Waiting for page to load...")
        WebDriverWait(driver_instance, 45).until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(4)

        # Wait for the "Change history of country code" h3 to appear in the DOM.
        # This is the reliable signal that the Angular SPA has rendered the section;
        # polling page_source.lower() is insufficient because the tab label alone can
        # match before the table content is actually loaded.
        if verbose:
            print(f"[ISO] Waiting for change history h3 element to appear...")
        try:
            WebDriverWait(driver_instance, 45).until(
                EC.presence_of_element_located((By.XPATH,
                    "//h3[contains(text(), 'Change history of country code')] | "
                    "//h3[contains(text(), 'Historique des modifications des codes de pays')]"
                ))
            )
            if verbose:
                print(f"[ISO] Change history h3 element detected.")
        except TimeoutException:
            if verbose:
                print(f"[ISO] Warning: change history h3 not found within 45s for {alpha2}. Attempting to parse anyway.")

        # Parse page content with BeautifulSoup
        if verbose:
            print(f"[ISO] Parsing page HTML...")
        page_html = driver_instance.page_source
        soup = BeautifulSoup(page_html, 'html.parser')

        # Scroll and re-parse to ensure all content is loaded
        for i in range(3):
            driver_instance.execute_script(f'window.scrollTo(0, {random.choice([200, 300, 400, 500, 600, 700])})')
            time.sleep(1)

        page_html = driver_instance.page_source
        soup = BeautifulSoup(page_html, 'html.parser')
        
        # Find the "Change history of country code" table
        if verbose:
            print(f"[ISO] Searching for change history table...")

        changes_table = None

        # Pass 1: look for the section heading in heading tags only (h1-h6).
        # Intentionally excludes span/div to avoid large container elements whose
        # get_text() returns the entire page (and would match any heading text).
        for header in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            header_text = header.get_text(strip=True).lower()
            if ('change history of country code' in header_text or
                    'historique des modifications des codes de pays' in header_text):
                candidate = header.find_next("table")
                if candidate:
                    changes_table = candidate
                    if verbose:
                        print(f"[ISO] Found change history table via <{header.name}> heading")
                    break

        # Pass 2: if no heading matched, fall back to inspecting every table's header row for
        # a pattern that looks like a change-history table (date + change/description columns).
        if not changes_table:
            _CHANGE_HISTORY_TERMS = {"date", "change", "description", "modification", "correction"}
            for table in soup.find_all("table"):
                first_row = table.find("tr")
                if not first_row:
                    continue
                cell_texts = [c.get_text(strip=True).lower() for c in first_row.find_all(["th", "td"])]
                matched = sum(1 for term in _CHANGE_HISTORY_TERMS if any(term in cell for cell in cell_texts))
                if matched >= 2:
                    changes_table = table
                    if verbose:
                        print(f"[ISO] Found change history table via column-header fallback")
                    break

        if not changes_table:
            if verbose:
                print(f"[ISO] No change history table found for {alpha2}")
            # Return empty DataFrame for consistency
            return pd.DataFrame(columns=['Change', 'Description of Change', 'Date Issued', 'Source']), {}
        
        # Extract table rows
        if verbose:
            print(f"[ISO] Extracting table data...")
        
        rows = changes_table.find_all("tr")

        # Determine column indices from the header row so we only extract the
        # English description column and ignore the French one.
        date_col_idx = 0
        change_col_idx = 1  # default: second column
        if rows:
            header_cells = rows[0].find_all(["th", "td"])
            for idx, cell in enumerate(header_cells):
                header_text = cell.get_text(strip=True).lower()
                if "(en)" in header_text or header_text in ("short description of change", "description of change"):
                    change_col_idx = idx
                    break

        # Skip header row and process data rows
        for row in rows[1:]:
            cols = row.find_all("td")
            
            # Each row should have at least 2 columns (date and description)
            if len(cols) >= 2:
                # Extract effective date (first column)
                date_raw = cols[date_col_idx].get_text(strip=True)
                
                # Extract English description only; Description of Change is left
                # empty for ISO OBP source (the third column is the French translation).
                change_text = ' '.join(cols[change_col_idx].get_text(strip=True).split()) if change_col_idx < len(cols) else ""
                change_text = change_text.replace('"', "'")
                
                description_of_change = ""
                
                # Skip rows where we couldn't extract essential data
                if not date_raw or not change_text:
                    continue
                
                # Parse and format the date
                try:
                    # Try to parse the date in YYYY-MM-DD format
                    from datetime import datetime
                    date_obj = datetime.strptime(date_raw, "%Y-%m-%d")
                    date_issued = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    # If parsing fails, use the raw date
                    date_issued = date_raw
                
                # Ensure Change text ends with a period if it doesn't already
                if change_text and not change_text.endswith('.'):
                    change_text = change_text + "."
                
                # Create entry in required format
                entry = {
                    "Change": change_text,
                    "Description of Change": description_of_change,
                    "Date Issued": date_issued,
                    "Source": source_field
                }
                
                changes_data.append(entry)
        
        if verbose:
            print(f"[ISO] Successfully extracted {len(changes_data)} entries for {alpha2}")
        
        # Convert list of dicts to DataFrame
        if changes_data:
            iso3166_df_selenium = pd.DataFrame(changes_data)
            # Reorder columns to match expected format
            iso3166_df_selenium = iso3166_df_selenium[['Change', 'Description of Change', 'Date Issued', 'Source']]
        else:
            iso3166_df_selenium = pd.DataFrame(columns=['Change', 'Description of Change', 'Date Issued', 'Source'])
        
        # Extract remarks data if available
        if verbose:
            print(f"[ISO] Searching for remarks section...")
        
        remarks_data = {}
        try:
            # Find the country summary table which contains remarks
            country_summary_table = soup.find(class_='core-view-summary')
            
            if country_summary_table:
                if verbose:
                    print(f"[ISO] Found country summary table with remarks")
                # Parse remarks from the summary table
                iso3166_df_selenium, remarks_data = parse_remarks_table(iso3166_df_selenium, country_summary_table)
                if verbose and remarks_data:
                    print(f"[ISO] Successfully extracted remarks data with {sum(1 for v in remarks_data.values() if v)} parts")
            else:
                if verbose:
                    print(f"[ISO] No country summary table found for remarks")
                remarks_data = {}
        except Exception as e:
            if verbose:
                print(f"[ISO] Could not extract remarks data: {e}")
            remarks_data = {}
        
        # Return DataFrame and remarks dict
        return iso3166_df_selenium, remarks_data
    
    except Exception as e:
        if verbose:
            print(f"[ISO] Error occurred: {type(e).__name__}: {e}")
        raise
    
    finally:
        # Close the browser only if we created it locally
        if driver_created_locally and driver_instance:
            if verbose:
                print(f"[ISO] Closing locally-created webdriver...")
            try:
                driver_instance.quit()
            except Exception as e:
                if verbose:
                    print(f"[ISO] Error closing driver: {e}")