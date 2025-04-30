import argparse
from typing import Dict, List, Union
from tqdm import tqdm
from iso3166_updates_export.utils import *
from iso3166_updates_export.get_updates_data import *

def get_iso3166_updates(alpha_codes: str="", year: str="", export_filename: str="iso3166-updates", export_folder: str="iso3166-updates-output",
        alpha_codes_range: str="", concat_updates: bool=True, export_json: bool=True, export_csv: bool=True, export_xml: bool=False, verbose: bool=True, 
        use_selenium: bool=True, use_wiki: bool=True, include_remarks_data: bool=True, save_each_iteration=False) -> Dict[str, Union[List[Dict], pd.DataFrame]]:
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
    :alpha_codes: str (default="")
        single string or comma separated list of ISO 3166-1 alpha-2, alpha-3 or numeric country codes,
        to get the latest ISO 3166 updates from. Any alpha-3 or numeric codes input are converted to their
        alpha-2 equivalent. If no value passed into param then all updates for all ISO 3166-1 countries are retrieved.
    :year: str (default="")
        single string or comma separated list of 1 or more years to get the specific ISO 3166 updates from,
        per country. By default the year param will be empty meaning all changes/updates for all years
        will be retrieved. You can also pass in a year range (e.g 2010-2015) or a year to get all updates
        less than or greater than that specified year (e.g >2007, <2021), as well as all updates except
        for a specific year (e.g <>2009).
    :export_filename: str (default="iso3166-updates")
        filename for JSON and CSV output files of inputted country's ISO 3166 updates.
    :export_folder: str (default="iso3166-updates-output")
        folder name to store all csv and json outputs for all country's ISO 3166 updates.
    :alpha_codes_range: str (default="")
        a range of 2 ISO 3166-1 alpha-2, alpha-3 or numeric country codes to export the updates data from, 
        separated by a '-'. The code on the left hand side will be the starting alpha code and the code on 
        the right hand side will be the final alpha code to which the data is exported from, e.g AD-LV, 
        will export all updates data from Andorra to Latvia, alphabetically. Useful if a subset of codes 
        are required. If only a single alpha code input then it will serve as the starting country.
    :concat_updates: bool (default=True)
        if multiple alpha codes input, concatenate updates into one JSON and or CSV file (concat_updates=True) 
        or into separately named files in export folder (concat_updates=False). By default all country's 
        updates will be compiled into the same files.
    :export_json: bool (default=True)
        export all ISO 3166 updates for inputted countries into JSON format in export folder.
    :export_csv: bool (default=True)
        export all ISO 3166 updates for inputted countries into CSV format in export folder.
    :export_xml: bool (default=False)
        export all ISO 3166 updates for inputted countries into XML format in export folder.
    :verbose: bool (default=False)
        Set to 1 to print out progress of updates functionality, 0 will not print progress.
    :use_selenium: bool (default=True)
        Gather all updates data for each country from its official page on the ISO website which
        requires Python Selenium and Chromedriver. By default this data is pulled.
    :use_wiki: bool (default=True)
        Gather all updates data for each country from its official wiki page. By default this 
        data is pulled.
    :include_remarks_data: bool (default=True)
        whether to include the remarks text in country updates export. Remarks are additional 
        notes on the change published by the ISO and are prevalent throughout the ISO pages;
        sometimes the remarks may be split up until parts (1 to 4). If True then the remarks 
        data will be parsed and added in brackets after their mention. By default the remarks
        are added to ensure all the info is captured from the updates data.
    :save_each_iteration: bool (default=False)
        if this parameter is set then during each country code iteration, the exports data will be 
        saved to the export dir, rather than at the end all in one go. This was implemented as 
        sometimes the Selenium session would timeout, loosing all the progress of the previous 
        iterations. This is only for the JSON exports. The exported JSON on each iteration will 
        contain all the exported data up until and including the current iteration and not just 
        the current iteration data. 

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
    year_range = False
    year_greater_than = False
    year_less_than = False
    year_not_equal = False

    #raise error if input alpha codes param is not a str
    if not (isinstance(alpha_codes, str)):
      raise TypeError(f"Expected input alpha_codes parameter to be a string, got {type(alpha_codes)}.")

    #keep track of original input alpha codes list 
    input_alpha_codes = alpha_codes

    #validate and convert inputted alpha codes and alpha codes range, if applicable
    alpha_codes_list, alpha_codes_range = get_alpha_codes_list(alpha_codes, alpha_codes_range)

    #validate input year 
    #a '-' separating 2 years implies a year range of sought country updates
    #a ',' separating 2 years implies a list of years
    #a '>' before year means get all country updates greater than or equal to specified year
    #a '<' before year means get all country updates less than specified year
    #a '<>' before the year means don't include year/list of years in export 
    year, year_range, year_greater_than, year_less_than, year_not_equal = validate_year(year)

    #object to store all country updates/changes
    all_iso3166_updates = {}

    #start elapsed time counter
    start = time.time()
    
    #initalise tqdm progress bar, if less than 5 alpha-2 codes input then don't display progress bar, or print elapsed time
    progress_bar = tqdm(alpha_codes_list, ncols=80, disable=(len(alpha_codes_list) < 5))

    #iterate over all input ISO 3166-1 country codes
    for alpha2 in progress_bar:
        progress_bar.set_description(f"{iso3166.countries_by_alpha2[alpha2].name.title()} ({alpha2})")        

        #initialise object of updates for current alpha-2 code
        all_iso3166_updates[alpha2] = []

        #pull wiki and ISO data depending on respective parameter bools
        if (use_wiki and use_selenium):

            #web scrape country's wiki data, convert html table/2D array to dataframe
            iso3166_df_wiki = get_updates_df_wiki(alpha2)

            #use Selenium Chromedriver to parse country's updates data from official ISO website
            iso_website_df, remarks_data = get_updates_df_selenium(alpha2, include_remarks_data)

            #concatenate two updates dataframes
            iso3166_df = pd.concat([iso3166_df_wiki, iso_website_df], ignore_index=True, sort=False)

        #pull just wiki data 
        elif (use_wiki):

            #web scrape country's wiki data, convert html table/2D array to dataframe
            iso3166_df = get_updates_df_wiki(alpha2)

        #pull just ISO page data 
        elif (use_selenium):

            #use Selenium Chromedriver to parse country's updates data from official ISO website
            iso3166_df, remarks_data = get_updates_df_selenium(alpha2, include_remarks_data)
        
        #raise error if both bools are set to False, no data being exported
        else:
            raise ValueError("No data exported as both bools are set to False, use_selenium & use_wiki = False.")
        
        #if updates dataframe is empty, skip to next iteration
        if (iso3166_df.empty):
            continue

        #if year parameter input, filter in/out the relevant rows depending on year values
        if (year and year != ['']):
            iso3166_df = filter_year(iso3166_df, year, year_range, year_greater_than, year_less_than, year_not_equal)

        #if updates dataframe is empty, skip to next iteration
        if (iso3166_df.empty):
            continue
            
        #drop any duplicate rows in object, e.g rows that have the same publication date and change/description of change attribute values
        iso3166_df = remove_duplicates(iso3166_df)

        if (use_selenium):
            if (include_remarks_data):
                if (remarks_data):
                    iso3166_df = add_remarks_data(iso3166_df, remarks_data)

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

        #save the updates data export at current iteration, useful in the case where the Selenium session might timeout
        if (save_each_iteration):
            export_updates(all_iso3166_updates, export_folder, export_filename, export_json, export_csv, export_xml, 
                           concat_updates, alpha2, alpha_codes_range, year, year_range, year_greater_than, 
                           year_less_than, year_not_equal)    

    #end elapsed time counter and calculate
    end = time.time()
    elapsed = end - start

    #auxiliary function to remove all empty nested dicts within object
    def _del(_d: dict):
        return {a:_del(b) if isinstance(b, dict) else b for a, b in _d.items() if b and not a.startswith('_')}

    #remove any empty nested updates dict if gathering all country updates with input year, keep empty dicts if list of alpha-2 codes input
    # if (year != [''] and year != ""):
    #     all_iso3166_updates = _del(all_iso3166_updates)    

    if ((year != [''] and year) and (input_alpha_codes == "" or input_alpha_codes == [''])):
        all_iso3166_updates = _del(all_iso3166_updates)    

    #add manual updates data to the output object, filter by year if applicable - temporary function
    all_iso3166_updates = manual_updates(all_iso3166_updates, year, year_range, year_greater_than, year_less_than, year_not_equal)

    #export all pulled ISO 3166 updates to JSON/CSV
    export_updates(all_iso3166_updates, export_folder, export_filename, export_json, export_csv, export_xml, concat_updates, alpha_codes_list, 
        alpha_codes_range, year, year_range, year_greater_than, year_less_than, year_not_equal)
    #export_updates(all_iso3166_updates, **export_params)

    #print out elapsed time for export
    if (verbose):
        print(f"Total elapsed time for executing script: {round(elapsed/60, 2)} minutes.")

    return all_iso3166_updates

if __name__ == "__main__":
    """ 
    Main entry script for full ISO 3166 Updates export pipeline. The get_iso3166_updates function is called function 
    that parses any input parameters using argparse library, passing in all the required parameters.
    """
    parser = argparse.ArgumentParser(description='Get latest changes/updates for all countries in the ISO 3166-1/3166-2 standards.')
    parser.add_argument('-alpha_codes', '--alpha_codes', type=str, required=False, default="", 
        help='Comma separated ISO 3166-1 alpha-2, alpha-3 or numeric country codes to export updates.')
    parser.add_argument('-year', '--year', type=str, required=False, default="", 
        help='Selected year(s) to check for updates, can also be a year range ("2010-2020"), greater than (">2007"), less than ("<2024") or not equal to ("<>2001") specific year.')
    parser.add_argument('-export_filename', '--export_filename', type=str, required=False, default="iso3166-updates", 
        help='Filename for exported ISO 3166 updates CSV and JSON files.')
    parser.add_argument('-export_folder', '--export_folder', type=str, required=False, default="test-iso3166-updates", 
        help='Folder where to store exported ISO 3166 updates files.')
    parser.add_argument('-alpha_codes_range', '--alpha_codes_range', type=str, required=False, default="", 
        help='Range of alpha codes to export from, inclusive. If only a single alpha code input then it will serve as the starting country.')
    parser.add_argument('-export_json', '--export_json', required=False, action=argparse.BooleanOptionalAction, default=1,
        help='Whether to export all found updates to json in export folder.')
    parser.add_argument('-export_csv', '--export_csv', required=False, action=argparse.BooleanOptionalAction, default=1,
        help='Whether to export all found updates to csv files in export folder.')
    parser.add_argument('-export_xml', '--export_xml', required=False, action=argparse.BooleanOptionalAction, default=0,
        help='Whether to export all found updates to xml files in export folder.')
    parser.add_argument('-concat_updates', '--concat_updates', required=False, action=argparse.BooleanOptionalAction, default=1,
        help='Whether to concatenate updates of individual countries into the same json or csv files or to individual files.')
    parser.add_argument('-verbose', '--verbose', type=int, required=False, action=argparse.BooleanOptionalAction, default=1, 
        help='Set to 1 to print out progress of updates function, 0 will not print progress.')
    parser.add_argument('-use_selenium', '--use_selenium', type=int, required=False, action=argparse.BooleanOptionalAction, default=1, 
        help='Gather updates from official ISO website for each country using Selenium package.')
    parser.add_argument('-use_wiki', '--use_wiki', type=int, required=False, action=argparse.BooleanOptionalAction, default=1, 
        help='Gather updates from wiki page for each country.')
    parser.add_argument('-include_remarks_data', '--include_remarks_data', type=int, required=False, action=argparse.BooleanOptionalAction, default=1, 
        help="Append the remarks data from the country's ISO page to each of the updates data objects.")
    parser.add_argument('-save_each_iteration', '--save_each_iteration', type=int, required=False, action=argparse.BooleanOptionalAction, default=0, 
        help="Export the updates data per each individual country iteration, useful for if Selenium might timeout and export progress is lost.")
    
    #parse input args
    args = parser.parse_args()

    #output ISO 3166 updates/changes for selected alpha code(s) and year(s)
    all_iso3166_updates = get_iso3166_updates(**vars(args))
