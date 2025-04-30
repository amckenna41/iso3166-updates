import pandas as pd
import re
from bs4 import Tag
from iso3166_updates_export.utils import *

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