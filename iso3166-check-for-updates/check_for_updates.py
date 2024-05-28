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

    Additionally, if the EXPORT_JSON and EXPORT_CSV environment variables are set then 
    the output object will be exported to a GCP Storage bucket, in JSON and CSV
    format, respectively.

    Parameters
    ==========
    None
    
    Returns
    =======
    :success_message/error_message: json
       jsonified response indicating whether the application has completed successfully 
       or an error has arose during execution.
    :success_code/error_code: int
        successful or erroneous status code, 400 or 200, respectively. 
    """
    #object containing current iso3166-2 updates after month range date filter applied
    latest_iso3166_updates_after_date_filter = {}
    
    #month range to get latest updates from, default of 12 months used if env var empty or not a valid int
    if ((os.environ.get("MONTH_RANGE") is None) or (os.environ.get("MONTH_RANGE") == "") or str(os.environ.get("MONTH_RANGE")).isdigit()):
        months = 12
    else:
        months = int(os.environ.get("MONTH_RANGE")) #convert to int - months should be a whole number

    #get create_issue bool env var which determines if GitHub Issues are created each time new/missing ISO 3166 updates are found
    if (os.environ.get("CREATE_ISSUE") is None or os.environ.get("CREATE_ISSUE") == ""):
        create_issue = False
    else:
        create_issue = int(os.environ.get("CREATE_ISSUE")) #env var should be 0 or 1

    #get export env var which determines if new updates data object is exported to GCP storage bucket
    if (os.environ.get("EXPORT_JSON") is None or os.environ.get("EXPORT_JSON") == ""):
        export = False
    else:
        export = int(os.environ.get("EXPORT_JSON")) #env var should be 0 or 1

    #get bucket name and blob name env vars for exporting object to GCP bucket, it can be empty/None if export env var is set to False
    bucket_name = os.environ.get("BUCKET_NAME")
    blob_name = os.environ.get("BLOB_NAME")

    #get latest date that iso3166-updates.json object was updated on the repo, using github client and library 
    github_client = Github()
    repo = github_client.get_repo("amckenna41/iso3166-updates")
    commits = repo.get_commits(path='iso3166-updates.json')
    if (commits.totalCount):
        latest_commit_date = datetime.strptime(commits[0].commit.committer.date.strftime('%Y-%m-%d'), "%Y-%m-%d")

    #date difference between current date and date object was last updated, print out difference in months
    date_diff = relativedelta(current_datetime, latest_commit_date)
    print(f"The iso3166-updates.json object was last updated {date_diff.months} months ago on: {str(latest_commit_date)}.")
    
    #call get_updates function to scrape all latest country updates from data sources
    latest_iso3166_updates, latest_iso3166_updates_csv = get_updates(export_json=False, export_csv=True, verbose=True)
    
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

    #create Github Issue of updates if new updates were found and env var is set to true, the successful or erroneous status code is returned
    if (bool(create_issue) and updates_found):
        create_github_issue_success_code = create_github_issue(date_filtered_updates, missing_filtered_updates, months) 

    #export object to bucket if new updates were found and env var is set to true, the successful or erroneous status code is returned
    if (export and updates_found):    
        export_to_bucket_success_code = export_to_bucket(latest_iso3166_updates, latest_iso3166_updates_csv)

    #set success message returned from function if updates have been found, message updated depending on success or failure of export and create issue functionalities
    if (updates_found):
        #set success messsage if export and create issue functionality enabled depending on success or failure of functions
        if (bool(create_issue) and export):
            if (create_github_issue_success_code != -1 and export_to_bucket_success_code != -1):
                success_message["message"] = f"New ISO 3166 updates found and successfully exported to bucket {bucket_name} and GitHub Issues created."
            elif (create_github_issue_success_code != -1 and export_to_bucket_success_code == -1):
                success_message["message"] = f"New ISO 3166 updates found and GitHub Issues created. There was an error exporting to the GCP storage bucket, double check the BUCKET_NAME and BLOB_NAME environment variables are set and correct, and that the bucket exists."
            elif (create_github_issue_success_code == -1 and export_to_bucket_success_code != -1):
                success_message["message"] = f"New ISO 3166 updates found and successfully exported to bucket {bucket_name}. There was an error creating the GitHub Issues, double check the required environment variables are set and correct."
            else:
                success_message["message"] = f"New ISO 3166 updates found but there was an error exporting to the GCP storage bucket, double check the required environment variables for both functionalities are set and correct."
        #set success message if create issue functionality enabled
        elif (bool(create_issue)):
            if (create_github_issue_success_code != -1):
                success_message["message"] = "New ISO 3166 updates found and GitHub Issues created."
            else:
                success_message["message"] = "New ISO 3166 updates found but there was an error creating the GitHub Issues, double check the required environment variables for are set and correct."
        #set success message if export functionality enabled
        elif (export):
            if (export_to_bucket_success_code != -1):
                success_message["message"] = f"New ISO 3166 updates found and successfully exported to bucket {bucket_name}."
            else:
                success_message["message"] = "New ISO 3166 updates found, but there was an error exporting to the GCP storage bucket, double check the BUCKET_NAME ({bucket_name}) and BLOB_NAME ({blob_name}) environment variables are set and correct, and that the bucket exists."
    #if no updates found but export functionality still enabled, export to bucket and return success message 
    else:
        if (export):
            export_to_bucket_success_code = export_to_bucket(latest_iso3166_updates, latest_iso3166_updates_csv)
            if (export_to_bucket_success_code != -1):
                success_message["message"] = f"ISO 3166 updates object successfully exported to bucket: {bucket_name}."
            else:
                success_message["message"] = "There was an error exporting to the GCP storage bucket, double check the BUCKET_NAME ({bucket_name}) and BLOB_NAME ({blob_name}) environment variables are set and correct, and that the bucket exists."
        #set success message when no updates found and export functionality not enabled
        else:
            success_message["message"] = f"No new ISO 3166 updates found, object not exported to bucket."

    return jsonify(success_message), 200

def update_json(latest_iso3166_updates: dict, latest_iso3166_updates_after_date_filter: dict) -> tuple[bool, dict, dict]:
    """
    The most recent ISO 3166 changes object that was exported is compared 
    to the object in the current version of the iso3166-updates software. 
    Any differences between the objects are tracked in another separate 
    object and returned from the function. Additionally, any missing data, 
    regardless of date range is similarly tracked and returned from the 
    function. 

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
    :individual_updates_json: dicts
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
    
def create_github_issue(latest_iso3166_updates_after_date_filter: dict, missing_filtered_updates: dict, month_range: int) -> int:
    """
    Create a GitHub issue on the iso3166-2, iso3166-updates and iso3166-flag-icons 
    repository, using the GitHub api, if any updates/changes were found in the 
    ISO 3166 that aren't in the current object. The Issue will be formatted and 
    tabulated in a way to clearly outline any of the updates/changes to be made 
    to the JSONs in the iso3166-2, iso3166-updates and iso3166-flag-icons repos. 

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
        return code to indicate if the create GitHub issue functionality was successfully 
        created or there was an error during execution.

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
            body += "<table><tr><th>Date Issued</th><th>Code/Subdivision Change</th><th>Description of Change</th><th>Edition/Newsletter</th></tr>"

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
            body += "<table><tr><th>Date Issued</th><th>Code/Subdivision Change</th><th>Description of Change</th><th>Edition/Newsletter</th></tr>"

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
               "Authorization": "token " + os.environ.get("GITHUB_API_TOKEN")}
    github_repos = os.environ.get("GITHUB_REPOS")
    
    #make post request to create issue in repos using GitHub api url and headers, if github_repo env vars set
    if not (github_repos is None and github_repos != ""): 
        #split into list of repos 
        github_repos = github_repos.replace(' ', '').split(';')

        #iterate over each repo listed in env var, making post request with issue_json data
        for repo in github_repos:
            
            #get url of repo and make post request
            issue_url = "https://api.github.com/repos/" + os.environ.get("GITHUB_OWNER") + "/" + repo + "/issues"
            github_request = requests.post(issue_url, data=json.dumps(issue_json), headers=headers)    

            #print error message if success status code not returned            
            if (github_request.status_code != 200):  
                if (github_request.status_code == 401):
                    print(f"Authorisation issue when creating GitHub Issue in repository {repo}, could be an issue with the GitHub PAT.")
                else:
                    print(f"Issue when creating GitHub Issue in repository {repo}, got status code {github_request.status_code}.")
                return -1
    return 0

def export_to_bucket(latest_iso3166_updates: dict, latest_iso3166_updates_csv: dict) -> int:
    """
    If the export environment variable is set and changes are found that 
    aren't present in the existing repo object, export the new object
    to the specified GCP bucket. This can then be downloaded and 
    incorporated into the software. 

    Parameters
    ==========
    :latest_iso3166_updates: dict
        dict object with all listed iso3166-2 updates, without date filter
        applied.       
    :latest_iso3166_updates_csv: dict 
        dict object with all listed iso3166-2 updates, without date filter
        applied, but with additional country code column for CSV export.

    Returns
    =======
    :success_code: int
        return code to indicate if the export to bucket functionality was successfully 
        created or there was an error during execution.
    """
    #initialise storage client
    storage_client = storage.Client()
    try:
        #create a bucket object for the bucket, raise error if bucket not found
        bucket = storage_client.get_bucket(os.environ.get("BUCKET_NAME"))
    except exceptions.NotFound:
        print(f"Error retrieving updates data json storage bucket: {os.environ.get('BUCKET_NAME')}.")
        return -1

    #use blob name specified by env var if applicable, else use default name
    if (os.environ.get("BLOB_NAME") is None or os.environ.get("BLOB_NAME") != ""):
        blob_name = "iso3166-updates.json"
    else:
        blob_name = os.environ.get("BLOB_NAME")

    #create a blob object from the blob name
    blob = bucket.blob(blob_name)
    
    #if blob of updates object is in bucket, create a copy of it and store in arhcive folder
    if  (blob.exists()):

        #move current updates json in bucket, if applicable, to an archive folder, append datetime to it
        if (os.environ.get("ARCHIVE_FOLDER") is None or os.environ.get("ARCHIVE_FOLDER") == ""):
            os.environ["ARCHIVE_FOLDER"] = "archive_iso3166_updates"
        
        #create temp archives folder 
        os.makedirs(os.environ.get("ARCHIVE_FOLDER"))

        archive_filepath = os.path.join(os.environ.get("ARCHIVE_FOLDER"), os.path.splitext(blob_name)[0] + "_" + str(current_datetime.strftime('%Y-%m-%d')) + ".json")

        #export updated json to temp folder
        with open(archive_filepath, 'w', encoding='utf-8') as output_json:
            json.dump(json.loads(blob.download_as_string(client=None)), output_json, ensure_ascii=False, indent=4)

        #create blob for archive updates json 
        archive_blob = bucket.blob(archive_filepath)
        
        #upload old updates json to archive folder 
        archive_blob.upload_from_filename(archive_filepath)

    #temp path for exported json
    tmp_updated_json_path = os.path.join("/tmp", blob_name)
    
    #export updated json to temp folder
    with open(tmp_updated_json_path, 'w', encoding='utf-8') as output_json:
        json.dump(latest_iso3166_updates, output_json, ensure_ascii=False, indent=4)

    #upload new updated json using gcp sdk, replacing current updates json 
    blob.upload_from_filename(tmp_updated_json_path)

    #EXPORT_CSV env var determines if the object is also exported to a CSV on the bucket, true by default
    if (os.environ.get("EXPORT_CSV") and not latest_iso3166_updates_csv.empty):
        
        csv_blob_name = os.path.splitext(blob_name)[0] + ".csv"

        #create a blob object from the blob name
        blob = bucket.blob(csv_blob_name)

        #temp path for exported csv
        tmp_updated_csv_path = os.path.join("/tmp", csv_blob_name)

        #export updates object to separate csv files
        latest_iso3166_updates_csv.to_csv(tmp_updated_csv_path, index=False)

        #upload new updated json using gcp sdk, replacing current updates json 
        blob.upload_from_filename(tmp_updated_csv_path)

    return 0

# def push_to_repo(latest_iso3166_updates: dict, version: float, commit_message: str):
#     """
    
#     """    
#     github_api_path = f"https://api.github.com/repos/{os.environ.get("GITHUB_OWNER")}/iso3166-updates/branches/master" 
#     # https://api.github.com/repos/amckenna41/iso3166-updates/contents/iso3166-updates.json
#     # https://stackoverflow.com/questions/11801983/how-to-create-a-commit-and-push-into-repo-with-github-api-v3/63461333#63461333

#     gh = Github(os.environ.get("GITHUB_API_TOKEN"))

#     # ** add validation for iso3166-updates.json 
#       ** need to update pyproject.toml as well 
#     #create GitHub repo object
#     remote_repo = gh.get_repo("amckenna41/iso3166-updates")

#     # Update files:
#     #   data/example-04/latest_datetime_01.txt
#     #   data/example-04/latest_datetime_02.txt
#     # with the current date.

#     file_to_update_01 = "data/example-04/latest_datetime_01.txt"
#     file_to_update_02 = "data/example-04/latest_datetime_02.txt"
#     blob_name = "iso3166-updates.json"

#     #temp path for exported json
#     tmp_updated_json_path = os.path.join("/tmp", blob_name)

#     #export updated json to temp folder
#     with open(tmp_updated_json_path, 'w', encoding='utf-8') as output_json:
#         json.dump(latest_iso3166_updates, output_json, ensure_ascii=False, indent=4)

#     # #temp path for exported json
#     # tmp_updated_json_path = os.path.join("/tmp", blob_name)

#     now = datetime.datetime.now()

#     blob_name_content = str(now)

#     blob1 = remote_repo.create_git_blob(blob_name_content, "utf-8")
#     element1 = Github.InputGitTreeElement(
#         path=file_to_update_01, mode='100644', type='blob', sha=blob1.sha)

#     commit_message = f'Example 04: update datetime to {now}'

#     branch_sha = remote_repo.get_branch("master").commit.sha
   
#     base_tree = remote_repo.get_git_tree(sha=branch_sha)
 
#     tree = remote_repo.create_git_tree([element1], base_tree)

#     parent = remote_repo.get_git_commit(sha=branch_sha)

#     commit = remote_repo.create_git_commit(commit_message, tree, [parent])

#     branch_refs = remote_repo.get_git_ref(f'heads/"master')

#     branch_refs.edit(sha=commit.sha)