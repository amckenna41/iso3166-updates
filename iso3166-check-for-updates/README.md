# ISO3166 Check for Updates Function

This secondary Google Cloud Function is periodically called (usually every 3-6 months) automatically using a CRON sceduler. The function uses the iso3166-updates Python software to pull all latest updates from all ISO3166-2 wiki's to check for the latest updates within a certain period e.g the past 3 months - 6 months. The function compares the generated output with that of the updates json in the Google Cloud Storage bucket and will replace this json to integrate the latest updates found such that the main GCP Cloud Function returns the latest data. Ultimately, this function ensures that the software and assoicated APIs are up-to-date with the latest ISO3166-2 information for all countries/territories/subdivisions etc. 

There is also functionality implemented that automatically creates a GitHub Issue on the [iso3166-2][https://github.com/amckenna41/iso3166-2] repository that outlines and formats all the relevant updates/changes that have been found for all ISO3166-2 countries. The creation of this Issue will notify the repository owner that changes are outstanding that need to be implemented into the JSONs of the [iso3166-2][https://github.com/amckenna41/iso3166-2] repo. 

GCP Cloud Architecture 
------------------------

<p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166-updates-api/gcp_cloud_arch.png" alt="gcp_arch" height="200" width="400"/>
</p>

Issue Example
-------------
