from google.cloud import storage
import json 
import iso3166
import re
import datetime

def iso3166_updates_main(request):
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
    : iso3166_updates : json
        jsonified response of iso3166 updates for selected country/alpha2 ISO code.
    """
    # Initialise a client
    storage_client = storage.Client()
    # Create a bucket object for our bucket
    bucket = storage_client.get_bucket("iso3166-updates")
    # Create a blob object from the filepath
    blob = bucket.blob("iso3166-updates.json")       

    #get input arguments as json
    request_json = request.get_json()
    
    #download iso3166-updates.json file from storage bucket 
    updates_data = json.loads(blob.download_as_string(client=None))

    #initialise vars
    iso3166_updates = {}
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
            #only 2 years should be included in input parameter
            if (len(year) > 2):
                year = []
                year_range = False
        elif (',' in year[0]):
            #split years into multiple years, if multiple are input
            year = year[0].split(',')
        #parse array for using greater than symbol
        elif ('>' in year[0]):
            year = year[0].split('>')
            greater_than = True
            year.remove('')
            #after removing >, only 1 year should be left in year parameter
            if (len(year) > 1):
                year = []
                greater_than = False
        #parse array for using less than symbol
        elif ('<' in year[0]):
            year = year[0].split('<')
            less_than = True
            year.remove('')
            #after removing <, only 1 year should be left in year parameter
            if (len(year) > 1):
                year = []
                less_than = False

    for year_ in year:
        #skip to next iteration if < or > symbol
        if (year_ == '<' or year_ == '>'):
            continue
        #validate each year format using regex
        if not (bool(re.match(r"^1|^2[0-9][0-9][0-9]", year_))):
            # year = []
            year.remove(year_)
            year_range = False 
            break 

    #if no input parameters set then return all country update updates_data
    if (year == [] and alpha2_code == []):
        return updates_data

    #get updates from updates_data object per country using alpha2 code
    if (alpha2_code == [] and year == []):
        iso3166_updates = {alpha2_code[0]: updates_data[alpha2_code[0]]}
    else:
        for code in alpha2_code:
            iso3166_updates[code] = updates_data[code]
    
    #temporary updates object
    temp_iso3166_updates = {}

    #if no valid alpha2 codes input use all alpha2 codes from iso3166 and all updates data
    if (year != [] and alpha2_code == []):
        input_alpha2_codes  = list(iso3166.countries_by_alpha2.keys())
        input_data = updates_data
    #else set input alpha2 codes to inputted and use corresponding updates data
    else:
        input_alpha2_codes = alpha2_code
        input_data = iso3166_updates
    
    #correct column order
    reordered_columns = ['Date Issued', 'Edition/Newsletter', 'Description of change in newsletter', 'Code/Subdivision change']

    #use temp object to get updates data either for specific country/alpha2 code or for all
    # countries, dependant on input_alpha2_codes and input_data vars above
    if (year != []):
        for code in input_alpha2_codes:
            temp_iso3166_updates[code] = []
            for update in range(0, len(input_data[code])):
                
                #reorder dict columns
                input_data[code][update] = {col: input_data[code][update][col] for col in reordered_columns}
                #convert year in Date Issued column to string of year
                temp_year = str(datetime.datetime.strptime(input_data[code][update]["Date Issued"].replace('\n', ''), '%Y-%m-%d').year)

                #if year range true then get country updates within specified range inclusive
                if (year_range):
                    if (temp_year != "" and (temp_year >= year[0] and temp_year <= year[1])):
                        temp_iso3166_updates[code].append(input_data[code][update])
                
                #if greater than true then get country updates greater than specified year inclusive
                elif (greater_than):
                    if (temp_year != "" and (temp_year >= year[0])):
                        temp_iso3166_updates[code].append(input_data[code][update])    

                #if less than true then get country updates less than specified year 
                elif (less_than):
                    if (temp_year != "" and (temp_year < year[0])):
                        temp_iso3166_updates[code].append(input_data[code][update]) 

                #if greater than & less than not true then get country updates equal to specified year
                elif not (greater_than and less_than):
                    for year_ in year:
                        if (temp_year != "" and (temp_year == year_)):
                            temp_iso3166_updates[code].append(input_data[code][update])
            
            #if current alpha2 has no rows for selected year/year range, remove from temp object
            if (temp_iso3166_updates[code] == []):
                temp_iso3166_updates.pop(code, None)

    #if no year parameter input then set temp data to original data
    else:
        temp_iso3166_updates = input_data
    
    #set main updates dict to temp one
    iso3166_updates = temp_iso3166_updates

    return iso3166_updates