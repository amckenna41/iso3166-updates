from google.cloud import storage
import json 
import iso3166
import re
import datetime

def iso3166_updates(request):
    """
    Google Cloud Function for iso3166-updates API. This function can take
    country, alpha2 code and year as input parameters and return the relevant 
    ISO3166 updates for 1 or more input countries.

    Parameters
    ----------
    : request : (flask.Request)
        HTTP request object.
    
    Returns
    -------
    : iso_updates : json
        jsonified response of iso3166 updates for selected country/ISO code.
    """
    # Initialise a client
    storage_client = storage.Client()
    # Create a bucket object for our bucket
    bucket = storage_client.get_bucket("iso3166-updates")
    # Create a blob object from the filepath
    blob = bucket.blob("iso3166-updates.json")

    #pass in year param on its own, returns all updates_data object with year  ***
    #return "No listed updates for year" for empty alpha2 code object
    # https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates2?alpha2=ST&year=2020         

    #get input arguments as json
    request_json = request.get_json()
    
    #download iso3166-updates.json file from storage bucket 
    updates_data = json.loads(blob.download_as_string(client=None))

    #initialise vars
    iso_updates = {}
    alpha2_code = []
    year_range = False
    greater_than = False
    less_than = False
    year = []

    #parse alpha2 code 
    if request.args and 'alpha2' in request.args:
        alpha2_code = sorted([request.args.get('alpha2').upper()])
    elif request_json and 'alpha2' in request_json:
        alpha2_code = sorted([request_json['alpha2'].upper()])

    #parse year parameter
    if request.args and 'year' in request.args:
        year = [request.args.get('year').upper()]
    elif request_json and 'year' in request_json:
        year = [request_json['year'].upper()]

    #validate multiple alpha2 codes input, remove any invalid ones
    # if (alpha2_code != []):
    if (alpha2_code != []):
        if (',' in alpha2_code[0]):
            alpha2_code = alpha2_code[0].split(',')
            alpha2_code = [code.strip() for code in alpha2_code]
            for code in alpha2_code:
                #use regex to validate format of alpha2 codes
                if not (bool(re.match(r"^[A-Z]{2}$", code))) or (code not in list(iso3166.countries_by_alpha2.keys())):
                    alpha2_code.remove(code)
        else:
            #if single alpha2 code passed in, validate its correctness
            if not (bool(re.match(r"^[A-Z]{2}$", alpha2_code[0]))) or (alpha2_code[0] not in list(iso3166.countries_by_alpha2.keys())):
                alpha2_code.remove(alpha2_code[0])

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

    print("year here", year)
    print("year here type", type(year))

    #if no input parameters set then return all country update updates_data
    if (year == [] and alpha2_code == []):
        return updates_data
    
    print("alpha2_code", alpha2_code)
    print("multi_alpha2_code", alpha2_code)
    print("multi_alpha2_code type", type(alpha2_code))

    #get updates from updates_data object per country using alpha2 code
    if (alpha2_code == [] and year == []):
        iso_updates = {alpha2_code[0]: updates_data[alpha2_code[0]]}
    else:
        for code in alpha2_code:
            iso_updates[code] = updates_data[code]
    
    #temporary updates object
    temp_iso_updates = {}

    #**
    if (year != [] and alpha2_code == []):
        input_alpha2_codes  = list(iso3166.countries_by_alpha2.keys())
        input_data = updates_data
    elif (year != [] and alpha2_code != []): 
        input_alpha2_codes = alpha2_code
        input_data = iso_updates

    #use temp object to get updates data either for specific country/alpha2 code or for all
    # countries, dependant on input_alpha2_codes and input_data vars above
    for code in input_alpha2_codes:
        temp_iso_updates[code] = []
        for update in range(0, len(input_data[code])):
            #if year range true then get country updates within specified range
            if (year_range):
                temp_year = str(datetime.datetime.strptime(updates_data[code][update]["Date issued"].replace('\n', ''), '%Y-%m-%d').year)
                if (temp_year >= year[0] and temp_year <= year[1]):
                    temp_iso_updates[code].append(updates_data[code][update])
            else:
                #iterate through all years, if year of country updates matches then append to temp object
                for year_ in year:
                    temp_year = str(datetime.datetime.strptime(updates_data[code][update]["Date issued"].replace('\n', ''), '%Y-%m-%d').year)
                    #add to object if current year is >= user input year
                    if (greater_than):
                        if (temp_year >= year_):
                            temp_iso_updates[code].append(updates_data[code][update])
                    #add to object if current year is < user input year
                    elif (less_than):
                        if (temp_year < year_):
                            temp_iso_updates[code].append(updates_data[code][update])
                    #if no < or > symbol passed in then add to object if current year = user input year
                    elif not (greater_than and less_than):
                        if (temp_year == year_):
                            temp_iso_updates[code].append(updates_data[code][update])

    #set main updates dict to temp one
    iso_updates = temp_iso_updates

    return iso_updates
