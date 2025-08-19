# try:
from iso3166_updates_export.get_updates_data import *
from iso3166_updates_export.driver import *
# except:
#     from ..iso3166_updates_export.get_updates_data import *
import iso3166
import requests
import pandas as pd
import warnings
from fake_useragent import UserAgent
from pandas.testing import assert_frame_equal
import unittest
unittest.TestLoader.sortTestMethodsUsing = None
warnings.simplefilter("ignore", ResourceWarning)

# @unittest.skip("Skipping get_updates_data tests.")
class ISO3166_Export_Updates_Get_Updates_Data_Tests(unittest.TestCase):
    """
    Test suite for testing the get_updates_data module in the ISO 3166
    updates export directory. The module exports the updates data from 
    the wiki and ISO data sources.

    Test Cases
    ==========
    test_data_sources_url:
        testing all of the data source urls, validating that each alpha code
        has the respective data sources.
    test_get_updates_df_wiki:
        testing function that exports the updates data from the respective
        wiki pages.
    test_get_updates_df_selenium:
        testing function that exports the updates data from the respective
        ISO pages.
    """
    def setUp(self):
        """ Initialise test variables, import json. """
        #initalise User-agent header for requests library 
        self.user_agent_header = UserAgent().random
        
        #base URL for ISO 3166-2 wiki and ISO pages
        self.wiki_base_url = "https://en.wikipedia.org/wiki/ISO_3166-2:"
        self.iso_base_url = "https://www.iso.org/obp/ui/en/#iso:code:3166:"
        
        #output columns from various functions
        self.expected_output_columns = ["Change", "Description of Change", "Date Issued", "Source"]

        #turn off tqdm progress bar functionality when running tests
        os.environ["TQDM_DISABLE"] = "1"

        #create Selenium Chromedriver instance for get_updates_df_selenium function
        self.driver = create_driver()

    @unittest.skip("Skipping to not overload Wiki or ISO servers on test suite run.")
    def test_data_sources_url(self):
        """ Test each ISO 3166-2 wiki URL and ISO endpoint to check valid status code 200 is returned. """
        #get list of alpha-2 codes from iso3166 library
        alpha2_codes = list(iso3166.countries_by_alpha2.keys())
#1.)
        #iterate over each ISO 3166 alpha-2 code, testing response code using request library for wiki and ISO pages
        for code in alpha2_codes:
            request = requests.get(self.wiki_base_url + code, headers={"headers": self.user_agent_header}, timeout=15)
            self.assertEqual(request.status_code, 200, f"Expected status code 200, got {request.status_code}.")

            request = requests.get(self.iso_base_url + code, headers={"headers": self.user_agent_header}, timeout=15)
            self.assertEqual(request.status_code, 200, f"Expected status code 200, got {request.status_code}.")

    # @unittest.skip("")
    def test_get_iso3166_updates_wiki_df(self): 
        """ Test function that pulls the updates data from the country's wiki page. """
        test_alpha_az = "AZ" #Azerbaijan 
        test_alpha_fi = "FI" #Finland
        test_alpha_gh = "gha" #Ghana
        test_alpha_ke = "KEN" #Kenya
        test_alpha_py = "600" #Paraguay {}
        test_alpha_error_1 = "ZZ"
        test_alpha_error_2 = "abcdef"
        test_alpha_error_3 = "AA"
        test_alpha_error_4 = 1234
        test_alpha_error_5 = False
        test_alpha_error_6 = ["AZ,FI,GH"]
#1.)
        az_updates_df = get_updates_df_wiki(test_alpha_az) #Azerbaijan
        az_expected_df = pd.DataFrame(
            [
                ['', 'Deletion of the romanization system; update List Source.', '2015-11-27', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AZ.'],
                ['Subdivisions added: AZ-KAN Kǝngǝrli. AZ-NV Naxçıvan (municipality). Subdivisions deleted: AZ-SS Şuşa. Codes: AZ-AB Əli Bayramlı -> AZ-SR Şirvan. AZ-DAV Dəvəçi -> AZ-SBN Şabran. AZ-XAN Xanlar -> AZ-GYG Göygöl.',
                'Alphabetical re-ordering, name change of administrative places, first level prefix addition and source list update.', '2011-12-13 (corrected 2011-12-15)',
                'Newsletter II-3 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf.'],
                ['Codes: Naxçıvan: AZ-MM -> AZ-NX.', 'Correction of one code and four spelling errors. Notification of the rayons belonging to the autonomous republic.',
                '2002-05-21', 'Newsletter I-2 - https://web.archive.org/web/20081218103157/http://www.iso.org/iso/iso_3166-2_newsletter_i-2_en.pdf.']
            ],
            columns=['Change', 'Description of Change', 'Date Issued', 'Source']
        )

        try:
            assert_frame_equal(az_updates_df, az_expected_df)
        except AssertionError as e:
            self.fail(f"Expected and actual dataframe of AZ updates data does not match:\n{az_updates_df}")
#2.)
        fi_updates_df = get_updates_df_wiki(test_alpha_fi) #Finland
        fi_expected_df = pd.DataFrame(
            [
                ['Name change: Satakunda -> Satakunta.', 'Change of spelling of FI-17; Update List Source.', '2022-11-29', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:FI.'],
                ['Subdivision layout: 6 provinces -> 19 regions.', 'Administrative re-organization, deletion of useless information and the region names in English and French, source list and source code update.',
                '2011-12-13 (corrected 2011-12-15)', "Newsletter II-3 - 'Changes in the list of subdivision names and code elements' - http://www.iso.org/iso/iso_3166-2_newsletter_ii-3_2011-12-13.pdf."]
            ],
            columns=['Change', 'Description of Change', 'Date Issued', 'Source']
        )

        try:
            assert_frame_equal(fi_updates_df, fi_expected_df)
        except AssertionError as e:
            self.fail(f"Expected and actual dataframe of FI updates data does not match:\n{fi_updates_df}")
#3.)
        gh_updates_df = get_updates_df_wiki(test_alpha_gh) #Ghana
        gh_expected_df = pd.DataFrame(
            [
                ['', 'Deletion of region GH-BA; Addition of regions GH-AF, GH-BE, GH-BO, GH-NE, GH-OT, GH-SV, GH-WN; Update List Source.', '2019-11-22', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:GH.'],
                ['', 'Update List Source.', '2015-11-27', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:GH.'],
                ['', 'Update List Source.', '2014-11-03', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:GH.']
            ],
            columns=['Change', 'Description of Change', 'Date Issued', 'Source']
        )

        try:
            assert_frame_equal(gh_updates_df, gh_expected_df)
        except AssertionError as e:
            self.fail(f"Expected and actual dataframe of GH updates data does not match:\n{gh_updates_df}")
#4.)
        ke_updates_df = get_updates_df_wiki(test_alpha_ke) #Kenya
        ke_expected_df = pd.DataFrame(
            [
                ['', 'Update Code Source.', '2016-11-15', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:KE.'],
                ['Deleted codes: KE-110, KE-200, KE-300, KE-400, KE-500, KE-600, KE-700, KE-800. Added codes: KE-01 through KE-47.', 'Delete provinces; add 47 counties; update List Source.', '2014-10-30', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:KE.'],
                ['', 'Update of the list source.', '2010-06-30', 'Newsletter II-2 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf.'],
                ['Codes: Western: KE-900 -> KE-800.', "Second edition of ISO 3166-2 (this change was not announced in a newsletter) - 'Statoid Newsletter January 2008' - http://www.statoids.com/n0801.html.", '2007-12-13', 'ISO 3166-2:2007 - http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=39718.']
            ],
            columns=['Change', 'Description of Change', 'Date Issued', 'Source']
        )       

        try:
            assert_frame_equal(ke_updates_df, ke_expected_df)
        except AssertionError as e:
            self.fail(f"Expected and actual dataframe of KE updates data does not match:\n{ke_updates_df}")
#5.)
        py_updates_df = get_updates_df_wiki(test_alpha_py) #Paraguay

        self.assertIsInstance(py_updates_df, pd.DataFrame, f"Output of function should be a dataframe, got {type(py_updates_df)}.")
        self.assertTrue(py_updates_df.empty, "Expected output dataframe to be empty.")
#6.)    
        with self.assertRaises(ValueError):
            get_updates_df_wiki(test_alpha_error_1)
            get_updates_df_wiki(test_alpha_error_2)
            get_updates_df_wiki(test_alpha_error_3)
#7.)
        with self.assertRaises(TypeError):
            get_updates_df_wiki(test_alpha_error_4)
            get_updates_df_wiki(test_alpha_error_5)
            get_updates_df_wiki(test_alpha_error_6)

    # @unittest.skip("Skipping to save having to go through process of installing Selenium and Chromedriver - tested locally.")
    # @patch('iso3166_updates_export.get_updates_data.sys.stdout', new_callable=io.StringIO)
    def test_get_iso3166_updates_selenium_df(self):
        """ Test function that pulls the updates data from the country's ISO page, using Selenium and Chromedriver. """
        test_alpha_bs = "BS" #Barbados
        test_alpha_cm = "CM" #Cameroon
        test_alpha_mn = "MNG" #Mongolia
        test_alpha_si = "svn" #Slovenia
        test_alpha_vu = "548" #Vanuatu
        test_alpha_error_1 = "abcdef"
        test_alpha_error_2 = "zz"
        test_alpha_error_3 = "muu"
        test_alpha_error_4 = ["FI,JA,JO"]
        test_alpha_error_5 = 1234
        test_alpha_error_6 = False
#1.)
        bs_updates_df, bs_remarks = get_updates_df_selenium(test_alpha_bs, driver=self.driver) #Barbados
        bs_expected_df = pd.DataFrame(
            [
                ['By a letter dated 10 April 2025, the Permanent Representative of The Bahamas confirmed the name of the country, which should be styled with a capital T.', '', '2025-07-22', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BS.'],
                ['Addition of island BS-NP; Addition of Remark; Update List Source.', '', '2018-11-26', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BS.'],
                ['Correction of NL II-2 for toponyms and typographical errors, one deletion and source list update.', '', '2011-12-13', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BS.'],
                ['Update of the administrative structure and of the list source.', '', '2010-06-30', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BS.']
            ],
            columns=['Change', 'Description of Change', 'Date Issued', 'Source']
        )   
        bs_expected_remarks = {'part1': 'Source UNTERM - United Nations', 'part2': 'The island of New Providence, where the capital Nassau is located, is administered directly by the national government', 'part3': '', 'part4': ''}

        try:
            assert_frame_equal(bs_updates_df, bs_expected_df)
        except AssertionError as e:
            self.fail(f"Expected and actual dataframe of BS updates data does not match:\n{bs_updates_df}")
        self.assertEqual(bs_remarks, bs_expected_remarks, f"Expected and observed remarks object for BS do not match:\n{bs_remarks}")
#2.)
        cm_updates_df, cm_remarks = get_updates_df_selenium(test_alpha_cm, driver=self.driver) #Cameroon
        cm_expected_df = pd.DataFrame(
            [
                ['Update List Source.', '', '2015-11-27', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CM.'],
                ['Update List Source.', '', '2014-11-03', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CM.']
            ],
            columns=['Change', 'Description of Change', 'Date Issued', 'Source']
        )    
        cm_expected_remarks = {'part1': '', 'part2': '', 'part3': '', 'part4': ''}

        try:
            assert_frame_equal(cm_updates_df, cm_expected_df)
        except AssertionError as e:
            self.fail(f"Expected and actual dataframe of CM updates data does not match:\n{cm_updates_df}")
        self.assertEqual(cm_remarks, cm_expected_remarks, f"Expected and observed remarks object for BS do not match:\n{cm_remarks}")
#3.)
        mn_updates_df, mn_remarks = get_updates_df_selenium(test_alpha_mn, driver=self.driver) #Mongolia
        mn_expected_df = pd.DataFrame(
            [
                ['Correction of the romanization system label.', '', '2018-11-26', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:MN.']
            ],
            columns=['Change', 'Description of Change', 'Date Issued', 'Source']
        )   
        mn_expected_remarks = {'part1': '', 'part2': '', 'part3': '', 'part4': ''}

        try:
            assert_frame_equal(mn_updates_df, mn_expected_df)
        except AssertionError as e:
            self.fail(f"Expected and actual dataframe of MN updates data does not match:\n{mn_updates_df}")
        self.assertEqual(mn_remarks, mn_expected_remarks, f"Expected and observed remarks object for BS do not match:\n{mn_remarks}")
#4.)
        si_updates_df, si_remarks = get_updates_df_selenium(test_alpha_si, driver=self.driver) #Slovenia
        si_expected_df = pd.DataFrame(
            [
                ['Change of spelling of SI-044, SI-197; Addition of category urban municipality; Change of category name from municipality to urban municipality for SI-011, SI-050, SI-052, SI-054, SI-061, SI-070, SI-080, SI-084, SI-085, SI-096, SI-112, SI-133; Update List Source.', '', '2022-11-29', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:SI.'],
                ["Addition of remark part 2.", '', '2021-11-25', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:SI.'],
                ['Correction of spelling for SI-065, SI-116, SI-169, SI-182, SI-204, SI-210; Deletion of asterisk from SI-212; Update List Source.', '', '2020-11-24', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:SI.'],
                ['Change of subdivision category from commune to municipality; addition of municipality SI-213.', '', '2016-11-15', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:SI.'],
                ['Add 1 commune SI-212; update List Source.', '', '2014-11-03', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:SI.'],
                ['Update of the administrative structure and languages and update of the list source.', '', '2010-06-30', 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:SI.']
            ],
            columns=['Change', 'Description of Change', 'Date Issued', 'Source']
        ) 
        si_expected_remarks = {'part1': '', 'part2': "The Italian and Hungarian languages are locally official in those municipalities where Italian or Hungarian national communities reside. For these municipalities the Hungarian or Italian subdivision name is provided under ‘local variation’", 
                               'part3': "Formerly part of Yougoslavia (YU, YUG, 891) before its split. See code element YUCS", 'part4': ''}
        
        try:
            assert_frame_equal(si_updates_df, si_expected_df)
        except AssertionError as e:
            self.fail(f"Expected and actual dataframe of SI updates data does not match:\n{si_updates_df}")
        self.assertEqual(si_remarks, si_expected_remarks, f"Expected and observed remarks object for BS do not match:\n{si_remarks}")
#5.)
        vu_updates_df, vn_remarks = get_updates_df_selenium(test_alpha_vu, driver=self.driver) #Vanuatu
        vn_expected_remarks = {}

        self.assertIsInstance(vu_updates_df, pd.DataFrame, f"Output of function should be a dataframe, got {type(vu_updates_df)}.")
        self.assertTrue(vu_updates_df.empty, "Expected output to be an empty dataframe.")
        self.assertEqual(vn_remarks, vn_expected_remarks, f"Expected and observed remarks object for VN do not match:\n{vn_remarks}")
#6.)
        with self.assertRaises(ValueError):
            get_updates_df_selenium(test_alpha_error_1, driver=self.driver)
            get_updates_df_selenium(test_alpha_error_2, driver=self.driver)
            get_updates_df_selenium(test_alpha_error_3, driver=self.driver)
#7.)
        with self.assertRaises(TypeError):        
            get_updates_df_selenium(test_alpha_error_4, driver=self.driver)
            get_updates_df_selenium(test_alpha_error_5, driver=self.driver)
            get_updates_df_selenium(test_alpha_error_6, driver=self.driver)
#8.)
        with self.assertRaises(RuntimeError):        
            get_updates_df_selenium(test_alpha_bs, driver=None)
            get_updates_df_selenium(test_alpha_cm)

if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)