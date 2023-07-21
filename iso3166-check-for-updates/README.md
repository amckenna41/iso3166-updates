# ISO 3166 Check for Updates Microservice Application

> In development

<!-- [![check-for-updates](https://github.com/amckenna41/iso3166-updates/workflows/Check%20for%20ISO3166%20Updates/badge.svg)](https://github.com/amckenna41/iso3166-updates/actions?query=workflowCheck%20for%20ISO3166%20Updates) -->

This custom-built microservice webapp is periodically initialised (usually every 3-6 months) automatically using a CRON sceduler. The app uses the `iso3166-updates` Python software to pull all latest updates from all of the ISO 3166-2 data sources to check for the latest updates within a certain period e.g the past 3 - 6 months. The functionality compares the generated output with that of the updates json in the Google Cloud Storage bucket and will replace this json to integrate the latest updates found such that the main API returns the latest data. Ultimately, this function ensures that the software and assoicated APIs are up-to-date with the latest ISO 3166-2 information for all countries/territories/subdivisions etc. The app is built using a custom Docker container that is run on the serverless GCP Cloud Run service. 

There is also functionality implemented that automatically creates a GitHub Issue on the [iso3166-updates](https://github.com/amckenna41/iso3166-updates), [iso3166-2](https://github.com/amckenna41/iso3166-2) and [iso3166-flag-icons](https://github.com/amckenna41/iso3166-flag-icons) repositories. Each of these repos require the latest and most accurate ISO 3166-2 data. The creation of these Issues will notify the repository owner that changes are outstanding that need to be implemented into the JSONs of the [iso3166-updates](https://github.com/amckenna41/iso3166-updates), [iso3166-2](https://github.com/amckenna41/iso3166-2) and [iso3166-flag-icons](https://github.com/amckenna41/iso3166-flag-icons) repos. 

Note, due to this microservice only being called peiodically, the Cloud Run app is created and then deleted after its execution to save on money and resources.

GCP Cloud Architecture 
------------------------

<p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166-updates-api/gcp_architecture.png" alt="gcp_arch" height="200" width="400"/>
</p>

Create check-for-updates microservice
-------------------------------------

Build Docker container using Dockerfile and Python image:
```bash
docker build -t check_for_updates .
```

Submit Docker container to GCP container registry:
```bash
gcloud builds submit --tag gcr.io/iso3166-updates/check_for_updates
```

Build and deploy Cloud Run application using Docker container (need to set the env vars):
```bash
gcloud beta run deploy check-for-updates --image gcr.io/iso3166-updates/check_for_updates \
  --region us-central1 --platform managed --memory 1024Mi --update-env-vars BUCKET_NAME="",\
  BLOB_NAME="",ARCHIVE_FOLDER="",github-owner="",github-repo-1="",github-repo-2="",\
  github-repo-3="",github-api-token=""
```

Delete Cloud Run application:
```bash
gcloud run services delete check-for-updates
```

<!-- #https://dev.to/googlecloud/using-headless-chrome-with-cloud-run-3fdp
#https://www.youtube.com/watch?v=mOJiWrjFVKY
#https://www.youtube.com/watch?v=LxHiCZCKwa8
# https://stackoverflow.com/questions/53073411/selenium-webdriverexceptionchrome-failed-to-start-crashed-as-google-chrome-is
# docker build -t check_for_updates . && gcloud builds submit --tag gcr.io/iso3166-updates/check_for_updates && gcloud beta run deploy check-for-updates --image gcr.io/iso3166-updates/check_for_updates --region us-central1 --platform managed --memory 2Gi --timeout 1800 --update-env-vars BUCKET_NAME=iso3166-updates,BLOB_NAME=iso3166-updates.json,ARCHIVE_FOLDER=iso3166_updates_archive,github-owner=amckenna41,github-repo-1=iso3166_updates,github-repo-2=iso3166-2,github-repo-3=iso3166-flag-icons,github-api-token=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 -->