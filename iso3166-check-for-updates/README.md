# ISO3166 Check for Updates Function

This secondary Google Cloud Function is periodically called (usually every 3 months) automatically using a CRON sceduler. The function uses the iso3166-updates Python software to pull all latest updates from all ISO3166-2 wiki's to check for the latest updates within a certain period e.g the past 3 months. The function compares the generated output with that of the updates json in the Google Cloud Storage bucket and will replace this json to integrate the latest updates found such that the main GCP Cloud Function returns the latest data. Ultimately, this function ensures that the software and assoicated APIs are up-to-date with the latest ISO3166-2 information for all countries/territories/subdivisions etc. 

There is also functionality implemented that automatically sends an email to a list of specified users when this GCP Function is executed. If there are any updates/changes to the ISO3166-2 then these will be appended in the email body. 

GCP Cloud Architecture 
------------------------

<p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166-updates-api/gcp_cloud_arch.png" alt="gcp_arch" height="200" width="400"/>
</p>

Email Example
-------------
