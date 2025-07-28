# iso3166-updates Tests 🧪 <a name="TOP"></a>

All of the modules and functionalities of iso3166-updates are thoroughly tested using the Python [unittest][unittest] framework. Currently there are 7 test cases with 56 unit tests functions made up of several unit tests.

## Module tests:

* `test_iso3166_updates` - unit tests for iso3166-updates package.
* `test_export_updates_driver` - unit tests for Chromedriver functionalities in export script.
* `test_export_updates_get_updates_data` - unit tests for script that pulls the data from the two main data sources in export script.
* `test_export_updates_main` - unit tests for main entry function in export script.
* `test_export_updates_utils` - unit tests for utils module that contains various utility functions used throughout export script. 
* `test_export_updates_parse_updates_data` - unit tests for functionalities that parse the updates data in export script.
* `test_iso3166_updates_api` - unit tests for iso3166-updates api.

## Running Tests

Prior to running any of the tests, ensure you have the required packages installed, all the packages can be downloaded via the requirements.txt
```bash
pip install -r tests/requirements.txt
```

To run all unittests, make sure you are in the main `iso3166-updates` directory and from a terminal/cmd-line run:
```bash
python -m unittest discover tests -v
#-v produces a more verbose and useful output
```

To run a specific unit test, make sure you are in the main `iso3166-updates` directory and from a terminal/cmd-line run:
```bash
python -m unittest discover tests.test_iso3166_updates -v
#-v produces a more verbose and useful output
```

[unittest]: https://docs.python.org/3/library/unittest.html