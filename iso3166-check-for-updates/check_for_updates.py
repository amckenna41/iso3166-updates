import iso3166_updates
import iso3166
import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
import smtplib
from google.cloud import storage

def check_iso3166_updates_main(request):
    """
    Google Cloud Function that checks for any updates within specified date range
    for the iso3166-updates API. It uses the accompnnying iso3166-updates Python
    software package to web scrape all country's ISO3166-2 wiki's checking for 
    any updates in a date range. 
    If any updates are found then an email is sent to a user/list of users using
    the smtplib library conveyiny these updates. The user can then use these
    updates to make any changes to their applications that use the ISO3166-2. 

    Parameters
    ----------
    : request : (flask.Request)
        HTTP request object.
    
    Returns
    -------
    : current_iso3166_updates : json
        json containing any iso3166 updates for selected country/alpha2 ISO code
        within specified date range.
    """
    #default month cutoff to check for updates
    months = 12

    #parse months var from input params, if applicable
    request_json = request.get_json()

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

    #sort codes in alphabetical order
    alpha2_codes.sort()
    alpha2_codes = [code.upper() for code in alpha2_codes]

    #call iso3166_updates get_updates function to scrape all updates from country wikis
    iso3166_updates.get_updates(alpha2_codes, export_json_filename="test-iso3166-updates", 
        export_folder="/tmp", export_json=True, export_csv=False)

    #load exported updates json
    with open(os.path.join("/tmp", "test-iso3166-updates.json")) as input_json:
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
    
    def send_email(iso3166_updates_json):
        """
        Send email with parsed updates from the iso3166-2 updates json to 
        and from emails specified in env vars of Cloud Function. 

        Parameters
        ----------
        : iso3166_updates_json : json
            json object with all listed iso3166-2 updates in specified month 
            range. 

        Returns
        -------
        None
        """
        #get email variables from Google Func env vars
        _to_email = os.environ['TO_MAIL']
        _from_email = os.environ['FROM_MAIL']
        _password = os.environ['PASSWORD']

        #email subject 
        subject = "ISO3166-2 Updates - " + str(current_datetime.strftime('%d-%m-%Y'))        
        plain_text = ""

        #body of email in html 
        body = """\
            <html>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/flag-icon-css/4.1.5/css/flag-icons.min.css" rel="stylesheet" />
            <body>
                <h1>ISO3166-2 Updates</h1>
            """

        #get total sum of updates for all countrys in json
        total_updates = sum([len(iso3166_updates_json[code]) for code in iso3166_updates_json])
        total_countries = len(iso3166_updates_json)

        #display number of updates for countrys and the date period
        body += "<h3>" + str(total_updates) + " updates found for " + str(total_countries) + " countries between period of " + \
            str((current_datetime + relativedelta(months=-1)).strftime('%d-%m-%Y')) + " to " + str(current_datetime.strftime('%d-%m-%Y')) + ".</h3>" 

        #iterate over updates in json, append to email body
        for code in list(iso3166_updates_json.keys()):
            
            # flag_icon_attr = '<span class="flag-icon flag-icon-' + code.lower() + '" style="width: 100%;" </span>'
            #header displaying current country name and code
            body += "<h2><u>" + "Country - " + iso3166.countries_by_alpha2[code].name + " (" + code + ")" + ":</u></h2>"
            # body += "<span>" + "Country - " + iso3166.countries_by_alpha2[code].name + " (" + code + ")" + flag_icon_attr + "</span>"  

            #get plaintext of country name and code
            plain_text += "Country - " + iso3166.countries_by_alpha2[code].name + code + "\n"

            #convert json object to str, so it can be appended to body
            temp = json.dumps(iso3166_updates_json[code])

            #append country updates to body within p tag
            body += "<p>"

            row_count = 0
            #iterate over all update rows for each country in object, appending to html body
            for row in iso3166_updates_json[code]:
                
                #increment row count which numbers each country's updates if more than 1
                if (len(iso3166_updates_json[code]) > 1):
                    row_count = row_count + 1
                    body += "<h4>" + str(row_count) + ".)" + "</h4>"

                #output all row field values 
                for key, val in row.items():
                    body += "<h4>" + str(key) + ": " + str(val)

                #close h4 and p tag
                body += "</h4></p>"
        
        #close body and html tags
        body += "</body></html>"

        #create instance of MIME (Multipurpose Internet Mail Extensions (MIME)) object,
        #   an Internet standard that extends the format of email to support: Text in 
        #   character sets other than ASCII, initilaise subject and to and from 
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = _from_email
        msg['To'] = _to_email

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(plain_text, 'plain')
        part2 = MIMEText(body, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        #create ssl context object
        context = ssl.create_default_context()

        #send email using gmail server (port 465) and smtp library 
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(_from_email, _password)
            # smtp.sendmail(_from_email, _to_email, em.as_string())
            smtp.sendmail(_from_email, _to_email, msg.as_string())

    def update_json(iso3166_updates_json):
        """
        Parameters
        ----------
        : iso3166_updates_json : json
            json object with all listed iso3166-2 updates in specified month 
            range. 

        Returns
        -------
        None
        """
        # Initialise a client
        storage_client = storage.Client()
        # Create a bucket object for our bucket
        bucket = storage_client.get_bucket("iso3166-updates")
        # Create a blob object from the filepath
        blob = bucket.blob("iso3166-updates.json")    

        #download iso3166-updates.json file from storage bucket 
        previous_updates_data = json.loads(blob.download_as_string(client=None))
        
        #set new json object to original one imported from gcp storage
        updated_json = previous_updates_data

        #iterate over all updates in json, if update/row not found in original json
        #...pulled from GCP storage, append to new updated_json object
        for code in iso3166_updates_json:   
            for update in iso3166_updates_json[code]:
                if not (update in previous_updates_data[code]):
                    updated_json[code].append(update)

        #convert json objects into str
        previous_updates_data_str = json.dumps(previous_updates_data, sort_keys=True)
        updated_json_str = json.dumps(updated_json, sort_keys=True)

        #if new updates json 
        if (previous_updates_data_str != updated_json_str):

            #temp path for exported json
            tmp_updated_json_path = os.path.join("/tmp", 'iso3166-3.json')
            
            #export updated json to temp folder
            with open(tmp_updated_json_path, 'w', encoding='utf-8') as output_json:
                json.dump(updated_json, output_json, ensure_ascii=False, indent=4)

            blob = bucket.blob('iso3166-3.json')
            #upload new updated json using gcp sdk 
            blob.upload_from_filename(tmp_updated_json_path)

    return_message = ""

    #if update object not empty - there are updates - then call send email function
    if (current_iso3166_updates != {}):
        send_email(current_iso3166_updates)
        update_json(current_iso3166_updates)
        return_message = "ISO3166-2 updates found."
    else:
        return_message = "No ISO3166-2 updates found."

    return return_message
#1.) https://cloud.google.com/functions/docs/securing/authenticating#functions-bearer-token-example-python
#2.) curl -H "Authorization: bearer $(gcloud auth print-identity-token)" https://us-central1-iso3166-updates.cloudfunctions.net/check-for-iso3166-updates
#3.)curl -m 460 -X POST https://us-central1-iso3166-updates.cloudfunctions.net/check-for-iso3166-updates \
# -H "Authorization: bearer $(gcloud auth print-identity-token)" \
# -H "Content-Type: application/json" \
# -d '{}'

