from flask import Flask, jsonify
import iso3166
import os
import json
import flag
from datetime import datetime
from operator import itemgetter
from dateutil.relativedelta import relativedelta
import requests
from google.cloud import storage
from get_all_iso3166_updates import *

#initialise Flask app
app = Flask(__name__)

#json object storing the error message and status code 
error_message = {}
error_message["status"] = 400

#json object storing the success message and status code
success_message = {}
success_message["status"] = 200

#get current date and time on function execution
current_datetime = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d")

@app.route("/")
def check_for_updates_main():
    """
    Google Cloud Run main entry script that checks for any latest/missing ISO 3166-2 
    updates data within specified date range for the iso3166-updates API. It uses the 
    get_all_iso3166_updates.py script to web scrape all country's ISO 3166-2 data 
    from the various data sources, checking for any updates in a date range. This 
    date range is normally set to the past 6-12 months, as the ISO 3166 is updated 
    annually (except for 2001 and 2006), usually at the end of the year as well as 
    periodically throughout. The Cloud run app is built using a custom docker container 
    that contains all the required dependancies and binaries required to run this script. 
    
    If any updates are found that are not already present in the JSON object within 
    the GCP Storage bucket then a GitHub Issue is automatically created that 
    tabulates and formats all the latest data in the iso3166-updates and iso3166-2 
    repositories that itself stores all the latest subdivision info and data relating 
    to the ISO 3166-2 standard. A similar Issue will also be raised in the 
    iso3166-flag-icons repo which is another custom repo that stores all the flag 
    icons of all countries and subdivisions in the ISO 3166-1 and ISO 3166-2. 
    Additionally, if changes are found then the ISO 3166 updates JSON file in the GCP 
    Storage bucket is updated which is the data source for the iso3166-updates 
    Python package and accompanying API.

    Parameters
    ==========
    None
    
    Returns
    =======
    :success_message/error_message: json
       jsonified response indicating whether the application has completed successfully or
       an error has arose during execution.
    """
    #object containing current iso3166-2 updates after month range date filter applied
    latest_iso3166_updates_after_date_filter = {}
    
    #month range to get latest updates from, default of 12 months used if env var empty 
    if (os.environ.get("MONTH_RANGE") is None or os.environ.get("MONTH_RANGE") == ""):
        months = 12
    else:
        months = int(os.environ["MONTH_RANGE"]) #convert to int - months should be a whole number

    #get create_issue bool env var which determines if GitHub Issues are created each time new/missing ISO 3166 updates are found
    if (os.environ.get("CREATE_ISSUE") is None or os.environ.get("CREATE_ISSUE") == ""):
        create_issue = True
    else:
        create_issue = bool(os.environ["CREATE_ISSUE"]) #convert to bool - var should be 0 or 1

    #get list of all country's 2 letter alpha-2 codes
    alpha2_codes = sorted(list(iso3166.countries_by_alpha2.keys()))

    #sort codes into alphabetical order and uppercase
    alpha2_codes.sort()
    alpha2_codes = [code.upper() for code in alpha2_codes]
    
    #call get_updates function to scrape all latest country updates from data sources
    latest_iso3166_updates = get_updates(alpha2_codes=alpha2_codes, export_json=False, export_csv=False, verbose=True)
    
    #iterate over all alpha-2 codes, check for any updates in specified months range in updates json 
    for alpha2 in list(latest_iso3166_updates.keys()):
        latest_iso3166_updates_after_date_filter[alpha2] = []
        for row in range(0, len(latest_iso3166_updates[alpha2])):
            if (latest_iso3166_updates[alpha2][row]["Date Issued"] != ""): #go to next iteration if no Date Issued in row
                #convert str date into date object, remove "corrected" date if appliceable
                row_date = (datetime.strptime(re.sub("[(].*[)]", "", latest_iso3166_updates[alpha2][row]["Date Issued"]).replace(' ', "").replace(".", ''), "%Y-%m-%d"))
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

    #bool to track if any ISO 3166 updates found
    updates_found = False
    
    #if update object not empty (i.e there are changes/updates), call update_json and create_github_issue functions
    updates_found, date_filtered_updates, missing_filtered_updates = update_json(latest_iso3166_updates, latest_iso3166_updates_after_date_filter)
    if (updates_found):
        if (create_issue):
            create_github_issue(date_filtered_updates, missing_filtered_updates, months)
            success_message["message"] = "New ISO 3166 updates found and successfully exported to bucket and GitHub Issues created."
            print(success_message["message"])
        else:
            success_message["message"] = "New ISO 3166 updates found and successfully exported to bucket."
            print(success_message["message"])
    else:
        success_message["message"] = "No new ISO 3166 updates found."
        print(success_message["message"])

    return jsonify(success_message), 200

def update_json(latest_iso3166_updates, latest_iso3166_updates_after_date_filter):
    """
    If changes have been found for any countries in the ISO 3166 within the
    specified date range using the check_iso3166_updates_main function then 
    the JSON in the storage bucket is updated with the new JSON and the old 
    one is stored in an archive folder on the same bucket. Additionally, the 
    current object is verified to not contain any missing data, regardless of
    date range, if so then these will similarly be appended to object.

    Parameters
    ==========
    :latest_iso3166_updates: json
        json object with all listed iso3166-2 updates, without date filter
        applied.
    :latest_iso3166_updates_after_date_filter: json
        json object with all listed iso3166-2 updates after month date filter
        applied. 

    Returns
    =======
    :updates_found: bool
        bool to track if updates/changes have been found in JSON object.
    :individual_updates_json: dict
        dictionary of individual ISO 3166 updates that aren't in existing 
        updates object on JSON, after date filter applied.
    :missing_individual_updates_json: dict
        dictionary of individual ISO 3166 updates that aren't in existing 
        updates object on JSON, with no date filter applied.
    """
    #initialise storage client
    storage_client = storage.Client()
    try:
        #create a bucket object for the bucket, raise error if env var not set or bucket not found
        if (os.environ.get("BUCKET_NAME") is None or os.environ.get("BUCKET_NAME") == ""):
            error_message["message"] = "Bucket name environment variable not set."
            return jsonify(error_message), 400
        bucket = storage_client.get_bucket(os.environ["BUCKET_NAME"])
    except google.cloud.exceptions.NotFound:
        error_message["message"] = "Error retrieving updates data json storage bucket: {}.".format(os.environ["BUCKET_NAME"])
        return jsonify(error_message), 400
    
    #create a blob object from the filepath, raise error if env var not set
    if (os.environ.get("BLOB_NAME") is None or os.environ.get("BLOB_NAME") == ""):
        error_message["message"] = "Blob name environment variable not set."
        return jsonify(error_message), 400
    blob = bucket.blob(os.environ["BLOB_NAME"])  
    
    #raise error if updates file not found in bucket
    if not (blob.exists()):
        raise ValueError("Error retrieving updates data json: {}.".format(os.environ["BLOB_NAME"]))
    
    #download current ISO 3166 updates JSON file from storage bucket 
    current_updates_data = json.loads(blob.download_as_string(client=None))

    #set new json object to original one imported from GCP storage
    updated_json = current_updates_data
    updates_found = False

    #seperate object that holds individual updates that were found with and without date range applied (used in create_github_issue function)
    individual_updates_json = {}
    missing_individual_updates_json = {}
    
    ## Appending any missing updates to object that were found after date range filter applied ##
     
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

    ## Appending any missing updates to object that were found, regardless of date range filter ##

    #iterate over all updates in json, if update/row not found in original json, pulled from GCP storage, 
    # append to new updated_json object, with date range filter applied
    for code in latest_iso3166_updates:   
        missing_individual_updates_json[code] = []
        for update in latest_iso3166_updates[code]:
            if not (update in current_updates_data[code]):
                updated_json[code].append(update)
                updates_found = True
                missing_individual_updates_json[code].append(update)

        #updates are appended to end of updates json, need to reorder by Date Issued, latest first
        updated_json[code] = sorted(updated_json[code], key=itemgetter('Date Issued'), reverse=True)

        #if current alpha-2 code has no updates associated with it, remove from temp object
        if (missing_individual_updates_json[code] == []):
            missing_individual_updates_json.pop(code, None)

    #if updates found in new updates json compared to current one in bucket
    if (updates_found):

        #move current updates json in bucket to an archive folder, append datetime to it
        if (os.environ.get("ARCHIVE_FOLDER") is None or os.environ.get("ARCHIVE_FOLDER") == ""):
            os.environ["ARCHIVE_FOLDER"] = "archive_iso3166_updates"

        #filepath to archive folder
        archive_filepath = os.path.splitext(os.environ["BLOB_NAME"])[0] \
            + "_" + str(current_datetime.strftime('%Y-%m-%d')) + ".json"

        #export updated json to temp folder
        with open(os.path.join("/tmp", archive_filepath), 'w', encoding='utf-8') as output_json:
            json.dump(json.loads(blob.download_as_string(client=None)), output_json, ensure_ascii=False, indent=4)

        #create blob for archive updates json 
        archive_blob = bucket.blob(os.path.join(os.environ["ARCHIVE_FOLDER"], archive_filepath))
        
        #upload old updates json to archive folder 
        archive_blob.upload_from_filename(os.path.join("/tmp", archive_filepath))

    #temp path for exported json
    tmp_updated_json_path = os.path.join("/tmp", os.environ["BLOB_NAME"])
    
    #export updated json object to bucket if env var true - if env var not set then don't export to bucket
    if (os.environ.get("EXPORT") is None):
        if (os.environ["EXPORT"]):

            #export updated json to temp folder
            with open(tmp_updated_json_path, 'w', encoding='utf-8') as output_json:
                json.dump(updated_json, output_json, ensure_ascii=False, indent=4)
            
            #create blob for updated JSON
            blob = bucket.blob(os.environ["BLOB_NAME"])

            #upload new updated json using gcp sdk, replacing current updates json 
            blob.upload_from_filename(tmp_updated_json_path)

    return updates_found, individual_updates_json, missing_individual_updates_json
    
def create_github_issue(latest_iso3166_updates_after_date_filter, missing_filtered_updates, month_range):
    """
    Create a GitHub issue on the iso3166-2, iso3166-updates and 
    iso3166-flag-icons repository, using the GitHub api, if any updates/changes 
    were found in the ISO 3166 that aren't in the current object. The Issue will 
    be formatted and tabulated in a way to clearly outline any of the updates/changes 
    to be made to the JSONs in the iso3166-2, iso3166-updates and iso3166-flag-icons 
    repos. 

    Parameters
    ==========
    :latest_iso3166_updates_after_date_filter: dict
        dict object with all listed ISO 3166 updates after month date filter applied.
    :missing_filtered_updates: dict
        dict object with any missing ISO 3166 updates, regardless of date filter.
    :month_range: int
        number of previous months updates were pulled from.

    Returns
    =======
    :create_issue_success: bool
        bool tracking if GitHub Issues were created successfully using the status 
        code of the post request.

    References
    ==========
    [1]: https://developer.github.com/v3/issues/#create-an-issue
    """
    issue_json = {}
    issue_json["title"] = "ISO 3166 updates: " + str(current_datetime.strftime('%Y-%m-%d')) + " (" + \
        (', '.join(set(list(latest_iso3166_updates_after_date_filter.keys()) + list(missing_filtered_updates.keys())))) + ")"

    #body of GitHub Issue
    body = "# ISO 3166 updates\n"

    #get total sum of updates for all countries in json
    total_updates = sum([len(latest_iso3166_updates_after_date_filter[code]) for code in latest_iso3166_updates_after_date_filter])
    total_countries = len(latest_iso3166_updates_after_date_filter)

    #append any updates data to body
    if (total_countries != 0):

        #display number of updates for countries and the date period
        body += "<h2>" + str(total_updates) + " update(s) found for " + str(total_countries) + " country/countries between the " + str(month_range) + " month period of " + \
            str((current_datetime + relativedelta(months=-month_range)).strftime('%Y-%m-%d')) + " to " + str(current_datetime.strftime('%Y-%m-%d')) + "</h2>"

        #iterate over updates in json, append to updates object
        for code in list(latest_iso3166_updates_after_date_filter.keys()):
            
            #header displaying current country name, code and flag icon using emoji-country-flag library
            body += "<h3>" + iso3166.countries_by_alpha2[code].name + " (" + code + ") " + flag.flag(code) + ":</h3>"

            #create table element to store output data
            body += "<table><tr><th>Date Issued</th><th>Edition/Newsletter</th><th>Code/Subdivision Change</th><th>Description of Change in Newsletter</th></tr>"

            #iterate over all update rows for each country in object, appending to table row 
            for row in latest_iso3166_updates_after_date_filter[code]:
                body += "<tr>"
                for _, val in row.items():
                    body += "<td>" + val + "</td>"
                body += "</tr>"
    
            #close table element 
            body += "</table>"

    #get total sum of any missing updates data for all countries in json, regardless of date filter
    total_missing_updates = sum([len(missing_filtered_updates[code]) for code in missing_filtered_updates])
    total_missing_countries = len(missing_filtered_updates)

    #append any missing updates data to body
    if (total_missing_countries != 0):

        #display number of updates for countries and the date period
        body += "<h2>" + str(total_missing_updates) + " missing update(s) found for " + str(total_missing_countries) + " country/countries</h2>"

        #iterate over updates in json, append to updates object
        for code in list(missing_filtered_updates.keys()):
            
            #header displaying current country name, code and flag icon using emoji-country-flag library
            body += "<h3>" + iso3166.countries_by_alpha2[code].name + " (" + code + ") " + flag.flag(code) + ":</h3>"

            #create table element to store output data
            body += "<table><tr><th>Date Issued</th><th>Edition/Newsletter</th><th>Code/Subdivision Change</th><th>Description of Change in Newsletter</th></tr>"

            #iterate over all update rows for each country in object, appending to table element
            for row in missing_filtered_updates[code]:
                body += "<tr>"
                for _, val in row.items():
                    body += "<td>" + val + "</td>"
                body += "</tr>"                
                
            #close table element
            body += "</table>"
    
    #add attributes to data json 
    issue_json["body"] = body
    issue_json["assignee"] = "amckenna41"
    issue_json["labels"] = ["iso3166-updates", "iso", "iso3166", "iso3166-1", "iso366-2", "subdivisions", "iso3166-flag-icons", str(current_datetime.strftime('%Y-%m-%d'))]

    #raise error if GitHub related env vars not set
    if (os.environ.get("GITHUB_OWNER") is None or os.environ.get("GITHUB_OWNER") == "" or \
        os.environ.get("GITHUB_API_TOKEN") is None or os.environ.get("GITHUB_API_TOKEN") == ""):
        error_message["message"] = "GitHub owner name and or API token environment variables not set."
        return jsonify(error_message), 400
    
    #http request headers for GitHub API
    headers = {'Content-Type': "application/vnd.github+json", 
               "Authorization": "token " + os.environ["GITHUB_API_TOKEN"]}
    github_repos = os.environ.get("GITHUB_REPOS")
    
    #make post request to create issue in repos using GitHub api url and headers, if github_repo env vars set
    if not (github_repos is None and github_repos != ""): 
        #split into list of repos 
        github_repos = github_repos.replace(' ', '').split(';')

        #iterate over each repo listed in env var, making post request with issue_json data 
        for repo in github_repos:
            
            issue_url = "https://api.github.com/repos/" + os.environ["GITHUB_OWNER"] + "/" + repo + "/issues"
            github_request = requests.post(issue_url, data=json.dumps(issue_json), headers=headers)    

            #print error message if success status code not returned            
            if (github_request.status_code != 200):  
                if (github_request.status_code == 401):
                    print("Authorisation issue when creating GitHub Issue in repository {}, could be an issue with the GitHub PAT.".format(repo))
                else:
                    print("Issue when creating GitHub Issue in repository {}, got status code {}.".format(repo, github_request.status_code))   