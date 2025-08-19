from iso3166_updates import *
import iso3166
from datetime import datetime
from importlib.metadata import metadata
from jsonschema import validate
import jsonschema
import shutil
from datetime import date
import unittest
from unittest.mock import patch
import io
unittest.TestLoader.sortTestMethodsUsing = None

# @unittest.skip("Skipping main iso3166-updates package tests.")
class ISO3166_Updates_Tests(unittest.TestCase):
    """
    Test suite for testing the iso3166-updates Python software package. 

    Test Cases
    ==========
    test_iso3166_updates_metadata:
        testing correct software metadata for the iso3166-updates package. 
    test_updates_json_schema:
        testing correct schema for iso3166-updates JSON. 
    test_updates_all:
        testing correct functionality for 'all' attribute in Updates class.
    test_updates_individual_totals:
        testing individual country updates total. 
    test_updates_duplicates:
        testing there are no duplicate updates object. 
    test_updates_alpha:
        testing correct functionality for __getitem__ function in Updates class.
    test_updates_year:
        testing correct functionality for year() function in Updates class.
    test_search:
        testing correct functionality for search() function in Updates class
    test_date_range:
        testing correct functionality for date_range() function in Updates class.
    test_custom_updates:
        testing correct functionality for custom_updates() function in Updates class.
    test_check_for_updates:
        testing correct functionality for check_for_updates() function in Updates class.
    test_validate_updates_dates:
        testing correct format and validity for dates in updates object.
    test_updates_str:
        testing correct functionality for __str__ in-built function in class.
    test_updates_repr:
        testing correct functionality for __repr__ in-built function in class.
    test_updates_sizeof:
        testing correct functionality for __sizeof__ in-built function in class.
    test_updates_len:
        testing correct functionality for __len__ in-built function in class.
    test_updates_contains:
        testing correct functionality for __contains__ in-built function in class.
    """
    def setUp(self):
        """ Initialise test variables. """                
        #instance of Updates() class
        self.all_updates = Updates(custom_updates_filepath=os.path.join("tests", "test-iso3166-updates.json"))

        #create temp test dir for storing any test class outputs
        self.test_export_folder = os.path.join("tests", "temp_test_dir")
        if not(os.path.isdir(self.test_export_folder)):
            os.makedirs(self.test_export_folder)

        #custom filepath for custom_update function tests
        self.custom_updates_filepath = os.path.join(self.test_export_folder, "custom_updates_test_iso3166_updates.json")

    # @unittest.skip("Skipping metadata unit tests.")    
    def test_iso3166_updates_metadata(self): 
        """ Testing correct iso3166-updates software version and metadata. """
        # self.assertEqual(metadata('iso3166-updates')['version'], "1.8.5", 
        #     f"iso3166-updates version is not correct, expected 1.8.5, got {metadata('iso3166-updates')['version']}.")
        self.assertEqual(metadata('iso3166-updates')['name'], "iso3166-updates", 
            f"iso3166-updates software name is not correct, expected iso3166-updates, got {metadata('iso3166-updates')['name']}.")
        # self.assertEqual(metadata('iso3166-updates')['author'], "AJ McKenna", 
        #     f"iso3166-updates author is not correct, expected AJ McKenna, got {metadata('iso3166-updates')['author']}.")
        self.assertEqual(metadata('iso3166-updates')['author-email'], "amckenna41@qub.ac.uk", 
            f"iso3166-updates author email is not correct, expected amckenna41@qub.ac.uk, got {metadata('iso3166-updates')['author-email']}.")
        self.assertEqual(metadata('iso3166-updates')['summary'], "Get the latest updates & changes to all ISO 3166 listed countries, dependent territories, and special areas of geographical interest.", 
            f"iso3166-updates package summary is not correct, got: {metadata('iso3166-updates')['summary']}.")
        self.assertEqual(metadata('iso3166-updates')['keywords'], 
            "iso,iso3166,beautifulsoup,python,pypi,countries,country codes,csv,iso3166-2,subdivisions,iso3166-1,alpha-2,alpha-3,selenium,chromedriver", 
            f"iso3166-updates keywords are not correct, got:\n{metadata('iso3166-updates')['keywords']}.")
        # self.assertEqual(metadata('iso3166-updates')['home-page'], "https://iso3166-updates.vercel.app/api", 
        #     f"iso3166-updates home page url is not correct, expected https://iso3166-updates.vercel.app/api, got {metadata('iso3166-updates')['home-page']}.")
        self.assertEqual(metadata('iso3166-updates')['maintainer'], "AJ McKenna", 
            f"iso3166-updates maintainer is not correct, expected AJ McKenna, got {metadata('iso3166-updates')['maintainer']}.")
        self.assertEqual(metadata('iso3166-updates')['license'], "MIT", 
            f"iso3166-updates license type is not correct, expected MIT, got {metadata('iso3166-updates')['license']}.")
    
    # @unittest.skip("")
    def test_updates_json_schema(self):
        """ Testing the schema for the iso3166-updates JSON. """
        with open(os.path.join("tests", "test-iso3166-updates.json"), encoding="utf-8") as iso3166_updates_json:
            iso3166_updates_all = json.loads(iso3166_updates_json.read())
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
            "additionalProperties": False
        }
        try:
            validate(instance=iso3166_updates_all, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"JSON schema validation failed: {e}")

    # @unittest.skip("")
    def test_updates_all(self):
        """ Testing 'all' attribute that should return all ISO 3166 updates data. """
#1.)
        test_all_updates = self.all_updates.all 

        self.assertIsInstance(test_all_updates, dict, 
            f"Expected output object to be of type dict, got {type(test_all_updates)}.")
        self.assertEqual(len(test_all_updates), 250, 
            f"Expected there to be 250 country keys in output object, got {len(test_all_updates)}.")
        for iso_code in list(test_all_updates.keys()):
            self.assertIn(iso_code, list(iso3166.countries_by_alpha2.keys()),
                    f"Alpha-2 code {iso_code} not found in list of available codes.")
#2.)
        iso3166_updates_empty = ["MZ", "PY", "SK", "VU", "XK"]  #testing only these country updates objects have empty arrays
        for iso_code in test_all_updates:
             if (test_all_updates[iso_code] == []):
                  self.assertTrue(iso_code in iso3166_updates_empty, 
                        f"Expected country code's updates object {iso_code} to be empty:\n{test_all_updates[iso_code]}.")
    
    # @unittest.skip("")
    def test_updates_duplicates(self):
        """ Testing there are no duplicate country updates objects. """
#1.)
        for country_code, updates in self.all_updates.all.items():
            unique_updates = {frozenset(update.items()) for update in updates}
            self.assertEqual(len(unique_updates), len(updates), f"Duplicates found in updates for country {country_code}:\n{updates}")

    # @unittest.skip("")
    def test_updates_individual_totals(self):
        """ Testing the individual total number of updates per country. """
        #expected updates counts per country
        expected_counts = {'AD': 3, 'AE': 3, 'AF': 6, 'AG': 3, 'AI': 1, 'AL': 6, 'AM': 1, 'AO': 6, 'AQ': 1, 
                                'AR': 1, 'AS': 1, 'AT': 2, 'AU': 3, 'AW': 3, 'AX': 3, 'AZ': 3, 'BA': 6, 'BB': 3, 
                                'BD': 6, 'BE': 2, 'BF': 3, 'BG': 9, 'BH': 2, 'BI': 4, 'BJ': 3, 'BL': 5, 'BM': 1, 
                                'BN': 4, 'BO': 5, 'BQ': 7, 'BR': 2, 'BS': 4, 'BT': 5, 'BV': 3, 'BW': 3, 'BY': 5, 
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
            actual_count = len(self.all_updates.all.get(code, []))
            self.assertEqual(actual_count, expected_count, 
                f"Incorrect updates total for country code {code}. Expected {expected_count}, got {actual_count}.")

    # @unittest.skip("")
    def test_updates_alpha(self):
        """ Testing __getitem__ function that allows the updates class to be subscriptable, using a variety of alpha-2 country codes. """
        test_alpha_bt = "BT" #Bhutan
        test_alpha_dj = "DJ" #Djibouti
        test_alpha_hn = "HND" #Honduras
        test_alpha_yt = "175" #Mayotte
        test_alpha_fj_gh_gn = "FJ, GHA, 324" #Fiji, Ghana and Guinea
        test_alpha_error_1 = "XX" #should raise value error
        test_alpha_error_2 = "abcdefg" #should raise value error
        test_alpha_error_3 = "aa" #should raise value error
        test_alpha_error_4 = False #should raise type error
        test_alpha_error_5 = 1234 #should raise type error
        test_alpha_error_6 = 1.06 #should raise type error
#1.) 
        test_alpha_bt_updates = self.all_updates[test_alpha_bt] #Bhutan
        test_alpha_bt_updates_expected = {"BT": [{"Change": "Change of spelling of BT-43; Update List Source.", "Description of Change": "", "Date Issued": "2020-11-24", 
            "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BT."}, 
            {"Change": "Correction of the romanization system label.", "Description of Change": "", "Date Issued": "2018-11-26", 
             "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BT."},
            {"Change": "Change of spelling of BT-13, BT-45; update list source.", "Description of Change": "", "Date Issued": "2016-11-15",
             "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BT."},
            {"Change": "Update List Source.", "Description of Change": "", "Date Issued": "2015-11-27",
             "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BT."},
            {"Change": "Update List Source.", "Description of Change": "", "Date Issued": "2014-11-03",
             "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BT."}]}
        
        self.assertEqual(test_alpha_bt_updates, test_alpha_bt_updates_expected, 
            f"Expected and observed output objects for get function do not match:\n{test_alpha_bt_updates}")
#2.) 
        test_alpha_dj_updates = self.all_updates[test_alpha_dj] #Djibouti
        test_alpha_dj_updates_expected = {"DJ": [{"Change": "Correction of the Code Source.", "Description of Change": "", "Date Issued": "2020-11-24", 
            "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:DJ."},
            {"Change": "Change of spelling of DJ-OB in ara.", "Description of Change": "", "Date Issued": "2016-11-15", 
            "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:DJ."},
            {"Change": "Add romanization system for Arabic; typographical correction of DJ-AS; update List Source.", "Description of Change": "", "Date Issued": "2015-11-27",
            "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:DJ."},
            {"Change": "Update List Source.", "Description of Change": "", "Date Issued": "2014-11-03",
            "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:DJ."},
            {"Change": "Language adjustment and source list update.", "Description of Change": "", "Date Issued": "2011-12-13 (corrected 2011-12-15)",
            "Source": "Newsletter II-3 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf."},
            {"Change": "Subdivisions added: DJ-AR Arta.", "Description of Change": "Change of generic term for administrative divisions. Addition of new region 'Arta'. New list source and code source.",
            "Date Issued": "2005-09-13", "Source": "Newsletter I-7 - https://web.archive.org/web/20081218103217/http://www.iso.org/iso/iso_3166-2_newsletter_i-7_en.pdf."}]}     

        self.assertEqual(test_alpha_dj_updates, test_alpha_dj_updates_expected, 
            f"Expected and observed output objects for get function do not match:\n{test_alpha_dj_updates}")
#3.) 
        test_alpha_hn_updates = self.all_updates[test_alpha_hn] #Honduras
        test_alpha_hn_updates_expected = {"HN": [{"Change": "Comment taken into account and source list update.", "Description of Change": "",
            "Date Issued": "2011-12-13 (corrected 2011-12-15)", "Source": "Newsletter II-3 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf."}]}
        
        self.assertEqual(test_alpha_hn_updates, test_alpha_hn_updates_expected, 
            f"Expected and observed output objects for get function do not match:\n{test_alpha_hn_updates}")
#4.) 
        test_alpha_yt_updates = self.all_updates[test_alpha_yt] #Mayotte
        test_alpha_yt_updates_expected = {"YT": [{"Change": "Modification of remark part 2. (Remark part 2: No subdivisions relevant for this standard. Included also as a subdivision of France (FR-976)).",
            "Description of Change": "", "Date Issued": "2022-11-29", "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:YT."}, 
            {"Change": "Modification of remark part 2. (Remark part 2: No subdivisions relevant for this standard. Included also as a subdivision of France (FR-976)).", 
             "Description of Change": "", "Date Issued": "2018-11-26", "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:YT."}]}

        self.assertEqual(test_alpha_yt_updates, test_alpha_yt_updates_expected, 
            f"Expected and observed output objects for get function do not match:\n{test_alpha_yt_updates}")
#5.)
        test_alpha_fj_gh_gn_updates = self.all_updates[test_alpha_fj_gh_gn] #Fiji, Ghana, Guinea
        test_alpha_fj_gh_gn_updates_expected_1 = {
            "Change": "Reinstatement of provinces deleted due to a technical glitch.",
            "Description of Change": "",
            "Date Issued": "2016-11-22",
            "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:FJ."
            }
        test_alpha_fj_gh_gn_updates_expected_2 = {
            "Change": "Correction of the Code Source.",
            "Description of Change": "",
            "Date Issued": "2020-11-24",
            "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:GH."
            }
        test_alpha_fj_gh_gn_updates_expected_3 = {
            "Change": "Correction of the Code Source.",
            "Description of Change": "",
            "Date Issued": "2020-11-24",
            "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:GN."
            }
        
        self.assertEqual(len(test_alpha_fj_gh_gn_updates), 3, 
            f"Expected there to be 3 updates in output object, got {len(test_alpha_fj_gh_gn_updates)}.")
        self.assertEqual(list(test_alpha_fj_gh_gn_updates), ["FJ", "GH", "GN"])
        for code in test_alpha_fj_gh_gn_updates:
            for row in test_alpha_fj_gh_gn_updates[code]:
                self.assertEqual(list(row.keys()), ["Change", "Description of Change", "Date Issued", "Source"], f"Columns from output do not match expected\n{list(row.keys())}.")
                self.assertIsInstance(row, dict, f"Output object should be of type dict, got {type(row)}.")
        self.assertEqual(test_alpha_fj_gh_gn_updates["FJ"][0], test_alpha_fj_gh_gn_updates_expected_1, "Expected and observed outputs do not match.")
        self.assertEqual(test_alpha_fj_gh_gn_updates["GH"][0], test_alpha_fj_gh_gn_updates_expected_2, "Expected and observed outputs do not match.")
        self.assertEqual(test_alpha_fj_gh_gn_updates["GN"][0], test_alpha_fj_gh_gn_updates_expected_3, "Expected and observed outputs do not match.")
#6.)     
        with self.assertRaises(ValueError):
            self.all_updates[test_alpha_error_1] 
            self.all_updates[test_alpha_error_2] 
            self.all_updates[test_alpha_error_3] 
#7.)
        with self.assertRaises(TypeError):
            self.all_updates[test_alpha_error_4] 
            self.all_updates[test_alpha_error_5]
            self.all_updates[test_alpha_error_6]

    # @unittest.skip("")
    def test_updates_year(self):
        """ Testing year function that returns all ISO 3166 updates for input year/years, year range or greater than/less than input year. """
        test_year_2019 = "2019"
        test_year_2003 = "2003"
        test_year_2000_2001_2002 = "2000,2001,2002"
        test_year_gt_2021 = ">2021"
        test_year_2004_2008 = "2004-2008"
        test_year_1999_2002 = "2002-1999"
        test_year_not_equal_2019 = "<>2019"
        test_year_not_equal_2005_2009 = "<>2005,2009"
        test_year_error1 = "1234" #ValueError
        test_year_error2 = "abcdef" #ValueError
        test_year_error3 = ">2009<>" #ValueError
        test_year_error4 = 8.99 #TypeError
        test_year_error5 = 12345 #TypeError
        test_year_error6 = True #TypeError
#1.)
        test_year_2019_updates = self.all_updates.year(test_year_2019)
        test_year_2019_expected_keys = ["BN", "BQ", "CN", "ET", "GB", "GH", "GR", "IN", "IT", "LA", "LK", "MA", "MD", "ME", "MH", "MK", 
                                        "MR", "NO", "NP", "PK", "SB", "SL", "SY", "TZ"]

        self.assertEqual(len(test_year_2019_updates), 24, 
            f"Expected 24 updates in output object, got {len(test_year_2019_updates)}.")
        self.assertEqual(list(test_year_2019_updates), test_year_2019_expected_keys, 
            f"Expected and observed list of country codes do not match:\n{list(test_year_2019_updates)}.")
        for update in test_year_2019_updates:
            for row in range(0, len(test_year_2019_updates[update])):
                self.assertEqual(datetime.strptime(test_year_2019_updates[update][row]["Date Issued"], '%Y-%m-%d').year, 2019, 
                    f"Expected year of updates output to be 2019, got {test_year_2019_updates[update][row]['Date Issued']}.")
#2.)
        test_year_2003_updates = self.all_updates.year(test_year_2003)
        test_year_2003_expected_keys = ["BW", "CH", "CZ", "LY", "MY", "SN", "TN", "TZ", "UG", "VE"]

        self.assertEqual(len(test_year_2003_updates), 10, 
            f"Expected 10 updates in output object, got {len(test_year_2003_updates)}.")
        self.assertEqual(list(test_year_2003_updates), test_year_2003_expected_keys, 
            f"Expected and observed list of country codes do not match:\n{list(test_year_2003_updates)}.")
        for update in test_year_2003_updates:
            for row in range(0, len(test_year_2003_updates[update])):
                self.assertEqual(datetime.strptime(test_year_2003_updates[update][row]['Date Issued'], '%Y-%m-%d').year, 2003, 
                    f"Expected year of updates output to be 2003, got {test_year_2003_updates[update][row]['Date Issued']}.")  
#3.) 
        test_year_2000_2001_2002_updates = self.all_updates.year(test_year_2000_2001_2002)
        test_year_2000_2001_2002_expected_keys = ['AE', 'AL', 'AO', 'AZ', 'BD', 'BG', 'BI', 'BJ', 'BY', 'CA', 'CD', 'CN', 'CV', 'CZ', 
                                                  'DO', 'EC', 'ER', 'ES', 'ET', 'FR', 'GB', 'GE', 'GN', 'GT', 'HR', 'ID', 'IN', 'IR', 
                                                  'IT', 'KG', 'KH', 'KP', 'KR', 'KZ', 'LA', 'MA', 'MD', 'MO', 'MU', 'MW', 'NG', 'NI', 
                                                  'PH', 'PL', 'PS', 'RO', 'RU', 'SI', 'TJ', 'TL', 'TM', 'TR', 'TW', 'UG', 'UZ', 'VE', 
                                                  'VN', 'YE']
        
        self.assertEqual(len(test_year_2000_2001_2002_updates), 58, 
            f"Expected 58 updates in output object, got {len(test_year_2000_2001_2002_updates)}.")
        self.assertEqual(list(test_year_2000_2001_2002_updates), test_year_2000_2001_2002_expected_keys, 
            f"Expected and observed list of country codes do not match:\n{list(test_year_2000_2001_2002_updates)}.")
        for update in test_year_2000_2001_2002_updates:
            for row in range(0, len(test_year_2000_2001_2002_updates[update])):
                self.assertIn(datetime.strptime(test_year_2000_2001_2002_updates[update][row]["Date Issued"], '%Y-%m-%d').year, [2000,2001,2002], 
                    f"Expected year of updates output to be either 2000, 2001 or 2002, got {test_year_2000_2001_2002_updates[update][row]['Date Issued']}.")    
#4.)
        test_year_gt_2021_updates = self.all_updates.year(test_year_gt_2021)
        test_year_gt_2021_expected_keys = ['BO', 'BS', 'CI', 'CN', 'DZ', 'ET', 'FI', 'FM', 'FR', 'GB', 'GF', 'GP', 'GT', 'HU', 'ID', 'IN', 'IQ', 'IR', 'IS', 'KH', 
                                           'KP', 'KR', 'KZ', 'LT', 'LV', 'ME', 'MQ', 'MX', 'NL', 'NP', 'NZ', 'PA', 'PH', 'PL', 'RE', 'RU', 'SI', 'SS', 'TR', 'VE', 'YT']

        self.assertEqual(len(test_year_gt_2021_updates), 41, 
            f"Expected 41 updates in output object, got {len(test_year_gt_2021_updates)}.")
        self.assertEqual(list(test_year_gt_2021_updates), test_year_gt_2021_expected_keys, 
            f"Expected and observed list of country codes do not match:\n{list(test_year_gt_2021_updates)}.")
        for update in test_year_gt_2021_updates:
            for row in range(0, len(test_year_gt_2021_updates[update])):
                self.assertTrue(datetime.strptime(test_year_gt_2021_updates[update][row]['Date Issued'], '%Y-%m-%d').year >= 2021, 
                    f"Expected year of updates output to be greater than or equal to 2021, got {test_year_gt_2021_updates[update][row]['Date Issued']}.")
#5.)
        test_year_2004_2008_updates = self.all_updates.year(test_year_2004_2008)
        test_year_2004_2008_updates_expected_keys = ['AD', 'AF', 'AG', 'AL', 'AU', 'BA', 'BB', 'BG', 'BH', 'BL', 'CI', 'CN', 'CO', 'CZ', 'DJ', 'DM', 'DO', 'EG', 
                                                     'FR', 'GB', 'GD', 'GE', 'GG', 'GL', 'GN', 'GP', 'HT', 'ID', 'IM', 'IR', 'IT', 'JE', 'KE', 'KN', 'KP', 'KW', 
                                                     'LB', 'LC', 'LI', 'LR', 'MA', 'MD', 'ME', 'MF', 'MG', 'MK', 'MT', 'NG', 'NP', 'NR', 'PF', 'PS', 'PW', 'RE', 
                                                     'RS', 'RU', 'RW', 'SB', 'SC', 'SD', 'SG', 'SI', 'SM', 'TD', 'TF', 'TN', 'TO', 'TV', 'UG', 'VC', 'VN', 'YE', 
                                                     'ZA']

        self.assertEqual(len(test_year_2004_2008_updates), 73, 
            f"Expected 73 updates in output object, got {len(test_year_2004_2008_updates)}.") 
        self.assertEqual(list(test_year_2004_2008_updates), test_year_2004_2008_updates_expected_keys, 
            f"Expected and observed list of country codes do not match:\n{list(test_year_2004_2008_updates)}.")
        for update in test_year_2004_2008_updates:
            for row in range(0, len(test_year_2004_2008_updates[update])):
                self.assertTrue((datetime.strptime(test_year_2004_2008_updates[update][row]["Date Issued"], '%Y-%m-%d').year >= 2004) and \
                                (datetime.strptime(test_year_2004_2008_updates[update][row]["Date Issued"], '%Y-%m-%d').year <= 2008), 
                            f"Expected year of updates output to be between 2004 and 2008, got {test_year_2004_2008_updates[update][row]['Date Issued']}.")
#6.)
        test_year_1999_2002_updates = self.all_updates.year(test_year_1999_2002)
        test_year_1999_2002_updates_expected_keys = ['AE', 'AL', 'AO', 'AZ', 'BD', 'BG', 'BI', 'BJ', 'BY', 'CA', 'CD', 'CN', 'CV', 'CZ', 'DO', 'EC', 'ER', 'ES', 'ET', 
                                                     'FR', 'GB', 'GE', 'GN', 'GT', 'HR', 'ID', 'IN', 'IR', 'IT', 'KG', 'KH', 'KP', 'KR', 'KZ', 'LA', 'MA', 'MD', 'MO', 
                                                     'MU', 'MW', 'NG', 'NI', 'PH', 'PL', 'PS', 'RO', 'RU', 'SI', 'TJ', 'TL', 'TM', 'TR', 'TW', 'UG', 'UZ', 'VE', 'VN', 
                                                     'YE']

        self.assertEqual(len(test_year_1999_2002_updates), 58, 
            f"Expected 58 updates in output object, got {len(test_year_1999_2002_updates)}.")
        self.assertEqual(list(test_year_1999_2002_updates), test_year_1999_2002_updates_expected_keys, 
            f"Expected and observed list of country codes do not match:\n{list(test_year_1999_2002_updates)}.")
        for update in test_year_1999_2002_updates:
            for row in range(0, len(test_year_1999_2002_updates[update])):
                self.assertTrue((datetime.strptime(test_year_1999_2002_updates[update][row]["Date Issued"], '%Y-%m-%d').year >= 1999) and \
                                (datetime.strptime(test_year_1999_2002_updates[update][row]["Date Issued"], '%Y-%m-%d').year <= 2002), 
                            f"Expected year of updates output to be between 1999 and 2002, got {test_year_1999_2002_updates[update][row]['Date Issued']}.")
#7.)  
        test_year_not_equal_2019_updates = self.all_updates.year(test_year_not_equal_2019)
        test_year_not_equal_2019_updates_total = 0

        for update in test_year_not_equal_2019_updates:
            for row in range(0, len(test_year_not_equal_2019_updates[update])):
                #convert year in Date Issued column to string of year, remove "corrected" date if applicable
                current_updates_year = extract_date(test_year_not_equal_2019_updates[update][row]["Date Issued"]).year
                test_year_not_equal_2019_updates_total+=1
                self.assertTrue(current_updates_year != 2019, f"Expected year of updates output to not equal 2019, got {test_year_not_equal_2019_updates[update][row]['Date Issued']}.")
        
        self.assertEqual(test_year_not_equal_2019_updates_total, 886, f"Expected 886 updates in output object, got {test_year_not_equal_2019_updates_total}.")
#8.)
        test_year_not_equal_2005_2009_updates = self.all_updates.year(test_year_not_equal_2005_2009)
        test_year_not_equal_2005_2009_updates_total = 0

        for update in test_year_not_equal_2005_2009_updates:
            for row in range(0, len(test_year_not_equal_2005_2009_updates[update])):
                #convert year in Date Issued column to string of year, remove "corrected" date if applicable
                current_updates_year = extract_date(test_year_not_equal_2005_2009_updates[update][row]["Date Issued"]).year
                test_year_not_equal_2005_2009_updates_total+=1
                self.assertTrue(current_updates_year != 2005 and current_updates_year != 2009, f"Expected year of updates output to not equal 2005 or 2009, got {test_year_not_equal_2005_2009_updates[update][row]['Date Issued']}.")

        self.assertEqual(test_year_not_equal_2005_2009_updates_total, 897, f"Expected 897 updates in output object, got {test_year_not_equal_2005_2009_updates_total}.")
#9.)
        with self.assertRaises(ValueError):
            self.all_updates.year(test_year_error1) #1234
            self.all_updates.year(test_year_error2) #abcdef
            self.all_updates.year(test_year_error3) #>2009<>
#10.)    
        with self.assertRaises(TypeError):
            self.all_updates.year(test_year_error4) #8.99
            self.all_updates.year(test_year_error5) #12345
            self.all_updates.year(test_year_error6) #True

    # @unittest.skip("")
    @patch('iso3166_updates.sys.stdout', new_callable=io.StringIO)
    def test_updates_search(self, mock_stdout):
        """ Testing the search function that returns the updates per input search terms. """
        test_search_australia = "AU-NSW"
        test_search_parishes = "parishes"
        test_search_governorates = "governorates"
        test_search_date = "2024-02-29"
        test_search_date_2 = "2021-11-25,2023-11-23"
        test_search_addition_deletion = "Addition,Deletion"
        test_search_subdivision = "subdivision,region"
        test_search_zzz = "zzz"
        test_search_blahblah = "blahblahstan"
        test_search_error1 = ["Belfast,Dublin,Donegal"]
        test_search_error2 = 12345
        test_search_error3 = True
#1.)
        test_search_australia_updates = self.all_updates.search(test_search_australia)
        expected_search_australia_updates = [{'Country Code': 'AU', 'Change': 'Codes: New South Wales: AU-NS -> AU-NSW. Queensland: AU-QL -> AU-QLD. Tasmania: AU-TS -> AU-TAS. Victoria: AU-VI -> AU-VIC. Australian Capital Territory: AU-CT -> AU-ACT.', 
                                            'Description of Change': 'Change of subdivision code in accordance with Australian Standard AS 4212-1994.', 'Date Issued': '2004-03-08', 
                                            'Source': 'Newsletter I-6 - https://web.archive.org/web/20081218103224/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf.', 'Match Score': 100}]

        self.assertEqual(test_search_australia_updates, expected_search_australia_updates, f"Expected and observed search output do not match:\n{test_search_australia_updates}")
#2.)
        test_search_parishes_updates = self.all_updates.search(test_search_parishes, likeness_score=80)
        expected_search_parishes_updates = [{'Country Code': 'AD', 'Change': 'Subdivisions added: 7 parishes.', 'Description of Change': 'Addition of the administrative subdivisions and of their code elements.', 'Date Issued': '2007-04-17', 
                                             'Source': 'Newsletter I-8 - https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf.', 'Match Score': 100}, 
                                             {'Country Code': 'AG', 'Change': 'Subdivisions added: 6 parishes, 1 dependency.', 'Description of Change': 'Addition of the administrative subdivisions and of their code elements.', 
                                             'Date Issued': '2007-04-17', 'Source': 'Newsletter I-8 - https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf.', 'Match Score': 100}, 
                                             {'Country Code': 'BB', 'Change': 'Subdivisions added: 11 parishes.', 'Description of Change': 'Addition of the administrative subdivisions and of their code elements.', 'Date Issued': '2007-04-17', 
                                             'Source': 'Newsletter I-8 - https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf.', 'Match Score': 100}, 
                                             {'Country Code': 'DM', 'Change': 'Subdivisions added: 10 parishes.', 'Description of Change': 'Addition of the administrative subdivisions and of their code elements.', 'Date Issued': '2007-04-17', 
                                             'Source': 'Newsletter I-8 - https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf.', 'Match Score': 100}, 
                                             {'Country Code': 'GD', 'Change': 'Subdivisions added: 6 parishes, 1 dependency.', 'Description of Change': 'Addition of the administrative subdivisions and of their code elements.', 'Date Issued': '2007-04-17', 
                                             'Source': 'Newsletter I-8 - https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf.', 'Match Score': 100}, 
                                             {'Country Code': 'KN', 'Change': 'Subdivisions added: 2 states, 14 parishes.', 'Description of Change': 'Addition of the administrative subdivisions and of their code elements.', 'Date Issued': '2007-04-17', 
                                             'Source': 'Newsletter I-8 - https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf.', 'Match Score': 100}, 
                                             {'Country Code': 'VC', 'Change': 'Subdivisions added: 6 parishes.', 'Description of Change': 'Addition of the administrative subdivisions and of their code elements.', 'Date Issued': '2007-04-17', 
                                             'Source': 'Newsletter I-8 - https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf.', 'Match Score': 100}]

        self.assertEqual(test_search_parishes_updates, expected_search_parishes_updates, f"Expected and observed search output do not match:\n{test_search_parishes_updates}")
#3.)
        test_search_governorates_updates = self.all_updates.search(test_search_governorates)
        expected_search_governorates_updates = [{'Country Code': 'BH', 'Change': 'Subdivision layout: 12 regions -> 5 governorates.', 'Description of Change': 'Modification of the administrative structure.', 'Date Issued': '2007-04-17', 
                                                 'Source': 'Newsletter I-8 - https://web.archive.org/web/20081218103230/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf.', 'Match Score': 100}, 
                                                 {'Country Code': 'GN', 'Change': 'Change Subdivision category special zone to governorate (GN-C); change governorates to administrative regions; update List Source.', 
                                                 'Description of Change': '', 'Date Issued': '2014-10-30', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:GN.', 'Match Score': 100}, 
                                                 {'Country Code': 'OM', 'Change': 'Change of subdivision category from region to governate for OM-BA, OM-DA, OM-SH, OM-WU, OM-ZA; change of subdivision code from OM-BA to OM-BJ, from OM-SH to OM-SJ; change of spelling of OM-BJ, OM-SJ; addition of governorates OM-BS, OM-SS; addition of local variations of OM-MA, OM-ZU; update List Source.', 
                                                 'Description of Change': '', 'Date Issued': '2015-11-27', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:OM.', 'Match Score': 100}, 
                                                 {'Country Code': 'PS', 'Change': 'Subdivisions added: 16 governorates.', 'Description of Change': 'Administrative division taken into account.', 'Date Issued': '2011-12-13 (corrected 2011-12-15)', 
                                                 'Source': 'Newsletter II-3 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf.', 'Match Score': 100}, 
                                                 {'Country Code': 'YE', 'Change': "Subdivisions added: YE-DA Aḑ Ḑāli'. YE-AM 'Amrān.", 'Description of Change': 'Addition of two governorates.', 'Date Issued': '2002-12-10', 
                                                 'Source': 'Newsletter I-4 - https://web.archive.org/web/20081218103210/http://www.iso.org/iso/iso_3166-2_newsletter_i-4_en.pdf.', 'Match Score': 100}]

        self.assertEqual(test_search_governorates_updates, expected_search_governorates_updates, f"Expected and observed search output do not match:\n{test_search_governorates_updates}")
#4.)
        test_search_date_updates = self.all_updates.search(test_search_date, exclude_match_score=1) 
        expected_search_date_updates = {'BO': {'Change': 'Change of short name upper case: replace the parentheses with a coma.', 'Description of Change': '', 'Date Issued': '2024-02-29', 
                                              'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BO.'}, 
                                        'FM': {'Change': 'Change of short name upper case: replace the parentheses with a coma and correct the remark in English of the entry of Micronesia Federate states (removing duplicated text).', 
                                              'Description of Change': '', 'Date Issued': '2024-02-29', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:FM.'}, 
                                        'IR': {'Change': 'Change of short name upper case: replace the parentheses with a comma.', 'Description of Change': '', 'Date Issued': '2024-02-29', 
                                              'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:IR.'}, 
                                        'KP': {'Change': 'Change of short name upper case in eng: replace the parentheses with a coma.', 'Description of Change': '', 'Date Issued': '2024-02-29', 
                                              'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:KP.'}, 
                                        'VE': {'Change': 'Change of short name upper case: replace the parentheses with a comma.', 'Description of Change': '', 'Date Issued': '2024-02-29', 
                                              'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:VE.'}}

        self.assertEqual(test_search_date_updates, expected_search_date_updates, f"Expected and observed search output do not match:\n{test_search_date}")
#5.)
        test_search_date_updates_2 = self.all_updates.search(test_search_date_2)
        self.assertEqual(len(test_search_date_updates_2), 23, f"Expected 23 search outputs, got {len(test_search_date_updates_2)}")
#6.)
        test_search_addition_deletion_updates = self.all_updates.search(test_search_addition_deletion)
        self.assertEqual(len(test_search_addition_deletion_updates), 318, f"Expected 318 search outputs, got {len(test_search_addition_deletion_updates)}")
#7.)
        test_search_subdivision_region_updates = self.all_updates.search(test_search_subdivision)
        self.assertEqual(len(test_search_subdivision_region_updates), 241, f"Expected 241 search outputs, got {len(test_search_subdivision_region_updates)}")
#8.)
        test_search_zzz_updates = self.all_updates.search(test_search_zzz)
        self.assertEqual(test_search_zzz_updates, [], f"Expected no search outputs, got {test_search_zzz_updates}")
#9.)
        test_search_blah_updates = self.all_updates.search(test_search_blahblah)
        self.assertEqual(test_search_blah_updates, [], f"Expected no search outputs, got {test_search_blah_updates}")
#10.)    
        with self.assertRaises(TypeError):
            self.all_updates.search(test_search_error1) #["Belfast,Dublin,Donegal"]
            self.all_updates.search(test_search_error2) #12345
            self.all_updates.search(test_search_error3) #True
#11.)
        with self.assertRaises(ValueError):
            self.all_updates.search(test_search_australia, likeness_score=150) #likeness_score=150
            self.all_updates.search(test_search_australia, likeness_score=0) #likeness_score=0

    # @unittest.skip("")
    def test_updates_date_range(self):
        """ Testing the date range function that returns all updates within a specified date range. """
        test_date_range1 = "2002-10-05,2004-12-15"
        test_date_range2 = "2007-01-01,2007-12-25"
        test_date_range3 = "2013-09-11"
        test_date_range4 = "12/04/2015,07/05/2010" 
        test_date_range5 = "1996-04-03,1996-05-03"
        test_error_date_range1 = "2019-08-16"
        test_error_date_range2 = "05-10-2008"
        test_error_date_range3 = "2002-10-05,2004-12-15,2019-08-16"
#1.)
        test_date_range1_updates = self.all_updates.date_range(test_date_range1) #2002-10-05,2004-12-15
        test_date_range1_updates_expected = ['AF', 'AL', 'AU', 'BI', 'BW', 'CA', 'CH', 'CN', 'CO', 'CZ', 'EC', 'ES', 'ET', 'GE', 'ID', 
                                             'IN', 'KG', 'KH', 'KP', 'KZ', 'LA', 'LY', 'MA', 'MD', 'MU', 'MY', 'RO', 'SI', 'SN', 'TJ', 
                                             'TL', 'TM', 'TN', 'TW', 'TZ', 'UG', 'UZ', 'VE', 'YE', 'ZA']
        
        for country_code, updates in test_date_range1_updates.items():
            for update in updates:
                current_updates_date = extract_date(update["Date Issued"])
                self.assertTrue(datetime.strptime("2002-10-05", "%Y-%m-%d") <= current_updates_date <= datetime.strptime("2004-12-15", "%Y-%m-%d"), 
                    f"Expected update of object to be between the dates 2002-10-05 and 2004-12-15, got date {current_updates_date}.")        
        self.assertEqual(list(test_date_range1_updates), test_date_range1_updates_expected, 
            f"Expected and observed country code objects do not match:\n{list(test_date_range1_updates)}.")
#2.)
        test_date_range2_updates = self.all_updates.date_range(test_date_range2) #2007-01-01,2007-12-25
        test_date_range2_updates_expected = ['AD', 'AG', 'BA', 'BB', 'BG', 'BH', 'BL', 'CI', 'CZ', 'DM', 'DO', 'EG', 'FR', 'GB', 'GD', 'GE', 'GG', 
                                             'GN', 'GP', 'HT', 'IM', 'IR', 'IT', 'JE', 'KE', 'KN', 'KW', 'LB', 'LC', 'LI', 'LR', 'ME', 'MF', 'MK', 
                                             'MT', 'NR', 'PF', 'PW', 'RE', 'RS', 'RU', 'RW', 'SB', 'SC', 'SD', 'SG', 'SM', 'TD', 'TF', 'TO', 'TV', 
                                             'UG', 'VC', 'YE', 'ZA']

        for country_code, updates in test_date_range2_updates.items():
            for update in updates:
                current_updates_date = extract_date(update["Date Issued"])
                self.assertTrue(datetime.strptime("2007-01-01", "%Y-%m-%d") <= current_updates_date <= datetime.strptime("2007-12-25", "%Y-%m-%d"), 
                    f"Expected update of object to be between the dates 2005-08-09 and 2005-09-19, got date {current_updates_date}.")    
        self.assertEqual(list(test_date_range2_updates), test_date_range2_updates_expected, 
            f"Expected and observed country code objects do not match:\n{list(test_date_range2_updates)}.")
#3.)
        test_date_range3_updates = self.all_updates.date_range(test_date_range3) #2013-09-11
        test_date_range3_updates_expected = ['AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AS', 'AT', 'AU', 'AW', 'AX', 'AZ', 'BA', 'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 
                                             'BJ', 'BL', 'BM', 'BN', 'BO', 'BQ', 'BR', 'BS', 'BT', 'BV', 'BW', 'BY', 'BZ', 'CA', 'CC', 'CD', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN', 
                                             'CO', 'CR', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ', 'DE', 'DJ', 'DM', 'DO', 'DZ', 'EC', 'EE', 'EG', 'EH', 'ER', 'ES', 'ET', 'FI', 'FJ', 'FK', 
                                             'FM', 'FO', 'FR', 'GA', 'GB', 'GD', 'GE', 'GF', 'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GR', 'GS', 'GT', 'GU', 'GW', 'GY', 'HK', 
                                             'HM', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM', 'IN', 'IO', 'IQ', 'IR', 'IS', 'IT', 'JE', 'JM', 'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 
                                             'KP', 'KR', 'KW', 'KY', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MF', 'MG', 'MH', 
                                             'MK', 'ML', 'MM', 'MN', 'MO', 'MP', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW', 'MX', 'NA', 'NC', 'NE', 'NF', 'NG', 'NI', 'NL', 'NO', 'NP', 
                                             'NR', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG', 'PH', 'PK', 'PL', 'PM', 'PN', 'PR', 'PS', 'PT', 'PW', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW', 
                                             'SA', 'SB', 'SC', 'SD', 'SI', 'SJ', 'SL', 'SM', 'SO', 'SR', 'SS', 'ST', 'SV', 'SX', 'SY', 'SZ', 'TC', 'TD', 'TF', 'TG', 'TH', 'TJ', 'TK', 
                                             'TL', 'TN', 'TR', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'UM', 'US', 'UY', 'UZ', 'VA', 'VC', 'VE', 'VG', 'VI', 'VN', 'WF', 'WS', 'YE', 'YT', 
                                             'ZA', 'ZM', 'ZW']

        for country_code, updates in test_date_range3_updates.items():
            for update in updates:
                current_updates_date = extract_date(update["Date Issued"])
                self.assertTrue(datetime.strptime("2013-09-11", "%Y-%m-%d") <= current_updates_date <= datetime.today(), 
                    f"Expected update of object to be between the dates 2013-09-11 and today's date, got date {current_updates_date}.")   
        self.assertEqual(list(test_date_range3_updates), test_date_range3_updates_expected, 
            f"Expected and observed country code objects do not match:\n{list(test_date_range3_updates)}.")
#4.)
        test_date_range4_updates = self.all_updates.date_range(test_date_range4, sort_by_date="dateAsc") #12/04/2015,07/05/2010, sort output ascending
        test_date_range4_updates_country_codes_expected = ['AD', 'AF', 'AG', 'AL', 'AO', 'AR', 'AT', 'AW', 'AX', 'AZ', 'BA', 'BB', 'BD', 
                                                           'BE', 'BF', 'BG', 'BI', 'BL', 'BN', 'BO', 'BQ', 'BS', 'BT', 'BV', 'BW', 'BY', 
                                                           'BZ', 'CA', 'CF', 'CG', 'CL', 'CM', 'CR', 'CU', 'CV', 'CW', 'CY', 'DE', 'DJ', 
                                                           'DK', 'DM', 'DO', 'DZ', 'EC', 'EE', 'EG', 'ER', 'ES', 'ET', 'FI', 'FJ', 'FM', 
                                                           'FR', 'GA', 'GB', 'GD', 'GH', 'GL', 'GM', 'GN', 'GQ', 'GR', 'GT', 'GY', 'HN', 
                                                           'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IN', 'IQ', 'IR', 'IT', 'JE', 'JM', 'JO', 
                                                           'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KP', 'KR', 'KW', 'LA', 'LC', 'LI', 'LK', 
                                                           'LS', 'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MF', 'MG', 'MH', 'MK', 
                                                           'MM', 'MR', 'MV', 'MW', 'MX', 'NA', 'NE', 'NG', 'NL', 'NO', 'NP', 'NR', 'NU', 
                                                           'NZ', 'OM', 'PA', 'PE', 'PG', 'PH', 'PK', 'PL', 'PS', 'PT', 'QA', 'RO', 'RS', 
                                                           'RU', 'SA', 'SB', 'SC', 'SD', 'SE', 'SH', 'SI', 'SM', 'SN', 'SO', 'SR', 'SS', 
                                                           'SV', 'SX', 'SY', 'TC', 'TD', 'TJ', 'TL', 'TM', 'TN', 'TR', 'TZ', 'UA', 'UG', 
                                                           'UM', 'US', 'UY', 'VA', 'VC', 'VE', 'VN', 'WS', 'YE', 'ZM']
        test_date_range4_updates_country_codes_observed = []

        for updates in test_date_range4_updates:
            #append country code of each object
            test_date_range4_updates_country_codes_observed.append(updates["Country Code"])

            current_updates_date = extract_date(updates["Date Issued"])
            self.assertTrue(datetime.strptime("2010-05-07", "%Y-%m-%d") <= current_updates_date <= datetime.strptime("2015-04-12", "%Y-%m-%d"), 
                f"Expected update of object to be between the dates 2010-05-07 and 2015-04-12, got date {current_updates_date}.")   
            self.assertEqual(list(updates), ["Country Code", "Change", "Description of Change", "Date Issued", "Source"], f"Expected and observed attributes list do not match\n{list(updates)}.")

        #sort observed list of country codes
        test_date_range4_updates_country_codes_observed = sorted(set(test_date_range4_updates_country_codes_observed))

        self.assertEqual(test_date_range4_updates_country_codes_observed, test_date_range4_updates_country_codes_expected, 
            f"Expected and observed country code objects do not match:\n{test_date_range4_updates_country_codes_observed}.")
#5.)
        test_date_range5_updates = self.all_updates.date_range(test_date_range5, sort_by_date="dateDesc") #1996-04-03,1996-05-03, sort output descending
        test_date_range5_updates_expected = ['VA']

        for country_code, updates in test_date_range5_updates.items():
            for update in updates:
                current_updates_date = extract_date(update["Date Issued"])
                self.assertTrue(datetime.strptime("1996-04-03", "%Y-%m-%d") <= current_updates_date <= datetime.strptime("1996-05-03", "%Y-%m-%d"), 
                    f"Expected update of object to be between the dates 1996-04-03 and 1996-05-03, got date {current_updates_date}.")   
        self.assertEqual(list(test_date_range5_updates), test_date_range5_updates_expected, 
            f"Expected and observed country code objects do not match:\n{list(test_date_range5_updates)}.")
#6.)
        with self.assertRaises(ValueError):
            self.all_updates.date_range(test_error_date_range1)
            self.all_updates.date_range(test_error_date_range2)
            self.all_updates.date_range(test_error_date_range3)
#7.)
        with self.assertRaises(TypeError):
            self.all_updates.date_range(False)
            self.all_updates.date_range(10.5)
            self.all_updates.date_range(2390)

    # @unittest.skip("")
    def test_custom_updates(self):
        """ Testing custom updates object are correctly added to main iso3166-updates.json object. """
        test_custom_updates_japan = {"Change": "New change for Japan!", "Date Issued": "2025-01-01", "Description of Change": "Blahblahblah", "Source": ""}
        test_custom_updates_mali = {"Change": "Subdivision deletion for Mali.", "Date Issued": "16-08-2025", "Description of Change": "Very important ISO 3166 deletion."}
        test_custom_updates_nauru = {"Change": "New change for Nauru!", "Date Issued": "01/01/2026", "Description of Change": "Very important ISO 3166 changes."}
        test_custom_updates_serbia = {"Change": "Brand new subdivision added.", "Date Issued": "2nd February 2027", "Description of Change": "Just a lil small change, no biggie.", "Source": "https://example.rs"}
        test_custom_updates_sudan = {"Change": "Change without Date Issued. Error should be raised."}
        test_custom_updates_tajikistan = {"Date Issued": "Date Issued without Change. Error should be raised."}
#1.)    
        self.all_updates.custom_update("JP", custom_update_object=test_custom_updates_japan, save_new=True, save_new_filename=self.custom_updates_filepath)
        self.assertIn(test_custom_updates_japan, self.all_updates.all["JP"], "Expected new custom update for JP to be in main updates JSON.")
#2.)
        self.all_updates.custom_update("ML", custom_update_object=test_custom_updates_mali, save_new=True, save_new_filename=self.custom_updates_filepath)
        self.assertIn(test_custom_updates_mali, self.all_updates.all["ML"], "Expected new custom update for ML to be in main updates JSON.")
#3.)
        self.all_updates.custom_update("NRU", custom_update_object=test_custom_updates_nauru, save_new=True, save_new_filename=self.custom_updates_filepath)
        self.assertIn(test_custom_updates_nauru, self.all_updates.all["NR"], "Expected new custom update for NR to be in main updates JSON.")
#4.)
        self.all_updates.custom_update("688", change=test_custom_updates_serbia["Change"], date_issued=test_custom_updates_serbia["Date Issued"], 
            description_of_change=test_custom_updates_serbia["Description of Change"], source=test_custom_updates_serbia["Source"], save_new=True, save_new_filename=self.custom_updates_filepath)
        self.assertIn(test_custom_updates_serbia, self.all_updates.all["RS"], "Expected new custom update for RS to be in main updates JSON.")
#5.)
        self.all_updates.custom_update("JP", custom_update_object=test_custom_updates_japan, delete=1, save_new=True, save_new_filename=self.custom_updates_filepath)
        self.all_updates.custom_update("ML", custom_update_object=test_custom_updates_mali, delete=1, save_new=True, save_new_filename=self.custom_updates_filepath)
        self.all_updates.custom_update("NRU", custom_update_object=test_custom_updates_nauru, delete=1, save_new=True, save_new_filename=self.custom_updates_filepath)
        self.all_updates.custom_update("688", custom_update_object=test_custom_updates_serbia, delete=1, save_new=True, save_new_filename=self.custom_updates_filepath)
#6.)
        with self.assertRaises(ValueError): 
            self.all_updates.custom_update("AA")
            self.all_updates.custom_update(123)
            self.all_updates.custom_update("SD", change=test_custom_updates_sudan)
            self.all_updates.custom_update("TV", change="Brand new change", date_issued="2025-2025-2025")
            self.all_updates.custom_update("SD", custom_update_object=test_custom_updates_sudan, save_new=True, save_new_filename=self.custom_updates_filepath)
            self.all_updates.custom_update("TJ", custom_update_object=test_custom_updates_tajikistan, save_new=True, save_new_filename=self.custom_updates_filepath)
#7.)
        with self.assertRaises(TypeError):
            self.all_updates.custom_update("BE", change=123)
            self.all_updates.custom_update("BE", change="Valid change", date_issued=False)
            self.all_updates.custom_update("BE", change="Valid change", date_issued="Valid date", description_of_change=9.02)
            self.all_updates.custom_update("BE", change="Valid change", date_issued="Valid date", description_of_change="Valid desc", source=100)

    # @unittest.skip("")
    def test_validate_updates_dates(self):
        """ Testing each date and corrected date in updates JSON is in valid YYYY-MM-DD format. """
#1.)
        for country in self.all_updates.all:
            for update in range(0, len(self.all_updates.all[country])):
                current_date = self.all_updates.all[country][update]["Date Issued"]

                #extract the original and corrected date from attribute, if applicable
                match = re.search(r"\d{4}-\d{2}-\d{2}", current_date)  
                corrected_match = re.search(r"\(corrected (\d{4}-\d{2}-\d{2})\)", current_date) 

                #find matching date and corrected date
                if match:
                    original_date = match.group(0) 
                else:
                    original_date = None  
                if corrected_match:
                    corrected_date = corrected_match.group(1)  # Extract corrected date
                else:
                    corrected_date = None  # No corrected date found

                #auxiliary function to validate date format
                def is_valid_date(date_str):
                    try:
                        datetime.strptime(date_str, "%Y-%m-%d")
                        return True
                    except ValueError:
                        return False

                #validate original date
                if original_date:
                    self.assertTrue(is_valid_date(original_date), f"Date in country {country} is not in valid YYYY-MM-DD format: {original_date}.")
                    self.assertLessEqual(datetime.strptime(original_date, "%Y-%m-%d").date(), date.today(), f"Expected no future publication dates, got: {original_date}.") #*****

                #validate corrected date, if applicable
                if corrected_date:
                    self.assertTrue(is_valid_date(corrected_date), f"Corrected date in country {country} is not in valid YYYY-MM-DD format: {corrected_date}.")
                    self.assertLessEqual(datetime.strptime(corrected_date, "%Y-%m-%d").date(), date.today(), f"Expected no future publication dates, got: {corrected_date}.")

    # @unittest.skip("")
    @patch('iso3166_updates.sys.stdout', new_callable=io.StringIO)
    def test_check_for_updates(self, mock_stdout): 
        """ Testing functionality that pulls the latest object from repo and compares with object in current version of software. """
        self.all_updates.check_for_updates()

    # @unittest.skip("")
    def test_updates_str(self):
        """ Testing __str__ function returns correct string representation for class object. """
        self.assertEqual(str(self.all_updates), f"Instance of ISO 3166 Updates class: Version {self.all_updates.__version__}.", 
                f"Expected and observed string output for class instance do not match:\n{str(self.all_updates)}.")

    # @unittest.skip("")
    def test_updates_repr(self):
        """ Testing __repr__ function returns correct object representation for class object. """
        self.assertEqual(repr(self.all_updates), "<Updates(version='1.8.5', countries_loaded=250, total_updates=911, source_file='test-iso3166-updates.json')>",
                f"Expected and observed object representation for class instance do not match:\n{repr(self.all_updates)}.")

    # @unittest.skip("")
    def test_updates_sizeof(self):
        """ Testing __sizeof__ function returns correct output for class object. """
        self.assertEqual(self.all_updates.__sizeof__(), 0.329, f"Expected and observed output for sizeof function do not match:\n{self.all_updates.__sizeof__()}.")
        
    # @unittest.skip("")
    def test_updates_len(self):
        """ Testing __len__ function returns the correct length for the updates object. """
        self.assertEqual(len(self.all_updates), 911, f"Expected the length of updates object to be 911, got {len(self.all_updates)}.")

    # @unittest.skip("")
    def test_updates_contains(self):
        """ Testing __contains__ function returns the correct output for object. """
        self.assertTrue("US" in self.all_updates, "Expected US updates data to be in object.")
        self.assertTrue("LU" in self.all_updates, "Expected LU updates data to be in object.")
        self.assertTrue("VU" in self.all_updates, "Expected VU updates data to be in object.")
        self.assertFalse("AA" in self.all_updates, "Expected AA updates data to be in object.")
        self.assertFalse("ZZ" in self.all_updates, "Expected ZZ updates data to be in object.")

    # @unittest.skip("")
    def tearDown(self):
        """ Delete instance of Updates class. """
        del self.all_updates
        shutil.rmtree(self.test_export_folder)
    
def extract_date(date_str: str) -> datetime:
    """
    Extract the original and corrected date from the Date Issued column,
    return Datetime object.

    Parameters
    ==========
    :date_str: str
        input publication date.

    Returns
    =======
    :parsed_date: datetime
        converted date as a datetime object.
    """
    #if date is 'corrected', parse new date 
    if "corrected" in date_str:
        cleaned = re.sub(r"[(].*[)]", "", date_str)
        cleaned = cleaned.replace(' ', '').replace('.', '').replace('\n', '')
        return datetime.strptime(cleaned, "%Y-%m-%d")
    #parse original date
    else:
        return datetime.strptime(date_str.replace('\n', ''), "%Y-%m-%d")
    
if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)