import iso3166_updates
import unittest
import iso3166
import requests
import datetime
import getpass
from importlib.metadata import metadata
unittest.TestLoader.sortTestMethodsUsing = None

class ISO3166_Updates(unittest.TestCase):
    """ Tests for iso3166-updates software package. """
     
    def setUp(self):
        """ Initialise test variables including base urls for API. """
        self.base_url = "https://us-central1-iso3166-updates.cloudfunctions.net/check-for-iso3166-updates"

        self.__version__ = metadata('iso3166_updates')['version']

        self.month_base_url = self.base_url + "/month/"
        self.month_base_url_2 = self.base_url + "?month="

        self.user_agent_header = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(self.__version__,
                                       'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}
    def test_check_for_updates(self):
        """ """
        pass