import iso3166_updates
import unittest
import iso3166
import requests
import datetime
import getpass
unittest.TestLoader.sortTestMethodsUsing = None

class ISO3166_Updates(unittest.TestCase):
    """ Tests for iso3166-updates software package. """
     
    def setUp(self):
        """ Initialise test variables including base urls for API. """
        self.base_url = "https://us-central1-iso3166-updates.cloudfunctions.net/iso3166-updates"
        self.alpha2_base_url = self.base_url + '?alpha2='
        self.year_base_url = self.base_url + '?year='
        self.user_agent_header = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(iso3166_updates.__version__,
                                       'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}
    
    @unittest.skip("Skipping to not overload API endpoint on test suite run.")
    def test_api_endpoint(self):
        """ Testing endpoint is valid and returns correct 200 status code for all alpha2 codes."""
        main_request = requests.get(self.base_url, headers=self.user_agent_header)
        self.assertEqual(main_request.status_code, 200, 
            "Should receive 200 status code from request, got {}".format(main_request.status_code))

        #for each alpha2, test API returns valid response to it and correct json content type
        for alpha2 in sorted(list(iso3166.countries_by_alpha2.keys())):
            test_request = requests.get(self.base_url + '?=' + alpha2, headers=self.user_agent_header)
            self.assertEqual(test_request.status_code, 200, 
                "Should receive 200 status code from request, got {}".format(test_request.status_code))
            self.assertEqual(test_request.headers["content-type"], "application/json", 
                "Content type should be json, got {}".format(test_request.headers["content-type"]))

    def test_alpha2(self):
        """ Testing single, multiple and invalid alpha2 codes for expected ISO3166 updates. """
        test_alpha2_ad = "AD" #Andorra 
        test_alpha2_bo = "BO" #Bolivia
        test_alpha2_co = "CO" #Colombia
        test_alpha2_dm = "DM" #Germany
        test_alpha2_ke = "KE" #Kenya 
        test_alpha2_1 = "blahblahblah"
        test_alpha2_2 = "42"
        test_alpha2_3 = "False"

        #correct column/key names for dict returned from api
        expected_output_columns = ["Code/Subdivision change", "Date Issued", "Description of change in newsletter", "Edition/Newsletter"]
#1.)
        test_request = requests.get(self.alpha2_base_url, headers=self.user_agent_header).json() 

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(len(test_request), 250, "Expected there to be elements in output table, got {}".format(len(test_request)))
#2.)
        test_request_ad = requests.get(self.alpha2_base_url + test_alpha2_ad, headers=self.user_agent_header).json() 
        
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

        self.assertIsInstance(test_request_ad, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request_ad)))
        self.assertIsInstance(test_request_ad[test_alpha2_ad], list, "Ouput object of API should be of type list, got {}".format(type(test_request_ad[test_alpha2_ad])))
        self.assertEqual(list(test_request_ad.keys()), [test_alpha2_ad], "Parent key of output does not match expected, got {}".format(list(test_request_ad.keys())))
        for row in test_request_ad[test_alpha2_ad]:
                self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
        self.assertEqual(len(test_request_ad[test_alpha2_ad]), 3, "Expected there to be 3 elements in output table, got {}".format(test_request_ad[test_alpha2_ad]))
        self.assertEqual(test_request_ad[test_alpha2_ad][0], test_alpha2_ad_expected1, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request_ad[test_alpha2_ad][1], test_alpha2_ad_expected2, "Expected observed and expected outputs to match.")
#3.)
        test_request_bo = requests.get(self.alpha2_base_url + test_alpha2_bo, headers=self.user_agent_header).json()
        
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

        self.assertIsInstance(test_request_bo, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request_bo)))
        self.assertIsInstance(test_request_bo[test_alpha2_bo], list, "Ouput object of API should be of type list, got {}".format(type(test_request_bo[test_alpha2_bo])))
        self.assertEqual(list(test_request_bo.keys()), [test_alpha2_bo], "Parent key of output does not match expected, got {}".format(list(test_request_bo.keys())))
        for row in test_request_bo[test_alpha2_bo]:
                self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
        self.assertEqual(len(test_request_bo[test_alpha2_bo]), 5, "Expected there to be 5 elements in output table, got {}".format(test_request_bo[test_alpha2_bo]))
        self.assertEqual(test_request_bo[test_alpha2_bo][0], test_alpha2_bo_expected1, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request_bo[test_alpha2_bo][1], test_alpha2_bo_expected2, "Expected observed and expected outputs to match.")
#4.)
        test_request_co = requests.get(self.alpha2_base_url + test_alpha2_co, headers=self.user_agent_header).json()

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

        self.assertIsInstance(test_request_co, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request_co)))
        self.assertIsInstance(test_request_co[test_alpha2_co], list, "Ouput object of API should be of type list, got {}".format(type(test_request_co[test_alpha2_co])))
        self.assertEqual(list(test_request_co.keys()), [test_alpha2_co], "Parent key of output does not match expected, got {}".format(list(test_request_co.keys())))
        for row in test_request_co[test_alpha2_co]:
                self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
        self.assertEqual(len(test_request_co[test_alpha2_co]), 2, "Expected there to be 2 elements in output table, got {}".format(len(test_request_co[test_alpha2_co])))
        self.assertEqual(test_request_co[test_alpha2_co][0], test_alpha2_co_expected1, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request_co[test_alpha2_co][1], test_alpha2_co_expected2, "Expected observed and expected outputs to match.")
#5.)
        test_request_bo_co_dm = requests.get(self.alpha2_base_url + test_alpha2_bo + ',' + test_alpha2_co + ',' + test_alpha2_dm, headers=self.user_agent_header).json()
                
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

        test_alpha2_list = ['BO', 'CO', 'DM']

        self.assertIsInstance(test_request_bo_co_dm, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request_bo_co_dm)))
        self.assertEqual(list(test_request_bo_co_dm.keys()), test_alpha2_list, "Columns from output do not match expected.")
        for alpha2 in test_alpha2_list:
                self.assertIsInstance(test_request_bo_co_dm[alpha2], list, "Ouput object of API should be of type list, got {}".format(type(test_request_bo_co_dm[alpha2])))
                for row in test_request_bo_co_dm[alpha2]:
                        self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
        self.assertEqual(len(test_request_bo_co_dm['BO']), 5, "Expected there to be 5 rows of updates for BO, got {}".format(len(test_request_bo_co_dm['BO'])))
        self.assertEqual(len(test_request_bo_co_dm['CO']), 2, "Expected there to be 2 rows of updates for CO, got {}".format(len(test_request_bo_co_dm['CO'])))
        self.assertEqual(len(test_request_bo_co_dm['DM']), 1, "Expected there to be 1 row of updates for DM, got {}".format(len(test_request_bo_co_dm['DM'])))
        self.assertEqual(test_request['BO'][0], test_alpha2_bo_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['CO'][0], test_alpha2_co_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['DM'][0], test_alpha2_dm_expected, "Expected observed and expected outputs to match.")
#6.)
        test_request_ke = requests.get(self.alpha2_base_url + test_alpha2_ke, headers=self.user_agent_header).json()

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
  
        self.assertIsInstance(test_request_ke, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request_ke)))
        self.assertIsInstance(test_request_ke[test_alpha2_ke], list, "Ouput object of API should be of type list, got {}".format(type(test_request_ke[test_alpha2_ke])))
        self.assertEqual(list(test_request_ke.keys()), [test_alpha2_ke], "Columns from output do not match expected.")
        for row in test_request_ke[test_alpha2_ke]:
                self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
        self.assertEqual(len(test_request_ke[test_alpha2_ke]), 4, "Expected there to be 4 rows of updates for BO, got {}".format(len(test_request_ke[test_alpha2_ke])))
        self.assertEqual(test_request_ke[test_alpha2_ke][0], test_alpha2_ke_expected1, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request_ke[test_alpha2_ke][1], test_alpha2_ke_expected2, "Expected observed and expected outputs to match.")
#7.)
        test_request = requests.get(self.alpha2_base_url + test_alpha2_1, headers=self.user_agent_header).json()

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(len(test_request), 250, "Expected there to be 250 elements in output response, got {}".format(len(test_request)))
#8.)
        test_request = requests.get(self.alpha2_base_url + test_alpha2_2, headers=self.user_agent_header).json()

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(len(test_request), 250, "Expected there to be 250 elements in output response, got {}".format(len(test_request)))
#9.)
        test_request = requests.get(self.alpha2_base_url + test_alpha2_3, headers=self.user_agent_header).json()

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(len(test_request), 250, "Expected there to be 250 elements in output response, got {}".format(len(test_request)))

    def test_year(self):
        """ Testing single and multiple years, year ranges and greater than/less than and invalid years. """
        test_year1 = "2016"
        test_year2 = "2007"
        test_year3 = "2021"
        test_year4 = "2004"
        test_year5 = ">2017"
        test_year6 = "<2002"
        test_year7 = "abc"
        test_year8 = "12345"

        #correct column/key names for dict returned from api
        expected_output_columns = ["Code/Subdivision change", "Date Issued", "Description of change in newsletter", "Edition/Newsletter"]
#1.)
        test_request = requests.get(self.year_base_url + test_year1, headers=self.user_agent_header).json() #2016

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
                "Code/Subdivision change": "Name changed:PW-050 Hatobohei → Hatohobei",
                "Date Issued": "2016-11-15",
                "Description of change in newsletter": "Change of spelling of PW-050 in eng, pau; update list source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:PW)"
                }

        #expected output keys
        test_year_keys = ['AU', 'BD', 'BF', 'BT', 'CD', 'CI', 'CL', 'CO', 'CZ', 'DJ', 'DZ', 'FR', 'GR', 'ID', 'KE',
                          'KH', 'KZ', 'MV', 'NA', 'PW', 'SI', 'TJ', 'TW', 'UG', 'YE']

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(list(test_request), test_year_keys, "Keys of output dict from API do not match expected, got {}.".format(list(test_request)))
        self.assertEqual(len(list(test_request)), 25, "Expected there to be 25 output objects from API call, got {}.".format(len(list(test_request))))
        for alpha2 in list(test_request):
                for row in test_request[alpha2]:
                        self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
                        self.assertIsInstance(row, dict, "Ouput object of API should be of type dict, got {}".format(type(row)))


        self.assertEqual(test_request['AU'][0], test_au_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['DZ'][0], test_dz_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['MV'][0], test_mv_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['PW'][0], test_pw_expected, "Expected observed and expected outputs to match.")
#2.)
        test_request = requests.get(self.year_base_url + test_year2, headers=self.user_agent_header).json() #2007
        
        #expected test outputs
        test_ag_expected = {
                "Code/Subdivision change": "Subdivisions added: 6 parishes, 1 dependency",
                "Date Issued": "2007-04-17",
                "Description of change in newsletter": "Addition of the administrative subdivisions and of their code elements",
                "Edition/Newsletter": "Newsletter I-8 (https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)"
                }
        test_bh_expected = {
                "Code/Subdivision change": "Subdivision layout: 12 regions (see below) → 5 governorates",
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
        test_year_keys = ['AD', 'AG', 'BA', 'BB', 'BG', 'BH', 'BL', 'CI', 'CZ', 'DM', 'DO', 'EG', 'FR', 'GB', 'GD', 'GE', 'GG', 'GN', 'HT', 'IM', \
                'IR', 'IT', 'JE', 'KE', 'KN', 'KW', 'LB', 'LC', 'LI', 'LR', 'ME', 'MF', 'MK', 'MT', 'NR', 'PW', 'RS', 'RU', 'RW', 'SB', 'SC', 'SD', \
                'SG', 'SM', 'TD', 'TO', 'TV', 'UG', 'VC', 'YE', 'ZA']

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(list(test_request), test_year_keys, "Keys of output dict from API do not match expected, got {}.".format(list(test_request)))
        self.assertEqual(len(list(test_request)), 51, "Expected there to be 51 output objects from API call, got {}.".format(len(list(test_request))))
        for alpha2 in list(test_request):
                for row in test_request[alpha2]:
                        self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
                        self.assertIsInstance(row, dict, "Ouput object of API should be of type dict, got {}".format(type(row)))
        self.assertEqual(test_request['AG'][0], test_ag_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['BH'][0], test_bh_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['GD'][0], test_gd_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['SM'][0], test_sm_expected, "Expected observed and expected outputs to match.")
#3.)
        test_request = requests.get(self.year_base_url + test_year3, headers=self.user_agent_header).json() #2021

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
        test_year_keys = ['CN', 'ET', 'FR', 'GB', 'GT', 'HU', 'IS', 'KH', 'LT', 'LV', 'NP', 'PA', 'RU', 'SS']

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(list(test_request), test_year_keys, "Keys of output dict from API do not match expected, got {}.".format(list(test_request)))
        self.assertEqual(len(list(test_request)), 14, "Expected there to be 14 output objects from API call, got {}.".format(len(list(test_request))))
        for alpha2 in list(test_request):
                for row in test_request[alpha2]:
                        self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
                        self.assertIsInstance(row, dict, "Ouput object of API should be of type dict, got {}".format(type(row)))
        self.assertEqual(test_request['CN'][0], test_cn_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['ET'][0], test_et_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['NP'][0], test_np_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['SS'][0], test_ss_expected, "Expected observed and expected outputs to match.")
#4.)
        test_request = requests.get(self.year_base_url + test_year4, headers=self.user_agent_header).json() #2004

        #expected test outputs
        test_af_expected = {
                "Code/Subdivision change": "Subdivisions added: AF-KHO Khowst AF-NUR Nūrestān",
                "Date Issued": "2004-03-08",
                "Description of change in newsletter": "Addition of 2 provinces. Update of list source",
                "Edition/Newsletter": "Newsletter I-6 (https://web.archive.org/web/20081218103224/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf)"
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
                "Code/Subdivision change": "Codes: ZA-NP Northern Province → ZA-LP Limpopo",
                "Date Issued": "2004-03-08",
                "Description of change in newsletter": "Change of name of Northern Province to Limpopo",
                "Edition/Newsletter": "Newsletter I-6 (https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf)"
                }

        #expected key outputs
        test_year_keys = ['AF', 'AL', 'AU', 'CN', 'CO', 'ID', 'KP', 'MA', 'TN', 'ZA']

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(list(test_request), test_year_keys, "Keys of output dict from API do not match expected, got {}.".format(list(test_request)))
        self.assertEqual(len(list(test_request)), 10, "Expected there to be 10 output objects from API call, got {}.".format(len(list(test_request))))
        for alpha2 in list(test_request):
                for row in test_request[alpha2]:
                        self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
                        self.assertIsInstance(row, dict, "Ouput object of API should be of type dict, got {}".format(type(row)))
        self.assertEqual(test_request['AF'][0], test_af_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['CO'][0], test_co_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['KP'][0], test_kp_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['ZA'][0], test_za_expected, "Expected observed and expected outputs to match.")
#5.)
        test_request = requests.get(self.year_base_url + test_year5, headers=self.user_agent_header).json() #>2017

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
                "Code/Subdivision change": "Subdivisions renamed: VE-X Vargas → La Guaira",
                "Date Issued": "2020-11-24",
                "Description of change in newsletter": "Change of subdivision name of VE-X; Update List Source; Correction of the Code Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:VE)"
                }

        #expected key outputs
        test_year_keys = ['AF', 'AM', 'AO', 'BA', 'BD', 'BG', 'BN', 'BS', 'BT', 'BY', 'CH', 'CL', 'CN', 'CY', 'CZ', 'DZ', \
                'EE', 'ES', 'ET', 'FI', 'FR', 'GB', 'GH', 'GL', 'GQ', 'GR', 'GT', 'GW', 'HU', 'ID', 'IN', 'IQ', 'IR', 'IS',\
                'IT', 'KG', 'KH', 'KP', 'KZ', 'LK', 'LS', 'LT', 'LV', 'MA', 'ME', 'MK', 'MU', 'MV', 'NA', 'NO', 'NP', 'NR',\
                'NZ', 'PA', 'PH', 'PK', 'PL', 'QA', 'RU', 'SA', 'SC', 'SD', 'SI', 'SL', 'SM', 'SS', 'ST', 'SZ', 'TD', 'TJ',\
                'TL', 'TT', 'TZ', 'UG', 'VE', 'VN', 'ZA']

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(list(test_request), test_year_keys, "Keys of output dict from API do not match expected, got {}.".format(list(test_request)))
        self.assertEqual(len(list(test_request)), 77, "Expected there to be 77 output objects from API call, got {}.".format(len(list(test_request))))
        for alpha2 in list(test_request):
                for row in test_request[alpha2]:
                        self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
                        self.assertIsInstance(row, dict, "Ouput object of API should be of type dict, got {}".format(type(row)))
        self.assertEqual(test_request['CL'][0], test_cl_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['GH'][0], test_gh_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['SA'][0], test_sa_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['VE'][0], test_ve_expected, "Expected observed and expected outputs to match.")
#6.)  
        test_request = requests.get(self.year_base_url + test_year6, headers=self.user_agent_header).json() #<2002

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
        test_year_keys = ['BY', 'CA', 'DO', 'ER', 'ES', 'IT', 'KR', 'NG', 'PL', 'RO', 'RU', 'TR', 'VN']

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(list(test_request), test_year_keys, "Keys of output dict from API do not match expected, got {}.".format(list(test_request)))
        self.assertEqual(len(list(test_request)), 13, "Expected there to be 13 output objects from API call, got {}.".format(len(list(test_request))))
        for alpha2 in list(test_request):
                for row in test_request[alpha2]:
                        self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
                        self.assertIsInstance(row, dict, "Ouput object of API should be of type dict, got {}".format(type(row)))
        self.assertEqual(test_request['CA'][0], test_ca_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['IT'][0], test_it_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['RO'][0], test_ro_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(test_request['TR'][0], test_tr_expected, "Expected observed and expected outputs to match.")
#7.) 
        test_request = requests.get(self.year_base_url + test_year7, headers=self.user_agent_header).json() #abc

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        # self.assertEqual(test_request, {}, "Ouput object of API should be an empty dict, got {}.".format(test_request)) #Should return nothing
        # self.assertEqual(len(list(test_request)), 0, "Expected there to be 0 output objects from API call, got {}.".format(len(list(test_request))))
#8.) 
        test_request = requests.get(self.year_base_url + test_year8, headers=self.user_agent_header).json() #1234

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}.".format(type(test_request)))
        # self.assertEqual(test_request, {}, "Ouput object of API should be an empty dict, got {}.".format(test_request)) #Should return nothing
        # self.assertEqual(len(list(test_request)), 0, "Expected there to be 0 output objects from API call, got {}.".format(len(list(test_request))))

    def test_alpha2_year(self):
        """ Testing varying combinations of alpha2 codes with years/year ranges. """
        test_ad_2015 = ("AD", "2015") #Andorra 2015
        test_es_2002 = ("ES", "2002") #Spain 2002
        test_hr_2011 = ("HR", "2011") #Croatia 2011
        test_ma_2019 = ("MA", "2019") #Morocco 2019
        test_tw_lt_2010 = ("TW", "<2010") #Taiwan <2010
        test_ve_2013 = ("VE", "2013") #Venezuela 2013 {}
        test_abc_2000 = ("abc", "2000") 

        #correct column/key names for dict returned from api
        expected_output_columns = ["Code/Subdivision change", "Date Issued", "Description of change in newsletter", "Edition/Newsletter"]
#1.)
        test_request = requests.get(self.base_url + '?alpha2=' + test_ad_2015[0] + '&year=' + test_ad_2015[1], headers=self.user_agent_header).json() #Andorra - 2015
        
        #expected test outputs
        test_ad_2015_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2015-11-27",
                "Description of change in newsletter": "Update List Source",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:AD)"
                }

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(list(test_request), ['AD'], "Expected AD to be the only key returned from API in dict, got {}.".format(list(test_request)))
        self.assertEqual(len(test_request), 1, "Expected 1 row returned from API, got {}.".format(len(test_request)))
        for alpha2 in list(test_request):
                for row in test_request[alpha2]:
                        self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
                        self.assertIsInstance(row, dict, "Ouput object of API should be of type dict, got {}".format(type(row)))
        self.assertIsInstance(test_request[test_ad_2015[0]], list, "Ouput object of API should be of type list, got {}".format(type(test_request[test_ad_2015[0]])))
        self.assertEqual(test_ad_2015_expected, test_request[test_ad_2015[0]][0], "Expected object to be in output of API.")
        self.assertEqual(str(datetime.datetime.strptime(test_request[test_ad_2015[0]][0]["Date Issued"], "%Y-%m-%d").year), "2015", 
                "Year in Date Issued column does not match expected, got {}.".format(datetime.datetime.strptime(test_request[test_ad_2015[0]][0]["Date Issued"], "%Y-%m-%d").year))
#2.)   
        test_request = requests.get(self.base_url + '?alpha2=' + test_es_2002[0] + '&year=' + test_es_2002[1], headers=self.user_agent_header).json() #Spain - 2002

        #expected test outputs
        test_es_2002_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2002-12-10",
                "Description of change in newsletter": "Error correction: Regional subdivision indicator corrected in ES-PM",
                "Edition/Newsletter": "Newsletter I-4 (https://web.archive.org/web/20081218103210/http://www.iso.org/iso/iso_3166-2_newsletter_i-4_en.pdf)"
                }

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(list(test_request), ['ES'], "Expected ES to be the only key returned from API in dict, got {}.".format(list(test_request)))
        self.assertEqual(len(test_request), 1, "Expected 1 row returned from API, got {}.".format(len(test_request)))
        for alpha2 in list(test_request):
                for row in test_request[alpha2]:
                        self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
                        self.assertIsInstance(row, dict, "Ouput object of API should be of type dict, got {}".format(type(row)))       
        self.assertIsInstance(test_request[test_es_2002[0]], list, "Ouput object of API should be of type list, got {}".format(type(test_request[test_es_2002[0]])))
        self.assertEqual(test_es_2002_expected, test_request[test_es_2002[0]][0], "Expected object to be in output of API.")
        self.assertEqual(str(datetime.datetime.strptime(test_request[test_es_2002[0]][0]["Date Issued"], "%Y-%m-%d").year), "2002", 
                "Year in Date Issued column does not match expected, got {}.".format(datetime.datetime.strptime(test_request[test_es_2002[0]][0]["Date Issued"], "%Y-%m-%d").year))
#3.) 
        test_request = requests.get(self.base_url + '?alpha2=' + test_hr_2011[0] + '&year=' + test_hr_2011[1], headers=self.user_agent_header).json()

        #expected test outputs
        test_hr_2011_expected = {
                "Code/Subdivision change": "",
                "Date Issued": "2011-12-15",
                "Description of change in newsletter": "Alphabetical re-ordering.",
                "Edition/Newsletter": "Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf)"
                }

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(list(test_request), ['HR'], "Expected HR to be the only key returned from API in dict, got {}.".format(list(test_request)))
        self.assertEqual(len(test_request), 1, "Expected 1 row returned from API, got {}.".format(len(test_request)))
        for alpha2 in list(test_request):
                for row in test_request[alpha2]:
                        self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
                        self.assertIsInstance(row, dict, "Ouput object of API should be of type dict, got {}".format(type(row)))
        self.assertIsInstance(test_request[test_hr_2011[0]], list, "Ouput object of API should be of type list, got {}".format(type(test_request[test_hr_2011[0]])))
        self.assertEqual(test_hr_2011_expected, test_request[test_hr_2011[0]][0], "Expected object to be in output of API.")
        self.assertEqual(str(datetime.datetime.strptime(test_request[test_hr_2011[0]][0]["Date Issued"], "%Y-%m-%d").year), "2011", 
                "Year in Date Issued column does not match expected, got {}.".format(datetime.datetime.strptime(test_request[test_hr_2011[0]][0]["Date Issued"], "%Y-%m-%d").year))
#4.)
        test_request = requests.get(self.base_url + '?alpha2=' + test_ma_2019[0] + '&year=' + test_ma_2019[1], headers=self.user_agent_header).json()

        #expected test outputs
        test_ma_2019_expected = {
                "Code/Subdivision change": "Parent changes:MA-CAS MA-08 → MA-06MA-SET MA-08 → MA-06MA-SIK MA-06 → MA-04Spelling change:MA-03 Fès- Meknès → Fès-Meknès",
                "Date Issued": "2019-04-09",
                "Description of change in newsletter": "",
                "Edition/Newsletter": "Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:MA)"
                }

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(list(test_request), ['MA'], "Expected MA to be the only key returned from API in dict, got {}.".format(list(test_request)))
        self.assertEqual(len(test_request), 1, "Expected 1 row returned from API, got {}.".format(len(test_request)))
        for alpha2 in list(test_request):
                for row in test_request[alpha2]:
                        self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
                        self.assertIsInstance(row, dict, "Ouput object of API should be of type dict, got {}".format(type(row)))                
        self.assertIsInstance(test_request[test_ma_2019[0]], list, "Ouput object of API should be of type list, got {}".format(type(test_request[test_ma_2019[0]])))
        self.assertEqual(test_ma_2019_expected, test_request[test_ma_2019[0]][0], "Expected object to be in output of API.")
        self.assertEqual(str(datetime.datetime.strptime(test_request[test_ma_2019[0]][0]["Date Issued"], "%Y-%m-%d").year), "2019", 
                "Year in Date Issued column does not match expected, got {}.".format(datetime.datetime.strptime(test_request[test_ma_2019[0]][0]["Date Issued"], "%Y-%m-%d").year))
#5.)
        test_request = requests.get(self.base_url + '?alpha2=' + test_tw_lt_2010[0] + '&year=' + test_tw_lt_2010[1], headers=self.user_agent_header).json()
            
        #expected test outputs
        test_tw_lt_2010_expected = {
                "Code/Subdivision change": "Codes: (to correct duplicate use)Chiayi (district): TW-CYI → TW-CYQHsinchu (district): TW-HSZ → TW-HSQKaohsiung"\
                "(district): TW-KHH → TW-KHQTaichung (district): TW-TXG → TW-TXQTainan (district): TW-TNN → TW-TNQTaipei (district): TW-TPE → TW-TPQ",
                "Date Issued": "2002-12-10",
                "Description of change in newsletter": "Error correction: Duplicate use of six code elements corrected. Subdivision categories in header re-sorted",
                "Edition/Newsletter": "Newsletter I-4 (https://web.archive.org/web/20081218103210/http://www.iso.org/iso/iso_3166-2_newsletter_i-4_en.pdf)"
                }

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(list(test_request), ['TW'], "Expected TW to be the only key returned from API in dict, got {}.".format(list(test_request)))
        self.assertEqual(len(test_request), 1, "Expected 1 row returned from API, got {}.".format(len(test_request)))
        for alpha2 in list(test_request):
                for row in test_request[alpha2]:
                        self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
                        self.assertIsInstance(row, dict, "Ouput object of API should be of type dict, got {}".format(type(row)))
        self.assertIsInstance(test_request[test_tw_lt_2010[0]], list, "Ouput object of API should be of type list, got {}".format(type(test_request[test_tw_lt_2010[0]])))
        # self.assertEqual(test_tw_lt_2010_expected, test_request[test_tw_lt_2010[0]][0], "Expected object to be in output of API.")
        self.assertTrue(str(datetime.datetime.strptime(test_request[test_tw_lt_2010[0]][0]["Date Issued"], "%Y-%m-%d").year) < "2010",
                "Year in Date Issued column should be less than 2010, got {}.".format(datetime.datetime.strptime(test_request[test_tw_lt_2010[0]][0]["Date Issued"], "%Y-%m-%d").year))
#6.) 
        test_request = requests.get(self.base_url + '?alpha2=' + test_abc_2000[0] + '&year=' + test_abc_2000[1], headers=self.user_agent_header).json()
        
        test_abc_2000_expected = {
                "Code/Subdivision change": "Subdivision layout: 10 provinces (see below) → 6 provinces",
                "Date Issued": "2000-06-21",
                "Description of change in newsletter": "Introduction of a completely new subdivision layout",
                "Edition/Newsletter": "Newsletter I-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf)"
                }

        #expected key outputs
        test_year_keys = ['BY', 'CA', 'DO', 'ER', 'ES', 'IT', 'KR', 'NG', 'PL', 'RO', 'RU', 'TR', 'VN']

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(list(test_request), test_year_keys, "Keys of output dict from API do not match expected, got {}.".format(list(test_request)))
        self.assertEqual(len(test_request), 13, "Expected 13 rows returned from API, got {}.".format(len(test_request)))
        for alpha2 in list(test_request):
                for row in test_request[alpha2]:
                        self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
                        self.assertIsInstance(row, dict, "Ouput object of API should be of type dict, got {}".format(type(row)))
        self.assertEqual(test_request['ER'][0], test_abc_2000_expected, "Expected observed and expected outputs to match.")
        self.assertEqual(str(datetime.datetime.strptime(test_request["ER"][0]["Date Issued"], "%Y-%m-%d").year), "2000",
                "Year in Date Issued column should be less than 2010, got {}.".format(datetime.datetime.strptime(test_request["ER"][0]["Date Issued"], "%Y-%m-%d").year))
#7.)
        test_request = requests.get(self.base_url + '?alpha2=' + test_ve_2013[0] + '&year=' + test_ve_2013[1], headers=self.user_agent_header).json()

        #expected test outputs
        test_ve_2013_expected = {}

        self.assertIsInstance(test_request, dict, "Ouput object of API should be of type dict, got {}".format(type(test_request)))
        self.assertEqual(len(test_request), 0, "Expected 0 rows returned from API, got {}.".format(len(test_request)))
        self.assertEqual(test_request, test_ve_2013_expected, "Expected output of API to be an empty dict.")

    def tearDown(self):
        """  """
        pass

if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)