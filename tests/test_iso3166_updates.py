from iso3166_updates import *
import iso3166
from datetime import datetime, date
from importlib.metadata import metadata
import unittest
unittest.TestLoader.sortTestMethodsUsing = None

class ISO3166_Updates_Tests(unittest.TestCase):
    """
    Test suite for testing the iso3166-updates Python software package. 

    Test Cases
    ==========
    test_iso3166_updates_metadata:
        testing correct software metadata for the iso3166-updates package. 
    test_updates_all:
        testing correct functionality for 'all' attribute in ISO3166_Updates class.
    test_updates_alpha:
        testing correct functionality for __getitem__ function in ISO3166_Updates class.
    test_updates_year:
        testing correct functionality for year() function in ISO3166_Updates class.
    test_updates_months:
        testing correct functionality for months() function in ISO3166_Updates class.
    """
    def setUp(self):
        """ Initialise test variables. """                
        #output columns from various functions
        self.expected_output_columns = ["Code/Subdivision Change", "Description of Change", "Date Issued", "Edition/Newsletter"]

        #instance of ISO3166_Updates() class
        self.all_updates = ISO3166_Updates()

    # @unittest.skip("Skipping metadata unit tests.")    
    def test_iso3166_updates_metadata(self): 
        """ Testing correct iso3166-updates software version and metadata. """
        # self.assertEqual(metadata('iso3166-updates')['version'], "1.7.1", 
        #     f"iso3166-updates version is not correct, expected 1.7.1, got {metadata('iso3166-updates')['version']}.")
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
        # self.assertEqual(metadata('iso3166-updates')['home-page'], "https://iso3166-updates.com/api/", 
        #     f"iso3166-updates home page url is not correct, expected https://iso3166-updates.com/api/, got {metadata('iso3166-updates')['home-page']}.")
        self.assertEqual(metadata('iso3166-updates')['maintainer'], "AJ McKenna", 
            f"iso3166-updates maintainer is not correct, expected AJ McKenna, got {metadata('iso3166-updates')['maintainer']}.")
        self.assertEqual(metadata('iso3166-updates')['license'], "MIT", 
            f"iso3166-updates license type is not correct, expected MIT, got {metadata('iso3166-updates')['license']}.")
    
    def test_updates_all(self):
        """ Testing 'all' attribute that should return all ISO 3166 updates data. """
#1.)
        test_all_updates = self.all_updates.all 

        self.assertIsInstance(test_all_updates, dict, 
            f"Expected output object to be of type dict, got {type(test_all_updates)}.")
        self.assertEqual(len(test_all_updates), 249, 
            f"Expected there to be 249 country keys in output object, got {len(test_all_updates)}.")
        for iso_code in list(test_all_updates.keys()):
            self.assertIn(iso_code, list(iso3166.countries_by_alpha2.keys()),
                    f"Alpha-2 code {iso_code} not found in list of available codes.")
#2.)
        updates_counter = 0
        for iso_code in test_all_updates:
            for update in range(0, len(test_all_updates[iso_code])):
                updates_counter += 1
                self.assertNotEqual(test_all_updates[iso_code][update]["Code/Subdivision Change"], "", "All individual ISO 3166 updates should not have an empty Code/Subdivision Change attribute.")
        self.assertEqual(updates_counter, 925, f"Expected 925 total ISO 3166 updates in output object, got {updates_counter}.")
#3.)
        iso3166_updates_empty = ["MZ", "PY", "SK", "VU"]  #testing only these country updates objects have empty dicts
        for iso_code in test_all_updates:
             if (test_all_updates[iso_code] == {}):
                  self.assertTrue(iso_code in iso3166_updates_empty, 
                        f"Expected country code's updates object to be empty:\n{test_all_updates[iso_code]}.")

    def test_updates_alpha(self):
        """ Testing __getitem__ function that allows the updates class to be subscriptable, using a variety of alpha-2 country codes. """
        test_alpha_bt = "BT" #Bhutan
        test_alpha_dj = "DJ" #Djibouti
        test_alpha_hn = "HND" #Honduras
        test_alpha_fj_gh_gn = "FJ, GHA, 324" #Fiji, Ghana and Guinea
        test_alpha_yt = "175" #Mayotte
        test_alpha_error_1 = "XX" #should raise value error
        test_alpha_error_2 = "abcdefg" #should raise value error
        test_alpha_error_3 = False #should raise type error
        test_alpha_error_4 = 1234 #should raise type error
#1.) 
        test_alpha_bt_updates = self.all_updates[test_alpha_bt] #Bhutan

        test_alpha_bt_updates_expected = {
            "Date Issued": "2020-11-24",
            "Edition/Newsletter": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:BT).",
            "Description of Change": "",
            "Code/Subdivision Change": "Change of spelling of BT-43; Update List Source."
            }

        self.assertEqual(len(test_alpha_bt_updates[test_alpha_bt]), 5, 
            f"Expected there to be 5 updates in output object, got {len(test_alpha_bt_updates[test_alpha_bt])}.")
        for row in test_alpha_bt_updates[test_alpha_bt]:
            self.assertEqual(list(row.keys()), self.expected_output_columns, f"Columns from output do not match expected\n{list(row.keys())}.")
            self.assertIsInstance(row, dict, f"Output object should be of type dict, got {type(row)}.")
        self.assertEqual(test_alpha_bt_updates["BT"][0], test_alpha_bt_updates_expected, "Expected and observed outputs do not match.")
#2.) 
        test_alpha_dj_updates = self.all_updates[test_alpha_dj] #Djibouti
        test_alpha_dj_updates_expected = {
            "Date Issued": "2020-11-24",
            "Edition/Newsletter": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:DJ).",
            "Description of Change": "",
            "Code/Subdivision Change": "Correction of the Code Source."
            }

        self.assertEqual(len(test_alpha_dj_updates[test_alpha_dj]), 6, 
            f"Expected there to be 6 updates in output object, got {len(test_alpha_dj_updates[test_alpha_dj])}.")
        for row in test_alpha_dj_updates[test_alpha_dj]:
            self.assertEqual(list(row.keys()), self.expected_output_columns, f"Columns from output do not match expected\n{list(row.keys())}.")
            self.assertIsInstance(row, dict, f"Output object should be of type dict, got {type(row)}.")
        self.assertEqual(test_alpha_dj_updates["DJ"][0], test_alpha_dj_updates_expected, "Expected and observed outputs do not match.")
#3.) 
        test_alpha_hn_updates = self.all_updates[test_alpha_hn] #Honduras
        test_alpha_hn_updates_expected = {
            "Date Issued": "2011-12-13 (corrected 2011-12-15)",
            "Edition/Newsletter": "Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf).",
            "Description of Change": "",
            "Code/Subdivision Change": "Comment taken into account and source list update."
            }

        self.assertEqual(len(test_alpha_hn_updates["HN"]), 1, 
            f"Expected there to be 1 update in output object, got {len(test_alpha_hn_updates['HN'])}.")
        for row in test_alpha_hn_updates["HN"]:
            self.assertEqual(list(row.keys()), self.expected_output_columns, f"Columns from output do not match expected\n{list(row.keys())}.")
            self.assertIsInstance(row, dict, f"Output object should be of type dict, got {type(row)}.")
        self.assertEqual(test_alpha_hn_updates["HN"][0], test_alpha_hn_updates_expected, "Expected and observed outputs do not match.")
#4.) 
        test_alpha_fj_gh_gn_updates = self.all_updates[test_alpha_fj_gh_gn] #Fiji, Ghana, Guinea
        test_alpha_fj_gh_gn_updates_expected_1 = {
            "Date Issued": "2016-11-22",
            "Edition/Newsletter": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:FJ).",
            "Description of Change": "",
            "Code/Subdivision Change": "Reinstatement of provinces deleted due to a technical glitch."
            }
        test_alpha_fj_gh_gn_updates_expected_2 = {
            "Date Issued": "2020-11-24",
            "Edition/Newsletter": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:GH).",
            "Description of Change": "",
            "Code/Subdivision Change": "Correction of the Code Source."
            }
        test_alpha_fj_gh_gn_updates_expected_3 = {
            "Date Issued": "2020-11-24",
            "Edition/Newsletter": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:GN).",
            "Description of Change": "",
            "Code/Subdivision Change": "Correction of the Code Source."
            }
        
        self.assertEqual(len(test_alpha_fj_gh_gn_updates), 3, 
            f"Expected there to be 3 updates in output object, got {len(test_alpha_fj_gh_gn_updates)}.")
        self.assertEqual(list(test_alpha_fj_gh_gn_updates), ["FJ", "GH", "GN"])
        for code in test_alpha_fj_gh_gn_updates:
            for row in test_alpha_fj_gh_gn_updates[code]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, f"Columns from output do not match expected\n{list(row.keys())}.")
                self.assertIsInstance(row, dict, f"Output object should be of type dict, got {type(row)}.")
        self.assertEqual(test_alpha_fj_gh_gn_updates["FJ"][0], test_alpha_fj_gh_gn_updates_expected_1, "Expected and observed outputs do not match.")
        self.assertEqual(test_alpha_fj_gh_gn_updates["GH"][0], test_alpha_fj_gh_gn_updates_expected_2, "Expected and observed outputs do not match.")
        self.assertEqual(test_alpha_fj_gh_gn_updates["GN"][0], test_alpha_fj_gh_gn_updates_expected_3, "Expected and observed outputs do not match.")
#5.) 
        test_alpha_yt_updates = self.all_updates[test_alpha_yt] #Mayotte
        test_alpha_yt_updates_expected = {
            "Date Issued": "2022-11-29",
            "Edition/Newsletter": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:YT).",
            "Description of Change": "",
            "Code/Subdivision Change": "Modification of remark part 2 (no subdivisions relevant for this standard. Included also as a subdivision of France (FR-976))."
            }
        
        self.assertEqual(len(test_alpha_yt_updates["YT"]), 2, 
            f"Expected there to be 2 updates in output object, got {len(test_alpha_yt_updates['YT'])}.")
        for row in test_alpha_yt_updates["YT"]:
            self.assertEqual(list(row.keys()), self.expected_output_columns, f"Columns from output do not match expected\n{list(row.keys())}.")
            self.assertIsInstance(row, dict, f"Output object should be of type dict, got {type(row)}.")
        self.assertEqual(test_alpha_yt_updates["YT"][0], test_alpha_yt_updates_expected, "Expected and observed outputs do not match.")
#6.)     
        with self.assertRaises(ValueError):
            self.all_updates[test_alpha_error_1] 
            self.all_updates[test_alpha_error_2] 
#7.)
        with self.assertRaises(TypeError):
            self.all_updates[test_alpha_error_3] 
            self.all_updates[test_alpha_error_4]

    def test_updates_year(self):
        """ Testing year function that returns all ISO 3166 updates for input year/years, year range or greater than/less than input year. """
        test_year_2019 = "2019"
        test_year_2003 = "2003"
        test_year_2000_2001_2002 = "2000,2001,2002"
        test_year_gt_2021 = ">2021"
        test_year_2004_2008 = "2004-2008"
        test_year_1999_2002 = "2002-1999"
        test_year_error1 = "1234" #ValueError
        test_year_error2 = "abcdef" #ValueError
        test_year_error3 = 12345 #TypeError
        test_year_error4 = True #TypeError
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
        test_year_gt_2021_expected_keys = ['BO', 'CI', 'CN', 'DZ', 'ET', 'FI', 'FM', 'FR', 'GB', 'GF', 'GP', 'GT', 'HU', 'ID', 'IN', 'IQ', 'IR', 'IS', 'KH', 'KP', 
                                           'KR', 'KZ', 'LT', 'LV', 'ME', 'MQ', 'MX', 'NL', 'NP', 'NZ', 'PA', 'PH', 'PL', 'RE', 'RU', 'SI', 'SS', 'TR', 'VE', 'YT']

        self.assertEqual(len(test_year_gt_2021_updates), 40, 
            f"Expected 40 updates in output object, got {len(test_year_gt_2021_updates)}.")
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
        with self.assertRaises(ValueError):
            self.all_updates.year(test_year_error1)
            self.all_updates.year(test_year_error2)
#8.)    
        with self.assertRaises(TypeError):
            self.all_updates.year(test_year_error3)
            self.all_updates.year(test_year_error4)

    @unittest.skip("Skipping months unit tests as output changes over time.")
    def test_updates_months(self):
        """ Testing month function that returns all ISO 3166 updates for number of months or month range. """
        test_month_1 = "3"
        test_month_2 = "9"
        test_month_3 = "36"
        test_month_4 = "24-48"
        test_month_5 = "abc"
        test_month_6 = ""
        test_month_7 = False
        test_month_8 = 1234
        current_datetime = datetime.strptime(str(date.today()), '%Y-%m-%d')        
#1.)
        test_updates_month1 = self.all_updates.months(test_month_1) #3
        test_updates_month1_expected = {'BO': [{'Date Issued': '2024-02-29', 'Edition/Newsletter': 'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:BO).', 
            'Code/Subdivision Change': 'Change of short name upper case: replace the parentheses with a coma.', 'Description of Change': ''}], 
            'IR': [{'Date Issued': '2024-02-29', 'Edition/Newsletter': 'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:IR).', 
                    'Code/Subdivision Change': 'Change of short name upper case: replace the parentheses with a coma.', 'Description of Change': ''}], 
                    'KP': [{'Date Issued': '2024-02-29', 'Edition/Newsletter': 'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:KP).', 
                    'Code/Subdivision Change': 'Change of short name upper case in eng: replace the parentheses with a coma.', 'Description of Change': ''}], 
                    'FM': [{'Date Issued': '2024-02-29', 'Edition/Newsletter': 'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:FM).', 
                    'Code/Subdivision Change': 'Change of short name upper case: replace the parentheses with a coma and correct the remark in English of the entry of Micronesia Federate states (removing duplicated text).', 
                    'Description of Change': ''}], 
                    'VE': [{'Date Issued': '2024-02-29', 'Edition/Newsletter': 'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:VE).', 
                            'Code/Subdivision Change': 'Change of short name upper case: replace the parentheses with a coma.', 'Description of Change': ''}]}

        self.assertIsInstance(test_updates_month1, dict, f"Expected output object of API to be of type dict, got {type(test_updates_month1)}.")
        self.assertEqual(len(test_updates_month1), 5, f"Expected 5 rows returned from API, got {len(test_updates_month1)}.")
        self.assertEqual(test_updates_month1, test_updates_month1_expected,  f"Expected and observed outputs do not match\n{test_updates_month1}.")
#2.)
        test_updates_month2 = self.all_updates.months(test_month_2) #9

        self.assertIsInstance(test_updates_month2, dict, f"Expected output object of API to be of type dict, got {type(test_updates_month2)}.")
        self.assertEqual(len(test_updates_month2), 13, f"Expected 13 rows returned from API, got {len(test_updates_month2)}.")
        for alpha2 in list(test_updates_month2):
                for row in range(0, len(test_updates_month2[alpha2])):
                       current_date_issued = datetime.strptime(test_updates_month2[alpha2][row]["Date Issued"], '%Y-%m-%d')
                       self.assertTrue(((current_datetime.year - current_date_issued.year) * 12 + current_datetime.month - current_date_issued.month)-1 <= 9,
                                       f"Expected current updates published data to be within the past 9 months:\n{test_updates_month2[alpha2][row]}.")
#3.)
        test_request_month3 = self.all_updates.months(test_month_3) #36

        self.assertIsInstance(test_request_month3, dict, f"Expected output object of API to be of type dict, got {type(test_request_month3)}.")
        self.assertEqual(len(test_request_month3), 40, f"Expected 40 rows returned from API, got {len(test_request_month3)}.")
        for alpha2 in list(test_request_month3):
                for row in range(0, len(test_request_month3[alpha2])):
                       current_date_issued = datetime.strptime(test_request_month3[alpha2][row]["Date Issued"], '%Y-%m-%d')
                       self.assertTrue(((current_datetime.year - current_date_issued.year) * 12 + current_datetime.month - current_date_issued.month)-1 <= 36,
                                       f"Expected current updates published data to be within the past 36 months:\n{test_request_month3[alpha2][row]}.")
#4.)
        test_request_month4 = self.all_updates.months(test_month_4) #24-48

        self.assertIsInstance(test_request_month4, dict, f"Expected output object of API to be of type dict, got {type(test_request_month4)}.")
        self.assertEqual(len(test_request_month4), 82, f"Expected 82 rows returned from API, got {len(test_request_month4)}.")
        for alpha2 in list(test_request_month4):
                for row in range(0, len(test_request_month4[alpha2])):
                       current_date_issued = datetime.strptime(test_request_month4[alpha2][row]["Date Issued"], '%Y-%m-%d')
                       month_difference_date_issued = ((current_datetime.year - current_date_issued.year) * 12 + current_datetime.month - current_date_issued.month)-1
                #        self.assertTrue(month_difference_date_issued >= 24 and month_difference_date_issued <= 48,
                #                        f"Expected current updates published data to be within the month range of 24-48 months:\n{test_request_month4[alpha2][row]}.")
#5.)
        with self.assertRaises(ValueError):
            test_request_month5 = self.all_updates.months(test_month_5) #abc
            test_request_month6 = self.all_updates.months(test_month_6) #""
#5.)
        with self.assertRaises(TypeError):
            test_request_month7 = self.all_updates.months(test_month_7) #False
            test_request_month8 = self.all_updates.months(test_month_8) #1234

    def tearDown(self):
        """ Delete instance of ISO3166_Updates class. """
        del self.all_updates
        
if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)