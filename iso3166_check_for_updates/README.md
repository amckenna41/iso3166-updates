# ISO 3166 Check for Updates Microservice Application ✅

<!-- [![check-for-updates](https://github.com/amckenna41/iso3166-updates/workflows/Check%20for%20ISO3166%20Updates/badge.svg)](https://github.com/amckenna41/iso3166-updates/actions?query=workflowCheck%20for%20ISO3166%20Updates) -->

This custom-built microservice webapp is periodically initialised and called automatically using a CRON scheduler. The app uses the `iso3166-updates` Python software to pull all the latest updates from all of the ISO 3166-2 data sources to check for the latest updates within a certain period e.g the past 6-12 months (this month range is used as the ISO usually publishes their updates at the end of the year with occasional mid-year updates). The functionality compares the generated output with that of the updates json in the current version of the `iso3166-updates` software. Ultimately, this function ensures that the software and associated APIs are up-to-date with the latest ISO 3166-2 information for all countries/territories/subdivisions etc. The app is built using a custom Docker container that is run on the serverless GCP Cloud Run service. 

There is also functionality implemented that automatically tabulates and formats all of the required updates in a GitHub Issue on the [iso3166-updates](https://github.com/amckenna41/iso3166-updates), [iso3166-2](https://github.com/amckenna41/iso3166-2) and [iso3166-flag-icons](https://github.com/amckenna41/iso3166-flag-icons) repositories. Each of these repos require the latest and most accurate ISO 3166-2 data. The creation of these Issues will notify the repository owner that changes are outstanding that need to be implemented into the JSONs of the [iso3166-updates](https://github.com/amckenna41/iso3166-updates), [iso3166-2](https://github.com/amckenna41/iso3166-2) and [iso3166-flag-icons](https://github.com/amckenna41/iso3166-flag-icons) repos. 

Currently, this script takes approximately 25 minutes to execute. 

Note, due to this microservice only being called periodically, the Cloud Run app is created and then deleted after its execution to save on resources.

GCP Cloud Architecture 
----------------------

<p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/refs/heads/main/iso3166_check_for_updates/gcp_architecture.png" alt="gcp_arch" height="500" width="750"/>
</p>

Requirements
------------
* [python][python] >= 3.9
* [iso3166-updates][iso3166-updates] >= 1.8.2
* [pandas][pandas] >= 1.4.3
* [requests][requests] >= 2.28.1
* [beautifulsoup4][beautifulsoup4] >= 4.11.1
* [iso3166][iso3166] >= 2.1.1
* [google-auth][google-auth] >= 2.17.3
* [google-cloud-storage][google-cloud-storage] >= 2.8.0
* [google-api-python-client][google-api-python-client] >= 2.86.0
* [emoji-country-flag][emoji-country-flag] == 1.3.0
* [selenium][selenium] >= 4.10.0
* [flask][flask] >= 2.3.2
* [gunicorn][gunicorn] >= 23.0.0
* [lxml][lxml] >=  4.9.3
* [tqdm][tqdm] >= 4.64.0
* [PyGithub][PyGithub] >= 2.3.0
* [python-dateutil] >= 2.9.0.post0
* [fake_useragent][fake_useragent] >= 1.5.0

Create check-for-updates microservice
-------------------------------------

**Build Docker container using Dockerfile and Python image:**
```bash
docker build -t {CONTAINER_NAME} .
```

**Submit Docker container to GCP container registry:**
```bash
gcloud builds submit --tag gcr.io/iso3166-updates/{CONTAINER_NAME}
```

**Build and deploy Cloud Run application using Docker container (need to set the env vars):**
```bash
gcloud beta run deploy {APP_NAME} --image gcr.io/iso3166-updates/{CONTAINER_NAME} \
  --region {REGION_NAME} --platform managed --memory 1024Mi --timeout 2700 --service-account {SERVICE_ACCOUNT} \
  --update-env-vars MONTH_RANGE="",BUCKET_NAME="",BLOB_NAME="",EXPORT_JSON=1,EXPORT_CSV=1,EXPORT_XML=1,CREATE_ISSUE=1,GITHUB_OWNER="",GITHUB_REPOS="",GITHUB_API_TOKEN="",ALPHA_CODES_RANGE=""

#MONTH_RANGE: number of months from script execution to get updates from (default=6). 
#BUCKET_NAME: name of the GCP storage bucket to upload the exported updates data to.
#BLOB_NAME: name of the file/blob of the exported data to be uploaded to the bucket.
#EXPORT_JSON: set to 1 to export latest ISO 3166 updates JSON to storage bucket (default=1).
#EXPORT_CSV: set to 1 to export latest ISO 3166 updates in CSV format to storage bucket (default=1).
#EXPORT_XML: set to 1 to export latest ISO 3166 updates in XML format to storage bucket (default=1).
#CREATE_ISSUE: set to 1 to create Issues on the GitHub repos outlining the latest ISO 3166 updates (default=0).
#GITHUB_OWNER: owner of GitHub repos.
#GITHUB_REPOS: list of GitHub repos where to create Issue outlining the latest ISO 3166 updates.
#GITHUB_API_TOKEN: GitHub API token for creating an Issue on the repos.
#ALPHA_CODES_RANGE: subset/range of alpha country codes to get updates data for, primarily used for testing.
```

**Run Cloud Run application/script:**
```bash
curl "$(gcloud run services describe {APP_NAME} --region {REGION_NAME} --format 'value(status.url)')"
```

**Delete Cloud Run application:**
```bash
gcloud run services delete {APP_NAME} --region {REGION_NAME}
```

**Combining the above all into one command:**
```bash
docker build -t {CONTAINER_NAME} . && gcloud builds submit --tag gcr.io/{APP_NAME}/{CONTAINER_NAME} && \
  yes | gcloud beta run deploy {APP_NAME} --image gcr.io/iso3166-updates/{CONTAINER_NAME} \
    --region {REGION_NAME} --platform managed --memory 1024Mi --timeout 2700 --service-account {SERVICE_ACCOUNT} \
    --update-env-vars MONTH_RANGE="",BUCKET_NAME="",BLOB_NAME="",EXPORT_JSON=1,EXPORT_CSV=1,EXPORT_XML=1,CREATE_ISSUE=1,GITHUB_OWNER="",GITHUB_REPOS="",GITHUB_API_TOKEN="",ALPHA_CODES_RANGE="" && curl "$(gcloud run services describe {APP_NAME} --region {REGION_NAME} --format 'value(status.url)')"

gcloud run services delete {APP_NAME} --region {REGION_NAME}
```

<!-- 
https://dev.to/googlecloud/using-headless-chrome-with-cloud-run-3fdp
https://www.youtube.com/watch?v=mOJiWrjFVKY
https://www.youtube.com/watch?v=LxHiCZCKwa8
https://stackoverflow.com/questions/53073411/selenium-webdriverexceptionchrome-failed-to-start-crashed-as-google-chrome-is 
-->

[python]: https://www.python.org/downloads/release/python-360/
[iso3166-updates]: https://github.com/amckenna41/iso3166-updates
[pandas]: https://pandas.pydata.org/
[requests]: https://requests.readthedocs.io/
[beautifulsoup4]: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
[google-auth]: https://cloud.google.com/python/docs/reference
[google-cloud-storage]: https://cloud.google.com/python/docs/reference
[google-api-python-client]: https://cloud.google.com/python/docs/reference
[flask]: https://flask.palletsprojects.com/en/2.3.x/
[emoji-country-flag]: https://pypi.org/project/emoji-country-flag/
[gunicorn]: https://pypi.org/project/gunicorn/
[selenium]: https://selenium-python.readthedocs.io/index.html
[lxml]: https://lxml.de/
[iso3166]: https://github.com/deactivated/python-iso3166
[tqdm]: https://github.com/tqdm/tqdm
[PyGithub]: https://github.com/PyGithub/PyGithub
[python-dateutil]: https://pypi.org/project/python-dateutil/
[fake_useragent]: https://pypi.org/project/fake-useragent/