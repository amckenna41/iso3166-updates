import iso3166_updates
import iso3166
import os
import json
import flag
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from google.cloud import storage

def check_iso3166_updates_main(request):
    """
    Google Cloud Function that checks for any updates within specified date range
    for the iso3166-updates API. It uses the accompanying iso3166-updates Python
    software package to web scrape all country's ISO3166-2 wiki's checking for 
    any updates in a date range. 

    If any updates are found then a GitHub Issue is automatically created in the 
    iso3166-2 repository that itself stores all the latest info and data relating 
    to the ISO3166-2 standard. Additionally, if changes are found then the 
    iso3166-updates.json file in the GCP Storage bucket is updated which is the 
    data source for the iso3166-updates Python package and accompanying API.

    Parameters
    ----------
    :request : (flask.Request)
       HTTP request object.
    
    Returns
    -------
    :current_iso3166_updates : json
       json containing any iso3166 updates for selected country/alpha2 ISO code
       within specified date range.
    """
    #default month cutoff to check for updates
    months = 6

    #get list of any input parameters to function
    request_json = request.get_json()

    #parse months var from input params, if applicable
    if request.args and 'months' in request.args:
        if (not(request.args.get('months') is None) or (request.args.get('months') != "")):
            months = request.args.get('months')
    elif request_json and 'months' in request_json:
        if (not(request.args.get('months') is None) or (request.args.get('months') != "")):
            months = request.args.get('months')

    #get current date and time on function execution
    current_datetime = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d")

    #object containing current iso3166-2 updates according to month range
    current_iso3166_updates = {}
    
    #get list of all country's 2 letter alpha2 codes
    alpha2_codes = sorted(list(iso3166.countries_by_alpha2.keys()))

    #sort codes in alphabetical order and uppercase
    alpha2_codes.sort()
    alpha2_codes = [code.upper() for code in alpha2_codes]

    #call iso3166_updates get_updates function to scrape all updates from country wikis
    iso3166_updates.get_updates(alpha2_codes, export_json_filename="new-iso3166-updates", 
        export_folder="/tmp", export_json=True, export_csv=False)

    #load exported updates json
    with open(os.path.join("/tmp", "new-iso3166-updates.json")) as input_json:
        iso3166_json = json.load(input_json)

    #iterate over all alpha2 codes, check for any updates in specified months range in updates json 
    for alpha2 in list(iso3166_json.keys()):
        current_iso3166_updates[alpha2] = []
        for row in range(0, len(iso3166_json[alpha2])):
            if (iso3166_json[alpha2][row]["Date Issued"] != ""): #go to next iteration if no Date Issued in row
                #convert str date into date object
                row_date = (datetime.strptime(iso3166_json[alpha2][row]["Date Issued"], "%Y-%m-%d"))
                #compare date difference from current row to current date
                date_diff = relativedelta(current_datetime, row_date)
                #calculate date difference in months
                diff_months = date_diff.months + (date_diff.years * 12)

                #if month difference is within months range, append to updates json object
                if (diff_months <= months):
                    current_iso3166_updates[alpha2].append(iso3166_json[alpha2][row])

        #if current alpha2 has no rows in date range, remove from temp object
        if (current_iso3166_updates[alpha2] == []):
            current_iso3166_updates.pop(alpha2, None)
    
    def create_issue(iso3166_updates_json):
        """
        Create a GitHub issue on the iso3166-2 repository, using the GitHub
        api, if any updates/changes are made to any entries in the ISO3166-2. 
        The Issue will be formatted in a way to clearly outline any of the 
        updates/changes to be made to the JSONs in the iso3166-2 repo. 

        Parameters
        ----------
        :iso3166_updates_json : json
           json object with all listed iso3166-2 updates in specified month 
           range. 

        Returns
        -------
        :message : str
            response message from GitHub api post request.

        References
        ----------
        [1]: https://developer.github.com/v3/issues/#create-an-issue
        """
        issue_json = {}
        issue_json["title"] = "ISO3166-2 Updates: " + str(current_datetime.strftime('%d-%m-%Y'))
        
        #get total sum of updates for all countrys in json
        total_updates = sum([len(iso3166_updates_json[code]) for code in iso3166_updates_json])
        total_countries = len(iso3166_updates_json)

        #body of Github Issue
        body = "# ISO3166-2 Updates\n"

        #get total sum of updates for all countrys in json
        total_updates = sum([len(iso3166_updates_json[code]) for code in iso3166_updates_json])
        total_countries = len(iso3166_updates_json)
        
        #display number of updates for countrys and the date period
        body += "## " + str(total_updates) + " updates found for " + str(total_countries) + " countries between period of " + \
            str((current_datetime + relativedelta(months=-1)).strftime('%d-%m-%Y')) + " to " + str(current_datetime.strftime('%d-%m-%Y')) + ".\n"

        #iterate over updates in json, append to email body
        for code in list(iso3166_updates_json.keys()):
            
            #header displaying current country name and code
            body += "\n### " + "Country - " + iso3166.countries_by_alpha2[code].name + " (" + code + ") " + flag.flag(code) + ":\n"

            #convert json object to str, so it can be appended to body
            temp = json.dumps(iso3166_updates_json[code])

            row_count = 0
            #iterate over all update rows for each country in object, appending to html body
            for row in iso3166_updates_json[code]:
                
                #increment row count which numbers each country's updates if more than 1
                if (len(iso3166_updates_json[code]) > 1):
                    row_count = row_count + 1
                    body += str(row_count) + ".)"

                #output all row field values 
                for key, val in row.items():
                    body += "<ins>" + str(key) + ":</ins> " + str(val) + "<br>"

        #add attributes to data json 
        issue_json["body"] = body
        issue_json["assignee"] = "amckenna41"
        issue_json["labels"] = ["iso3166-updates", "iso366-2", str(current_datetime.strftime('%d-%m-%Y'))]

        #api url and headers
        issue_url = "https://api.github.com/repos/" + os.environ["github-owner"] + "/" + os.environ["github-repo"] + "/issues"
        headers = {'Content-Type': "application/vnd.github+json", 
            "Authorization": "token " + os.environ["github-api-token"]}

        #make post request to github repo using api
        github_post_request = requests.post(issue_url, data=json.dumps(issue_json), headers=headers)

    def update_json(iso3166_updates_json):
        """
        If changes have been found for any countrys in the ISO3166-2 using the
        check_iso3166_updates_main function then the JSON in the storage bucket 
        is updated with the new JSON.

        Parameters
        ----------
        :iso3166_updates_json : json
           json object with all listed iso3166-2 updates in specified month 
           range. 

        Returns
        -------
        None
        """
        #initialise storage client
        storage_client = storage.Client()
        #create a bucket object for the bucket
        bucket = storage_client.get_bucket("iso3166-updates")
        #create a blob object from the filepath
        blob = bucket.blob("iso3166-updates.json")    

        #download iso3166-updates.json file from storage bucket 
        previous_updates_data = json.loads(blob.download_as_string(client=None))
        
        #set new json object to original one imported from gcp storage
        updated_json = previous_updates_data

        #iterate over all updates in json, if update/row not found in original json
        #pulled from GCP storage, append to new updated_json object
        for code in iso3166_updates_json:   
            for update in iso3166_updates_json[code]:
                if not (update in previous_updates_data[code]):
                    updated_json[code].append(update)

        #convert json objects into str
        previous_updates_data_str = json.dumps(previous_updates_data, sort_keys=True)
        updated_json_str = json.dumps(updated_json, sort_keys=True)

        #if updates found in JSON
        if (previous_updates_data_str != updated_json_str):

            #temp path for exported json
            tmp_updated_json_path = os.path.join("/tmp", 'iso3166-updates.json')
            
            #export updated json to temp folder
            with open(tmp_updated_json_path, 'w', encoding='utf-8') as output_json:
                json.dump(updated_json, output_json, ensure_ascii=False, indent=4)
            
            #create blob for updates JSON
            blob = bucket.blob('iso3166-updates.json')
            #upload new updated json using gcp sdk 
            blob.upload_from_filename(tmp_updated_json_path)
    
    #all GCP cloud funcs need to return something
    return_message = ""

    #if update object not empty - there are updates call send_email and update_json function
    if (current_iso3166_updates != {}):
        create_issue(current_iso3166_updates)
        update_json(current_iso3166_updates)
        return_message = "ISO3166-2 updates found."
    else:
        return_message = "No ISO3166-2 updates found."

    return return_message