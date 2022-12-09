import iso3166_updates
import unittest
import iso3166
import requests
import getpass
unittest.TestLoader.sortTestMethodsUsing = None


class ISO3166_Updates(unittest.TestCase):
    """ Tests for iso3166-updates software package. """
     
    def setUp(self):
        """ """
        self.base_url = "https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates2"
        self.user_agent_header = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(iso3166_updates.__version__,
                                       'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}
    def test_api_endpoint(self):
        """ """
        main_request = requests.get(self.base_url, headers=self.user_agent_header)
        self.assertEqual(main_request.status_code, 200, "")
        #test encoding, type and other attributes from request library 
        #main_request.headers[content-type] = application/json

        for alpha2 in sorted(list(iso3166.countries_by_alpha2.keys())):
            test_request = requests.get(self.base_url + '?=' + alpha2, headers=self.user_agent_header)
            self.assertEqual(test_request.status_code, 200, "")
            self.assertEqual(test_request.headers["content-type"], "application/json", "")

    def test_alpha2(self):
        """ """
        alpha2_base_url = self.base_url + '?alpha2='

    def test_year(self):
        """ """
        year_base_url = self.base_url + '?year='


    def test_alpha2_year(self):
        pass

    def tearDown(self):
        """  """
        pass


if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)