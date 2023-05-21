from flask import jsonify
from google.cloud import storage, exceptions
from google.api_core.exceptions import NotFound
import json 
import iso3166
import re
import unicodedata
import os
from datetime import datetime
from dateutil import relativedelta

def iso3166_updates_main(request):
    """
    Google Cloud Function for iso3166-updates API. This function can take
    country, alpha2 code and year as input parameters and return the relevant 
    ISO3166 updates for 1 or more input countries.
    Parameters
    ----------
    :request : (flask.Request)
       HTTP request object.
    
    Returns
    -------
    :iso3166_updates : json
      jsonified response of iso3166 updates for selected country/alpha2 ISO code.
    """
    #json object storing the error message and status code 
    error_message = {}
    error_message["status"] = 400

    #initialise storage client
    storage_client = storage.Client()
    try:
        #create a bucket object for the bucket
        bucket = storage_client.get_bucket(os.environ["BUCKET_NAME"])
    except NotFound:
        error_message["message"] = f"Error retrieving updates data json."
        return jsonify(error_message), 400
    #create a blob object from the filepath
    blob = bucket.blob(os.environ["BLOB_NAME"])      
    
    #return error if object not found in bucket
    if not (blob.exists()):
        error_message["message"] = f"Error retrieving updates data json."
        return jsonify(error_message), 400

    #download iso3166-updates.json file from storage bucket 
    updates_data = json.loads(blob.download_as_string(client=None))
 
    #get current datetime object
    current_datetime = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d")

    #initialise vars
    iso3166_updates = {}
    alpha2_code = []
    year_range = False
    greater_than = False
    less_than = False
    year = []
    months = []

    #parse alpha2 code parameter
    if (request.args and 'alpha2' in request.args):
        alpha2_code = sorted([request.args.get('alpha2').upper()])

    #parse year parameter
    if (request.args and 'year' in request.args):
        year = [request.args.get('year')]

    #parse months parameter, return error message if invalid input
    if (request.args and 'months' in request.args):
        try:
            months = int(request.args.get('months'))
        except:
            error_message["message"] = f"Invalid month input: {''.join(request.args.get('months'))}."
            return jsonify(error_message), 400
            
    #if no input parameters set then return all country update updates_data
    if (year == [] and alpha2_code == [] and months == []):
        return updates_data

    #iterate over all years, convert > or < symbol from unicode to string ("%3E" and "%3C", respectively)
    for y in range(0, len(year)):
        if ("%3E" in year[y]):
            year[y] = ">" + year[y][3:]
        elif ("%3C" in year[y]):
            year[y] = "<" + year[y][3:]

    def convert_to_alpha2(alpha3_code):
        """ 
        Convert an ISO3166 country's 3 letter alpha-3 code into its 2 letter
        alpha-2 counterpart. 

        Parameters 
        ----------
        :alpha3_code: str
            3 letter ISO3166 country code.
        
        Returns
        -------
        :iso3166.countries_by_alpha3[alpha3_code].alpha2: str
            2 letter ISO3166 country code. 
        """
        #return error if 3 letter alpha-3 code not found
        if not (alpha3_code in list(iso3166.countries_by_alpha3.keys())):
            return None
        else:
            #use iso3166 package to find corresponding alpha-2 code from its alpha-3
            return iso3166.countries_by_alpha3[alpha3_code].alpha2

    #validate multiple alpha-2 codes input, remove any invalid ones
    if (alpha2_code != []):
        if (',' in alpha2_code[0]):
            alpha2_code = alpha2_code[0].split(',')
            alpha2_code = [code.strip() for code in alpha2_code]
            for code in range(0, len(alpha2_code)):
                #api can accept 3 letter alpha-3 code for country, this has to be converted into its alpha-2 counterpart
                if (len(alpha2_code[code]) == 3):
                    temp_code = convert_to_alpha2(alpha2_code[code])
                    #return error message if invalid alpha-3 code input
                    if (temp_code is None):
                        error_message["message"] = f"Invalid 3 letter alpha-3 code input: {''.join(alpha2_code[code])}."
                        return jsonify(error_message), 400
                    alpha2_code[code] = temp_code
                #use regex to validate format of alpha-2 codes
                if not (bool(re.match(r"^[A-Z]{2}$", alpha2_code[code]))) or (alpha2_code[code] not in list(iso3166.countries_by_alpha2.keys())):
                    alpha2_code.remove(alpha2_code[code])
        else:
            #api can accept 3 letter alpha-3 code for country, this has to be converted into its alpha-2 counterpart
            if (len(alpha2_code[0]) == 3):
                temp_code = convert_to_alpha2(alpha2_code[0])
                #return error message if invalid alpha-3 code input
                if (temp_code is None):
                    error_message["message"] = f"Invalid 3 letter alpha-3 code input: {''.join(alpha2_code[0])}."
                    return jsonify(error_message), 400
                alpha2_code[0] = temp_code
            #if single alpha-2 code passed in, validate its correctness
            if not (bool(re.match(r"^[A-Z]{2}$", alpha2_code[0]))) or \
                (alpha2_code[0] not in list(iso3166.countries_by_alpha2.keys()) and \
                alpha2_code[0] not in list(iso3166.countries_by_alpha3.keys())):
                error_message["message"] = f"Invalid 2 letter alpha-2 code input: {''.join(alpha2_code)}."
                return jsonify(error_message), 400

    #a '-' seperating 2 years implies a year range of sought country updates, validate format of years in range
    if (year != [] and months == []):
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
        #validate each year format using regex, raise error if invalid year input
        if not (bool(re.match(r"^1[0-9][0-9][0-9]$|^2[0-9][0-9][0-9]$", year_))):
            error_message["message"] = f"Invalid year input: {''.join(year)}."
            return jsonify(error_message), 400

    #get updates from updates_data object per country using alpha2 code
    if (alpha2_code == [] and year == [] and months == []):
        iso3166_updates = {alpha2_code[0]: updates_data[alpha2_code[0]]}
    else:
        for code in alpha2_code:
            iso3166_updates[code] = updates_data[code]
    
    #temporary updates object
    temp_iso3166_updates = {}

    #if no valid alpha2 codes input use all alpha2 codes from iso3166 and all updates data
    if ((year != [] and alpha2_code == [] and months == []) or \
        ((year == [] or year != []) and alpha2_code == [] and months != [])): #**
        input_alpha2_codes  = list(iso3166.countries_by_alpha2.keys())
        input_data = updates_data
    #else set input alpha2 codes to inputted and use corresponding updates data
    else:
        input_alpha2_codes = alpha2_code
        input_data = iso3166_updates
    
    #use temp object to get updates data either for specific country/alpha2 code or for all
    #countries, dependant on input_alpha2_codes and input_data vars above
    if (year != [] and months == []):
        for code in input_alpha2_codes:
            temp_iso3166_updates[code] = []
            for update in range(0, len(input_data[code])):

                #convert year in Date Issued column to string of year
                temp_year = str(datetime.strptime(input_data[code][update]["Date Issued"].replace('\n', ''), '%Y-%m-%d').year)

                #if year range true then get country updates within specified range inclusive
                if (year_range):
                    if (temp_year != "" and (temp_year >= year[0] and temp_year <= year[1])):
                        temp_iso3166_updates[code].append(input_data[code][update])
                
                #if greater than true then get country updates greater than specified year, inclusive
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

    #if months parameter input then get updates within this months range
    elif (months != []):
        #return error if invalid month value input
        if not (str(months).isdigit()):
            error_message["message"] = f"Invalid month input: {''.join(months)}."
            return jsonify(error_message), 400
        for code in input_alpha2_codes:
            temp_iso3166_updates[code] = [] 
            for update in range(0, len(input_data[code])):
                
                #convert date in Date Issued column to date object
                row_date = (datetime.strptime(input_data[code][update]["Date Issued"], "%Y-%m-%d"))
                
                #calculate difference in dates
                date_diff = relativedelta.relativedelta(current_datetime, row_date)

                #calculate months difference
                diff_months = date_diff.months + (date_diff.years * 12)

                #if current updates row is <= month input param then add to temp object
                if (diff_months <= months):
                    temp_iso3166_updates[code].append(input_data[code][update])
   
            #if current alpha2 has no rows for selected month range, remove from temp object
            if (temp_iso3166_updates[code] == []):
                temp_iso3166_updates.pop(code, None)
    else:
        temp_iso3166_updates = input_data #return updates data when Years and Month params are empty
    
    #set main updates dict to temp one
    iso3166_updates = temp_iso3166_updates

    return iso3166_updates