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
import xml.etree.ElementTree as ET
from xml.dom import minidom
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

#instance of Updates class to get all updates in current software version
current_iso3166_updates = Updates()

@app.route("/")
def check_for_updates_main() -> tuple[dict, int]:
    """
    Google Cloud Run main entry script that checks for any latest/missing ISO 3166-2 
    updates data within specified date range for the iso3166-updates software & API. 
    It uses the get_all_iso3166_updates.py script to web scrape all country's' ISO 
    3166-2 updates data from the various data sources (wiki and ISO), checking for 
    any updates in a date range. This date range is normally set to the past 6-12 
    months, as the ISO 3166 is usually updated annually, normally at the end of the 
    year as well as periodic updates published throughout the year. The Cloud run 
    app is built using a custom docker container that contains all the required 
    dependencies and binaries required to run the full export pipeline script. 
    
    If any updates are found that are not already present in the JSON object within 
    the current version of the iso3166-updates software package then a GitHub Issue 
    is automatically created that tabulates and formats all the latest data. This
    Issue is usually created on the iso3166-updates and iso3166-2 repos, the latter 
    is an additional custom-built software package that stores all the latest subdivision 
    info and data relating to the ISO 3166-2 standard. A similar Issue will also be raised 
    in the iso3166-flag-icons repo which is another custom repo that stores all the flag 
    icons of all countries and subdivisions in the ISO 3166-1 and ISO 3166-2. Additionally, 
    if the relevant env vars are set the latest exported updates data will be exported to a 
    GCP Storage bucket.

    There are 11 env vars supported in the Cloud Run app, an overview of each is below:

    MONTH_RANGE: number of months from script execution to get updates from (default=6). 
    BUCKET_NAME: name of the GCP storage bucket to upload the exported updates data to.
    BLOB_NAME: name of the file/blob of the exported data to be uploaded to the bucket.
    EXPORT_JSON: set to 1 to export latest ISO 3166 updates JSON to storage bucket (default=1).
    EXPORT_CSV: set to 1 to export latest ISO 3166 updates in CSV format to storage bucket (default=1).
    EXPORT_XML: set to 1 to export latest ISO 3166 updates in XML format to storage bucket (default=1).
    CREATE_ISSUE: set to 1 to create Issues on the GitHub repos outlining the latest ISO 3166 updates (default=0).
    GITHUB_OWNER: owner of GitHub repos, required for create issue functionality.
    GITHUB_REPOS: list of GitHub repos where to create Issue outlining the latest ISO 3166 updates.
    GITHUB_API_TOKEN: GitHub API token for creating an Issue on the repos.
    ALPHA_CODES_RANGE: subset/range of alpha country codes to get updates data for, primarily used for testing.

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
    #object containing latest iso3166-2 updates after month range date filter applied
    latest_iso3166_updates_after_date_filter = {}
    
    #parse 7 of the main env vars required for normal app execution, validating them & assigning default values if they aren't set
    month_range, export_json, export_csv, export_xml, bucket_name, blob_name, create_issue = parse_env_vars()

    #get last date that iso3166-updates.json object was updated on the repo, using github client and library 
    github_client = Github()
    repo = github_client.get_repo("amckenna41/iso3166-updates")
    commits = repo.get_commits(path='iso3166-updates.json')
    if (commits.totalCount):
        latest_commit_date = datetime.strptime(commits[0].commit.committer.date.strftime('%Y-%m-%d'), "%Y-%m-%d")
    
    #date difference between current date and date object was last updated, print out difference in months
    date_diff = relativedelta(current_datetime, latest_commit_date)
    if (date_diff.months < 1):
        print(f"The iso3166-updates.json object was last updated less than a month ago on: {latest_commit_date.strftime('%Y-%m-%d')}.")
    elif (date_diff.months == 1):
        print(f"The iso3166-updates.json object was last updated {date_diff.months} month ago on: {latest_commit_date.strftime('%Y-%m-%d')}.")
    else:
        print(f"The iso3166-updates.json object was last updated {date_diff.months} months ago on: {latest_commit_date.strftime('%Y-%m-%d')}.")

    #call get_updates function to scrape all the latest country updates from data sources
    latest_iso3166_updates = get_iso3166_updates()

    print("latest_iso3166_updates here")
    print(latest_iso3166_updates)
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
                if (diff_months <= month_range):
                    latest_iso3166_updates_after_date_filter[alpha2].append(latest_iso3166_updates[alpha2][row])
            
        #if current alpha-2 has no rows in date range, remove from temp object
        if (latest_iso3166_updates_after_date_filter[alpha2] == []):
            latest_iso3166_updates_after_date_filter.pop(alpha2, None)

    #bool to track if any ISO 3166 updates found
    updates_found = False
        
    #if update object not empty (i.e there are changes/updates), call update_json which returns the object of missing/new updates in comparison to current object
    updates_found, date_filtered_updates, missing_filtered_updates = update_json(latest_iso3166_updates, latest_iso3166_updates_after_date_filter)

    #create Github Issue of updates if new updates were found and env var is set to true, the successful or erroneous status code is returned
    if (create_issue and updates_found):
        create_github_issue_success_code = create_github_issue(date_filtered_updates, missing_filtered_updates, month_range) 

    #set default export bucket var
    export_to_bucket_success_code = -1

    #export object to bucket if new updates were found and env var is set to true, the successful or erroneous status code is returned
    if ((export_json or export_csv or export_xml) and updates_found):    
        if (bucket_name is None or bucket_name == ""):
            error_message["message"] = f"Bucket name env var cannot be empty and must be a valid bucket."
            return jsonify(error_message), 400
        export_to_bucket_success_code = export_to_bucket(latest_iso3166_updates, bucket_name, blob_name, export_json, export_csv, export_xml)

    #set success message returned from function if updates have been found, message updated depending on success or failure of export and create issue functionalities
    if (updates_found):
        #set success message if export and create issue functionality enabled depending on success or failure of functions
        if (create_issue and (export_json or export_csv or export_xml)):
            if (create_github_issue_success_code != -1 and export_to_bucket_success_code != -1):
                success_message["message"] = f"New ISO 3166 updates found and successfully exported to bucket {bucket_name} and GitHub Issues created."
            elif (create_github_issue_success_code != -1 and export_to_bucket_success_code == -1):
                success_message["message"] = f"New ISO 3166 updates found and GitHub Issues created. There was an error exporting to the GCP storage bucket, double check the BUCKET_NAME ({bucket_name}) and BLOB_NAME ({blob_name}) environment variables are set and correct, and that the bucket exists."
            elif (create_github_issue_success_code == -1 and export_to_bucket_success_code != -1):
                success_message["message"] = f"New ISO 3166 updates found and successfully exported to bucket {bucket_name}. There was an error creating the GitHub Issues, double check the required environment variables are set and correct."
            else:
                success_message["message"] = f"New ISO 3166 updates found but there was an error exporting to the GCP storage bucket {bucket_name}, double check the required environment variables for both functionalities are set and correct."
        #set success message if create issue functionality enabled
        elif (create_issue):
            if (create_github_issue_success_code != -1):
                success_message["message"] = "New ISO 3166 updates found and GitHub Issues successfully created."
            else:
                success_message["message"] = "New ISO 3166 updates found but there was an error creating the GitHub Issues, double check the required environment variables (GITHUB_OWNER, GITHUB_REPOS, GITHUB_API_TOKEN) for are set and correct."
        #set success message if export functionality enabled
        elif (export_json or export_csv or export_xml):
            if (export_to_bucket_success_code != -1):
                success_message["message"] = f"New ISO 3166 updates found and successfully exported to bucket {bucket_name}."
            else:
                success_message["message"] = f"New ISO 3166 updates found, but there was an error exporting to the GCP storage bucket, double check the BUCKET_NAME ({bucket_name}) and BLOB_NAME ({blob_name}) environment variables are set and correct, and that the bucket exists."
    #if no updates found but export functionality still enabled, export to bucket and return success message 
    else:
        if (export_json or export_csv or export_xml):
            export_to_bucket_success_code = export_to_bucket(latest_iso3166_updates, bucket_name, blob_name, export_json, export_csv, export_xml)
            if (export_to_bucket_success_code != -1):
                success_message["message"] = f"ISO 3166 updates object successfully exported to bucket: {bucket_name}."
            else:
                success_message["message"] = f"There was an error exporting to the GCP storage bucket, double check the BUCKET_NAME ({bucket_name}) and BLOB_NAME ({blob_name}) environment variables are set and correct, and that the bucket exists."
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
    :latest_iso3166_updates_after_date_filter: dict
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
            if not (update in current_iso3166_updates.all[code]):
                updated_json[code].append(update)
                updates_found = True
                individual_updates_json[code].append(update)

        #updates are appended to end of updates json, need to reorder by Date Issued, most recent first
        updated_json[code] = sorted(updated_json[code], key=itemgetter('Date Issued'), reverse=True)

        #if current alpha-2 code has no updates associated with it, remove from temp object
        if (individual_updates_json[code] == []):
            individual_updates_json.pop(code, None)

    ## Appending any missing updates to object that were found, regardless of date range filter ##

    #iterate over all updates in json, if update/row not found in original json, append to new updated_json object, with date range filter applied
    for code in latest_iso3166_updates:   
        missing_individual_updates_json[code] = []
        for update in latest_iso3166_updates[code]:
            if not (update in current_iso3166_updates.all[code]):
                updated_json[code].append(update)
                updates_found = True
                missing_individual_updates_json[code].append(update)

        #updates are appended to end of updates json, need to reorder by Date Issued, most recent first
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

        #iterate over updates in json, output individual updates data
        for code in list(latest_iso3166_updates_after_date_filter.keys()):
            
            #header displaying current country name, code and flag icon using emoji-country-flag library
            body += "<h3>" + iso3166.countries_by_alpha2[code].name + " (" + code + ") " + flag.flag(code) + ":</h3>"

            #create table element to store output data
            body += "<table><tr><th>Date Issued</th><th>Change</th><th>Description of Change</th><th>Source</th></tr>"

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
            body += "<table><tr><th>Date Issued</th><th>Change</th><th>Description of Change</th><th>Source</th></tr>"

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

def export_to_bucket(latest_iso3166_updates: dict, bucket_name: str, blob_name: str, export_json: bool=True, 
    export_csv: bool=False, export_xml: bool=False) -> int:
    """
    If the export environment variable is set, upload the latest exported object
    to the specified GCP bucket. The object is exported if or if they are not any
    changes/updates found between the object. The newly and up-to-date object can 
    then be downloaded and incorporated into the software. 

    Parameters
    ==========
    :latest_iso3166_updates: dict
        dict object with all listed iso3166-2 updates, without date filter
        applied.       
    :bucket_name: str
        name of storage bucket to upload exported updates to.
    :blob_name: str
        name of file/blob for exported updates data.
    :export_json: bool (default=True)
        export all ISO 3166 updates into JSON format.
    :export_csv: bool (default=False)
        export all ISO 3166 updates into CSV format.
    :export_xml: bool (default=False)
        export all ISO 3166 updates into XML format.

    Returns
    =======
    :success_code: int
        return code to indicate if the export to bucket functionality was successful 
        or there was an error during execution.
    """
    #initialise storage client
    storage_client = storage.Client()
    try:
        #create a bucket object for the bucket, raise error if bucket not found
        bucket = storage_client.get_bucket(bucket_name)
    except exceptions.NotFound:
        print(f"Error retrieving updates data json storage bucket: {bucket_name}.")
        return -1

    #use blob name specified by env var if applicable, else use default name
    if (blob_name is None or blob_name == ""):
        blob_name = "iso3166-updates.json"
    else:
        blob_name = blob_name

    #create a blob object from the blob name
    blob = bucket.blob(blob_name)
    
    #if blob of updates object is in bucket, create a copy of it and store in archive folder
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

    #if exporting to CSV need to add country code column to identify each row's updates
    if (os.environ.get("EXPORT_CSV") and latest_iso3166_updates):
        #dataframe for csv export
        csv_iso3166_df = pd.DataFrame()

        #flatten the dictionary and add the "Country Code" column
        flattened_data = []
        for country_code, updates in latest_iso3166_updates.items():
            for update in updates:
                flattened_update = {**update, 'Country Code': country_code}
                flattened_data.append(flattened_update)

        #convert flattened data to DataFrame
        csv_iso3166_df = pd.DataFrame(flattened_data)

        #if empty dataframe, reset export_csv flag to False 
        if (csv_iso3166_df.empty):
            print("Updates data empty, CSV file not exported.")
            return 0
        else:
            #reindex columns in dataframe
            csv_iso3166_df = csv_iso3166_df[['Country Code', 'Change', 'Description of Change', 'Date Issued', 'Source']]

            #remove country code column if only one country's updates data exported, otherwise sort them alphabetically
            if (csv_iso3166_df["Country Code"].nunique() == 1):
                csv_iso3166_df.drop("Country Code", axis=1, inplace=True)
            else:
                csv_iso3166_df.sort_values('Country Code', inplace=True)

            #create a blob object from the blob name
            blob = bucket.blob(csv_blob_name)

            csv_blob_name = os.path.splitext(blob_name)[0] + ".csv"

            #temp path for exported csv
            tmp_updated_csv_path = os.path.join("/tmp", csv_blob_name)

            csv_iso3166_df.to_csv(tmp_updated_csv_path, index=False)

            #upload new updated json using gcp sdk, replacing current updates json 
            blob.upload_from_filename(tmp_updated_csv_path)            


    #EXPORT_XML env var determines if the object is to be exported to a XML on the bucket, true by default
    if (os.environ.get("EXPORT_XML") and latest_iso3166_updates):
        
        #create XML tree element 
        xml_root = ET.Element("ISO3166Updates")
        #iterate through country code and updates data, appending each as a child/sub element of the XML tree
        for country_code, updates in latest_iso3166_updates.items():
            country_elem = ET.SubElement(xml_root, "Country", code=country_code)
            for update in updates:
                update_elem = ET.SubElement(country_elem, "Update")
                for key, value in update.items():
                    child = ET.SubElement(update_elem, key.replace(" ", "_"))
                    child.text = str(value)

        #convert ElementTree to a pretty-printed XML string
        long_xml_string = ET.tostring(xml_root, 'utf-8')
        parsed_xml_elem = minidom.parseString(long_xml_string)
        pretty_xml_as_string = parsed_xml_elem.toprettyxml(indent="  ")
        
        xml_blob_name = os.path.splitext(blob_name)[0] + ".xml"

        #create a blob object from the blob name
        blob = bucket.blob(xml_blob_name)

        #temp path for exported xml
        tmp_updated_xml_path = os.path.join("/tmp", xml_blob_name)

        #write to file
        with open(tmp_updated_xml_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml_as_string)

        #upload xml to bucket
        blob.upload_from_filename(tmp_updated_xml_path)

    return 0

def parse_env_vars() -> tuple[int, bool, bool, bool, str, bool]:
    """
    Parse, validate and extract the relevant environment variables required for 
    the export app. If any of the env vars are invalid or not in the correct
    format then the default values will be used. 
    
    Parameters
    ==========
    None

    Returns
    =======
    month_range: int
        number of months to get the exported data from. 
    export_json: bool
        export the exported updates to JSON format. 
    export_csv: bool
        export the exported updates to CSV format.  
    export_xml: bool 
        export the exported updates to XML format. 
    bucket_name: str 
        name of GCP storage bucket.
    blob_name: str 
        name of blob for object in GCP storage bucket. 
    create_issue: bool
        whether to create the GitHub Issue or not.
    """
    #month range to get latest updates from, default of 12 months used if env var empty or not a valid int
    if ((os.environ.get("MONTH_RANGE") is None) or (os.environ.get("MONTH_RANGE") == "") or str(os.environ.get("MONTH_RANGE")).isdigit()):
        month_range = 12
    else:
        month_range = int(os.environ.get("MONTH_RANGE")) #convert to int - months should be a whole number

    #get export env var which determines if new updates data object JSON is exported to GCP storage bucket
    if (os.environ.get("EXPORT_JSON") is None or os.environ.get("EXPORT_JSON") == ""):
        export_json = True
    else:
        export_json = int(os.environ.get("EXPORT_JSON")) #env var should be 0 or 1

    #get export env var which determines if new updates data object CSV is exported to GCP storage bucket
    if (os.environ.get("EXPORT_CSV") is None or os.environ.get("EXPORT_CSV") == ""):
        export_csv = False
    else:
        export_csv = int(os.environ.get("EXPORT_CSV")) #env var should be 0 or 1

    #get export env var which determines if new updates data object XML is exported to GCP storage bucket
    if (os.environ.get("EXPORT_XML") is None or os.environ.get("EXPORT_XML") == ""):
        export_xml = False
    else:
        export_xml = int(os.environ.get("EXPORT_XML")) #env var should be 0 or 1

    #get bucket name env var for exporting object to GCP bucket, use a default bucket name if it is empty/None
    bucket_name = os.environ.get("BUCKET_NAME")
    if (bucket_name is None or bucket_name == ""):
        bucket_name = "iso3166-updates"

    #get blob name env var for exporting object to GCP bucket, use a default blob name with the date appended to it if it is empty/None
    blob_name = os.environ.get("BLOB_NAME")
    if (blob_name is None or blob_name == ""):
        blob_name = f"iso3166-updates-{current_datetime.strftime('%Y-%m-%d')}.json"

    #get create_issue bool env var which determines if GitHub Issues are created each time new/missing ISO 3166 updates are found
    if (os.environ.get("CREATE_ISSUE") is None or os.environ.get("CREATE_ISSUE") == ""):
        create_issue = False
    else:
        create_issue = bool(int(os.environ.get("CREATE_ISSUE"))) #env var should be 0 or 1

    return month_range, export_json, export_csv, export_xml, bucket_name, blob_name, create_issue

#run Cloud Run Flask app on port 8080
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Cloud Run provides this
    app.run(host="0.0.0.0", port=port)

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