from __future__ import annotations
import os
import sys
import json
import re
import copy
import asyncio
from functools import lru_cache
from datetime import datetime
from importlib.metadata import version as _pkg_version
from pycountry import countries
import requests
from thefuzz import fuzz

@lru_cache(maxsize=None)
def _load_updates_json(filepath: str) -> dict:
    """Load and cache the ISO 3166 updates JSON, keyed by filepath to avoid repeated disk I/O."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

class Updates():
    """
    This class is used to access all the ISO-3166 updates/changes data from its respective json
    created from the data sources used in the iso3166_updates_export scripts. All of the keys
    and objects in the JSON are accessible via dot notation using the Map class. Each country 
    has the attributes: Change, Description of Change, Date Issued and Source.
    
    Date Issued is the date at which the change was published by the ISO, the Source column is 
    the name and or edition of newsletter or the Online Browsing Platform (OBP) link that the 
    ISO 3166 change/update was communicated in. The Change column is the overall summary of the
    change/update made and Description of Change is more in-depth info about the change/update 
    that was made, if applicable.

    The class also accepts a custom filepath to a custom updates object. By default the class
    will import the object that is a part of the software package distribution but if you want
    to import and use a secondary updates object, this can be done via the custom_updates_filepath
    input parameter.

    Currently there are 250 country's listed in the updates json with updates dating from 1996 up
    to the present year.

    Parameters
    ==========
    :country_code: str (default="")
        ISO 3166-1 alpha-2, alpha-3 or numeric country code to get updates data for. A list
        of country codes can also be input. If the alpha-3 or numeric codes are input, they are
        converted into their alpha-2 counterparts.
    :custom_updates_filepath: str (default="")
        filepath to updates object that class will import. This is an optional parameter, if its
        empty then the default path will be used.

    Methods
    =======
    __getitem__(alpha_code):
        get all listed updates/changes in the updates json object for an input country/countries,
        by making the instance object subscriptable and updates accessible via their alpha-2, 
        alpha-3 or numeric country codes.
    year(input_year):
        get all listed updates/changes in the updates json object for an input year, set of years,
        year range, greater than/less than year or not equal to a year.
    date_range(input_date_range, sort_by_date=""):
        get all listed updates/changes in the updates json that were published within the input date
        range, inclusive. If only one date input then get all updates from this date, inclusive.
    search(search_term, likeness_score=100, include_match_score=True):
        get all listed updates/changes in the updates JSON object for an input search keyword/item. For
        example searching for a specific subdivision/country name. The function can also accept a list 
        of keywords. A likeness score is used to allow you to ge the percentage of likeness for search 
        results.
    stats():
        return a high-level summary dict of the dataset: total updates, number of countries with
        updates, year range covered, most-updated country, most common change type, and the most
        recent Date Issued.
    check_for_updates():
        pulling the latest updates object from the repo and comparing it with the current version
        of the object, outlining any changes that need to be implemented.
    custom_update(alpha_code, custom_update_object=None, change="", date_issued="", description_of_change="", 
                      source="", delete=0, save_new=0, save_new_filename="iso3166_updates_copy.json"):
        add or delete a custom Update to an existing country on the main iso3166-updates.json 
        object. Custom Updates can be used for in-house/bespoke applications that are using 
        the iso3166-updates software but require additional custom updates to be included.
        These can be added to the default object that the software imports or on a custom
        updates object that can be exported.
    convert_to_alpha2(alpha_code):
        convert the inputted ISO 3166-1 alpha-3 or numeric country codes into their 2 letter 
        alpha-2 counterpart.
    convert_date_format(date_str):
        convert the inputted date into the YYYY-MM-DD format. 
    __str__:
        string representation of class instance.
    __repr__:
        object representation of class instance.
    __len__:
        get total length of ISO 3166 Updates object - number of country updates objects.
    __contains__:
        return True/False if the input country code is in updates object.
    __sizeof__:
        get total size of class instance in MB.

    Usage
    =====
    from iso3166_updates import *

    #create instance of class
    iso = Updates()

    #get all listed changes/updates for ALL countries 
    iso.all

    #get ALL listed country updates/changes data for Ireland, Colombia, Denmark and Finland
    iso['IE']
    iso['CO']
    iso['DK']
    iso['FI']

    #get all listed country updates/changes data for France and Germany
    iso["FR,DE"]

    #get all listed country updates/changes data for Fiji, Guyana, Haiti and Hungary
    iso["FJ,GY,HI,HU"]

    #get all listed country updates/changes data for 2016
    iso.year("2016")

    #get all listed country updates/changes data for 2002, 2009, 2023
    iso.year("2002,2009,2023")

    #get all listed country updates/changes data for years 2005 - 2010
    iso.year("2005-2010")

    #get all listed country updates/changes data with year <2009
    iso.year("<2009")

    #get all listed country updates/changes data, excluding year data for 2010,2019
    iso.year("<>2010,2019")

    #get all listed country updates/changes data with years >2020, for France
    iso.year(">2020").FR

    #get all listed country updates/changes data that have London or Edinburgh keywords in them
    iso.search("London, Edinburgh")

    #get all listed country updates/changes data that have Addition or Deletion keywords in them
    iso.search("addition, deletion")

    #get all listed country updates/changes data that were published between 2004-10-03 and 2006-07-07, inclusive, sort by date ascending
    iso.date_range("2004-10-03,2006-07-07", sort_by_date="dateAsc")

    #get all listed country updates/changes data that were published from 2020-03-10, inclusive
    iso.date_range("2020-03-10")

    #add custom update object to Liechtenstein
    iso.custom_update("LI", change="Brand new LI subdivision", date_issued="2025-01-01", description_of_change="Short description here.")
    
    #delete above custom updates object
    iso.custom_update("LI", change="Brand new LI subdivision", date_issued="2025-01-01", delete=1)

    #get total number of updates in updates object
    len(iso)

    #get total size of updates object in MB
    iso.__sizeof__()
    """
    def __init__(self, country_code: str="", custom_updates_filepath: str="") -> None:
        
        self.__version__ = _pkg_version("iso3166-updates")
        self.iso3166_updates_json_filename = "iso3166-updates.json"
        self.country_code = country_code

        #if not using a custom object filepath, use the default object in module directory 
        if custom_updates_filepath:
            self.iso3166_updates_path = custom_updates_filepath
        else:            
            self.iso3166_updates_path = os.path.join(os.path.dirname(os.path.abspath(sys.modules[self.__module__].__file__)), self.iso3166_updates_json_filename)

        #raise error if default or custom iso3166-updates json doesn't exist in folder
        if not (os.path.isfile(self.iso3166_updates_path)):
            raise OSError(f"Issue finding iso3166-updates.json in dir: {self.iso3166_updates_path}.")

        #load from cache to avoid repeated disk I/O; deepcopy for instance isolation
        try:
            self.all = copy.deepcopy(_load_updates_json(self.iso3166_updates_path))
        except json.JSONDecodeError:
            raise ValueError("Error ❗: The ISO 3166 updates file contains invalid JSON.")

        #full list of valid alpha-2 codes from pycountry
        self.valid_alpha2_codes = {country.alpha_2 for country in countries}

        #if input country code param set, iterate over data object and get updates data for specified input/inputs
        if self.country_code:
            temp_updates_data = {}
            self.country_code = self.country_code.upper().replace(" ", "").split(',')
            for i, code in enumerate(self.country_code):
                #convert 3 letter alpha-3 or numeric code into its 2 letter alpha-2 counterpart, if alpha-2 code then validate it
                converted_alpha_code = self.convert_to_alpha2(code)

                #raise error if invalid alpha code input, cannot be converted into corresponding alpha-2 code
                if (converted_alpha_code is None):
                    raise ValueError(f"Invalid ISO 3166-1 alpha country code input: {code}.")

                #set valid and converted alpha-2 code to list element
                self.country_code[i] = converted_alpha_code

                #add country's updates data to temporary object
                temp_updates_data[converted_alpha_code] = self.all[converted_alpha_code]

            #replace 'all' class attribute with filtered country/countries updates data
            self.all = temp_updates_data
    
    def __getitem__(self, alpha_code: str) -> dict:
        """
        Get all listed updates/changes in the updates json object for an input country/countries,
        using their ISO 3166-1 alpha-2, alpha-3 or numeric country codes. This function uses the Map 
        class to make the instance object of the class subscriptable. It can accept 1 or more alpha 
        codes for countries and return the data for each. If the alpha-3 or numeric codes are input 
        its converted into its alpha-2 counterpart.
        
        Parameters
        ==========
        :alpha_code: str
            one or more ISO 3166-1 alpha-2, alpha-3 or numeric country codes for sought country/
            territory updates e.g. AD, DE, EGT, 184. The alpha-3 or numeric codes will be 
            converted into their alpha-2 counterparts. 

        Returns
        =======
        :iso3166_updates_dict: dict
            dict object of country updates info for inputted code/codes.

        Usage
        =====
        from iso3166_updates import *
        
        #create instance of class
        iso = Updates()

        #get country ISO 3166 updates info for Ethiopia
        iso["ET"] 
        iso["ETH"] 
        iso["231"] 
 
        #get country ISO 3166 updates info for Gabon
        iso["GA"] 
        iso["GAB"] 
        iso["266"] 

        #get country ISO 3166 updates info for Rwanda, Tuvalu, Ukraine and Uruguay
        iso["RW, TV, UA, UY"]
        iso["RWA, TUV, UKR, URY"]
        iso["646, 798, 804, 858"]

        Raises
        ======
        TypeError:
            If input alpha code parameter isn't a string.
        ValueError:
            Invalid alpha code parameter input after validation/conversion.
            Valid alpha code input but country data not available as 'country_code' 
            parameter was input on class instantiation.
        """
        #raise type error if input isn't a string
        if not (isinstance(alpha_code, str)):
            raise TypeError(f'Input parameter {alpha_code} is not of correct datatype string, got {type(alpha_code)}.')       
    
        #stripping input of whitespace, separating multiple alpha codes, if applicable and sort list, remove any leading/trailing commas
        alpha_code = sorted([code for code in alpha_code.strip().replace(' ', '').split(',') if code])

        #object to store country data, it is a dict if more than one country or list if only one country
        iso3166_updates_dict = {}

        #iterate over all input alpha codes, appending all updates to country object, pass through Map class to access via dot notation
        for i, code in enumerate(alpha_code):

            #convert 3 letter alpha-3 or numeric code into its 2 letter alpha-2 counterpart, if alpha-2 code then validate it
            converted_alpha_code = self.convert_to_alpha2(code)
            
            #raise error if invalid alpha-2 code input or country data not imported on object instantiation 
            if not (converted_alpha_code in self.valid_alpha2_codes):
                raise ValueError(f"Invalid ISO 3166-1 alpha-2 code input: {code}.")
            if converted_alpha_code not in self.all:
                raise ValueError(f"Valid alpha-2 code input {code}, but country data not available as 'country_code' parameter was input on class instantiation,"
                                " try creating another instance of the class with no initial input parameter value, e.g iso = Updates().")

            #set valid converted alpha code to list element
            alpha_code[i] = converted_alpha_code

            #add each country update to country object, wrapping each update in Map for dot notation access
            iso3166_updates_dict[converted_alpha_code] = []
            for update in self.all[converted_alpha_code]:
                map_update = Map(update)
                #convert nested dicts into Map instances for dot notation access
                for key in map_update.keys():
                    if isinstance(map_update[key], dict):
                        map_update[key] = Map(map_update[key])
                iso3166_updates_dict[converted_alpha_code].append(map_update)
            
        #keys in updates dict needs sorted in the case of alpha-3 and or numeric codes being input
        iso3166_updates_dict = dict(sorted(iso3166_updates_dict.items()))

        #convert into instance of Map class so keys can be accessed via dot notation
        iso3166_updates_dict = Map(iso3166_updates_dict)

        return iso3166_updates_dict 
    
    def year(self, input_year: str|list) -> dict:
        """
        Get all listed updates/changes in the updates json object for an input year, set of years,
        year range, greater than/less than year or not equal to a year. The json object will be 
        iterated over and any matching updates from the "Date Issued" column will be appended 
        to the output dict.

        Parameters
        ==========
        :input_year: str|list
            single or comma separated str/list of multiple years. Can also accept a year range or a year 
            to get updates greater than or less than e.g "2015", "2009,2019", ">2022", "<2004", "2005-2012".

        Returns
        =======
        :country_output_dict: dict
            output dictionary of sought ISO 3166 updates for input year/years.
        
        Raises
        ======
        TypeError:
            Invalid data type for year input parameter.
        ValueError:
            Invalid year parameter input after validation and conversion.

        Note
        ====
        If the class was instantiated with a 'country_code' parameter, results are
        scoped to that country/countries only.
        """
        #if single str of 1 or more years input then convert to array, remove whitespace, separate using comma
        if (isinstance(input_year, str)):
            input_year = input_year.replace(' ', '').split(',')
        elif not (isinstance(input_year, list)):
            #raise error if invalid data type for year parameter
            raise TypeError(f"Invalid data type for year parameter, expected str or list, got {type(input_year)}.")
        
        #parse year filter mode flags and process input year via shared utility
        input_year, year_range, year_greater_than, year_less_than, year_not_equal = self._parse_year_filter(input_year)

        #temp object to not override original updates object
        country_output_dict = {}

        #filter updates by year; int comparisons used to avoid lexicographic issues
        if (input_year != []):
            for code in self.all:
                country_output_dict[code] = []
                for update in self.all[code]:

                    #extract integer year from Date Issued, stripping corrected date parenthetical if applicable
                    parsed = Updates._parse_date_issued(update["Date Issued"])
                    if parsed is None:
                        continue
                    current_updates_year = parsed.year

                    #exclude rows matching the input year/years
                    if (year_not_equal):
                        if current_updates_year not in [int(y) for y in input_year]:
                            country_output_dict[code].append(update)

                    #include rows where year >= input year
                    elif (year_greater_than):
                        if current_updates_year >= int(input_year[0]):
                            country_output_dict[code].append(update)

                    #include rows where year < input year
                    elif (year_less_than):
                        if current_updates_year < int(input_year[0]):
                            country_output_dict[code].append(update)

                    #include rows within year range, inclusive
                    elif (year_range):
                        if int(input_year[0]) <= current_updates_year <= int(input_year[1]):
                            country_output_dict[code].append(update)

                    #include rows matching the year/list of years
                    else:
                        for year_ in input_year:
                            if current_updates_year == int(year_):
                                country_output_dict[code].append(update)

            #remove any empty objects from dict
            country_output_dict = {i:j for i,j in country_output_dict.items() if j != []}

        #make updates object subscriptable using Map class
        country_output_dict = Map(country_output_dict)

        return country_output_dict

    def date_range(self, date: str|list, sort_by_date: str="") -> dict|list:
        """
        Get all listed updates/changes in the updates json object that have publication dates within
        the inputted date range, inclusive. The function accepts a comma separated list of 2 dates
        or a list with 2 date elements. The dates should be in the YYYY-MM-DD format. If just a 
        single date input then all updates from this date will be returned up until the present 
        day. If any invalid date formats are input then an error is raised. 

        Parameters
        ==========
        :date: str|list 
            string of 1 or 2 comma separated dates or a list of date elements.
        :sort_by_date: str (default="")
            whether to sort by publication date ascending or descending. Acceptable values are
            "dateAsc" and "dateDesc", representing date ascending or descending, respectively. 
            If data other than these are input then objects not sorted by date.

        Returns
        =======
        :date_filtered_data: dict|list
            object of all found updates/changes that were published within the input date range. 
            If the sort_by_date parameter is set a list of updates, sorted by date descending
            or ascending will be returned.

        Raises
        ======
        ValueError: 
            Invalid parameter or date format input.
        TypeError:
            Input parameter wasn't a string or list.

        Note
        ====
        If the class was instantiated with a 'country_code' parameter, results are
        scoped to that country/countries only.
        """
        #carry out relevant data validation if the input date is a string
        if isinstance(date, str):
            date_parts = date.split(",")
            date_parts = [d.strip() for d in date_parts] 
        #carry out relevant data validation if the input date is a list
        elif isinstance(date, list):
            date_parts = date
        #raise error if input isn't a string or list
        else:
            raise TypeError(f"Input must be a string or a list of two dates , got {date}.")
        
        #if only one date input, treat this as the starting date, setting the end date as today
        if len(date_parts) == 1:
            date_parts.append(datetime.today().strftime("%Y-%m-%d"))
        elif len(date_parts) != 2:
            raise ValueError(f"Date input must contain either one or two dates, got: {date_parts}.")

        #extra start and end date and convert each
        start_date, end_date = date_parts[0], date_parts[1]
        start_date = self.convert_date_format(start_date)
        end_date = self.convert_date_format(end_date)

        #raise error if start or end date couldn't be converted into the YYYY-MM-DD format
        if (start_date is None or end_date is None):
            raise ValueError(f"Input dates could not be converted into the YYYY-MM-DD format, got: {start_date, end_date}.")

        #swap dates if start_date is later than end_date
        if start_date > end_date:
            start_date, end_date = end_date, start_date

        #object to store date filtered updates data
        date_filtered_data = {}

        #iterate over all updates data, adding all data that's within desired date range
        for country_code, updates in self.all.items():
            filtered_changes = []
            for update in updates:

                #parse the original publication date from attribute
                original_date_str = update["Date Issued"].split(" ")[0]  
                original_date = datetime.strptime(original_date_str, "%Y-%m-%d")

                #extract corrected date from parenthetical in Date Issued, if present
                corrected_date_match = re.search(r"\(.*?(\d{4}-\d{2}-\d{2}).*?\)", update["Date Issued"])
                corrected_date = datetime.strptime(corrected_date_match.group(1), "%Y-%m-%d") if corrected_date_match else None
                
                #track if current date has been added to object
                update_added = False

                #check if the original date falls within the input range
                if (start_date <= original_date <= end_date): 
                    filtered_changes.append(update)
                    update_added = True

                #check if the corrected date falls within the input range
                if (corrected_date):
                    if (start_date <= corrected_date <= end_date):
                        if not (update_added):
                            filtered_changes.append(update)

            #add filtered changes to main date filtered object
            if filtered_changes:
                date_filtered_data[country_code] = filtered_changes

        #sort the updates output by date descending or ascending, skip if only one data element in output
        if (sort_by_date.lower() in ("dateasc", "datedesc") and len(date_filtered_data) > 1):
            
            #list of flattened outputs
            flattened_updates = []

            #iterate over object of updates, create copy, add Country Code attribute to identify each
            for country_code, updates in date_filtered_data.items():
                for update in updates:
                    update_with_code = update.copy()

                    #temp var of updates object, append Country Code
                    update_with_code = {"Country Code": country_code, **update_with_code}

                    #parse the original publication date from attribute
                    original_date_str = update["Date Issued"].split(" ")[0]  
                    original_date = datetime.strptime(original_date_str, "%Y-%m-%d")

                    #create new parsed date attribute for sorting 
                    update_with_code["sortable_date"] = original_date
                    
                    #append object to list
                    flattened_updates.append(update_with_code)

            #sort list of outputs by Date Issued, descending or ascending depending on input parameter
            if (sort_by_date.lower() == "datedesc"):
                flattened_updates.sort(key=lambda x: x["sortable_date"], reverse=True)
            else:
                flattened_updates.sort(key=lambda x: x["sortable_date"], reverse=False)

            #remove parsed temp date attribute
            for update in flattened_updates:
                del update["sortable_date"]

            date_filtered_data = flattened_updates

        return date_filtered_data

    def search(self, search_term: str, likeness_score: int=100, include_match_score: bool=True) -> dict|list:
        """
        Get all listed updates/changes in the updates json object that have the inputted search
        terms. It can accept 1 or more search terms and return the data for each. The 'likeness_score' 
        input parameter determines if the function searches for an exact match on the search terms or 
        searches for 1 or more near matching updates, by default it will search for an exact match 
        (likeness_score=100). Setting the likeness score between 0 and 100 will be a percentage score that 
        the Change and Description of Change attributes have to meet to be considered a match, by default
        an exact match is sought. The outputs are sorted by % match, highest matching updates first. A 
        fuzzy search algorithm is used to acquire the matching updates via "thefuzz" package.

        If a date is explicitly input in one of the search terms the Date Issued attribute will be added
        to the search space, alongside the Change and Description of Change attributes. 

        The attribute Match Score is appended to each output object, indicating the % match the input 
        search terms are to the returned updates objects. Setting include_match_score to False removes
        this attribute, returning a dict of updates sorted alphabetically by country code.

        Parameters
        ========== 
        :search_term: str
            sought search term/keywords to find in updates object.
        :likeness_score: int (default=100)
            likeness score between 1 and 100 that sets the percentage of likeness the input 
            search term is to the updates data in the dataset. The default value of 100 will 
            look for exact matches to the input search terms.
        :include_match_score: bool (default=True) 
            set to False to strip the % match score from the returned update objects. When False,
            a dict sorted alphabetically by country code is returned. When True (the default), a
            list sorted by descending match score is returned.

        Returns
        =======
        :search_results: dict/list
            output list of sought ISO 3166 updates that match the inputted search keyword(s). By 
            default (include_match_score=True) a list of results is returned, sorted by % match
            score descending. When include_match_score=False a dict sorted by country code is
            returned. If no matches found an empty list or dict will be returned.
        
        Raises
        ======
        ValueError:
            Invalid likeness score input.
        TypeError:
            Invalid data type input for search term parameter.

        Note
        ====
        If the class was instantiated with a 'country_code' parameter, results are
        scoped to that country/countries only.
        """
        #raise error if search_term parameter isn't a string
        if not (isinstance(search_term, str)):
            raise TypeError(f"Input search term should be of type str, got {type(search_term)}.")

        #raise error if invalid (1-100) likeness score input
        if not (1 <= likeness_score <= 100):
            raise ValueError(f"Likeness score must be between 1 and 100, got {likeness_score}.")

        #split search terms into comma separated list 
        search_terms = [term.strip().lower() for term in search_term.split(",")]

        #store search results
        search_results = []

        #iterate through main country updates data object 
        for country_code, updates in self.all.items():
            for update in updates:
                #combine main change and description attributes into one search space 
                combined_text = f"{update['Change']} {update.get('Description of Change', '')}".lower()

                #iterate over all input search terms
                for term in search_terms:
                    #if input term has a date in it, try to parse into supported YYYY-MM-DD format, else return None
                    input_date_original = self.convert_date_format(term)

                    #if valid date found in search term, add Date Issued attribute data to search space
                    if not (input_date_original is None):
                        input_date_converted = str(self.convert_date_format(term)).split(" ")[0]
                        combined_text = f"{combined_text}{update.get('Date Issued').strip()}".lower()
                        term = input_date_converted

                    #temp var of updates object, append Country Code
                    temp_search_result = {"Country Code": country_code, **update}

                    #create regex pattern for term, 2 regex patterns are supported depending on if non-word characters are in the term e.g "2023-11-23"
                    if re.search(r'\W', term):  # contains non-word characters (like "-", ".", etc.)
                        word_pattern = re.escape(term)
                    else:
                        word_pattern = r'\b{}\b'.format(re.escape(term))

                    #search for exact match of keyword in combined search text
                    if re.search(word_pattern, combined_text):
                        #add Match Score of 100 to object, meaning an exact match
                        temp_search_result["Match Score"] = 100
                        search_results.append(temp_search_result)
                    #search for non-exact match, find best fuzzy search score across all words
                    else:
                        words = re.findall(r'\w+', combined_text)
                        if words:
                            #get max score across all words in text
                            score = max(fuzz.ratio(term, word) for word in words)
                            #if score is greater than likeness score threshold, append to object, add score
                            if (score >= likeness_score):
                                temp_search_result["Match Score"] = score
                                search_results.append(temp_search_result)

        #no matching data found for search terms
        if not search_results:
            print(f"No matching updates found with the given search term(s): {search_terms}")
            return search_results
        
        #if include_match_score=False, strip scores and return dict sorted by country code
        if not (include_match_score):
            for item in search_results:
                item.pop("Match Score", None)

            #group results by country code, preserving all matches per country
            temp_search_results = {}
            for update in search_results:
                code = update["Country Code"]
                update_copy = {k: v for k, v in update.items() if k != "Country Code"}
                temp_search_results.setdefault(code, []).append(update_copy)

            #sort dict by country code, alphabetically
            search_results = dict(sorted(temp_search_results.items()))
        else:
            #sort output by matching score, highest match first
            search_results.sort(key=lambda x: x["Match Score"], reverse=True)

        return search_results

    def custom_update(self, alpha_code: str, custom_update_object: dict=None, change: str="", date_issued: str="", description_of_change: str="", 
                      source: str="", delete: bool=False, save_new: bool=False, save_new_filename: str="iso3166_updates_copy.json") -> None:
        """  
        Add or delete a custom change/update to an existing country in the main iso3166-updates.json 
        object. Custom updates can be used for in-house/bespoke applications that are using 
        the iso3166-updates software but require additional custom changes/updates to be included. 
        When adding a new update, the "Change" and "Date Issued" attributes are required
        with the "Description of Change" and "Source" attributes being optional. You can also pass
        an object of the changes to the function via the custom_update_object parameter. If the input 
        custom change/update already exists then an error will be raised, otherwise it will be 
        appended to the object. 

        If the added change/update is required to be deleted from the object, then you can 
        call the same function with the "Change" and "Date Issued" parameters/attributes
        of the added Update, but also setting the 'delete' parameter to 1/True. You can 
        also uninstall and reinstall. 

        To avoid writing over the main existing updates file you can export to a separate object 
        via the `save_new` and `save_new_filename` parameters.

        Note that this is a destructive yet temporary functionality. Adding a new custom 
        change/update will make the dataset out of sync with the official ISO 3166 Updates data, 
        therefore it is the user's responsibility to keep track of any custom Updates
        and delete them when necessary.

        Parameters
        ==========
        :alpha_code: str
            ISO 3166-1 alpha-2, alpha-3 or numeric country code.
        :custom_update_object: dict (default=None)
            object of the new custom updates object with the required attributes and values. If this 
            object is populated, the values in this object will be prioritised over the individual 
            parameter values. 
        :change: str (default="")
            ISO 3166 change/updates.
        :date_issued: str (default="")
            date that the change/update was published.
        :description_of_change: str (default="")
            description of the change/update.
        :source: str (default="")
            source of the change/update, usually a URL to the edition/newsletter if applicable. 
        :delete: bool (default=0)
            the delete flag is set to 1 if the inputted change/update is to be deleted
            from json object.      
        :save_new: bool (default=0)
            save a new copy of the iso3166-updates.json object with the new changes applied,
            such that the original object is not overwritten. 
        :save_new_filename: str (default="iso3166_updates_copy.json")
            filename for copied iso3166-updates.json object with the new changes applied.

        Returns
        ======= 
        None

        Usage
        =====
        from iso3166_updates import *

        #create instance of Updates() class
        iso3166_updates = Updates()

        #adding custom ISO 3166 Updates to Uzbekistan
        iso.custom_update("UZ", change="Example ISO 3166 update for UZ", description_of_change="blahblahblah", date_issued="2025-01-01", source="https://en.wikipedia.org/wiki/ISO_3166-2:US")
        
        #adding custom ISO 3166 Updates to France
        iso.custom_update("FR", custom_update_object=custom_update_object)

        #adding custom ISO 3166 Updates to Lebanon
        iso.custom_update("LB", change="Example ISO 3166 update for LB", date_issued="2025-01-01")

        #deleting above custom subdivisions
        iso.custom_update("UZ", change="Example ISO 3166 update for UZ", date_issued="2025-01-01", delete=1)
        iso.custom_update("LB", change="example ISO 3166 update for LB", date_issued="2025-01-01", delete=1)

        Raises
        ======
        TypeError:
            Invalid data type input for the function parameters.
        ValueError:
            Invalid ISO 3166-1 alpha-2 country code input.
            Invalid date format for Date Issued attribute.
            No matching updates found when delete parameter set. 
            New custom update object already present in main updates object.
        """
        #default to empty dict to avoid mutable default argument issue
        if custom_update_object is None:
            custom_update_object = {}

        #raise type error if input isn't a string
        if not (isinstance(alpha_code, str)):
            raise TypeError(f"Input alpha_code parameter is not of correct datatype string, got {type(alpha_code)}.")       

        #raise type error if input isn't a string
        if not (isinstance(change, str)):
            raise TypeError(f"Input Change parameter is not of correct datatype string, got {type(change)}.")   
 
        #raise type error if type isn't a string
        if not (isinstance(description_of_change, str)):
            raise TypeError(f"Input Description of Change parameter is not of correct datatype string, got {type(description_of_change)}.")  

        #raise type error if type isn't a string 
        if not (isinstance(date_issued, str)):
            raise TypeError(f"Input Date Issued parameter is not of correct datatype string, got {type(date_issued)}.")  
    
        #raise type error if type isn't a string
        if not (isinstance(source, str)):
            raise TypeError(f"Input Source parameter is not of correct datatype string, got {type(source)}.")  

        #uppercase and remove whitespace
        alpha_code = alpha_code.upper().replace(' ', '')

        #convert 3 letter alpha-3 or numeric code into its 2 letter alpha-2 counterpart, if alpha-2 code then validate it
        converted_alpha_code = self.convert_to_alpha2(alpha_code)

        #raise error if invalid alpha code input, cannot be converted into corresponding alpha-2 code
        if (converted_alpha_code is None):
            raise ValueError(f"Invalid ISO 3166-1 alpha-2 country code input: {alpha_code}.")

        #set valid and converted alpha-2 code to alpha code var
        alpha_code = converted_alpha_code

        #validate and correct date format, if applicable, raise error if date can't be converted
        if date_issued:
            converted_date = self.convert_date_format(date_issued)
            if converted_date is None:
                raise ValueError(f"Invalid date format for Date Issued, got: {date_issued}.")
            date_issued = converted_date.strftime("%Y-%m-%d")
        if custom_update_object and "Date Issued" in custom_update_object:
            converted_date = self.convert_date_format(custom_update_object["Date Issued"])
            if converted_date is None:
                raise ValueError(f"Invalid date format for Date Issued in custom update object, got: {custom_update_object['Date Issued']}.")
            custom_update_object["Date Issued"] = converted_date.strftime("%Y-%m-%d")

        #raise error if Change and Date Issued attributes not in object, add Desc of Change and Source if they're not present
        if (custom_update_object):
            if not all(element in custom_update_object for element in ["Change", "Date Issued"]):
                raise ValueError("If inputting a custom updates object, the Change and Date Issued attributes are required.")
            if not ("Description of Change" in custom_update_object):
                custom_update_object["Description of Change"] = ""
            if not ("Source" in custom_update_object):
                custom_update_object["Source"] = ""

        #raise error if not deleting and neither custom_update_object nor change+date_issued are provided
        if not delete and not custom_update_object and not (change and date_issued):
            raise ValueError("When adding a custom update, either 'custom_update_object' or both 'change' and 'date_issued' parameters must be provided.")

        #get all updates data for current country updates
        all_updates_data = self.all[alpha_code]

        #pre-build the new update record and mark as ready-to-add; the loop below will
        #clear this flag if a duplicate is detected or set delete_object_found on success
        if not delete:
            if custom_update_object:
                custom_updates_data = {key: custom_update_object[key] for key in ['Change', 'Description of Change', 'Date Issued', 'Source']}
            else:
                custom_updates_data = {"Change": change, "Date Issued": date_issued, "Description of Change": description_of_change, "Source": source}
            new_update_object = True
        else:
            custom_updates_data = {}
            new_update_object = False

        delete_object_found = False

        #iterate over all current updates for country code
        for i, entry_data in enumerate(all_updates_data):

            #delete update if delete parameter set, iterate over each update for country code and delete matching, raise error if no match found
            if (delete):
                if (custom_update_object):
                    #if matching update found, delete from current object
                    if (entry_data['Change'].strip().lower() == custom_update_object['Change'].strip().lower() and
                        entry_data['Date Issued'].strip() == custom_update_object['Date Issued'].strip()):
                        del all_updates_data[i]
                        delete_object_found = True
                        break
                else:
                    #if matching update found, delete from current object
                    if (entry_data['Change'].strip().lower() == change.strip().lower() and
                        entry_data['Date Issued'].strip() == date_issued.strip()):
                        del all_updates_data[i]
                        delete_object_found = True
                        break
            else:
                if (custom_update_object):
                    #if existing update found in object raise error
                    if (entry_data['Change'].strip().lower() == custom_update_object['Change'].strip().lower() and
                        entry_data['Date Issued'].strip() == custom_update_object['Date Issued'].strip()):
                        raise ValueError(f"Custom updates object should be unique and not already present an existing update: {custom_update_object}.")
                else:
                    #if existing update found in object raise error
                    if (entry_data['Change'].strip().lower() == change.strip().lower() and
                        entry_data['Date Issued'].strip() == date_issued.strip()):
                        raise ValueError(f"Custom updates object should be unique and not already present an existing code: {change}.")

        #add new object to main class object
        if (new_update_object):
            self.all[alpha_code].append(custom_updates_data)

        #raise error if object to be deleted not found in updates object, 
        elif (delete and not delete_object_found):
            raise ValueError(f"No matching updates object found to delete.")

        #export new updates object to custom output if parameter set
        if (save_new):
            with open(save_new_filename, 'w', encoding='utf-8') as output_json:
                json.dump(self.all, output_json, ensure_ascii=False, indent=4)  
        #export new updates object to existing object
        else:
            with open(os.path.join(self.iso3166_updates_path), 'w', encoding='utf-8') as output_json:
                json.dump(self.all, output_json, ensure_ascii=False, indent=4)
            #invalidate cache so future instantiations reload the updated file
            _load_updates_json.cache_clear()

    def check_for_updates(self, since_date: str="", since_version: str="") -> dict:
        """ 
        Pull the latest version of the object from the repo, comparing it with the current 
        version of the object installed in the software. If new updates/changes are found,
        they are listed and a message encouraging the user to download the latest version 
        is output. Returns a structured dict describing any new or changed records so
        callers can act programmatically (e.g. fail a CI build when the dataset is stale).

        The optional ``since_date`` parameter restricts the comparison to only records
        whose ``Date Issued`` is >= the supplied date, making it easy to audit "what
        changed since our last deployment."  The optional ``since_version`` parameter
        fetches the JSON at that tagged release from GitHub and uses it as the baseline
        instead of the locally-installed copy.

        Parameters
        ==========
        :since_date: str (default="")
            ISO 8601 date string (YYYY-MM-DD).  When set, only records published on or
            after this date are included in the diff.  Accepts any format recognised by
            ``convert_date_format``.
        :since_version: str (default="")
            A version tag (e.g. ``"1.8.0"``) that is used to fetch the historic JSON
            from GitHub as the baseline for the comparison, instead of the local copy.

        Returns
        =======
        :result: dict
            A structured dict with keys:
            - ``"updates_found"`` (bool): True when at least one new record was found.
            - ``"total_updates"`` (int): total count of new records across all countries.
            - ``"total_countries"`` (int): number of countries that have new records.
            - ``"updates"`` (dict): mapping of alpha-2 code to list of new update dicts.

        Raises
        ====== 
        ValueError:
            Invalid ``since_date`` or ``since_version`` format.
        RequestException:
            Error retrieving the updates JSON from main GitHub repo. 
        """
        #validate and parse since_date if provided
        since_date_dt = None
        if since_date:
            since_date_dt = self.convert_date_format(since_date)
            if since_date_dt is None:
                raise ValueError(f"Invalid since_date format, got: {since_date!r}. Expected YYYY-MM-DD or another recognised date format.")

        #determine the baseline JSON URL — either a tagged release or the latest main branch
        if since_version:
            #validate version string
            if not re.match(r'^\d+\.\d+(\.\d+)?$', since_version.strip()):
                raise ValueError(f"Invalid since_version format, expected e.g. '1.8.0', got: {since_version!r}.")
            updates_url = f"https://raw.githubusercontent.com/amckenna41/iso3166-updates/v{since_version.strip()}/iso3166_updates/iso3166-updates.json"
        else:
            updates_url = "https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166_updates/iso3166-updates.json"

        #pull latest (or versioned) data object from repo
        try:
            response = requests.get(updates_url, timeout=15)
            response.raise_for_status()
            latest_iso3166_updates_json = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch the latest Updates data from repo: {e}.")
            return {"updates_found": False, "total_updates": 0, "total_countries": 0, "updates": {}}

        #separate object that holds individual data objects that were found on the object in the repo that weren't in the software object
        new_iso3166_updates = {}

        #bool to track if any new updates found
        updates_found = False

        #baseline is either the versioned repo JSON (since_version path) or the local installed copy
        baseline_json = latest_iso3166_updates_json if since_version else self.all

        #when since_version is set, compare *latest main* against the *versioned baseline*
        #when not set, compare *latest main* against the *local installed copy*
        compare_against = self.all if not since_version else {}
        if since_version:
            #re-fetch latest main to compare against the versioned baseline
            try:
                main_response = requests.get(
                    "https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166_updates/iso3166-updates.json",
                    timeout=15
                )
                main_response.raise_for_status()
                compare_against = main_response.json()
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch the latest Updates data from repo: {e}.")
                return {"updates_found": False, "total_updates": 0, "total_countries": 0, "updates": {}}

        #iterate over all ISO 3166 updates data in the compare_against object
        for alpha_code, entries in compare_against.items():
            baseline_entries = baseline_json.get(alpha_code, [])
            new_iso3166_updates[alpha_code] = []

            #iterate over individual updates entries, add to object if not in baseline
            for update in entries:
                if update not in baseline_entries:
                    #apply since_date filter if set
                    if since_date_dt:
                        raw_date_str = update.get("Date Issued", "").split("(")[0].strip().split(" ")[0].strip()
                        try:
                            update_dt = datetime.strptime(raw_date_str, "%Y-%m-%d")
                        except ValueError:
                            continue
                        if update_dt < since_date_dt:
                            continue
                    updates_found = True
                    new_iso3166_updates[alpha_code].append(update)

            #if current alpha-2 code has no new ISO 3166 updates associated with it, remove from temp object
            if not new_iso3166_updates[alpha_code]:
                new_iso3166_updates.pop(alpha_code, None)

        #print out any found updates 
        if (updates_found):

            print("New ISO 3166 Updates data found, please update the iso3166-updates software to incorporate these latest changes, you can do this by running: pip install iso3166-updates --upgrade\n")

            #get total sum of new data updates for all countries in json
            total_updates = sum(len(v) for v in new_iso3166_updates.values())
            total_countries = len(new_iso3166_updates)
            
            print(f"{total_updates} update(s) found for {total_countries} country/countries, these are outlined below")
            print("===================================================================\n\n")
            
            #iterate over new data in json
            for code in list(new_iso3166_updates.keys()):
                
                #output current country name and code
                print(f"{countries.get(alpha_2=code).name} ({code}):")
                
                #iterate over rows of new data and print each update as formatted JSON
                for update_row in new_iso3166_updates[code]:
                    print(json.dumps(update_row, indent=2, ensure_ascii=False))
                    print("\n")
        else:
            print("No new updates found for iso3166-updates.")
        
        #return structured diff for programmatic use
        return {
            "updates_found": updates_found,
            "total_updates": sum(len(v) for v in new_iso3166_updates.values()),
            "total_countries": len(new_iso3166_updates),
            "updates": new_iso3166_updates,
        }

    @property
    def last_updated(self) -> str:
        """
        Return the most recent ``Date Issued`` value found anywhere in the dataset
        as a ``YYYY-MM-DD`` string.  Useful for auto-populating documentation without
        maintaining a separate "last updated" date field manually.

        Returns
        =======
        :str
            Most recent publication date across the entire updates dataset in
            ``YYYY-MM-DD`` format, or an empty string if no parseable dates are found.
        """
        latest = None
        for entries in self.all.values():
            for update in entries:
                raw = update.get("Date Issued", "").split("(")[0].strip().split(" ")[0].strip()
                try:
                    dt = datetime.strptime(raw, "%Y-%m-%d")
                except ValueError:
                    continue
                if latest is None or dt > latest:
                    latest = dt
        return latest.strftime("%Y-%m-%d") if latest else ""

    def change_type(self, change_type: str) -> dict:
        """
        Filter the dataset by the structural type of ISO 3166 change using keyword
        matching on the ``Change`` and ``Description of Change`` fields.

        Supported types (case-insensitive):
        * ``addition``  — records that add new subdivisions or codes.
        * ``deletion``  — records that remove subdivisions or codes.
        * ``correction`` — records that correct existing entries (spelling, codes, etc.).
        * ``amendment`` — records that amend or modify existing entries.

        A comma-separated string of multiple types is also accepted, e.g.
        ``"correction,amendment"``.

        Parameters
        ==========
        :change_type: str
            One or more change types, comma-separated.

        Returns
        =======
        :result: Map (dict)
            Filtered updates object keyed by alpha-2 code, containing only those
            update records that match the requested change type(s).

        Raises
        ======
        TypeError:
            ``change_type`` is not a string.
        ValueError:
            An unrecognised change type was supplied.
        """
        if not isinstance(change_type, str):
            raise TypeError(f"change_type must be a string, got {type(change_type)}.")

        _valid_types = {"addition", "deletion", "correction", "amendment"}

        #keywords for each type used in the text matching pass
        _keywords = {
            "addition":   re.compile(r"(subdivisions?\s+added|addition|added)", re.IGNORECASE),
            "deletion":   re.compile(r"(subdivisions?\s+deleted|deletion|deleted|removed)", re.IGNORECASE),
            "correction": re.compile(r"(correction|corrected|correct)", re.IGNORECASE),
            "amendment":  re.compile(r"(amendment|amended|amend|modification|modified|modify|change|changed|update|updated)", re.IGNORECASE),
        }

        requested_types = [t.strip().lower() for t in change_type.split(",") if t.strip()]
        for t in requested_types:
            if t not in _valid_types:
                raise ValueError(
                    f"Unrecognised change_type {t!r}. Valid types are: {sorted(_valid_types)}."
                )

        #build combined regex from all requested types
        combined_pattern = re.compile(
            "|".join(_keywords[t].pattern for t in requested_types),
            re.IGNORECASE,
        )

        result = {}
        for code, entries in self.all.items():
            matched = []
            for update in entries:
                combined_text = f"{update.get('Change', '')} {update.get('Description of Change', '')}"
                if combined_pattern.search(combined_text):
                    matched.append(update)
            if matched:
                result[code] = matched

        return Map(result)

    def stats(self) -> dict:
        """
        Return a high-level summary of the dataset as a plain dict.

        Returns
        =======
        :dict with the following keys:
            - ``total_updates`` (int): total number of update records across all countries.
            - ``total_countries`` (int): number of countries that have at least one update.
            - ``year_range`` (list[int]): two-element list [earliest_year, latest_year] derived
              from ``Date Issued`` values that contain a recognisable four-digit year.
            - ``most_updated_country`` (str): alpha-2 code of the country with the highest
              number of update records (ties broken alphabetically).
            - ``most_common_change_type`` (str): one of ``"addition"``, ``"deletion"``,
              ``"correction"``, ``"amendment"``, or ``"unknown"`` — whichever keyword appears
              most often across all ``Change`` and ``Description of Change`` field values.
            - ``last_updated`` (str): most recent ``Date Issued`` value in ``YYYY-MM-DD`` format.

        Usage
        =====
        from iso3166_updates import *

        iso = Updates()
        iso.stats()
        # {
        #   'total_updates': <n>,          # approximate — grows over time
        #   'total_countries': <n>,
        #   'year_range': [1996, <current_year>],
        #   'most_updated_country': 'FR',
        #   'most_common_change_type': 'addition',
        #   'last_updated': '<YYYY-MM-DD>'   # approximate — updated with new data
        # }
        """
        total_updates = 0
        years = []
        updates_per_country = {}
        change_type_counts = {"addition": 0, "deletion": 0, "correction": 0, "amendment": 0}
        change_type_patterns = {
            "addition": re.compile(r"addition|subdivisions? added|added", re.IGNORECASE),
            "deletion": re.compile(r"deletion|deleted|removed", re.IGNORECASE),
            "correction": re.compile(r"correction|corrected", re.IGNORECASE),
            "amendment": re.compile(r"amendment|amended", re.IGNORECASE),
        }

        for code, entries in self.all.items():
            count = len(entries)
            total_updates += count
            updates_per_country[code] = updates_per_country.get(code, 0) + count
            for update in entries:
                # collect year from Date Issued
                raw_date = update.get("Date Issued", "").split("(")[0].strip()
                year_match = re.search(r"\b(\d{4})\b", raw_date)
                if year_match:
                    years.append(int(year_match.group(1)))
                # classify change type
                combined = f"{update.get('Change', '')} {update.get('Description of Change', '')}"
                for ctype, pattern in change_type_patterns.items():
                    if pattern.search(combined):
                        change_type_counts[ctype] += 1

        most_updated_country = min(
            (code for code in updates_per_country if updates_per_country[code] == max(updates_per_country.values())),
        ) if updates_per_country else ""

        if change_type_counts and max(change_type_counts.values()) > 0:
            most_common = max(change_type_counts, key=lambda k: (change_type_counts[k], k))
        else:
            most_common = "unknown"

        return {
            "total_updates": total_updates,
            "total_countries": len(self.all),
            "year_range": [min(years), max(years)] if years else [],
            "most_updated_country": most_updated_country,
            "most_common_change_type": most_common,
            "last_updated": self.last_updated,
        }

    def save_to_file(self, filepath: str) -> None:
        """
        Persist the current in-memory updates dataset to a JSON file at the given
        path.  This is the companion method to ``custom_update()`` — use it to make
        custom changes durable across Python sessions without overwriting the
        package's own ``iso3166-updates.json``.

        Parameters
        ==========
        :filepath: str
            Destination path for the exported JSON file (e.g.
            ``"my_custom_updates.json"``). The file will be created or overwritten.

        Returns
        =======
        None

        Raises
        ======
        TypeError:
            ``filepath`` is not a string.
        OSError:
            The destination directory does not exist or is not writable.

        Usage
        =====
        from iso3166_updates import *

        iso = Updates()
        iso.custom_update("LI", change="Brand new LI subdivision", date_issued="2025-01-01",
                          description_of_change="Short description here.")

        # Persist the modified dataset so the custom entry survives the next session
        iso.save_to_file("my_custom_iso3166_updates.json")
        """
        if not isinstance(filepath, str):
            raise TypeError(f"filepath must be a string, got {type(filepath)}.")
        dest_dir = os.path.dirname(os.path.abspath(filepath))
        if not os.path.isdir(dest_dir):
            raise OSError(f"Destination directory does not exist: {dest_dir!r}.")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.all, f, ensure_ascii=False, indent=4)

    @staticmethod
    def _parse_date_issued(date_str: str):
        """
        Parse a raw ``Date Issued`` field value into a datetime, handling the optional
        ``(corrected YYYY-MM-DD)`` parenthetical suffix.  Returns None if the value
        cannot be parsed.
        """
        try:
            if "corrected" in date_str:
                cleaned = re.sub(r"[(].*[)]", "", date_str).replace(" ", "").replace(".", "").replace("\n", "")
            else:
                cleaned = date_str.replace("\n", "")
            return datetime.strptime(cleaned, "%Y-%m-%d")
        except ValueError:
            return None

    @staticmethod
    def _parse_year_filter(input_year: list) -> tuple:
        """
        Parse year filter input and return the processed year list with mode flags.
        Extracted as a shared utility to avoid duplicating symbol-parsing logic.

        Parameters
        ==========
        :input_year: list
            list of year strings as received from the year() method.

        Returns
        =======
        :tuple: (input_year, year_range, year_greater_than, year_less_than, year_not_equal)
        """
        year_range = False
        year_greater_than = False
        year_less_than = False
        year_not_equal = False

        #validate each year's format using regex
        for year_ in input_year:
            sanitized_year = re.sub(r"[<>]", "", year_)
            years = sanitized_year.split('-')
            for y in years:
                if not y:
                    continue
                if not re.match(r"^1[0-9]{3}$|^2[0-9]{3}$", y):
                    raise ValueError(f"Invalid year input, must be a valid year >= 1996, got {year_}.")
                elif int(y) < 1996:
                    raise ValueError(f"Invalid year input, must be a valid year >= 1996, got {year_}.")

        #a '-' separating 2 years implies a year range
        #a '>' before year means >= specified year
        #a '<' before year means < specified year
        #a '<>' before year means exclude that year/years
        if ("<>" in input_year[0]):
            year_not_equal = True
            input_year[0] = input_year[0].replace('<>', '')
        elif ('-' in input_year[0]):
            year_range = True
            input_year = input_year[0].split('-')
            if input_year[0] > input_year[1]:
                input_year[0], input_year[1] = input_year[1], input_year[0]
            if len(input_year) > 2:
                raise ValueError(f"If using a range of years, there must only be 2 years separated by a '-': {input_year}.")
        elif ('>' in input_year[0]):
            input_year = list(input_year[0].rpartition(">")[1:])
            year_greater_than = True
            input_year.remove('>')
            if len(input_year) > 2:
                raise ValueError(f"If greater than year input, there must only be 1 year prepended by a '>': {input_year}.")
        elif ('<' in input_year[0]):
            input_year = list(input_year[0].rpartition("<")[1:])
            year_less_than = True
            input_year.remove('<')
            if len(input_year) > 2:
                raise ValueError(f"If less than year input, there must only be 1 year prepended by a '<': {input_year}.")
        elif (',' in input_year[0]):
            input_year = input_year[0].split(',')

        #raise error if any remaining year-related symbols are present
        for year_ in input_year:
            if any(symbol in year_ for symbol in ["-", "<", ">"]):
                raise ValueError(f"Only one type of symbol should be input for year e.g '-', '<' or '>': {year_}.")

        return input_year, year_range, year_greater_than, year_less_than, year_not_equal

    @staticmethod
    def convert_to_alpha2(alpha_code: str) -> str:
        """ 
        Auxiliary function that converts an ISO 3166 country's 3 letter alpha-3 
        or numeric code into its 2 letter alpha-2 counterpart. The function also
        validates the input alpha-2 or converted alpha-2 code, raising an error 
        if it is invalid. None will be returned if conversion could'nt be done.

        Parameters 
        ==========
        :alpha_code: str
            3 letter ISO 3166-1 alpha-3 or numeric country code.
        
        Returns
        =======
        :alpha2_code: str | None
            2 letter ISO 3166 alpha-2 country code, looked up via pycountry.
            None returned if input cannot be converted.
        
        Raises
        ======
        TypeError:
            Invalid data type for alpha code input parameter. 
        ValueError:
            Invalid alpha code input parameter after validation/conversion. 
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
        
        #use pycountry to find corresponding alpha-2 code from its numeric code, return error if numeric code not found
        if (alpha_code.isdigit()):
            country = countries.get(numeric=alpha_code)
            if country is None:
                raise ValueError(f"Invalid ISO 3166-1 alpha numeric country code input: {initial_alpha_code}.")
            return country.alpha_2

        #return input alpha code if its valid, return error if alpha-2 code not found
        if len(alpha_code) == 2:
            if countries.get(alpha_2=alpha_code) is None:
                raise ValueError(f"Invalid ISO 3166-1 alpha-2 country code input: {initial_alpha_code}.")
            return alpha_code

        #use pycountry to find corresponding alpha-2 code from its alpha-3 code, return error if code not found
        if len(alpha_code) == 3:
            country = countries.get(alpha_3=alpha_code)
            if country is None:
                raise ValueError(f"Invalid ISO 3166-1 alpha-3 country code: {initial_alpha_code}.")
            return country.alpha_2

        return None
    
    @staticmethod
    def convert_date_format(date: str) -> datetime | None:
        """
        Convert inputted date string into the YYYY-MM-DD format. There
        are a series of accepted formats for the input date:
        '%Y-%m-%d', '%d %B %Y', '%Y-%d-%m', '%d/%m/%Y', '%d-%m-%Y', '%y-%m-%d'.

        If a matching format is not found then None will be returned.

        Parameters
        ==========
        :date: str
            input date string.

        Returns
        =======
        :parsed_date: datetime | None:
            converted date as a datetime object, or None if no recognised format matched.
        """
        #raise error if input isn't a string
        if not isinstance(date, str):
            return None
        
        #strip whitespace and "." from input date
        date = date.strip().rstrip(".") 

        #list of accepted input date formats
        date_formats = ['%Y-%m-%d', '%d %B %Y', '%Y-%d-%m', '%d/%m/%Y', '%d-%m-%Y', '%y-%m-%d']

        #iterate over accepted date formats
        for fmt in date_formats:
            try:
                #parse input date
                parsed_date = datetime.strptime(date, fmt)

                #handle potential ambiguity with the '%Y-%d-%m' format, in the case of the d & m values inputted incorrectly
                if fmt == '%Y-%d-%m':
                    day = int(date.split('-')[1])  
                    #if day is greater than 12, swap day and month, try and parse date
                    if day > 12:  
                        return parsed_date
                    else:
                        #return None if date cannot be converted into desired format
                        return None

                #return converted date 
                return parsed_date
                
            #skip to next date format iteration if the current one has failed
            except ValueError:
                continue  
  
        #return None if date cannot be converted into desired format
        return None

    def __len__(self) -> int:
        """ Get total number of ISO 3166 Updates objects. """
        return sum(len(changes) for changes in self.all.values())

    def __contains__(self, country_code: str) -> bool:
        """ Return True/False if the input country code is in updates object. """
        return country_code in self.all
        
    def __str__(self) -> str:
        """ Get string representation of class instance. """
        return f"Instance of ISO 3166 Updates class: Version {self.__version__}."
    
    def __repr__(self) -> str:
        """ Object representation of class instance. """
        return (f"<Updates(version={self.__version__!r}, "
        f"countries_loaded={len(self.all)}, "
        f"total_updates={len(self)}, "
        f"source_file={os.path.basename(self.iso3166_updates_path)!r})>")

    def __sizeof__(self) -> float:
        """ Return size of instance of ISO 3166 Updates JSON in MB. """
        size_in_bytes = os.path.getsize(self.iso3166_updates_path)  
        size_in_mb = size_in_bytes / (1024 * 1024) 
        return round(size_in_mb, 3)
class Map(dict):
    """
    Class that accepts a dict and allows you to use dot notation to access
    members of the dictionary. 
    
    Parameters
    ==========
    :dict
        input dictionary to convert into instance of map class so the keys/vals
        can be accessed via dot notation.

    Usage
    =====
    # create instance of map class
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    # Add new key
    m.new_key = 'Hello world!'
    # Or
    m['new_key'] = 'Hello world!'
    # Update values
    m.new_key = 'Yay!'
    # Or
    m['new_key'] = 'Yay!'
    # Delete key
    del m.new_key
    # Or
    del m['new_key']

    References
    ==========
    [1]: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v
        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(f"'Map' object has no attribute '{attr}'")

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


class AsyncUpdates:
    """
    Async-compatible wrapper around the synchronous :class:`Updates` class.

    All data-access methods (``all``, ``year``, ``date_range``, ``search``,
    ``change_type``, ``last_updated``) delegate synchronously because
    they operate entirely in-memory.  The ``check_for_updates`` method is
    genuinely async — it performs an HTTP fetch using ``asyncio`` with the
    standard library's ``asyncio.to_thread`` helper so it does not block the
    calling event loop, making it safe to use inside FastAPI, aiohttp, and
    similar frameworks.

    Parameters
    ==========
    :country_code: str (default="")
        Forwarded to the underlying :class:`Updates` constructor.
    :custom_updates_filepath: str (default="")
        Forwarded to the underlying :class:`Updates` constructor.

    Usage
    =====
    import asyncio
    from iso3166_updates import AsyncUpdates

    async def main():
        iso = AsyncUpdates()
        diff = await iso.check_for_updates()
        print(diff)

    asyncio.run(main())
    """

    def __init__(self, country_code: str = "", custom_updates_filepath: str = "") -> None:
        self._updates = Updates(country_code=country_code, custom_updates_filepath=custom_updates_filepath)

    # ------------------------------------------------------------------ #
    #  Synchronous pass-throughs (no I/O, safe to call directly)          #
    # ------------------------------------------------------------------ #

    @property
    def all(self) -> dict:
        """ Proxy to the underlying Updates.all attribute. """
        return self._updates.all

    @property
    def last_updated(self) -> str:
        """ Proxy to the underlying Updates.last_updated property. """
        return self._updates.last_updated

    def __getitem__(self, alpha_code: str) -> dict:
        return self._updates[alpha_code]

    def year(self, input_year) -> dict:
        return self._updates.year(input_year)

    def date_range(self, date, sort_by_date: str = "") -> dict:
        return self._updates.date_range(date, sort_by_date=sort_by_date)

    def search(self, search_term: str, likeness_score: int = 100, include_match_score: bool = True):
        return self._updates.search(search_term, likeness_score=likeness_score, include_match_score=include_match_score)

    def stats(self) -> dict:
        return self._updates.stats()

    def change_type(self, change_type: str) -> dict:
        return self._updates.change_type(change_type)

    def custom_update(self, *args, **kwargs) -> None:
        return self._updates.custom_update(*args, **kwargs)

    def save_to_file(self, filepath: str) -> None:
        return self._updates.save_to_file(filepath)

    # ------------------------------------------------------------------ #
    #  Async methods                                                       #
    # ------------------------------------------------------------------ #

    async def check_for_updates(self, since_date: str = "", since_version: str = "") -> dict:
        """
        Async version of :meth:`Updates.check_for_updates`.  Runs the synchronous
        implementation in a thread-pool executor so it does not block the event loop.

        Parameters
        ==========
        :since_date: str (default="")
            Forwarded to :meth:`Updates.check_for_updates`.
        :since_version: str (default="")
            Forwarded to :meth:`Updates.check_for_updates`.

        Returns
        =======
        :dict
            Structured diff dict — same shape as :meth:`Updates.check_for_updates`.
        """
        return await asyncio.to_thread(
            self._updates.check_for_updates, since_date=since_date, since_version=since_version
        )

    def __len__(self) -> int:
        return len(self._updates)

    def __contains__(self, country_code: str) -> bool:
        return country_code in self._updates

    def __str__(self) -> str:
        return f"AsyncUpdates wrapping: {self._updates}"

    def __repr__(self) -> str:
        return f"<AsyncUpdates({self._updates!r})>"


@lru_cache(maxsize=None)
def _load_iso3166_3_json(filepath: str) -> dict:
    """Load and cache the ISO 3166-3 JSON, keyed by filepath to avoid repeated disk I/O."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


class Iso31663:
    """
    Read-only access to the ISO 3166-3 dataset of formerly used country codes.

    ISO 3166-3 defines alpha-4 codes for countries and territories that were once
    listed in ISO 3166-1 but have since been deleted (e.g. ``DDDE`` for the German
    Democratic Republic, ``YUCS`` for the former Yugoslavia).  As of April 2024
    there are **73** codes defined in the standard.

    The dataset is bundled with the package as ``iso3166-3.json`` and is loaded
    lazily on first access.

    Parameters
    ==========
    :alpha4_code: str (default="")
        One or more comma-separated ISO 3166-3 alpha-4 codes to filter on
        (e.g. ``"DDDE"``, ``"DDDE,YUCS"``).  If empty, all 73 entries are loaded.

    Attributes
    ==========
    :all: dict
        The full (or filtered) ISO 3166-3 dataset, keyed by alpha-4 code.

    Usage
    =====
    from iso3166_updates import Iso31663

    # load all formerly used codes
    iso3 = Iso31663()
    iso3.all

    # access a single entry
    iso3["DDDE"]   # German Democratic Republic
    iso3["YUCS"]   # Socialist Federal Republic of Yugoslavia

    # access via dot notation
    iso3["DDDE"].Name
    iso3["DDDE"].Withdrawal_Date
    iso3["DDDE"].Current_Codes
    """

    def __init__(self, alpha4_code: str = "") -> None:
        self.iso3166_3_json_filename = "iso3166-3.json"
        self.iso3166_3_path = os.path.join(
            os.path.dirname(os.path.abspath(sys.modules[__name__].__file__)),
            self.iso3166_3_json_filename,
        )

        if not os.path.isfile(self.iso3166_3_path):
            raise OSError(f"ISO 3166-3 data file not found: {self.iso3166_3_path!r}.")

        try:
            self.all = copy.deepcopy(_load_iso3166_3_json(self.iso3166_3_path))
        except json.JSONDecodeError:
            raise ValueError("Error: The ISO 3166-3 data file contains invalid JSON.")

        self.alpha4_code = alpha4_code
        if self.alpha4_code:
            requested = [c.strip().upper() for c in self.alpha4_code.split(",") if c.strip()]
            filtered = {}
            for code in requested:
                if code not in self.all:
                    raise ValueError(f"Invalid or unknown ISO 3166-3 alpha-4 code: {code!r}.")
                filtered[code] = self.all[code]
            self.all = filtered

    def __getitem__(self, alpha4_code: str) -> dict:
        """
        Return the ISO 3166-3 entry for the given alpha-4 code (case-insensitive).

        Parameters
        ==========
        :alpha4_code: str
            ISO 3166-3 alpha-4 code, e.g. ``"DDDE"``.

        Returns
        =======
        :Map
            Entry dict wrapped in :class:`Map` for dot-notation access.

        Raises
        ======
        TypeError:
            Input is not a string.
        ValueError:
            Unknown alpha-4 code.
        """
        if not isinstance(alpha4_code, str):
            raise TypeError(f"Expected a string, got {type(alpha4_code)}.")
        key = alpha4_code.strip().upper()
        if key not in self.all:
            raise ValueError(f"Unknown ISO 3166-3 alpha-4 code: {key!r}.")
        return Map(self.all[key])

    def __len__(self) -> int:
        return len(self.all)

    def __contains__(self, alpha4_code: str) -> bool:
        return alpha4_code.strip().upper() in self.all

    def __str__(self) -> str:
        return f"ISO 3166-3 dataset: {len(self.all)} formerly used country codes."

    def __repr__(self) -> str:
        return f"<Iso31663(loaded={len(self.all)}, source_file={os.path.basename(self.iso3166_3_path)!r})>"