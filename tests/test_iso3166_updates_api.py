import unittest
import iso3166
import requests
import re
import os
from jsonschema import validate
from datetime import datetime
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from importlib.metadata import metadata
unittest.TestLoader.sortTestMethodsUsing = None

@unittest.skip("Skipping prior to new published release of iso3166-updates.")
class Updates_Api_Tests(unittest.TestCase):
    """
    Test suite for testing ISO 3166 Updates API created to accompany the iso3166-updates Python software package. 

    Test Cases
    ==========
    test_homepage_endpoint:
        testing main endpoint that returns the homepage and API documentation. 
    test_api_endpoints:
        testing main api endpoints/paths, validating they return correct response type and status code.
    test_all_endpoint:
        testing /all endpoint, validating that it returns updates data for all countries. 
   test_json_schema_all_endpoint:
        testing JSON schema for all data using /all endpoint.
    test_all_endpoint_duplicates:
        testing /all endpoint, validating that there are no duplicate objects.    
    test_alpha_endpoint:
        testing /alpha2 endpoint, validating correct data and output object returned, using a variety of alpha-2 codes.
    test_year_endpoint:
        testing /year endpoint, validating correct data and output object returned, using a variety of years.
    test_name_endpoint:
        testing /name endpoint, validating correct data and output object returned, using a variety of country names.
    test_search_endpoint:
        testing /search endpoint, validating correct data and output object returned, usins a variety of search terms.
    test_name_year_endpoint:
        testing /name/year endpoint, validating correct data and output object returned, using a variety of country names
        and years.
    test_alpha_year_endpoint:
        testing /alpha/year endpoint, validating correct data and output object returned, using a variety of alpha-2 codes
        and years.
    test_date_range_endpoint:
        testing /date_range endpoint, validating correct data and output object returned, using a variety of date ranges.
    test_search_endpoint:
        testing /search endpoint, validating correct data and output object returned, using a variety of search terms.
    """     
    def setUp(self):
        """ Initialise test variables including base urls for API. """
        self.base_url = "https://iso3166-updates.vercel.app/api"
        # self.base_url = "https://iso3166-updates.com/api" 

        #get version and random user-agent
        self.__version__ = metadata('iso3166_updates')['version']
        user_agent = UserAgent()
        self.user_agent_header = user_agent.random

        #base endpoint urls
        self.alpha_base_url = self.base_url + "/alpha/"
        self.year_base_url = self.base_url + '/year/'
        self.name_base_url = self.base_url + '/name/'
        self.all_base_url = self.base_url + '/all'
        self.date_range_url = self.base_url + '/date_range/'

        #correct column/key names for dict returned from api
        self.expected_output_columns = ["Change", "Date Issued", "Description of Change", "Source"]

        #turn off tqdm progress bar functionality when running tests
        os.environ["TQDM_DISABLE"] = "1"

    def test_homepage_endpoint(self):
        """ Testing contents of main '/api' endpoint that returns the homepage and API documentation. """
        test_request_main = requests.get(self.base_url, headers=self.user_agent_header, timeout=10)
        soup = BeautifulSoup(test_request_main.content, 'html.parser')
#1.)
        # version = soup.find(id='version').text.split(': ')[1]
        last_updated = soup.find(id='last-updated').text.split(': ')[1]
        author = soup.find(id='author').text.split(': ')[1]

        # self.assertEqual(version, "1.7.0", f"Expected API version to be 1.7.0, got {version}.")
        self.assertEqual(last_updated, "April 2024", f"Expected last updated date to be April 2024, got {last_updated}.")
        self.assertEqual(author, "AJ", f"Expected author to be AJ, got {author}.")
#2.)
        section_list_menu = soup.find(id='section-list-menu').find_all('li')
        correct_section_menu = ["About", "Attributes", "Endpoints", "All", "Alpha Code", "Year", "Name", "Date Range", "Contributing", "Credits"]
        for li in section_list_menu:
            self.assertIn(li.text.strip(), correct_section_menu, f"Expected list element {li} to be in list.")

    def test_all_endpoint(self):
        """ Testing '/api/all' endpoint that returns all updates data for all countries. """
        test_request_all = requests.get(self.all_base_url, headers=self.user_agent_header, timeout=10)
#1.)
        self.assertIsInstance(test_request_all.json(), dict, f"Expected output object of API to be of type dict, got {type(test_request_all.json())}.")
        self.assertEqual(len(test_request_all.json()), 249, f"Expected there to be 249 elements in output object, got {len(test_request_all.json())}.")
        self.assertEqual(test_request_all.status_code, 200, f"Expected 200 status code from request, got {test_request_all.status_code}.")
        self.assertEqual(test_request_all.headers["content-type"], "application/json", f"Expected Content type to be application/json, got {test_request_all.headers['content-type']}.")

    def test_json_schema_all_endpoint(self):
        """ Testing the JSON schema for all the data, using the /all endpoint. """
        test_request_all = requests.get(self.all_base_url, headers=self.user_agent_header, timeout=10)
        schema = {
            "type": "object",
            "patternProperties": {
                "^[A-Z]{2}$": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "Change": {"type": "string"},
                            "Description of Change": {"type": "string"},
                            "Date Issued": {"type": "string"},
                            "Source": {"type": "string"},
                        },
                        "required": ["Change", "Date Issued", "Source"],
                    },
                }
            },
        }
#1.)
        self.assertTrue(validate(instance=test_request_all, schema=schema), "Expected and observed schema for API output using /all endpoint does not match.")

    def test_all_endpoint_duplicates(self):
        """ Testing '/api/all' endpoint has no duplicate updates objects. """
        test_request_all = requests.get(self.all_base_url, headers=self.user_agent_header, timeout=10)
#1.)
        for country_code, updates in test_request_all.json():
            unique_updates = {frozenset(update.items()) for update in updates}
            self.assertEqual(len(unique_updates), len(updates), f"Duplicates found in updates for country {country_code}:\n{updates}")

    def test_alpha_endpoint(self):
        """ Testing '/api/alpha' endpoint using single, multiple and invalid alpha codes for expected ISO 3166 updates. """
        test_alpha_ad = "AD" #Andorra 
        test_alpha_bo = "BO" #Bolivia
        test_alpha_co = "COL" #Colombia
        test_alpha_bf = "854" #Burkina Faso
        test_alpha_bn_cu_dm = "BN,CUB,262" #Brunei, Cuba, Djibouti 
        error_test_alpha_1 = "blahblahblah"
        error_test_alpha_2 = "42"
        error_test_alpha_3 = "XYZ" #invalid alpha-3 code
#1.)
        test_request_ad = requests.get(self.alpha_base_url + test_alpha_ad, headers=self.user_agent_header, timeout=10).json() #AD
        
        #expected test outputs
        test_alpha_ad_expected1 = {
                "Change": "Update List Source.",
                "Date Issued": "2015-11-27",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:AD)."
                }
        test_alpha_ad_expected2 = {
                "Change": "Update List Source.",
                "Date Issued": "2014-11-03",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:AD)."
                }

        self.assertIsInstance(test_request_ad, dict, f"Expected output object of API to be of type dict, got {type(test_request_ad)}.")
        self.assertIsInstance(test_request_ad[test_alpha_ad], list, f"Expected output object of API updates to be of type list, got {type(test_request_ad[test_alpha_ad])}.")
        self.assertEqual(list(test_request_ad.keys()), [test_alpha_ad], f"Expected parent key does not match output, got {list(test_request_ad.keys())}.")
        for row in test_request_ad[test_alpha_ad]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(row.keys())}.")
        self.assertEqual(len(test_request_ad[test_alpha_ad]), 3, f"Expected there to be 3 elements in output object, got {len(test_request_ad[test_alpha_ad])}.")
        self.assertEqual(test_request_ad[test_alpha_ad][0], test_alpha_ad_expected1, f"Expected and observed outputs do not match:\n{test_request_ad[test_alpha_ad][0]}.")
        self.assertEqual(test_request_ad[test_alpha_ad][1], test_alpha_ad_expected2, f"Expected and observed outputs do not match:\n{test_request_ad[test_alpha_ad][1]}.")
#2.)
        test_request_bo = requests.get(self.alpha_base_url + test_alpha_bo, headers=self.user_agent_header, timeout=10).json() #BO
        
        #expected test outputs
        test_alpha_bo_expected1 = {
                "Change": "Change of short name upper case: replace the parentheses with a coma.",
                "Date Issued": "2024-02-29",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:BO)."
                }
        test_alpha_bo_expected2 = {
                "Change": "Alignment of the English and French short names upper and lower case with UNTERM.",
                "Date Issued": "2014-12-18",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:BO)."
                }
        
        self.assertIsInstance(test_request_bo, dict, f"Expected output object of API to be of type dict, got {type(test_request_bo)}.")
        self.assertIsInstance(test_request_bo[test_alpha_bo], list, f"Expected output object of API updates to be of type list, got {type(test_request_bo[test_alpha_bo])}.")
        self.assertEqual(list(test_request_bo.keys()), [test_alpha_bo], f"Expected parent key does not match output, got {list(test_request_bo.keys())}.")
        for row in test_request_bo[test_alpha_bo]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(row.keys())}.")
        self.assertEqual(len(test_request_bo[test_alpha_bo]), 6, f"Expected there to be 6 elements in output object, got {len(test_request_bo[test_alpha_bo])}.")
        self.assertEqual(test_request_bo[test_alpha_bo][0], test_alpha_bo_expected1, f"Expected and observed outputs do not match:\n{test_request_bo[test_alpha_bo][0]}")
        self.assertEqual(test_request_bo[test_alpha_bo][1], test_alpha_bo_expected2, f"Expected and observed outputs do not match:\n{test_request_bo[test_alpha_bo][1]}")
#3.)
        test_request_co = requests.get(self.alpha_base_url + test_alpha_co, headers=self.user_agent_header, timeout=10).json() #COL

        #expected test outputs
        test_alpha_co_expected1 = {
                "Change": "Addition of local variation of CO-DC, CO-SAP, CO-VAC; update list source.",
                "Date Issued": "2016-11-15",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:CO)."
                }
        test_alpha_co_expected2 = {
                "Change": "Change of name of CO-DC.",
                "Date Issued": "2004-03-08",
                "Description of Change": "",
                "Source": "Newsletter I-6 (https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf)."
                }       

        self.assertIsInstance(test_request_co, dict, f"Expected output object of API to be of type dict, got {type(test_request_co)}.")
        self.assertIsInstance(test_request_co["CO"], list, f"Expected output object of API updates to be of type list, got {type(test_request_co['CO'])}.")
        self.assertEqual(list(test_request_co.keys()), ["CO"], f"Expected parent key does not match output, got {list(test_request_co.keys())}.")
        for row in test_request_co["CO"]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(row.keys())}.")
        self.assertEqual(len(test_request_co["CO"]), 2, f"Expected there to be 2 elements in output object, got {len(test_request_co['CO'])}.")
        self.assertEqual(test_request_co["CO"][0], test_alpha_co_expected1, f"Expected and observed outputs do not match:\n{test_request_co['CO'][0]}")
        self.assertEqual(test_request_co["CO"][1], test_alpha_co_expected2, f"Expected and observed outputs do not match:\n{test_request_co['CO'][1]}")
#4.)
        test_request_bf = requests.get(self.alpha_base_url + test_alpha_bf, headers=self.user_agent_header, timeout=10).json() #854
        
        #expected test outputs
        test_alpha_bf_expected1 = {
                "Change": "Spelling change: BF-TUI Tui -> Tuy.",
                "Date Issued": "2016-11-15",
                "Description of Change": "Change of spelling of BF-TUI; update list source.",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:BF)."
                }
        test_alpha_bf_expected2 = {
                "Change": "Correction of the short name lowercase in French.",
                "Date Issued": "2014-04-15",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:BF)."
                }         

        self.assertIsInstance(test_request_bf, dict, f"Expected output object of API to be of type dict, got {type(test_request_bf)}.")
        self.assertIsInstance(test_request_bf["BF"], list, f"Expected output object of API updates to be of type list, got {type(test_request_bf['BF'])}.")
        self.assertEqual(list(test_request_bf.keys()), ["BF"], f"Expected parent key does not match output, got {list(test_request_bf.keys())}.")
        for row in test_request_bf["BF"]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(row.keys())}.")
        self.assertEqual(len(test_request_bf["BF"]), 3, f"Expected there to be 3 elements in output object, got {len(test_request_bf['BF'])}.")
        self.assertEqual(test_request_bf["BF"][0], test_alpha_bf_expected1, f"Expected and observed outputs do not match:\n{test_request_bf['BF'][0]}")
        self.assertEqual(test_request_bf["BF"][1], test_alpha_bf_expected2, f"Expected and observed outputs do not match:\n{test_request_bf['BF'][1]}")

#4.)
        test_request_bn_cu_dm = requests.get(self.alpha_base_url + test_alpha_bn_cu_dm, headers=self.user_agent_header, timeout=10).json() #BN, CUB, 262

        test_alpha_list = ['BN', 'CU', 'DJ']  
        
        #expected test outputs
        test_alpha_bn_expected = {
                "Change": "Spelling change: BN-BM Brunei-Muara -> Brunei dan Muara (ms).",
                "Date Issued": "2019-11-22",
                "Description of Change": "Change of subdivision name of BN-BM; Update List Source.",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:BN)."
                }  
        test_alpha_cu_expected = {
                "Change": "Update List Source.",
                "Date Issued": "2015-11-27",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:CU)."
                }  
        test_alpha_dj_expected = {
                "Change": "Correction of the Code Source.",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:DJ)."
                }     

        self.assertIsInstance(test_request_bn_cu_dm, dict, f"Expected output object of API to be of type dict, got {type(test_request_bn_cu_dm)}.")
        self.assertEqual(list(test_request_bn_cu_dm.keys()), test_alpha_list, f"Expected columns do not match output, got {list(test_request_bn_cu_dm.keys())}.")
        for alpha2 in test_alpha_list:
                self.assertIsInstance(test_request_bn_cu_dm[alpha2], list, f"Expected output object of API updates to be of type list, got {test_request_bn_cu_dm[alpha2]}.")
                for row in test_request_bn_cu_dm[alpha2]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(row.keys())}.")
        self.assertEqual(len(test_request_bn_cu_dm['BN']), 4, f"Expected there to be 4 rows of updates for BO, got {len(test_request_bn_cu_dm['BN'])}.")
        self.assertEqual(len(test_request_bn_cu_dm['CU']), 2, f"Expected there to be 2 rows of updates for CO, got {len(test_request_bn_cu_dm['CU'])}.")
        self.assertEqual(len(test_request_bn_cu_dm['DJ']), 6, f"Expected there to be 6 rows of updates for DM, got {len(test_request_bn_cu_dm['DJ'])}.")
        self.assertEqual(test_request_bn_cu_dm['BN'][0], test_alpha_bn_expected, f"Expected and observed outputs do not match:\n{test_request_bn_cu_dm['BN'][0]}")
        self.assertEqual(test_request_bn_cu_dm['CU'][0], test_alpha_cu_expected, f"Expected and observed outputs do not match:\n{test_request_bn_cu_dm['CU'][0]}")
        self.assertEqual(test_request_bn_cu_dm['DJ'][0], test_alpha_dj_expected, f"Expected and observed outputs do not match:\n{test_request_bn_cu_dm['DJ'][0]}")
#5.)
        test_request_error1 = requests.get(self.alpha_base_url + error_test_alpha_1, headers=self.user_agent_header, timeout=10).json() #blahblahblah

        self.assertIsInstance(test_request_error1, dict, f"Expected output object of API to be of type dict, got {type(test_request_error1)}.")
        self.assertEqual(list(test_request_error1.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error1["message"], "Invalid ISO 3166-1 alpha country code input, no corresponding alpha-2 code found: " + error_test_alpha_1.upper() + ".", f"Error message incorrect: {test_request_error1['message']}.")
        self.assertEqual(test_request_error1["status"], 400, f"Error status code incorrect: {test_request_error1['status']}.")
        self.assertEqual(test_request_error1["path"], self.alpha_base_url + error_test_alpha_1, f"Error path incorrect: {test_request_error1['path']}.")
#6.)
        test_request_error2 = requests.get(self.alpha_base_url + error_test_alpha_2, headers=self.user_agent_header, timeout=10).json() #42

        self.assertIsInstance(test_request_error2, dict, f"Expected output object of API to be of type dict, got {type(test_request_error2)}.")
        self.assertEqual(list(test_request_error2.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error2["message"], "Invalid ISO 3166-1 alpha country code input, no corresponding alpha-2 code found: " + error_test_alpha_2.upper() + ".", f"Error message incorrect: {test_request_error2['message']}.")
        self.assertEqual(test_request_error2["status"], 400, f"Error status code incorrect: {test_request_error2['status']}.")
        self.assertEqual(test_request_error2["path"], self.alpha_base_url + error_test_alpha_2, f"Error path incorrect: {test_request_error2['path']}.")
#7.)
        test_request_error3 = requests.get(self.alpha_base_url + error_test_alpha_3, headers=self.user_agent_header, timeout=10).json() #xyz

        self.assertIsInstance(test_request_error3, dict, f"Expected output object of API to be of type dict, got {type(test_request_error3)}.")
        self.assertEqual(list(test_request_error3.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error3["message"], f"Invalid ISO 3166-1 alpha-3 country code input, cannot convert into corresponding alpha-2 code: {error_test_alpha_3.upper()}.", f"Error message incorrect: {test_request_error3['message']}.")
        self.assertEqual(test_request_error3["status"], 400, f"Error status code incorrect: {test_request_error3['status']}.")
        self.assertEqual(test_request_error3["path"], self.alpha_base_url + error_test_alpha_3, f"Error path incorrect: {test_request_error3['path']}.")

    def test_year_endpoint(self): 
        """ Testing '/api/year' path/endpoint using single and multiple years, year ranges and greater than/less than and invalid years. """
        test_year_2016 = "2016"
        test_year_2007 = "2007"
        test_year_2004_2009 = "2004-2009"
        test_year_gt_2017 = ">2017"
        test_year_lt_2002 = "<2002"
        test_year_abc = "abc"
        test_year_12345 = "12345"
#1.)
        test_request_year_2016 = requests.get(self.year_base_url + test_year_2016, headers=self.user_agent_header, timeout=10).json() #2016

        #expected test outputs
        test_au_expected = {
                "Change": "Update List Source; update Code Source.",
                "Date Issued": "2016-11-15",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:AU)."
                }
        test_dz_expected = {
                "Change": "Change of spelling of DZ-28; Update list source.",
                "Date Issued": "2016-11-15",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:DZ)."
                }
        test_mv_expected = {
                "Change": "Spelling change: MV-05.",
                "Date Issued": "2016-11-15",
                "Description of Change": "Change of spelling of MV-05.",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:MV)."
                }
        test_pw_expected = {
                "Change": "Name changed: PW-050 Hatobohei -> Hatohobei.",
                "Date Issued": "2016-11-15",
                "Description of Change": "Change of spelling of PW-050 in eng, pau; update list source.",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:PW)."
                }

        #expected output keys
        test_year_2016_keys = ['AU', 'AW', 'BD', 'BF', 'BR', 'BT', 'CD', 'CI', 'CL', 'CO', 'CZ', 'DJ', 'DO', 'DZ', 'ES', 'FI', 'FJ', 
                               'FR', 'GD', 'GM', 'GR', 'ID', 'IL', 'IQ', 'KE', 'KG', 'KH', 'KR', 'KZ', 'LA', 'MM', 'MV', 'MX', 'NA', 
                               'PW', 'RW', 'SI', 'TG', 'TJ', 'TK', 'TV', 'TW', 'UG', 'YE']

        self.assertIsInstance(test_request_year_2016, dict, f"Expected output object of API to be of type dict, got {type(test_request_year_2016)}.")
        self.assertEqual(list(test_request_year_2016), test_year_2016_keys, f"Expected keys of output dict from API do not match, got {list(test_request_year_2016)}.")
        self.assertEqual(len(list(test_request_year_2016)), 44, f"Expected there to be 44 output objects from API call, got {len(list(test_request_year_2016))}.")
        for alpha2 in list(test_request_year_2016):
                for row in range(0, len(test_request_year_2016[alpha2])):
                        self.assertEqual(list(test_request_year_2016[alpha2][row].keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(test_request_year_2016[alpha2][row].keys())}.")
                        self.assertIsInstance(test_request_year_2016[alpha2][row], dict, f"Expected output row object of API to be of type dict, got {type(test_request_year_2016[alpha2][row])}.")
                        self.assertEqual(datetime.strptime(test_request_year_2016[alpha2][row]["Date Issued"], "%Y-%m-%d").year, 2016, 
                                f"Year in Date Issued column does not match expected 2016, got {datetime.strptime(test_request_year_2016[alpha2][row]['Date Issued'], '%Y-%m-%d').year}.")
        self.assertEqual(test_request_year_2016['AU'][0], test_au_expected, f"Expected and observed outputs do not match:\n{test_request_year_2016['AU'][0]}.")
        self.assertEqual(test_request_year_2016['DZ'][0], test_dz_expected, f"Expected and observed outputs do not match:\n{test_request_year_2016['DZ'][0]}.")
        self.assertEqual(test_request_year_2016['MV'][0], test_mv_expected, f"Expected and observed outputs do not match:\n{test_request_year_2016['MV'][0]}.")
        self.assertEqual(test_request_year_2016['PW'][0], test_pw_expected, f"Expected and observed outputs do not match:\n{test_request_year_2016['PW'][0]}.")
#2.)
        test_request_year_2007 = requests.get(self.year_base_url + test_year_2007, headers=self.user_agent_header, timeout=10).json() #2007
        
        #expected test outputs
        test_ag_expected = {
                "Change": "Subdivisions added: 6 parishes, 1 dependency.",
                "Date Issued": "2007-04-17",
                "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
                "Source": "Newsletter I-8 (https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)."
                }
        test_bh_expected = {
                "Change": "Subdivision layout: 12 regions (see below) -> 5 governorates.",
                "Date Issued": "2007-04-17",
                "Description of Change": "Modification of the administrative structure.",
                "Source": "Newsletter I-8 (https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)."
                }
        test_gd_expected = {
                "Change": "Subdivisions added: 6 parishes, 1 dependency.",
                "Date Issued": "2007-04-17",
                "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
                "Source": "Newsletter I-8 (https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)."
                }
        test_sm_expected = {
                "Change": "Subdivisions added: 9 municipalities.",
                "Date Issued": "2007-04-17",
                "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
                "Source": "Newsletter I-8 (https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)."
                }

        #expected key outputs
        test_year_2007_keys = ['AD', 'AG', 'BA', 'BB', 'BG', 'BH', 'BL', 'CI', 'CZ', 'DM', 'DO', 'EG', 'FR', 'GB', 'GD', 'GE', 'GG', 'GN', 'GP', 'HT', 'IM', 'IR', 
                               'IT', 'JE', 'KE', 'KN', 'KW', 'LB', 'LC', 'LI', 'LR', 'ME', 'MF', 'MK', 'MT', 'NR', 'PF', 'PW', 'RE', 'RS', 'RU', 'RW', 'SB', 'SC', 
                               'SD', 'SG', 'SM', 'TD', 'TF', 'TO', 'TV', 'UG', 'VC', 'YE', 'ZA']

        self.assertIsInstance(test_request_year_2007, dict, f"Expected output object of API to be of type dict, got {type(test_request_year_2007)}.")
        self.assertEqual(list(test_request_year_2007), test_year_2007_keys, f"Expected keys of output dict from API do not match, got {list(test_request_year_2007)}.")
        self.assertEqual(len(list(test_request_year_2007)), 55, f"Expected there to be 55 output objects from API call, got {len(list(test_request_year_2007))}.")
        for alpha2 in list(test_request_year_2007):
                for row in range(0, len(test_request_year_2007[alpha2])):
                        self.assertEqual(list(test_request_year_2007[alpha2][row].keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(test_request_year_2007[alpha2][row].keys())}.")
                        self.assertIsInstance(test_request_year_2007[alpha2][row], dict, f"Expected output row of object of API to be of type dict, got {type(test_request_year_2007[alpha2][row])}.")
                        self.assertEqual(str(datetime.strptime(test_request_year_2007[alpha2][row]["Date Issued"], "%Y-%m-%d").year), "2007", 
                                f"Year in Date Issued column does not match expected 2007, got {datetime.strptime(test_request_year_2007[alpha2][row]['Date Issued'], '%Y-%m-%d').year}.")
        self.assertEqual(test_request_year_2007['AG'][0], test_ag_expected, f"Expected and observed outputs do not match:\n{test_request_year_2007['AG'][0]}.")
        self.assertEqual(test_request_year_2007['BH'][0], test_bh_expected, f"Expected and observed outputs do not match:\n{test_request_year_2007['BH'][0]}.")
        self.assertEqual(test_request_year_2007['GD'][0], test_gd_expected, f"Expected and observed outputs do not match:\n{test_request_year_2007['GD'][0]}.")
        self.assertEqual(test_request_year_2007['SM'][0], test_sm_expected, f"Expected and observed outputs do not match:\n{test_request_year_2007['SM'][0]}.")
#3.)
        test_request_year_2004_2009 = requests.get(self.year_base_url + test_year_2004_2009, headers=self.user_agent_header, timeout=10).json() #2004-2009

        #expected test outputs
        test_af_expected = {
                "Change": "Subdivisions added: AF-DAY Dāykondī AF-PAN Panjshīr.",
                "Date Issued": "2005-09-13",
                "Description of Change": "Addition of 2 provinces. Update of list source.",
                "Source": "Newsletter I-7 (https://web.archive.org/web/20081218103217/http://www.iso.org/iso/iso_3166-2_newsletter_i-7_en.pdf)."
                }
        test_co_expected = {
                "Change": "Change of name of CO-DC.",
                "Date Issued": "2004-03-08",
                "Description of Change": "",
                "Source": "Newsletter I-6 (https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf)."
                }
        test_kp_expected = {
                "Change": "Spelling correction in header of list source.",
                "Date Issued": "2004-03-08",
                "Description of Change": "",
                "Source": "Newsletter I-6 (https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf)."
                }
        test_za_expected = {
                "Change": "Codes: Gauteng: ZA-GP -> ZA-GT KwaZulu-Natal: ZA-ZN -> ZA-NL.",
                "Date Issued": "2007-12-13",
                "Description of Change": "Second edition of ISO 3166-2 (not announced in a newsletter).",
                "Source": "ISO 3166-2:2007 (http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=39718)."
                }

        #expected key outputs
        test_year_2004_2009_keys = ['AD', 'AF', 'AG', 'AL', 'AU', 'BA', 'BB', 'BG', 'BH', 'BL', 'BO', 'CF', 'CI', 'CN', 'CO', 'CZ', 'DJ', 'DM', 'DO', 'EG', 'FR', 
                                    'GB', 'GD', 'GE', 'GG', 'GL', 'GN', 'GP', 'HT', 'ID', 'IM', 'IR', 'IT', 'JE', 'KE', 'KI', 'KM', 'KN', 'KP', 'KW', 'LB', 'LC', 
                                    'LI', 'LR', 'MA', 'MD', 'ME', 'MF', 'MG', 'MK', 'MT', 'NG', 'NP', 'NR', 'PF', 'PS', 'PW', 'RE', 'RS', 'RU', 'RW', 'SB', 'SC', 
                                    'SD', 'SG', 'SI', 'SM', 'TD', 'TF', 'TN', 'TO', 'TV', 'UG', 'VC', 'VE', 'VN', 'YE', 'ZA']
        
        self.assertIsInstance(test_request_year_2004_2009, dict, f"Expected output object of API to be of type dict, got {type(test_request_year_2004_2009)}.")
        self.assertEqual(list(test_request_year_2004_2009), test_year_2004_2009_keys, f"Expected keys of output dict from API do not match, got {list(test_request_year_2004_2009)}.")
        self.assertEqual(len(list(test_request_year_2004_2009)), 78, f"Expected there to be 78 output objects from API call, got {len(list(test_request_year_2004_2009))}.")
        for alpha2 in list(test_request_year_2004_2009):
                for row in range(0, len(test_request_year_2004_2009[alpha2])):
                        self.assertEqual(list(test_request_year_2004_2009[alpha2][row].keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(test_request_year_2004_2009[alpha2][row].keys())}.")
                        self.assertIsInstance(test_request_year_2004_2009[alpha2][row], dict, f"Expected output row of object of API to be of type dict, got {type(test_request_year_2004_2009[alpha2][row])}.")
                        self.assertTrue((datetime.strptime(test_request_year_2004_2009[alpha2][row]["Date Issued"], "%Y-%m-%d").year >= 2004 and \
                                          (datetime.strptime(test_request_year_2004_2009[alpha2][row]["Date Issued"], "%Y-%m-%d").year <= 2009)), 
                                          f"Year in Date Issued column does not match expected 2004-2009, got {datetime.strptime(test_request_year_2004_2009[alpha2][row]['Date Issued'], '%Y-%m-%d').year}.")
        self.assertEqual(test_request_year_2004_2009['AF'][0], test_af_expected, f"Expected and observed outputs do not match:\n{test_request_year_2004_2009['AF'][0]}.")
        self.assertEqual(test_request_year_2004_2009['CO'][0], test_co_expected, f"Expected and observed outputs do not match:\n{test_request_year_2004_2009['CO'][0]}.")
        self.assertEqual(test_request_year_2004_2009['KP'][0], test_kp_expected, f"Expected and observed outputs do not match:\n{test_request_year_2004_2009['KP'][0]}.")
        self.assertEqual(test_request_year_2004_2009['ZA'][0], test_za_expected, f"Expected and observed outputs do not match:\n{test_request_year_2004_2009['ZA'][0]}.")
#4.)    
        test_request_year_gt_2017 = requests.get(self.year_base_url + test_year_gt_2017, headers=self.user_agent_header, timeout=10).json() #>2017

        #expected test outputs
        test_cl_expected = {
                "Change": "Subdivisions added: CL-NB Ñuble.",
                "Date Issued": "2018-11-26",
                "Description of Change": "Addition of region CL-NB; Update List Source.",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:CL)."
                }
        test_gh_expected = {
                "Change": "Correction of the Code Source.",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:GH)."
                }
        test_sa_expected = {
                "Change": "Change of subdivision category from province to region.",
                "Date Issued": "2018-11-26",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:SA)."
                }
        test_ve_expected = {
                "Change": "Change of short name upper case: replace the parentheses with a coma.",
                "Date Issued": "2024-02-29",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:VE)."
                }

        #expected key outputs
        test_year_gt_2017_keys = ['AF', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AS', 'AW', 'AX', 'BA', 'BD', 'BG', 'BI', 'BJ', 'BL', 'BM', 'BN', 'BO', 
                                  'BQ', 'BR', 'BS', 'BT', 'BV', 'BW', 'BY', 'CC', 'CD', 'CH', 'CI', 'CK', 'CL', 'CN', 'CV', 'CW', 'CX', 'CY', 
                                  'CZ', 'DE', 'DJ', 'DZ', 'EC', 'EE', 'EH', 'ER', 'ES', 'ET', 'FI', 'FK', 'FM', 'FO', 'FR', 'GB', 'GE', 'GF', 
                                  'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GR', 'GS', 'GT', 'GU', 'GW', 'GY', 'HK', 'HM', 'HU', 'ID', 
                                  'IL', 'IM', 'IN', 'IO', 'IQ', 'IR', 'IS', 'IT', 'JE', 'JP', 'KG', 'KH', 'KM', 'KP', 'KR', 'KY', 'KZ', 'LA', 
                                  'LB', 'LK', 'LS', 'LT', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MF', 'MH', 'MK', 'ML', 'MM', 'MN', 'MO', 'MP', 
                                  'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW', 'MX', 'NA', 'NC', 'NF', 'NI', 'NL', 'NO', 'NP', 'NR', 'NU', 'NZ', 
                                  'PA', 'PE', 'PF', 'PH', 'PK', 'PL', 'PM', 'PN', 'PR', 'QA', 'RE', 'RS', 'RU', 'SA', 'SB', 'SC', 'SD', 'SI', 
                                  'SJ', 'SL', 'SM', 'SS', 'ST', 'SX', 'SY', 'SZ', 'TC', 'TD', 'TF', 'TG', 'TH', 'TJ', 'TK', 'TL', 'TN', 'TR', 
                                  'TT', 'TW', 'TZ', 'UA', 'UG', 'UM', 'UZ', 'VA', 'VE', 'VG', 'VI', 'VN', 'WF', 'YE', 'YT', 'ZA', 'ZM']

        self.assertIsInstance(test_request_year_gt_2017, dict, f"Expected output object of API to be of type dict, got {type(test_request_year_gt_2017)}.")
        self.assertEqual(list(test_request_year_gt_2017), test_year_gt_2017_keys, f"Expected keys of output dict from API do not match, got {list(test_request_year_gt_2017)}.")
        self.assertEqual(len(list(test_request_year_gt_2017)), 179, f"Expected there to be 179 output objects from API call, got {len(list(test_request_year_gt_2017))}.")
        for alpha2 in list(test_request_year_gt_2017):
                for row in range(0, len(test_request_year_gt_2017[alpha2])):
                        self.assertEqual(list(test_request_year_gt_2017[alpha2][row].keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(test_request_year_gt_2017[alpha2][row].keys())}.")
                        self.assertIsInstance(test_request_year_gt_2017[alpha2][row], dict, f"Expected output row of object of API to be of type dict, got {type(test_request_year_gt_2017[alpha2][row])}.")
                        self.assertTrue(datetime.strptime(test_request_year_gt_2017[alpha2][row]["Date Issued"], "%Y-%m-%d").year >= 2017,
                                f"Year in Date Issued column should be greater than 2017, got {datetime.strptime(test_request_year_gt_2017[alpha2][row]['Date Issued'], '%Y-%m-%d').year}.")
        self.assertEqual(test_request_year_gt_2017['CL'][0], test_cl_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_gt_2017['GH'][0], test_gh_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_gt_2017['SA'][0], test_sa_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_year_gt_2017['VE'][0], test_ve_expected, "Expected and observed outputs do not match.")
#5.)    
        test_request_year_lt_2002 = requests.get(self.year_base_url + test_year_lt_2002, headers=self.user_agent_header, timeout=10).json() #<2002

        #expected test outputs
        test_ca_expected = {
                "Change": "Subdivisions added: CA-NU Nunavut.",
                "Date Issued": "2000-06-21",
                "Description of Change": "Addition of 1 new territory.",
                "Source": "Newsletter I-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf)."
                }
        test_it_expected = {
                "Change": "Correction of spelling mistakes of names of 2 provinces.",
                "Date Issued": "2000-06-21",
                "Description of Change": "",
                "Source": "Newsletter I-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf)."
                }
        test_ro_expected = {
                "Change": "Correction of spelling mistake of subdivision category in header.",
                "Date Issued": "2000-06-21",
                "Description of Change": "",
                "Source": "Newsletter I-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf)."
                }
        test_tr_expected = {
                "Change": "Subdivisions added: TR-80 Osmaniye.",
                "Date Issued": "2000-06-21",
                "Description of Change": "Addition of 1 new province. Correction of 2 spelling errors.",
                "Source": "Newsletter I-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf)."
                }

        #expected key outputs
        test_year_lt_2002_keys = ['BY', 'CA', 'DO', 'ER', 'ES', 'IT', 'KR', 'NG', 'PL', 'RO', 'RU', 'TR', 'VA', 'VN']

        self.assertIsInstance(test_request_year_lt_2002, dict, f"Expected output object of API to be of type dict, got {type(test_request_year_lt_2002)}.")
        self.assertEqual(list(test_request_year_lt_2002), test_year_lt_2002_keys, f"Expected keys of output dict from API do not match, got {list(test_request_year_lt_2002)}.")
        self.assertEqual(len(list(test_request_year_lt_2002)), 14, f"Expected there to be 14 output objects from API call, got {len(list(test_request_year_lt_2002))}.")
        for alpha2 in list(test_request_year_lt_2002):
                for row in range(0, len(test_request_year_lt_2002[alpha2])):
                        self.assertEqual(list(test_request_year_lt_2002[alpha2][row].keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(test_request_year_lt_2002[alpha2][row].keys())}.")
                        self.assertIsInstance(test_request_year_lt_2002[alpha2][row], dict, f"Expected output row of object of API to be of type dict, got {type(test_request_year_lt_2002[alpha2][row])}.")
                        self.assertTrue(datetime.strptime(test_request_year_lt_2002[alpha2][row]["Date Issued"], "%Y-%m-%d").year < 2002,
                                f"Year in Date Issued column should be less than 2002, got {datetime.strptime(test_request_year_lt_2002[alpha2][row]['Date Issued'], '%Y-%m-%d').year}.")
        self.assertEqual(test_request_year_lt_2002['CA'][0], test_ca_expected, f"Expected and observed outputs do not match:\n{test_request_year_lt_2002['CA'][0]}.")
        self.assertEqual(test_request_year_lt_2002['IT'][0], test_it_expected, f"Expected and observed outputs do not match:\n{test_request_year_lt_2002['IT'][0]}.")
        self.assertEqual(test_request_year_lt_2002['RO'][0], test_ro_expected, f"Expected and observed outputs do not match:\n{test_request_year_lt_2002['RO'][0]}.")
        self.assertEqual(test_request_year_lt_2002['TR'][0], test_tr_expected, f"Expected and observed outputs do not match:\n{test_request_year_lt_2002['TR'][0]}.")
#6.) 
        test_request_year_abc = requests.get(self.year_base_url + test_year_abc, headers=self.user_agent_header, timeout=10).json() #abc
        
        self.assertIsInstance(test_request_year_abc, dict, f"Expected output object of API to be of type dict, got {type(test_request_year_abc)}.")
        self.assertEqual(list(test_request_year_abc.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_year_abc["message"], f"Invalid year input {test_year_abc}, year should be >=1996 and <=2024.", f"Error message incorrect: {test_request_year_abc['message']}.")
        self.assertEqual(test_request_year_abc["status"], 400, f"Error status code incorrect: {test_request_year_abc['status']}.")
        self.assertEqual(test_request_year_abc["path"], self.year_base_url + test_year_abc, f"Error path incorrect: {test_request_year_abc['path']}.")
#7.) 
        test_request_year_12345 = requests.get(self.year_base_url + test_year_12345, headers=self.user_agent_header, timeout=10).json() #1234

        self.assertIsInstance(test_request_year_12345, dict, f"Expected output object of API to be of type dict, got {type(test_request_year_12345)}.")
        self.assertEqual(list(test_request_year_12345.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_year_12345["message"], f"Invalid year input {test_year_12345.upper()}  year should be >=1996 and <=2024.", f"Error message incorrect: {test_request_year_12345['message']}.")
        self.assertEqual(test_request_year_12345["status"], 400, f"Error status code incorrect: {test_request_year_12345['status']}.")
        self.assertEqual(test_request_year_12345["path"], self.year_base_url + test_year_12345, f"Error path incorrect: {test_request_year_12345['path']}.")
    
    def test_alpha_year_endpoint(self):
        """ Testing '/api/alpha/year' path/endpoint, using various combinations of alpha codes with years, and year ranges. """
        test_ad_2015 = ("AD", "2015") #Andorra 2015
        test_es_2002 = ("ESP", "2002") #Spain 2002
        test_tr_2002 = ("TR", ">2002") #Turkey <2011
        test_ma_mh_nr_lt_2019 = ("MA,MHL,520", "<2019") #Morocco, Marshall Islands, Nauru <2019
        test_ve_2021_2023 = ("VE", "2021-2023") #Venezuela 2021-2023
        test_abc_2000 = ("abc", "2000") 
#1.)
        test_ad_2015_request = requests.get(f"{self.alpha_base_url}{test_ad_2015[0]}/year/{test_ad_2015[1]}", headers=self.user_agent_header, timeout=10).json() #Andorra - 2015
        
        #expected test outputs
        test_ad_2015_expected = {
                "Change": "Update List Source.",
                "Date Issued": "2015-11-27",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:AD)."
                }

        self.assertIsInstance(test_ad_2015_request, dict, f"Expected output object of API to be of type dict, got {type(test_ad_2015_request)}.")
        self.assertEqual(list(test_ad_2015_request), ['AD'], f"Expected AD to be the only key returned from API in dict, got {list(test_ad_2015_request)}.")
        self.assertEqual(len(test_ad_2015_request), 1, f"Expected 1 row returned from API, got {len(test_ad_2015_request)}.")
        for alpha2 in list(test_ad_2015_request):
                for row in range(0, len(test_ad_2015_request[alpha2])):
                        self.assertEqual(list(test_ad_2015_request[alpha2][row].keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(test_ad_2015_request[alpha2][row].keys())}.")
                        self.assertIsInstance(test_ad_2015_request[alpha2][row], dict, f"Expected output row of object of API to be of type dict, got {type(test_ad_2015_request[alpha2][row])}.")
                        self.assertEqual(datetime.strptime(test_ad_2015_request[alpha2][row]["Date Issued"], "%Y-%m-%d").year, 2015, 
                                f"Year in Date Issued column does not match expected 2015, got {datetime.strptime(test_ad_2015_request[alpha2][row]['Date Issued'], '%Y-%m-%d'.year)}.")
        self.assertIsInstance(test_ad_2015_request[test_ad_2015[0]], list, f"Expected output object of API to be of type list, got {type(test_ad_2015_request[test_ad_2015[0]])}.")
        self.assertEqual(test_ad_2015_expected, test_ad_2015_request[test_ad_2015[0]][0], f"Observed and expected outputs of API do not match.")
#2.) 
        test_es_2002_request = requests.get(f"{self.alpha_base_url}{test_es_2002[0]}/year/{test_es_2002[1]}", headers=self.user_agent_header, timeout=10).json() #Spain - 2002

        #expected test outputs
        test_es_2002_expected = {
                "Change": "Error correction: Regional subdivision indicator corrected in ES-PM.",
                "Date Issued": "2002-12-10",
                "Description of Change": "",
                "Source": "Newsletter I-4 (https://web.archive.org/web/20081218103210/http://www.iso.org/iso/iso_3166-2_newsletter_i-4_en.pdf)."
                }

        self.assertIsInstance(test_es_2002_request, dict, f"Expected output object of API to be of type dict, got {type(test_es_2002_request)}.")
        self.assertEqual(list(test_es_2002_request), ['ES'], f"Expected ES to be the only key returned from API in dict, got {list(test_es_2002_request)}.")
        self.assertEqual(len(test_es_2002_request), 1, f"Expected 1 row returned from API, got {len(test_es_2002_request)}.")
        for alpha2 in list(test_es_2002_request):
                for row in range(0, len(test_es_2002_request[alpha2])):
                        self.assertEqual(list(test_es_2002_request[alpha2][row].keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(test_es_2002_request[alpha2][row].keys())}.")
                        self.assertIsInstance(test_es_2002_request[alpha2][row], dict, f"Expected output row of object of API to be of type dict, got {type(test_es_2002_request[alpha2][row])}.")
                        self.assertEqual(datetime.strptime(test_es_2002_request[alpha2][row]["Date Issued"], "%Y-%m-%d").year, 2002, 
                                f"Year in Date Issued column does not match expected 2002, got {datetime.strptime(test_es_2002_request[alpha2][row]['Date Issued'], '%Y-%m-%d').year}.")
        self.assertIsInstance(test_es_2002_request["ES"], list, f"Expected output object of API to be of type list, got {type(test_es_2002_request['ES'])}.")
        self.assertEqual(test_es_2002_expected, test_es_2002_request["ES"][0], "Observed and expected outputs of API do not match.")
#3.) 
        test_tr_gt_2002_request = requests.get(f"{self.alpha_base_url}{test_tr_2002[0]}/year/{test_tr_2002[1]}", headers=self.user_agent_header, timeout=10).json() #Turkey - >2002
        
        #expected test outputs 
        test_tr_gt_2002_expected = {
                "Change": "Change of the short and full name.",
                "Date Issued": "2022-07-11",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:TR)."
                }
                
        self.assertIsInstance(test_tr_gt_2002_request, dict, f"Expected output object of API to be of type dict, got {type(test_tr_gt_2002_request)}.")
        self.assertEqual(list(test_tr_gt_2002_request), ['TR'], f"Expected TR to be the only key returned from API in dict, got {list(test_tr_gt_2002_request)}.")
        self.assertEqual(len(test_tr_gt_2002_request), 1, f"Expected 1 row returned from API, got {len(test_tr_gt_2002_request)}.")
        for alpha2 in list(test_tr_gt_2002_request):
                for row in range(0, len(test_tr_gt_2002_request[alpha2])):
                        self.assertEqual(list(test_tr_gt_2002_request[alpha2][row].keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(test_tr_gt_2002_request[alpha2][row].keys())}.")
                        self.assertIsInstance(test_tr_gt_2002_request[alpha2][row], dict, f"Expected output row of object of API to be of type dict, got {type(test_tr_gt_2002_request[alpha2][row])}.")
                        self.assertTrue(datetime.strptime(re.sub("[(].*[)]", "", test_tr_gt_2002_request[alpha2][row]["Date Issued"]).replace(' ', "").replace(".", ''), '%Y-%m-%d').year >= 2002, 
                                f"Expected year of updates output to be greater than 2002, got {test_tr_gt_2002_request[alpha2][row]['Date Issued']}.")  
        self.assertIsInstance(test_tr_gt_2002_request[test_tr_2002[0]], list, f"Expected output object of API to be of type list, got {type(test_tr_gt_2002_request[test_tr_2002[0]])}.")
        self.assertEqual(test_tr_gt_2002_expected, test_tr_gt_2002_request[test_tr_2002[0]][0], "Observed and expected outputs of API do not match.")
#4.)
        test_ma_mh_nr_lt_2019_request = requests.get(f"{self.alpha_base_url}{test_ma_mh_nr_lt_2019[0]}/year/{test_ma_mh_nr_lt_2019[1]}", headers=self.user_agent_header, timeout=10).json() #Morocco, Marshall Islands, Nauru - <2019

        #expected test outputs
        test_ma_lt_2019_expected = {
                "Change": "Spelling change: MA-05 Béni-Mellal-Khénifra -> Béni Mellal-Khénifra Location change: MA-ESM Es-Semara (EH) -> Es-Semara (EH-partial).",
                "Date Issued": "2018-11-26",
                "Description of Change": "Change of spelling of MA-05; Change of (EH) to (EH-partial) for MA-ESM; Correction of the romanization system label.",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:MA)."
                }
        test_mh_lt_2019_expected = {
                "Change": "Change of spelling of subdivision name in mah of MH‐ALK, MH‐ALL, MH‐ARN, MH‐EBO, MH‐JAB, MH‐JAL, MH‐KWA, MH‐LIB, MH‐MAJ, MH‐MAL, MH‐MEJ, MH‐MIL, MH‐NMK, MH‐NMU, MH‐RON, MH‐UTI, MH‐WTH, WTJ; in mah/eng of MH-ENI, MH-KIL; update List Source.",
                "Date Issued": "2017-11-23",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:MH)."
                }
        test_nr_lt_2019_expected = {
                "Change": "Name changed: NR-05 Baiti -> Baitsi.",
                "Date Issued": "2017-11-23",
                "Description of Change": "Change of subdivision name of NR-05; addition of local variation of NR-05, update List Source.",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:NR)."
                }
        
        self.assertIsInstance(test_ma_mh_nr_lt_2019_request, dict, f"Expected output object of API to be of type dict, got {type(test_ma_mh_nr_lt_2019_request)}.")
        self.assertEqual(list(test_ma_mh_nr_lt_2019_request), ['MA', 'MH', 'NR'], f"Expected the output keys returned to be MA, MH and NR from API in dict, got {list(test_ma_mh_nr_lt_2019_request)}.")
        self.assertEqual(len(test_ma_mh_nr_lt_2019_request), 3, f"Expected 3 rows returned from API, got {len(test_ma_mh_nr_lt_2019_request)}.")
        for alpha2 in list(test_ma_mh_nr_lt_2019_request):
                for row in range(0, len(test_ma_mh_nr_lt_2019_request[alpha2])):
                        self.assertEqual(list(test_ma_mh_nr_lt_2019_request[alpha2][row].keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(test_ma_mh_nr_lt_2019_request[alpha2][row].keys())}.")
                        self.assertIsInstance(test_ma_mh_nr_lt_2019_request[alpha2][row], dict, f"Expected output row of object of API to be of type dict, got {type(test_ma_mh_nr_lt_2019_request[alpha2][row])}.")
                        self.assertTrue(datetime.strptime(re.sub("[(].*[)]", "", test_ma_mh_nr_lt_2019_request[alpha2][row]["Date Issued"]).replace(' ', "").replace(".", ''), '%Y-%m-%d').year < 2019, 
                                f"Expected year of updates output to be less than 2019, got {re.sub('[(].*[)]', '', test_ma_mh_nr_lt_2019_request[alpha2][row]['Date Issued']).replace(' ', '').replace('.', '')}.")  

        self.assertEqual(test_ma_lt_2019_expected, test_ma_mh_nr_lt_2019_request["MA"][0], "Observed and expected outputs of API do not match.") 
        self.assertEqual(test_mh_lt_2019_expected, test_ma_mh_nr_lt_2019_request["MH"][0], "Observed and expected outputs of API do not match.") 
        self.assertEqual(test_nr_lt_2019_expected, test_ma_mh_nr_lt_2019_request["NR"][0], "Observed and expected outputs of API do not match.") 
#5.)
        test_ve_2021_2023_request = requests.get(f"{self.alpha_base_url}{test_ve_2021_2023[0]}/year/{test_ve_2021_2023[1]}", headers=self.user_agent_header, timeout=10).json() #Venezuela - 2021-2023

        self.assertIsInstance(test_ve_2021_2023_request, dict, f"Expected output object of API to be of type dict, got {type(test_ve_2021_2023_request)}.")
        self.assertEqual(len(test_ve_2021_2023_request), 0, f"Expected 0 rows returned from API, got {len(test_ve_2021_2023_request)}.")
        self.assertEqual(test_ve_2021_2023_request, {}, f"Expected output of API to be an empty dict, got\n{test_ve_2021_2023_request}")
#6.) 
        test_abc_2000_request = requests.get(f"{self.alpha_base_url}{test_abc_2000[0]}/year/{test_abc_2000[1]}", headers=self.user_agent_header, timeout=10).json() #abc - 2000
        
        self.assertIsInstance(test_abc_2000_request, dict, f"Expected output object of API to be of type dict, got {type(test_abc_2000_request)}.")
        self.assertEqual(list(test_abc_2000_request.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_abc_2000_request["message"], f"Invalid ISO 3166-1 alpha-3 country code input, cannot convert into corresponding alpha-2 code: {test_abc_2000[0].upper()}.", f"Error message incorrect: {test_abc_2000_request['message']}.")
        self.assertEqual(test_abc_2000_request["status"], 400, f"Error status code incorrect: {test_abc_2000_request['status']}.")
        self.assertEqual(test_abc_2000_request["path"], self.alpha_base_url + test_abc_2000[0] + "/year/" + test_abc_2000[1], f"Error path incorrect: {test_abc_2000_request['path']}.")

    def test_name_endpoint(self):
        """ Testing '/api/name' path/endpoint, return all ISO 3166 updates data from input ISO 3166-1 name/names. """
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
        #for each country, test API returns correct object using its alpha-2 code
        for alpha2 in sorted(list(iso3166.countries_by_alpha2.keys())):
            country_name = iso3166.countries_by_alpha2[alpha2].name
            if (country_name == "Kosovo"):
                continue
            test_request_name = requests.get(self.name_base_url + country_name, headers=self.user_agent_header, timeout=10).json()
            #convert country name to its more common name
            if (country_name in list(name_exceptions_converted.keys())):
                country_name = name_exceptions_converted[country_name]
            self.assertEqual(list(test_request_name)[0], alpha2, 
                    f"Input country name {country_name} and one in output object do not match: {list(test_request_name)[0]}.")
#2.)
        test_request_bj = requests.get(self.name_base_url + test_name_benin, headers=self.user_agent_header, timeout=10).json() #Benin

        test_name_bj_expected = {
                "Change": "Correction of the Code Source.",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:BJ)."
                }

        self.assertIsInstance(test_request_bj, dict, f"Expected output object of API to be of type dict, got {type(test_request_bj)}.")
        self.assertIsInstance(test_request_bj["BJ"], list, f"Expected output object of API updates to be of type list, got {type(test_request_bj['BJ'])}.")
        self.assertEqual(list(test_request_bj.keys()), ["BJ"], f"Expected parent key does not match output, got {list(test_request_bj.keys())}.")
        for row in test_request_bj["BJ"]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(row.keys())}.")
        self.assertEqual(len(test_request_bj["BJ"]), 3, f"Expected there to be 3 elements in output object, got {len(test_request_bj['BJ'])}.")
        self.assertEqual(test_request_bj["BJ"][0], test_name_bj_expected, "Expected and observed outputs do not match.")
#3.)
        test_request_tj = requests.get(self.name_base_url + test_name_tajikistan, headers=self.user_agent_header, timeout=10).json() #Tajikistan

        test_name_tj_expected = {
                "Change": "Correction of the Code Source.",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:TJ)."
                }
        
        self.assertIsInstance(test_request_tj, dict, f"Expected output object of API to be of type dict, got {type(test_request_tj)}.")
        self.assertIsInstance(test_request_tj["TJ"], list, f"Expected output object of API updates to be of type list, got {type(test_request_tj['TJ'])}.")
        self.assertEqual(list(test_request_tj.keys()), ["TJ"], f"Expected parent key does not match output, got {list(test_request_tj.keys())}.")
        for row in test_request_tj["TJ"]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(row.keys())}.")
        self.assertEqual(len(test_request_tj["TJ"]), 7, f"Expected there to be 7 elements in output object, got {len(test_request_tj['TJ'])}.")
        self.assertEqual(test_request_tj["TJ"][0], test_name_tj_expected, f"Expected and observed outputs do not match:\n{test_request_tj['TJ'][0]}.")
#4.)
        test_request_md = requests.get(self.name_base_url + test_name_moldova, headers=self.user_agent_header, timeout=10).json() #Moldova

        test_name_md_expected = {
                "Change": "Modification of the French short name lower case.",
                "Date Issued": "2019-02-15",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:MD)."
                }
        
        self.assertIsInstance(test_request_md, dict, f"Expected output object of API to be of type dict, got {type(test_request_md)}.")
        self.assertIsInstance(test_request_md["MD"], list, f"Expected output object of API updates to be of type list, got {type(test_request_md['MD'])}.")
        self.assertEqual(list(test_request_md.keys()), ["MD"], f"Expected parent key does not match output, got {list(test_request_md.keys())}.")
        for row in test_request_md["MD"]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(row.keys())}.")
        self.assertEqual(len(test_request_md["MD"]), 11, f"Expected there to be 11 elements in output object, got {len(test_request_md['MD'])}.")
        self.assertEqual(test_request_md["MD"][0], test_name_md_expected, f"Expected and observed outputs do not match:\n{test_request_md['MD'][0]}.")
#5.)
        test_request_ml_ni = requests.get(self.name_base_url + test_name_mali_nicaragua, headers=self.user_agent_header, timeout=10).json() #Mali, Nicaragua 

        test_name_ml_ni_expected = {
                "Change": "Addition of regions ML-9, ML-10; update List Source.",
                "Date Issued": "2017-11-23",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:ML)."
                }
        test_name_ml_ni_expected_2 = {
                "Change": "Correction of the Code Source.",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:NI)."
                }
        
        self.assertIsInstance(test_request_ml_ni, dict, f"Expected output object of API to be of type dict, got {type(test_request_ml_ni)}.")
        self.assertIsInstance(test_request_ml_ni["ML"], list, f"Expected output object of API updates to be of type list, got {type(test_request_ml_ni['ML'])}.")
        self.assertIsInstance(test_request_ml_ni["NI"], list, f"Expected output object of API updates to be of type list, got {type(test_request_ml_ni['NI'])}.")
        self.assertEqual(list(test_request_ml_ni.keys()), ["ML", "NI"], f"Expected parent key does not match output, got {list(test_request_ml_ni.keys())}.")
        for code in test_request_ml_ni:
                for row in test_request_ml_ni[code]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(row.keys())}.")
        self.assertEqual(len(test_request_ml_ni["ML"]), 1, f"Expected there to be 1 element in output object, got {len(test_request_ml_ni['ML'])}.")
        self.assertEqual(len(test_request_ml_ni["NI"]), 3, f"Expected there to be 3 elements in output object, got {len(test_request_ml_ni['NI'])}.")
        self.assertEqual(test_request_ml_ni["ML"][0], test_name_ml_ni_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_ml_ni["NI"][0], test_name_ml_ni_expected_2, "Expected and observed outputs do not match.")
#6.)
        test_request_error = requests.get(self.name_base_url + test_name_error1, headers=self.user_agent_header, timeout=10).json() #ABCDEF

        self.assertIsInstance(test_request_error, dict, f"Expected output object of API to be of type dict, got {type(test_request_error)}.")
        self.assertEqual(list(test_request_error.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error["message"], f"No matching country name found for input: {test_name_error1.title()}.", f"Error message incorrect: {test_request_error['message']}.")
        self.assertEqual(test_request_error["status"], 400, f"Error status code incorrect: {test_request_error['status']}.")
        self.assertEqual(test_request_error["path"], self.name_base_url + test_name_error1, f"Error path incorrect: {test_request_error['path']}.")
#7.)
        test_request_error_2 = requests.get(self.name_base_url + test_name_error2, headers=self.user_agent_header, timeout=10).json() #12345
 
        self.assertIsInstance(test_request_error_2, dict, f"Expected output object of API to be of type dict, got {type(test_request_error_2)}.")
        self.assertEqual(list(test_request_error_2.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error_2["message"], f"No matching country name found for input: {test_name_error2.title()}.", f"Error message incorrect: {test_request_error_2['message']}.")
        self.assertEqual(test_request_error_2["status"], 400, f"Error status code incorrect: {test_request_error_2['status']}.")
        self.assertEqual(test_request_error_2["path"], self.name_base_url + test_name_error2, f"Error path incorrect: {test_request_error_2['path']}.")

    def test_name_year_endpoint(self):
        """ Testing '/api/name' + '/api/year' path/endpoint, using a variety of combinations of country names with years and year ranges. """
        test_name_egypt_2014 = ("Egypt", "2014")
        test_name_indonesia_2022 = ("Indonesia", "2022")
        test_name_japan_gt_2018 = ("Japan", ">2018")
        test_name_kiribati_lesotho_lt_2012 = ("Kiribati, Lesotho", "<2012")
        test_name_malta_nepal_2007_2011 = ("Malta, Nepal", "2011-2007")
        test_name_error1 = ("ABCDEFGHIJ", "200202")
        test_name_error2 = ("12345", "ABCD")
        test_name_error3 = ("blahblahblah", "2040-2050")
#1.) 
        test_request_egypt_2014 = requests.get(f"{self.name_base_url}{test_name_egypt_2014[0]}/year/{test_name_egypt_2014[1]}", headers=self.user_agent_header, timeout=10).json() #Egypt 2014

        test_name_egypt_2014_expected = {
                "Change": "Delete EG-HU and EG-SU; update List Source.",
                "Date Issued": "2014-10-29",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:EG)."
                }
        
        self.assertIsInstance(test_request_egypt_2014, dict, f"Expected output object of API to be of type dict, got {type(test_request_egypt_2014)}.")
        self.assertIsInstance(test_request_egypt_2014["EG"], list, f"Expected output object of API updates to be of type list, got {type(test_request_egypt_2014['EG'])}.")
        self.assertEqual(list(test_request_egypt_2014.keys()), ["EG"], f"Expected parent key does not match output, got {list(test_request_egypt_2014.keys())}.")
        for code in test_request_egypt_2014:
                for row in test_request_egypt_2014[code]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(row.keys())}.")
        self.assertEqual(len(test_request_egypt_2014["EG"]), 1, f"Expected there to be 1 element in output object, got {len(test_request_egypt_2014['EG'])}.")
        self.assertEqual(test_request_egypt_2014["EG"][0], test_name_egypt_2014_expected, "Expected and observed outputs do not match.")
#2.) 
        test_request_indonesia_2022 = requests.get(f"{self.name_base_url}{test_name_indonesia_2022[0]}/year/{test_name_indonesia_2022[1]}", headers=self.user_agent_header, timeout=10).json() #Indonesia 2022

        test_name_indonesia_2022_expected = {
                "Change": "Addition of provinces ID-PE, ID-PS and ID-PT; Update List Source.",
                "Date Issued": "2022-11-29",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:ID)."
                }

        self.assertIsInstance(test_request_indonesia_2022, dict, f"Expected output object of API to be of type dict, got {type(test_request_indonesia_2022)}.")
        self.assertIsInstance(test_request_indonesia_2022["ID"], list, f"Expected output object of API updates to be of type list, got {type(test_request_indonesia_2022['ID'])}.")
        self.assertEqual(list(test_request_indonesia_2022.keys()), ["ID"], f"Expected parent key does not match output, got {list(test_request_indonesia_2022.keys())}.")
        for code in test_request_indonesia_2022:
                for row in test_request_indonesia_2022[code]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(row.keys())}.")
        self.assertEqual(len(test_request_indonesia_2022["ID"]), 1, f"Expected there to be 1 element in output object, got {len(test_request_indonesia_2022['ID'])}.")
        self.assertEqual(test_request_indonesia_2022["ID"][0], test_name_indonesia_2022_expected, "Expected and observed outputs do not match.")
#3.) 
        test_request_japan_gt_2018 = requests.get(f"{self.name_base_url}{test_name_japan_gt_2018[0]}/year/{test_name_japan_gt_2018[1]}", headers=self.user_agent_header, timeout=10).json() #Japan >2018

        test_name_japan_gt_2018_expected = {
                "Change": "Correction of the romanization system label.",
                "Date Issued": "2018-11-26",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:JP)."
                }

        self.assertIsInstance(test_request_japan_gt_2018, dict, f"Expected output object of API to be of type dict, got {type(test_request_japan_gt_2018)}.")
        self.assertIsInstance(test_request_japan_gt_2018["JP"], list, f"Expected output object of API updates to be of type list, got {type(test_request_japan_gt_2018['JP'])}.")
        self.assertEqual(list(test_request_japan_gt_2018.keys()), ["JP"], f"Expected parent key does not match output, got {list(test_request_japan_gt_2018.keys())}.")
        for code in test_request_japan_gt_2018:
                for row in test_request_japan_gt_2018[code]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(row.keys())}.")
        self.assertEqual(len(test_request_japan_gt_2018["JP"]), 1, f"Expected there to be 1 element in output object, got {len(test_request_japan_gt_2018['JP'])}.")
        self.assertEqual(test_request_japan_gt_2018["JP"][0], test_name_japan_gt_2018_expected, f"Expected and observed outputs do not match:\n{test_request_japan_gt_2018['JP'][0],}")
#4.)
        test_request_kiribati_lesotho_lt_2012 = requests.get(f"{self.name_base_url}{test_name_kiribati_lesotho_lt_2012[0]}/year/{test_name_kiribati_lesotho_lt_2012[1]}", headers=self.user_agent_header, timeout=10).json() #Kiribati, Lesotho <2012

        test_name_kiribati_lesotho_lt_2012_expected = {
                "Change": "Addition of administrative language Gilbertese (-, gil).",
                "Date Issued": "2009-03-03",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:KI)."
                }
        test_name_kiribati_lesotho_lt_2012_expected_2 = {
                "Change": "Addition of local generic administrative term, update of the official languages according to ISO 3166-2 and source list update.",
                "Date Issued": "2011-12-13 (corrected 2011-12-15)",
                "Description of Change": "",
                "Source": "Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf)."
                }
        
        self.assertIsInstance(test_request_kiribati_lesotho_lt_2012, dict, f"Expected output object of API to be of type dict, got {test_request_kiribati_lesotho_lt_2012}.")
        self.assertIsInstance(test_request_kiribati_lesotho_lt_2012["KI"], list, f"Expected output object of API updates to be of type list, got {type(test_request_kiribati_lesotho_lt_2012['KI'])}.")
        self.assertIsInstance(test_request_kiribati_lesotho_lt_2012["LS"], list, f"Expected output object of API updates to be of type list, got {type(test_request_kiribati_lesotho_lt_2012['LS'])}.")
        self.assertEqual(list(test_request_kiribati_lesotho_lt_2012.keys()), ["KI", "LS"], f"Expected parent key does not match output, got {list(test_request_kiribati_lesotho_lt_2012.keys())}.")
        for code in test_request_kiribati_lesotho_lt_2012:
                for row in test_request_kiribati_lesotho_lt_2012[code]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(row.keys())}.")
        self.assertEqual(len(test_request_kiribati_lesotho_lt_2012["KI"]), 1, f"Expected there to be 1 element in output object, got {len(test_request_kiribati_lesotho_lt_2012['KI'])}.")
        self.assertEqual(len(test_request_kiribati_lesotho_lt_2012["LS"]), 1, f"Expected there to be 3 elements in output object, got {len(test_request_kiribati_lesotho_lt_2012['LS'])}.")
        self.assertEqual(test_request_kiribati_lesotho_lt_2012["KI"][0], test_name_kiribati_lesotho_lt_2012_expected, f"Expected and observed outputs do not match:\n{test_request_kiribati_lesotho_lt_2012['KI'][0]}")
        self.assertEqual(test_request_kiribati_lesotho_lt_2012["LS"][0], test_name_kiribati_lesotho_lt_2012_expected_2, f"Expected and observed outputs do not match:\n{test_request_kiribati_lesotho_lt_2012['LS'][0]}")
#5.)
        test_request_malta_nepal_2007_2011 = requests.get(f"{self.name_base_url}{test_name_malta_nepal_2007_2011[0]}/year/{test_name_malta_nepal_2007_2011[1]}", headers=self.user_agent_header, timeout=10).json() #Malta, Nepal 2007-2011

        test_name_malta_nepal_2007_2011_expected = {
                "Change": "Subdivisions added: 68 local councils.",
                "Date Issued": "2007-11-28",
                "Description of Change": "Addition of administrative subdivisions and of their code elements.",
                "Source": "Newsletter I-9 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/newsletter_i-9.pdf)."
                }
        test_name_malta_nepal_2007_2011_expected_2 = {
                "Change": "First level prefix addition, language adjustment, comment addition, deletion of the romanization system and source list update.",
                "Date Issued": "2011-12-13 (corrected 2011-12-15)",
                "Description of Change": "",
                "Source": "Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf)."
                }

        self.assertIsInstance(test_request_malta_nepal_2007_2011, dict, f"Expected output object of API to be of type dict, got {type(test_request_malta_nepal_2007_2011)}.")
        self.assertIsInstance(test_request_malta_nepal_2007_2011["MT"], list, f"Expected output object of API updates to be of type list, got {type(test_request_malta_nepal_2007_2011['MT'])}.")
        self.assertIsInstance(test_request_malta_nepal_2007_2011["NP"], list, f"Expected output object of API updates to be of type list, got {type(test_request_malta_nepal_2007_2011['NP'])}.")
        self.assertEqual(list(test_request_malta_nepal_2007_2011.keys()), ["MT", "NP"], "Expected parent key does not match output, got {list(test_request_malta_nepal_2007_2011.keys())}.")
        for code in test_request_malta_nepal_2007_2011:
                for row in test_request_malta_nepal_2007_2011[code]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(row.keys())}.")
        self.assertEqual(len(test_request_malta_nepal_2007_2011["MT"]), 1, f"Expected there to be 1 element in output object, got {len(test_request_malta_nepal_2007_2011['MT'])}.")
        self.assertEqual(len(test_request_malta_nepal_2007_2011["NP"]), 4, f"Expected there to be 4 elements in output object, got {len(test_request_malta_nepal_2007_2011['NP'])}.")
        self.assertEqual(test_request_malta_nepal_2007_2011["MT"][0], test_name_malta_nepal_2007_2011_expected, f"Expected and observed outputs do not match:\n{test_request_malta_nepal_2007_2011['MT'][0]}")
        self.assertEqual(test_request_malta_nepal_2007_2011["NP"][0], test_name_malta_nepal_2007_2011_expected_2, f"Expected and observed outputs do not match:\n{test_request_malta_nepal_2007_2011['MT'][0]}")
#6.)
        test_request_error = requests.get(f"{self.name_base_url}{test_name_error1[0]}/year/{test_name_error1[1]}", headers=self.user_agent_header, timeout=10).json() #ABCDEF, 200202

        self.assertIsInstance(test_request_error, dict, f"Expected output object of API to be of type dict, got {type(test_request_error)}.")
        self.assertEqual(list(test_request_error.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error["message"], f"No matching country name found for input: {test_name_error1[0].title()}.", f"Error message incorrect: {test_request_error['message']}.")
        self.assertEqual(test_request_error["status"], 400, f"Error status code incorrect: {test_request_error['status']}.")
        self.assertEqual(test_request_error["path"], f"{self.name_base_url} + {test_name_error1[0]}/year/{test_name_error1[1]}", f"Error path incorrect: {test_request_error['path']}.")
#7.)
        test_request_error_2 = requests.get(f"{self.name_base_url}{test_name_error2[0]}/year/{test_name_error2[1]}", headers=self.user_agent_header, timeout=10).json() #12345, ABCDE

        self.assertIsInstance(test_request_error_2, dict, f"Expected output object of API to be of type dict, got {type(test_request_error_2)}.")
        self.assertEqual(list(test_request_error_2.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error_2["message"], f"No matching country name found for input: {test_name_error2[0]}.", f"Error message incorrect: {test_request_error_2['message']}.")
        self.assertEqual(test_request_error_2["status"], 400, f"Error status code incorrect: {test_request_error_2['status']}.")
        self.assertEqual(test_request_error_2["path"], f"{self.name_base_url}{test_name_error2[0]}/year/{test_name_error2[1]}", f"Error path incorrect: {test_request_error_2['path']}.")
#8.)
        test_request_error_3 = requests.get(f"{self.name_base_url}{test_name_error3[0]}/year/{test_name_error3[1]}", headers=self.user_agent_header, timeout=10).json() #blahblahblahblah, 2040-2050

        self.assertIsInstance(test_request_error_3, dict, f"Expected output object of API to be of type dict, got {type(test_request_error_3)}.")
        self.assertEqual(list(test_request_error_3.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error_3["message"], f"No matching country name found for input: {test_name_error3[0].title()}.", f"Error message incorrect: {test_request_error_3['message']}.")
        self.assertEqual(test_request_error_3["status"], 400, f"Error status code incorrect: {test_request_error_3['status']}.")
        self.assertEqual(test_request_error_3["path"], self.name_base_url + test_name_error3[0] + "/year/" + test_name_error3[1], f"Error path incorrect: {test_request_error_3['path']}.")

    def test_date_range_endpoint(self):
        """ Testing '/api/date_range' endpoint, which returns the updates in a specified date range. """
        test_date_range1 = "2014-04-07,2016-10-16"
        test_date_range2 = "2009-08-17,2011-11-12"
        test_date_range3 = "2022-01-01"
#1.)
        test_request_date_range1 = requests.get(self.date_range_url + test_date_range1, headers=self.user_agent_header, timeout=10).json() #2014-04-07,2016-10-16
        test_request_date_range1_expected = ['AF', 'AL', 'AU', 'BI', 'BW', 'CA', 'CH', 'CN', 'CO', 'CZ', 'EC', 'ES', 'ET', 'GE', 'ID', 
                                             'IN', 'KG', 'KH', 'KP', 'KZ', 'LA', 'LY', 'MA', 'MD', 'MU', 'MY', 'RO', 'SI', 'SN', 'TJ', 
                                             'TL', 'TM', 'TN', 'TW', 'TZ', 'UG', 'UZ', 'VE', 'YE', 'ZA']

        for country_code, updates in test_request_date_range1.items():
            for update in updates:
                if ("corrected" in update["Date Issued"]):
                    current_updates_date = datetime.strptime(re.sub("[(].*[)]", "", update["Date Issued"]).replace(' ', "").replace(".", '').replace('\n', ''), '%Y-%m-%d')
                else:
                    current_updates_date = datetime.strptime(update["Date Issued"].replace('\n', ''), '%Y-%m-%d')

                self.assertTrue(datetime.strptime("2014-04-07", "%Y-%m-%d") <= current_updates_date <= datetime.strptime("2016-10-16", "%Y-%m-%d"), 
                    f"Expected update of object to be between the dates 2014-04-07 and 2016-10-16, got date {current_updates_date}.")        

        self.assertEqual(list(test_request_date_range1), test_request_date_range1_expected, 
            f"Expected and observed country code objects do not match:\n{list(test_request_date_range1)}.")
#2.)
        test_request_date_range2 = requests.get(self.date_range_url + test_date_range2, headers=self.user_agent_header, timeout=10).json() #2009-08-17,2011-11-12
        test_request_date_range2_expected = ['AF', 'AL', 'AU', 'BI', 'BW', 'CA', 'CH', 'CN', 'CO', 'CZ', 'EC', 'ES', 'ET', 'GE', 'ID', 
                                             'IN', 'KG', 'KH', 'KP', 'KZ', 'LA', 'LY', 'MA', 'MD', 'MU', 'MY', 'RO', 'SI', 'SN', 'TJ', 
                                             'TL', 'TM', 'TN', 'TW', 'TZ', 'UG', 'UZ', 'VE', 'YE', 'ZA']

        for country_code, updates in test_request_date_range2.items():
            for update in updates:
                if ("corrected" in update["Date Issued"]):
                    current_updates_date = datetime.strptime(re.sub("[(].*[)]", "", update["Date Issued"]).replace(' ', "").replace(".", '').replace('\n', ''), '%Y-%m-%d')
                else:
                    current_updates_date = datetime.strptime(update["Date Issued"].replace('\n', ''), '%Y-%m-%d')

                self.assertTrue(datetime.strptime("2009-08-17", "%Y-%m-%d") <= current_updates_date <= datetime.strptime("2011-11-12", "%Y-%m-%d"), 
                    f"Expected update of object to be between the date 2009-08-17 and 2011-11-12, got date {current_updates_date}.")        

        self.assertEqual(list(test_request_date_range2), test_request_date_range2_expected, 
            f"Expected and observed country code objects do not match:\n{list(test_request_date_range2)}.")
#3.)
        test_request_date_range3 = requests.get(self.date_range_url + test_date_range3, headers=self.user_agent_header, timeout=10).json() #2022-01-01
        test_request_date_range3_expected = ['AF', 'AL', 'AU', 'BI', 'BW', 'CA', 'CH', 'CN', 'CO', 'CZ', 'EC', 'ES', 'ET', 'GE', 'ID', 
                                             'IN', 'KG', 'KH', 'KP', 'KZ', 'LA', 'LY', 'MA', 'MD', 'MU', 'MY', 'RO', 'SI', 'SN', 'TJ', 
                                             'TL', 'TM', 'TN', 'TW', 'TZ', 'UG', 'UZ', 'VE', 'YE', 'ZA']

        for country_code, updates in test_request_date_range3.items():
            for update in updates:
                if ("corrected" in update["Date Issued"]):
                    current_updates_date = datetime.strptime(re.sub("[(].*[)]", "", update["Date Issued"]).replace(' ', "").replace(".", '').replace('\n', ''), '%Y-%m-%d')
                else:
                    current_updates_date = datetime.strptime(update["Date Issued"].replace('\n', ''), '%Y-%m-%d')

                self.assertTrue(datetime.strptime("2022-01-01", "%Y-%m-%d") <= current_updates_date <= datetime.today(), 
                    f"Expected update of object to be between the dates 2022-01-01 and today's date, got date {current_updates_date}.")   

        self.assertEqual(list(test_request_date_range3), test_request_date_range3_expected, 
            f"Expected and observed country code objects do not match:\n{list(test_request_date_range3)}.")
        

if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)