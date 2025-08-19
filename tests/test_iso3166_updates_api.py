import unittest
import requests
import re
import os
from jsonschema import validate, ValidationError
from datetime import datetime,date
from fake_useragent import UserAgent
from iso3166_updates import * 
from bs4 import BeautifulSoup
from importlib.metadata import metadata
unittest.TestLoader.sortTestMethodsUsing = None

# @unittest.skip("Skipping prior to new published release of iso3166-updates.")
class Updates_Api_Tests(unittest.TestCase):
    """
    Test suite for testing ISO 3166 Updates API created to accompany the iso3166-updates 
    Python software package. The API has 7 main endpoints to test:
    - /api
    - /api/all
    - /api/alpha
    - /api/year
    - /api/country_name
    - /api/search
    - /api/date_range

    Test Cases
    ==========
    test_homepage_endpoint:
        testing main endpoint that returns the homepage and API documentation. 
    test_all_endpoint:
        testing /all endpoint, validating that it returns updates data for all countries. 
    test_json_schema_all_endpoint:
        testing JSON schema for all data using /api/all endpoint.
    test_all_endpoint_duplicates:
        testing /all endpoint, validating that there are no duplicate objects.  
    test_all_endpoint_individual_totals:
        testing the individual total number of updates per country from /api/all endpoint.  
    test_alpha_endpoint:
        testing /alpha2 endpoint, validating correct data and output object returned, using a variety of alpha-2 codes.
    test_year_endpoint:
        testing /year endpoint, validating correct data and output object returned, using a variety of years.
    test_country_name_endpoint:
        testing /country_name endpoint, validating correct data and output object returned, using a variety of country names.
    test_country_name_year_endpoint:
        testing /country_name/year endpoint, validating correct data and output object returned, using a variety of country names
        and years.
    test_search_endpoint:
        testing /search endpoint, validating correct data and output object returned, using a variety of search terms.
    test_alpha_year_endpoint:
        testing /alpha/year endpoint, validating correct data and output object returned, using a variety of alpha-2 codes
        and years.
    test_date_range_endpoint:
        testing /date_range endpoint, validating correct data and output object returned, using a variety of date ranges.
    test_date_range_alpha_endpoint:
        testing /date_range/alpha endpoint, validating correct data and output object returned, using a variety of date 
        ranges and alpha country codes. 
    """     
    def setUp(self):
        """ Initialise test variables including base urls for API. """
        self.base_url = "https://iso3166-updates.vercel.app/api"

        #get version and random user-agent
        self.__version__ = metadata('iso3166_updates')['version']
        user_agent = UserAgent()
        self.user_agent_header = {"User-Agent": user_agent.random, 'Accept': 'application/json'}

        #base endpoint urls
        self.alpha_base_url = self.base_url + "/alpha/"
        self.year_base_url = self.base_url + '/year/'
        self.all_base_url = self.base_url + '/all'
        self.country_name_base_url = self.base_url + '/country_name/'
        self.date_range_url = self.base_url + '/date_range/'
        self.search_url = self.base_url + '/search/'

        #correct column/key names for dict returned from api
        self.expected_output_columns = ["Change", "Date Issued", "Description of Change", "Source"]

        #turn off tqdm progress bar functionality when running tests
        os.environ["TQDM_DISABLE"] = "1"

        #object of updates from iso3166-updates software
        all_iso3166_updates_obj = Updates()
        self.all_iso3166_updates = all_iso3166_updates_obj.all

        #call /api/all endpoint to get all data from API
        self.test_request_all = requests.get(self.all_base_url, headers=self.user_agent_header)

#     @unittest.skip("")
    def test_homepage_endpoint(self):
        """ Testing contents of main '/api' endpoint that returns the homepage and API documentation. """
        test_request_main = requests.get(self.base_url, headers=self.user_agent_header)
        soup = BeautifulSoup(test_request_main.content, 'html.parser')
#1.)
        # version = soup.find(id='version').text.split(': ')[1]
        # last_updated = soup.find(id='last-updated').text.split(': ')[1]
        author = soup.find(id='author').text.split(': ')[1]

        # self.assertEqual(version, "1.8.3", f"Expected API version to be 1.8.3, got {version}.")
        # self.assertEqual(last_updated, "May 2025", f"Expected last updated date to be May 2025, got {last_updated}.")
        self.assertEqual(author, "AJ", f"Expected author to be AJ, got {author}.")
#2.)
        section_list_menu = soup.find(id='section-list-menu').find_all('li')
        correct_section_menu = ["About", "Attributes", "Query String Parameters", "Endpoints", "All", "Alpha Code", "Country Name", "Year", "Search", "Date Range", "Contributing", "Credits"]
        for li in section_list_menu:
            self.assertIn(li.text.strip(), correct_section_menu, f"Expected list element {li} to be in list.")

#     @unittest.skip("")
    def test_all_endpoint(self):
        """ Testing '/api/all' endpoint that returns all updates data for all countries. """
#1.)    
        self.assertIsInstance(self.test_request_all.json(), dict, f"Expected output object of API to be of type dict, got {type(self.test_request_all.json())}.")
        self.assertEqual(len(self.test_request_all.json()), 250, f"Expected there to be 250 elements in output object, got {len(self.test_request_all.json())}.")
        self.assertEqual(self.test_request_all.status_code, 200, f"Expected 200 status code from request, got {self.test_request_all.status_code}.")
        self.assertEqual(self.test_request_all.headers["content-type"], "application/json", f"Expected Content type to be application/json, got {self.test_request_all.headers['content-type']}.")

        total_updates = sum(len(changes) for changes in self.all_iso3166_updates.values())
        self.assertEqual(total_updates, 911, f"Expected and observed total updates do not match, got {total_updates}.")
#2.)
        for alpha2 in list(self.test_request_all.json().keys()):
            self.assertIn(alpha2, iso3166.countries_by_alpha2, f"Alpha-2 code {alpha2} not found in list of available country codes.")
#3.)
        test_request_all_sort_by_date = requests.get(self.all_base_url, headers=self.user_agent_header, params={"sortby": "dateDesc"})

        self.assertIsInstance(test_request_all_sort_by_date.json(), list, f"Expected output object of API to be of type list, got {type(test_request_all_sort_by_date.json())}.")
        self.assertEqual(len(test_request_all_sort_by_date.json()), 910, f"Expected there to be 910 elements in output object, got {len(test_request_all_sort_by_date.json())}.")
        self.assertEqual(test_request_all_sort_by_date.status_code, 200, f"Expected 200 status code from request, got {test_request_all_sort_by_date.status_code}.")
        self.assertEqual(test_request_all_sort_by_date.headers["content-type"], "application/json", f"Expected Content type to be application/json, got {test_request_all_sort_by_date.headers['content-type']}.")

        #list to store all publication dates for all updates
        date_list = []

        #iterate over all updates, parse date and append to array
        for item in test_request_all_sort_by_date.json():
                match = re.search(r"\d{4}-\d{2}-\d{2}", item.get("Date Issued", ""))
                parsed_date = datetime.strptime(match.group(), "%Y-%m-%d") 
                date_list.append(parsed_date)

        self.assertEqual(date_list, sorted(date_list, reverse=True), "Expected updates to be sorted by date descending.")

        #validate there are no dates in the future
        for date_issued in date_list:
                self.assertLessEqual(date_issued.date(), date.today(), f"Expected there to be no publication dates in the future: {date_issued}.")
        
#     @unittest.skip("")
    def test_json_schema_all_endpoint(self):
        """ Testing the JSON schema for all the data, using the /api/all endpoint. """
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
                                "Date Issued": {
                                "type": "string",
                                "pattern": r"^\d{4}-\d{2}-\d{2}(?: \([^)]+\))?$"
                                },
                                "Source": {"type": "string", "format": "uri"}
                        },
                        "required": ["Change", "Date Issued", "Source"],
                        "additionalProperties": False
                        }
                }
                },
                "additionalProperties": False
        }
#1.)
        try:
                validate(instance=self.test_request_all.json(), schema=schema)
        except ValidationError as e:
                self.fail(f"JSON schema for /all endpoint output validation failed: {e.message}.")

#     @unittest.skip("")
    def test_all_endpoint_duplicates(self):
        """ Testing '/api/all' endpoint has no duplicate updates objects. """
#1.)
        for country_code, updates in self.test_request_all.json().items():
            unique_updates = {frozenset(update.items()) for update in updates}
            self.assertEqual(len(unique_updates), len(updates), f"Duplicates found in updates for country {country_code}:\n{updates}")
 
#     @unittest.skip("")
    def test_all_endpoint_individual_totals(self):
        """ Testing individual total number of updates per country, using /api/all endpoint. """
        #expected updates counts per country
        expected_counts = {'AD': 3, 'AE': 3, 'AF': 6, 'AG': 3, 'AI': 1, 'AL': 6, 'AM': 1, 'AO': 6, 'AQ': 1, 
                                'AR': 1, 'AS': 1, 'AT': 2, 'AU': 3, 'AW': 3, 'AX': 3, 'AZ': 3, 'BA': 6, 'BB': 3, 
                                'BD': 6, 'BE': 2, 'BF': 3, 'BG': 9, 'BH': 2, 'BI': 4, 'BJ': 3, 'BL': 5, 'BM': 1, 
                                'BN': 4, 'BO': 5, 'BQ': 7, 'BR': 2, 'BS': 3, 'BT': 5, 'BV': 3, 'BW': 3, 'BY': 5, 
                                'BZ': 2, 'CA': 4, 'CC': 1, 'CD': 3, 'CF': 3, 'CG': 4, 'CH': 2, 'CI': 4, 'CK': 1, 
                                'CL': 4, 'CM': 2, 'CN': 6, 'CO': 2, 'CR': 2, 'CU': 2, 'CV': 6, 'CW': 3, 'CX': 1, 
                                'CY': 5, 'CZ': 10, 'DE': 4, 'DJ': 6, 'DK': 1, 'DM': 3, 'DO': 6, 'DZ': 4, 'EC': 3, 
                                'EE': 3, 'EG': 4, 'EH': 1, 'ER': 7, 'ES': 9, 'ET': 7, 'FI': 3, 'FJ': 6, 'FK': 1, 
                                'FM': 4, 'FO': 1, 'FR': 11, 'GA': 2, 'GB': 13, 'GD': 4, 'GE': 5, 'GF': 2, 'GG': 4, 
                                'GH': 4, 'GI': 1, 'GL': 3, 'GM': 5, 'GN': 5, 'GP': 3, 'GQ': 3, 'GR': 8, 'GS': 1, 
                                'GT': 4, 'GU': 1, 'GW': 2, 'GY': 3, 'HK': 2, 'HM': 1, 'HN': 1, 'HR': 3, 'HT': 3, 
                                'HU': 4, 'ID': 13, 'IE': 4, 'IL': 5, 'IM': 2, 'IN': 9, 'IO': 1, 'IQ': 5, 'IR': 8, 
                                'IS': 6, 'IT': 7, 'JE': 3, 'JM': 2, 'JO': 2, 'JP': 2, 'KE': 4, 'KG': 5, 'KH': 7, 
                                'KI': 4, 'KM': 7, 'KN': 5, 'KP': 8, 'KR': 5, 'KW': 3, 'KY': 1, 'KZ': 7, 'LA': 9, 
                                'LB': 2, 'LC': 3, 'LI': 3, 'LK': 5, 'LR': 2, 'LS': 2, 'LT': 2, 'LU': 2, 'LV': 2, 
                                'LY': 7, 'MA': 8, 'MC': 2, 'MD': 11, 'ME': 11, 'MF': 5, 'MG': 3, 'MH': 4, 'MK': 7, 
                                'ML': 1, 'MM': 6, 'MN': 1, 'MO': 2, 'MP': 1, 'MQ': 2, 'MR': 4, 'MS': 1, 'MT': 3, 
                                'MU': 2, 'MV': 4, 'MW': 3, 'MX': 5, 'MY': 1, 'MZ': 0, 'NA': 3, 'NC': 1, 'NE': 1, 
                                'NF': 1, 'NG': 4, 'NI': 3, 'NL': 5, 'NO': 4, 'NP': 10, 'NR': 4, 'NU': 3, 'NZ': 6, 
                                'OM': 2, 'PA': 5, 'PE': 3, 'PF': 2, 'PG': 4, 'PH': 5, 'PK': 5, 'PL': 4, 'PM': 1, 
                                'PN': 1, 'PR': 1, 'PS': 5, 'PT': 2, 'PW': 2, 'PY': 0, 'QA': 2, 'RE': 3, 'RO': 4, 
                                'RS': 5, 'RU': 7, 'RW': 3, 'SA': 3, 'SB': 5, 'SC': 4, 'SD': 6, 'SE': 1, 'SG': 1, 
                                'SH': 3, 'SI': 8, 'SJ': 1, 'SK': 0, 'SL': 3, 'SM': 4, 'SN': 2, 'SO': 2, 'SR': 2, 
                                'SS': 4, 'ST': 1, 'SV': 1, 'SX': 5, 'SY': 4, 'SZ': 2, 'TC': 2, 'TD': 4, 'TF': 2, 
                                'TG': 2, 'TH': 1, 'TJ': 7, 'TK': 2, 'TL': 4, 'TM': 2, 'TN': 6, 'TO': 1, 'TR': 5, 
                                'TT': 2, 'TV': 4, 'TW': 5, 'TZ': 4, 'UA': 2, 'UG': 9, 'UM': 3, 'US': 3, 'UY': 2, 
                                'UZ': 3, 'VA': 3, 'VC': 4, 'VE': 8, 'VG': 1, 'VI': 1, 'VN': 7, 'VU': 0, 'WF': 2, 
                                'WS': 3, 'YE': 7, 'YT': 2, 'ZA': 4, 'ZM': 3, 'ZW': 1}
#1.)
        for code, expected_count in expected_counts.items():
            actual_count = len(self.test_request_all.json().get(code, []))
            self.assertEqual(actual_count, expected_count, 
                f"Incorrect updates total for code {code}. Expected {expected_count}, got {actual_count}.")

#     @unittest.skip("")
    def test_alpha_endpoint(self):
        """ Testing '/api/alpha' endpoint using single, multiple and invalid alpha codes for expected ISO 3166 updates. """
        test_alpha_ad = "AD" #Andorra 
        test_alpha_bo = "BOL" #Bolivia
        test_alpha_bf = "854" #Burkina Faso
        test_alpha_bn_cu_dm = "BN,CUB,262" #Brunei, Cuba, Djibouti 
        error_test_alpha_1 = "blahblahblah"
        error_test_alpha_2 = "42"
        error_test_alpha_3 = "XYZ" #invalid alpha-3 code
#1.)
        test_request_ad = requests.get(self.alpha_base_url + test_alpha_ad, headers=self.user_agent_header).json() #AD
        test_alpha_ad_expected = {"AD": [{
                "Change": "Update List Source.",
                "Date Issued": "2015-11-27",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD."
                },
                {
                "Change": "Update List Source.",
                "Date Issued": "2014-11-03",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD."
                },
                {
                "Change": "Subdivisions added: 7 parishes.",
                "Date Issued": "2007-04-17",
                "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
                "Source": "Newsletter I-8 - https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf."
                }]}
        
        self.assertEqual(test_request_ad, test_alpha_ad_expected, f"Expected and observed outputs do not match:\n{test_request_ad}.")
#2.)
        test_request_bo = requests.get(self.alpha_base_url + test_alpha_bo, headers=self.user_agent_header).json() #BOL        
        test_alpha_bo_expected = {"BO": [{
                "Change": "Change of short name upper case: replace the parentheses with a coma.",
                "Date Issued": "2024-02-29",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BO."
                },
                {
                "Change": "Alignment of the English and French short names upper and lower case with UNTERM.",
                "Date Issued": "2014-12-18",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BO."
                },
                {
                "Change": "Update List Source.",
                "Date Issued": "2014-11-03",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BO."
                },
                {
                "Change": "Change of short form country name in accordance with ISO 3166-1, NL VI-6 (2009-05-08).",
                "Date Issued": "2010-02-03 (corrected 2010-02-19)",
                "Description of Change": "",
                "Source": "Newsletter II-1 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-1_corrected_2010-02-19.pdf."
                },
                {
                "Change": "Change of short and full names.",
                "Date Issued": "2009-05-08",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BO."
                }]}

        self.assertEqual(test_request_bo, test_alpha_bo_expected, f"Expected and observed outputs do not match:\n{test_request_bo['BO']}")
#3.)
        test_request_bf = requests.get(self.alpha_base_url + test_alpha_bf, headers=self.user_agent_header).json() #854        
        test_alpha_bf_expected = {"BF": [{
                "Change": "Spelling change: BF-TUI Tui -> Tuy.",
                "Date Issued": "2016-11-15",
                "Description of Change": "Change of spelling of BF-TUI; update list source.",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BF."
                },
                {
                "Change": "Correction of the short name lowercase in French.",
                "Date Issued": "2014-04-15",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BF."
                },    
                {
                "Change": "Subdivisions added: 13 regions.",
                "Date Issued": "2010-06-30",
                "Description of Change": "Update of the administrative structure and of the list source.",
                "Source": "Newsletter II-2 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf."
                }]}

        self.assertEqual(test_request_bf, test_alpha_bf_expected, f"Expected and observed outputs do not match:\n{test_request_bf['BF'][0]}")
#4.)
        test_request_bn_cu_dm = requests.get(self.alpha_base_url + test_alpha_bn_cu_dm, headers=self.user_agent_header).json() #BN, CUB, 262
        test_bn_cu_dm_alpha_list = ['BN', 'CU', 'DJ']          
        test_alpha_bn_expected = {
                "Change": "Spelling change: BN-BM Brunei-Muara -> Brunei dan Muara (ms).",
                "Date Issued": "2019-11-22",
                "Description of Change": "Change of subdivision name of BN-BM; Update List Source.",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BN."
                }  
        test_alpha_cu_expected = {
                "Change": "Update List Source.",
                "Date Issued": "2015-11-27",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CU."
                }  
        test_alpha_dj_expected = {
                "Change": "Correction of the Code Source.",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:DJ."
                }     

        self.assertIsInstance(test_request_bn_cu_dm, dict, f"Expected output object of API to be of type dict, got {type(test_request_bn_cu_dm)}.")
        self.assertEqual(list(test_request_bn_cu_dm.keys()), test_bn_cu_dm_alpha_list, f"Expected columns do not match output, got {list(test_request_bn_cu_dm.keys())}.")
        for alpha2 in test_bn_cu_dm_alpha_list:
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
        test_request_error1 = requests.get(self.alpha_base_url + error_test_alpha_1, headers=self.user_agent_header).json() #blahblahblah
        test_request_error1_expected = {"message": f"Invalid ISO 3166-1 alpha-2 code input: {error_test_alpha_1}.", "path": self.alpha_base_url + error_test_alpha_1, "status": 400}
        self.assertEqual(test_request_error1, test_request_error1_expected, f"Expected and observed output error object do not match:\n{test_request_error1}")
#6.)
        test_request_error2 = requests.get(self.alpha_base_url + error_test_alpha_2, headers=self.user_agent_header).json() #42
        test_request_error2_expected = {"message": f"Invalid ISO 3166-1 alpha numeric country code input: {error_test_alpha_2}.", "path": self.alpha_base_url + error_test_alpha_2, "status": 400}
        self.assertEqual(test_request_error2, test_request_error2_expected, f"Expected and observed output error object do not match:\n{test_request_error2}")
#7.)
        test_request_error3 = requests.get(self.alpha_base_url + error_test_alpha_3, headers=self.user_agent_header).json() #xyz
        test_request_error3_expected = {"message": f"Invalid ISO 3166-1 alpha-3 country code: {error_test_alpha_3.upper()}.", "path": self.alpha_base_url + error_test_alpha_3, "status": 400}
        self.assertEqual(test_request_error3, test_request_error3_expected, f"Expected and observed output error object do not match:\n{test_request_error3}")

#     @unittest.skip("")
    def test_year_endpoint(self): 
        """ Testing '/api/year' path/endpoint using single and multiple years, year ranges and greater than/less than and invalid years. """
        test_year_2016 = "2016"
        test_year_2007 = "2007"
        test_year_2004_2009 = "2004-2009"
        test_year_gt_2017 = ">2017"
        test_year_lt_2002 = "<2002"
        test_year_not_equal_2011_2020 = "<>2011,2020"
        test_year_abc = "abc"
        test_year_12345 = "12345"
#1.)
        test_request_year_2016 = requests.get(self.year_base_url + test_year_2016, headers=self.user_agent_header).json() #2016
        test_au_expected = {
                "Change": "Update List Source; update Code Source.",
                "Date Issued": "2016-11-15",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AU."
                }
        test_dz_expected = {
                "Change": "Change of spelling of DZ-28; Update list source.",
                "Date Issued": "2016-11-15",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:DZ."
                }
        test_mv_expected = {
                "Change": "Spelling change: MV-05.",
                "Date Issued": "2016-11-15",
                "Description of Change": "Change of spelling of MV-05.",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:MV."
                }
        test_pw_expected = {
                "Change": "Name changed: PW-050 Hatobohei -> Hatohobei.",
                "Date Issued": "2016-11-15",
                "Description of Change": "Change of spelling of PW-050 in eng, pau; update list source.",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:PW."
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
        test_request_year_2007 = requests.get(self.year_base_url + test_year_2007, headers=self.user_agent_header).json() #2007
        test_ag_expected = {
                "Change": "Subdivisions added: 6 parishes, 1 dependency.",
                "Date Issued": "2007-04-17",
                "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
                "Source": "Newsletter I-8 - https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf."
                }
        test_bh_expected = {
                "Change": "Subdivision layout: 12 regions -> 5 governorates.",
                "Date Issued": "2007-04-17",
                "Description of Change": "Modification of the administrative structure.",
                "Source": "Newsletter I-8 - https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf."
                }
        test_gd_expected = {
                "Change": "Subdivisions added: 6 parishes, 1 dependency.",
                "Date Issued": "2007-04-17",
                "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
                "Source": "Newsletter I-8 - https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf."
                }
        test_sm_expected = {
                "Change": "Subdivisions added: 9 municipalities.",
                "Date Issued": "2007-04-17",
                "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
                "Source": "Newsletter I-8 - https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf."
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
        test_request_year_2004_2009 = requests.get(self.year_base_url + test_year_2004_2009, headers=self.user_agent_header).json() #2004-2009
        test_af_expected = {
                "Change": "Subdivisions added: AF-DAY Dāykondī. AF-PAN Panjshīr.",
                "Date Issued": "2005-09-13",
                "Description of Change": "Addition of 2 provinces. Update of list source.",
                "Source": "Newsletter I-7 - https://web.archive.org/web/20081218103217/http://www.iso.org/iso/iso_3166-2_newsletter_i-7_en.pdf."
                }
        test_co_expected = {
                "Change": "Change of name of CO-DC.",
                "Date Issued": "2004-03-08",
                "Description of Change": "",
                "Source": "Newsletter I-6 - https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf."
                }
        test_kp_expected = {
                "Change": "Spelling correction in header of list source.",
                "Date Issued": "2004-03-08",
                "Description of Change": "",
                "Source": "Newsletter I-6 - https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf."
                }
        test_za_expected = {
                "Change": "Codes: Gauteng: ZA-GP -> ZA-GT. KwaZulu-Natal: ZA-ZN -> ZA-NL.",
                "Date Issued": "2007-12-13",
                "Description of Change": "Second edition of ISO 3166-2 (not announced in a newsletter).",
                "Source": "ISO 3166-2:2007 - http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=39718."
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
        test_request_year_gt_2017 = requests.get(self.year_base_url + test_year_gt_2017, headers=self.user_agent_header).json() #>2017
        test_cl_expected = {
                "Change": "Subdivisions added: CL-NB Ñuble.",
                "Date Issued": "2018-11-26",
                "Description of Change": "Addition of region CL-NB; Update List Source.",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CL."
                }
        test_gh_expected = {
                "Change": "Correction of the Code Source.",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:GH."
                }
        test_sa_expected = {
                "Change": "Change of subdivision category from province to region.",
                "Date Issued": "2018-11-26",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:SA."
                }
        test_ve_expected = {
                "Change": "Change of short name upper case: replace the parentheses with a comma.",
                "Date Issued": "2024-02-29",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:VE."
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
        test_request_year_lt_2002 = requests.get(self.year_base_url + test_year_lt_2002, headers=self.user_agent_header).json() #<2002
        test_ca_expected = {
                "Change": "Subdivisions added: CA-NU Nunavut.",
                "Date Issued": "2000-06-21",
                "Description of Change": "Addition of 1 new territory.",
                "Source": "Newsletter I-1 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf."
                }
        test_it_expected = {
                "Change": "Correction of spelling mistakes of names of 2 provinces.",
                "Date Issued": "2000-06-21",
                "Description of Change": "",
                "Source": "Newsletter I-1 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf."
                }
        test_ro_expected = {
                "Change": "Correction of spelling mistake of subdivision category in header.",
                "Date Issued": "2000-06-21",
                "Description of Change": "",
                "Source": "Newsletter I-1 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf."
                }
        test_tr_expected = {
                "Change": "Subdivisions added: TR-80 Osmaniye.",
                "Date Issued": "2000-06-21",
                "Description of Change": "Addition of 1 new province. Correction of 2 spelling errors.",
                "Source": "Newsletter I-1 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_i-1_en.pdf."
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
        test_request_year_not_equal_2011_2020 = requests.get(self.year_base_url + test_year_not_equal_2011_2020, headers=self.user_agent_header).json() #<>2011,2020
        test_year_lt_2002_keys = ['AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AW', 'AX', 'AZ', 'BA', 'BB', 'BD', 'BE', 'BF', 'BG', 
                                  'BH', 'BI', 'BJ', 'BL', 'BM', 'BN', 'BO', 'BQ', 'BR', 'BS', 'BT', 'BV', 'BW', 'BY', 'BZ', 'CA', 'CC', 'CD', 'CF', 'CG', 'CH', 'CI', 
                                  'CK', 'CL', 'CM', 'CN', 'CO', 'CR', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ', 'DE', 'DJ', 'DM', 'DO', 'DZ', 'EC', 'EE', 'EG', 'EH', 'ER', 
                                  'ES', 'ET', 'FI', 'FJ', 'FK', 'FM', 'FO', 'FR', 'GA', 'GB', 'GD', 'GE', 'GF', 'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GR', 
                                  'GS', 'GT', 'GU', 'GW', 'GY', 'HK', 'HM', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM', 'IN', 'IO', 'IQ', 'IR', 'IS', 'IT', 'JE', 'JM', 
                                  'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KP', 'KR', 'KW', 'KY', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LT', 'LU', 'LV', 
                                  'LY', 'MA', 'MD', 'ME', 'MF', 'MG', 'MH', 'MK', 'ML', 'MM', 'MN', 'MO', 'MP', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 
                                  'NA', 'NC', 'NE', 'NF', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG', 'PH', 'PK', 'PL', 'PM', 'PN', 
                                  'PR', 'PS', 'PT', 'PW', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW', 'SA', 'SB', 'SC', 'SD', 'SG', 'SH', 'SI', 'SJ', 'SL', 'SM', 'SN', 'SO', 
                                  'SR', 'SS', 'SV', 'SX', 'SY', 'SZ', 'TC', 'TD', 'TF', 'TG', 'TH', 'TJ', 'TK', 'TL', 'TM', 'TN', 'TO', 'TR', 'TT', 'TV', 'TW', 'TZ', 
                                  'UA', 'UG', 'UM', 'US', 'UY', 'UZ', 'VA', 'VC', 'VE', 'VG', 'VI', 'VN', 'WF', 'WS', 'YE', 'YT', 'ZA', 'ZM', 'ZW']

        self.assertIsInstance(test_request_year_not_equal_2011_2020, dict, f"Expected output object of API to be of type dict, got {type(test_request_year_not_equal_2011_2020)}.")
        self.assertEqual(list(test_request_year_not_equal_2011_2020), test_year_lt_2002_keys, f"Expected keys of output dict from API do not match, got {list(test_request_year_not_equal_2011_2020)}.")
        self.assertEqual(len(list(test_request_year_not_equal_2011_2020)), 239, f"Expected there to be 239 output objects from API call, got {len(list(test_request_year_not_equal_2011_2020))}.")
        for alpha2 in list(test_request_year_not_equal_2011_2020):
                for row in range(0, len(test_request_year_not_equal_2011_2020[alpha2])):
                        current_updates_year = extract_date(test_request_year_not_equal_2011_2020[alpha2][row]["Date Issued"])
                        self.assertEqual(list(test_request_year_not_equal_2011_2020[alpha2][row].keys()), self.expected_output_columns, f"Expected columns do not match output, got\n{list(test_request_year_not_equal_2011_2020[alpha2][row].keys())}.")
                        self.assertIsInstance(test_request_year_not_equal_2011_2020[alpha2][row], dict, f"Expected output row of object of API to be of type dict, got {type(test_request_year_not_equal_2011_2020[alpha2][row])}.")
                        self.assertTrue((current_updates_year!= 2011 and current_updates_year != 2020), 
                                f"Year in Date Issued column should not equal 2011 or 2020, got {current_updates_year}.")
#7.)
        test_request_year_abc = requests.get(self.year_base_url + test_year_abc, headers=self.user_agent_header).json() #abc
        test_request_year_abc_expected = {"message": f"Invalid year input, must be a valid year >= 1996, got {test_year_abc}.", "path": self.year_base_url + test_year_abc, "status": 400}
        self.assertEqual(test_request_year_abc, test_request_year_abc_expected, f"Expected and observed output error object do not match:\n{test_request_year_abc}")
#8.) 
        test_request_year_12345 = requests.get(self.year_base_url + test_year_12345, headers=self.user_agent_header).json() #1234
        test_request_year_12345_expected = {"message": f"Invalid year input, must be a valid year >= 1996, got {test_year_12345}.", "path": self.year_base_url + test_year_12345, "status": 400}
        self.assertEqual(test_request_year_12345, test_request_year_12345_expected, f"Expected and observed output error object do not match:\n{test_request_year_12345}")

#     @unittest.skip("")
    def test_alpha_year_endpoint(self):
        """ Testing '/api/alpha/year' path/endpoint, using various combinations of alpha codes with years, and year ranges. """
        test_ad_2015 = ("AD", "2015") #Andorra 2015
        test_es_2002 = ("ESP", "2002") #Spain 2002
        test_tr_2002 = ("792", ">2020") #Turkey >2020
        test_ma_mh_nr_lt_2011 = ("MA,MHL,520", "<2011") #Morocco, Marshall Islands, Nauru <2011
        test_ve_2004_2008 = ("VE", "2004-2008") #Venezuela 2004-2008
        test_pe_pr_ne_2014 = ("PE,PRI", "<>2014") #Peru, Puerto Rico - <>2014
        test_abc_2000 = ("abc", "2000") 
        test_de_12345 = ("DE", "12345") 
#1.)
        test_ad_2015_request = requests.get(f"{self.alpha_base_url}{test_ad_2015[0]}/year/{test_ad_2015[1]}", headers=self.user_agent_header).json() #Andorra - 2015
        test_ad_2015_expected = {"AD": [{
                "Change": "Update List Source.",
                "Date Issued": "2015-11-27",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD."
                }]}
        
        self.assertEqual(test_ad_2015_expected, test_ad_2015_request, f"Observed and expected outputs of API do not match:\n{test_ad_2015_request}")
#2.) 
        test_es_2002_request = requests.get(f"{self.alpha_base_url}{test_es_2002[0]}/year/{test_es_2002[1]}", headers=self.user_agent_header).json() #Spain - 2002
        test_es_2002_expected = {
                "ES": [{
                        "Change": "Error correction: Regional subdivision indicator corrected in ES-PM.",
                        "Date Issued": "2002-12-10",
                        "Description of Change": "",
                        "Source": "Newsletter I-4 - https://web.archive.org/web/20081218103210/http://www.iso.org/iso/iso_3166-2_newsletter_i-4_en.pdf."
                },
                {
                        "Change": "Codes: Illes Balears: ES-PM -> ES-IB (to correct duplicate use). ES-GE Gerona -> ES-GI Girona.",
                        "Date Issued": "2002-05-21",
                        "Description of Change": "Spelling correction and update in header information. Four corrections in spellings of subdivisions.",
                        "Source": "Newsletter I-2 - https://web.archive.org/web/20120131102127/http://www.iso.org/iso/iso_3166-2_newsletter_i-2_en.pdf."
                }]
        }
        
        self.assertEqual(test_es_2002_expected, test_es_2002_request, f"Observed and expected outputs of API do not match:\n{test_es_2002_request}")
#3.) 
        test_tr_gt_2020_request = requests.get(f"{self.alpha_base_url}{test_tr_2002[0]}/year/{test_tr_2002[1]}", headers=self.user_agent_header).json() #Turkey - >2020
        test_tr_gt_2020_expected = {"TR": [
                {
                "Change": "Change of the short and full name.",
                "Date Issued": "2022-07-11",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:TR."
                },
                {
                "Change": "Correction of the Code Source.",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:TR."
                }
        ]}

        self.assertEqual(test_tr_gt_2020_request, test_tr_gt_2020_expected, f"Observed and expected outputs of API do not match:\n{test_tr_gt_2020_request}")
#4.)
        test_ma_mh_nr_lt_2011_request = requests.get(f"{self.alpha_base_url}{test_ma_mh_nr_lt_2011[0]}/year/{test_ma_mh_nr_lt_2011[1]}", headers=self.user_agent_header).json() #Morocco, Marshall Islands, Nauru - <2011
        test_ma_mh_nr_lt_2011_expected = {
              "MA": [
                {
                "Change": "Subdivisions added: MA-AOU Aousserd. MA-FAH Fahs-Anjra. MA-MED Médiouna. MA-MMD Marrakech-Medina. MA-MMN Marrakech-Menara. MA-MOH Mohammadia. MA-MOU Moulay Yacoub. MA-NOU Nouaceur. MA-RAB Rabat. MA-SAL Salé. MA-SKH Skhirate-Témara. MA-SYB Sidi Youssef Ben Ali. MA-TAI Taourirt. MA-ZAG Zagora. Subdivisions deleted: MA-MAR Marrakech. MA-RBA Rabat-Salé. Code changes: MA-BAH Aït Baha -> MA-CHT Chtouka-Ait Baha. MA-MEL Aït Melloul -> MA-INE Inezgane-Ait Melloul.",
                "Date Issued": "2010-02-03 (corrected 2010-02-19)",
                "Description of Change": "Addition of the country code prefix as the first code element, addition of names in administrative languages.",
                "Source": "Newsletter II-1 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-1_corrected_2010-02-19.pdf."
                },
                {
                "Change": "Change of spelling for Laâyoune.",
                "Date Issued": "2004-03-08",
                "Description of Change": "",
                "Source": "Newsletter I-6 - https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf."
                },
                {
                "Change": "Subdivision layout: 7 economic regions -> 16 economic regions (now called regions). Code changes: Jerada: MA-IRA -> MA-JRA.",
                "Date Issued": "2002-05-21",
                "Description of Change": "New subdivision layout at economic region level. List source updated. Addition of one reference in the code source. Two name spellings corrected. One code corrected.",
                "Source": "Newsletter I-2 - https://web.archive.org/web/20120131102127/http://www.iso.org/iso/iso_3166-2_newsletter_i-2_en.pdf."
                }
              ],
              "MH": [
                {
                "Change": "Subdivisions added: MH-JAB Jabat. Subdivisions deleted: MH-UJL Ujelang.",
                "Date Issued": "2010-02-03 (corrected 2010-02-19)",
                "Description of Change": "Addition of the country code prefix as the first code element, addition of names in administrative languages.",
                "Source": "Newsletter II-1 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-1_corrected_2010-02-19.pdf."
                }
              ],
              "NR": [
                {
                "Change": "Subdivisions added: 14 districts.",
                "Date Issued": "2007-04-17",
                "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
                "Source": "Newsletter I-8 - https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf."
                }
        ]}

        self.assertEqual(test_ma_mh_nr_lt_2011_request, test_ma_mh_nr_lt_2011_expected, f"Observed and expected outputs of API do not match:\n{test_ma_mh_nr_lt_2011_request}") 
#5.) 
        test_pe_pr_ne_2014_request = requests.get(f"{self.alpha_base_url}{test_pe_pr_ne_2014[0]}/year/{test_pe_pr_ne_2014[1]}", headers=self.user_agent_header).json() #Peru, Puerto Rico - <>2014
        test_pe_pr_ne_2014_expected = {
              "PE": [
                {
                "Change": "Correction of the Code Source.",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:PE."
                },
                {
                "Change": "Subdivision added: PE-LMA Municipalidad Metropolitana de Lima.",
                "Date Issued": "2010-06-30",
                "Description of Change": "Update of the administrative structure and languages and update of the list source.",
                "Source": "Newsletter II-2."
                }
              ],
              "PR": [
                {
                "Change": "Modification of remark part 2. (Remark part 2: No subdivisions relevant for this standard. Included also as a subdivision of the United States (US-PR)).",
                "Date Issued": "2018-11-26",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:PR."
                }     
              ]}

        self.assertEqual(test_pe_pr_ne_2014_request, test_pe_pr_ne_2014_expected, f"Observed and expected outputs of API do not match:\n{test_pe_pr_ne_2014_request}")
#6.)
        test_ve_2004_2008_request = requests.get(f"{self.alpha_base_url}{test_ve_2004_2008[0]}/year/{test_ve_2004_2008[1]}", headers=self.user_agent_header).json() #Venezuela - 2004-2008
        self.assertEqual(test_ve_2004_2008_request, {}, f"Expected output of API to be an empty dict, got:\n{test_ve_2004_2008_request}")
#7.) 
        test_abc_2000_request = requests.get(f"{self.alpha_base_url}{test_abc_2000[0]}/year/{test_abc_2000[1]}", headers=self.user_agent_header).json() #abc - 2000
        test_abc_2000_request_expected = {"message": f"Invalid ISO 3166-1 country code input, cannot convert into corresponding alpha-2 code: {test_abc_2000[0]}.", "path": f"{self.alpha_base_url}{test_abc_2000[0]}/year/{test_abc_2000[1]}", "status": 400}
        self.assertEqual(test_abc_2000_request, test_abc_2000_request_expected, f"Expected and observed output error object do not match:\n{test_abc_2000_request}")
#8.)
        test_de_12345_request = requests.get(f"{self.alpha_base_url}{test_de_12345[0]}/year/{test_de_12345[1]}", headers=self.user_agent_header).json() #DE - 12345
        test_de_12345_request_expected = {"message": f"Invalid year input, must be a valid year >= 1996, got {test_de_12345[1]}.", "path": f"{self.alpha_base_url}{test_de_12345[0]}/year/{test_de_12345[1]}", "status": 400}
        self.assertEqual(test_de_12345_request, test_de_12345_request_expected, f"Expected and observed output error object do not match:\n{test_de_12345_request}")

#     @unittest.skip("")
    def test_country_name_endpoint(self):
        """ Testing '/api/country_name' endpoint using a variety of country names. """
        test_name_benin = "Benin"
        test_name_tajikistan = "Tajikista"
        test_name_monaco = "Monaco"
        test_name_mali_nicaragua = "Mali, Nicaragua"
        test_name_error1 = "ABCDEF"
        test_name_error2 = "12345"
#1.)
        test_request_bj = requests.get(self.country_name_base_url + test_name_benin, headers=self.user_agent_header).json() #Benin
        test_name_bj_expected = {"BJ": [
                {
                "Change": "Correction of the Code Source.",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BJ."
                },
                {
                "Change": "Change of spelling of BJ-AK, BJ-KO; update List Source.",
                "Date Issued": "2015-11-27",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BJ."
                },
                {
                "Change": "Subdivisions added: BJ-AL Alibori. BJ-CO Collines. BJ-DO Donga. BJ-KO Kouffo. BJ-LI Littoral. BJ-PL Plateau.",
                "Date Issued": "2002-05-21",
                "Description of Change": "New subdivision layout: 12 departments. Six with previous names and six with new names.",
                "Source": "Newsletter I-2 - https://web.archive.org/web/20120131102127/http://www.iso.org/iso/iso_3166-2_newsletter_i-2_en.pdf."
                }
                ]
        }

        self.assertEqual(test_request_bj, test_name_bj_expected, "Expected and observed outputs do not match.")
#3.)
        test_request_tj = requests.get(self.country_name_base_url + test_name_tajikistan, headers=self.user_agent_header, params={"likeness": "80"}).json() #Tajikistan
        test_name_tj_expected = [{
                "Change": "Correction of the Code Source.",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:TJ."
                },
                {
                "Change": "Correction of the romanization system label.",
                "Date Issued": "2018-11-26",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:TJ."
                },
                {
                "Change": "Spelling change: TJ-RA Nohiyahoi Tobei Jumhurí -> nohiyahoi tobei jumhurí.",
                "Date Issued": "2017-11-23",
                "Description of Change": "Change of subdivision name of TJ-RA; change of spelling of category name in eng, tgk; update List Source; modification of the English remark part 2. (Remark part 2: Remark: The deletion of the region Karategin left one part of the country without name and without code in this part of ISO 3166. This section of the country is designated districts under republic administration (tgk: nohiyahoi tobei jumhurí) and comprises 13 districts (tgk: nohiya) which are administered directly by the central government at first-order level).",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:TJ."
                }]
        
        self.assertIsInstance(test_request_tj, dict, f"Expected output object of API to be of type dict, got {test_request_tj}.")
        self.assertEqual(len(test_request_tj["TJ"]), 7, f"Expected there to be 7 elements in output object, got {len(test_request_tj['TJ'])}.")
        self.assertEqual(test_request_tj["TJ"][0:3], test_name_tj_expected, f"Expected and observed outputs do not match:\n{test_request_tj['TJ'][0:3]}")
#4.)
        test_request_mc = requests.get(self.country_name_base_url + test_name_monaco, headers=self.user_agent_header).json() #Monaco
        test_name_mc_expected = {"MC": [
                {
                "Change": "Correction of the Code Source.",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:MC."
                },
                {
                "Change": "Administrative subdivisions addition.",
                "Date Issued": "2011-12-13 (corrected 2011-12-15)",
                "Description of Change": "",
                "Source": "Newsletter II-3 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf."
                }
                ]
        }

        self.assertEqual(test_request_mc, test_name_mc_expected, "Expected and observed outputs do not match.")
#5.)
        test_request_ml_ni = requests.get(self.country_name_base_url + test_name_mali_nicaragua, headers=self.user_agent_header, params={"sortby": "datedesc"}).json() #Mali, Nicaragua 
        test_name_ml_ni_expected = [
                {
                "Change": "Correction of the Code Source.",
                "Country Code": "NI",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:NI."
                },
                {
                "Change": "Name change: NI-AN Atlántico Norte -> Costa Caribe Norte. NI-AS Atlántico Sur -> Costa Caribe Sur.",
                "Country Code": "NI",
                "Date Issued": "2018-04-20",
                "Description of Change": "Change of subdivision name of NI-AN, NI-AS; update List Source.",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:NI."
                },
                {
                "Change": "Addition of regions ML-9, ML-10; update List Source.",
                "Country Code": "ML",
                "Date Issued": "2017-11-23",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:ML."
                },
                {
                "Change": "Subdivisions added: NI-AN Atlántico Norte. NI-AS Atlántico Sur. Subdivisions deleted: NI-ZE Zelaya.",
                "Country Code": "NI",
                "Date Issued": "2002-05-21",
                "Description of Change": "Deletion of one department. Addition of two autonomous regions. New list source.",
                "Source": "Newsletter I-2 - https://web.archive.org/web/20120131102127/http://www.iso.org/iso/iso_3166-2_newsletter_i-2_en.pdf."
                }
        ]

        self.assertEqual(test_request_ml_ni, test_name_ml_ni_expected, f"Expected and observed outputs do not match:\n{test_request_ml_ni}")
#6.)
        test_request_error_1 = requests.get(self.country_name_base_url + test_name_error1, headers=self.user_agent_header).json() #ABCDEF
        test_request_error_expected = {"message": f"No matching country name found for input: {test_name_error1.title()}.", "path": self.country_name_base_url + test_name_error1, "status": 400}
        self.assertEqual(test_request_error_1, test_request_error_expected, f"Expected and observed output error object do not match:\n{test_request_error_1}")
#7.) 
        test_request_error_2 = requests.get(self.country_name_base_url + test_name_error2, headers=self.user_agent_header).json() #12345
        test_request_error_expected = {"message": f"No matching country name found for input: {test_name_error2.title()}.", "path": self.country_name_base_url + test_name_error2, "status": 400}
        self.assertEqual(test_request_error_2, test_request_error_expected, f"Expected and observed output error object do not match:\n{test_request_error_2}")

#     @unittest.skip("")
    def test_country_name_year_endpoint(self):
        """ Testing '/api/country_name/<input_country_name}/year' endpoint using a variety of country names and years. """
        test_name_panama_2017 = ("Panama", "2017")
        test_name_seychelles_2010_2013 = ("Seychelles", "2010-2013")
        test_name_zambia_zimbabwe_gt_2015 = ("Zambia,zimbabwe", ">2015")
        test_name_year_error1 = ("Germany", "99999")
        test_name_year_error2 = ("ABCDEF", "2018")
#1.)
        test_request_name_panama_2017 = requests.get(f'{self.country_name_base_url}{test_name_panama_2017[0]}/year/{test_name_panama_2017[1]}' , headers=self.user_agent_header).json() #Panama - 2017
        test_name_year_panama_expected = {"PA": [
                {
                "Change": "Change of subdivision name of PA-KY; addition of local variation of PA-KY, update List Source.",
                "Date Issued": "2017-11-23",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:PA."
                }
                ]
        }

        self.assertEqual(test_request_name_panama_2017, test_name_year_panama_expected, "Expected and observed outputs do not match.")
#2.)
        test_request_name_seychelles_2010_2013 = requests.get(f'{self.country_name_base_url}{test_name_seychelles_2010_2013[0]}/year/{test_name_seychelles_2010_2013[1]}' , headers=self.user_agent_header).json() #Seychelles - 2010-2013
        test_name_year_seychelles_expected = {"SC": [
                {
                "Change": "Correct the local language code for the local short name.",
                "Date Issued": "2013-02-06",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:SC."
                },
                {
                "Change": "Subdivisions added: SC-24 Les Mamelles. SC-25 Roche Caiman.",
                "Date Issued": "2010-06-30",
                "Description of Change": "Update of the administrative structure and languages and update of the list source.",
                "Source": "Newsletter II-2 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf."
                },
        ]}

        self.assertEqual(test_request_name_seychelles_2010_2013, test_name_year_seychelles_expected, "Expected and observed outputs do not match.")
#3.)
        test_request_name_zambia_zimbabwe_gt_2015 = requests.get(f'{self.country_name_base_url}{test_name_zambia_zimbabwe_gt_2015[0]}/year/{test_name_zambia_zimbabwe_gt_2015[1]}' , headers=self.user_agent_header).json() #Zambia, Zimbabwe - >2015
        test_name_year_zambia_zimbabwe_expected = {"ZM": [
                {
                "Change": "Addition of an asterisk to ZM-01 to ZM-10; Correction du Code Source.",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:ZM."
                },
                {
                "Change": "Update List Source and Code Source.",
                "Date Issued": "2015-11-27",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:ZM."
                }],
                "ZW": [{
                "Change": "Update List Source.",
                "Date Issued": "2015-11-27",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:ZW."
                }]}

        self.assertEqual(test_request_name_zambia_zimbabwe_gt_2015, test_name_year_zambia_zimbabwe_expected, "Expected and observed outputs do not match.")
#4.)
        test_request_error_1 = requests.get(f'{self.country_name_base_url}{test_name_year_error1[0]}/year/{test_name_year_error1[1]}', headers=self.user_agent_header).json() #Germany - 99999
        test_request_error_expected = {"message": f"Invalid year input, must be a valid year >= 1996, got {test_name_year_error1[1]}.", "path": f'{self.country_name_base_url}{test_name_year_error1[0]}/year/{test_name_year_error1[1]}', "status": 400}
        self.assertEqual(test_request_error_1, test_request_error_expected, f"Expected and observed output error object do not match:\n{test_request_error_1}")
#5.)
        test_request_error_2 = requests.get(f'{self.country_name_base_url}{test_name_year_error2[0]}/year/{test_name_year_error2[1]}', headers=self.user_agent_header).json() #ABCDEF - 2018
        test_request_error_expected = {"message": f"No matching country name found for input: {test_name_year_error2[0].title()}.", "path": f'{self.country_name_base_url}{test_name_year_error2[0]}/year/{test_name_year_error2[1]}', "status": 400}
        self.assertEqual(test_request_error_2, test_request_error_expected, f"Expected and observed output error object do not match:\n{test_request_error_2}")

#     @unittest.skip("")
    def test_date_range_endpoint(self):
        """ Testing '/api/date_range' endpoint, which returns the updates in a specified date range. """
        test_date_range1 = "2014-04-07,2016-10-16"
        test_date_range2 = "2009-08-17,2011-11-12"
        test_date_range3 = "2022-01-01"
        test_date_range4 = "2002-12-14,2000-06-21" #dates in incorrect order but should be swapped
        test_date_range_error1 = ""
        test_date_range_error2 = "20022-123-4"
        test_date_range_error3 = "2019"
        test_date_range_error4 = "abcdef"
#1.)
        test_request_date_range1 = requests.get(self.date_range_url + test_date_range1, headers=self.user_agent_header).json() #2014-04-07,2016-10-16
        test_request_date_range1_expected = ['AD', 'AE', 'AF', 'AG', 'AL', 'AO', 'AT', 'AU', 'AZ', 'BA', 'BB', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BL', 
                                             'BN', 'BO', 'BQ', 'BT', 'BW', 'BY', 'BZ', 'CA', 'CG', 'CI', 'CL', 'CM', 'CR', 'CU', 'CY', 'CZ', 'DJ', 'DM', 
                                             'DO', 'DZ', 'EE', 'EG', 'ER', 'ES', 'ET', 'FJ', 'FM', 'GA', 'GB', 'GD', 'GH', 'GM', 'GN', 'GR', 'GT', 'GY', 
                                             'HT', 'ID', 'IE', 'IL', 'IN', 'IQ', 'IR', 'IS', 'JM', 'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KP', 
                                             'KR', 'KW', 'LA', 'LC', 'LI', 'LK', 'LR', 'LT', 'LU', 'LY', 'MA', 'MD', 'ME', 'MF', 'MG', 'MH', 'MK', 'MM', 
                                             'MR', 'MT', 'MX', 'NA', 'NE', 'NG', 'NR', 'NZ', 'OM', 'PA', 'PE', 'PG', 'PH', 'PK', 'PS', 'PT', 'RO', 'RS', 
                                             'RW', 'SA', 'SB', 'SD', 'SI', 'SM', 'SR', 'SS', 'SV', 'SX', 'SY', 'TC', 'TD', 'TJ', 'TK', 'TN', 'TT', 'TW', 
                                             'TZ', 'UA', 'UG', 'UM', 'US', 'UY', 'VA', 'VC', 'VE', 'VN', 'WF', 'WS', 'YE', 'ZM', 'ZW']

        for country_code, updates in test_request_date_range1.items():
            for update in updates:
                current_updates_date = extract_date(update["Date Issued"])
                self.assertTrue(date(2014, 4, 7) <= current_updates_date <= date(2016, 10, 16), 
                    f"Expected update of object to be between the dates 2014-04-07 and 2016-10-16, got date {current_updates_date}.")      
                
        self.assertEqual(list(test_request_date_range1), test_request_date_range1_expected, 
            f"Expected and observed country code objects do not match:\n{list(test_request_date_range1)}.")
#2.)
        test_request_date_range2 = requests.get(self.date_range_url + test_date_range2, headers=self.user_agent_header).json() #2009-08-17,2011-11-12
        test_request_date_range2_expected = ['AG', 'AL', 'AR', 'AX', 'BA', 'BF', 'BG', 'BI', 'BO', 'BQ', 'BS', 'BY', 'CF', 'CL', 'CV', 'CW', 'CZ', 'EC', 
                                             'EG', 'ES', 'FJ', 'FR', 'GB', 'GL', 'GN', 'GR', 'GW', 'HR', 'HU', 'ID', 'IE', 'IT', 'KE', 'KM', 'KN', 'KP', 
                                             'LK', 'LY', 'MA', 'MD', 'MH', 'MM', 'MW', 'NG', 'NL', 'NP', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PH', 'RS', 'RU', 
                                             'SC', 'SD', 'SH', 'SI', 'SN', 'SS', 'SX', 'TD', 'TM', 'UG', 'VE', 'YE']

        for country_code, updates in test_request_date_range2.items():
            for update in updates:
                current_updates_date = extract_date(update["Date Issued"])
                self.assertTrue(date(2009, 8, 17) <= current_updates_date <= date(2011, 11, 12), 
                    f"Expected update of object to be between the date 2009-08-17 and 2011-11-12, got date {current_updates_date}.")        

        self.assertEqual(list(test_request_date_range2), test_request_date_range2_expected, 
            f"Expected and observed country code objects do not match:\n{list(test_request_date_range2)}.")
#3.)
        test_request_date_range3 = requests.get(self.date_range_url + test_date_range3, headers=self.user_agent_header).json() #2022-01-01
        test_request_date_range3_expected = ['BO', 'CI', 'DZ', 'ET', 'FI', 'FM', 'GB', 'GF', 'GP', 'ID', 'IN', 'IQ', 'IR', 'IS', 'KP', 'KR', 
                                             'KZ', 'ME', 'MQ', 'MX', 'NL', 'NP', 'NZ', 'PA', 'PH', 'PL', 'RE', 'SI', 'TR', 'VE', 'YT']

        for country_code, updates in test_request_date_range3.items():
            for update in updates:
                current_updates_date = extract_date(update["Date Issued"])
                self.assertTrue(date(2022, 1, 1)  <= current_updates_date <= date.today(), 
                    f"Expected update of object to be between the dates 2022-01-01 and today's date, got date {current_updates_date}.")   

        self.assertEqual(list(test_request_date_range3), test_request_date_range3_expected, 
            f"Expected and observed country code objects do not match:\n{list(test_request_date_range3)}.")
#4.)
        test_request_date_range4 = requests.get(self.date_range_url + test_date_range4, headers=self.user_agent_header).json() #2002-12-14,2000-08-09
        test_request_date_range4_expected = ['AE', 'AL', 'AO', 'AZ', 'BD', 'BG', 'BI', 'BJ', 'BY', 'CA', 'CD', 'CN', 'CV', 'CZ', 'DO', 'EC', 'ER', 'ES', 
                                             'ET', 'FR', 'GB', 'GE', 'GN', 'GT', 'HR', 'ID', 'IN', 'IR', 'IT', 'KG', 'KH', 'KP', 'KR', 'KZ', 'LA', 'MA', 
                                             'MD', 'MO', 'MU', 'MW', 'NG', 'NI', 'PH', 'PL', 'PS', 'RO', 'RU', 'SI', 'TJ', 'TL', 'TM', 'TR', 'TW', 'UG', 
                                             'UZ', 'VE', 'VN', 'YE']

        for country_code, updates in test_request_date_range4.items():
            for update in updates:
                current_updates_date = extract_date(update["Date Issued"])
                self.assertTrue(date(2000, 6, 21) <= current_updates_date <= date(2002, 12, 14), 
                    f"Expected update of object to be between the date 2000-05-21 and 2002-12-14, got date {current_updates_date}.")        

        self.assertEqual(list(test_request_date_range4), test_request_date_range4_expected, 
            f"Expected and observed country code objects do not match:\n{list(test_request_date_range4)}.")
#5.)
        test_request_error1 = requests.get(self.date_range_url + test_date_range_error1, headers=self.user_agent_header).json() #""
        test_request_error1_expected = {"message": "Input date cannot be empty, expecting at least one date in the format YYYY-MM-DD.", "path": f"{self.date_range_url}{test_date_range_error1}", "status": 400}
        self.assertEqual(test_request_error1, test_request_error1_expected, f"Expected and observed output error objects does not match:\n{test_request_error1}")
#6.)
        test_request_error2 = requests.get(self.date_range_url + test_date_range_error2, headers=self.user_agent_header).json() #20022-123-4
        test_request_error2_expected = {"message": f"Invalid date format, expected YYYY-MM-DD format: {test_date_range_error2}.", "path": f"{self.date_range_url}{test_date_range_error2}", "status": 400}
        self.assertEqual(test_request_error2, test_request_error2_expected, f"Expected and observed output error objects does not match:\n{test_request_error2}")
#7.)
        test_request_error3 = requests.get(self.date_range_url + test_date_range_error3, headers=self.user_agent_header).json() #2019
        test_request_error3_expected = {"message": f"Invalid date format, expected YYYY-MM-DD format: {test_date_range_error3}.", "path": f"{self.date_range_url}{test_date_range_error3}", "status": 400}
        self.assertEqual(test_request_error3, test_request_error3_expected, f"Expected and observed output error objects does not match:\n{test_request_error3}")
#8.)
        test_request_error4 = requests.get(self.date_range_url + test_date_range_error4, headers=self.user_agent_header).json() #abcdef
        test_request_error4_expected = {"message": f"Invalid date format, expected YYYY-MM-DD format: {test_date_range_error4}.", "path": f"{self.date_range_url}{test_date_range_error4}", "status": 400}
        self.assertEqual(test_request_error4, test_request_error4_expected, f"Expected and observed output error objects do not match:\n{test_request_error4}")

#     @unittest.skip("")
    def test_date_range_alpha_endpoint(self):
        """ Testing '/api/date_range' endpoint, which returns the updates in a specified date range. """
        test_date_range_alpha1 = ("2019-04-09,2021-01-01","NO")
        test_date_range_alpha2 = ("2007-01-01,2016-05-07", "PW,QA")
        test_date_range_alpha3 = ("2014-02-02", "SO")
        test_date_range_alpha_error1 = ("abc", "AD")
        test_date_range_alpha_error2 = ("20022-123-4", "HU")
        test_date_range_alpha_error3 = ("2021-01-024", "abcdef")
#1.)
        test_date_range_alpha1_request = requests.get(f"{self.date_range_url}{test_date_range_alpha1[0]}/alpha/{test_date_range_alpha1[1]}", headers=self.user_agent_header).json() #2019-04-09,2021-01-01 - NO
        test_date_range_alpha1_expected = {
                "NO": [
                {
                "Change": "Subdivisions deleted: NO-01 Østfold. NO-02 Akershus. NO-04 Hedmark. NO-05 Oppland. NO-06 Buskerud. NO-07 Vestfold. NO-08 Telemark. NO-09 Aust-Agder. NO-10 Vest-Agder. NO-12 Hordaland. NO-14 Sogn og Fjordane. NO-19 Troms. NO-20 Finnmark. Subdivisions added: NO-30 Viken. NO-34 Innlandet. NO-38 Vestfold og Telemark. NO-42 Agder. NO-46 Vestland. NO-54 Troms og Finnmark.",
                "Date Issued": "2020-11-24",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:NO."
                },
                {
                "Change": "Change of subdivision code from NO-23 to NO-50.",
                "Date Issued": "2019-04-09",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:NO."
                }]}

        self.assertEqual(test_date_range_alpha1_request, test_date_range_alpha1_expected, f"Observed and expected outputs of API do not match:\n{test_date_range_alpha1_request}")
#2.)
        test_date_range_alpha2_request = requests.get(f"{self.date_range_url}{test_date_range_alpha2[0]}/alpha/{test_date_range_alpha2[1]}", headers=self.user_agent_header).json() #2007-01-01,2016-05-07 - PW,QA
        test_date_range_alpha2_expected = {
                "PW": [
                {
                "Change": "Subdivisions added: 16 states.",
                "Date Issued": "2007-04-17",
                "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
                "Source": "Newsletter I-8 - https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf."
                }],
                "QA": [
                {
                "Change": "Subdivisions added: QA-ZA Az̧ Za̧`āyin. Subdivisions deleted: QA-GH Al Ghuwayrīyah. QA-JU Al Jumaylīyah. QA-JB Jarīyān al Bāţnah.",
                "Date Issued": "2011-12-13 (corrected 2011-12-15)",
                "Description of Change": "Update resulting from the addition of names in administrative languages, and update of the administrative structure and of the list source.",
                "Source": "Newsletter II-3 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf."
                }
                ]}

        self.assertEqual(test_date_range_alpha2_request, test_date_range_alpha2_expected, f"Observed and expected outputs of API do not match:\n{test_date_range_alpha2_request}")
#3.)
        test_date_range_alpha3_request = requests.get(f"{self.date_range_url}{test_date_range_alpha3[0]}/alpha/{test_date_range_alpha3[1]}", headers=self.user_agent_header).json() #2014-02-02 - SO
        test_date_range_alpha3_expected = {
                "SO": [
                {
                "Change": "Add 'the' before the English full name.",
                "Date Issued": "2014-03-03",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:SO."
                }]}

        self.assertEqual(test_date_range_alpha3_request, test_date_range_alpha3_expected, f"Observed and expected outputs of API do not match:\n{test_date_range_alpha3_request}")
#4.)
        test_request_error1 = requests.get(f'{self.date_range_url}{test_date_range_alpha_error1[0]}/alpha/{test_date_range_alpha_error1[1]}', headers=self.user_agent_header).json() #"abc" - AD
        test_request_error1_expected = {"message": f"Invalid date format, expected YYYY-MM-DD format: {test_date_range_alpha_error1[0]}.", "path": f'{self.date_range_url}{test_date_range_alpha_error1[0]}/alpha/{test_date_range_alpha_error1[1]}', "status": 400}
        self.assertEqual(test_request_error1, test_request_error1_expected, f"Expected and observed output error objects does not match:\n{test_request_error1}")
#5.)
        test_request_error2 = requests.get(f'{self.date_range_url}{test_date_range_alpha_error2[0]}/alpha/{test_date_range_alpha_error2[1]}', headers=self.user_agent_header).json() #20022-123-4 - HU
        test_request_error2_expected = {"message": f"Invalid date format, expected YYYY-MM-DD format: {test_date_range_alpha_error2[0]}.", "path": f'{self.date_range_url}{test_date_range_alpha_error2[0]}/alpha/{test_date_range_alpha_error2[1]}', "status": 400}   
        self.assertEqual(test_request_error2, test_request_error2_expected, f"Expected and observed output error objects does not match:\n{test_request_error2}")
#6.)
        test_request_error3 = requests.get(f'{self.date_range_url}{test_date_range_alpha_error3[0]}/alpha/{test_date_range_alpha_error3[1]}', headers=self.user_agent_header).json() #2021-01-024 - abcdef
        test_request_error3_expected = {"message": f"Invalid ISO 3166-1 alpha-2 code input: {test_date_range_alpha_error3[1]}.", "path": f'{self.date_range_url}{test_date_range_alpha_error3[0]}/alpha/{test_date_range_alpha_error3[1]}', "status": 400}
        self.assertEqual(test_request_error3, test_request_error3_expected, f"Expected and observed output error objects does not match:\n{test_request_error3}")

#     @unittest.skip("")
    def test_search_endpoint(self):
        """ Testing '/api/search' endpoint, which returns the updates found with sought search terms. """
        test_search1 = "parishes"
        test_search2 = "cantons"
        test_search3 = "remark part 2"
        test_search4 = "2017-11-23"
        test_search5 = "abcdefg"
        test_search6 = "123"
        test_search7 = ""
#1.)    
        test_request_search1 = requests.get(self.search_url + test_search1, headers=self.user_agent_header).json() #parishes
        test_search1_expected = [{
                "Country Code": "AD",
                "Match Score": 100,
                "Change": "Subdivisions added: 7 parishes.",
                "Date Issued": "2007-04-17",
                "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
                "Source": "Newsletter I-8 - https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf."
                },
                {
                "Country Code": "AG",
                "Match Score": 100,
                "Change": "Subdivisions added: 6 parishes, 1 dependency.",
                "Date Issued": "2007-04-17",
                "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
                "Source": "Newsletter I-8 - https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf."
                },
                {
                "Country Code": "BB",
                "Match Score": 100,
                "Change": "Subdivisions added: 11 parishes.",
                "Date Issued": "2007-04-17",
                "Description of Change": "Addition of the administrative subdivisions and of their code elements.",
                "Source": "Newsletter I-8 - https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf."
                }]
        
        self.assertEqual(test_request_search1[0:3], test_search1_expected, f"Expected and observed output objects do not match:\n{test_request_search1[0:3]}")
#2.)
        test_request_search2 = requests.get(self.search_url + test_search2, headers=self.user_agent_header, params={"likeness": 90, "excludeMatchScore": 1}).json() #cantons - exclude match attribute, likeness=0.9
        test_search2_expected = {'BA': {'Change': 'Subdivisions added: 10 cantons.', 'Date Issued': '2007-12-13', 
                'Description of Change': "Second edition of ISO 3166-2 (this change was not announced in a newsletter) - 'Statoid Newsletter January 2008' - http://www.statoids.com/n0801.html.", 'Source': 'ISO 3166-2:2007 - http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=39718.'}, 
                'CH': {'Change': 'Deletion of canton CH-GR in fra; Update List Source.', 'Date Issued': '2020-11-24', 'Description of Change': '', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CH.'}, 
                'LU': {'Change': 'Addition of cantons LU-CA, LU-CL, LU-DI, LU-EC, LU-ES, LU-GR, LU-LU, LU-ME, LU-RD, LU-RM, LU-VD, LU-WI; update List Source.', 'Date Issued': '2015-11-27', 'Description of Change': '', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:LU.'}}
        
        self.assertEqual(test_request_search2, test_search2_expected, f"Expected and observed output objects do not match:\n{test_request_search2}")
#3.)
        test_request_search3 = requests.get(self.search_url + test_search3, headers=self.user_agent_header).json() #remark part 2
        test_search3_expected = [{
                "Country Code": "AI",
                "Match Score": 100,
                "Change": "Modification of remark part 2. (Remark part 2: No subdivisions relevant for this standard).",
                "Date Issued": "2018-11-26",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AI."
                },
                {  
                "Country Code": "AQ",
                "Match Score": 100,
                "Change": "Modification of remark part 2. (Remark part 2: No subdivisions relevant for this standard).",
                "Date Issued": "2018-11-26",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AQ."
                },
                {
                "Country Code": "AS",
                "Match Score": 100,
                "Change": "Modification of remark part 2. (Remark part 2: No subdivisions relevant for this standard. Included also as a subdivision of the United States (US-AS)).",
                "Date Issued": "2018-11-26",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AS."
                }]
        
        self.assertEqual(test_request_search3[0:3], test_search3_expected, f"Expected and observed output objects do not match:\n{test_request_search3[0:3]}")
#4.)
        test_request_search4 = requests.get(self.search_url + test_search4, headers=self.user_agent_header).json() #2017-11-23
        test_search4_expected = [{
                "Country Code": "CN",
                "Match Score": 100,
                "Change": "Change of subdivision code: CN-11 -> CN-BJ. CN-12 -> CN-TJ. CN-13 -> CN-HE. CN-14 -> CN-SX. CN-15 -> CN-NM. CN-21 -> CN-LN. CN-22 -> CN-JL. CN-23 -> CN-HL. CN-31 -> CN-SH. CN-32 -> CN-JS. CN-33 -> CN-ZJ. CN-34 -> CN-AH. CN-35 -> CN-FJ. CN-36 -> CN-JX. CN-37 -> CN-SD. CN-41 -> CN-HA. CN-42 -> CN-HB. CN-43 -> CN-HN. CN-44 -> CN-GD. CN-45 -> CN-GX. CN-46 -> CN-HI. CN-50 -> CN-CQ. CN-51 -> CN-SC. CN-52 -> CN-GZ. CN-53 -> CN-YN. CN-54 -> CN-XZ. CN-61 -> CN-SN. CN-62 -> CN-GS. CN-63 -> CN-QH. CN-64 -> CN-NX. CN-65 -> CN-XJ. CN-71 -> CN-TW. CN-91 -> CN-HK. CN-92 -> CN-MO.",
                "Date Issued": "2017-11-23",
                "Description of Change": "Change of subdivision code from CN-15 to CN-NM, CN-45 to CN-GX, CN-54 to CN-XZ, CN-64 to CN-NX, CN-65 to CN-XJ, CN-11 to CN-BJ, CN-12 to CN-TJ, CN-31 to CN-SH, CN-50 to CN-CQ, CN-13 to CN-HE, CN-14 to CN-SX, CN-21 to CN-LN, CN-22 to CN-JL, CN-23 to CN-HL, CN-32 to CN-JS, CN-33 to CN-ZJ, CN-34 to CN-AH, CN-35 to CN-FJ, CN-36 to CN-JX, CN-37 to CN-SD, CN-41 to CN-HA, CN-42 to CN-HB, CN-43 to CN-HN, CN-44 to CN-GD, CN-46 to CN-HI, CN-51 to CN-SC, CN-52 to CN-GZ, CN-53 to CN-YN, CN-61 to CN-SN, CN-62 to CN-GS, CN-63 to CN-QH, CN-71 to CN-TW, CN-91 to CN-HK, CN-92 to CN-MO; change of subdivision name of CN-NM, CN-GX, CN-XZ, CN-NX, CN-XJ, CN-BJ, CN-TJ, CN-SH, CN-CQ, CN-HE, CN-SX, CN-LN, CN-JL, CN-HL, CN-JS, CN-ZJ, CN-AH, CN-FJ, CN-JX, CN-SD, CN-HA, CN-HB, CN-HN, CN-GD, CN-HI, CN-SC, CN-GZ, CN-YN, CN-SN, CN-GS, CN-QH, CN-TW, CN-HK, CN-MO; addition of remark in parentheses to subdivision name for CN-HK, CN-MO in eng; addition of region CN-MO in por; update Code Source; update List Source.",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CN."
                },
                {  
                "Country Code": "CY",
                "Match Score": 100,
                "Change": "Update List Source; change of spelling of CY-02, CY-04 (tur).",
                "Date Issued": "2017-11-23",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CY."
                },
                {
                "Country Code": "DE",
                "Match Score": 100,
                "Change": "Change of spelling of category name in eng.",
                "Date Issued": "2017-11-23",
                "Description of Change": "",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:DE."
                }]     
        
        self.assertEqual(test_request_search4[0:3], test_search4_expected, f"Expected and observed output objects do not match:\n{test_request_search4[0:3]}")
#5.)
        test_request_search5 = requests.get(self.search_url + test_search5, headers=self.user_agent_header).json() #abcdefg
        test_search5_expected = {"Message": f"No matching updates found with the given search term(s): {test_search5}. Try using the query string parameter '?likeness' and reduce the likeness score to expand the search space, '?likeness=30' will return subdivision data that have a 30% match to the input name. The current likeness score is set to 100."}
        self.assertEqual(test_request_search5, test_search5_expected, f"Expected and observed output objects do not match:\n{test_request_search5}")
#6.)
        test_request_search6 = requests.get(self.search_url + test_search6, headers=self.user_agent_header).json() #123
        test_search6_expected = {"Message": f"No matching updates found with the given search term(s): {test_search6}. Try using the query string parameter '?likeness' and reduce the likeness score to expand the search space, '?likeness=30' will return subdivision data that have a 30% match to the input name. The current likeness score is set to 100."}
        self.assertEqual(test_request_search6, test_search6_expected, f"Expected and observed output objects do not match:\n{test_request_search6}")
#7.)
        test_request_search7 = requests.get(self.search_url + test_search7, headers=self.user_agent_header).json() #""
        test_request_search7_expected = {"message": "The search input parameter cannot be empty.", "path": "https://iso3166-updates.vercel.app/api/search/", "status": 400}
        self.assertEqual(test_request_search7, test_request_search7_expected, f"Expected and observed output error objects do not match:\n{test_request_search7}")
#8.)
        test_request_search8 = requests.get(self.search_url + test_search1, headers=self.user_agent_header, params={"likeness": "200"}).json()  #likeness=200

        test_request_search8_expected = {"message": "Likeness query string parameter value must be between 0 and 100.", "path": "https://iso3166-updates.vercel.app/api/search/parishes?likeness=200", "status": 400}
        self.assertEqual(test_request_search8, test_request_search8_expected, f"Expected and observed output error objects do not match:\n{test_request_search8}")
#9.)
        test_request_search9 = requests.get(self.search_url + test_search1, headers=self.user_agent_header, params={"likeness": "-100"}).json() #likeness=-100
        test_request_search9_expected = {"message": "Likeness query string parameter value must be between 0 and 100.", "path": "https://iso3166-updates.vercel.app/api/search/parishes?likeness=-100", "status": 400}
        self.assertEqual(test_request_search9, test_request_search9_expected, f"Expected and observed output error objects do not match:\n{test_request_search9}")

def extract_date(date_str: str) -> datetime.date:
    """
    Extract the original and corrected date from the Date Issued column.

    Parameters
    ==========
    :date_str: str
        input publication date.

    Returns
    =======
    :parsed_date: datetime.date
        converted date string.
    """
    clean_str = re.sub(r"\(.*?\)", "", date_str).replace(' ', '').replace('.', '').replace('\n', '')
    return datetime.strptime(clean_str, "%Y-%m-%d").date()

if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)