# iso3166-updates Tests <a name="TOP"></a>

All of the modules and functionalities of iso3166-updates are thoroughly tested using the Python [unittest][unittest] framework.
## Module tests:

* `test_iso3166_updates` - tests for iso3166-updates package.
* `test_iso3166_updates_api` - tests for iso3166-updates api.

## Running Tests

To run all unittests, make sure you are in the main iso3166-updates directory and from a terminal/cmd-line run:
```python
python -m unittest discover tests -v
#-v produces a more verbose and useful output
```

To run a specific unit test, make sure you are in the main iso3166-updates directory and from a terminal/cmd-line run:
```python
python -m unittest discover tests.test_iso3166_updates -v
#-v produces a more verbose and useful output
```

[unittest]: https://docs.python.org/3/library/unittest.html


