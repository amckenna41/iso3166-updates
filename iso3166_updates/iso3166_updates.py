import os
import sys
import json
import re
from datetime import datetime
from dateutil import relativedelta
import iso3166
import platform

class ISO3166_Updates():
    """
    This class is used to access all the ISO-3166 updates/changes data from its respective json
    created from the data sources used in the get_all_iso3166_updates.py script. All of the 
    keys and objects in the JSON are accessible via dot notation using the Map class. Each
    country has the attributes: Code/Subdivision Change, Description of Change, Date Issued and 
    Edition/Newsletter.
    
    "Date Issued" is the date at which the change was published by the ISO, the "Edition/Newsletter"
    column is the name and or edition of newsletter that the ISO 3166 change/update was communicated 
    in, "Code/Subdivision Change" column is the overall summary of change/update made and 
    "Description of Change" is a more in-depth info about the change/update that was made.

    Currently there are 249 country's listed in the updates json with updates dating from 2000 up
    to the present year, with ~500 individual published updates.

    Parameters
    ==========
    :country_code: str (default="")
        ISO 3166-1 alpha-2, alpha-3 or numeric country code to get subdivision data for. A list
        of country codes can also be input. If the alpha-3 or numeric codes are input, they are
        converted into their alpha-2 counterparts.

    Methods
    =======
    year(input_year):
        get all listed updates/changes in the updates json object for an input year, set of years,
        year range or greater than/less than year.
    months(input_month):
        get all listed updates/changes in the updates json that have been published within the past
        number of months or within a specified month range.    
    __getitem__(alpha_code):
        get all listed updates/changes in the updates json object for an input country/countries,
        by making the instance object subscriptable and updates accessible via their alpha-2, 
        alpha-3 or numeric country codes.
    convert_to_alpha2(alpha_code):
        convert the inputted ISO 3166-1 alpha-3 or numeric country codes into their 2 letter 
        alpha-2 counterpart.

    Usage
    =====
    from iso3166_updates import *

    #create instance of class
    iso = ISO3166_Updates()

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

    #get all listed country updates/changes data with years >2020, for France
    iso.year(">2020").FR

    #get all listed country updates/changes data published over the previous 6 months
    iso.months("6")

    #get all listed country updates/changes data published over the previous 24-36 months
    iso.months("24-36")
    """
    def __init__(self, country_code: str="") -> None:
        
        self.iso3166_updates_json_filename = "iso3166-updates.json"
        self.country_code = country_code
        
        #get module path to access the json object
        self.iso3166_updates_module_path = os.path.dirname(os.path.abspath(sys.modules[self.__module__].__file__))
        
        #raise error if iso3166-updates json doesn't exist in folder
        if not (os.path.isfile(os.path.join(self.iso3166_updates_module_path, self.iso3166_updates_json_filename))):
            raise OSError(f"Issue finding iso3166-updates.json in dir: {os.path.join(self.iso3166_updates_module_path, self.iso3166_updates_json_filename)}.")

        #importing all updates data from JSON, open iso3166-updates json file and load it into class variable, loading in a JSON is different in Windows & Unix/Linux systems
        if (platform.system() != "Windows"):
            with open(os.path.join(self.iso3166_updates_module_path, self.iso3166_updates_json_filename)) as iso3166_updates_json:
                self.all = json.load(iso3166_updates_json)
        else:
            with open(os.path.join(self.iso3166_updates_module_path, self.iso3166_updates_json_filename), encoding="utf-8") as iso3166_updates_json:
                self.all = json.loads(iso3166_updates_json.read())

        #make all updates object subscriptable using Map class
        # self.all = Map(self.all)

        #if input country code param set, iterate over data object and get updates data for specified input/inputs
        if (self.country_code != ""):
            temp_updates_data = {}
            self.country_code = self.country_code.upper().replace(" ", "").split(',')
            for code in range(0, len(self.country_code)):
                #if 3 letter alpha-3 or numeric codes input then convert to corresponding alpha-2, if invalid code then raise error
                if (len(self.country_code[code]) == 3):
                    temp_alpha_code = self.convert_to_alpha2(self.country_code[code])
                    if (temp_alpha_code is None and self.country_code[code].isdigit()):
                        raise ValueError(f"Invalid ISO 3166-1 numeric country code input, cannot convert into corresponding alpha-2 code: {self.country_code[code]}.")
                    if (temp_alpha_code is None):
                        raise ValueError(f"Invalid ISO 3166-1 alpha-3 country code input, cannot convert into corresponding alpha-2 code: {self.country_code[code]}.")
                    self.country_code[code] = temp_alpha_code

                #raise error if invalid alpha-2 code input
                if not (self.country_code[code] in sorted(list(iso3166.countries_by_alpha2.keys()))) or not (self.country_code[code] in list(self.all.keys())):
                    raise ValueError(f"Invalid alpha-2 country code input: {self.country_code[code]}.")
                
                #create temporary updates data object
                temp_updates_data[self.country_code[code]] = {}
                temp_updates_data[self.country_code[code]] = self.all[self.country_code[code]]
            
            #delete existing 'all' class attribute that currently has all updates data for all countries, which aren't needed if input country is specified
            del self.all

            #set 'all' class attribute to the updates data from input country/countries
            self.all = temp_updates_data
        
        #get list of all countries by their 2 letter alpha-2 code
        # self.alpha2 = sorted(list(iso3166.countries_by_alpha2.keys()))

    def __getitem__(self, alpha_code: str) -> dict:
        """
        Get all listed updates/changes in the updates json object for an input country/countries,
        using the ISO 3166-1 alpha-2, alpha-3 or numeric country codes. This function uses the Map 
        class to make the instance object of the class subscriptable. It can accept 1 or more alpha 
        codes for countries and return the data for each. If the alpha-3 or numeric codes are input 
        its converted into its alpha-2 counterpart.
        
        Parameters
        ==========
        :alpha_code: str
            one or more ISO 3166-1 alpha-2, alpha-3 or numeric country codes for sought country/
            territory updates e.g. AD, DE, EGT, 184. The alpha-3 or numeric codes will be 
            converted into their alpha-3 counterparts. 

        Returns
        =======
        :country_updates_dict: dict
            dict object of country updates info for inputted code/codes.

        Usage
        -----
        from iso3166_updates import *
        
        #create instance of class
        iso = ISO3166_Updates()

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
        """
        #raise type error if input isn't a string
        if not (isinstance(alpha_code, str)):
            raise TypeError('Input parameter {} is not of correct datatype string, got {}.'.format(alpha_code, type(alpha_code)))       
    
        #stripping input of whitespace, uppercasing, separating multiple alpha codes, if applicable and sort list
        alpha_code = alpha_code.strip().upper()
        alpha_code = sorted(alpha_code.replace(' ', '').split(','))

        #object to store country data, it is a dict if more than one country or list if only one country
        country_updates_dict = {}

        #iterate over all input alpha codes, appending all updates to country object, pass through Map class to access via dot notation
        for code in range(0, len(alpha_code)):

            #if 3 letter alpha-3 or numeric codes input then convert to corresponding alpha-2, else raise error
            if (len(alpha_code[code]) == 3):
                temp_alpha_code = self.convert_to_alpha2(alpha_code[code])
                if (temp_alpha_code is None and alpha_code[code].isdigit()):
                    raise ValueError(f"Invalid ISO 3166-1 numeric country code input, cannot convert into corresponding alpha-2 code: {alpha_code[code]}.")
                if (temp_alpha_code is None):
                    raise ValueError(f"Invalid ISO 3166-1 alpha-3 country code input, cannot convert into corresponding alpha-2 code: {alpha_code[code]}.")
                alpha_code[code] = temp_alpha_code
               
            #raise error if invalid alpha-2 code input or country data not imported on object instantiation 
            if not (alpha_code[code] in sorted(list(iso3166.countries_by_alpha2.keys()))):
                raise ValueError(f"Invalid alpha-2 code input: {alpha_code[code]}.")
            if not (alpha_code[code] in list(self.all.keys())):
                raise ValueError(f"Valid alpha-2 code input {alpha_code[code]}, but country data not available as 'country_code' parameter was input on class instantiation,"
                                " try creating another instance of the class with no initial input parameter value, e.g iso = ISO3166_Updates().")

            #add each country update to country object
            country_updates_dict[alpha_code[code]] = []
            for update in range(0, len(self.all[alpha_code[code]])):
                country_updates_dict[alpha_code[code]].append(Map(self.all[alpha_code[code]][update]))
                #iterate over nested dicts, convert into instances of Map class so they can be accessed via dot notation
                for key in country_updates_dict[alpha_code[code]][update].keys():
                    if (isinstance(country_updates_dict[alpha_code[code]][update][key], dict)):
                        country_updates_dict[alpha_code[code]][update][key] = Map(country_updates_dict[alpha_code[code]][update][key])
            
        #keys in updates dict needs sorted in the case of alpha-3 and or numeric codes being input
        country_updates_dict = dict(sorted(country_updates_dict.items()))

        #convert into instance of Map class so keys can be accessed via dot notation
        country_updates_dict = Map(country_updates_dict)

        return country_updates_dict 
    
    def year(self, input_year: str) -> dict:
        """
        Get all listed updates/changes in the updates json object for an input year, set of years,
        year range or greater than/less than year. The json object will be iterated over and any
        matching updates from the "Date Issued" column will be appended to the output dict.

        Parameters
        ==========
        :input_year: str
            single or comma separated list of multiple years. Can also accept a year range or a year 
            to get updates greater than or less than e.g "2015", "2009,2019", ">2022", "<2004", "2005-2012".

        Returns
        =======
        :country_output_dict: dict
            output dictionary of sought ISO 3166 updates for input year/years.
        """
        #if single str of 1 or more years input then convert to array, remove whitespace, separate using comma
        if (isinstance(input_year, str)):
            input_year = input_year.replace(' ', '').split(',')
        else:
            #raise error if invalid data type for year parameter
            raise TypeError(f"Invalid data type for year parameter, expected str, got {type(input_year)}.")
        
        country_output_dict = {}

        year_range = False
        greater_than = False
        less_than = False
        
        #a '-' separating 2 years implies a year range of sought country updates
        #a ',' separating 2 years implies a list of years
        #a '>' before year means get all country updates greater than or equal to specified year
        #a '<' before year means get all country updates less than specified year
        if (input_year != []):
            if ('-' in input_year[0]):
                year_range = True
                input_year = input_year[0].split('-')
                #if year range years are wrong way around then swap them
                if (input_year[0] > input_year[1]):
                    input_year[0], input_year[1] = input_year[1], input_year[0]
                #only 2 years should be included in input parameter
                if (len(input_year) > 2):
                    input_year = []
                    year_range = False
            #parse array for using greater than symbol
            elif ('>' in input_year[0]):
                input_year = list(input_year[0].rpartition(">")[1:])
                greater_than = True
                input_year.remove('>')
                if (len(input_year) > 2):
                    input_year = []
                    greater_than = False
            #parse array for using less than symbol
            elif ('<' in input_year[0]):
                input_year = list(input_year[0].rpartition("<")[1:])
                less_than = True
                input_year.remove('<')
                if (len(input_year) > 2):
                    input_year = []
                    less_than = False
            elif (',' in input_year[0]):
                #split years into multiple years, if multiple are input
                input_year = input_year[0].split(',')
        #validate each year's format using regex
        for year_ in input_year:
            #skip to next iteration if < or > symbol
            if (year_ == '<' or year_ == '>' or year_ == '-'):
                continue
            if not (bool(re.match(r"^1[0-9][0-9][0-9]$|^2[0-9][0-9][0-9]$", year_))):
                raise ValueError(f"Invalid year input: {year_}.")

        #temp object to not override original updates object
        country_output_dict = {}

        #drop rows of dict where Date Issued column isn't same as year parameter, if greater_than, 
        #less_than or year_range bools set then drop any objects of dict that don't meet condition
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
                        
                    #drop all rows in dict that are less than input year
                    if (greater_than):
                        if not (current_updates_year < input_year[0]):
                            country_output_dict[code].append(self.all[code][update])

                    #drop all rows in dict that are greater than or equal to input year
                    elif (less_than):
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

    def months(self, input_month: str) -> dict:
        """
        Get all listed updates/changes in the updates json object that have a published date
        over the past number of months, inclusive, specified by the input parameter, e.g. 
        all updates from the past 12, 24 or 36 months. You can also get those published within 
        a month range e.g all updates from the past 6-12 months. The json object will be 
        iterated over and any matching updates from the "Date Issued" column will be appended 
        to the output dict.

        Parameters
        ==========
        :input_month: str
            single month or month range from present day e.g "12", "24", "36-60".

        Returns
        =======
        :country_output_dict: dict
            output dictionary of sought ISO 3166 updates for input months/month range.
        """
        # #if no input month parameter specified then return error message
        # if (input_month == ""):
        #     raise ValueError("The month input parameter cannot be empty.")

        #add int functionality

        #return error if invalid month value type input, skip if month range input
        if not ('-' in input_month):
            if not (str(input_month).isdigit()):
                raise ValueError(f"Invalid month input: {''.join(input_month)}.")

        #get current datetime object
        current_datetime = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d")

        #object to store country updates 
        country_output_dict = {}

        #get all alpha-2 codes from iso3166 and all updates data before filtering by month
        input_alpha_codes = list(iso3166.countries_by_alpha2.keys())

        #remove XK (Kosovo) from list, if applicable
        if ("XK" in input_alpha_codes):
            input_alpha_codes.remove("XK")

        #filter out updates that are not within specified month range
        for code in input_alpha_codes:
            country_output_dict[code] = [] 
            for update in range(0, len(self.all[code])):

                #convert year in Date Issued column to date object, remove "corrected" date if applicable
                if ("corrected" in self.all[code][update]["Date Issued"]):
                    row_date = datetime.strptime(re.sub("[(].*[)]", "", self.all[code][update]["Date Issued"]).replace(' ', "").
                                                        replace(".", '').replace('\n', ''), '%Y-%m-%d')
                else:
                    row_date = datetime.strptime(self.all[code][update]["Date Issued"].replace('\n', ''), '%Y-%m-%d')
                
                #calculate difference in dates
                date_diff = relativedelta.relativedelta(current_datetime, row_date)

                #calculate months difference
                diff_months = date_diff.months + (date_diff.years * 12)

                #parse parameter to get range of months to get updates from
                if ('-' in input_month):
                    start_month, end_month = int(input_month.split('-')[0]), int(input_month.split('-')[1])
                    #if months in month range input are wrong way around then swap them
                    if (start_month > end_month):
                        start_month, end_month = end_month, start_month
                    #if current updates row is >= start month input param and <= end month then add to output object
                    if ((diff_months >= start_month) and (diff_months <= end_month)):
                        country_output_dict[code].append(self.all[code][update])
                else:
                    #if current updates row is <= month input param then add to output object
                    if (diff_months <= int(input_month)):
                        country_output_dict[code].append(self.all[code][update])

            #if current alpha-2 has no rows for selected month range, remove from output object
            if (country_output_dict[code] == []):
                country_output_dict.pop(code, None)

        #make updates object subscriptable using Map class
        country_output_dict = Map(country_output_dict)

        return country_output_dict
        
    def convert_to_alpha2(self, alpha_code: str) -> str:
        """ 
        Auxillary function that converts an ISO 3166 country's 3 letter alpha-3 
        or numeric code into its 2 letter alpha-2 counterpart. 

        Parameters 
        ==========
        :alpha_code: str
            3 letter ISO 3166-1 alpha-3 or numeric country code.
        
        Returns
        =======
        :iso3166.countries_by_alpha3[alpha3_code].alpha2: str
            2 letter ISO 3166 alpha-2 country code. 
        """
        if (alpha_code.isdigit()):
            #return error if numeric code not found
            if not (alpha_code in list(iso3166.countries_by_numeric.keys())):
                return None
            else:
                #use iso3166 package to find corresponding alpha-2 code from its numeric code
                return iso3166.countries_by_numeric[alpha_code].alpha2
    
        #return error if 3 letter alpha-3 code not found
        if not (alpha_code in list(iso3166.countries_by_alpha3.keys())):
            return None
        else:
            #use iso3166 package to find corresponding alpha-2 code from its alpha-3 code
            return iso3166.countries_by_alpha3[alpha_code].alpha2
    
    def __str__(self) -> str:
        return "Instance of ISO3166 Updates class."

    def __sizeof__(self) -> float:
        """ Return size of instance of ISO 3166 Updates class. """
        return self.__sizeof__()

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