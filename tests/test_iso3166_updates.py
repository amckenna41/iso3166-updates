import iso3166_updates as iso
import iso3166
from datetime import datetime
from importlib.metadata import metadata
import unittest
unittest.TestLoader.sortTestMethodsUsing = None

class ISO3166_Updates_Tests(unittest.TestCase):
    """
    Test suite for testing the iso3166-updates Python software package. 

    Test Cases
    ----------
    test_iso3166_updates_metadata:
        testing correct software metdata for the iso3166-updates package. 
    test_updates_all:
        testing correct functionality for 'all' attribute in ISO3166_Updates class.
    test_updates_alpha2:
        testing correct functionality for test_updates_alpha2 function in ISO3166_Updates class.
    test_updates_year:
        testing correct functionality for test_updates_year function in ISO3166_Updates class.
    """
    def setUp(self):
        """ Initialise test variables. """                
        #output columns from various functions
        self.expected_output_columns = ["Date Issued", "Edition/Newsletter", "Code/Subdivision change", "Description of change in newsletter"]
    
    def test_iso3166_updates_metadata(self): 
        """ Testing correct iso3166-updates software version and metadata. """
        self.assertEqual(metadata('iso3166-updates')['version'], "1.4.2", 
            "iso3166-updates version is not correct, got: {}".format(metadata('iso3166-updates')['version']))
        self.assertEqual(metadata('iso3166-updates')['name'], "iso3166-updates", 
            "iso3166-updates software name is not correct, got: {}".format(metadata('iso3166-updates')['name']))
        self.assertEqual(metadata('iso3166-updates')['author'], "AJ McKenna, https://github.com/amckenna41", 
            "iso3166-updates author is not correct, got: {}".format(metadata('iso3166-updates')['author']))
        self.assertEqual(metadata('iso3166-updates')['author-email'], "amckenna41@qub.ac.uk", 
            "iso3166-updates author email is not correct, got: {}".format(metadata('iso3166-updates')['author-email']))
        self.assertEqual(metadata('iso3166-updates')['summary'], "A Python package that pulls the latest updates & changes to all ISO3166 listed countries.", 
            "iso3166-updates package summary is not correct, got: {}".format(metadata('iso3166-updates')['summary']))
        self.assertEqual(metadata('iso3166-updates')['keywords'], "iso,iso3166,beautifulsoup,python,pypi,countries,country codes,csv,iso3166-2,iso3166-1,alpha-2,alpha-3,selenium,chromedriver", 
            "iso3166-updates keywords are not correct, got: {}".format(metadata('iso3166-updates')['keywords']))
        self.assertEqual(metadata('iso3166-updates')['home-page'], "https://github.com/amckenna41/iso3166-updates", 
            "iso3166-updates home page url is not correct, got: {}".format(metadata('iso3166-updates')['home-page']))
        self.assertEqual(metadata('iso3166-updates')['maintainer'], "AJ McKenna", 
            "iso3166-updates maintainer is not correct, got: {}".format(metadata('iso3166-updates')['maintainer']))
        self.assertEqual(metadata('iso3166-updates')['license'], "MIT", 
            "iso3166-updates license type is not correct, got: {}".format(metadata('iso3166-updates')['license']))
    
    def test_updates_all(self):
        """ Testing all attribute that should return all ISO 3166 updates data. """
#1.)
        test_all_updates = iso.updates.all 

        self.assertIsInstance(test_all_updates, dict, 
            "Expected there output object to be of type dict, got {}.".format(type(test_all_updates)))
        self.assertEqual(len(test_all_updates), 249, 
            "Expected there to be 249 updates in output object, got {}.".format(len(test_all_updates)))
        for iso_code in list(test_all_updates.keys()):
            self.assertIn(iso_code, list(iso3166.countries_by_alpha2.keys()),
                    "Alpha-2 code {} not found in list of available codes.".format(iso_code))

    def test_updates_alpha2(self):
        """ Testing __getitem__ function that allows the updates class to be subscriptable, using a variety of alpha-2 country codes. """
        test_alpha2_bt = "BT" #Bhutan
        test_alpha2_dj = "DJ" #Djibouti
        test_alpha2_hn = "HN" #Honduras
        test_alpha2_fj_gh_gn = "FJ, GH, GN" #Fiji, Ghana and Guinea
        test_alpha2_yt = "YT" #Mayotte
        test_alpha2_error_1 = "XX" #should raise value error
        test_alpha2_error_2 = "abcdefg" #should raise value error
        test_alpha2_error_3 = False #should raise type error
        test_alpha2_error_4 = 1234 #should raise type error
#1.) 
        test_alpha2_bt_updates = iso.updates[test_alpha2_bt] #Bhutan
    
        test_alpha2_bt_updates_expected = {
            "Date Issued": "2020-11-24",
            "Edition/Newsletter": "Online Browsing Platform (OBP).",
            "Description of change in newsletter": "Change of spelling of BT-43; Update List Source.",
            "Code/Subdivision change": ""
            }

        self.assertEqual(len(test_alpha2_bt_updates), 5, 
            "Expected there to be 5 updates in output object, got {}.".format(len(test_alpha2_bt_updates)))
        for row in test_alpha2_bt_updates:
            self.assertEqual(list(row.keys()), self.expected_output_columns, "Columns from output do not match expected.")
            self.assertIsInstance(row, dict, "Ouput object should be of type dict, got {}.".format(type(row)))
        self.assertEqual(test_alpha2_bt_updates[0], test_alpha2_bt_updates_expected, "Expected and observed outputs do not match.")
#2.) 
        test_alpha2_dj_updates = iso.updates[test_alpha2_dj] #Djibouti
    
        test_alpha2_dj_updates_expected = {
            "Date Issued": "2020-11-24",
            "Edition/Newsletter": "Online Browsing Platform (OBP).",
            "Description of change in newsletter": "Correction of the Code Source.",
            "Code/Subdivision change": ""
            }

        self.assertEqual(len(test_alpha2_dj_updates), 7, 
            "Expected there to be 7 updates in output object, got {}.".format(len(test_alpha2_dj_updates)))
        for row in test_alpha2_dj_updates:
            self.assertEqual(list(row.keys()), self.expected_output_columns, "Columns from output do not match expected.")
            self.assertIsInstance(row, dict, "Ouput object should be of type dict, got {}.".format(type(row)))
        self.assertEqual(test_alpha2_dj_updates[0], test_alpha2_dj_updates_expected, "Expected and observed outputs do not match.")
#3.) 
        test_alpha2_hn_updates = iso.updates[test_alpha2_hn] #Honduras
    
        test_alpha2_hn_updates_expected = {
            "Date Issued": "2011-12-15",
            "Edition/Newsletter": "Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf).",
            "Description of change in newsletter": "Comment taken into account and source list update.",
            "Code/Subdivision change": ""
            }

        self.assertEqual(len(test_alpha2_hn_updates), 2, 
            "Expected there to be 2 updates in output object, got {}.".format(len(test_alpha2_hn_updates)))
        for row in test_alpha2_hn_updates:
            self.assertEqual(list(row.keys()), self.expected_output_columns, "Columns from output do not match expected.")
            self.assertIsInstance(row, dict, "Ouput object should be of type dict, got {}.".format(type(row)))
        self.assertEqual(test_alpha2_hn_updates[0], test_alpha2_hn_updates_expected, "Expected and observed outputs do not match.")
#4.) 
        test_alpha2_fj_gh_gn_updates = iso.updates[test_alpha2_fj_gh_gn] #Fiji, Ghana, Guyana
    
        test_alpha2_fj_gh_gn_updates_expected_1 = {
            "Date Issued": "2016-11-22",
            "Edition/Newsletter": "Online Browsing Platform (OBP).",
            "Description of change in newsletter": "Reinstatement of provinces deleted due to a technical glitch.",
            "Code/Subdivision change": ""
            }
        test_alpha2_fj_gh_gn_updates_expected_2 = {
            "Date Issued": "2020-11-24",
            "Edition/Newsletter": "Online Browsing Platform (OBP).",
            "Description of change in newsletter": "Correction of the Code Source.",
            "Code/Subdivision change": ""
            }
        
        self.assertEqual(len(test_alpha2_fj_gh_gn_updates), 3, 
            "Expected there to be 3 updates in output object, got {}.".format(len(test_alpha2_fj_gh_gn_updates)))
        self.assertEqual(list(test_alpha2_fj_gh_gn_updates), ["FJ", "GH", "GN"])
        for code in test_alpha2_fj_gh_gn_updates:
            for row in test_alpha2_fj_gh_gn_updates[code]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, "Columns from output do not match expected.")
                self.assertIsInstance(row, dict, "Ouput object should be of type dict, got {}.".format(type(row)))
        self.assertEqual(test_alpha2_fj_gh_gn_updates["FJ"][0], test_alpha2_fj_gh_gn_updates_expected_1, "Expected and observed outputs do not match.")
        self.assertEqual(test_alpha2_fj_gh_gn_updates["GH"][0], test_alpha2_fj_gh_gn_updates_expected_2, "Expected and observed outputs do not match.")
#5.) 
        test_alpha2_yt_updates = iso.updates[test_alpha2_yt] #Mayotte

        test_alpha2_yt_updates_expected = {
            "Date Issued": "2022-11-29",
            "Edition/Newsletter": "Online Browsing Platform (OBP).",
            "Description of change in newsletter": "Modification of remark part 2.",
            "Code/Subdivision change": ""
            }
        
        self.assertEqual(len(test_alpha2_yt_updates), 2, 
            "Expected there to be 2 updates in output object, got {}.".format(len(test_alpha2_yt_updates)))
        for row in test_alpha2_yt_updates:
            self.assertEqual(list(row.keys()), self.expected_output_columns, "Columns from output do not match expected.")
            self.assertIsInstance(row, dict, "Ouput object should be of type dict, got {}.".format(type(row)))
        self.assertEqual(test_alpha2_yt_updates[0], test_alpha2_yt_updates_expected, "Expected and observed outputs do not match.")
#6.)     
        with self.assertRaises(ValueError):
            test_alpha2_error1_updates = iso.updates[test_alpha2_error_1] 
            test_alpha2_error_updates = iso.updates[test_alpha2_error_2] 
#7.)
        with self.assertRaises(TypeError):
            test_alpha2_error1_updates = iso.updates[test_alpha2_error_3] 
            test_alpha2_error1_updates = iso.updates[test_alpha2_error_4]

    def test_updates_year(self):
        """ Testing year function that returns all ISO 3166 updates for input year/years, year range or greater than/less than input year. """
        test_year_2019 = "2019"
        test_year_2003 = "2003"
        test_year_2000_2001_2002 = "2000,2001,2002"
        test_year_gt_2021 = ">2021"
        test_year_2004_2008 = "2004-2008"
        test_year_1999_2002 = "1999-2002"
        test_year_error1 = "1234" #ValueError
        test_year_error2 = "abcdef" #ValueError
        test_year_error3 = 12345 #TypeError
        test_year_error4 = True #TypeError
#1.)
        test_year_2019_updates = iso.updates.year(test_year_2019)
        test_year_2019_expected_keys = ["BN", "BQ", "CN", "ET", "GB", "GH", "GR", "IN", "IT", "LA", "LK", "MA", "MD", "ME", "MH", "MK", 
                                        "MR", "NO", "NP", "PK", "SB", "SL", "SY", "TZ"]

        self.assertEqual(len(test_year_2019_updates), 24, 
            "Expected 24 updates in output object, got {}.".format(len(test_year_2019_updates)))
        self.assertEqual(list(test_year_2019_updates),  test_year_2019_expected_keys, 
            "Expected and observed list of country codes do not match:\n{}".format(list(test_year_2019_updates)))
        for update in test_year_2019_updates:
            for row in range(0, len(test_year_2019_updates[update])):
                self.assertEqual(datetime.strptime(test_year_2019_updates[update][row]["Date Issued"], '%Y-%m-%d').year, 2019, 
                    "Expected year of updates output to be 2019, got {}.".format(test_year_2019_updates[update][row]["Date Issued"]))
#2.)
        test_year_2003_updates = iso.updates.year(test_year_2003)
        test_year_2003_expected_keys = ["BW", "CH", "CZ", "LY", "MY", "SN", "TN", "TZ", "UG", "VE"]

        self.assertEqual(len(test_year_2003_updates), 10, 
            "Expected 10 updates in output object, got {}.".format(len(test_year_2003_updates)))
        self.assertEqual(list(test_year_2003_updates),  test_year_2003_expected_keys, 
            "Expected and observed list of country codes do not match:\n{}".format(list(test_year_2003_updates)))
        for update in test_year_2003_updates:
            for row in range(0, len(test_year_2003_updates[update])):
                self.assertEqual(datetime.strptime(test_year_2003_updates[update][row]["Date Issued"], '%Y-%m-%d').year, 2003, 
                    "Expected year of updates output to be 2003, got {}.".format(test_year_2003_updates[update][row]["Date Issued"]))    
#3.) 
        test_year_2000_2001_2002_updates = iso.updates.year(test_year_2000_2001_2002)
        test_year_2000_2001_2002_expected_keys = ['AE', 'AL', 'AO', 'AZ', 'BD', 'BG', 'BI', 'BJ', 'BY', 'CA', 'CD', 'CN', 'CV', 'CZ', 
                                                  'DO', 'EC', 'ER', 'ES', 'ET', 'FR', 'GB', 'GE', 'GN', 'GT', 'HR', 'ID', 'IN', 'IR', 
                                                  'IT', 'KG', 'KH', 'KP', 'KR', 'KZ', 'LA', 'MA', 'MD', 'MO', 'MU', 'MW', 'NG', 'NI', 
                                                  'PH', 'PL', 'PS', 'RO', 'RU', 'SI', 'TJ', 'TL', 'TM', 'TR', 'TW', 'UG', 'UZ', 'VE', 
                                                  'VN', 'YE']
        
        self.assertEqual(len(test_year_2000_2001_2002_updates), 58, 
            "Expected 58 updates in output object, got {}.".format(len(test_year_2000_2001_2002_updates)))
        self.assertEqual(list(test_year_2000_2001_2002_updates),  test_year_2000_2001_2002_expected_keys, 
            "Expected and observed list of country codes do not match:\n{}".format(list(test_year_2000_2001_2002_updates)))
        for update in test_year_2000_2001_2002_updates:
            for row in range(0, len(test_year_2000_2001_2002_updates[update])):
                self.assertIn(datetime.strptime(test_year_2000_2001_2002_updates[update][row]["Date Issued"], '%Y-%m-%d').year, [2000,2001,2002], 
                    "Expected year of updates output to be either 2000, 2001 or 2002, got {}.".format(test_year_2000_2001_2002_updates[update][row]["Date Issued"]))    
#4.)
        test_year_gt_2021_updates = iso.updates.year(test_year_gt_2021)
        test_year_gt_2021_expected_keys = ["CI", "CN", "DZ", "ET", "FI", "FR", "GB", "GF", "GP", "GT", "HU", "ID", "IQ", "IS", "KH", "KP", 
                                           "KZ", "LT", "LV", "MQ", "MX", "NL", "NP", "NZ", "PA", "RE", "RU", "SI", "SS", "TR", "YT"]

        self.assertEqual(len(test_year_gt_2021_updates), 31, 
            "Expected 31 updates in output object, got {}.".format(len(test_year_gt_2021_updates)))
        self.assertEqual(list(test_year_gt_2021_updates),  test_year_gt_2021_expected_keys, 
            "Expected and observed list of country codes do not match:\n{}".format(list(test_year_gt_2021_updates)))
        for update in test_year_gt_2021_updates:
            for row in range(0, len(test_year_gt_2021_updates[update])):
                self.assertTrue(datetime.strptime(test_year_gt_2021_updates[update][row]["Date Issued"], '%Y-%m-%d').year >= 2021, 
                    "Expected year of updates output to be greater than or equal to 2021, got {}.".format(test_year_gt_2021_updates[update][row]["Date Issued"]))   
#5.)
        test_year_2004_2008_updates = iso.updates.year(test_year_2004_2008)

        self.assertEqual(len(test_year_2004_2008_updates), 73, 
            "Expected 73 updates in output object, got {}.".format(len(test_year_2004_2008_updates))) #**
        for update in test_year_2004_2008_updates:
            for row in range(0, len(test_year_2004_2008_updates[update])):
                self.assertTrue((datetime.strptime(test_year_2004_2008_updates[update][row]["Date Issued"], '%Y-%m-%d').year >= 2004) and \
                                (datetime.strptime(test_year_2004_2008_updates[update][row]["Date Issued"], '%Y-%m-%d').year <= 2008), 
                            "Expected year of updates output to be between 2004 and 2008, got {}.".format(test_year_2004_2008_updates[update][row]["Date Issued"])) 
#6.)
        test_year_1999_2002_updates = iso.updates.year(test_year_1999_2002)
        
        self.assertEqual(len(test_year_1999_2002_updates), 58, 
            "Expected 58 updates in output object, got {}.".format(len(test_year_1999_2002_updates)))
        for update in test_year_1999_2002_updates:
            for row in range(0, len(test_year_1999_2002_updates[update])):
                self.assertTrue((datetime.strptime(test_year_1999_2002_updates[update][row]["Date Issued"], '%Y-%m-%d').year >= 1999) and \
                                (datetime.strptime(test_year_1999_2002_updates[update][row]["Date Issued"], '%Y-%m-%d').year <= 2002), 
                            "Expected year of updates output to be between 1999 and 2002, got {}.".format(test_year_1999_2002_updates[update][row]["Date Issued"])) 
#7.)    
        with self.assertRaises(ValueError):
            test_year_error1_updates = iso.updates.year(test_year_error1)
            test_year_error2_updates = iso.updates.year(test_year_error2)
#8.)    
        with self.assertRaises(TypeError):
            test_year_error3_updates = iso.updates.year(test_year_error3)
            test_year_error4_updates = iso.updates.year(test_year_error4)
    
if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)