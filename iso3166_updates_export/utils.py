import re
import os 
import json
from itertools import product
from datetime import datetime
import iso3166
from bs4 import BeautifulSoup, Tag
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import pprint

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

    #raise error if more than 1 country code input
    if ("," in alpha_code):
        raise ValueError(f"Only one country code should be input into the function: {alpha_code}.")
        
    #uppercase alpha code, initial_alpha_code var maintains the original alpha code pre-uppercasing
    alpha_code = alpha_code.upper()
    initial_alpha_code = alpha_code

    #use iso3166 package to find corresponding alpha-2 code from its numeric code, return error if numeric code not found
    if (alpha_code.isdigit()):
        if not (alpha_code in list(iso3166.countries_by_numeric.keys())):
            raise ValueError(f"Invalid ISO 3166-1 alpha numeric country code input: {initial_alpha_code}.")
        return iso3166.countries_by_numeric[alpha_code].alpha2

    #return input alpha code if its valid, return error if alpha-2 code not found
    if len(alpha_code) == 2:
        if not (alpha_code in list(iso3166.countries_by_alpha2.keys())):
            raise ValueError(f"Invalid ISO 3166-1 alpha-2 country code input: {initial_alpha_code}.")
        return alpha_code

    #use iso3166 package to find corresponding alpha-2 code from its alpha-3 code, return error if code not found
    if len(alpha_code) == 3:
        if not (alpha_code in list(iso3166.countries_by_alpha3.keys())):
            raise ValueError(f"Invalid ISO 3166-1 alpha-3 country code: {initial_alpha_code}.")
        return iso3166.countries_by_alpha3[alpha_code].alpha2

    #return error by default if input code not returned already
    raise ValueError(f"Invalid alpha country code input {alpha_code}.")

def validate_year(year: str) -> tuple[list,bool,bool,bool,bool]:
    """
    Validate and parse the year parameter into a list of years. Also return if
    a year range, greater than/less than or not equal to year are input. Raise 
    error if invalid year format.

    Parameters
    ========= 
    :year: str
        single string or comma separated list of 1 or more years to get the specific 
        ISO 3166 updates from, per country. You can also pass in a year range 
        (e.g 2010-2015), a year to get all updates less than or greater than that 
        specified year (e.g >2007, <2021) or not equal to a year (e.g <>2001)

    Returns
    ======= 
    :year: str
        parsed and validated list of years.
    :year_range: bool
        if input year parameter contains a range of years.
    :year_greater_than: bool
        if input year parameter contains ">", thus getting all updates >= year.
    :year_less_than: bool
        if input year parameter contains "<", thus getting all updates < year.
    :year_not_equal: bool 
        if input year parameter contains "<>", thus excluding any rows with input 
        year/years.

    Raises
    ======
    TypeError:
        Invalid data type input for year parameter.
    ValueError:
        Invalid year format. 
        Only one type of symbol should be input for year e.g '-', '<' or '>'.
    """
    #raise error if invalid type input
    if not (isinstance(year, str)):
        raise TypeError(f"Expected input year to be a string, got {type(year)}.")

    #split year into comma separated list of years, remove any whitespace
    year = year.replace(" ", "").split(',')
    # year = re.sub(r"[<>]", "", year).replace(" ", "").split(',')

    #year bools
    year_range = False
    year_greater_than = False
    year_less_than = False
    year_not_equal = False

    #validate each year's format using regex
    for year_ in year:
        #remove symbols like '<' or '>'
        sanitized_year = re.sub(r"[<>]", "", year_)

        #if it's a range, split and validate each part
        years = sanitized_year.split('-')
        for y in years:
            #skip empty strings
            if not y:
                continue

            #validate year format
            if not re.match(r"^1[0-9]{3}$|^2[0-9]{3}$", y):
                raise ValueError(f"Invalid year input, must be a year >= 1996, got {year_}.")

    #a '-' separating 2 years implies a year range of sought country updates
    #a ',' separating 2 years implies a list of years
    #a '>' before year means get all country updates greater than or equal to specified year
    #a '<' before year means get all country updates less than specified year
    #a '<>' before the year means don't include year/list of years in export 
    if ("<>" in year[0]):
        year_not_equal = True
        year = [x.replace("<>", "") for x in year]
    elif ('-' in year[0]):
        year_range = True
        year = year[0].split('-')
        #if year range years are wrong way around then swap them
        if (year[0] > year[1]):
            year[0], year[1] = year[1], year[0]
        #raise error if more than 2 years in list
        if (len(year) > 2):
            raise ValueError(f"If using a range of years, there must only be 2 years separated by a '-': {year}.")
    #parse array for using greater than symbol
    elif ('>' in year[0]):
        year = list(year[0].rpartition(">")[1:])
        year_greater_than = True
        year.remove('>')
        #raise error if more than 2 years in list
        if (len(year) > 2):
            raise ValueError(f"If greater than year input, there must only be 1 year prepended by a '>': {year}.")
    #parse array for using less than symbol
    elif ('<' in year[0]):
        year = list(year[0].rpartition("<")[1:])
        year_less_than = True
        year.remove('<')
        #raise error if more than 2 years in list
        if (len(year) > 2):
            raise ValueError(f"If less than year input, there must only be 1 year prepended by a '<': {year}.")
    #split years into comma separated list of multiple years if multiple years are input
    elif (',' in year[0]):
        year = year[0].split(',')

    #raise error if more than one year related symbols are in year str
    for year_ in year:
        if any(symbol in year_ for symbol in ["-", "<", ">"]):
            raise ValueError(f"Only one type of symbol should be input for year e.g '-', '<' or '>': {year_}.")

    return year, year_range, year_greater_than, year_less_than, year_not_equal                         

def filter_year(iso3166_updates_df: pd.DataFrame, year: list, year_range: bool=False, year_greater_than: bool=False, 
    year_less_than: bool=False, year_not_equal: bool=False) -> pd.DataFrame:
    """
    Filter out the relevant rows of updates DataFrame from the input year parameter values. If year/list of 
    years input, filter out rows that don't equal year, if year range input filter out rows not within range 
    inclusive. If year_greater_than or year_less_than True then filter out respective rows, less than or 
    greater than, respectively. If not equal to year, remove rows with that year in them.

    Parameters
    ==========
    :iso3166_updates_df: pd.DataFrame:
        exported ISO 3166 updates data from the data sources.
    :year: list/array 
        array/list of year(s). Only the ISO 3166 updates for the selected year for a particular
        country will be returned. If empty then all years of updates are returned.
    :year_range: bool (default=False)
        set to True if a range of years are input into year parameter e.g "2002-2010" etc.
        Function will remove all rows in Dataframe that aren't in specified year range.
    :year_less_than: bool (default=False)
        set to True if less than symbol is input into year parameter e.g "<2018" etc.
        Function will remove all rows in Dataframe that are greater than or equal to
        specified year.
    :year_greater_than: bool (default=False)
        set to True if greater than symbol is input into year parameter e.g ">2005" etc.
        Function will remove all rows in Dataframe that are less than specified year.
    :year_not_equal: bool (default=False)
        set to True if not equal to symbol is input into year parameter e.g "<>2020" etc.
        Function will remove all rows in Dataframe that have the input publication year.

    Returns
    =======
    :iso3166_updates_df: pd.DataFrame:
        dataframe of ISO 3166 updates data with relevant year filters applied.

    Raises
    ======
    TypeError:
        Input data isn't a DataFrame.
    """      
    #raise type error if input isn't a dataframe
    if not (isinstance(iso3166_updates_df, pd.DataFrame)):
        raise TypeError("Input ISO 3166 updates data should be a DataFrame.")

    #if input is a string, run validate function to ensure year is in correct format
    if (isinstance(year, str)):
        year, year_range, year_greater_than, year_less_than, year_not_equal = validate_year(year)

    #create temp year column to get year of updates from date column, convert to str
    iso3166_updates_df['Year'] = iso3166_updates_df["Date Issued"].apply(get_year)
    iso3166_updates_df['Year'] = iso3166_updates_df['Year'].astype(str)    

    #drop all rows in dataframe that are less than input year
    if (year_greater_than):
        iso3166_updates_df = iso3166_updates_df[iso3166_updates_df['Year'] >= str(year[0])]
    #drop all rows in dataframe that are greater than or equal to input year
    elif (year_less_than):
        iso3166_updates_df = iso3166_updates_df[iso3166_updates_df['Year'] < str(year[0])]
    #drop all rows in dataframe that are not within input year range
    elif (year_range):
        iso3166_updates_df = iso3166_updates_df[(iso3166_updates_df['Year'] >= str(year[0])) & (iso3166_updates_df['Year'] <= str(year[1]))]  
    #drop all rows in dataframe that have input year value
    elif (year_not_equal):
        iso3166_updates_df = iso3166_updates_df[~iso3166_updates_df["Year"].isin(year)]
    #drop all rows in dataframe that aren't equal to year/list of years in year parameter
    else:
        iso3166_updates_df = iso3166_updates_df[iso3166_updates_df['Year'].isin(year)]

    #drop Year column
    iso3166_updates_df = iso3166_updates_df.drop('Year', axis=1)

    return iso3166_updates_df

def get_alpha_codes_list(alpha_codes: str="", alpha_codes_range: str="") -> tuple:
    """
    Get the full list of ISO 3166 alpha-2 country codes to download the updates data
    for. The function validates and converts the list/str of alpha codes input, if 
    applicable. If a range of alpha codes input via the alpha_codes_range parameter,
    the full range of alpha codes will be gotten, alphabetically.

    Parameters
    ==========
    :alpha_codes: str|list (default="")
        comma separated list of one or more ISO 3166 alpha-2, alpha-3 or numeric country codes.
    :alpha_codes_range: str
        a range of 2 ISO 3166-1 alpha-2, alpha-3 or numeric country codes to export the 
        updates data from, separated by a '-'. The code on the left hand side will be the 
        starting alpha code and the code on the right hand side will be the final alpha code 
        to which the data is exported from, e.g AD-LV, will export all updates data from 
        Andorra to Latvia, alphabetically. If only a single alpha code input then it will 
        serve as the starting country.

    Returns
    =======
    :alpha_codes_list: list
        list of validated and converted alpha-2 country codes.
    :alpha_codes_range: str (default="")
        corrected and validated range of alpha codes.
    
    Raises
    ======
    TypeError:
        Input parameters are not of correct str type.
    """
    if alpha_codes:
        if isinstance(alpha_codes, list):
            alpha_codes = ", ".join(alpha_codes)
        #raise error if input isn't a string or list
        elif not isinstance(alpha_codes, str):
            raise TypeError(f"Input parameter alpha_codes should be a list or string, got {type(alpha_codes)}.")
        #get list of alpha-2 codes, convert to alpha-2 if applicable
        alpha_codes_list = [convert_to_alpha2(code) for code in alpha_codes.replace(' ', '').split(',')]
        alpha_codes_range = ""
    elif alpha_codes_range:
    
        #sorted list of ISO 3166 alpha codes
        sorted_alpha_codes = sorted(iso3166.countries_by_alpha2.keys())

        #raise error if alpha codes range parameter is not a string
        if not isinstance(alpha_codes_range, str):
            raise TypeError(f"Input parameter alpha_codes_range should be a string, got {type(alpha_codes_range)}.")
    
        #if 2 alpha-2 codes separated by '-' not in parameter then the single alpha code will serve as the starting point
        if not ('-' in alpha_codes_range):
            #convert 3 letter alpha-3 or numeric code into its 2 letter alpha-2 counterpart OR validate existing 2 letter alpha-2
            start_alpha_code = convert_to_alpha2(alpha_codes_range.upper().replace(' ', ''))

            #get list of alpha codes from start alpha code, alphabetically, using its index
            alpha_codes_list = sorted_alpha_codes[sorted_alpha_codes.index(start_alpha_code):]

            #alpha codes range parameter set to input alpha code to the last country code alphabetically (ZW)
            alpha_codes_range = start_alpha_code + "-ZW"
        else:
            #convert 3 letter alpha-3 or numeric code into its 2 letter alpha-2 counterpart OR validate existing 2 letter alpha-2
            start_alpha_code = convert_to_alpha2(alpha_codes_range.split('-')[0])
            end_alpha_code = convert_to_alpha2(alpha_codes_range.split('-')[1])

            #swap 2 alpha codes to ensure they're in alphabetical order
            if (start_alpha_code > end_alpha_code):
                temp_code = start_alpha_code
                start_alpha_code = end_alpha_code
                end_alpha_code = temp_code

            #alpha codes range parameter set to validated and converted start and end alpha code
            alpha_codes_range = start_alpha_code + "-" + end_alpha_code

            #get full range of alpha codes from range parameter 
            alpha_codes_list = [code for code in sorted_alpha_codes if start_alpha_code <= code <= end_alpha_code]
    else:
        #using all ISO 3166 alpha codes
        alpha_codes_list = sorted(iso3166.countries_by_alpha2.keys())

    #sort list of alpha codes alphabetically
    alpha_codes_list.sort()

    #exclude Kosovo if applicable
    if "XK" in alpha_codes_list: 
        alpha_codes_list.remove("XK")

    return alpha_codes_list, alpha_codes_range

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

def get_year(row: str) -> int:
    """ 
    Extract year from date row.

    Parameters
    ==========
    :row: str
        row/string to parse year value from, including "corrected" date rows.
    
    Returns
    =======
    :datetime.strptime(parsed_date, '%Y-%m-%d').year: str
        year from current row date.
    """
    if "corrected" in row:
        original_date = re.sub(r"\(.*\)", "", row).strip()
    else:
        original_date = row.strip()
    parsed_date = parse_date(original_date)
    return datetime.strptime(parsed_date, '%Y-%m-%d').year

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
    :row: str
        row string with extra spacing removed. 
    """
    row = re.sub(' +', ' ', row)
    row = re.sub(r' \.', '.', row) 
    return row

def export_updates(iso3166_updates_data: dict, export_folder: str="iso3166-updates-output", export_filename: str="iso3166-updates", 
    export_json: bool=True, export_csv: bool=False, export_xml: bool=False, concat_updates: bool=True, alpha_codes: list=[], alpha_codes_range: str="", year: list=[], 
    year_range: bool=False, year_greater_than: bool=False, year_less_than: bool=False, year_not_equal: bool=False) -> None:
    """
    Export the exported ISO 3166 updates data to JSON, CSV or XML files in export folder. The various 
    input parameters are required for the naming of the exported files which differ depending on the 
    alpha codes and year parameters. If the concat_updates parameter is set then the data objects will 
    be exported to the one JSON file otherwise they will be exported to separate files. By default, the
    data will be exported to a JSON. 

    Parameters
    ==========
    :iso3166_updates_data: dict
        object of all exported ISO 3166 updates data.
    :export_folder: str (default="iso3166-updates-output")
        folder name to store JSON & CSV outputs for all country's ISO 3166 updates.
    :export_filename: str (default="iso3166-updates")
        base filename for JSON & CSV output files of inputted country's ISO 3166 updates.
    :concat_updates: bool (default=True)
        if multiple alpha codes input, concatenate updates into one JSON/CSV file
        (concat_updates=True) or into separately named files in export folder
        (concat_updates=False). By default all country's updates will be compiled 
        into the same file.
    :export_json: bool (default=True)
        export all ISO 3166 updates for inputted countries into JSON format in export folder.
    :export_csv: bool (default=False)
        export all ISO 3166 updates for inputted countries into CSV format in export folder.
    :export_xml: bool (default=False)
        export all ISO 3166 updates for inputted countries into XML format in export folder.
    :alpha_codes: list (default=[])
        comma separated list of ISO 3166-1 alpha-2, alpha-3 or numeric country codes,
        to get the latest ISO 3166 updates from. Any alpha-3 or numeric codes input 
        are converted to their alpha-2 equivalent. If less than 10 alpha codes in
        list these will be appended to export filename, otherwise the alpha codes wont
        be included in filename.
    :alpha_codes_range: (default="")
        a range of 2 ISO 3166-1 alpha-2, alpha-3 or numeric country codes to export the updates 
        data from, separated by a '-'. The code on the left hand side will be the starting alpha 
        code and the code on the right hand side will be the final alpha code to which the data 
        is exported from, e.g AD-LV, will export all updates data from Andorra to Latvia, 
        alphabetically. Useful if a subset of codes are required. If only a single alpha code 
        input then it will serve as the starting country.
    :year_range: bool (default=False)
        set to True if a range of years are input into year parameter e.g "2002-2010" etc.
        Function will remove all rows in Dataframe that aren't in specified year range.
    :year_less_than: bool (default=False)
        set to True if less than symbol is input into year parameter e.g "<2018" etc.
        Function will remove all rows in Dataframe that are greater than or equal to
        specified year.
    :year_greater_than: bool (default=False)
        set to True if greater than symbol is input into year parameter e.g ">2005" etc.
        Function will remove all rows in Dataframe that are less than specified year.
    :year_not_equal: bool (default=False)
        set to True if not equal to  symbol is input into year parameter e.g "<>2020" etc.
        Function will remove all rows in Dataframe that have the input publication year.

    Returns
    =======
    None

    Raises
    ======
    ValueError:
        No input ISO 3166 updates data.
    TypeError:
        Input data is not of correct type list.
    """
    #both export bool parameters not set
    if (not export_json and not export_csv and not export_xml):
        print("Export JSON, CSV and XML parameters all set to False so ISO 3166 Updates data not exported to any format.")
        return None
    
    #create export folder if it doesn't exist
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)

    #raise error if no input data
    if not (iso3166_updates_data):
        raise ValueError("No ISO 3166 data to export, empty dict input.")

    #base filename
    base_filename = os.path.splitext(export_filename)[0]

    #convert alpha codes str into list
    if not (isinstance(alpha_codes, list)):
        alpha_codes = alpha_codes.split(",")

    #raise error if input data object is not of correct dict data type
    if not (isinstance(iso3166_updates_data, dict)):
        raise TypeError("Input data object should be of type dict and in the format: \
                        {'AA': []}, where AA is the alpha country code and [] is its list of updates.")

    #check to see if dictionary only contains empty country updates data, if so csv export is skipped
    all_empty = all(isinstance(value, list) and not value for value in iso3166_updates_data.values())

    #if exporting to CSV need to add country code column to identify each row's updates
    if (export_csv and not all_empty):
        #dataframe for csv export
        csv_iso3166_df = pd.DataFrame()

        #flatten the dictionary and add the "Country Code" column
        flattened_data = []
        for country_code, updates in iso3166_updates_data.items():
            for update in updates:
                flattened_update = {**update, 'Country Code': country_code}
                flattened_data.append(flattened_update)

        #convert flattened data to DataFrame
        csv_iso3166_df = pd.DataFrame(flattened_data)

        #if empty dataframe, reset export_csv flag to False 
        if (csv_iso3166_df.empty):
            export_csv = False
        else:
            #reindex columns in dataframe
            csv_iso3166_df = csv_iso3166_df[['Country Code', 'Change', 'Description of Change', 'Date Issued', 'Source']]

            #remove country code column if only one country's updates data exported, otherwise sort them alphabetically
            if (csv_iso3166_df["Country Code"].nunique() == 1):
                csv_iso3166_df.drop("Country Code", axis=1, inplace=True)
            else:
                csv_iso3166_df.sort_values('Country Code', inplace=True)

            #iterate over dict, removing 'Country Code' from nested dicts which isn't required for JSON export
            iso3166_updates_data = {k: [{key: val for key, val in record.items() if key != 'Country Code'} for record in v] for k, v in iso3166_updates_data.items()}

    #export to XML if bool set and data is non-empty
    if (export_xml and not all_empty):
        
        #create XML tree element 
        xml_root = ET.Element("ISO3166Updates")
        #iterate through country code and updates data, appending each as a child/sub element of the XML tree
        for country_code, updates in iso3166_updates_data.items():
            country_elem = ET.SubElement(xml_root, "Country", code=country_code)
            for update in updates:
                update_elem = ET.SubElement(country_elem, "Update")
                for key, value in update.items():
                    child = ET.SubElement(update_elem, key.replace(" ", "_"))
                    child.text = str(value)

    #construct export filename when we are concatenating all exported updates into one output file
    if (concat_updates):
        #base filename
        export_filename_concat_updates = base_filename

        #append alpha codes or range of alpha codes to filename, don't append if more than 10 individual alpha codes input
        if (len(alpha_codes) <= 10 and alpha_codes != []):
            export_filename_concat_updates += f"_{','.join(alpha_codes)}"
        elif (alpha_codes_range and alpha_codes == []):
            export_filename_concat_updates += f"_{alpha_codes_range}"

        #append year parameters to filename, if applicable
        if (year != [''] and year != []):
            if (year_greater_than):
                export_filename_concat_updates += f"_>{','.join(year)}"
            elif (year_less_than):
                export_filename_concat_updates += f"_<{','.join(year)}"
            elif (year_range):
                export_filename_concat_updates += f"_{year[0]}-{year[1]}"

            elif (year_not_equal):
                export_filename_concat_updates += f"_<>{','.join(year)}"
            else:
                export_filename_concat_updates += f"_{','.join(year)}"

        #export updates into the same JSON
        if (export_json):
            with open(os.path.join(export_folder, export_filename_concat_updates + ".json"), "w") as write_file:
                json.dump(iso3166_updates_data, write_file, indent=4, ensure_ascii=False)
            print(f"\nAll ISO 3166 updates exported to JSON: {os.path.join(export_folder, export_filename_concat_updates)}.json.")
        #export updates into the same CSV 
        if (export_csv and not all_empty):
            csv_iso3166_df.to_csv(os.path.join(export_folder, os.path.splitext(export_filename_concat_updates)[0] + ".csv"), index=False)
            print(f"\nAll ISO 3166 updates exported to CSV: {os.path.join(export_folder, export_filename_concat_updates)}.csv.")
        #export updates into the same XML 
        if (export_xml and not all_empty):

            #convert ElementTree to a pretty-printed XML string
            long_xml_string = ET.tostring(xml_root, 'utf-8')
            parsed_xml_elem = minidom.parseString(long_xml_string)
            pretty_xml_as_string = parsed_xml_elem.toprettyxml(indent="  ")

            #write to file
            with open(os.path.join(export_folder, os.path.splitext(export_filename_concat_updates)[0] + ".xml"), "w", encoding="utf-8") as f:
                f.write(pretty_xml_as_string)

            print(f"\nAll ISO 3166 updates exported to XML: {os.path.join(export_folder, export_filename_concat_updates)}.xml.\n")

    #updates data being exported to different individual files
    else:
        #iterate over each updates object, getting its export filename
        for update in iso3166_updates_data:
            
            #base filename
            export_filename_no_concat_updates = base_filename

            #append alpha-2 codes and list of years or gt/lt/range symbols, if applicable, to separate files
            if (year != [''] and year != []):
                if (year_greater_than):
                    export_filename_no_concat_updates += f"_{update}_>{','.join(year)}"
                elif (year_less_than):
                    export_filename_no_concat_updates += f"_{update}_<{','.join(year)}"
                elif (year_range):
                    export_filename_no_concat_updates += f"_{update}_{year[0]}-{year[1]}"
                elif (year_not_equal):
                    export_filename_no_concat_updates += f"_{update}_<>{','.join(year)}"
                else:
                    export_filename_no_concat_updates += f"_{update}-{','.join(year)}"
            else:
                export_filename_no_concat_updates += f"_{update}" 

            #export updates into separate JSON
            if (export_json):
                with open(os.path.join(export_folder, export_filename_no_concat_updates + ".json"), "w") as write_file:
                    json.dump(iso3166_updates_data[update], write_file, indent=4, ensure_ascii=False)
            #export updates into separate CSV, extract current country codes rows, drop country code column
            if (export_csv and not all_empty):
                current_update_df = csv_iso3166_df[csv_iso3166_df['Country Code'] == update]
                current_update_df = current_update_df.drop("Country Code", axis=1)
                current_update_df.to_csv(os.path.join(export_folder, export_filename_no_concat_updates + ".csv"), index=False)
            #export updates to XML 
            if (export_xml and not all_empty):

                #convert ElementTree to a pretty-printed XML string
                long_xml_string = ET.tostring(xml_root, 'utf-8')
                parsed_xml_elem = minidom.parseString(long_xml_string)
                pretty_xml_as_string = parsed_xml_elem.toprettyxml(indent="  ")

                #write to file
                with open(os.path.join(export_folder, os.path.splitext(export_filename_no_concat_updates)[0] + ".xml"), "w", encoding="utf-8") as f:
                    f.write(pretty_xml_as_string)

        print(f"All ISO 3166 updates exported to output folder: {export_folder}.")    

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

def manual_updates(iso3166_updates: dict, year: str, year_range: bool=False, year_greater_than: bool=False, 
    year_less_than: bool=False, year_not_equal: bool=False) -> dict:
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
    :year: str 
        str of year(s). Only the ISO 3166 updates for the selected year for a particular
        country will be returned. If empty then all years of updates are returned.
    :year_range: bool (default=False)
        set to True if a range of years are input into year parameter e.g "2002-2010" etc.
        Function will remove all rows in Dataframe that aren't in specified year range.
    :year_less_than: bool (default=False)
        set to True if less than symbol is input into year parameter e.g "<2018" etc.
        Function will remove all rows in Dataframe that are greater than or equal to
        specified year.
    :year_greater_than: bool (default=False)
        set to True if greater than symbol is input into year parameter e.g ">2005" etc.
        Function will remove all rows in Dataframe that are less than specified year.
    :year_not_equal: bool (default=False)
        set to True if not equal to symbol is input into year parameter e.g "<>2020" etc.
        Function will remove all rows in Dataframe that have the input publication year.

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
                            "TZ": [{"Date Issued": "2019-02-14", "Delete": 1}],
                            "XK": []}

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

    #object to store year filtered updates
    filtered = {}
    
    #filter out updates by year if parameter set
    if (year != ['']):
        #iterate over each country updates object, filtering by year if applicable
        for country_code, entries in iso3166_updates.items():
            new_entries = []
            for entry in entries:
                #parse year from date
                entry_year = str(get_year(entry.get("Date Issued", "")))
                if not entry_year:
                    #skip to next iteration
                    continue

                #filter updates based on year conditions
                if year_greater_than and entry_year >= str(year[0]):
                    new_entries.append(entry)
                elif year_less_than and entry_year < str(year[0]):
                    new_entries.append(entry)
                elif year_range and str(year[0]) <= entry_year <= str(year[1]):
                    new_entries.append(entry)
                elif year_not_equal and entry_year not in map(str, year):
                    new_entries.append(entry)
                elif not (year_greater_than or year_less_than or year_range or year_not_equal):
                    if entry_year in map(str, year):
                        new_entries.append(entry)

            #store new year filtered updates
            filtered[country_code] = new_entries

        iso3166_updates = filtered

    return iso3166_updates

def merge_update_files(update_folder_path: str="") -> None:
    """
    Merge individually exported update files, generated when the save_each_iteration parameter has 
    been set, into one single file. The individual files should be within one exported folder and
    each file will be individually iterated over, merging them all into one master updates file.

    Parameters
    ==========
    :update_folder_path: str (default="")
        filepath to folder where individual files are exported.

    Returns
    =======
    None

    Raises
    ======
    OSError:
        Folder of individually exported updates files can't be found.
    """
    #exported filename
    merged_iso3166_updates_filepath = "merged_iso3166_updates.json"

    #raise error if folder not found
    if not (os.path.isdir(update_folder_path)):
        raise OSError(f"Export directory not found: {update_folder_path}.")

    #merged updates data
    merged_data = []

    #iterate over exported updates file in the directory
    for filename in os.listdir(update_folder_path):
        if filename.startswith("iso3166_updates_") and filename.endswith(".json"):
            file_path = os.path.join(update_folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    merged_data.append(data)
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode updates JSON: {filename}")

    #write merged data to output file
    with open(os.path.join(update_folder_path, merged_iso3166_updates_filepath), "w", encoding="utf-8") as f:
        json.dump(merged_data, f, indent=4)

    print(f"Merged {len(merged_data)} JSON files into {merged_iso3166_updates_filepath}.")

def export_to_csv_xml(input_json_path: str="", export_filename: str="") -> None:
    """
    Export the input JSON object to CSV and XML. By default, in the export pipeline, only 
    the JSON is exported. This function allows the JSON to be exported to CSV and XML after
    the processing.

    Parameters
    ==========
    :input_json_path: str (default="")
        filepath to exported JSON.
    :export_filename: str (default="")
        export filename for csv and xml files. If no value input it
        will be the same as the input JSON file.

    Returns
    =======
    None

    Raises
    ======
    OSError:
        Filepath to JSON is invalid.
    ValueError:
        Error parsing JSON.
    """
    #raise error if invalid JSON object path
    if not os.path.isfile(input_json_path):
        raise OSError(f"Invalid filepath to JSON object: {input_json_path}.")

    #open JSON object, raise error if issue parsing
    try:
        with open(input_json_path, "r", encoding="utf-8") as f:
            iso3166_updates_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}.") from e

    #check to see if dictionary only contains empty country updates data, if so csv export is skipped
    all_empty = all(isinstance(value, list) and not value for value in iso3166_updates_data.values())

    #if exporting to CSV need to add country code column to identify each row's updates
    if not (all_empty):
        #dataframe for csv export
        csv_iso3166_df = pd.DataFrame()

        #flatten the dictionary and add the "Country Code" column
        flattened_data = []
        for country_code, updates in iso3166_updates_data.items():
            for update in updates:
                flattened_update = {**update, 'Country Code': country_code}
                flattened_data.append(flattened_update)

        #convert flattened data to DataFrame
        csv_iso3166_df = pd.DataFrame(flattened_data)

        #if non-empty dataframe, add columns and data
        if not (csv_iso3166_df.empty):
            #reindex columns in dataframe
            csv_iso3166_df = csv_iso3166_df[['Country Code', 'Change', 'Description of Change', 'Date Issued', 'Source']]

            #remove country code column if only one country's updates data exported, otherwise sort them alphabetically
            if (csv_iso3166_df["Country Code"].nunique() == 1):
                csv_iso3166_df.drop("Country Code", axis=1, inplace=True)
            else:
                csv_iso3166_df.sort_values('Country Code', inplace=True)

            #iterate over dict, removing 'Country Code' from nested dicts which isn't required for JSON export
            iso3166_updates_data = {k: [{key: val for key, val in record.items() if key != 'Country Code'} for record in v] for k, v in iso3166_updates_data.items()}

    #export to XML if bool set and data is non-empty
    # if not (all_empty):
    #create XML tree element 
    xml_root = ET.Element("ISO3166Updates")
    #iterate through country code and updates data, appending each as a child/sub element of the XML tree
    for country_code, updates in iso3166_updates_data.items():
        country_elem = ET.SubElement(xml_root, "Country", code=country_code)
        for update in updates:
            update_elem = ET.SubElement(country_elem, "Update")
            for key, value in update.items():
                child = ET.SubElement(update_elem, key.replace(" ", "_"))
                child.text = str(value)

    #get export filename, use basename of JSON filepath by default
    if (export_filename == ""):
        export_filename = os.path.basename(os.path.splitext(input_json_path)[0])

    #export updates to a CSV and xml
    if not (all_empty):
        csv_iso3166_df.to_csv(export_filename + ".csv", index=False)
        print(f"\nAll ISO 3166 updates exported to CSV: {export_filename}.csv.")

    #convert ElementTree to a pretty-printed XML string
    long_xml_string = ET.tostring(xml_root, 'utf-8')
    parsed_xml_elem = minidom.parseString(long_xml_string)
    pretty_xml_as_string = parsed_xml_elem.toprettyxml(indent="  ")

    #write to file
    with open(export_filename + ".xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml_as_string)

    print(f"\nAll ISO 3166 updates exported to XML: {export_filename}.xml.\n")

# def compare_updates_files(updates1_filepath: str, updates2_filepath: str, export_differences: bool=0) -> str:
#     """
#     This function allows you to import 2 separate exported updates JSON files and
#     directly compare their object contents. Returned will be any missing or differing
#     subdivision data between the 2 objects. This is similar to the check_for_updates
#     function in the main iso3166-updates software but it allows you to import 2 files
#     directly. check_for_updates is a fixed comparison between two objects.

#     Parameters
#     ==========
#     :updates1_filepath: str
#         filepath for first updates JSON.
#     :updates2_filepath: str
#         filepath for second updates JSON.
#     :export_differences: bool
#         export the differences between the 2 files to a CSV.

#     Returns
#     =======
#     None

#     Raises
#     ======
#     OSError:
#         Invalid filepath to either of the two JSONs
#     """
#     #raise error if any of the two input update object files are invalid
#     if not (os.path.isfile(updates1_filepath)):
#         raise OSError(f"Invalid filepath for updates file: {updates1_filepath}.")
#     if not (os.path.isfile(updates2_filepath)):
#         raise OSError(f"Invalid filepath for updates file: {updates2_filepath}.")

#     #separate object that holds any differences, if applicable, between the 2 objects
#     iso3166_updates_differences = {}

#     #open 2 updates object JSONs
#     with open(updates1_filepath, "r", encoding="utf-8") as f:
#         iso3166_updates_json1 = json.load(f)
#     with open(updates2_filepath, "r", encoding="utf-8") as f:
#         iso3166_updates_json2 = json.load(f)

#     # print(iso3166_updates_json2)
#     #iterate over all ISO 3166 updates data in 1st object, if update/row not found in second json, append to difference object
#     for alpha_code, entries in iso3166_updates_json1.items():
#         current_entries = iso3166_updates_json2.get(alpha_code, {})
#         iso3166_updates_differences[alpha_code] = []

#         #iterate over individual updates entries, add to object if not in existing other updates object
#         for update in entries:
#             print("update", update)
#             print("entries", entries)

#             if update not in current_entries:
#                 updates_found = True
#                 iso3166_updates_differences[alpha_code].append(update)

#         #if current alpha-2 code has no new ISO 3166 updates associated with it, remove from temp object
#         if not iso3166_updates_differences[alpha_code]:
#             iso3166_updates_differences.pop(alpha_code, None)

#     #print out any found updates 
#     if (updates_found):

#         print("Differences found between two ISO 3166 Updates data objects\n")

#         #get total sum of new data updates for all countries in json
#         total_updates = sum(len(v) for v in iso3166_updates_differences.values())
#         total_countries = len(iso3166_updates_differences)
        
#         print(f"{total_updates} update(s) found for {total_countries} country/countries, these are outlined below")
#         print("===================================================================\n\n")
        
#         #iterate over differences data in json
#         for code in list(iso3166_updates_differences.keys()):
            
#             #output current country name and code
#             print(f"{iso3166.countries_by_alpha2[code].name} ({code}):")
            
#             #iterate over rows of differences data and pretty print json
#             for row in range(0, len(iso3166_updates_differences[code])):
#                 pprint.pprint(iso3166_updates_differences[code][row], compact=True)
#                 print("\n")
#     else:
#         print("No differences found between two input update objects.")

#     print("iso3166_updates_differences")
#     print(iso3166_updates_differences)
#     #export the differences between the 2 objects to a CSV
#     # if (export_differences):
    
#     return