from itertools import product
import argparse
import pandas as pd
import requests
import iso3166
import os
import getpass
import json
import logging
import re
from bs4 import BeautifulSoup
import datetime
from pprint import pprint

#initialise logging library 
__version__ = "0.0.3"
log = logging.getLogger(__name__)

#initalise User-agent header for requests library 
USER_AGENT_HEADER = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(__version__,
                                       'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}

#base URL for ISO3166-2 wiki
wiki_base_url = "https://en.wikipedia.org/wiki/ISO_3166-2:"

def get_updates(alpha2_codes, year=[], export_filename="iso3166-updates", 
        export_folder="../test-iso3166-updates", export_json=True):
    """
    Get all listed updates to a country's ISO3166-2 subdivision codes via 
    the "Changes" section on its wiki. The "Changes" section lists updates 
    or changes to any ISO3166-2 codes according to the ISO newsletter which
    is realeased peridically by the ISO.
    The ISO newsletters are not easily discoverable online and may require
    a subscription to the ISO3166-2 database (https://www.iso.org/iso/updating_information.pdf).

    The changes/updates table is converted to a DataFrame and then exported to a 
    CSV for further analysis. You can also get the updates from a particular year
    by using the Year parameter. 

    Parameters
    ----------
    : alpha2_codes : str / list
        single string or list of alpha-2 ISO3166 codes to get the latest ISO3166-2 updates from. If
        single alpha2 code passed in then it is converted to an iterable list.
    : year : list
        list of 1 or more years to get the specific ISO3166-2 updates from per country.
    : export_filename : str 
        filename for csv output of country's ISO3166-2 updates. 
    :export_folder : str
        folder name to store all csv outputs for country's ISO3166-2 updates. 
    : export_json : bool
        export all ISO3166 updates for inputted country's into json format. 

    Returns
    -------
    None
    """
    year_range = False
    greater_than = False
    less_than = False

    #a '-' seperating 2 years implies a year range of sought country updates, validate format of years in range
    if (year != []):
        if ('-' in year[0]):
            year_range = True
            year = year[0].split('-')
            print('year after split', year)
            #only 2 years should be included in input parameter
            if (len(year) > 2):
                print('year shouldnt be here')
                year = []
                year_range = False
        elif (',' in year[0]):
            #split years into multiple years, if multiple are input
            year = year[0].split(',')
        #parse array for using greater than symbol
        elif ('>' in year[0]):
            year = year[0].split('>')
            greater_than = True
            year.remove('>')
            if (len(year) > 2):
                year = []
                greater_than = False
        #parse array for using less than symbol
        elif ('<' in year[0]):
            year = year[0].split('<')
            less_than = True
            year.remove('<')
            if (len(year) > 2):
                year = []
                less_than = False
    for year_ in year:
        #skip to next iteration if < or > symbol
        if (year_ == '<' or year_ == '>'):
            continue
        #validate year format using regex
        if not (bool(re.match(r"^1|^2[0-9][0-9][0-9]", year_))):
            year = []
            year_range = False 
            break 

    #convert year parameter string to datetime object
    # if (isinstance(year, str) and year != ""):
    #     year = str(datetime.datetime.strptime(str(year), "%Y").year)

    all_changes = {}

    #iterate over all input ISO country codes
    for alpha2 in alpha2_codes:

        export_fname = export_filename + '-' + alpha2 

        #skip to next iteration if alpha2 not valid
        if (alpha2 not in list(iso3166.countries_by_alpha2.keys())):
            continue

        print("ISO Code: {} ({}) ".format(alpha2, wiki_base_url + alpha2))

        all_changes[alpha2] = {}

        #get html content from wiki of ISO3166 page 
        page = requests.get(wiki_base_url + alpha2, headers=USER_AGENT_HEADER)
        #convert html content into BS4 object
        soup = BeautifulSoup(page.content, "html.parser")

        #get Changes Section/Heading from soup 
        changesSection = soup.find("span", {"id": "Changes"})

        #skip to next iteration if no changes for ISO code found
        if (changesSection is None):
            # print("No changes section found for {} ({})".format(alpha2, wiki_base_url + alpha2))
            continue

        #get table element in Changes Section 
        table = changesSection.findNext('table')
        #do findNext again to check for another changes table e.g. PA, UK
        
        #convert html to 2D array 
        iso3166_table = table_to_array(table)

        #convert updates html table/2D array to dataframe 
        iso3166_df = get_updates_df(iso3166_table, year)

        #some wiki's have two updates tables  
        iso3166_table_2 = table.findNext('table', {"class": "wikitable"})

        #concat both updates table to 1 df, if applicable 
        if (iso3166_table_2 != None):
            temp_iso3166_table = table_to_array(iso3166_table_2)
            #several tables have extra unwanted cols meaning we ignore those tables
            if ('former code' not in [col.lower() for col in temp_iso3166_table[0]] and 
                'in region' not in [col.lower() for col in temp_iso3166_table[0]] and 
                'before' not in [col.lower() for col in temp_iso3166_table[0]]): 
                temp_iso3166_df = get_updates_df(temp_iso3166_table, year)

                #concat two dataframes
                iso3166_df = pd.concat([iso3166_df, temp_iso3166_df], axis=0)

        #set Edition/Newsletter to OBP if no value 
        if ((iso3166_df["Edition/Newsletter"] == "").all()):
          iso3166_df["Edition/Newsletter"] = "Online Browsing Platform (OBP)"

        #append year onto filename, if not empty
        export_fname = export_fname + (("-" + str(year)) if year != [] else '')  #potentially need to add strip to export_fname
            
        #create output folder if doesn't exist
        if not (os.path.isdir(export_folder)):
            os.mkdir(export_folder)

        #only export non-empty dataframes         
        if not (iso3166_df.empty):
            
            #sort by date
            iso3166_df = iso3166_df.sort_values(by=['Date Issued'], ascending=False)

            #order by Date Issued,
            iso3166_df.to_csv(os.path.join(export_folder, export_fname + '.csv'), index=False)
        
            #add ISO updates to object of all ISO3166 updates, convert to json 
            all_changes[alpha2] = json.loads(iso3166_df.to_json(orient='records'))

            #print output to terminal if less than 10 ISO3166 codes input
            if len(alpha2_codes) < 10:
                pprint(all_changes[alpha2], depth=2, sort_dicts=False)
                print('\n')

        #reset export filename var 
        export_fname = export_filename

    #export all ISO3166 updates to json, store in main dir
    if (export_json):
        if (all_changes):
            with open(os.path.join("../", "iso3166-updates.json"), "w") as write_file:
                json.dump(all_changes, write_file, indent=4, ensure_ascii=False)
            print("All ISO3166 changes exported to folder {}".format(export_folder))
    
def get_updates_df(iso3166_updates_table, year=[]):
    """
    Convert parsed html table, from Changes Section in the respective ISO3166-2 wiki
    page, into a pandas dataframe. Convert columns/headers using correct naming 
    conventions, correct "Date Issued" column into correct date format. If year param 
    not empty then remove any rows that don't have specified year/s or year range.

    Parameters
    ----------
    :iso3166_updates_table : array
        2D array of ISO3166-2 updates from Changes section in wiki
    :year : array
        array/list of year(s), if not empty only the ISO3166 updates for the selected
        year for a particular country will be returned. If empty then all years of 
        updates are returned.

    Returns
    -------
    :iso3166_df : pd.DataFrame
        comverted pandas dataframe of all ISO3166-2 changes for particular country
        from 2D input array.
    """
    #update column names to correct naming conventions
    cols = correct_columns(iso3166_updates_table[0])

    #convert 2D array into dataframe    
    iso3166_df = pd.DataFrame(iso3166_updates_table[1:], columns=cols)

    #get index and name of Date column in DataFrame, i.e the column that has 'date' in it
    dateColIndex = [idx for idx, s in enumerate(list(map(lambda x: x.lower(), iso3166_df.columns))) if 'date' in s]
    dateColName = list(iso3166_df.columns)[dateColIndex[0]]

    def correct_date(row):
        """ parse new date from row if changes have been "corrected". """
        if "corrected" in row:
            # wordEndIndex = row.index("corrected") + len("corrected")
            return row[row.index("corrected") + len("corrected"):].strip().replace(')', '')
        else:
            return row 

    def convert_date(row):
        """ convert string date in rows of df into year from date object. """
        return datetime.datetime.strptime(row.replace('\n', ''), '%Y-%m-%d').year

    #parse date column to get corrected & most recent date, if applicable 
    iso3166_df[dateColName] = iso3166_df[dateColName].apply(correct_date)

    #only include rows of dataframe where date updated is same as year parameter, drop year col
    if (year != []): 
        iso3166_df['Year'] = iso3166_df[dateColName].apply(convert_date)         #create temp new column to get year of updates from date column 
        iso3166_df = iso3166_df.drop(iso3166_df[iso3166_df['Year'] != year].index)
        iso3166_df = iso3166_df.drop('Year', axis=1)

    #add below columns if not present so all DF's follow same format
    if ("Edition/Newsletter" not in iso3166_df):
        iso3166_df["Edition/Newsletter"] = ""

    if ("Code/Subdivision change" not in iso3166_df):
        iso3166_df["Code/Subdivision change"] = ""

    #reindex/reorder columns in df
    iso3166_df = iso3166_df.reindex(columns=['Edition/Newsletter', 'Date Issued', 'Description of change in newsletter', 'Code/Subdivision change'])

    #replace all null/nan with empty string
    iso3166_df.fillna("", inplace = True)

    return iso3166_df

def correct_columns(cols):
    """ 
    Update column names so all dataframes follow the column format of:
    ["Edition/Newsletter", "Date Issued", "Description of change in newsletter", 
    "Code/Subdivision change"]. 

    Parameters
    ----------
    : cols : list
        list of column names from header of parsed Changes table on wiki.
    
    Returns
    -------
    : cols : list
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
    : table_tag : bs4.element.Tag
        bs4 object of table element.
    
    Returns
    -------
    : table : tuple
        tuple of parsed data from html table in Changes section of ISO3166 wiki.
    
    Reference
    ---------
    [1]: https://stackoverflow.com/questions/48393253/how-to-parse-table-with-rowspan-and-colspan

    """
    rowspans = []  # track pending rowspans
    rows = table_tag.find_all('tr') #all table rows

    # first scan, see how many columns we need
    colcount = 0
    for r, row in enumerate(rows):
        cells = row.find_all(['td', 'th'], recursive=False)
        # count columns (including spanned).
        # add active rowspans from preceding rows
        # we *ignore* the colspan value on the last cell, to prevent
        # creating 'phantom' columns with no actual cells, only extended
        # colspans. This is achieved by hardcoding the last cell width as 1. 
        # a colspan of 0 means “fill until the end” but can really only apply
        # to the last cell; ignore it elsewhere. 
        colcount = max(
            colcount,
            sum(int(c.get('colspan', 1)) or 1 for c in cells[:-1]) + len(cells[-1:]) + len(rowspans))
        # update rowspan bookkeeping; 0 is a span to the bottom. 
        rowspans += [int(c.get('rowspan', 1)) or len(rows) - r for c in cells]
        rowspans = [s - 1 for s in rowspans if s > 1]

    # it doesn't matter if there are still rowspan numbers 'active'; no extra
    # rows to show in the table means the larger than 1 rowspan numbers in the
    # last table row are ignored.

    # build an empty matrix for all possible cells
    table = [[None] * colcount for row in rows]
    # fill matrix from row data
    rowspans = {}  # track pending rowspans, column number mapping to count
    for row, row_elem in enumerate(rows):
        span_offset = 0  # how many columns are skipped due to row and colspans 
        for col, cell in enumerate(row_elem.find_all(['td', 'th'], recursive=False)):
            # adjust for preceding row and colspans
            col += span_offset
            while rowspans.get(col, 0):
                span_offset += 1
                col += 1

            # fill table data
            rowspan = rowspans[col] = int(cell.get('rowspan', 1)) or len(rows) - row
            colspan = int(cell.get('colspan', 1)) or colcount - col
            # next column is offset by the colspan
            span_offset += colspan - 1

            # if table cell is a newline character set to empty string
            if (cell.get_text() == "\n"):
                value = ""
            else:
                value = cell.get_text()

            #add href link to newsletter rows if applicable - ignore any wiki links            
            if not (cell.find('a') is None):
                if not (cell.find('a')['href'].startswith('/wiki/')):
                    value = value + " (" + cell.find('a')['href'] + ')'

            for drow, dcol in product(range(rowspan), range(colspan)):
                try:
                    table[row + drow][col + dcol] = value
                    # print(table[row + drow][col + dcol])
                    rowspans[col + dcol] = rowspan
                except IndexError:
                    # rowspan or colspan outside the confines of the table
                    pass
          
        # update rowspan bookkeeping
        rowspans = {c: s - 1 for c, s in rowspans.items() if s > 1}

    #iterate through converted table, removing any newline characters
    for row in range(0, len(table)):
        for col in range(0, len(table[row])):
            if not (table[row][col] is None):
                table[row][col] = table[row][col].replace('\n', '')

    return table 

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Get latest changes/updates of ISO3166-2 country codes.')
    parser.add_argument('-alpha2', '--alpha2', type=str, required=False, default="", help='Alpha2 code/s of ISO3166 countries to check for updates.')
    parser.add_argument('-export_filename', '--export_filename', type=str, required=False, default='', help='Filename for exported ISO updates file.')
    parser.add_argument('-export_folder', '--export_folder', type=str, required=False, default='', help='Folder where to store exported ISO files.')
    parser.add_argument('-year', '--year', type=str, required=False, default="", help='Selected year to check for updates.')

    #parse input args
    args = parser.parse_args()
    alpha2_codes = args.alpha2.split(',')
    export_filename = args.export_filename
    export_folder = args.export_folder
    year = args.year.split(',')
    alpha_codes = []

    #use all ISO3166 codes if invalid alpha2 code input, otherwise convert alpha2 to array
    if (alpha2_codes == [''] or not isinstance(alpha2_codes, list)):
        alpha2_codes = sorted(list(iso3166.countries_by_alpha2.keys()))

    #validate year input parameter 
    # year = [""]

    #sort codes in alphabetical order
    alpha2_codes.sort()
    alpha2_codes = [code.upper() for code in alpha2_codes]

    #output ISO3166 updates/changes for selected alpha2 code/s
    # get_updates(alpha2, year=year)
    get_updates(alpha2_codes, year)


