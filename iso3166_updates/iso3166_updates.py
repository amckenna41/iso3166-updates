import os
import sys
import json
import re
from datetime import datetime
import iso3166
import platform
import requests
import pprint
from thefuzz import fuzz

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

    Currently there are 249 country's listed in the updates json with updates dating from 1996 up
    to the present year, with 910 individual published updates.

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
    date_range(input_date_range, sort_by_date=False):
        get all listed updates/changes in the updates json that were published within the input date
        range, inclusive. If only one date input then get all updates from this date, inclusive.
    search(search_term, likeness_score=1.0, exclude_match_score=0):
        get all listed updates/changes in the updates JSON object for an input search keyword/item. For
        example searching for a specific subdivision/country name. The function can also accept a list 
        of keywords. A likeness score is used to allow you to ge the percentage of likeness for search 
        results.
    check_for_updates():
        pulling the latest updates object from the repo and comparing it with the current version
        of the object, outlining any changes that need to be implemented.
    custom_update():
        add or delete a custom Update to an existing country on the main iso3166-updates.json 
        object. Custom Updates can be used for in-house/bespoke applications that are using 
        the iso3166-updates software but require additional custom updates to be included.
        These can be added to the default object that the software imports or on a custom
        updates object.
    convert_to_alpha2(alpha_code):
        convert the inputted ISO 3166-1 alpha-3 or numeric country codes into their 2 letter 
        alpha-2 counterpart.
    convert_date_format(date_str):
        convert the inputted date into the YYYY-MM-DD format. 
    __str__:
        string representation of class instance.
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

    #get all listed country updates/changes data that were published between 2004-10-03 and 2006-07-07, inclusive
    iso.date_range("2004-10-03,2006-07-07")

    #get all listed country updates/changes data that were published from 2020-03-10, inclusive
    iso.date_range("2020-03-10")

    #add custom update object to Liechtenstein
    iso.custom_update("LI", change="Brand new LI subdivision", date_issued="2025-01-01", description_of_change="Short description here.")

    #get total number of updates in updates object
    len(iso)

    #get total size of updates object in MB
    iso.__sizeof__()
    """
    def __init__(self, country_code: str="", custom_updates_filepath: str="") -> None:
        
        self.__version__ = "1.8.2"
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

        #importing all updates data from JSON, open iso3166-updates json file and load it into class variable, loading in a JSON is different in Windows & Unix/Linux systems
        #raise error if issue finding file or JSON
        if (platform.system() != "Windows"):
            try:
                with open(self.iso3166_updates_path, "r", encoding="utf-8") as f:
                    self.all = json.load(f)
            except FileNotFoundError:
                raise OSError("Error: The ISO 3166 updates file was not found.")
            except json.JSONDecodeError:
                raise ValueError("Error: The ISO 3166 updates file contains invalid JSON.")
        else:
            try:
                with open(self.iso3166_updates_path, encoding="utf-8") as iso3166_updates_json:
                    self.all = json.loads(iso3166_updates_json.read())
            except FileNotFoundError:
                raise OSError("Error: The ISO 3166 updates file was not found.")
            except json.JSONDecodeError:
                raise ValueError("Error: The ISO 3166 updates file contains invalid JSON.")
            
        #make all updates object subscriptable using Map class
        # self.all = Map(self.all)

        #full list of valid alpha-2 codes from iso3166
        self.valid_alpha2_codes = set(iso3166.countries_by_alpha2.keys())

        #if input country code param set, iterate over data object and get updates data for specified input/inputs
        if self.country_code:
            temp_updates_data = {}
            self.country_code = self.country_code.upper().replace(" ", "").split(',')
            for code in range(0, len(self.country_code)):
                #convert 3 letter alpha-3 or numeric code into its 2 letter alpha-2 counterpart, if alpha-2 code then validate it
                converted_alpha_code = self.convert_to_alpha2(self.country_code[code])

                #raise error if invalid alpha code input, cannot be converted into corresponding alpha-2 code
                if (converted_alpha_code is None):
                    raise ValueError(f"Invalid ISO 3166-1 alpha country code input: {self.country_code[code]}.")

                #set valid and converted alpha-2 code to list element
                self.country_code[code] = converted_alpha_code

                #create temporary updates data object
                temp_updates_data[self.country_code[code]] = {}
                temp_updates_data[self.country_code[code]] = self.all[self.country_code[code]]
            
            #delete existing 'all' class attribute that currently has all updates data for all countries, which aren't needed if input country is specified
            del self.all

            #set 'all' class attribute to the updates data from input country/countries
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
    
        #stripping input of whitespace, uppercasing, separating multiple alpha codes, if applicable and sort list, remove any leading/trailing commas
        alpha_code = sorted([code for code in alpha_code.strip().upper().replace(' ', '').split(',') if code])

        #object to store country data, it is a dict if more than one country or list if only one country
        iso3166_updates_dict = {}

        #iterate over all input alpha codes, appending all updates to country object, pass through Map class to access via dot notation
        for code in range(0, len(alpha_code)):

            #convert 3 letter alpha-3 or numeric code into its 2 letter alpha-2 counterpart, if alpha-2 code then validate it
            converted_alpha_code = self.convert_to_alpha2(alpha_code[code])
               
            #raise error if invalid alpha-2 code input or country data not imported on object instantiation 
            if not (converted_alpha_code in self.valid_alpha2_codes):
                raise ValueError(f"Invalid ISO 3166-1 alpha-2 code input: {alpha_code[code]}.")
            if not (converted_alpha_code in list(self.all.keys())):
                raise ValueError(f"Valid alpha-2 code input {alpha_code[code]}, but country data not available as 'country_code' parameter was input on class instantiation,"
                                " try creating another instance of the class with no initial input parameter value, e.g iso = Updates().")

            #set valid converted alpha code to list element
            alpha_code[code] = converted_alpha_code

            #add each country update to country object
            iso3166_updates_dict[alpha_code[code]] = []
            for update in range(0, len(self.all[alpha_code[code]])):
                iso3166_updates_dict[alpha_code[code]].append(Map(self.all[alpha_code[code]][update]))
                #iterate over nested dicts, convert into instances of Map class so they can be accessed via dot notation
                for key in iso3166_updates_dict[alpha_code[code]][update].keys():
                    if (isinstance(iso3166_updates_dict[alpha_code[code]][update][key], dict)):
                        iso3166_updates_dict[alpha_code[code]][update][key] = Map(iso3166_updates_dict[alpha_code[code]][update][key])
            
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
        """
        #if single str of 1 or more years input then convert to array, remove whitespace, separate using comma
        if (isinstance(input_year, str)):
            input_year = input_year.replace(' ', '').split(',')
        elif not (isinstance(input_year, list)):
            #raise error if invalid data type for year parameter
            raise TypeError(f"Invalid data type for year parameter, expected str or list, got {type(input_year)}.")
        
        country_output_dict = {}

        year_range = False
        year_greater_than = False
        year_less_than = False
        year_not_equal = False

        #validate each year's format using regex
        for year_ in input_year:
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
        if ("<>" in input_year[0]):
            year_not_equal = True
            input_year[0] = input_year[0].replace('<>', '')
        elif ('-' in input_year[0]):
            year_range = True
            input_year = input_year[0].split('-')
            #if year range years are wrong way around then swap them
            if (input_year[0] > input_year[1]):
                input_year[0], input_year[1] = input_year[1], input_year[0]
            if (len(input_year) > 2):
                raise ValueError(f"If using a range of years, there must only be 2 years separated by a '-': {input_year}.")
        #parse array for using greater than symbol
        elif ('>' in input_year[0]):
            input_year = list(input_year[0].rpartition(">")[1:])
            year_greater_than = True
            input_year.remove('>')
            if (len(input_year) > 2):
                raise ValueError(f"If greater than year input, there must only be 1 year prepended by a '>': {input_year}.")
        #parse array for using less than symbol
        elif ('<' in input_year[0]):
            input_year = list(input_year[0].rpartition("<")[1:])
            year_less_than = True
            input_year.remove('<')
            if (len(input_year) > 2):
                raise ValueError(f"If less than year input, there must only be 1 year prepended by a '<': {input_year}.")
        #split years into comma separated list of multiple years if multiple years are input
        elif (',' in input_year[0]):
            input_year = input_year[0].split(',')
        
        #raise error if any other year related symbols are in year str
        for year_ in input_year:
            if any(symbol in year_ for symbol in ["-", "<", ">"]):
                raise ValueError(f"Only one type of symbol should be input for year e.g '-', '<' or '>': {year_}.")

        #temp object to not override original updates object
        country_output_dict = {}

        #drop rows of dict where Date Issued column isn't same as year parameter, if year_greater_than, 
        #year_less_than, year_not_equal or year_range bools set then drop any objects of dict that don't meet condition
        if (input_year != []): 
            for code in self.all:
                country_output_dict[code] = []
                for update in range(0, len(self.all[code])):

                    #convert year in Date Issued column to string of year, remove "corrected" date if applicable
                    if ("corrected" in self.all[code][update]["Date Issued"]):
                        current_updates_year = str(datetime.strptime(re.sub("[(].*[)]", "", self.all[code][update]["Date Issued"]).replace(' ', "").
                                                        replace(".", '').replace('\n', ''), '%Y-%m-%d').year)
                    else:
                        current_updates_year = str(datetime.strptime(self.all[code][update]["Date Issued"].replace('\n', ''), '%Y-%m-%d').year)

                    #drop all rows that are equal to input year
                    if (year_not_equal):
                        if (current_updates_year not in input_year):
                            country_output_dict[code].append(self.all[code][update])

                    #drop all rows in dict that are less than input year
                    elif (year_greater_than):
                        if not (current_updates_year < input_year[0]):
                            country_output_dict[code].append(self.all[code][update])

                    #drop all rows in dict that are greater than or equal to input year
                    elif (year_less_than):
                        if not (current_updates_year >= input_year[0]):
                            country_output_dict[code].append(self.all[code][update])

                    #drop all rows in dict that are not within input year range
                    elif (year_range):
                        if (current_updates_year != "" and (current_updates_year >= input_year[0] and current_updates_year <= input_year[1])):
                            country_output_dict[code].append(self.all[code][update])

                    #drop all rows in dict that aren't equal to year/list of years in year parameter
                    else:
                        for year_ in input_year:
                            if (current_updates_year == str(year_)):
                                country_output_dict[code].append(self.all[code][update])

            #remove any empty objects from dict 
            country_output_dict = {i:j for i,j in country_output_dict.items() if j != []}

        #make updates object subscriptable using Map class
        country_output_dict = Map(country_output_dict)

        return country_output_dict

    def date_range(self, date: str|list, sort_by_date: bool=False) -> dict|list:
        """
        Get all listed updates/changes in the updates json object that have publication dates within
        the inputted date range, inclusive. The function accepts a comma separated list of 2 dates
        or a list with 2 date elements. The dates should be in the YYYY-MM-DD format. If just a 
        single date input then all updates from this date will be returned up until the present 
        day. If any invalid date formats are input then an error is raised. 

        Parameters
        ==========
        :date: str|list 
            string of 2 comma separated dates or a list of date elements. 
        :sort_by_date: bool
            set to True to sort the output by date descending, otherwise they are sorted by 
            the country code, alphabetically. 

        Returns
        =======
        :date_filtered_data: dict|list
            object of all found updates/changes that were published within the input date range. 
            If the sort_by_date parameter is set a list of updates, sorted by date descending
            will be returned.

        Raises
        ======
        ValueError: 
            Invalid parameter or date format input.
        TypeError:
            Input parameter wasn't a string or list.
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

        print(start_date, end_date)


        #object to store date filtered updates data
        date_filtered_data = {}

        #iterate over all updates data, adding all data that's within desired date range
        for country_code, updates in self.all.items():
            filtered_changes = []
            for update in updates:

                #parse the original publication date from attribute
                original_date_str = update["Date Issued"].split(" ")[0]  
                original_date = datetime.strptime(original_date_str, "%Y-%m-%d")

                #parse corrected date from publication date attribute, if applicable 
                cleaned_date_row = re.sub(r"\(.*?\)", "", update["Date Issued"])
                corrected_date = re.sub(r'\s+', ' ', cleaned_date_row.replace('.', '').strip())

                #convert corrected date to datetime object, if applicable 
                corrected_date = None
                if corrected_date:
                    corrected_date = datetime.strptime(corrected_date, "%Y-%m-%d")
                
                #track if current date has been added to object
                update_added = False

                #check if the original date falls within the input range
                if (start_date <= original_date <= end_date): 
                    filtered_changes.append(update)
                    update_added = True

                #check if the corrected date falls within the input range
                if (corrected_date):
                    # if (start_date <= corrected_date.strftime("%Y-%m-%d") <= end_date):
                    if (start_date <= corrected_date <= end_date):
                        if not (update_added):
                            filtered_changes.append(update)

            #add filtered changes to main date filtered object
            if filtered_changes:
                date_filtered_data[country_code] = filtered_changes

        #sort the updates output by date descending, latest first, skip if only one data element in output 
        if (sort_by_date and len(date_filtered_data) > 1):
            
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

            #sort list of outputs by Date Issued
            flattened_updates.sort(key=lambda x: x["sortable_date"], reverse=True)

            #remove parsed temp date attribute
            for update in flattened_updates:
                del update["sortable_date"]

            date_filtered_data = flattened_updates

        return date_filtered_data

    def search(self, search_term: str, likeness_score: int=100, exclude_match_score: bool=0) -> dict|list:
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
        search terms are to the returned updates objects. Setting the exclude_match_score parameter to
        1 removes this attribute, returning an object of updates, sorted by their country code. 

        Parameters
        ========== 
        :search_term: str
            sought search term/keywords to find in updates object.
        :likeness_score: int (default=100)
            likeness score between 1 and 100 that sets the percentage of likeness the input 
            search term is to the updates data in the dataset. The default value of 100 will 
            look for exact matches to the input search terms.
        :exclude_match_score: bool (default=0)
            set to True to exclude the % match the returned updates objects are to the input
            search keywords. If this attribute is excluded from the output, a dict of outputs
            will be returned, sorted alphabetically by country code, otherwise a list will be 
            returned, sorted by match score.

        Returns
        =======
        :search_results: dict/list
            output list of sought ISO 3166 updates that match the inputted search keyword(s). By 
            default a list of results is returned, sorted by % match score, otherwise a dict of 
            results, sorted by country code alpbetically is returned. If no matches found an empty 
            list or dict will be returned.
        
        Raises
        ======
        ValueError:
            Invalid likeness score input.
        TypeError:
            Invalid data type input for search term parameter.
        """
        #raise error if search_term parameter isn't a string
        if not (isinstance(search_term, str)):
            raise TypeError(f"Input search term should be of type str, got {type(search_term)}.")

        #normalise likeness_score if input is less than 1, convert to int
        if likeness_score < 1:
            likeness_score *= 100
            likeness_score = int(likeness_score)

        #raise error if invalid likeness score input
        if (likeness_score > 100):
            raise ValueError(f"Likeness score must be between 1 and 100, got {likeness_score}.")

        #split search terms into comma separated list 
        search_terms = [term.strip() for term in search_term.split(",")]

        #store search results
        search_results = []

        #iterate through main country updates data object 
        for country_code, updates in self.all.items():
            for update in updates:
                #combine main change and description attributes into one search space 
                combined_text = f"{update['Change']} {update.get('Description of Change', '')}".lower()

                #iterate over all input search terms
                for term in search_terms:
                    term = term.lower()
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
        
        #if excludeMatchScore parameter set then remove from update objects, convert object to dict and sort by country code
        if (exclude_match_score):
            [item.pop("Match Score", None) for item in search_results]

            #make Country Code attribute the parent key for the updates objects
            temp_search_results = {
                update["Country Code"]: update
                for update in search_results
            }

            #iterate over each object and remove Country Code from it 
            for code, update in temp_search_results.items():
                update.pop("Country Code", None)  

            #sort dict by country code, alphabetically
            temp_search_results = dict(sorted(temp_search_results.items()))
            search_results = temp_search_results
        else:
            #sort output by matching score, highest match first
            search_results.sort(key=lambda x: x["Match Score"], reverse=True)

        return search_results

    def custom_update(self, alpha_code: str, custom_update_object: dict={}, change: str="", date_issued: str="", description_of_change: str="", 
                      source: str="", delete: bool=0, save_new: bool=0, save_new_filename: str="iso3166_updates_copy.json") -> None:
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

        Note that this is a destructive yet temporary functionality. Adding a new custom 
        change/update will make the dataset out of sync with the official ISO 3166 Updates data, 
        therefore it is the user's responsibility to keep track of any custom Updates
        and delete them when necessary. Although you can also create the required changes to a
        temp object, specified by the save_new_filename parameter. 

        Parameters
        ==========
        :alpha_code: str
            ISO 3166-1 alpha-2, alpha-3 or numeric country code.
        :custom_update_object: dict (default={})
            object of the new custom object with the required attributes and values. If this object
            is populated, the values in this object will be prioritised over the individual 
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
        
        #raise error if Change and Date Issued attributes not in object, add Desc of Change and Source if they're not present
        if (custom_update_object):
            if not all(element in custom_update_object for element in ["Change", "Date Issued"]):
                raise ValueError("If inputting a custom updates object, the Change and Date Issued attributes are required.")
            elif not ("Description of Change" in custom_update_object):
                custom_update_object["Description of Change"] = ""
            elif not ("Source" in custom_update_object):
                custom_update_object["Source"] = ""

        #get all updates data for current country updates
        all_updates_data = self.all[alpha_code]

        #store parsed and validated custom updates
        custom_updates_data = {}

        #iterate over all current updates for country code
        for entry in range(0, len(all_updates_data)):
            
            #bool to track if custom updates are valid and should be added to the existing object
            new_update_object = False
            delete_object_found = False

            #delete update if delete parameter set, iterate over each update for country code and delete matching, raise error if no match found
            if (delete):
                if (custom_update_object):
                    #if matching update found, delete from current object
                    if (all_updates_data[entry]['Change'].strip().lower() == custom_update_object['Change'].strip().lower() and
                        all_updates_data[entry]['Date Issued'].strip() == custom_update_object['Date Issued'].strip()):
                        del all_updates_data[entry]
                        delete_object_found = True
                        break
                else:
                    #if matching update found, delete from current object
                    if (all_updates_data[entry]['Change'].strip().lower() == change.strip().lower() and
                        all_updates_data[entry]['Date Issued'].strip() == date_issued.strip()):
                        del all_updates_data[entry]
                        delete_object_found = True
                        break
            else:
                if (custom_update_object):
                    #if existing update found in object raise error 
                    if (all_updates_data[entry]['Change'].strip().lower() == custom_update_object['Change'].strip().lower() and
                        all_updates_data[entry]['Date Issued'].strip() == custom_update_object['Date Issued'].strip()):
                        raise ValueError(f"Custom updates object should be unique and not already present an existing update: {custom_update_object}.")

                    #create object of new data to be added, reorder attributes
                    custom_updates_data = {key: custom_update_object[key] for key in ['Change', 'Description of Change', 'Date Issued', 'Source']}

                    #new object valid and can be added to updates object
                    new_update_object = True
                else:
                    #if existing update found in object raise error 
                    if (all_updates_data[entry]['Change'].strip().lower() == change.strip().lower() and
                        all_updates_data[entry]['Date Issued'].strip() == date_issued.strip()):
                        raise ValueError(f"Custom updates object should be unique and not already present an existing code: {change}.")

                    #create object of new data to be added from input parameters, reorder attributes
                    custom_updates_data = {"Change": change, "Date Issued": date_issued, "Description of Change": description_of_change, "Source": source}  

                    #new object valid and can be added to updates object
                    new_update_object = True

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

    def check_for_updates(self) -> None:
        """ 
        Pull the latest version of the object from the repo, comparing it with the current 
        version of the object installed in the software. If new updates/changes are found,
        they are listed and a message encouraging the user to download the latest version 
        is output.

        Parameters
        ==========
        None

        Returns
        =======
        None

        Raises
        ====== 
        RequestException:
            Error retrieving the updates JSON from main GitHub repo. 
        """
        #current updates object URL
        updates_url = "https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166_updates/iso3166-updates.json"

        #pull latest data object from repo
        try:
            response = requests.get(updates_url, timeout=15)
            response.raise_for_status()
            latest_iso3166_updates_json = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch the latest Updates data from repo: {e}.")
            return None

        #separate object that holds individual data objects that were found on the object in the repo that weren't in the software object
        new_iso3166_updates = {}

        #bool to track if any new updates found
        updates_found = False

        #iterate over all ISO 3166 updates data in latest object on repo, if update/row not found in current json in software version, append to new updated_json object 
        for alpha_code, entries in latest_iso3166_updates_json.items():
            current_entries = self.all.get(alpha_code, {})
            new_iso3166_updates[alpha_code] = []

            #iterate over individual updates entries, add to object if not in existing software updates object
            for update in entries:
                if update not in current_entries:
                    updates_found = True
                    new_iso3166_updates[alpha_code].append(update)

            #if current alpha-2 code has no new ISO 3166 updates associated with it, remove from temp object
            if not new_iso3166_updates[alpha_code]:
                new_iso3166_updates.pop(alpha_code, None)

        #print out any found updates 
        if (updates_found):

            print("New ISO 3166 Updates data found, please update the iso3166-updates software to incorporate these latest changes, you can do this by running:")
            print("pip install iso3166-updates --upgrade\n\n\n")

            #get total sum of new data updates for all countries in json
            total_updates = sum(len(v) for v in new_iso3166_updates.values())
            total_countries = len(new_iso3166_updates)
            
            print(f"{total_updates} update(s) found for {total_countries} country/countries, these are outlined below")
            print("============================================================================\n\n")
            
            #iterate over new data in json, append to updates object
            for code in list(new_iso3166_updates.keys()):
                
                #output current country name and code
                print(f"{iso3166.countries_by_alpha2[code].name} ({code})")
                
                #iterate over rows of new data and pretty print json
                for row in range(0, len(new_iso3166_updates[code])):
                    pprint.pprint(new_iso3166_updates[code][row], compact=True)
        else:
            print("No new updates found for iso3166-updates.")
        
        return
    
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
        :iso3166.countries_by_alpha3[alpha3_code].alpha2: str | None
            2 letter ISO 3166 alpha-2 country code. None returned
            if input cannot be converted.
        
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

        #uppercase alpha code
        alpha_code = alpha_code.upper()
        
        #use iso3166 package to find corresponding alpha-2 code from its numeric code, return error if numeric code not found
        if (alpha_code.isdigit()):
            if not (alpha_code in list(iso3166.countries_by_numeric.keys())):
                raise ValueError(f"Invalid ISO 3166-1 alpha numeric country code input: {alpha_code}.")
            return iso3166.countries_by_numeric[alpha_code].alpha2

        #return input alpha code if its valid, return error if alpha-2 code not found
        if len(alpha_code) == 2:
            if not (alpha_code in list(iso3166.countries_by_alpha2.keys())):
                raise ValueError(f"Invalid ISO 3166-1 alpha-2 country code input: {alpha_code}.")
            return alpha_code

        #use iso3166 package to find corresponding alpha-2 code from its alpha-3 code, return error if code not found
        if len(alpha_code) == 3:
            if not (alpha_code in list(iso3166.countries_by_alpha3.keys())):
                raise ValueError(f"Invalid ISO 3166-1 alpha-3 country code: {alpha_code}.")
            return iso3166.countries_by_alpha3[alpha_code].alpha2

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
            converted date in the YYYY-MM-DD format or None.
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
        return self.get(attr)

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