from itertools import product
import argparse
import pandas as pd
import requests
import iso3166
import os
import getpass
import json
import logging
from bs4 import BeautifulSoup
import datetime

#initialise logging library 
__version__ = "0.0.2"
log = logging.getLogger(__name__)

#initalise User-agent header for requests library 
USER_AGENT_HEADER = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(__version__,
                                       'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}

#base URL for ISO3166-2 wiki
wiki_base_url = "https://en.wikipedia.org/wiki/ISO_3166-2:"

def get_updates(iso_code, year="", export_filename="iso3166-updates", 
        export_folder="../iso3166-updates", export_json=True):
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
    :iso_code : str / list
        single string or list of ISO codes to get the latest ISO3166-2 updates from. If
        single ISO code passed in then it is converted to an iterable list.

    Returns
    -------
    None
    """
    #if single str ISO code input then convert to iterable list
    if (isinstance(iso_code, str)):
        iso_code = [iso_code]
    
    #convert year parameter string to datetime object
    if (isinstance(year, str) and year != ""):
        year = str(datetime.datetime.strptime(str(year), "%Y").year)

    all_changes = {}

    #iterate over all input ISO country codes
    for iso in iso_code:

        print("ISO Code: {} ({}) ".format(iso, wiki_base_url + iso))
        iso = iso.upper()
        export_fname = export_filename + '-' + iso 

        all_changes[iso] = {}
        # selected_iso = all_changes[iso]

        #get html content from wiki of ISO page 
        page = requests.get(wiki_base_url + iso)
        #convert html content into BS4 object
        soup = BeautifulSoup(page.content, "html.parser")

        #get Changes Section/Heading from soup 
        changesSection = soup.find("span", {"id": "Changes"})

        #skip to next iteration if no changes for ISO code found
        if (changesSection is None):
            # print("No changes section found for {} ({})".format(iso, wiki_base_url + iso))
            continue

        #get table element in Changes Section 
        table = changesSection.findNext('table')
        
        #convert html to 2D array 
        iso3166_table = table_to_array(table)

        #iterate through converted table, removing any newline characters
        for row in range(0, len(iso3166_table)):
            for col in range(0, len(iso3166_table[row])):
                if not (iso3166_table[row][col] is None):
                    iso3166_table[row][col] = iso3166_table[row][col].replace('\n', '')
        
        #convert updates html table/2D array to dataframe 
        iso3166_df = get_updates_df(iso3166_table)

        #append year onto filename
        if (year != ""): 
            export_fname = export_fname + "-" + str(year) 
            
        #create output folder if doesn't exist
        if not(os.path.isdir(export_folder)):
            os.mkdir(export_folder)

        #only export non-empty dataframes         
        if not (iso3166_df.empty):
            iso3166_df.to_csv(os.path.join(export_folder, export_fname + '.csv'), index=False)
        
        #add ISO updates to object of all ISO updates, convert to json 

        all_changes[iso] = json.loads(iso3166_df.to_json(orient='records'))

        #reset export filename var 
        export_fname = export_filename

    if (export_json):
        with open("iso3166-updates.json", "w") as write_file:
            json.dump(all_changes, write_file, indent=4)
        # export_to_json(all_changes)

    print("All ISO3166 changes exported to folder {}".format(export_folder))

def get_updates_df(iso3166_updates_table):
    """

    Parameters
    ----------
    :iso3166_updates_table : array
        2D array of ISO3166-2 updates from Changes section in wiki

    Returns
    -------
    :iso3166_df : pd.DataFrame
        comverted pandas dataframe of all ISO3166-2 changes for particular country
        from 2D input array.
    """
    #convert 2D array into dataframe             
    iso3166_df = pd.DataFrame(iso3166_updates_table[1:], columns=iso3166_updates_table[0])

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
    if (year != ""): 
        iso3166_df['Year'] = iso3166_df[dateColName].apply(convert_date)         #create temp new column to get year of updates from date column 
        iso3166_df = iso3166_df.drop(iso3166_df[iso3166_df['Year'] != year].index)
        iso3166_df = iso3166_df.drop('Year', axis=1)
        export_fname = export_fname + "-" + str(year) #append year onto filename

    return iso3166_df

def export_to_json(all_changes):
    pass
    

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
        tuple of parsed data from html table in Changes section of ISO wiki.
    
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

            for drow, dcol in product(range(rowspan), range(colspan)):
                try:
                    table[row + drow][col + dcol] = value
                    rowspans[col + dcol] = rowspan
                except IndexError:
                    # rowspan or colspan outside the confines of the table
                    pass
          
        # update rowspan bookkeeping
        rowspans = {c: s - 1 for c, s in rowspans.items() if s > 1}

    return table 

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Get latest changes/updates of ISO3166-2 country codes.')
    parser.add_argument('-iso_code', '--iso_code', type=str, required=False, default="", help='ISO code/s of countries to check for updates.')
    parser.add_argument('-export_filename', '--export_filename', type=str, required=False, default='', help='Filename for exported ISO updates file.')
    parser.add_argument('-export_folder', '--export_folder', type=str, required=False, default='', help='Folder where to store exported ISO files.')
    parser.add_argument('-year', '--year', type=str, required=False, default='', help='Selected year to check for updates.')

    #parse input args
    args = parser.parse_args()
    iso_code = args.iso_code
    export_filename = args.export_filename
    export_folder = args.export_folder
    year = args.year

    #get list of ISO3166 codes from iso3166 library 
    all_iso_codes = sorted(list(iso3166.countries_by_alpha2.keys()))

    #use all ISO3166 codes if invalid ISO code input, otherwise convert iso_code to array
    if ((not isinstance(iso_code, str)) or (len(iso_code) != 2) or (iso_code not in all_iso_codes)):
        iso_code = all_iso_codes
    else:
        iso_code = [iso_code]

    #output ISO3166 updates/changes for selected ISO code/s
    get_updates(iso_code)


