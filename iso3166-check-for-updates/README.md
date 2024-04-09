# ISO 3166 Check for Updates Microservice Application

<!-- [![check-for-updates](https://github.com/amckenna41/iso3166-updates/workflows/Check%20for%20ISO3166%20Updates/badge.svg)](https://github.com/amckenna41/iso3166-updates/actions?query=workflowCheck%20for%20ISO3166%20Updates) -->

This custom-built microservice webapp is periodically initialised and called (usually every 3-6 months) automatically using a CRON scheduler. The app uses the `iso3166-updates` Python software to pull all the latest updates from all of the ISO 3166-2 data sources to check for the latest updates within a certain period e.g the past 6-12 months (this month range is used as the ISO usually publishes their updates at the end of the year with occasional mid-year updates). The functionality compares the generated output with that of the updates json in the current version of the `iso3166-updates` software. Ultimately, this function ensures that the software and associated APIs are up-to-date with the latest ISO 3166-2 information for all countries/territories/subdivisions etc. The app is built using a custom Docker container that is run on the serverless GCP Cloud Run service. 

There is also functionality implemented that automatically tabulates and formats all of the required updates in a GitHub Issue on the [iso3166-updates](https://github.com/amckenna41/iso3166-updates), [iso3166-2](https://github.com/amckenna41/iso3166-2) and [iso3166-flag-icons](https://github.com/amckenna41/iso3166-flag-icons) repositories. Each of these repos require the latest and most accurate ISO 3166-2 data. The creation of these Issues will notify the repository owner that changes are outstanding that need to be implemented into the JSONs of the [iso3166-updates](https://github.com/amckenna41/iso3166-updates), [iso3166-2](https://github.com/amckenna41/iso3166-2) and [iso3166-flag-icons](https://github.com/amckenna41/iso3166-flag-icons) repos. 

Currently, this script takes approximately 25 minutes to execute. 

Note, due to this microservice only being called periodically, the Cloud Run app is created and then deleted after its execution to save on money and resources.

GCP Cloud Architecture 
----------------------

<p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166-updates-api/gcp_architecture.png?raw=true" alt="gcp_arch" height="500" width="750"/>
</p>

Requirements
------------
* [python][python] >= 3.8
* [iso3166-updates][iso3166-updates] >= 1.3.0
* [pandas][pandas] >= 1.4.3
* [numpy][numpy] >= 1.23.2
* [requests][requests] >= 2.28.1
* [beautifulsoup4][beautifulsoup4] >= 4.11.1
* [iso3166][iso3166] >= 2.1.1
* [google-auth][google-auth] >= 2.17.3
* [google-cloud-storage][google-cloud-storage] >= 2.8.0
* [google-api-python-client][google-api-python-client] >= 2.86.0
* [emoji-country-flag][emoji-country-flag] == 1.3.0
* [selenium][selenium] >= 4.10.0
* [flask][flask] >= 2.3.2
* [gunicorn][gunicorn] >= 21.2.0
* [lxml][lxml] >=  4.9.3
* [tqdm][tqdm] >= 4.64.0
* [PyGithub][PyGithub] >= 2.3.0

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
  --update-env-vars GITHUB_OWNER="",GITHUB_REPOS="",GITHUB_API_TOKEN="",MONTH_RANGE="",CREATE_ISSUE=1

#GITHUB_OWNER: owner of GitHub repos.
#GITHUB_REPOS: list of GitHub repos where to create Issue outlining the latest ISO 3166 updates.
#GITHUB_API_TOKEN: GitHub API token for creating an Issue on the repos.
#MONTH_RANGE: number of months from script execution to get updates from. 
#CREATE_ISSUE: set to 1 to create Issues on the GitHub repos outlining the latest ISO 3166 updates.
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
docker build -t {CONTAINER_NAME} . && gcloud builds submit --tag gcr.io/iso3166-updates/{CONTAINER_NAME} && \
  yes | gcloud beta run deploy {APP_NAME} --image gcr.io/iso3166-updates/{CONTAINER_NAME} \
    --region {REGION_NAME} --platform managed --memory 1024Mi --timeout 2700 --service-account {SERVICE_ACCOUNT} \
    --update-env-vars GITHUB_OWNER="",GITHUB_REPOS="",GITHUB_API_TOKEN="",MONTH_RANGE="",CREATE_ISSUE=1 && \
    curl "$(gcloud run services describe {APP_NAME} --region {REGION_NAME} --format 'value(status.url)')"

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
[numpy]: https://numpy.org/
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