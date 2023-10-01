import unittest
import iso3166
import requests
import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import getpass
from importlib.metadata import metadata
unittest.TestLoader.sortTestMethodsUsing = None

class ISO3166_Updates_Api_Tests(unittest.TestCase):
    """
    Test suite for testing ISO 3166 Updates API created to accompany the iso3166-updates Python software package. 

    Test Cases
    ==========
    test_homepage_endpoint:
        testing main endpoint that returns the homepage and API documentation. 
    test_api_endpoints:
        testing main api endpoints/paths validating they return correct response type and status code.
    test_all_endpoint:
        testing /all endpoint that returns all updates data for all countries.
    test_alpha2_endpoint:
        testing /alpha2 endpoint validating correct data and output object returned, using a variety of alpha-2 codes.
    test_year_endpoint:
        testing /year endpoint validating correct data and output object returned, using a variety of years.
    test_name_endpoint:
        testing /name endpoint validating correct data and output object returned, using a variety of country names.
    test_name_year_endpoint:
        testing /name/year endpoint validating correct data and output object returned, using a variety of country names
        and years.
    test_alpha2_year_endpoint:
        testing /alpha2/year endpoint validating correct data and output object returned, using a variety of alpha-2 codes
        and years.
    test_month_endpoint:
        testing /month endpoint validating correct data and output object returned, using a variety of month values.
    """     
    def setUp(self):
        """ Initialise test variables including base urls for API. """
        # self.base_url = "https://iso3166-updates-frontend.vercel.app/api"
        self.base_url = "https://iso3166-updates.com/api" 

        self.__version__ = metadata('iso3166_updates')['version']

        self.alpha2_base_url = self.base_url + "/alpha2/"
        self.year_base_url = self.base_url + '/year/'
        self.name_base_url = self.base_url + '/name/'
        self.all_base_url = self.base_url + '/all'
        self.month_base_url = self.base_url + '/month/'
        self.user_agent_header = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(self.__version__,
                                       'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}
    
        #correct column/key names for dict returned from api
        self.expected_output_columns = ["Code/Subdivision Change", "Date Issued", "Description of Change in Newsletter", "Edition/Newsletter"]

    def test_homepage_endpoint(self):
        """ Testing contents of main "/api" endpoint that returns the homepage and API documentation. """
        test_request_main = requests.get(self.base_url, headers=self.user_agent_header)
        soup = BeautifulSoup(test_request_main.content, 'html.parser')
#1.)
        version = soup.find(id='version').text.split(': ')[1]
        last_updated = soup.find(id='last-updated').text.split(': ')[1]
        author = soup.find(id='author').text.split(': ')[1]

        self.assertEqual(version, "1.4.4", "Expected API version to be 1.4.4, got {}.".format(version))
        self.assertEqual(last_updated, "September 2023", "Expected last updated data to be September 2023, got {}.".format(last_updated))
        self.assertEqual(author, "AJ", "Expected author to be AJ, got {}.".format(author))
#2.)
        section_list_menu = soup.find(id='section-list-menu').find_all('li')
        correct_section_menu = ["About", "Attributes", "Endpoints", "All", "Alpha-2 Code", "Name", "Credits", "Contributing"]
        for li in section_list_menu:
            self.assertIn(li.text.strip(), correct_section_menu, "Expected list element {} to be in list.".format(li))

    def test_all_endpoint(self):
        """ Testing /all endpoint that returns all updates data for all countries. """
        test_request_all = requests.get(self.all_base_url, headers=self.user_agent_header)
#1.)
        self.assertIsInstance(test_request_all.json(), dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_all.json())))
        self.assertEqual(len(test_request_all.json()), 249, "Expected there to be 249 elements in output object, got {}.".format(len(test_request_all.json())))
        self.assertEqual(test_request_all.status_code, 200, "Expected 200 status code from request, got {}.".format(test_request_all.status_code))
        self.assertEqual(test_request_all.headers["content-type"], "application/json", 
                "Expected Content type to be application/json, got {}.".format(test_request_all.headers["content-type"]))

    @unittest.skip("Skipping to not overload API endpoints on test suite run.")
    def test_api_endpoints(self):
        """ Testing API endpoints are valid and return expected 200 status code for all alpha-2 codes. """
#1.)
        main_request = requests.get(self.base_url, headers=self.user_agent_header)
        self.assertEqual(main_request.status_code, 200, 
            "Expected 200 status code from request, got {}.".format(main_request.status_code))
        self.assertEqual(main_request.headers["content-type"], "text/html; charset=utf-8", 
            "Expected Content type to be text/html; charset=utf-8, got {}.".format(main_request.headers["content-type"]))
#2.)
        #for each alpha-2, test API returns valid response to it and correct json content type
        for alpha2 in sorted(list(iso3166.countries_by_alpha2.keys())):
            if (alpha2 == "XK"):
               continue
            test_request = requests.get(self.alpha2_base_url + alpha2, headers=self.user_agent_header)
            self.assertEqual(test_request.status_code, 200, 
                "Expected 200 status code from request for alpha-2 code {}, got {}.".format(alpha2, test_request.status_code))
            self.assertEqual(test_request.headers["content-type"], "application/json", 
                "Expected Content type to be application/json for alpha-2 code {}, got {}.".format(alpha2, test_request.headers["content-type"]))

    def test_alpha2_endpoint(self):
        """ Testing single, multiple and invalid alpha-2 codes for expected ISO 3166 updates. """
        test_alpha2_ad = "AD" #Andorra 
        test_alpha2_bo = "BO" #Bolivia
        test_alpha2_co = "CO" #Colombia
        test_alpha2_bo_co_dm = "BO,CO,DM" 
        test_alpha2_ke = "KEN" #Kenya (using alpha-3 code)
        error_test_alpha2_1 = "blahblahblah"
        error_test_alpha2_2 = "42"
        error_test_alpha2_3 = "XYZ" #invalid alpha-3 code
#1.)
        test_request_ad = requests.get(self.alpha2_base_url + test_alpha2_ad, headers=self.user_agent_header).json() #AD
        
        #expected test outputs
        test_alpha2_ad_expected1 = {
                "Code/Subdivision Change": "",
                "Date Issued": "2015-11-27",
                "Description of Change in Newsletter": "Update List Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD)."
                }
        test_alpha2_ad_expected2 = {
                "Code/Subdivision Change": "",
                "Date Issued": "2014-11-03",
                "Description of Change in Newsletter": "Update List Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD)."
                }

        self.assertIsInstance(test_request_ad, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_ad)))
        self.assertIsInstance(test_request_ad[test_alpha2_ad], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_ad[test_alpha2_ad])))
        self.assertEqual(list(test_request_ad.keys()), [test_alpha2_ad], "Expected parent key does not match output, got {}.".format(list(test_request_ad.keys())))
        for row in test_request_ad[test_alpha2_ad]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_ad[test_alpha2_ad]), 3, "Expected there to be 3 elements in output object, got {}.".format(len(test_request_ad[test_alpha2_ad])))
        self.assertEqual(test_request_ad[test_alpha2_ad][0], test_alpha2_ad_expected1, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_ad[test_alpha2_ad][1], test_alpha2_ad_expected2, "Expected and observed outputs do not match.")
#2.)
        test_request_bo = requests.get(self.alpha2_base_url + test_alpha2_bo, headers=self.user_agent_header).json() #BO
        
        #expected test outputs
        test_alpha2_bo_expected1 = {
                "Code/Subdivision Change": "",
                "Date Issued": "2014-12-18",
                "Description of Change in Newsletter": "Alignment of the English and French short names upper and lower case with UNTERM.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }
        test_alpha2_bo_expected2 = {
                "Code/Subdivision Change": "",
                "Date Issued": "2014-11-03",
                "Description of Change in Newsletter": "Update List Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }
        
        self.assertIsInstance(test_request_bo, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_bo)))
        self.assertIsInstance(test_request_bo[test_alpha2_bo], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_bo[test_alpha2_bo])))
        self.assertEqual(list(test_request_bo.keys()), [test_alpha2_bo], "Expected parent key does not match output, got {}.".format(list(test_request_bo.keys())))
        for row in test_request_bo[test_alpha2_bo]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_bo[test_alpha2_bo]), 5, "Expected there to be 5 elements in output object, got {}.".format(len(test_request_bo[test_alpha2_bo])))
        self.assertEqual(test_request_bo[test_alpha2_bo][0], test_alpha2_bo_expected1, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_bo[test_alpha2_bo][1], test_alpha2_bo_expected2, "Expected and observed outputs do not match.")
#3.)
        test_request_co = requests.get(self.alpha2_base_url + test_alpha2_co, headers=self.user_agent_header).json() #CO

        #expected test outputs
        test_alpha2_co_expected1 = {
                "Code/Subdivision Change": "",
                "Date Issued": "2016-11-15",
                "Description of Change in Newsletter": "Addition of local variation of CO-DC, CO-SAP, CO-VAC; update list source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:CO)."
                }
        test_alpha2_co_expected2 = {
                "Code/Subdivision Change": "",
                "Date Issued": "2004-03-08",
                "Description of Change in Newsletter": "Change of name of CO-DC.",
                "Edition/Newsletter": "Newsletter I-6 (https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf)."
                }       

        self.assertIsInstance(test_request_co, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_co)))
        self.assertIsInstance(test_request_co[test_alpha2_co], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_co[test_alpha2_co])))
        self.assertEqual(list(test_request_co.keys()), [test_alpha2_co], "Expected parent key does not match output, got {}.".format(list(test_request_co.keys())))
        for row in test_request_co[test_alpha2_co]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_co[test_alpha2_co]), 2, "Expected there to be 2 elements in output object, got {}.".format(len(test_request_co[test_alpha2_co])))
        self.assertEqual(test_request_co[test_alpha2_co][0], test_alpha2_co_expected1, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_co[test_alpha2_co][1], test_alpha2_co_expected2, "Expected and observed outputs do not match.")
#4.)
        test_request_bo_co_dm = requests.get(self.alpha2_base_url + test_alpha2_bo_co_dm, headers=self.user_agent_header).json() #BO,CO,DM
        test_alpha2_list = ['BO', 'CO', 'DM']  
        
        #expected test outputs
        test_alpha2_bo_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2014-12-18",
                "Description of Change in Newsletter": "Alignment of the English and French short names upper and lower case with UNTERM.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }  
        test_alpha2_co_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2016-11-15",
                "Description of Change in Newsletter": "Addition of local variation of CO-DC, CO-SAP, CO-VAC; update list source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:CO)."
                }  
        test_alpha2_dm_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2015-11-27",
                "Description of Change in Newsletter": "Update List Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }     

        self.assertIsInstance(test_request_bo_co_dm, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_bo_co_dm)))
        self.assertEqual(list(test_request_bo_co_dm.keys()), test_alpha2_list, "Expected columns do not match output, got {}.".format(list(test_request_bo_co_dm.keys())))
        for alpha2 in test_alpha2_list:
                self.assertIsInstance(test_request_bo_co_dm[alpha2], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_bo_co_dm[alpha2])))
                for row in test_request_bo_co_dm[alpha2]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_bo_co_dm['BO']), 5, "Expected there to be 5 rows of updates for BO, got {}.".format(len(test_request_bo_co_dm['BO'])))
        self.assertEqual(len(test_request_bo_co_dm['CO']), 2, "Expected there to be 2 rows of updates for CO, got {}.".format(len(test_request_bo_co_dm['CO'])))
        self.assertEqual(len(test_request_bo_co_dm['DM']), 3, "Expected there to be 3 rows of updates for DM, got {}.".format(len(test_request_bo_co_dm['DM'])))
        self.assertEqual(test_request_bo_co_dm['BO'][0], test_alpha2_bo_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_bo_co_dm['CO'][0], test_alpha2_co_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_bo_co_dm['DM'][0], test_alpha2_dm_expected, "Expected and observed outputs do not match.")
#5.)
        test_request_ke = requests.get(self.alpha2_base_url + test_alpha2_ke, headers=self.user_agent_header).json() #KEN

        #expected test outputs
        test_alpha2_ke_expected1 = {
                "Code/Subdivision Change": "",
                "Date Issued": "2016-11-15",
                "Description of Change in Newsletter": "Update Code Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:KE)."
                } 
        test_alpha2_ke_expected2 = {
                "Code/Subdivision Change": "Deleted codes: KE-110, KE-200, KE-300, KE-400, KE-500, KE-600, KE-700, KE-800 Added codes: KE-01 through KE-47.",
                "Date Issued": "2014-10-30",
                "Description of Change in Newsletter": "Delete provinces; add 47 counties; update List Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:KE)."
                }       
        
        self.assertIsInstance(test_request_ke, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_ke)))
        self.assertIsInstance(test_request_ke["KE"], list, "Expected ouput object of API should be of type list, got {}.".format(type(test_request_ke["KE"])))
        self.assertEqual(list(test_request_ke.keys()), ["KE"], "Expected output columns of API do not match, got {}.".format(list(test_request_ke.keys()))) 
        for row in test_request_ke["KE"]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_ke["KE"]), 4, "Expected there to be 4 rows of updates for BO, got {}.".format(len(test_request_ke["KE"])))
        self.assertEqual(test_request_ke["KE"][0], test_alpha2_ke_expected1, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_ke["KE"][1], test_alpha2_ke_expected2, "Expected and observed outputs do not match.")
#6.)
        test_request_error1 = requests.get(self.alpha2_base_url + error_test_alpha2_1, headers=self.user_agent_header).json() #blahblahblah

        self.assertIsInstance(test_request_error1, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_error1)))
        self.assertEqual(list(test_request_error1.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error1["message"], "Invalid 2 letter alpha-2 code input: " + error_test_alpha2_1.upper() + ".", "Error message incorrect: {}.".format(test_request_error1["message"]))
        self.assertEqual(test_request_error1["status"], 400, "Error status code incorrect: {}.".format(test_request_error1["status"]))
        self.assertEqual(test_request_error1["path"], self.alpha2_base_url + error_test_alpha2_1, "Error path incorrect: {}.".format(test_request_error1["path"]))
#7.)
        test_request_error2 = requests.get(self.alpha2_base_url + error_test_alpha2_2, headers=self.user_agent_header).json() #42

        self.assertIsInstance(test_request_error2, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_error2)))
        self.assertEqual(list(test_request_error2.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error2["message"], "Invalid 2 letter alpha-2 code input: " + error_test_alpha2_2.upper() + ".", "Error message incorrect: {}.".format(test_request_error2["message"]))
        self.assertEqual(test_request_error2["status"], 400, "Error status code incorrect: {}.".format(test_request_error2["status"]))
        self.assertEqual(test_request_error2["path"], self.alpha2_base_url + error_test_alpha2_2, "Error path incorrect: {}.".format(test_request_error2["path"]))
#8.)
        test_request_error3 = requests.get(self.alpha2_base_url + error_test_alpha2_3, headers=self.user_agent_header).json() #xyz

        self.assertIsInstance(test_request_error3, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_error3)))
        self.assertEqual(list(test_request_error3.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error3["message"], "Invalid 3 letter alpha-3 code input: " + error_test_alpha2_3.upper() + ".", "Error message incorrect: {}.".format(test_request_error3["message"]))
        self.assertEqual(test_request_error3["status"], 400, "Error status code incorrect: {}.".format(test_request_error3["status"]))
        self.assertEqual(test_request_error3["path"], self.alpha2_base_url + error_test_alpha2_3, "Error path incorrect: {}.".format(test_request_error3["path"]))

    def test_year_endpoint(self): 
        """ Testing single and multiple years, year ranges and greater than/less than and invalid years. """
        test_year_2016 = "2016"
        test_year_2007 = "2007"
        test_year_2021 = "2021"
        test_year_2004_2009 = "2004-2009"
        test_year_gt_2017 = ">2017"
        test_year_lt_2002 = "<2002"
        test_year_abc = "abc"
        test_year_12345 = "12345"
#1.)
        test_request_year_2016 = requests.get(self.year_base_url + test_year_2016, headers=self.user_agent_header).json() #2016

        #expected test outputs
        test_au_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2016-11-15",
                "Description of Change in Newsletter": "Update List Source; update Code Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }
        test_dz_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2016-11-15",
                "Description of Change in Newsletter": "Change of spelling of DZ-28; Update list source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }
        test_mv_expected = {
                "Code/Subdivision Change": "Spelling change: MV-05.",
                "Date Issued": "2016-11-15",
                "Description of Change in Newsletter": "Change of spelling of MV-05.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:MV)."
                }
        test_pw_expected = {
                "Code/Subdivision Change": "Name changed: PW-050 Hatobohei -> Hatohobei.",
                "Date Issued": "2016-11-15",
                "Description of Change in Newsletter": "Change of spelling of PW-050 in eng, pau; update list source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:PW)."
                }

        #expected output keys
        test_year_2016_keys = ['AU', 'AW', 'BD', 'BF', 'BR', 'BT', 'CD', 'CI', 'CL', 'CO', 'CZ', 'DJ', 'DO', 'DZ', 'ES', 'FI', 'FJ', 
                               'FR', 'GD', 'GM', 'GR', 'ID', 'IL', 'IQ', 'KE', 'KG', 'KH', 'KR', 'KZ', 'LA', 'MM', 'MV', 'MX', 'NA', 
                               'PW', 'RW', 'SI', 'TG', 'TJ', 'TK', 'TV', 'TW', 'UG', 'YE']

        self.assertIsInstance(test_request_year_2016, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_year_2016)))
        self.assertEqual(list(test_request_year_2016), test_year_2016_keys, "Expected keys of output dict from API do not match, got {}.".format(list(test_request_year_2016)))
        self.assertEqual(len(list(test_request_year_2016)), 44, "Expected there to be 44 output objects from API call, got {}.".format(len(list(test_request_year_2016))))
        for alpha2 in list(test_request_year_2016):
                for row in range(0, len(test_request_year_2016[alpha2])):
                        self.assertEqual(list(test_request_year_2016[alpha2][row].keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(test_request_year_2016[alpha2][row].keys())))
                        self.assertIsInstance(test_request_year_2016[alpha2][row], dict, "Expected output row object of API to be of type dict, got {}.".format(type(test_request_year_2016[alpha2][row])))
                        self.assertEqual(datetime.strptime(test_request_year_2016[alpha2][row]["Date Issued"], "%Y-%m-%d").year, 2016, 
                                "Year in Date Issued column does not match expected 2016, got {}.".format(datetime.strptime(test_request_year_2016[alpha2][row]["Date Issued"], "%Y-%m-%d").year))
        self.assertEqual(test_request_year_2016['AU'][0], test_au_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_2016['DZ'][0], test_dz_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_2016['MV'][0], test_mv_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_2016['PW'][0], test_pw_expected, "Expected and observed outputs do not match.")
#2.)
        test_request_year_2007 = requests.get(self.year_base_url + test_year_2007, headers=self.user_agent_header).json() #2007
        
        #expected test outputs
        test_ag_expected = {
                "Code/Subdivision Change": "Subdivisions added: 6 parishes, 1 dependency.",
                "Date Issued": "2007-04-17",
                "Description of Change in Newsletter": "Addition of the administrative subdivisions and of their code elements.",
                "Edition/Newsletter": "Newsletter I-8 (https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)."
                }
        test_bh_expected = {
                "Code/Subdivision Change": "Subdivision layout: 12 regions (see below) -> 5 governorates.",
                "Date Issued": "2007-04-17",
                "Description of Change in Newsletter": "Modification of the administrative structure.",
                "Edition/Newsletter": "Newsletter I-8 (https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)."
                }
        test_gd_expected = {
                "Code/Subdivision Change": "Subdivisions added: 6 parishes, 1 dependency.",
                "Date Issued": "2007-04-17",
                "Description of Change in Newsletter": "Addition of the administrative subdivisions and of their code elements.",
                "Edition/Newsletter": "Newsletter I-8 (https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)."
                }
        test_sm_expected = {
                "Code/Subdivision Change": "Subdivisions added: 9 municipalities.",
                "Date Issued": "2007-04-17",
                "Description of Change in Newsletter": "Addition of the administrative subdivisions and of their code elements.",
                "Edition/Newsletter": "Newsletter I-8 (https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)."
                }

        #expected key outputs
        test_year_2007_keys = ['AD', 'AG', 'BA', 'BB', 'BG', 'BH', 'BL', 'CI', 'CZ', 'DM', 'DO', 'EG', 'FR', 'GB', 'GD', 'GE', 'GG', 'GN', 'GP', 'HT', 'IM', 'IR', 
                               'IT', 'JE', 'KE', 'KN', 'KW', 'LB', 'LC', 'LI', 'LR', 'ME', 'MF', 'MK', 'MT', 'NR', 'PF', 'PW', 'RE', 'RS', 'RU', 'RW', 'SB', 'SC', 
                               'SD', 'SG', 'SM', 'TD', 'TF', 'TO', 'TV', 'UG', 'VC', 'YE', 'ZA']

        self.assertIsInstance(test_request_year_2007, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_year_2007)))
        self.assertEqual(list(test_request_year_2007), test_year_2007_keys, "Expected keys of output dict from API do not match, got {}.".format(list(test_request_year_2007)))
        self.assertEqual(len(list(test_request_year_2007)), 55, "Expected there to be 55 output objects from API call, got {}.".format(len(list(test_request_year_2007))))
        for alpha2 in list(test_request_year_2007):
                for row in range(0, len(test_request_year_2007[alpha2])):
                        self.assertEqual(list(test_request_year_2007[alpha2][row].keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(test_request_year_2007[alpha2][row].keys())))
                        self.assertIsInstance(test_request_year_2007[alpha2][row], dict, "Expected output row of object of API to be of type dict, got {}.".format(type(test_request_year_2007[alpha2][row])))
                        self.assertEqual(str(datetime.strptime(test_request_year_2007[alpha2][row]["Date Issued"], "%Y-%m-%d").year), "2007", 
                                "Year in Date Issued column does not match expected 2007, got {}.".format(datetime.strptime(test_request_year_2007[alpha2][row]["Date Issued"], "%Y-%m-%d").year))
        self.assertEqual(test_request_year_2007['AG'][0], test_ag_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_2007['BH'][0], test_bh_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_2007['GD'][0], test_gd_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_2007['SM'][0], test_sm_expected, "Expected and observed outputs do not match.")
#3.)
        test_request_year_2021 = requests.get(self.year_base_url + test_year_2021, headers=self.user_agent_header).json() #2021

        #expected test outputs
        test_cn_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2021-11-25",
                "Description of Change in Newsletter": "Change of spelling of CN-NX; Update List Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }
        test_et_expected = {
                "Code/Subdivision Change": "Subdivisions added: ET-SI Sidama.",
                "Date Issued": "2021-11-25",
                "Description of Change in Newsletter": "Addition of regional state ET-SI; Update List Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:ET)."
                }
        test_np_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2021-11-25",
                "Description of Change in Newsletter": "Change of spelling of NP-P5; Modification of remark part 2; Update List Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:NP)."
                }
        test_ss_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2021-11-25",
                "Description of Change in Newsletter": "Typographical correction of SS-BW (deletion of the extra space between el and Ghazal).",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }

        #expected key outputs
        test_year_2021_keys = ['CN', 'ET', 'FR', 'GB', 'GT', 'HU', 'IS', 'KH', 'LT', 'LV', 'NP', 'PA', 'RU', 'SI', 'SS']

        self.assertIsInstance(test_request_year_2021, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_year_2021)))
        self.assertEqual(list(test_request_year_2021), test_year_2021_keys, "Expected keys of output dict from API do not match, got {}.".format(list(test_request_year_2021)))
        self.assertEqual(len(list(test_request_year_2021)), 15, "Expected there to be 15 output objects from API call, got {}.".format(len(list(test_request_year_2021))))
        for alpha2 in list(test_request_year_2021):
                for row in range(0, len(test_request_year_2021[alpha2])):
                        self.assertEqual(list(test_request_year_2021[alpha2][row].keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(test_request_year_2021[alpha2][row].keys())))
                        self.assertIsInstance(test_request_year_2021[alpha2][row], dict, "Expected output row of object of API to be of type dict, got {}.".format(type(test_request_year_2021[alpha2][row])))
                        self.assertEqual(str(datetime.strptime(test_request_year_2021[alpha2][row]["Date Issued"], "%Y-%m-%d").year), "2021", 
                                "Year in Date Issued column does not match expected 2021, got {}.".format(datetime.strptime(test_request_year_2021[alpha2][row]["Date Issued"], "%Y-%m-%d").year))
        self.assertEqual(test_request_year_2021['CN'][0], test_cn_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_2021['ET'][0], test_et_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_2021['NP'][0], test_np_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_2021['SS'][0], test_ss_expected, "Expected and observed outputs do not match.")
#4.)
        test_request_year_2004_2009 = requests.get(self.year_base_url + test_year_2004_2009, headers=self.user_agent_header).json() #2004-2009

        #expected test outputs
        test_af_expected = {
                "Code/Subdivision Change": "Subdivisions added: AF-DAY Dāykondī AF-PAN Panjshīr.",
                "Date Issued": "2005-09-13",
                "Description of Change in Newsletter": "Addition of 2 provinces. Update of list source.",
                "Edition/Newsletter": "Newsletter I-7 (https://web.archive.org/web/20081218103217/http://www.iso.org/iso/iso_3166-2_newsletter_i-7_en.pdf)."
                }
        test_co_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2004-03-08",
                "Description of Change in Newsletter": "Change of name of CO-DC.",
                "Edition/Newsletter": "Newsletter I-6 (https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf)."
                }
        test_kp_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2004-03-08",
                "Description of Change in Newsletter": "Spelling correction in header of list source.",
                "Edition/Newsletter": "Newsletter I-6 (https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf)."
                }
        test_za_expected = {
                "Code/Subdivision Change": "Codes: Gauteng: ZA-GP -> ZA-GT KwaZulu-Natal: ZA-ZN -> ZA-NL.",
                "Date Issued": "2007-12-13",
                "Description of Change in Newsletter": "Second edition of ISO 3166-2 (this change was not announced in a newsletter).",
                "Edition/Newsletter": "ISO 3166-2:2007 (http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=39718)."
                }

        #expected key outputs
        test_year_2004_2009_keys = ['AD', 'AF', 'AG', 'AL', 'AU', 'BA', 'BB', 'BG', 'BH', 'BL', 'BO', 'CF', 'CI', 'CN', 'CO', 'CZ', 'DJ', 'DM', 'DO', 'EG', 'FR', 
                                    'GB', 'GD', 'GE', 'GG', 'GL', 'GN', 'GP', 'HT', 'ID', 'IM', 'IR', 'IT', 'JE', 'KE', 'KI', 'KM', 'KN', 'KP', 'KW', 'LB', 'LC', 
                                    'LI', 'LR', 'MA', 'MD', 'ME', 'MF', 'MG', 'MK', 'MT', 'NG', 'NP', 'NR', 'PF', 'PS', 'PW', 'RE', 'RS', 'RU', 'RW', 'SB', 'SC', 
                                    'SD', 'SG', 'SI', 'SM', 'TD', 'TF', 'TN', 'TO', 'TV', 'UG', 'VC', 'VE', 'VN', 'YE', 'ZA']
        
        self.assertIsInstance(test_request_year_2004_2009, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_year_2004_2009)))
        self.assertEqual(list(test_request_year_2004_2009), test_year_2004_2009_keys, "Expected keys of output dict from API do not match, got {}.".format(list(test_request_year_2004_2009)))
        self.assertEqual(len(list(test_request_year_2004_2009)), 78, "Expected there to be 78 output objects from API call, got {}.".format(len(list(test_request_year_2004_2009))))
        for alpha2 in list(test_request_year_2004_2009):
                for row in range(0, len(test_request_year_2004_2009[alpha2])):
                        self.assertEqual(list(test_request_year_2004_2009[alpha2][row].keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(test_request_year_2004_2009[alpha2][row].keys())))
                        self.assertIsInstance(test_request_year_2004_2009[alpha2][row], dict, "Expected output row of object of API to be of type dict, got {}.".format(type(test_request_year_2004_2009[alpha2][row])))
                        self.assertTrue((datetime.strptime(test_request_year_2004_2009[alpha2][row]["Date Issued"], "%Y-%m-%d").year >= 2004 and \
                                          (datetime.strptime(test_request_year_2004_2009[alpha2][row]["Date Issued"], "%Y-%m-%d").year <= 2009)), 
                                          "Year in Date Issued column does not match expected 2004-2009, got {}.".format(datetime.strptime(test_request_year_2004_2009[alpha2][row]["Date Issued"], "%Y-%m-%d").year))
        self.assertEqual(test_request_year_2004_2009['AF'][0], test_af_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_2004_2009['CO'][0], test_co_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_2004_2009['KP'][0], test_kp_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_2004_2009['ZA'][0], test_za_expected, "Expected and observed outputs do not match.")
#5.)    
        test_request_year_gt_2017 = requests.get(self.year_base_url + test_year_gt_2017, headers=self.user_agent_header).json() #>2017

        #expected test outputs
        test_cl_expected = {
                "Code/Subdivision Change": "Subdivisions added: CL-NB Ñuble.",
                "Date Issued": "2018-11-26",
                "Description of Change in Newsletter": "Addition of region CL-NB; Update List Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:CL)."
                }
        test_gh_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2020-11-24",
                "Description of Change in Newsletter": "Correction of the Code Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }
        test_sa_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2018-11-26",
                "Description of Change in Newsletter": "Change of subdivision category from province to region.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:SA)."
                }
        test_ve_expected = {
                "Code/Subdivision Change": "Subdivisions renamed: VE-X Vargas -> La Guaira.",
                "Date Issued": "2020-11-24",
                "Description of Change in Newsletter": "Change of subdivision name of VE-X; Update List Source; Correction of the Code Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:VE)."
                }

        #expected key outputs
        test_year_gt_2017_keys = ['AF', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AS', 'AW', 'AX', 'BA', 'BD', 'BG', 'BI', 'BJ', 'BL', 'BM', 'BN', 'BQ', 'BR', 'BS', 'BT', 'BV', 'BW', 
                                  'BY', 'CC', 'CD', 'CH', 'CI', 'CK', 'CL', 'CN', 'CV', 'CW', 'CX', 'CY', 'CZ', 'DE', 'DJ', 'DZ', 'EC', 'EE', 'EH', 'ER', 'ES', 'ET', 'FI', 
                                  'FK', 'FO', 'FR', 'GB', 'GE', 'GF', 'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GR', 'GS', 'GT', 'GU', 'GW', 'GY', 'HK', 'HM', 'HU', 
                                  'ID', 'IL', 'IM', 'IN', 'IO', 'IQ', 'IR', 'IS', 'IT', 'JE', 'JP', 'KG', 'KH', 'KM', 'KP', 'KR', 'KY', 'KZ', 'LA', 'LB', 'LK', 'LS', 'LT', 
                                  'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MF', 'MH', 'MK', 'ML', 'MM', 'MN', 'MO', 'MP', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW', 'MX', 'NA', 
                                  'NC', 'NF', 'NI', 'NL', 'NO', 'NP', 'NR', 'NU', 'NZ', 'PA', 'PE', 'PF', 'PH', 'PK', 'PL', 'PM', 'PN', 'PR', 'QA', 'RE', 'RS', 'RU', 'SA', 
                                  'SB', 'SC', 'SD', 'SI', 'SJ', 'SL', 'SM', 'SS', 'ST', 'SX', 'SY', 'SZ', 'TC', 'TD', 'TF', 'TG', 'TH', 'TJ', 'TK', 'TL', 'TN', 'TR', 'TT', 
                                  'TW', 'TZ', 'UA', 'UG', 'UM', 'UZ', 'VA', 'VE', 'VG', 'VI', 'VN', 'WF', 'YE', 'YT', 'ZA', 'ZM']

        self.assertIsInstance(test_request_year_gt_2017, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_year_gt_2017)))
        self.assertEqual(list(test_request_year_gt_2017), test_year_gt_2017_keys, "Expected keys of output dict from API do not match, got {}.".format(list(test_request_year_gt_2017)))
        self.assertEqual(len(list(test_request_year_gt_2017)), 177, "Expected there to be 177 output objects from API call, got {}.".format(len(list(test_request_year_gt_2017))))
        for alpha2 in list(test_request_year_gt_2017):
                for row in range(0, len(test_request_year_gt_2017[alpha2])):
                        self.assertEqual(list(test_request_year_gt_2017[alpha2][row].keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(test_request_year_gt_2017[alpha2][row].keys())))
                        self.assertIsInstance(test_request_year_gt_2017[alpha2][row], dict, "Expected output row of object of API to be of type dict, got {}.".format(type(test_request_year_gt_2017[alpha2][row])))
                        self.assertTrue(datetime.strptime(test_request_year_gt_2017[alpha2][row]["Date Issued"], "%Y-%m-%d").year >= 2017,
                                "Year in Date Issued column should be greater than 2017, got {}.".format(datetime.strptime(test_request_year_gt_2017[alpha2][row]["Date Issued"], "%Y-%m-%d").year))
        self.assertEqual(test_request_year_gt_2017['CL'][0], test_cl_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_gt_2017['GH'][0], test_gh_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_gt_2017['SA'][0], test_sa_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_gt_2017['VE'][0], test_ve_expected, "Expected and observed outputs do not match.")
#6.)    
        test_request_year_lt_2002 = requests.get(self.year_base_url + test_year_lt_2002, headers=self.user_agent_header).json() #<2002

        #expected test outputs
        test_ca_expected = {
                "Code/Subdivision Change": "Subdivisions added: CA-NU Nunavut.",
                "Date Issued": "2000-06-21",
                "Description of Change in Newsletter": "Addition of 1 new territory.",
                "Edition/Newsletter": "Newsletter I-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf)."
                }
        test_it_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2000-06-21",
                "Description of Change in Newsletter": "Correction of spelling mistakes of names of 2 provinces.",
                "Edition/Newsletter": "Newsletter I-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf)."
                }
        test_ro_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2000-06-21",
                "Description of Change in Newsletter": "Correction of spelling mistake of subdivision category in header.",
                "Edition/Newsletter": "Newsletter I-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf)."
                }
        test_tr_expected = {
                "Code/Subdivision Change": "Subdivisions added: TR-80 Osmaniye.",
                "Date Issued": "2000-06-21",
                "Description of Change in Newsletter": "Addition of 1 new province. Correction of 2 spelling errors.",
                "Edition/Newsletter": "Newsletter I-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf)."
                }

        #expected key outputs
        test_year_lt_2002_keys = ['BY', 'CA', 'DO', 'ER', 'ES', 'IT', 'KR', 'NG', 'PL', 'RO', 'RU', 'TR', 'VA', 'VN']

        self.assertIsInstance(test_request_year_lt_2002, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_year_lt_2002)))
        self.assertEqual(list(test_request_year_lt_2002), test_year_lt_2002_keys, "Expected keys of output dict from API do not match, got {}.".format(list(test_request_year_lt_2002)))
        self.assertEqual(len(list(test_request_year_lt_2002)), 14, "Expected there to be 14 output objects from API call, got {}.".format(len(list(test_request_year_lt_2002))))
        for alpha2 in list(test_request_year_lt_2002):
                for row in range(0, len(test_request_year_lt_2002[alpha2])):
                        self.assertEqual(list(test_request_year_lt_2002[alpha2][row].keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(test_request_year_lt_2002[alpha2][row].keys())))
                        self.assertIsInstance(test_request_year_lt_2002[alpha2][row], dict, "Expected output row of object of API to be of type dict, got {}.".format(type(test_request_year_lt_2002[alpha2][row])))
                        self.assertTrue(datetime.strptime(test_request_year_lt_2002[alpha2][row]["Date Issued"], "%Y-%m-%d").year < 2002,
                                "Year in Date Issued column should be less than 2002, got {}.".format(datetime.strptime(test_request_year_lt_2002[alpha2][row]["Date Issued"], "%Y-%m-%d").year))
        self.assertEqual(test_request_year_lt_2002['CA'][0], test_ca_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_lt_2002['IT'][0], test_it_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_lt_2002['RO'][0], test_ro_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_lt_2002['TR'][0], test_tr_expected, "Expected and observed outputs do not match.")
#7.) 
        test_request_year_abc = requests.get(self.year_base_url + test_year_abc, headers=self.user_agent_header).json() #abc
        
        self.assertIsInstance(test_request_year_abc, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_year_abc)))
        self.assertEqual(list(test_request_year_abc.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_year_abc["message"], "Invalid year input: " + test_year_abc + ".", "Error message incorrect: {}.".format(test_request_year_abc["message"]))
        self.assertEqual(test_request_year_abc["status"], 400, "Error status code incorrect: {}.".format(test_request_year_abc["status"]))
        self.assertEqual(test_request_year_abc["path"], self.year_base_url + test_year_abc, "Error path incorrect: {}.".format(test_request_year_abc["path"]))
#8.) 
        test_request_year_12345 = requests.get(self.year_base_url + test_year_12345, headers=self.user_agent_header).json() #1234

        self.assertIsInstance(test_request_year_12345, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_year_12345)))
        self.assertEqual(list(test_request_year_12345.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_year_12345["message"], "Invalid year input: " + test_year_12345.upper() + ".", "Error message incorrect: {}.".format(test_request_year_12345["message"]))
        self.assertEqual(test_request_year_12345["status"], 400, "Error status code incorrect: {}.".format(test_request_year_12345["status"]))
        self.assertEqual(test_request_year_12345["path"], self.year_base_url + test_year_12345, "Error path incorrect: {}.".format(test_request_year_12345["path"]))
    
    def test_alpha2_year_endpoint(self):
        """ Testing varying combinations of alpha-2 codes with years/year ranges. """
        test_ad_2015 = ("AD", "2015") #Andorra 2015
        test_es_2002 = ("ES", "2002") #Spain 2002
        test_hr_2011 = ("HR", "2011") #Croatia 2011
        test_ma_2019 = ("MA", "<2019") #Morocco 2019
        test_tr_2002 = ("TR", ">2002") #Turkey <2011
        test_ve_2013 = ("VE", "2013") #Venezuela 2013 
        test_abc_2000 = ("abc", "2000") 
#1.)
        test_ad_2015_request = requests.get(self.alpha2_base_url + test_ad_2015[0] + "/year/" + test_ad_2015[1], headers=self.user_agent_header).json() #Andorra - 2015
        
        #expected test outputs
        test_ad_2015_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2015-11-27",
                "Description of Change in Newsletter": "Update List Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD)."
                }

        self.assertIsInstance(test_ad_2015_request, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_ad_2015_request)))
        self.assertEqual(list(test_ad_2015_request), ['AD'], "Expected AD to be the only key returned from API in dict, got {}.".format(list(test_ad_2015_request)))
        self.assertEqual(len(test_ad_2015_request), 1, "Expected 1 row returned from API, got {}.".format(len(test_ad_2015_request)))
        for alpha2 in list(test_ad_2015_request):
                for row in range(0, len(test_ad_2015_request[alpha2])):
                        self.assertEqual(list(test_ad_2015_request[alpha2][row].keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(test_ad_2015_request[alpha2][row].keys())))
                        self.assertIsInstance(test_ad_2015_request[alpha2][row], dict, "Expected output row of object of API to be of type dict, got {}.".format(type(test_ad_2015_request[alpha2][row])))
                        self.assertEqual(datetime.strptime(test_ad_2015_request[alpha2][row]["Date Issued"], "%Y-%m-%d").year, 2015, 
                                "Year in Date Issued column does not match expected 2015, got {}.".format(datetime.strptime(test_ad_2015_request[alpha2][row]["Date Issued"], "%Y-%m-%d").year))
        self.assertIsInstance(test_ad_2015_request[test_ad_2015[0]], list, "Expected output object of API to be of type list, got {}.".format(type(test_ad_2015_request[test_ad_2015[0]])))
        self.assertEqual(test_ad_2015_expected, test_ad_2015_request[test_ad_2015[0]][0], "Observed and expected outputs of API do not match.")
#2.) 
        test_es_2002_request = requests.get(self.alpha2_base_url + test_es_2002[0] + "/year/" + test_es_2002[1], headers=self.user_agent_header).json() #Spain - 2002

        #expected test outputs
        test_es_2002_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2002-12-10",
                "Description of Change in Newsletter": "Error correction: Regional subdivision indicator corrected in ES-PM.",
                "Edition/Newsletter": "Newsletter I-4 (https://web.archive.org/web/20081218103210/http://www.iso.org/iso/iso_3166-2_newsletter_i-4_en.pdf)."
                }

        self.assertIsInstance(test_es_2002_request, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_es_2002_request)))
        self.assertEqual(list(test_es_2002_request), ['ES'], "Expected ES to be the only key returned from API in dict, got {}.".format(list(test_es_2002_request)))
        self.assertEqual(len(test_es_2002_request), 1, "Expected 1 row returned from API, got {}.".format(len(test_es_2002_request)))
        for alpha2 in list(test_es_2002_request):
                for row in range(0, len(test_es_2002_request[alpha2])):
                        self.assertEqual(list(test_es_2002_request[alpha2][row].keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(test_es_2002_request[alpha2][row].keys())))
                        self.assertIsInstance(test_es_2002_request[alpha2][row], dict, "Expected output row of object of API to be of type dict, got {}.".format(type(test_es_2002_request[alpha2][row])))
                        self.assertEqual(datetime.strptime(test_es_2002_request[alpha2][row]["Date Issued"], "%Y-%m-%d").year, 2002, 
                                "Year in Date Issued column does not match expected 2002, got {}.".format(datetime.strptime(test_es_2002_request[alpha2][row]["Date Issued"], "%Y-%m-%d").year))
        self.assertIsInstance(test_es_2002_request[test_es_2002[0]], list, "Expected output object of API to be of type list, got {}.".format(type(test_es_2002_request[test_es_2002[0]])))
        self.assertEqual(test_es_2002_expected, test_es_2002_request[test_es_2002[0]][0], "Observed and expected outputs of API do not match.")
#3.) 
        test_hr_2011_request = requests.get(self.alpha2_base_url + test_hr_2011[0] + "/year/" + test_hr_2011[1], headers=self.user_agent_header).json() #Croatia - 2011

        #expected test outputs
        test_hr_2011_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2011-12-13 (corrected 2011-12-15)",
                "Description of Change in Newsletter": "Alphabetical re-ordering.",
                "Edition/Newsletter": "Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf)."
                }

        self.assertIsInstance(test_hr_2011_request, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_hr_2011_request)))
        self.assertEqual(list(test_hr_2011_request), ['HR'], "Expected HR to be the only key returned from API in dict, got {}.".format(list(test_hr_2011_request)))
        self.assertEqual(len(test_hr_2011_request), 1, "Expected 1 row returned from API, got {}.".format(len(test_hr_2011_request)))
        for alpha2 in list(test_hr_2011_request):
                for row in range(0, len(test_hr_2011_request[alpha2])):
                        self.assertEqual(list(test_hr_2011_request[alpha2][row].keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(test_hr_2011_request[alpha2][row].keys())))
                        self.assertIsInstance(test_hr_2011_request[alpha2][row], dict, "Expected output row of object of API to be of type dict, got {}.".format(type(test_hr_2011_request[alpha2][row])))
                        self.assertEqual(datetime.strptime(re.sub("[(].*[)]", "", test_hr_2011_request[alpha2][row]["Date Issued"]).replace(' ', "").replace(".", ''), "%Y-%m-%d").year, 2011, 
                                "Year in Date Issued column does not match expected 2011, got {}.".format(datetime.strptime(re.sub("[(].*[)]", "", test_hr_2011_request[alpha2][row]["Date Issued"]).replace(' ', "").replace(".", ''), "%Y-%m-%d").year))
        self.assertIsInstance(test_hr_2011_request[test_hr_2011[0]], list, "Expected output object of API to be of type list, got {}.".format(type(test_hr_2011_request[test_hr_2011[0]])))
        self.assertEqual(test_hr_2011_expected, test_hr_2011_request[test_hr_2011[0]][0], "Observed and expected outputs of API do not match.")
#4.) 
        test_ma_lt_2019_request = requests.get(self.alpha2_base_url + test_ma_2019[0] + "/year/" + test_ma_2019[1], headers=self.user_agent_header).json() #Morocco - <2019

        #expected test outputs
        test_ma_lt_2019_expected = {
                "Code/Subdivision Change": "Spelling change: MA-05 Béni-Mellal-Khénifra -> Béni Mellal-Khénifra Location change: MA-ESM Es-Semara (EH) -> Es-Semara (EH-partial).",
                "Date Issued": "2018-11-26",
                "Description of Change in Newsletter": "Change of spelling of MA-05; Change of (EH) to (EH-partial) for MA-ESM; Correction of the romanization system label.",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:MA)."
                }
        
        self.assertIsInstance(test_ma_lt_2019_request, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_ma_lt_2019_request)))
        self.assertEqual(list(test_ma_lt_2019_request), ['MA'], "Expected MA to be the only key returned from API in dict, got {}.".format(list(test_ma_lt_2019_request)))
        self.assertEqual(len(test_ma_lt_2019_request), 1, "Expected 1 row returned from API, got {}.".format(len(test_ma_lt_2019_request)))
        for alpha2 in list(test_ma_lt_2019_request):
                for row in range(0, len(test_ma_lt_2019_request[alpha2])):
                        self.assertEqual(list(test_ma_lt_2019_request[alpha2][row].keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(test_ma_lt_2019_request[alpha2][row].keys())))
                        self.assertIsInstance(test_ma_lt_2019_request[alpha2][row], dict, "Expected output row of object of API to be of type dict, got {}.".format(type(test_ma_lt_2019_request[alpha2][row])))
                        self.assertTrue(datetime.strptime(re.sub("[(].*[)]", "", test_ma_lt_2019_request[alpha2][row]["Date Issued"]).replace(' ', "").replace(".", ''), '%Y-%m-%d').year < 2019, 
                                "Expected year of updates output to be less than 2019, got {}.".format(re.sub("[(].*[)]", "", test_ma_lt_2019_request[alpha2][row]["Date Issued"]).replace(' ', "").replace(".", '')))        
        self.assertIsInstance(test_ma_lt_2019_request[test_ma_2019[0]], list, "Expected output object of API to be of type list, got {}".format(type(test_ma_lt_2019_request[test_ma_2019[0]])))
        self.assertEqual(test_ma_lt_2019_expected, test_ma_lt_2019_request[test_ma_2019[0]][0], "Observed and expected outputs of API do not match.")
#5.) 
        test_tr_gt_2002_request = requests.get(self.alpha2_base_url + test_tr_2002[0] + "/year/" + test_tr_2002[1], headers=self.user_agent_header).json() #Turkey - >2002
        
        #expected test outputs 
        test_tr_gt_2002_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2022-07-11",
                "Description of Change in Newsletter": "Change of the short and full name.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }

        self.assertIsInstance(test_tr_gt_2002_request, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_tr_gt_2002_request)))
        self.assertEqual(list(test_tr_gt_2002_request), ['TR'], "Expected TR to be the only key returned from API in dict, got {}.".format(list(test_tr_gt_2002_request)))
        self.assertEqual(len(test_tr_gt_2002_request), 1, "Expected 1 row returned from API, got {}.".format(len(test_tr_gt_2002_request)))
        for alpha2 in list(test_tr_gt_2002_request):
                for row in range(0, len(test_tr_gt_2002_request[alpha2])):
                        self.assertEqual(list(test_tr_gt_2002_request[alpha2][row].keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(test_tr_gt_2002_request[alpha2][row].keys())))
                        self.assertIsInstance(test_tr_gt_2002_request[alpha2][row], dict, "Expected output row of object of API to be of type dict, got {}.".format(type(test_tr_gt_2002_request[alpha2][row])))
                        self.assertTrue(datetime.strptime(re.sub("[(].*[)]", "", test_tr_gt_2002_request[alpha2][row]["Date Issued"]).replace(' ', "").replace(".", ''), '%Y-%m-%d').year >= 2002, 
                                "Expected year of updates output to be greater than 2002, got {}.".format(test_tr_gt_2002_request[alpha2][row]["Date Issued"]))  
        self.assertIsInstance(test_tr_gt_2002_request[test_tr_2002[0]], list, "Expected output object of API to be of type list, got {}.".format(type(test_tr_gt_2002_request[test_tr_2002[0]])))
        self.assertEqual(test_tr_gt_2002_expected, test_tr_gt_2002_request[test_tr_2002[0]][0], "Observed and expected outputs of API do not match.")
#6.)
        test_ve_2013_request = requests.get(self.alpha2_base_url + test_ve_2013[0] + "/year/" + test_ve_2013[1], headers=self.user_agent_header).json() #Venezuela - 2013

        self.assertIsInstance(test_ve_2013_request, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_ve_2013_request)))
        self.assertEqual(len(test_ve_2013_request), 0, "Expected 0 rows returned from API, got {}.".format(len(test_ve_2013_request)))
        self.assertEqual(test_ve_2013_request, {}, "Expected output of API to be an empty dict, got\n{}".format(test_ve_2013_request))
#7.) 
        test_abc_2000_request = requests.get(self.alpha2_base_url + test_abc_2000[0] + "/year/" + test_abc_2000[1], headers=self.user_agent_header).json() #abc - 2000
        
        self.assertIsInstance(test_abc_2000_request, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_abc_2000_request)))
        self.assertEqual(list(test_abc_2000_request.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_abc_2000_request["message"], "Invalid 3 letter alpha-3 code input: " + test_abc_2000[0].upper() + ".", "Error message incorrect: {}.".format(test_abc_2000_request["message"]))
        self.assertEqual(test_abc_2000_request["status"], 400, "Error status code incorrect: {}.".format(test_abc_2000_request["status"]))
        self.assertEqual(test_abc_2000_request["path"], self.alpha2_base_url + test_abc_2000[0] + "/year/" + test_abc_2000[1], "Error path incorrect: {}.".format(test_abc_2000_request["path"]))

    def test_name_endpoint(self):
        """ Testing name endpoint, return all ISO 3166 updates data from input alpha-2 name/names. """
        test_name_benin = "Benin"
        test_name_tajikistan = "Tajikistan"
        test_name_moldova = "Moldova"
        test_name_mali_nicaragua = "Mali, Nicaragua"
        test_name_error1 = "ABCDEF"
        test_name_error2 = "12345"
        #need to convert country names from iso3166 package to their more conventional names
        name_exceptions_converted = {"Brunei Darussalam": "Brunei", "Bolivia, Plurinational State of": "Bolivia", 
                                     "Bonaire, Sint Eustatius and Saba": "Caribbean Netherlands", "Congo, Democratic Republic of the": "DR Congo",
                                     "Congo": "Republic of the Congo", "Côte d'Ivoire": "Ivory Coast", "Cabo Verde": "Cape Verde", "Falkland Islands (Malvinas)": 
                                     "Falkland Islands", "Micronesia, Federated States of" : "Micronesia", "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
                                     "South Georgia and the South Sandwich Islands": "South Georgia", "Iran, Islamic Republic of": "Iran",
                                     "Korea, Democratic People's Republic of": "North Korea", "Korea, Republic of": "South Korea",
                                     "Lao People's Democratic Republic": "Laos", "Moldova, Republic of": "Moldova", "Saint Martin (French part)": "Saint Martin",
                                     "Macao": "Macau", "Pitcairn": "Pitcairn Islands", "Palestine, State of": "Palestine", "Russian Federation": "Russia", "Sao Tome and Principe": "São Tomé and Príncipe",
                                     "Sint Maarten (Dutch part)": "Sint Maarten", "Syrian Arab Republic": "Syria", "French Southern Territories": "French Southern and Antarctic Lands",
                                     "Türkiye": "Turkey", "Taiwan, Province of China": "Taiwan", "Tanzania, United Republic of": "Tanzania", "United States of America": "United States",
                                     "Holy See": "Vatican City", "Venezuela, Bolivarian Republic of": "Venezuela", "Virgin Islands, British": "British Virgin Islands",
                                     "Virgin Islands, U.S.": "United States Virgin Islands", "Viet Nam": "Vietnam"}
#1.)    
        #for each countrytest_name_year_endpoint name, test API returns correct object, test using common.name attribute
        for alpha2 in sorted(list(iso3166.countries_by_alpha2.keys())):
            country_name = iso3166.countries_by_alpha2[alpha2].name
            if (country_name == "Kosovo"):
                continue
            test_request_name = requests.get(self.name_base_url + country_name, headers=self.user_agent_header).json()
            #convert country name to its more comon name
            if (country_name in list(name_exceptions_converted.keys())):
                country_name = name_exceptions_converted[country_name]
            self.assertEqual(list(test_request_name)[0], alpha2, 
                    "Input country name {} and one in output object do not match: {}.".format(country_name, list(test_request_name)[0]))
#2.)
        test_request_bj = requests.get(self.name_base_url + test_name_benin, headers=self.user_agent_header).json() #Benin

        test_name_bj_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2020-11-24",
                "Description of Change in Newsletter": "Correction of the Code Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }

        self.assertIsInstance(test_request_bj, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_bj)))
        self.assertIsInstance(test_request_bj["BJ"], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_bj["BJ"])))
        self.assertEqual(list(test_request_bj.keys()), ["BJ"], "Expected parent key does not match output, got {}.".format(list(test_request_bj.keys())))
        for row in test_request_bj["BJ"]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_bj["BJ"]), 3, "Expected there to be 3 elements in output object, got {}.".format(len(test_request_bj["BJ"])))
        self.assertEqual(test_request_bj["BJ"][0], test_name_bj_expected, "Expected and observed outputs do not match.")
#3.)
        test_request_tj = requests.get(self.name_base_url + test_name_tajikistan, headers=self.user_agent_header).json() #Tajikistan

        test_name_tj_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2020-11-24",
                "Description of Change in Newsletter": "Correction of the Code Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }
        
        self.assertIsInstance(test_request_tj, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_tj)))
        self.assertIsInstance(test_request_tj["TJ"], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_tj["TJ"])))
        self.assertEqual(list(test_request_tj.keys()), ["TJ"], "Expected parent key does not match output, got {}.".format(list(test_request_tj.keys())))
        for row in test_request_tj["TJ"]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_tj["TJ"]), 7, "Expected there to be 7 elements in output object, got {}.".format(len(test_request_tj["TJ"])))
        self.assertEqual(test_request_tj["TJ"][0], test_name_tj_expected, "Expected and observed outputs do not match.")
#4.)
        test_request_md = requests.get(self.name_base_url + test_name_moldova, headers=self.user_agent_header).json() #Moldova

        test_name_md_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2019-02-15",
                "Description of Change in Newsletter": "Modification of the French short name lower case.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }
        
        self.assertIsInstance(test_request_md, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_md)))
        self.assertIsInstance(test_request_md["MD"], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_md["MD"])))
        self.assertEqual(list(test_request_md.keys()), ["MD"], "Expected parent key does not match output, got {}.".format(list(test_request_md.keys())))
        for row in test_request_md["MD"]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_md["MD"]), 11, "Expected there to be 11 elements in output object, got {}.".format(len(test_request_md["MD"])))
        self.assertEqual(test_request_md["MD"][0], test_name_md_expected, "Expected and observed outputs do not match.")
#5.)
        test_request_ml_ni = requests.get(self.name_base_url + test_name_mali_nicaragua, headers=self.user_agent_header).json() #Mali, Nicaragua 

        test_name_ml_ni_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2017-11-23",
                "Description of Change in Newsletter": "Addition of regions ML-9, ML-10; update List Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }
        test_name_ml_ni_expected_2 = {
                "Code/Subdivision Change": "",
                "Date Issued": "2020-11-24",
                "Description of Change in Newsletter": "Correction of the Code Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }
        
        self.assertIsInstance(test_request_ml_ni, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_ml_ni)))
        self.assertIsInstance(test_request_ml_ni["ML"], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_ml_ni["ML"])))
        self.assertIsInstance(test_request_ml_ni["NI"], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_ml_ni["NI"])))
        self.assertEqual(list(test_request_ml_ni.keys()), ["ML", "NI"], "Expected parent key does not match output, got {}.".format(list(test_request_ml_ni.keys())))
        for code in test_request_ml_ni:
                for row in test_request_ml_ni[code]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_ml_ni["ML"]), 1, "Expected there to be 1 element in output object, got {}.".format(len(test_request_ml_ni["ML"])))
        self.assertEqual(len(test_request_ml_ni["NI"]), 3, "Expected there to be 3 elements in output object, got {}.".format(len(test_request_ml_ni["NI"])))
        self.assertEqual(test_request_ml_ni["ML"][0], test_name_ml_ni_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_ml_ni["NI"][0], test_name_ml_ni_expected_2, "Expected and observed outputs do not match.")
#6.)
        test_request_error = requests.get(self.name_base_url + test_name_error1, headers=self.user_agent_header).json() 

        self.assertIsInstance(test_request_error, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_error)))
        self.assertEqual(list(test_request_error.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error["message"], f'Country name {test_name_error1.title()} not found in the ISO 3166.', "Error message incorrect: {}.".format(test_request_error["message"]))
        self.assertEqual(test_request_error["status"], 400, "Error status code incorrect: {}.".format(test_request_error["status"]))
        self.assertEqual(test_request_error["path"], self.name_base_url + test_name_error1, "Error path incorrect: {}.".format(test_request_error["path"]))
#7.)
        test_request_error_2 = requests.get(self.name_base_url + test_name_error2, headers=self.user_agent_header).json() 

        self.assertIsInstance(test_request_error_2, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_error_2)))
        self.assertEqual(list(test_request_error_2.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error_2["message"], f'Country name {test_name_error2.title()} not found in the ISO 3166.', "Error message incorrect: {}.".format(test_request_error_2["message"]))
        self.assertEqual(test_request_error_2["status"], 400, "Error status code incorrect: {}.".format(test_request_error_2["status"]))
        self.assertEqual(test_request_error_2["path"], self.name_base_url + test_name_error2, "Error path incorrect: {}.".format(test_request_error_2["path"]))

    def test_name_year_endpoint(self):
        """ Testing varying combinations of country names with years/year ranges. """
        test_name_egypt_2014 = ("Egypt", "2014")
        test_name_indonesia_2022 = ("Indonesia", "2022")
        test_name_japan_gt_2018 = ("Japan", ">2018")
        test_name_kiribati_lesotho_lt_2012 = ("Kiribati, Lesotho", "<2012")
        test_name_malta_nepal_2007_2011 = ("Malta, Nepal", "2007-2011")
        test_name_error1 = ("ABCDEF", "2002")
        test_name_error2 = ("12345", "ABCD")
        test_name_error3 = ("blahblah", "2040")
#1.) 
        test_request_egypt_2014 = requests.get(self.name_base_url + test_name_egypt_2014[0] + "/year/" + test_name_egypt_2014[1], headers=self.user_agent_header).json() #Egypt 2014

        test_name_egypt_2014_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2014-10-29",
                "Description of Change in Newsletter": "Delete EG-HU and EG-SU; update List Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }
        
        self.assertIsInstance(test_request_egypt_2014, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_egypt_2014)))
        self.assertIsInstance(test_request_egypt_2014["EG"], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_egypt_2014["EG"])))
        self.assertEqual(list(test_request_egypt_2014.keys()), ["EG"], "Expected parent key does not match output, got {}.".format(list(test_request_egypt_2014.keys())))
        for code in test_request_egypt_2014:
                for row in test_request_egypt_2014[code]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_egypt_2014["EG"]), 1, "Expected there to be 1 element in output object, got {}.".format(len(test_request_egypt_2014["EG"])))
        self.assertEqual(test_request_egypt_2014["EG"][0], test_name_egypt_2014_expected, "Expected and observed outputs do not match.")
#2.) 
        test_request_indonesia_2022 = requests.get(self.name_base_url + test_name_indonesia_2022[0] + "/year/" + test_name_indonesia_2022[1], headers=self.user_agent_header).json() #Indonesia 2022

        test_name_indonesia_2022_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2022-11-29",
                "Description of Change in Newsletter": "Addition of provinces ID-PE, ID-PS and ID-PT; Update List Source.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }

        self.assertIsInstance(test_request_indonesia_2022, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_indonesia_2022)))
        self.assertIsInstance(test_request_indonesia_2022["ID"], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_indonesia_2022["ID"])))
        self.assertEqual(list(test_request_indonesia_2022.keys()), ["ID"], "Expected parent key does not match output, got {}.".format(list(test_request_indonesia_2022.keys())))
        for code in test_request_indonesia_2022:
                for row in test_request_indonesia_2022[code]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_indonesia_2022["ID"]), 1, "Expected there to be 1 element in output object, got {}.".format(len(test_request_indonesia_2022["ID"])))
        self.assertEqual(test_request_indonesia_2022["ID"][0], test_name_indonesia_2022_expected, "Expected and observed outputs do not match.")
#3.) 
        test_request_japan_gt_2018 = requests.get(self.name_base_url + test_name_japan_gt_2018[0] + "/year/" + test_name_japan_gt_2018[1], headers=self.user_agent_header).json() #Japan >2018

        test_name_japan_gt_2018_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2018-11-26",
                "Description of Change in Newsletter": "Correction of the romanization system label.",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }

        self.assertIsInstance(test_request_japan_gt_2018, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_japan_gt_2018)))
        self.assertIsInstance(test_request_japan_gt_2018["JP"], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_japan_gt_2018["JP"])))
        self.assertEqual(list(test_request_japan_gt_2018.keys()), ["JP"], "Expected parent key does not match output, got {}.".format(list(test_request_japan_gt_2018.keys())))
        for code in test_request_japan_gt_2018:
                for row in test_request_japan_gt_2018[code]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_japan_gt_2018["JP"]), 1, "Expected there to be 1 element in output object, got {}.".format(len(test_request_japan_gt_2018["JP"])))
        self.assertEqual(test_request_japan_gt_2018["JP"][0], test_name_japan_gt_2018_expected, "Expected and observed outputs do not match.")
#4.)
        test_request_kiribati_lesotho_lt_2012 = requests.get(self.name_base_url + test_name_kiribati_lesotho_lt_2012[0] + "/year/" + test_name_kiribati_lesotho_lt_2012[1], headers=self.user_agent_header).json() #Kiribati, Lesotho <2012

        test_name_kiribati_lesotho_lt_2012_expected = {
                "Code/Subdivision Change": "",
                "Date Issued": "2009-03-03",
                "Description of Change in Newsletter": "Addition of administrative language Gilbertese (-, gil).",
                "Edition/Newsletter": "Online Browsing Platform (OBP)."
                }
        test_name_kiribati_lesotho_lt_2012_expected_2 = {
                "Code/Subdivision Change": "",
                "Date Issued": "2011-12-13 (corrected 2011-12-15)",
                "Description of Change in Newsletter": "Addition of local generic administrative term, update of the official languages according to ISO 3166-2 and source list update.",
                "Edition/Newsletter": "Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf)."
                }
        
        self.assertIsInstance(test_request_kiribati_lesotho_lt_2012, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_kiribati_lesotho_lt_2012)))
        self.assertIsInstance(test_request_kiribati_lesotho_lt_2012["KI"], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_kiribati_lesotho_lt_2012["KI"])))
        self.assertIsInstance(test_request_kiribati_lesotho_lt_2012["LS"], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_kiribati_lesotho_lt_2012["LS"])))
        self.assertEqual(list(test_request_kiribati_lesotho_lt_2012.keys()), ["KI", "LS"], "Expected parent key does not match output, got {}.".format(list(test_request_kiribati_lesotho_lt_2012.keys())))
        for code in test_request_kiribati_lesotho_lt_2012:
                for row in test_request_kiribati_lesotho_lt_2012[code]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_kiribati_lesotho_lt_2012["KI"]), 1, "Expected there to be 1 element in output object, got {}.".format(len(test_request_kiribati_lesotho_lt_2012["KI"])))
        self.assertEqual(len(test_request_kiribati_lesotho_lt_2012["LS"]), 1, "Expected there to be 3 elements in output object, got {}.".format(len(test_request_kiribati_lesotho_lt_2012["LS"])))
        self.assertEqual(test_request_kiribati_lesotho_lt_2012["KI"][0], test_name_kiribati_lesotho_lt_2012_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_kiribati_lesotho_lt_2012["LS"][0], test_name_kiribati_lesotho_lt_2012_expected_2, "Expected and observed outputs do not match.")
#5.)
        test_request_malta_nepal_2007_2011 = requests.get(self.name_base_url + test_name_malta_nepal_2007_2011[0] + "/year/" + test_name_malta_nepal_2007_2011[1], headers=self.user_agent_header).json() #Malta, Nepal 2007-2011

        test_name_malta_nepal_2007_2011_expected = {
                "Code/Subdivision Change": "Subdivisions added: 68 local councils.",
                "Date Issued": "2007-11-28",
                "Description of Change in Newsletter": "Addition of administrative subdivisions and of their code elements.",
                "Edition/Newsletter": "Newsletter I-9 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/newsletter_i-9.pdf)."
                }
        test_name_malta_nepal_2007_2011_expected_2 = {
                "Code/Subdivision Change": "",
                "Date Issued": "2011-12-13 (corrected 2011-12-15)",
                "Description of Change in Newsletter": "First level prefix addition, language adjustment, comment addition, deletion of the romanization system and source list update.",
                "Edition/Newsletter": "Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf)."
                }
        
        self.assertIsInstance(test_request_malta_nepal_2007_2011, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_malta_nepal_2007_2011)))
        self.assertIsInstance(test_request_malta_nepal_2007_2011["MT"], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_malta_nepal_2007_2011["MT"])))
        self.assertIsInstance(test_request_malta_nepal_2007_2011["NP"], list, "Expected ouput object of API updates to be of type list, got {}.".format(type(test_request_malta_nepal_2007_2011["NP"])))
        self.assertEqual(list(test_request_malta_nepal_2007_2011.keys()), ["MT", "NP"], "Expected parent key does not match output, got {}.".format(list(test_request_malta_nepal_2007_2011.keys())))
        for code in test_request_malta_nepal_2007_2011:
                for row in test_request_malta_nepal_2007_2011[code]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_malta_nepal_2007_2011["MT"]), 1, "Expected there to be 1 element in output object, got {}.".format(len(test_request_malta_nepal_2007_2011["MT"])))
        self.assertEqual(len(test_request_malta_nepal_2007_2011["NP"]), 4, "Expected there to be 4 elements in output object, got {}.".format(len(test_request_malta_nepal_2007_2011["NP"])))
        self.assertEqual(test_request_malta_nepal_2007_2011["MT"][0], test_name_malta_nepal_2007_2011_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_malta_nepal_2007_2011["NP"][0], test_name_malta_nepal_2007_2011_expected_2, "Expected and observed outputs do not match.")
#6.)
        test_request_error = requests.get(self.name_base_url + test_name_error1[0] + "/year/" + test_name_error1[1], headers=self.user_agent_header).json() #ABCDEF, 2002

        self.assertIsInstance(test_request_error, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_error)))
        self.assertEqual(list(test_request_error.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error["message"], f'Country name {test_name_error1[0].title()} not found in the ISO 3166.', "Error message incorrect: {}.".format(test_request_error["message"]))
        self.assertEqual(test_request_error["status"], 400, "Error status code incorrect: {}.".format(test_request_error["status"]))
        self.assertEqual(test_request_error["path"], self.name_base_url + test_name_error1[0] + "/year/" + test_name_error1[1], "Error path incorrect: {}.".format(test_request_error["path"]))
#7.)
        test_request_error_2 = requests.get(self.name_base_url + test_name_error2[0] + "/year/" + test_name_error2[1], headers=self.user_agent_header).json() #12345, ""

        self.assertIsInstance(test_request_error_2, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_error_2)))
        self.assertEqual(list(test_request_error_2.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error_2["message"], f'Country name {test_name_error2[0].title()} not found in the ISO 3166.', "Error message incorrect: {}.".format(test_request_error_2["message"]))
        self.assertEqual(test_request_error_2["status"], 400, "Error status code incorrect: {}.".format(test_request_error_2["status"]))
        self.assertEqual(test_request_error_2["path"], self.name_base_url + test_name_error2[0] + "/year/" + test_name_error2[1], "Error path incorrect: {}.".format(test_request_error_2["path"]))
#8.)
        test_request_error_3 = requests.get(self.name_base_url + test_name_error3[0] + "/year/" + test_name_error3[1], headers=self.user_agent_header).json() #"", ""

        self.assertIsInstance(test_request_error_3, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_error_3)))
        self.assertEqual(list(test_request_error_3.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error_3["message"], f'Country name {test_name_error3[0].title()} not found in the ISO 3166.', "Error message incorrect: {}.".format(test_request_error_3["message"]))
        self.assertEqual(test_request_error_3["status"], 400, "Error status code incorrect: {}.".format(test_request_error_3["status"]))
        self.assertEqual(test_request_error_3["path"], self.name_base_url + test_name_error3[0] + "/year/" + test_name_error3[1], "Error path incorrect: {}.".format(test_request_error_3["path"]))

    @unittest.skip("Skipping as number of results will change month by month of running tests.")
    def test_month_endpoint(self):
        """ Testing months input parameter which returns the updates in a specified month range. """
        test_month_1 = "1"
        test_month_2 = "6"
        test_month_3 = "10"
        test_month_4 = "20"
        test_month_5 = "50"
        test_month_6 = "abc"
#1.)
        test_request_month1 = requests.get(self.month_base_url + test_month_1, headers=self.user_agent_header).json() #1

        self.assertIsInstance(test_request_month1, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_month1)))
        self.assertEqual(len(test_request_month1), 0, "Expected 0 rows returned from API, got {}.".format(len(test_request_month1)))
        self.assertEqual(test_request_month1, {}, "Expected output of API to be an empty dict, got\n{}".format(test_request_month1)) 
#2.)
        test_request_month2 = requests.get(self.month_base_url + test_month_2, headers=self.user_agent_header).json() #6

        self.assertIsInstance(test_request_month2, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_month2)))
        self.assertEqual(len(test_request_month2), 12, "Expected 12 rows returned from API, got {}.".format(len(test_request_month2)))
        for alpha2 in list(test_request_month2):
                for row in range(0, len(test_request_month2[alpha2])):
                       self.assertEqual(datetime.strptime(test_request_month2[alpha2][row]["Date Issued"], '%Y-%m-%d').month, (date.today() + relativedelta(months=-6)).month,
                                        "Expected Date of country update to be within the past 6 months:\nToday: {}, Update: {}.".format(date.today(), test_request_month2[alpha2][row]["Date Issued"]))
#3.)
        test_request_month3 = requests.get(self.month_base_url + test_month_3, headers=self.user_agent_header).json() #10

        self.assertIsInstance(test_request_month3, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_month3)))
        self.assertEqual(len(test_request_month3), 11, "Expected 11 rows returned from API, got {}.".format(len(test_request_month3)))
        for alpha2 in list(test_request_month3):
                for row in range(0, len(test_request_month3[alpha2])):
                       self.assertEqual(datetime.strptime(test_request_month3[alpha2][row]["Date Issued"], '%Y-%m-%d').month, (date.today() + relativedelta(months=-10)).month,
                                        "Expected Date of country update to be within the past 10 months:\nToday: {}, Update: {}.".format(date.today(), test_request_month3[alpha2][row]["Date Issued"]))
#4.)
        test_request_month4 = requests.get(self.month_base_url + test_month_4, headers=self.user_agent_header).json() #20

        self.assertIsInstance(test_request_month4, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_month4)))
        self.assertEqual(len(test_request_month4), 21, "Expected 21 rows returned from API, got {}.".format(len(test_request_month4)))
        for alpha2 in list(test_request_month4):
                for row in range(0, len(test_request_month4[alpha2])):
                       self.assertEqual(datetime.strptime(test_request_month4[alpha2][row]["Date Issued"], '%Y-%m-%d').month, (date.today() + relativedelta(months=-20)).month,
                                        "Expected Date of country update to be within the past 20 months:\nToday: {}, Update: {}.".format(date.today(), test_request_month4[alpha2][row]["Date Issued"]))
#5.)
        test_request_month5 = requests.get(self.month_base_url + test_month_5, headers=self.user_agent_header).json() #50

        self.assertIsInstance(test_request_month5, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_month5)))
        self.assertEqual(len(test_request_month5), 59, "Expected 59 rows returned from API, got {}.".format(len(test_request_month5)))
        for alpha2 in list(test_request_month5):
                for row in range(0, len(test_request_month5[alpha2])):
                       self.assertEqual(datetime.strptime(test_request_month5[alpha2][row]["Date Issued"], '%Y-%m-%d').month, (date.today() + relativedelta(months=-50)).month,
                                        "Expected Date of country update to be within the past 50 months:\nToday: {}, Update: {}.".format(date.today(), test_request_month5[alpha2][row]["Date Issued"]))
#6.)
        test_request_month6 = requests.get(self.month_base_url + test_month_6, headers=self.user_agent_header).json() #abc

        self.assertIsInstance(test_request_month6, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_month6)))
        self.assertEqual(list(test_request_month6.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_month6["message"], "Invalid month input: " + test_month_6 + ".", "Error message incorrect: {}.".format(test_request_month6["message"]))
        self.assertEqual(test_request_month6["status"], 400, "Error status code incorrect: {}.".format(test_request_month6["status"]))
        self.assertEqual(test_request_month6["path"], self.base_url + '?months=' + test_month_6, "Error path incorrect: {}.".format(test_request_month6["path"]))

if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)