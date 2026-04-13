# Workflows used in iso3166-updates ⚙️

* `build_test.yml` - build and test the iso3166-updates application, running all unit tests.
* `deploy_test_pypi.yml` - after test workflow successful, deploy to test pypi server.
* `deploy_pypi.yml` - after deployment to test pypi server successful, deploy to pypi server..
* `auto_update_iso3166_updates.yml` - workflow run on a CRON schedule every 3 months (Jan, Apr, Jul, Oct) to export the latest ISO 3166 updates via the export pipeline, compare the output against the existing JSON, and automatically open a pull request if changes are detected.

<!-- GCP Cloud Architecture 
------------------------

<p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166-updates-api/gcp_architecture.png" alt="gcp_arch" height="500" width="700"/>
</p> -->