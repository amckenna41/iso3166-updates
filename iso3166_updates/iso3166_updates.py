from itertools import product
import argparse
import pandas as pd
import requests
import iso3166
import os
import getpass
import json
import re
from bs4 import BeautifulSoup, Tag
from importlib import metadata
import datetime

#get current software version
__version__ = metadata.metadata('iso3166_updates')['version']

#initalise User-agent header for requests library 
USER_AGENT_HEADER = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(__version__,
                                       'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}

#base URL for ISO3166-2 wiki
wiki_base_url = "https://en.wikipedia.org/wiki/ISO_3166-2:"

def get_updates(alpha2_codes=[], year=[], export_filename="iso3166-updates", export_folder="test_iso3166-updates", 
        concat_updates=True, export_json=True, export_csv=False, verbose=True):
    """
    Get all listed changes/updates to a country/country's ISO 3166-2 subdivision codes/names 
    via the "Changes" section on its wiki page. All wiki pages follow the convention
    https://en.wikipedia.org/wiki/ISO_3166-2:XX where XX is the 2 letter alpha-2 code
    for a country listed in the ISO 3166-1. The "Changes" section lists updates or changes 
    to any ISO 3166-2 codes, including historical changes, according to the ISO newsletter 
    which is released peridically by the ISO as well as its Online Browsing Platform (OBP). 
    The ISO newsletters are not easily discoverable and accessinle online and may require a 
    subscription to the ISO 3166-2 database (https://www.iso.org/iso/updating_information.pdf). 
    The earliest available changes are from the year 2000 and the latest changes are from 2023.

    The changes/updates table is converted to a DataFrame and then exported to a CSV and or 
    JSON for further analysis. You can also get the updates from a particular year, list of 
    years, year range or updates greater than or less than a specified year, using the year 
    parameter. All of the updates are ordered alphabetically by their 2 letter ISO 3166-1 
    country code and exported to a JSON and or CSV file.

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
    :verbose: int (default=1)
        Set to 1 to print out progress of updates functionality, 0 will not print progress.

    Returns
    -------
    :all_changes : dict
        dictionary of all found ISO 3166 updates from user's inputted alpha2 codes and or year
        parameter values.
    """
    year_range = False
    greater_than = False
    less_than = False
    all_updates = False #set to True if gathering all ISO 3166 updates

    #if alpha-2 codes input param isn't str or list raise type error
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
    if (alpha2_codes != ['']):
        for code in range(0, len(alpha2_codes)):
            if (len(alpha2_codes[code]) == 3): 
                temp_alpha2_code = convert_to_alpha2(alpha2_codes[code])
                if not (temp_alpha2_code is None):
                    alpha2_codes[code] = temp_alpha2_code
                else:
                    raise ValueError("Invalid alpha-3 code input, cannot convert into corresponding alpha-2 code: {}.".format(alpha2_codes[code]))
    
    input_alpha2_codes = alpha2_codes

    #use all ISO 3166-1 codes if no input alpha-2 parameter input, set all_updates to True
    if ((alpha2_codes == [''] or alpha2_codes == [])):
        alpha2_codes = sorted(list(iso3166.countries_by_alpha2.keys()))
        all_updates = True

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
        
        #skip to next iteration if alpha-2 not valid
        if (alpha2 not in list(iso3166.countries_by_alpha2.keys())):
            continue

        #print out progress of function
        if (verbose):
            print("ISO 3166-1 Code: {} ({})".format(alpha2, wiki_base_url + alpha2))

        all_changes[alpha2] = {}

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

        #skip to next iteration if no changes for ISO code found
        if (changesSection is None):
            continue

        #get table element in Changes Section 
        table = changesSection.findNext('table')
        
        #convert html table to 2D array 
        iso3166_table = table_to_array(table)
        
        #convert updates html table/2D array to dataframe 
        iso3166_df = get_updates_df(iso3166_table, year, year_range, less_than, greater_than)

        #some wiki's have two updates tables  
        iso3166_table_2 = table.findNext('table', {"class": "wikitable"})

        #concatenate both updates table to 1 dataframe, if applicable 
        if (iso3166_table_2 != None):
            #convert secondary table into 2D array
            temp_iso3166_table = table_to_array(iso3166_table_2)
            #several tables have extra unwanted cols meaning we ignore those tables
            if ('former code' not in [col.lower() for col in temp_iso3166_table[0]] and 
                'in region' not in [col.lower() for col in temp_iso3166_table[0]] and 
                'before' not in [col.lower() for col in temp_iso3166_table[0]]): 
                temp_iso3166_df = get_updates_df(temp_iso3166_table, year, year_range, less_than, greater_than)

                #concat two dataframes together
                iso3166_df = pd.concat([iso3166_df, temp_iso3166_df], axis=0)
        
        #set Edition/Newsletter to OBP if no value/empty string
        if ((iso3166_df["Edition/Newsletter"] == "").any()):
          iso3166_df["Edition/Newsletter"] = iso3166_df["Edition/Newsletter"].replace('', 
            "Online Browsing Platform (OBP)", regex=True)

        #seperate 'Browsing' and 'Platform' string if they are concatenated in column
        iso3166_df["Edition/Newsletter"] = iso3166_df["Edition/Newsletter"].str.replace('BrowsingPlatform', "Browsing Platform")

        #only export non-empty dataframes         
        if not (iso3166_df.empty):
            
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
    if year != [] and (input_alpha2_codes == [] or input_alpha2_codes == ['']):
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

def get_updates_df(iso3166_updates_table, year=[], year_range=False, less_than=False, greater_than=False):
    """
    Convert parsed html table, from the Changes/Updates Section in the respective 
    ISO 3166-2 wiki page, into a pandas dataframe. Convert columns/headers using 
    correct naming conventions, correct Date column into correct format and 
    translate any unicode arrows in the text to normal arrow (->). If year param 
    not empty then remove any rows that don't have specified year(s). If year 
    range, less than or greater than parameters set to True then get all updates 
    from year range or all updates less than or all updates greater than a year, 
    respectively. 

    Parameters
    ----------
    :iso3166_updates_table : array
        2D array of ISO 3166-2 updates from Changes/Updates section in wiki.
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
        from 2D input array.
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
        """ parse new date from row if date of changes has been "corrected". """
        if ("corrected" in row):
            return row[row.index("corrected") + len("corrected"):].strip().replace(')', '')
        else:
            return row 
        
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
    Update column names so all dataframes follow the column format of:
    ["Date Issued", "Edition/Newsletter", "Code/Subdivision change",
    "Description of change in newsletter"].

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

            # if table cell is a newline character set to empty string
            if (cell.get_text() == "\n"):
                value = ""
            #if text has breakpoint (<br>), replace with space
            # elif ("<br/>" in str(cell)):
            #     value = cell.get_text(separator=" ").strip()
            else:
                value = cell.get_text().strip()

            #add href link to newsletter rows if applicable - ignore any wiki links            
            if not (cell.find('a') is None):
                if not (cell.find('a')['href'].startswith('/wiki/')):
                    value = value + " (" + cell.find('a')['href'] + ')'

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

    parser = argparse.ArgumentParser(description='Get latest changes/updates for all countries in the ISO 3166-1/3166-2 standard.')
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
        help='Whether to concatenate updates of individual countrys into the same json or csv files or individual files.')
    parser.add_argument('-verbose', '--verbose', type=int, required=False, action=argparse.BooleanOptionalAction, default=1, 
        help='Set to 1 to print out progress of updates function, 0 will not print progress.')

    #parse input args
    args = parser.parse_args()
    alpha2_codes = args.alpha2
    export_folder = args.export_folder
    concat_updates = args.concat_updates
    export_json = args.export_json
    export_csv = args.export_csv
    year = args.year
    verbose = args.verbose
    export_filename = args.export_filename
    
    #output ISO 3166 updates/changes for selected alpha-2 code(s) and year(s)
    get_updates(alpha2_codes, year, export_filename, export_folder, 
        concat_updates, export_json, export_csv, verbose)