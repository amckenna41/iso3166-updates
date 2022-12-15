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
        self.alpha2_base_url = self.base_url + '?alpha2='
        self.year_base_url = self.base_url + '?year='
        self.user_agent_header = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(iso3166_updates.__version__,
                                       'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}
    def test_api_endpoint(self):
        """ Testing endpoint is valid and returns correct 200 status code for all alpha2 codes."""
        main_request = requests.get(self.base_url, headers=self.user_agent_header)
        self.assertEqual(main_request.status_code, 200, "")
        #test encoding, type and other attributes from request library 
        #main_request.headers[content-type] = application/json

        for alpha2 in sorted(list(iso3166.countries_by_alpha2.keys())):
            test_request = requests.get(self.base_url + '?=' + alpha2, headers=self.user_agent_header)
            self.assertEqual(test_request.status_code, 200, "")
            self.assertEqual(test_request.headers["content-type"], "application/json", "")

    def test_alpha2(self):
        """ Testing single, multiple and invalid alpha2 codes for expected ISO3166 updates. """
        test_alpha2_1 = "AD"
        test_alpha2_2 = "BO"
        test_alpha2_3 = "CO"
        test_alpha2_4 = "DE"
        test_alpha2_5 = "KE"
        test_alpha2_6 = "blahblahblah"
        test_alpha2_7 = 42
        test_alpha2_8 = False


        test_request = requests.get(self.alpha2_base_url + test_alpha2_1, headers=self.user_agent_header)
        test_alpha2_1_expected = {}
        test_request = requests.get(self.alpha2_base_url + test_alpha2_2, headers=self.user_agent_header)
        test_request = requests.get(self.alpha2_base_url + test_alpha2_3, headers=self.user_agent_header)
        test_request = requests.get(self.alpha2_base_url + test_alpha2_4, headers=self.user_agent_header)
        test_request = requests.get(self.alpha2_base_url + test_alpha2_5, headers=self.user_agent_header)
        test_request = requests.get(self.alpha2_base_url + test_alpha2_6, headers=self.user_agent_header)
        self.assertEqual(test_request.status_code, 404, "")

        test_request = requests.get(self.alpha2_base_url + test_alpha2_7, headers=self.user_agent_header)
        self.assertEqual(test_request.status_code, 404, "")

        test_request = requests.get(self.alpha2_base_url + test_alpha2_8, headers=self.user_agent_header)
        self.assertEqual(test_request.status_code, 404, "")

    def test_year(self):
        """ Testing single and multiple years, year ranges and greater than/less than and invalid years. """
        test_year1 = "2016"
        test_year2 = "2007"
        test_year3 = "2021"
        test_year4 = "2004"
        test_year5 = ">2017"
        test_year6 = "<2010"
        test_year7 = "2010-2020"
        test_year8 = "abc"
        test_year9 = False

        test_request = requests.get(self.year_base_url + test_year1, headers=self.user_agent_header)
        test_request = requests.get(self.year_base_url + test_year2, headers=self.user_agent_header)
        test_request = requests.get(self.year_base_url + test_year3, headers=self.user_agent_header)
        test_request = requests.get(self.year_base_url + test_year4, headers=self.user_agent_header)
        test_request = requests.get(self.year_base_url + test_year5, headers=self.user_agent_header)
        test_request = requests.get(self.year_base_url + test_year6, headers=self.user_agent_header)
        test_request = requests.get(self.year_base_url + test_year7, headers=self.user_agent_header)
        test_request = requests.get(self.year_base_url + test_year8, headers=self.user_agent_header)
        self.assertEqual(test_request.status_code, 404, "Expected a 404 response as URL has invalid parameters, got status code {}".format(test_request.status_code))
        test_request = requests.get(self.year_base_url + test_year9, headers=self.user_agent_header)
        self.assertEqual(test_request.status_code, 404, "Expected a 404 response as URL has invalid parameters, got status code {}".format(test_request.status_code)))


    def test_alpha2_year(self):
        """ Testing varying combinations of alpha2 codes with years/year ranges. """
        test_alpha2_year1 = ("AD", "2015")
        test_alpha2_year2 = ("", "")
        test_alpha2_year3 = ("", "")
        test_alpha2_year4 = ("", "")
        test_alpha2_year5 = ("", "")
        test_alpha2_year6 = ("", "")
        test_alpha2_year7 = ("", "")

        test_request = requests.get(self.base_url + '?alpha2=' + test_alpha2_year1[0] + '&year=' + test_alpha2_year1[1], headers=self.user_agent_header)
        test_request = requests.get(self.base_url + '?alpha2=' + test_alpha2_year2[0] + '&year=' + test_alpha2_year2[1], headers=self.user_agent_header)
        test_request = requests.get(self.base_url + '?alpha2=' + test_alpha2_year3[0] + '&year=' + test_alpha2_year3[1], headers=self.user_agent_header)
        test_request = requests.get(self.base_url + '?alpha2=' + test_alpha2_year4[0] + '&year=' + test_alpha2_year4[1], headers=self.user_agent_header)
        test_request = requests.get(self.base_url + '?alpha2=' + test_alpha2_year5[0] + '&year=' + test_alpha2_year5[1], headers=self.user_agent_header)


    def tearDown(self):
        """  """
        pass


if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)