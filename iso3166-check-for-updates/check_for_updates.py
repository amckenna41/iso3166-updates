from flask import Flask, jsonify
import iso3166
import os
import json
import flag
from datetime import datetime
from operator import itemgetter
from dateutil.relativedelta import relativedelta
from iso3166_updates import *
import requests
from google.cloud import storage, exceptions
from get_all_iso3166_updates import *
from github import Github

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

#instance of ISO3166_Updates class to get all updates in current software version
current_iso3166_updates = ISO3166_Updates()

@app.route("/")
def check_for_updates_main() -> tuple[dict, int]:
    """
    Google Cloud Run main entry script that checks for any latest/missing ISO 3166-2 
    updates data within specified date range for the iso3166-updates API. It uses the 
    get_all_iso3166_updates.py script to web scrape all country's ISO 3166-2 updates 
    data from the various data sources (wiki and ISO), checking for any updates in a 
    date range. This date range is normally set to the past 6-12 months, as the ISO 3166 
    is updated annually (except for 2001 and 2006), usually at the end of the year as 
    well as period updates published throughout the year. The Cloud run app is built 
    using a custom docker container that contains all the required dependencies and 
    binaries required to run this script. 
    
    If any updates are found that are not already present in the JSON object within 
    the current version of the iso3166-updates software package then a GitHub Issue 
    is automatically created that tabulates and formats all the latest data in the 
    iso3166-updates and iso3166-2 repositories that itself stores all the latest 
    subdivision info and data relating to the ISO 3166-2 standard. A similar Issue 
    will also be raised in the iso3166-flag-icons repo which is another custom repo 
    that stores all the flag icons of all countries and subdivisions in the 
    ISO 3166-1 and ISO 3166-2. 

    Additionally, if the EXPORT environment variable is set then the output object
    will be exported to a GCP Storage bucket.

    Parameters
    ==========
    None
    
    Returns
    =======
    :success_message/error_message: json
       jsonified response indicating whether the application has completed successfully or
       an error has arose during execution.
    :success_code/error_code: int
        successful or erroneous status code, 400 or 200, respectively. 
    """
    #object containing current iso3166-2 updates after month range date filter applied
    latest_iso3166_updates_after_date_filter = {}
    
    #month range to get latest updates from, default of 12 months used if env var empty or not a valid int
    if ((os.environ.get("MONTH_RANGE") is None) or (os.environ.get("MONTH_RANGE") == "") or str(os.environ.get("MONTH_RANGE")).isdigit()):
        months = 12
    else:
        months = int(os.environ["MONTH_RANGE"]) #convert to int - months should be a whole number

    #get create_issue bool env var which determines if GitHub Issues are created each time new/missing ISO 3166 updates are found
    if (os.environ.get("CREATE_ISSUE") is None or os.environ.get("CREATE_ISSUE") == ""):
        create_issue = False
    else:
        create_issue = bool(os.environ["CREATE_ISSUE"]) #convert to bool - var should be 0 or 1

    #get export env var which determines if new updates data object is exported to GCP storage bucket
    if (os.environ.get("EXPORT") is None or os.environ.get("EXPORT") == ""):
        export = False
    else:
        export = bool(os.environ["EXPORT"]) #convert to bool - var should be 0 or 1

    #get bucket name & blob details env vars for exporting object to GCP, these can be empty/None if export env var is set to False
    bucket_name = os.environ.get("BUCKET_NAME")
    blob_name = os.environ.get("BUCKET_NAME")
    archive_folder = os.environ.get("ARCHIVE_FOLDER")

    #get latest date that object was updated on the repo, using github client and library 
    github_client = Github()
    repo = github_client.get_repo("amckenna41/iso3166-updates")
    commits = repo.get_commits(path='iso3166-updates.json')
    if (commits.totalCount):
        latest_commit_date = commits[0].commit.committer.date

    #get month difference between current date and last updated date, print out the difference
    # month_difference = latest_commit_date.months - current_datetime.months
    print("latest_commit_date type", type(latest_commit_date))
    # print(f"iso3166-updates.json object last updated {month_difference} months ago on: {latest_commit_date}.")
    print(f"iso3166-updates.json object last updated months ago on: {latest_commit_date}.")
    
    #call get_updates function to scrape all latest country updates from data sources
    latest_iso3166_updates = get_updates(export_json=False, export_csv=False, verbose=True)
    
    #iterate over all alpha-2 codes, check for any updates in specified months range in updates json 
    for alpha2 in list(latest_iso3166_updates.keys()):
        latest_iso3166_updates_after_date_filter[alpha2] = []
        for row in range(0, len(latest_iso3166_updates[alpha2])):
            if (latest_iso3166_updates[alpha2][row]["Date Issued"] != ""): #go to next iteration if no Date Issued in row
                #convert str date into date object, remove "corrected" date if applicable
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
        
    #if update object not empty (i.e there are changes/updates), call update_json, create_github_issue and or export to bucket functions
    updates_found, date_filtered_updates, missing_filtered_updates = update_json(latest_iso3166_updates, latest_iso3166_updates_after_date_filter)
    
    #
    if (updates_found):
        #
        if (create_issue and (export and not (bucket_name or blob_name) is None)):
            create_github_issue_success_code = create_github_issue(date_filtered_updates, missing_filtered_updates, months)
            export_to_bucket_success_code = export_to_bucket(latest_iso3166_updates)
            if (create_github_issue_success_code != -1 and export_to_bucket_success_code != -1):
                success_message["message"] = f"New ISO 3166 updates found and successfully exported to bucket {bucket_name} and GitHub Issues created."
            elif (create_github_issue_success_code != -1):
                success_message["message"] = "New ISO 3166 updates found and GitHub Issues created. There was an error exporting to the GCP storage bucket."
            elif (export_to_bucket_success_code != -1):
                success_message["message"] = f"New ISO 3166 updates found and successfully exported to bucket {bucket_name}. There was an error creating the GitHub Issues."
        #
        elif (export and (bucket_name or blob_name) is None):
            success_message["message"] = f"New ISO 3166 updates found but could not export to bucket as the bucket environment variables \
                  BUCKET and BLOB_NAME were not specified."
        #
        elif (create_issue):
            create_github_issue_success_code = create_github_issue(date_filtered_updates, missing_filtered_updates, months)
            if (create_github_issue_success_code != -1):
                success_message["message"] = "New ISO 3166 updates found and GitHub Issues created."
            else:
                success_message["message"] = "New ISO 3166 updates found but there was an error creating the GitHub Issues."
    else:
        success_message["message"] = "No new ISO 3166 updates found."

    print(success_message["message"])

    return jsonify(success_message), 200

def update_json(latest_iso3166_updates: dict, latest_iso3166_updates_after_date_filter: dict) -> tuple[bool, dict, dict]:
    """
    The most recent ISO 3166 changes object is compared to the object in 
    the current version of the iso3166-updates software. Any differences
    between the objects are tracked in another separate object and
    returned from the function. Additionally, any missing data, regardless 
    of date range is similarly tracked and returned from the function. 

    Parameters
    ==========
    :latest_iso3166_updates: dict
        json object with all listed iso3166-2 updates, without date filter
        applied.
    :latest_iso3166_updates_after_date_filter: dictß
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
    #set new json object to original one imported from current software version
    updated_json = current_iso3166_updates.all
    updates_found = False

    #separate object that holds individual updates that were found with and without date range applied (used in create_github_issue function)
    individual_updates_json = {}
    missing_individual_updates_json = {}
    
    ## Appending any missing updates to object that were found after date range filter applied ##
     
    #iterate over all updates in json, if update/row not found in original json in software version, append to new updated_json object 
    for code in latest_iso3166_updates_after_date_filter:   
        individual_updates_json[code] = []
        for update in latest_iso3166_updates_after_date_filter[code]:
            if not (update in current_iso3166_updates[code]):
                updated_json[code].append(update)
                updates_found = True
                individual_updates_json[code].append(update)

        #updates are appended to end of updates json, need to reorder by Date Issued, latest first
        updated_json[code] = sorted(updated_json[code], key=itemgetter('Date Issued'), reverse=True)

        #if current alpha-2 code has no updates associated with it, remove from temp object
        if (individual_updates_json[code] == []):
            individual_updates_json.pop(code, None)

    ## Appending any missing updates to object that were found, regardless of date range filter ##

    #iterate over all updates in json, if update/row not found in original json, append to new updated_json object, with date range filter applied
    for code in latest_iso3166_updates:   
        missing_individual_updates_json[code] = []
        for update in latest_iso3166_updates[code]:
            if not (update in current_iso3166_updates[code]):
                updated_json[code].append(update)
                updates_found = True
                missing_individual_updates_json[code].append(update)

        #updates are appended to end of updates json, need to reorder by Date Issued, latest first
        updated_json[code] = sorted(updated_json[code], key=itemgetter('Date Issued'), reverse=True)

        #if current alpha-2 code has no updates associated with it, remove from temp object
        if (missing_individual_updates_json[code] == []):
            missing_individual_updates_json.pop(code, None)

    return updates_found, individual_updates_json, missing_individual_updates_json
    
def create_github_issue(latest_iso3166_updates_after_date_filter: dict, missing_filtered_updates: dict, month_range: int) -> tuple[dict, dict, int]:
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
    :success_code: int
        return code to indicate if the GitHub issue was successfully created or 
        there was an error during execution.

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
            body += "<table><tr><th>Date Issued</th><th>Edition/Newsletter</th><th>Code/Subdivision Change</th><th>Description of Change</th></tr>"

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
            body += "<table><tr><th>Date Issued</th><th>Edition/Newsletter</th><th>Code/Subdivision Change</th><th>Description of Change</th></tr>"

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
        print("GitHub owner name and or API token environment variables not set.")
        return -1
    
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
            
            #get url of repo and make post request
            issue_url = "https://api.github.com/repos/" + os.environ["GITHUB_OWNER"] + "/" + repo + "/issues"
            github_request = requests.post(issue_url, data=json.dumps(issue_json), headers=headers)    

            #print error message if success status code not returned            
            if (github_request.status_code != 200):  
                if (github_request.status_code == 401):
                    print(f"Authorisation issue when creating GitHub Issue in repository {repo}, could be an issue with the GitHub PAT.")
                else:
                    print(f"Issue when creating GitHub Issue in repository {repo}, got status code {github_request.status_code}.")
                
                return -1
    
    return 0

def export_to_bucket(latest_iso3166_updates: dict) -> None:
    """
    If the export environment variable is set and changes are found that 
    aren't present in the existing repo object, export the new object
    to the specified GCP bucket. This can then be downloaded and 
    incorporated into the software. 

    Parameters
    ==========
    :latest_iso3166_updates: dict
        json object with all listed iso3166-2 updates, without date filter
        applied.        

    Returns
    =======
    None
    """
    #initialise storage client
    storage_client = storage.Client()
    try:
        # #create a bucket object for the bucket, raise error if bucket not found
        bucket = storage_client.get_bucket(os.environ["BUCKET_NAME"])
    except exceptions.NotFound:
        error_message["message"] = f"Error retrieving updates data json storage bucket: {os.environ["BUCKET_NAME"]}."
        return jsonify(error_message), 400

    #create a blob object from the filepath
    blob = bucket.blob(os.environ["BLOB_NAME"])  

    if  (blob.exists()):


        #move current updates json in bucket, if applicable, to an archive folder, append datetime to it
        if (os.environ.get("ARCHIVE_FOLDER") is None or os.environ.get("ARCHIVE_FOLDER") == ""):
            os.environ["ARCHIVE_FOLDER"] = "archive_iso3166_updates"
            archive_filepath = os.environ["ARCHIVE_FOLDER"] + "/" + os.path.splitext(os.environ["BLOB_NAME"])[0] \
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
    
    #export updated json to temp folder
    with open(tmp_updated_json_path, 'w', encoding='utf-8') as output_json:
        json.dump(latest_iso3166_updates, output_json, ensure_ascii=False, indent=4)

    #create blob for updated JSON
    blob = bucket.blob(os.environ["BLOB_NAME"])

    #upload new updated json using gcp sdk, replacing current updates json 
    blob.upload_from_filename(tmp_updated_json_path)

    #upload new updated json using gcp sdk, replacing current updates json 
    blob.upload_from_filename(os.environ["BLOB_NAME"])