# Workflows used in iso3166-updates

* `build_test_deploy.yml` - build and test the iso3166-updates application, running all unit tests.
* `deploy_test_pypi.yml` - after test workflow successful, deploy to test pypi server.
* `deploy_pypi.yml` - after deployment to test pypi server successful, deploy to pypi server.
* `check_for_updates.yml` - workflow run using a CRON schedule every 6 months to check for the latest ISO 3166 updates using a custom-built Cloud run application.

GCP Cloud Architecture 
------------------------

<p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166-updates-api/gcp_arch.png" alt="gcp_arch" height="200" width="400"/>
</p>