import unittest
import iso3166
import requests
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import getpass
from importlib.metadata import metadata
unittest.TestLoader.sortTestMethodsUsing = None

class ISO3166_Updates_Api_Tests(unittest.TestCase):
    """ Tests for iso3166-updates software package. """
     
    def setUp(self):
        """ Initialise test variables including base urls for API. """
        # self.base_url = "https://iso3166-updates-frontend.vercel.app/"
        self.base_url = "https://iso3166-updates.com/api" 

        self.__version__ = metadata('iso3166_updates')['version']

        self.alpha2_base_url = self.base_url + "/alpha2/"
        self.year_base_url = self.base_url + '/year/'
        self.user_agent_header = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(self.__version__,
                                       'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}
    
        #correct column/key names for dict returned from api
        self.expected_output_columns = ["Code/Subdivision change", "Date Issued", "Description of change in newsletter", "Edition/Newsletter"]

    @unittest.skip("Skipping to not overload API endpoints on test suite run.")
    def test_api_endpoints(self):
        """ Testing API endpoints are valid and return expected 200 status code for all alpha-2 codes. """
#1.)
        main_request = requests.get(self.base_url, headers=self.user_agent_header)
        self.assertEqual(main_request.status_code, 200, 
            "Expected 200 status code from request, got {}.".format(main_request.status_code))
        self.assertEqual(main_request.headers["content-type"], "application/json", 
            "Expected Content type to be application/json, got {}.".format(main_request.headers["content-type"]))
#2.)
        #for each alpha-2, test API returns valid response to it and correct json content type
        for alpha2 in sorted(list(iso3166.countries_by_alpha2.keys())):
            test_request = requests.get(self.alpha2_base_url + alpha2, headers=self.user_agent_header)
            self.assertEqual(test_request.status_code, 200, 
                "Expected 200 status code from request for alpha-2 code {}, got {}.".format(alpha2, test_request.status_code))
            self.assertEqual(test_request.headers["content-type"], "application/json", 
                "Expected Content type to be application/json for alpha-2 code {}, got {}.".format(alpha2, test_request.headers["content-type"]))

    def test_updates_alpha2(self):
        """ Testing single, multiple and invalid alpha-2 codes for expected ISO3166 updates. """
        test_alpha2_ad = "AD" #Andorra 
        test_alpha2_bo = "BO" #Bolivia
        test_alpha2_co = "CO" #Colombia
        test_alpha2_bo_co_dm = "BO,CO,DM" 
        test_alpha2_ke = "KEN" #Kenya (using alpha-3 code)
        error_test_alpha2_1 = "blahblahblah"
        error_test_alpha2_2 = "42"
        error_test_alpha2_3 = "XYZ" #invalid alpha-3 code
#1.)
        test_request = requests.get(self.base_url, headers=self.user_agent_header) 
        
        self.assertIsInstance(test_request.json(), dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request)))
        self.assertEqual(len(test_request.json()), 250, "Expected there to be 250 elements in output table, got {}.".format(len(test_request.json())))
        self.assertEqual(test_request.status_code, 200, "Expected 200 status code from request, got {}.".format(test_request.status_code))
        self.assertEqual(test_request.headers["content-type"], "application/json", 
                "Expected Content type to be application/json, got {}.".format(test_request.headers["content-type"]))
#2.)
        test_request_ad = requests.get(self.alpha2_base_url + test_alpha2_ad, headers=self.user_agent_header).json() #AD
        
        #expected test outputs
        test_alpha2_ad_expected1 = {
                "Code/Subdivision change": "",
                "Date Issued": "2015-11-27",
                "Description of change in newsletter": "Update List Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD)"
                }
        test_alpha2_ad_expected2 = {
                "Code/Subdivision change": "",
                "Date Issued": "2014-11-03",
                "Description of change in newsletter": "Update List Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD)"
                }

        self.assertIsInstance(test_request_ad, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_ad)))
        self.assertIsInstance(test_request_ad[test_alpha2_ad], list, "Expected ouput object of API should be of type list, got {}.".format(type(test_request_ad[test_alpha2_ad])))
        self.assertEqual(list(test_request_ad.keys()), [test_alpha2_ad], "Expected parent key does not match output, got {}.".format(list(test_request_ad.keys())))
        for row in test_request_ad[test_alpha2_ad]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_ad[test_alpha2_ad]), 3, "Expected there to be 3 elements in output table, got {}.".format(len(test_request_ad[test_alpha2_ad])))
        self.assertEqual(test_request_ad[test_alpha2_ad][0], test_alpha2_ad_expected1, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_ad[test_alpha2_ad][1], test_alpha2_ad_expected2, "Expected and observed outputs do not match.")
#3.)
        test_request_bo = requests.get(self.alpha2_base_url + test_alpha2_bo, headers=self.user_agent_header).json() #BO
        
        #expected test outputs
        test_alpha2_bo_expected1 = {
                "Code/Subdivision change": "",
                "Date Issued": "2014-12-18",
                "Description of change in newsletter": "Alignment of the English and French short names upper and lower case with UNTERM",
                "Edition/Newsletter": "Online Browsing Platform (OBP)"
                }
        test_alpha2_bo_expected2 = {
                "Code/Subdivision change": "",
                "Date Issued": "2014-11-03",
                "Description of change in newsletter": "Update List Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP)"
                }
        
        self.assertIsInstance(test_request_bo, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_bo)))
        self.assertIsInstance(test_request_bo[test_alpha2_bo], list, "Expected ouput object of API should be of type list, got {}.".format(type(test_request_bo[test_alpha2_bo])))
        self.assertEqual(list(test_request_bo.keys()), [test_alpha2_bo], "Expected parent key does not match output, got {}.".format(list(test_request_bo.keys())))
        for row in test_request_bo[test_alpha2_bo]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_bo[test_alpha2_bo]), 5, "Expected there to be 5 elements in output table, got {}.".format(len(test_request_bo[test_alpha2_bo])))
        self.assertEqual(test_request_bo[test_alpha2_bo][0], test_alpha2_bo_expected1, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_bo[test_alpha2_bo][1], test_alpha2_bo_expected2, "Expected and observed outputs do not match.")
#4.)
        test_request_co = requests.get(self.alpha2_base_url + test_alpha2_co, headers=self.user_agent_header).json() #CO

        #expected test outputs
        test_alpha2_co_expected1 = {
                "Code/Subdivision change": "",
                "Date Issued": "2016-11-15",
                "Description of change in newsletter": "Addition of local variation of CO-DC, CO-SAP, CO-VAC; update list source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:CO)"
                }
        test_alpha2_co_expected2 = {
                "Code/Subdivision change": "",
                "Date Issued": "2004-03-08",
                "Description of change in newsletter": "Change of name of CO-DC",
                "Edition/Newsletter": "Newsletter I-6 (https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf)"
                }       

        self.assertIsInstance(test_request_co, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_co)))
        self.assertIsInstance(test_request_co[test_alpha2_co], list, "Expected ouput object of API should be of type list, got {}.".format(type(test_request_co[test_alpha2_co])))
        self.assertEqual(list(test_request_co.keys()), [test_alpha2_co], "Expected parent key does not match output, got {}.".format(list(test_request_co.keys())))
        for row in test_request_co[test_alpha2_co]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_co[test_alpha2_co]), 2, "Expected there to be 2 elements in output table, got {}.".format(len(test_request_co[test_alpha2_co])))
        self.assertEqual(test_request_co[test_alpha2_co][0], test_alpha2_co_expected1, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_co[test_alpha2_co][1], test_alpha2_co_expected2, "Expected and observed outputs do not match.")
#5.)
        test_request_bo_co_dm = requests.get(self.alpha2_base_url + test_alpha2_bo_co_dm, headers=self.user_agent_header).json() #BO,CO,DM
        test_alpha2_list = ['BO', 'CO', 'DM']  
        
        #expected test outputs
        test_alpha2_bo_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2014-12-18",
                "Description of change in newsletter": "Alignment of the English and French short names upper and lower case with UNTERM",
                "Edition/Newsletter": "Online Browsing Platform (OBP)"
                }  
        test_alpha2_co_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2016-11-15",
                "Description of change in newsletter": "Addition of local variation of CO-DC, CO-SAP, CO-VAC; update list source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:CO)"
                }  
        test_alpha2_dm_expected = {
                "Code/Subdivision change": "Subdivisions added: 10 parishes",
                "Date Issued": "2007-04-17",
                "Description of change in newsletter": "Addition of the administrative subdivisions and of their code elements",
                "Edition/Newsletter": "Newsletter I-8 (https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)"
                }     

        self.assertIsInstance(test_request_bo_co_dm, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_bo_co_dm)))
        self.assertEqual(list(test_request_bo_co_dm.keys()), test_alpha2_list, "Expected columns do not match output, got {}.".format(list(test_request_bo_co_dm.keys())))
        for alpha2 in test_alpha2_list:
                self.assertIsInstance(test_request_bo_co_dm[alpha2], list, "Expected ouput object of API should be of type list, got {}.".format(type(test_request_bo_co_dm[alpha2])))
                for row in test_request_bo_co_dm[alpha2]:
                        self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_bo_co_dm['BO']), 5, "Expected there to be 5 rows of updates for BO, got {}.".format(len(test_request_bo_co_dm['BO'])))
        self.assertEqual(len(test_request_bo_co_dm['CO']), 2, "Expected there to be 2 rows of updates for CO, got {}.".format(len(test_request_bo_co_dm['CO'])))
        self.assertEqual(len(test_request_bo_co_dm['DM']), 1, "Expected there to be 1 row of updates for DM, got {}.".format(len(test_request_bo_co_dm['DM'])))
        self.assertEqual(test_request_bo_co_dm['BO'][0], test_alpha2_bo_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_bo_co_dm['CO'][0], test_alpha2_co_expected, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_bo_co_dm['DM'][0], test_alpha2_dm_expected, "Expected and observed outputs do not match.")
#6.)
        test_request_ke = requests.get(self.alpha2_base_url + test_alpha2_ke, headers=self.user_agent_header).json() #KEN

        #expected test outputs
        test_alpha2_ke_expected1 = {
                "Code/Subdivision change": "",
                "Date Issued": "2016-11-15",
                "Description of change in newsletter": "Update Code Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:KE)"
                } 
        test_alpha2_ke_expected2 = {
                "Code/Subdivision change": "Deleted codes:KE-110, KE-200, KE-300, KE-400, KE-500, KE-600, KE-700, KE-800Added codes:KE-01 through KE-47",
                "Date Issued": "2014-10-30",
                "Description of change in newsletter": "Delete provinces; add 47 counties; update List Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:KE)"
                } 
  
        self.assertIsInstance(test_request_ke, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_ke)))
        self.assertIsInstance(test_request_ke["KE"], list, "Expected ouput object of API should be of type list, got {}.".format(type(test_request_ke["KE"])))
        self.assertEqual(list(test_request_ke.keys()), ["KE"], "Expected output columns of API do not match, got {}.".format(list(test_request_ke.keys()))) 
        for row in test_request_ke["KE"]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(row.keys())))
        self.assertEqual(len(test_request_ke["KE"]), 4, "Expected there to be 4 rows of updates for BO, got {}.".format(len(test_request_ke["KE"])))
        self.assertEqual(test_request_ke["KE"][0], test_alpha2_ke_expected1, "Expected and observed outputs do not match.")
        self.assertEqual(test_request_ke["KE"][1], test_alpha2_ke_expected2, "Expected and observed outputs do not match.")
#7.)
        test_request_error1 = requests.get(self.alpha2_base_url + error_test_alpha2_1, headers=self.user_agent_header).json() #blahblahblah

        self.assertIsInstance(test_request_error1, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_error1)))
        self.assertEqual(list(test_request_error1.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error1["message"], "Invalid 2 letter alpha-2 code input: " + error_test_alpha2_1.upper() + ".", "Error message incorrect: {}.".format(test_request_error1["message"]))
        self.assertEqual(test_request_error1["status"], 400, "Error status code incorrect: {}.".format(test_request_error1["status"]))
        self.assertEqual(test_request_error1["path"], self.alpha2_base_url + error_test_alpha2_1, "Error path incorrect: {}.".format(test_request_error1["path"]))
#8.)
        test_request_error2 = requests.get(self.alpha2_base_url + error_test_alpha2_2, headers=self.user_agent_header).json() #42

        self.assertIsInstance(test_request_error2, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_error2)))
        self.assertEqual(list(test_request_error2.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error2["message"], "Invalid 2 letter alpha-2 code input: " + error_test_alpha2_2.upper() + ".", "Error message incorrect: {}.".format(test_request_error2["message"]))
        self.assertEqual(test_request_error2["status"], 400, "Error status code incorrect: {}.".format(test_request_error2["status"]))
        self.assertEqual(test_request_error2["path"], self.alpha2_base_url + error_test_alpha2_2, "Error path incorrect: {}.".format(test_request_error2["path"]))
#9.)
        test_request_error3 = requests.get(self.alpha2_base_url + error_test_alpha2_3, headers=self.user_agent_header).json() #xyz

        self.assertIsInstance(test_request_error3, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_error3)))
        self.assertEqual(list(test_request_error3.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_error3["message"], "Invalid 3 letter alpha-3 code input: " + error_test_alpha2_3.upper() + ".", "Error message incorrect: {}.".format(test_request_error3["message"]))
        self.assertEqual(test_request_error3["status"], 400, "Error status code incorrect: {}.".format(test_request_error3["status"]))
        self.assertEqual(test_request_error3["path"], self.alpha2_base_url + error_test_alpha2_3, "Error path incorrect: {}.".format(test_request_error3["path"]))

    def test_updates_year(self):
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
                "Code/Subdivision change": "",
                "Date Issued": "2016-11-15",
                "Description of change in newsletter": "Update List Source; update Code Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP)"
                }
        test_dz_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2016-11-15",
                "Description of change in newsletter": "Change of spelling of DZ-28; Update list source",
                "Edition/Newsletter": "Online Browsing Platform (OBP)"
                }
        test_mv_expected = {
                "Code/Subdivision change": "Spelling change:MV-05",
                "Date Issued": "2016-11-15",
                "Description of change in newsletter": "Change of spelling of MV-05",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:MV)"
                }
        test_pw_expected = {
                "Code/Subdivision change": "Name changed:PW-050 Hatobohei -> Hatohobei",
                "Date Issued": "2016-11-15",
                "Description of change in newsletter": "Change of spelling of PW-050 in eng, pau; update list source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:PW)"
                }

        #expected output keys
        test_year_2016_keys = ['AU', 'BD', 'BF', 'BT', 'CD', 'CI', 'CL', 'CO', 'CZ', 'DJ', 'DZ', 'FR', 'GR', 'ID', 'KE',
                          'KH', 'KZ', 'MV', 'NA', 'PW', 'SI', 'TJ', 'TW', 'UG', 'YE']

        self.assertIsInstance(test_request_year_2016, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_year_2016)))
        self.assertEqual(list(test_request_year_2016), test_year_2016_keys, "Expected keys of output dict from API do not match, got {}.".format(list(test_request_year_2016)))
        self.assertEqual(len(list(test_request_year_2016)), 25, "Expected there to be 25 output objects from API call, got {}.".format(len(list(test_request_year_2016))))
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
                "Code/Subdivision change": "Subdivisions added: 6 parishes, 1 dependency",
                "Date Issued": "2007-04-17",
                "Description of change in newsletter": "Addition of the administrative subdivisions and of their code elements",
                "Edition/Newsletter": "Newsletter I-8 (https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)"
                }
        test_bh_expected = {
                "Code/Subdivision change": "Subdivision layout: 12 regions (see below) -> 5 governorates",
                "Date Issued": "2007-04-17",
                "Description of change in newsletter": "Modification of the administrative structure",
                "Edition/Newsletter": "Newsletter I-8 (https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)"
                }
        test_gd_expected = {
                "Code/Subdivision change": "Subdivisions added: 6 parishes, 1 dependency",
                "Date Issued": "2007-04-17",
                "Description of change in newsletter": "Addition of the administrative subdivisions and of their code elements",
                "Edition/Newsletter": "Newsletter I-8 (https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)"
                }
        test_sm_expected = {
                "Code/Subdivision change": "Subdivisions added: 9 municipalities",
                "Date Issued": "2007-04-17",
                "Description of change in newsletter": "Addition of the administrative subdivisions and of their code elements",
                "Edition/Newsletter": "Newsletter I-8 (https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)"
                }

        #expected key outputs
        test_year_2007_keys = ['AD', 'AG', 'BA', 'BB', 'BG', 'BH', 'BL', 'CI', 'CZ', 'DM', 'DO', 'EG', 'FR', 'GB', 'GD', 'GE', 'GG', 'GN', 'HT', 'IM', \
                'IR', 'IT', 'JE', 'KE', 'KN', 'KW', 'LB', 'LC', 'LI', 'LR', 'ME', 'MF', 'MK', 'MT', 'NR', 'PW', 'RS', 'RU', 'RW', 'SB', 'SC', 'SD', \
                'SG', 'SM', 'TD', 'TO', 'TV', 'UG', 'VC', 'YE', 'ZA']

        self.assertIsInstance(test_request_year_2007, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_year_2007)))
        self.assertEqual(list(test_request_year_2007), test_year_2007_keys, "Expected keys of output dict from API do not match, got {}.".format(list(test_request_year_2007)))
        self.assertEqual(len(list(test_request_year_2007)), 51, "Expected there to be 51 output objects from API call, got {}.".format(len(list(test_request_year_2007))))
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
                "Code/Subdivision change": "",
                "Date Issued": "2021-11-25",
                "Description of change in newsletter": "Change of spelling of CN-NX; Update List Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP)"
                }
        test_et_expected = {
                "Code/Subdivision change": "Subdivisions added: ET-SI Sidama",
                "Date Issued": "2021-11-25",
                "Description of change in newsletter": "Addition of regional state ET-SI; Update List Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:ET)"
                }
        test_np_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2021-11-25",
                "Description of change in newsletter": "Change of spelling of NP-P5; Modification of remark part 2; Update List Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:NP)"
                }
        test_ss_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2021-11-25",
                "Description of change in newsletter": "Typographical correction of SS-BW (deletion of the extra space between el and Ghazal)",
                "Edition/Newsletter": "Online Browsing Platform (OBP)"
                }

        #expected key outputs
        test_year_2021_keys = ['CN', 'ET', 'FR', 'GB', 'GT', 'HU', 'IS', 'KH', 'LT', 'LV', 'NP', 'PA', 'RU', 'SS']

        self.assertIsInstance(test_request_year_2021, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_year_2021)))
        self.assertEqual(list(test_request_year_2021), test_year_2021_keys, "Expected keys of output dict from API do not match, got {}.".format(list(test_request_year_2021)))
        self.assertEqual(len(list(test_request_year_2021)), 14, "Expected there to be 14 output objects from API call, got {}.".format(len(list(test_request_year_2021))))
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
        test_request_year_2004_2009 = requests.get(self.year_base_url + test_year_2004_2009, headers=self.user_agent_header).json() #2004 (updated 2004-2009)

        #expected test outputs
        test_af_expected = {
                "Code/Subdivision change": "Subdivisions added: AF-DAY Dāykondī AF-PAN Panjshīr",
                "Date Issued": "2005-09-13",
                "Description of change in newsletter": "Addition of 2 provinces. Update of list source",
                "Edition/Newsletter": "Newsletter I-7 (https://web.archive.org/web/20081218103217/http://www.iso.org/iso/iso_3166-2_newsletter_i-7_en.pdf)"
                }
        test_co_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2004-03-08",
                "Description of change in newsletter": "Change of name of CO-DC",
                "Edition/Newsletter": "Newsletter I-6 (https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf)"
                }
        test_kp_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2004-03-08",
                "Description of change in newsletter": "Spelling correction in header of list source",
                "Edition/Newsletter": "Newsletter I-6 (https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf)"
                }
        test_za_expected = {
                "Code/Subdivision change": "Codes: Gauteng: ZA-GP -> ZA-GT KwaZulu-Natal: ZA-ZN -> ZA-NL",
                "Date Issued": "2007-12-13",
                "Description of change in newsletter": "Second edition of ISO 3166-2 (this change was not announced in a newsletter)",
                "Edition/Newsletter": "ISO 3166-2:2007 (http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=39718)"
                }

        #expected key outputs
        test_year_2004_2009_keys = ['AD', 'AF', 'AG', 'AL', 'AU', 'BA', 'BB', 'BG', 'BH', 'BL', 'BO', 'CI', 'CN', 'CO', 'CZ', 'DJ', 'DM', 'DO', 'EG', 'FR', 'GB', 'GD', 'GE', \
                                    'GG', 'GN', 'HT', 'ID', 'IM', 'IR', 'IT', 'JE', 'KE', 'KM', 'KN', 'KP', 'KW', 'LB', 'LC', 'LI', 'LR', 'MA', 'MD', 'ME', 'MF', 'MK', 'MT', \
                                        'NR', 'PW', 'RS', 'RU', 'RW', 'SB', 'SC', 'SD', 'SG', 'SI', 'SM', 'TD', 'TN', 'TO', 'TV', 'UG', 'VC', 'VE', 'VN', 'YE', 'ZA']
        
        self.assertIsInstance(test_request_year_2004_2009, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_year_2004_2009)))
        self.assertEqual(list(test_request_year_2004_2009), test_year_2004_2009_keys, "Expected keys of output dict from API do not match, got {}.".format(list(test_request_year_2004_2009)))
        self.assertEqual(len(list(test_request_year_2004_2009)), 67, "Expected there to be 67 output objects from API call, got {}.".format(len(list(test_request_year_2004_2009))))
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
                "Code/Subdivision change": "Subdivisions added:CL-NB Ñuble",
                "Date Issued": "2018-11-26",
                "Description of change in newsletter": "Addition of region CL-NB; Update List Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:CL)"
                }
        test_gh_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2019-11-22",
                "Description of change in newsletter": "Deletion of region GH-BA; Addition of regions GH-AF, GH-BE, GH-BO, GH-NE, GH-OT, GH-SV, GH-WN; Update List Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP)"
                }
        test_sa_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2018-11-26",
                "Description of change in newsletter": "Change of subdivision category from province to region",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:SA)"
                }
        test_ve_expected = {
                "Code/Subdivision change": "Subdivisions renamed: VE-X Vargas -> La Guaira",
                "Date Issued": "2020-11-24",
                "Description of change in newsletter": "Change of subdivision name of VE-X; Update List Source; Correction of the Code Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:VE)"
                }

        #expected key outputs
        test_year_gt_2017_keys = ['AF', 'AM', 'AO', 'BA', 'BD', 'BG', 'BN', 'BS', 'BT', 'BY', 'CH', 'CL', 'CN', 'CY', 'CZ', 'DZ', \
                'EE', 'ES', 'ET', 'FI', 'FR', 'GB', 'GH', 'GL', 'GQ', 'GR', 'GT', 'GW', 'HU', 'ID', 'IN', 'IQ', 'IR', 'IS',\
                'IT', 'KG', 'KH', 'KP', 'KZ', 'LK', 'LS', 'LT', 'LV', 'MA', 'ME', 'MK', 'MU', 'MV', 'NA', 'NI', 'NO', 'NP', 
                'NR', 'NZ', 'PA', 'PH', 'PK', 'PL', 'QA', 'RU', 'SA', 'SC', 'SD', 'SI', 'SL', 'SM', 'SS', 'ST', 'SZ', 'TD', 
                'TJ', 'TL', 'TT', 'TZ', 'UG', 'VE', 'VN', 'ZA']

        self.assertIsInstance(test_request_year_gt_2017, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_year_gt_2017)))
        self.assertEqual(list(test_request_year_gt_2017), test_year_gt_2017_keys, "Expected keys of output dict from API do not match, got {}.".format(list(test_request_year_gt_2017)))
        self.assertEqual(len(list(test_request_year_gt_2017)), 78, "Expected there to be 78 output objects from API call, got {}.".format(len(list(test_request_year_gt_2017))))
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
                "Code/Subdivision change": "Subdivisions added: CA-NU Nunavut",
                "Date Issued": "2000-06-21",
                "Description of change in newsletter": "Addition of 1 new territory",
                "Edition/Newsletter": "Newsletter I-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf)"
                }
        test_it_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2000-06-21",
                "Description of change in newsletter": "Correction of spelling mistakes of names of 2 provinces",
                "Edition/Newsletter": "Newsletter I-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf)"
                }
        test_ro_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2000-06-21",
                "Description of change in newsletter": "Correction of spelling mistake of subdivision category in header",
                "Edition/Newsletter": "Newsletter I-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf)"
                }
        test_tr_expected = {
                "Code/Subdivision change": "Subdivisions added: TR-80 Osmaniye",
                "Date Issued": "2000-06-21",
                "Description of change in newsletter": "Addition of 1 new province. Correction of 2 spelling errors",
                "Edition/Newsletter": "Newsletter I-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf)"
                }

        #expected key outputs
        test_year_lt_2002_keys = ['BY', 'CA', 'DO', 'ER', 'ES', 'IT', 'KR', 'NG', 'PL', 'RO', 'RU', 'TR', 'VN']

        self.assertIsInstance(test_request_year_lt_2002, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_year_lt_2002)))
        self.assertEqual(list(test_request_year_lt_2002), test_year_lt_2002_keys, "Expected keys of output dict from API do not match, got {}.".format(list(test_request_year_lt_2002)))
        self.assertEqual(len(list(test_request_year_lt_2002)), 13, "Expected there to be 13 output objects from API call, got {}.".format(len(list(test_request_year_lt_2002))))
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

    def test_updates_alpha2_year(self):
        """ Testing varying combinations of alpha-2 codes with years/year ranges. """
        test_ad_2015 = ("AD", "2015") #Andorra 2015
        test_es_2002 = ("ES", "2002") #Spain 2002
        test_hr_2011 = ("HR", "2011") #Croatia 2011
        test_ma_2019 = ("MA", "<2019") #Morocco 2019
        test_tr_2002 = ("TR", ">2002") #Turkey <2011
        test_ve_2013 = ("VE", "2013") #Venezuela 2013 
        test_abc_2000 = ("abc", "2000") 
#1.)
        test_ad_2015_request = requests.get(self.base_url, params={"alpha2": test_ad_2015[0], "year": test_ad_2015[1]}, headers=self.user_agent_header).json() #Andorra - 2015
        
        #expected test outputs
        test_ad_2015_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2015-11-27",
                "Description of change in newsletter": "Update List Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD)"
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
        test_es_2002_request = requests.get(self.base_url, params={"alpha2": test_es_2002[0], "year": test_es_2002[1]}, headers=self.user_agent_header).json() #Spain - 2002

        #expected test outputs
        test_es_2002_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2002-12-10",
                "Description of change in newsletter": "Error correction: Regional subdivision indicator corrected in ES-PM",
                "Edition/Newsletter": "Newsletter I-4 (https://web.archive.org/web/20081218103210/http://www.iso.org/iso/iso_3166-2_newsletter_i-4_en.pdf)"
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
        test_hr_2011_request = requests.get(self.base_url, params={"alpha2": test_hr_2011[0], "year": test_hr_2011[1]}, headers=self.user_agent_header).json() #Croatia - 2011

        #expected test outputs
        test_hr_2011_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2011-12-15",
                "Description of change in newsletter": "Alphabetical re-ordering.",
                "Edition/Newsletter": "Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf)"
                }

        self.assertIsInstance(test_hr_2011_request, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_hr_2011_request)))
        self.assertEqual(list(test_hr_2011_request), ['HR'], "Expected HR to be the only key returned from API in dict, got {}.".format(list(test_hr_2011_request)))
        self.assertEqual(len(test_hr_2011_request), 1, "Expected 1 row returned from API, got {}.".format(len(test_hr_2011_request)))
        for alpha2 in list(test_hr_2011_request):
                for row in range(0, len(test_hr_2011_request[alpha2])):
                        self.assertEqual(list(test_hr_2011_request[alpha2][row].keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(test_hr_2011_request[alpha2][row].keys())))
                        self.assertIsInstance(test_hr_2011_request[alpha2][row], dict, "Expected output row of object of API to be of type dict, got {}.".format(type(test_hr_2011_request[alpha2][row])))
                        self.assertEqual(datetime.strptime(test_hr_2011_request[alpha2][row]["Date Issued"], "%Y-%m-%d").year, 2011, 
                                "Year in Date Issued column does not match expected 2011, got {}.".format(datetime.strptime(test_hr_2011_request[alpha2][row]["Date Issued"], "%Y-%m-%d").year))
        self.assertIsInstance(test_hr_2011_request[test_hr_2011[0]], list, "Expected output object of API to be of type list, got {}.".format(type(test_hr_2011_request[test_hr_2011[0]])))
        self.assertEqual(test_hr_2011_expected, test_hr_2011_request[test_hr_2011[0]][0], "Observed and expected outputs of API do not match.")
#4.) 
        test_ma_lt_2019_request = requests.get(self.base_url, params={"alpha2": test_ma_2019[0], "year": test_ma_2019[1]}, headers=self.user_agent_header).json() #Morocco - <2019

        #expected test outputs
        test_ma_lt_2019_expected = {
                "Code/Subdivision change": "Spelling change:MA-05 Béni-Mellal-Khénifra -> Béni Mellal-KhénifraLocation change:MA-ESM Es-Semara (EH) -> Es-Semara (EH-partial)",
                "Date Issued": "2018-11-26",
                "Description of change in newsletter": "",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:MA)"
                }
        
        self.assertIsInstance(test_ma_lt_2019_request, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_ma_lt_2019_request)))
        self.assertEqual(list(test_ma_lt_2019_request), ['MA'], "Expected MA to be the only key returned from API in dict, got {}.".format(list(test_ma_lt_2019_request)))
        self.assertEqual(len(test_ma_lt_2019_request), 1, "Expected 1 row returned from API, got {}.".format(len(test_ma_lt_2019_request)))
        for alpha2 in list(test_ma_lt_2019_request):
                for row in range(0, len(test_ma_lt_2019_request[alpha2])):
                        self.assertEqual(list(test_ma_lt_2019_request[alpha2][row].keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(test_ma_lt_2019_request[alpha2][row].keys())))
                        self.assertIsInstance(test_ma_lt_2019_request[alpha2][row], dict, "Expected output row of object of API to be of type dict, got {}.".format(type(test_ma_lt_2019_request[alpha2][row])))
                        self.assertTrue(datetime.strptime(test_ma_lt_2019_request[alpha2][row]["Date Issued"], '%Y-%m-%d').year < 2019, 
                                "Expected year of updates output to be less than 2019, got {}.".format(test_ma_lt_2019_request[alpha2][row]["Date Issued"]))        
        self.assertIsInstance(test_ma_lt_2019_request[test_ma_2019[0]], list, "Expected output object of API to be of type list, got {}".format(type(test_ma_lt_2019_request[test_ma_2019[0]])))
        self.assertEqual(test_ma_lt_2019_expected, test_ma_lt_2019_request[test_ma_2019[0]][0], "Observed and expected outputs of API do not match.")
#5.) 
        test_tr_gt_2002_request = requests.get(self.base_url, params={"alpha2": test_tr_2002[0], "year": test_tr_2002[1]}, headers=self.user_agent_header).json() #Turkey - >2002
        
        #expected test outputs 
        test_tr_gt_2002_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2011-12-15",
                "Description of change in newsletter": "Toponym evolution and source list update.",
                "Edition/Newsletter": "Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdff)"
                }

        self.assertIsInstance(test_tr_gt_2002_request, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_tr_gt_2002_request)))
        self.assertEqual(list(test_tr_gt_2002_request), ['TR'], "Expected TR to be the only key returned from API in dict, got {}.".format(list(test_tr_gt_2002_request)))
        self.assertEqual(len(test_tr_gt_2002_request), 1, "Expected 1 row returned from API, got {}.".format(len(test_tr_gt_2002_request)))
        for alpha2 in list(test_tr_gt_2002_request):
                for row in range(0, len(test_tr_gt_2002_request[alpha2])):
                        self.assertEqual(list(test_tr_gt_2002_request[alpha2][row].keys()), self.expected_output_columns, "Expected columns do not match output, got\n{}.".format(list(test_tr_gt_2002_request[alpha2][row].keys())))
                        self.assertIsInstance(test_tr_gt_2002_request[alpha2][row], dict, "Expected output row of object of API to be of type dict, got {}.".format(type(test_tr_gt_2002_request[alpha2][row])))
                        self.assertTrue(datetime.strptime(test_tr_gt_2002_request[alpha2][row]["Date Issued"], '%Y-%m-%d').year >= 2002, 
                                "Expected year of updates output to be greater than 2002, got {}.".format(test_tr_gt_2002_request[alpha2][row]["Date Issued"]))  
        self.assertIsInstance(test_tr_gt_2002_request[test_tr_2002[0]], list, "Expected output object of API to be of type list, got {}.".format(type(test_tr_gt_2002_request[test_tr_2002[0]])))
        self.assertEqual(test_tr_gt_2002_expected, test_tr_gt_2002_request[test_tr_2002[0]][0], "Observed and expected outputs of API do not match.")
#6.)
        test_ve_2013_request = requests.get(self.base_url, params={"alpha2": test_ve_2013[0], "year": test_ve_2013[1]}, headers=self.user_agent_header).json() #Venezuela - 2013

        self.assertIsInstance(test_ve_2013_request, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_ve_2013_request)))
        self.assertEqual(len(test_ve_2013_request), 0, "Expected 0 rows returned from API, got {}.".format(len(test_ve_2013_request)))
        self.assertEqual(test_ve_2013_request, {}, "Expected output of API to be an empty dict, got\n{}".format(test_ve_2013_request))
#7.) 
        test_abc_2000_request = requests.get(self.base_url, params={"alpha2": test_abc_2000[0], "year": test_abc_2000[1]}, headers=self.user_agent_header).json() #ABC - 2000
        
        self.assertIsInstance(test_abc_2000_request, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_abc_2000_request)))
        self.assertEqual(list(test_abc_2000_request.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_abc_2000_request["message"], "Invalid 3 letter alpha-3 code input: " + test_abc_2000[0].upper() + ".", "Error message incorrect: {}.".format(test_abc_2000_request["message"]))
        self.assertEqual(test_abc_2000_request["status"], 400, "Error status code incorrect: {}.".format(test_abc_2000_request["status"]))
        self.assertEqual(test_abc_2000_request["path"], self.alpha2_base_url + test_abc_2000[0].upper() + "/year/" + test_abc_2000[1] + "/", "Error path incorrect: {}.".format(test_abc_2000_request["path"]))

    @unittest.skip("Skipping as number of results will change month by month of running tests.")
    def test_updates_month(self):
        """ Testing months input parameter which returns the updates in a specified month range. """
        test_month_1 = "1"
        test_month_2 = "6"
        test_month_3 = "10"
        test_month_4 = "20"
        test_month_5 = "50"
        test_month_6 = "abc"
#1.)
        test_request_month1 = requests.get(self.base_url, params={"months": test_month_1}, headers=self.user_agent_header).json() #1

        self.assertIsInstance(test_request_month1, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_month1)))
        self.assertEqual(len(test_request_month1), 0, "Expected 0 rows returned from API, got {}.".format(len(test_request_month1)))
        self.assertEqual(test_request_month1, {}, "Expected output of API to be an empty dict, got\n{}".format(test_request_month1)) 
#2.)
        test_request_month2 = requests.get(self.base_url, params={"months": test_month_2}, headers=self.user_agent_header).json() #6

        self.assertIsInstance(test_request_month2, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_month2)))
        self.assertEqual(len(test_request_month2), 12, "Expected 12 rows returned from API, got {}.".format(len(test_request_month2)))
        for alpha2 in list(test_request_month2):
                for row in range(0, len(test_request_month2[alpha2])):
                       self.assertEqual(datetime.strptime(test_request_month2[alpha2][row]["Date Issued"], '%Y-%m-%d').month, (date.today() + relativedelta(months=-6)).month,
                                        "Expected Date of country update to be within the past 6 months:\nToday: {}, Update: {}.".format(date.today(), test_request_month2[alpha2][row]["Date Issued"]))
#3.)
        test_request_month3 = requests.get(self.base_url, params={"months": test_month_3}, headers=self.user_agent_header).json() #10

        self.assertIsInstance(test_request_month3, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_month3)))
        self.assertEqual(len(test_request_month3), 11, "Expected 11 rows returned from API, got {}.".format(len(test_request_month3)))
        for alpha2 in list(test_request_month3):
                for row in range(0, len(test_request_month3[alpha2])):
                       self.assertEqual(datetime.strptime(test_request_month3[alpha2][row]["Date Issued"], '%Y-%m-%d').month, (date.today() + relativedelta(months=-10)).month,
                                        "Expected Date of country update to be within the past 10 months:\nToday: {}, Update: {}.".format(date.today(), test_request_month3[alpha2][row]["Date Issued"]))
#4.)
        test_request_month4 = requests.get(self.base_url, params={"months": test_month_4}, headers=self.user_agent_header).json() #20

        self.assertIsInstance(test_request_month4, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_month4)))
        self.assertEqual(len(test_request_month4), 21, "Expected 21 rows returned from API, got {}.".format(len(test_request_month4)))
        for alpha2 in list(test_request_month4):
                for row in range(0, len(test_request_month4[alpha2])):
                       self.assertEqual(datetime.strptime(test_request_month4[alpha2][row]["Date Issued"], '%Y-%m-%d').month, (date.today() + relativedelta(months=-20)).month,
                                        "Expected Date of country update to be within the past 20 months:\nToday: {}, Update: {}.".format(date.today(), test_request_month4[alpha2][row]["Date Issued"]))
#5.)
        test_request_month5 = requests.get(self.base_url, params={"months": test_month_5}, headers=self.user_agent_header).json() #50

        self.assertIsInstance(test_request_month5, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_month5)))
        self.assertEqual(len(test_request_month5), 59, "Expected 59 rows returned from API, got {}.".format(len(test_request_month5)))
        for alpha2 in list(test_request_month5):
                for row in range(0, len(test_request_month5[alpha2])):
                       self.assertEqual(datetime.strptime(test_request_month5[alpha2][row]["Date Issued"], '%Y-%m-%d').month, (date.today() + relativedelta(months=-50)).month,
                                        "Expected Date of country update to be within the past 50 months:\nToday: {}, Update: {}.".format(date.today(), test_request_month5[alpha2][row]["Date Issued"]))
#6.)
        test_request_month6 = requests.get(self.base_url, params={"months": test_month_6}, headers=self.user_agent_header).json() #abc

        self.assertIsInstance(test_request_month6, dict, "Expected output object of API to be of type dict, got {}.".format(type(test_request_month6)))
        self.assertEqual(list(test_request_month6.keys()), ["message", "path", "status"], "Expected error message output to contain message, path and status keys.")
        self.assertEqual(test_request_month6["message"], "Invalid month input: " + test_month_6 + ".", "Error message incorrect: {}.".format(test_request_month6["message"]))
        self.assertEqual(test_request_month6["status"], 400, "Error status code incorrect: {}.".format(test_request_month6["status"]))
        self.assertEqual(test_request_month6["path"], self.base_url + '?months=' + test_month_6, "Error path incorrect: {}.".format(test_request_month6["path"]))

if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)