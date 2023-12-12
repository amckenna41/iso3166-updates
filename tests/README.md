# iso3166-updates Tests 🧪 <a name="TOP"></a>

All of the modules and functionalities of iso3166-updates are thoroughly tested using the Python [unittest][unittest] framework. Currently there are 3 test cases with 23 unit tests functions made up of several unit tests.
## Module tests:

* `test_iso3166_updates` - unit tests for iso3166-updates package.
* `test_get_all_iso3166_updates` - unit tests for script that pulls all updates from data sources.
* `test_iso3166_updates_api` - unit tests for iso3166-updates api.

## Running Tests

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