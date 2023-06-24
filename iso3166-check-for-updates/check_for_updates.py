import iso3166_updates
import iso3166
import os
import json
import flag
from datetime import datetime
from operator import itemgetter
from dateutil.relativedelta import relativedelta
import requests
from google.cloud import storage
from flask import jsonify

def check_iso3166_updates_main(request):
    """
    Google Cloud Function that checks for any updates within specified date range
    for the iso3166-updates API. It uses the accompanying iso3166-updates Python
    software package to web scrape all country's ISO3166-2 wiki's checking for 
    any updates in a date range. 

    If any updates are found that are not already present in the JSON object
    within the GCP Storage bucket then a GitHub Issue is automatically created in the 
    iso3166-updates and iso3166-2 repository that itself stores all the latest info 
    and data relating to the ISO3166-2 standard. A similar Issue will also be raised 
    in the iso3166-flag-icons repo which is another custom repo that stores all the 
    flag icons of all countries and subdivisions in the ISO 3166-1 and ISO 3166-2.
    Additionally, if changes are found then the ISO 3166 updates JSON file in the 
    GCP Storage bucket is updated which is the data source for the iso3166-updates 
    Python package and accompanying API.

    Parameters
    ----------
    :request : (flask.Request)
       HTTP request object.
    
    Returns
    -------
    :current_iso3166_updates : json
       json containing any iso3166 updates for selected country/alpha-2 ISO code
       within specified date range.
    """
    #json object storing the error message and status code 
    error_message = {}
    error_message["status"] = 400

    #json object storing the success message and status code
    success_message = {}
    success_message["status"] = 200

    #default month cutoff for checking for updates
    months = 6

    #get list of any input parameters to function
    request_json = request.get_json()

    #parse months var from input params, use default value of 6 if param empty
    if request.args and 'months' in request.args:
        if (not(request.args.get('months') is None) or (request.args.get('months') != "")):
            months = request.args.get('months')
    elif request_json and 'months' in request_json:
        if (not(request.args.get('months') is None) or (request.args.get('months') != "")):
            months = request.args.get('months')

    #get current date and time on function execution
    current_datetime = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d")

    #object containing current iso3166-2 updates after month range date filter applied
    latest_iso3166_updates_after_date_filter = {}

    #get list of all country's 2 letter alpha-2 codes
    alpha2_codes = sorted(list(iso3166.countries_by_alpha2.keys()))

    #sort codes in alphabetical order and uppercase
    alpha2_codes.sort()
    alpha2_codes = [code.upper() for code in alpha2_codes]

    #call iso3166_updates get_updates function to scrape all updates from country wikis
    latest_iso3166_updates = iso3166_updates.get_updates(alpha2_codes, export_filename="new-iso3166-updates", 
        export_folder="/tmp", export_json=True, export_csv=False, verbose=True)

    #iterate over all alpha-2 codes, check for any updates in specified months range in updates json 
    for alpha2 in list(latest_iso3166_updates.keys()):
        latest_iso3166_updates_after_date_filter[alpha2] = []
        for row in range(0, len(latest_iso3166_updates[alpha2])):
            if (latest_iso3166_updates[alpha2][row]["Date Issued"] != ""): #go to next iteration if no Date Issued in row
                #convert str date into date object
                row_date = (datetime.strptime(latest_iso3166_updates[alpha2][row]["Date Issued"], "%Y-%m-%d"))
                #compare date difference from current row to current date
                date_diff = relativedelta(current_datetime, row_date)
                #calculate date difference in months
                diff_months = date_diff.months + (date_diff.years * 12)

                #if month difference is within months range, append to updates json object
                if (diff_months <= months):
                    latest_iso3166_updates_after_date_filter[alpha2].append(latest_iso3166_updates[alpha2][row])

        #if current alpha-2 has no rows in date range, remove from temp object
        if (latest_iso3166_updates_after_date_filter[alpha2] == []):
            latest_iso3166_updates_after_date_filter.pop(alpha2, None)
    
    def update_json(latest_iso3166_updates_after_date_filter):
        """
        If changes have been found for any countrys in the ISO3166-2 within the
        specified date range using the check_iso3166_updates_main function then 
        the JSON in the storage bucket is updated with the new JSON and the old 
        one is stored in an archive folder on the same bucket.

        Parameters
        ----------
        :latest_iso3166_updates_after_date_filter : json
           json object with all listed iso3166-2 updates after month date filter
           applied.

        Returns
        -------
        :updates_found : bool
            bool to track if updates/changes have been found in JSON object.
        individual_updates_json: dict
            dictionary of individual ISO 3166 updates that aren't in existing 
            updates object on JSON.
        """
        #initialise storage client
        storage_client = storage.Client()
        try:
            #create a bucket object for the bucket
            bucket = storage_client.get_bucket(os.environ["BUCKET_NAME"])
        except google.cloud.exceptions.NotFound:
            error_message["message"] = "Error retrieving updates data json storage bucket: {}.".format(os.environ["BUCKET_NAME"])
            return jsonify(error_message), 400
        #create a blob object from the filepath
        blob = bucket.blob(os.environ["BLOB_NAME"])  

        #raise error if updates file not found in bucket
        if not (blob.exists()):
            raise ValueError("Error retrieving updates data json: {}.".format(os.environ["BLOB_NAME"]))
        
        #download current ISO 3166 updates JSON file from storage bucket 
        current_updates_data = json.loads(blob.download_as_string(client=None))

        #set new json object to original one imported from gcp storage
        updated_json = current_updates_data
        updates_found = False

        #seperate object that holds individual updates that were found, used in create_issue function
        individual_updates_json = {}

        #iterate over all updates in json, if update/row not found in original json, pulled from GCP storage, 
        # append to new updated_json object
        for code in latest_iso3166_updates_after_date_filter:   
            individual_updates_json[code] = []
            for update in latest_iso3166_updates_after_date_filter[code]:
                if not (update in current_updates_data[code]):
                    updated_json[code].append(update)
                    updates_found = True
                    individual_updates_json[code].append(update)

            #updates are appended to end of updates json, need to reorder by Date Issued, latest first
            updated_json[code] = sorted(updated_json[code], key=itemgetter('Date Issued'), reverse=True)

            #if current alpha-2 code has no updates associated with it, remove from temp object
            if (individual_updates_json[code] == []):
                individual_updates_json.pop(code, None)

        #if updates found in new updates json compared to current one
        if (updates_found):

            #temp path for exported json
            tmp_updated_json_path = os.path.join("/tmp", os.environ["BLOB_NAME"])
            
            #export updated json to temp folder
            with open(tmp_updated_json_path, 'w', encoding='utf-8') as output_json:
                json.dump(updated_json, output_json, ensure_ascii=False, indent=4)
            
            #create blob for updated JSON
            blob = bucket.blob(os.environ["BLOB_NAME"])

            #move current updates json in bucket to an archive folder, append datetime to it
            archive_filepath = os.environ["ARCHIVE_FOLDER"] + "/" + os.path.splitext(os.environ["BLOB_NAME"])[0] \
                + "_" + str(current_datetime.strftime('%Y-%m-%d')) + ".json"
            
            #create blob for archive updates json 
            archive_blob = bucket.blob(archive_filepath)
            
            #upload old updates json to archive folder 
            archive_blob.upload_from_filename(tmp_updated_json_path)

            #upload new updated json using gcp sdk, replacing current updates json 
            blob.upload_from_filename(tmp_updated_json_path)

        return updates_found, individual_updates_json
        
    def create_issue(latest_iso3166_updates_after_date_filter, month_range):
        """
        Create a GitHub issue on the iso3166-2, iso3166-updates and 
        iso3166-flag-icons repository, using the GitHub api, if any updates/changes 
        are made to any entries in the ISO 3166-2. The Issue will be formatted in 
        a way to clearly outline any of the updates/changes to be made to the JSONs 
        in the iso3166-2, iso3166-updates and iso3166-flag-icons repos. 

        Parameters
        ----------
        :latest_iso3166_updates_after_date_filter : json
           json object with all listed iso3166-2 updates after month date filter
           applied.
        :month_range : int
            number of past months updates were pulled from.

        Returns
        -------
        :message : str
            response message from GitHub api post request.

        References
        ----------
        [1]: https://developer.github.com/v3/issues/#create-an-issue
        """
        issue_json = {}
        issue_json["title"] = "ISO 3166-2 Updates: " + str(current_datetime.strftime('%Y-%m-%d')) + " (" + ', '.join(list(latest_iso3166_updates_after_date_filter)) + ")" 
        
        #body of Github Issue
        body = "# ISO 3166-2 Updates\n"

        #get total sum of updates for all countrys in json
        total_updates = sum([len(latest_iso3166_updates_after_date_filter[code]) for code in latest_iso3166_updates_after_date_filter])
        total_countries = len(latest_iso3166_updates_after_date_filter)
        
        #change body text if more than 1 country 
        if (total_countries == 1):
            body += "### " + str(total_updates) + " updates found for " + str(total_countries) + " country between the "
        else:
            body += "### " + str(total_updates) + " updates found for " + str(total_countries) + " countries between the "

        #display number of updates for countrys and the date period
        body += "### " + str(total_updates) + " updates found for " + str(total_countries) + " countries between the " + str(month_range) + " month period of " + \
            str((current_datetime + relativedelta(months=-month_range)).strftime('%Y-%m-%d')) + " to " + str(current_datetime.strftime('%d-%m-%Y')) + ".\n"

        #iterate over updates in json, append to updates object
        for code in list(latest_iso3166_updates_after_date_filter.keys()):
            
            #header displaying current country name, code and flag icon using emoji-country-flag library
            body += "\n### " + "Country - " + iso3166.countries_by_alpha2[code].name + " (" + code + ") " + flag.flag(code) + ":\n"

            row_count = 0

            #iterate over all update rows for each country in object, appending to html body
            for row in latest_iso3166_updates_after_date_filter[code]:
                
                #increment row count which numbers each country's updates if more than 1
                if (len(latest_iso3166_updates_after_date_filter[code]) > 1):
                    row_count = row_count + 1
                    body += str(row_count) + ".)"

                #output all row field values 
                for key, val in row.items():
                    body += "<ins>" + str(key) + ":</ins> " + str(val) + "<br>"

        #add attributes to data json 
        issue_json["body"] = body
        issue_json["assignee"] = "amckenna41"
        issue_json["labels"] = ["iso3166-updates", "iso3166", "iso366-2", "subdivisions", "iso3166-flag-icons", str(current_datetime.strftime('%Y-%m-%d'))]

        #api url and headers
        issue_url = "https://api.github.com/repos/" + os.environ["github-owner"] + "/" + os.environ["github-repo-1"] + "/issues"
        issue_url_2 = "https://api.github.com/repos/" + os.environ["github-owner"] + "/" + os.environ["github-repo-2"] + "/issues"
        issue_url_3 = "https://api.github.com/repos/" + os.environ["github-owner"] + "/" + os.environ["github-repo-3"] + "/issues"
        headers = {'Content-Type': "application/vnd.github+json", 
            "Authorization": "token " + os.environ["github-api-token"]}

        #make post request to github repos using api
        requests.post(issue_url, data=json.dumps(issue_json), headers=headers)
        requests.post(issue_url_2, data=json.dumps(issue_json), headers=headers)
        requests.post(issue_url_3, data=json.dumps(issue_json), headers=headers)

    #if update object not empty (i.e there are updates), call update_json and create_issue functions
    if (latest_iso3166_updates_after_date_filter != {}):
        updates_found, filtered_updates = update_json(latest_iso3166_updates_after_date_filter)
    if (updates_found):
        create_issue(filtered_updates, months)
        print("ISO 3166-2 updates found and successfully exported.")
        success_message["message"] = "ISO 3166-2 updates found and successfully exported."
    else:
        print("No ISO 3166-2 updates found.")
        success_message["message"] = "No ISO 3166-2 updates found."

    return jsonify(success_message), 200