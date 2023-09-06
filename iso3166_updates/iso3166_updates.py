import os
import sys
import json
import re
from datetime import datetime
import iso3166

class ISO3166_Updates():
    """
    This class is used to access all the ISO-3166 updates/changes data from it's respecrtive json
    created from the two data sources used in the get_all_iso3166_updates.py script. All of the 
    keys and objects in the JSON are accessible via dot notation using the Map class. Each
    country has the attributes: Date Issued, Edition/Newsletter, Code/Subdivision Change and
    Description of Change in Newsletter. Currently there are 250 country's listed in the 
    updates json with X of these having any changes/updates data.
    
    Parameters
    ----------
    None

    Usage
    -----
    import iso3166_updates as iso

    #get ALL listed changes/updates for ALL countries 
    iso.updates.all

    #get ALL listed country updates/changes data for Ireland, Colombia, Denmark and Finland
    iso.updates['IE']
    iso.updates['CO']
    iso.updates['DK']
    iso.updates['FI']

    #get ALL listed country updates/changes data for France and Germany
    iso.updates["FR,DE"]

    #get ALL listed country updates/changes data for Fiji, Guyana, Haiti and Hungary
    iso.updates["FJ,GY,HI,HU"]

    #get ALL listed country updates/changes data for year 2016
    iso.updates.year("2016")

    #get ALL listed country updates/changes data for years 2005 - 2010
    iso.updates.year("2005-2010")

    #get ALL listed country updates/changes data with year <2009
    iso.updates.year("<2009")

    #get ALL listed country updates/changes data with years >2020
    iso.updates.year(">2020")
    """
    def __init__(self):
        
        self.iso3166_updates_json_filename = "iso3166-updates.json"
        
        #get module path
        self.iso3166_updates_module_path = os.path.dirname(os.path.abspath(sys.modules[self.__module__].__file__))
        
        #raise error if iso3166-upates json doesnt exist in folder
        if not (os.path.isfile(os.path.join(self.iso3166_updates_module_path, self.iso3166_updates_json_filename))):
            raise OSError("Issue finding iso3166-updates.json in dir: {}".format(
                os.path.join(self.iso3166_updates_module_path, self.iso3166_updates_json_filename)))

        #open iso3166-updates json file and load it into class variable
        with open(os.path.join(self.iso3166_updates_module_path, self.iso3166_updates_json_filename)) as iso3166_updates_json:
            self.all = json.load(iso3166_updates_json)

        #make all updates object subscriptable using Map class
        self.all = Map(self.all)

        #get list of all countries by 2 letter alpha3 code
        self.alpha2 = sorted(list(iso3166.countries_by_alpha2.keys()))
        
        #get list of all countries by 3 letter alpha3 code
        self.alpha3 = sorted(list(iso3166.countries_by_alpha3.keys()))
    
    def year(self, input_year):
        """
        Get all listed updates/changes in the updates json object for an input year, set of years,
        year range or greater than less than year. The json object will be iterated over and
        any matching updates from the "Date Issued" column will be appended to the output dict.

        Parameters
        ----------
        :input_year: str/list
            single or list of multiple years. Can also accept a year range or a year to get updates
            greater than or less than. 

        Returns
        -------
        :country_output_dict : dict
            output dictionary of sought ISO 3166 updates for input year/years.
        """
        #if single str of 1 or more years input then convert to array, remove whitespace, seperate using comma
        if (isinstance(input_year, str)):
            input_year = input_year.replace(' ', '').split(',')
        else:
            #raise error if invalid data type for year parameter
            raise TypeError("Invalid data type for year parameter, expected str, got {}.".format(type(input_year)))
        
        country_output_dict = {}

        year_range = False
        greater_than = False
        less_than = False
        
        #a '-' seperating 2 years implies a year range of sought country updates, validate format of years in range
        #a ',' seperating 2 years implies a list of years
        #a '>' before year means get all country updates greater than or equal to specified year
        #a '<' before year means get all country updates less than specified year
        if (input_year != []):
            if ('-' in input_year[0]):
                year_range = True
                input_year = input_year[0].split('-')
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
                raise ValueError("Invalid year input: {}.".format(year_))

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

        #make updates object subscritable using Map class
        country_output_dict = Map(country_output_dict)

        return country_output_dict

    def __getitem__(self, alpha2_code):
        """
        Get all listed updates/changes in the updates json object for an input country/countries,
        using the 2 letter ISO 3166-1 code. This function uses the Map class to make the clas
        subscriptable. It can accept 1 or more 2 letter alpha-2 codes for countries. Also the
        3 letter alpha-3 code for a country can be input which will be converted into its alpha-2 
        counterpart.
        
        Parameters
        ----------
        :alpha2_code : str
            one or more 2 letter alpha-2 code for sought country/territory e.g (AD, EG, DE). Can 
            also accept 3 letter alpha-3 code e.g (AND, EGT, DEU), this will be converted into 
            its alpha-2 counterpart.

        Returns
        -------
        :country_updates_dict: dict
            dict object of country updates info for inputted code/codes.

        Usage
        -----
        import iso3166_updates as iso

        #get country ISO 3166 updates info for Ethiopia
        iso.updates["ET"] 
        iso.updates["ETH"] 
        iso.updates["et"] 
 
        #get country ISO 3166 updates info for Gabon
        iso.updates["GA"] 
        iso.updates["GAB"] 
        iso.updates["ga"] 

        #get country ISO 3166 updates info for Rwanda, Tuvalu, Ukraine and Uruguay
        iso.updates["RW, TV, UA, UY"]
        iso.updates["RWA, TUV, UKR, URY"]
        iso.updates["rw, tv, ua, uy"]
        """
        #raise type error if input isn't a string
        if not (isinstance(alpha2_code, str)):
            raise TypeError('Input parameter {} is not of correct datatype string, got {}.' \
                .format(alpha2_code, type(alpha2_code)))       
        
        #stripping input of whitespace, uppercasing, seperating multiple alpha-2 codes, if applicable and sort list
        alpha2_code = alpha2_code.strip().upper()
        alpha2_code = sorted(alpha2_code.replace(' ', '').split(','))

        #object to store country data, dict if more than one country, list if only one country
        country_updates_dict = {}

        #iterate over all input alpha-2 codes, appending all updates to country object, pass through Map class to access via dot notation
        for code in alpha2_code:

            #validate 2 letter alpha-2 code exists in ISO 3166-1, raise error if not found            
            if (len(code) == 2):
                if not (code in self.alpha2):      
                    raise ValueError("Alpha-2 Code {} not found in list of ISO 3166-1 codes.".format(code))            

            #if 3 letter code input, check it exists in ISO 3166-1, then convert into its 2 letter alpha-2 code, raise error if not found            
            if (len(code) == 3):
                if (code in self.alpha3):      
                    code = iso3166.countries_by_alpha3[code].alpha2
                else:
                    raise ValueError("Alpha-3 Code {} not found in list of ISO 3166-1 codes.".format(code))        

            #raise error if alpha-2 code not found in list of available codes
            if not (code in self.alpha2):
                raise ValueError("Alpha-2 Code {} not found in list of ISO 3166-1 codes.".format(code))        

            #if only one alpha-2 code input, convert country object to list and append all country update to it
            if (len(alpha2_code) == 1):
                country_updates_dict = []
                for update in range(0, len(self.all[code])):
                    country_updates_dict.append(Map(self.all[code][update]))
                    #iterate over nested dicts, convert into instances of Map class so they can be accessed via dot notation
                    for key in country_updates_dict[update].keys():
                        if (isinstance(country_updates_dict[update][key], dict)):
                            country_updates_dict[update][key] = Map(country_updates_dict[update][key])
            #if multiple alpha-2 codes input, add update dict to country object
            else:
                country_updates_dict[code] = []
                for update in range(0, len(self.all[code])):
                    country_updates_dict[code].append(Map(self.all[code][update]))
                    #iterate over nested dicts, convert into instances of Map class so they can be accessed via dot notation
                    for key in country_updates_dict[code][update].keys():
                        if (isinstance(country_updates_dict[code][update][key], dict)):
                            country_updates_dict[code][update][key] = Map(country_updates_dict[code][update][key])
                
                #convert into instance of Map class so keys can be accessed via dot notation
                country_updates_dict = Map(country_updates_dict)

        return country_updates_dict 
    
    def __str__(self):
        return "Instance of ISO Updates class."

    def __sizeof__(self):
        """ Return size of instance of ISO 3166 Updates class. """
        return self.__sizeof__()

class Map(dict):
    """
    Class that accepts a dict and allows you to use dot notation to access
    members of the dictionary. 

    Parameters
    ----------
    :dict
        input dictionary to convert into instance of map class so the keys/vals
        can be accessed via dot notation.

    Usage
    -----
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
    ----------
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

#create instance of ISO3166_Updates class
updates = ISO3166_Updates()