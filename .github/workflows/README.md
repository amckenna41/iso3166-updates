# Workflows used in iso3166-updates

* `build_test.yml` - build and test the iso3166-updates application, running all unit tests.
* `deploy_testpypi.yml` - after test workflow successful, deploy to test pypi server.
* `deploy_ypi.yml` - after deployment to test pypi server successful, deploy to pypi server.