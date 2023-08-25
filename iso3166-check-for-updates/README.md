# ISO 3166 Check for Updates Microservice Application

<!-- [![check-for-updates](https://github.com/amckenna41/iso3166-updates/workflows/Check%20for%20ISO3166%20Updates/badge.svg)](https://github.com/amckenna41/iso3166-updates/actions?query=workflowCheck%20for%20ISO3166%20Updates) -->

This custom-built microservice webapp is periodically initialised (usually every 3-6 months) automatically using a CRON sceduler. The app uses the `iso3166-updates` Python software to pull all latest updates from all of the ISO 3166-2 data sources to check for the latest updates within a certain period e.g the past 6-12 months (this month range is used as the ISO usually publishes their newsletter at the end of the year with occasional mid-year updates published). The functionality compares the generated output with that of the updates json in the Google Cloud Storage bucket and will replace this json to integrate the latest updates found such that the main API returns the latest data. Ultimately, this function ensures that the software and assoicated APIs are up-to-date with the latest ISO 3166-2 information for all countries/territories/subdivisions etc. The app is built using a custom Docker container that is run on the serverless GCP Cloud Run service. 

There is also functionality implemented that automatically tabulates and formats all of the required updates in a GitHub Issue on the [iso3166-updates](https://github.com/amckenna41/iso3166-updates), [iso3166-2](https://github.com/amckenna41/iso3166-2) and [iso3166-flag-icons](https://github.com/amckenna41/iso3166-flag-icons) repositories. Each of these repos require the latest and most accurate ISO 3166-2 data. The creation of these Issues will notify the repository owner that changes are outstanding that need to be implemented into the JSONs of the [iso3166-updates](https://github.com/amckenna41/iso3166-updates), [iso3166-2](https://github.com/amckenna41/iso3166-2) and [iso3166-flag-icons](https://github.com/amckenna41/iso3166-flag-icons) repos. 

Currently, this script takes approximately 25 minutes to execute. 

Note, due to this microservice only being called peiodically, the Cloud Run app is created and then deleted after its execution to save on money and resources.

GCP Cloud Architecture 
------------------------

<p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166-updates-api/gcp_architecture.png?raw=true" alt="gcp_arch" height="500" width="750"/>
</p>

Create check-for-updates microservice
-------------------------------------

Build Docker container using Dockerfile and Python image:
```bash
docker build -t {CONTAINER_NAME} .
```

Submit Docker container to GCP container registry:
```bash
gcloud builds submit --tag gcr.io/iso3166-updates/{CONTAINER_NAME}
```

Build and deploy Cloud Run application using Docker container (need to set the env vars):
```bash
gcloud beta run deploy {APP_NAME} --image gcr.io/iso3166-updates/{CONTAINER_NAME} \
  --region {REGION_NAME} --platform managed --memory 1024Mi --timeout 2700 --update-env-vars BUCKET_NAME="",\
  BLOB_NAME="",ARCHIVE_FOLDER="",GITHUB_OWNER="",GITHUB_REPO_1="",GITHUB_REPO_2="",\
  GITHUB_REPO_3="",GITHUB_API_TOKEN="",MONTH_RANGE="",CREATE_ISSUE=1
```

Delete Cloud Run application:
```bash
gcloud run services delete {APP_NAME} --region {REGION_NAME}
```

<!-- 
https://dev.to/googlecloud/using-headless-chrome-with-cloud-run-3fdp
https://www.youtube.com/watch?v=mOJiWrjFVKY
https://www.youtube.com/watch?v=LxHiCZCKwa8
https://stackoverflow.com/questions/53073411/selenium-webdriverexceptionchrome-failed-to-start-crashed-as-google-chrome-is 
-->