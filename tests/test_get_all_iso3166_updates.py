try:
    from get_all_iso3166_updates import *
except:
    from ..get_all_iso3166_updates import *
import iso3166
import getpass
import requests
import json
import shutil
import os
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import platform
from importlib.metadata import metadata
import unittest
unittest.TestLoader.sortTestMethodsUsing = None

# @unittest.skip("Skipping tests for get_all_iso3166_updates.py script to not overload servers and test runners.")
class ISO3166_Get_Updates_Tests(unittest.TestCase):
    """
    Test suite for testing the get_all_iso3166_updates script that gathers and parses all ISO 3166-2 
    updates from the various data sources.
    
    Test Cases
    ==========
    test_data_sources_url:
        testing that each ISO 3166-1 alpha-2 country code has a corresponding wiki page and ISO page 
        which is the data source for the updates.
    test_table_to_array:
        testing table_to_array() function that converts a html table into a 2 dimensional array. 
    test_get_updates_wiki_df:
        testing get_updates_df_wiki() function that converts the 2 dimensional converted html table array 
        from the country's wiki page into a Pandas DataFrame.
    test_get_updates_selenium_df:
        testing get_updates_df_selenium() function that converts the 2 dimensional converted html table array 
        from the country's ISO page using Selenium into a Pandas DataFrame.
    test_get_updates_alpha:
        testing main get_updates() function that gets all the ISO 3166 updates for the input country/countries, 
        using a variety of ISO 3166-1 alpha codes parameter values.
    test_get_updates_year:
        testing main get_updates() function that gets all the ISO 3166 updates for the input country/countries, 
        using a variety of year parameter values.
    test_get_updates_alpha_year:
        testing main get_updates() function that gets all the ISO 3166 updates for the input country/countries, 
        using a variety of ISO 3166-1 alpha codes and year parameter values.
    """
    def setUp(self):
        """ Initialise test variables, import json. """
        #initalise User-agent header for requests library 
        self.__version__ = metadata('iso3166_updates')['version']
        self.user_agent_header = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(self.__version__,
                                            'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}
        
        #base URL for ISO 3166-2 wiki and ISO pages
        self.wiki_base_url = "https://en.wikipedia.org/wiki/ISO_3166-2:"
        self.iso_base_url = "https://www.iso.org/obp/ui/en/#iso:code:3166:"
        
        #importing all updates data from JSON, open iso3166-updates json file and load it into class variable, loading in a JSON is different in Windows & Unix/Linux systems
        if (platform.system() != "Windows"):
            with open("iso3166-updates.json") as input_json:
                self.iso3166_json = json.load(input_json)
        else:
            with open("iso3166-updates.json", encoding="utf-8") as input_json:
                self.iso3166_json = json.loads(input_json.read())

        #temp filename & dir exports
        self.export_filename = "test_iso3166_updates"
        self.export_folder = "temp_test_dir"
        
        #output columns from various functions
        self.expected_output_columns = ["Code/Subdivision Change", "Description of Change", "Date Issued", "Edition/Newsletter"]

        #create temp dir to store any function outputs
        if not (os.path.isdir(self.export_folder)):
            os.mkdir(self.export_folder)

        #turn off tqdm progress bar functionality when running tests
        os.environ["TQDM_DISABLE"] = "1"

    @unittest.skip("Skipping to not overload Wiki or ISO servers on test suite run.")
    def test_data_sources_url(self):
        """ Test each ISO 3166-2 wiki URL and ISO endpoint to check valid status code 200 is returned. """
        #get list of alpha-2 codes from iso3166 library
        alpha2_codes = list(iso3166.countries_by_alpha2.keys())

        #iterate over each ISO 3166 alpha-2 code, testing response code using request library for wiki and ISO pages
        for code in alpha2_codes:
            request = requests.get(self.wiki_base_url + code, headers=self.user_agent_header)
            self.assertEqual(request.status_code, 200, 
                "Expected status code 200, got {}.".format(request.status_code))   

            request = requests.get(self.iso_base_url + code, headers=self.user_agent_header)
            self.assertEqual(request.status_code, 200, 
                "Expected status code 200, got {}.".format(request.status_code))   

    # @unittest.skip("")
    def test_table_to_array(self):
        """ Test function that parses updates html table into 2D array of headers & rows. """
        test_alpha2_ba = "BA" #Bosnia
        test_alpha2_eg = "EG" #Egypt
        test_alpha2_qa = "QA" #Qatar
        test_alpha2_rs = "RS" #Serbia
        test_alpha2_br = "BR" #Brazil, no listed changes/updates
        test_alpha2_pt = "PT" #Portugal, no listed changes/updates
        test_alpha2_error_1 = 12345 #should raise type error
        test_alpha2_error_2 = "abcdefg" #should raise type error
        test_alpha2_error_3 = False #should raise type error

        #get html content from wiki of ISO page, convert html content into BS4 object,
        #...get Changes Section/Heading from soup, get table element from section
#1.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_ba).content, "html.parser") #Bosnia
        table_html = soup.find("span", {"id": "Changes"}).findNext('table')
        ba_table = table_to_array(table_html)

        ba_expected_output1 = ['ISO 3166-2:2007 (http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=39718).', 
            '2007-12-13.', 'Second edition of ISO 3166-2 (this change was not announced in a newsletter)[1] (#cite_note-2).', 
            'Subdivisions added: 10 cantons.']
        ba_expected_output2 = ['Newsletter II-2 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf).', 
            '2010-06-30.', 'Addition of the country code prefix as the first code element, addition of names in administrative languages, \
                update of the administrative structure and of the list source.', 'Subdivisions added: BA-BRC Brčko distrikt.']
        
        #removing any whitespace or newlines from expected and test outputs
        ba_expected_output1 = [entry.replace(" ", "") for entry in ba_expected_output1]
        ba_expected_output2 = [entry.replace(" ", "") for entry in ba_expected_output2]
        ba_test_output1 = [entry.replace(" ", "") for entry in ba_table[1]]
        ba_test_output2 = [entry.replace(" ", "") for entry in ba_table[2]]

        self.assertIsInstance(ba_table, list, "Expected output table to be of type list, got {}.".format(type(ba_table)))
        self.assertEqual(len(ba_table), 3, "Expected there to be 3 elements in output table, got {}.".format(len(ba_table)))
        self.assertListEqual(ba_table[0], ['Edition/Newsletter', 'Date issued', 'Description of change in newsletter', 'Code/Subdivision change'], 
            "Expected columns/headers in observed and expected output to match.")
        self.assertEqual(ba_test_output1, ba_expected_output1, f"Expected and observed outputs do not match:\n{ba_test_output1}.")
        self.assertEqual(ba_test_output2, ba_expected_output2, f"Expected and observed outputs do not match:\n{ba_expected_output2}.")
#2.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_eg).content, "html.parser") #Egypt
        table_html = soup.find("span", {"id": "Changes"}).findNext('table')
        eg_table = table_to_array(table_html)

        eg_expected_output1 = ['ISO 3166-2:2007 (http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=39718).', 
            '2007-12-13.', 'Second edition of ISO 3166-2 (this change was not announced in a newsletter)[1] (#cite_note-3).', 
            'Subdivision added: EG-LX Al Uqşur.']
        eg_expected_output2 = ['Newsletter II-2 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf).', 
            '2010-06-30.', 'Update of the administrative structure and of the list source.', 'Subdivisions added: EG-SU As Sādis min Uktūbar EG-HU Ḩulwān.']

        #removing any whitespace or newlines from expected and test outputs
        eg_expected_output1 = [entry.replace(" ", "") for entry in eg_expected_output1]
        eg_expected_output2 = [entry.replace(" ", "") for entry in eg_expected_output2]
        eg_test_output1 = [entry.replace(" ", "") for entry in eg_table[1]]
        eg_test_output2 = [entry.replace(" ", "") for entry in eg_table[2]]

        self.assertIsInstance(eg_table, list, "Expected output table to be of type list, got {}.".format(type(eg_table)))
        self.assertEqual(len(eg_table), 3, "Expected there to be 2 elements in output table, got {}.".format(len(eg_table)))
        self.assertListEqual(eg_table[0], ['Edition/Newsletter', 'Date issued', 'Description of change', 'Code/Subdivision change'], 
            "Expected columns/headers in observed and expected output to match.")
        self.assertEqual(eg_test_output1, eg_expected_output1, f"Expected and observed outputs do not match:\n{eg_test_output1}.")
        self.assertEqual(eg_test_output2, eg_expected_output2, f"Expected and observed outputs do not match:\n{eg_test_output2}")
#3.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_qa).content, "html.parser") #Qatar
        table_html = soup.find("span", {"id": "Changes"}).findNext('table')
        qa_table = table_to_array(table_html)

        qa_expected_output = ['Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf).',
                        '2011-12-13 (corrected 2011-12-15).',
                        'Update resulting from the addition of names in administrative languages, and update of the administrative structure and of the list source.',
                        'Subdivisions added: QA-ZA Az̧ Za̧`āyin Subdivisions deleted: QA-GH Al Ghuwayrīyah QA-JU Al Jumaylīyah QA-JB Jarīyān al Bāţnah.']

        #removing any whitespace or newlines from expected and test outputs
        qa_expected_output = [entry.replace(" ", "") for entry in qa_expected_output]
        qa_test_output = [entry.replace(" ", "") for entry in qa_table[1]]

        self.assertIsInstance(qa_table, list, "Expected output table to be of type list, got {}.".format(type(qa_table)))
        self.assertEqual(len(qa_table), 2, "Expected there to be 2 elements in output table, got {}.".format(len(qa_table)))
        self.assertListEqual(qa_table[0], ['Newsletter', 'Date issued', 'Description of change in newsletter', 'Code/Subdivision change'], 
            "Expected columns/headers in observed and expected output to match.")
        self.assertEqual(qa_test_output, qa_expected_output, f"Expected and observed outputs do not match:\n{qa_test_output}")
#4.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_rs).content, "html.parser") #Serbia
        table_html = soup.find("span", {"id": "Changes"}).findNext('table')
        rs_table = table_to_array(table_html)

        rs_expected_output1 = ['Newsletter I-8 (https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf).', 
            '2007-04-17.', 'Addition of a new country (in accordance with ISO 3166-1 Newsletter V-12).', 'Subdivisions added: 1 city, 2 autonomous republics, 29 districts.']
        rs_expected_output2 = ['Newsletter II-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-1_corrected_2010-02-19.pdf).', 
            '2010-02-03 (corrected 2010-02-19).', 'Addition of the country code prefix as the first code element, administrative update.', '']
        
        #removing any whitespace or newlines from expected and test outputs
        rs_expected_output1 = [entry.replace(" ", "") for entry in rs_expected_output1]
        rs_expected_output2 = [entry.replace(" ", "") for entry in rs_expected_output2]
        rs_test_output1 = [entry.replace(" ", "") for entry in rs_table[1]]
        rs_test_output2 = [entry.replace(" ", "") for entry in rs_table[2]]

        self.assertIsInstance(rs_table, list, "Expected output table to be of type list, got {}.".format(type(rs_table)))
        self.assertEqual(len(rs_table), 3, "Expected there to be 2 elements in output table, got {}.".format(len(rs_table)))
        self.assertListEqual(rs_table[0], ['Newsletter','Date issued','Description of change in newsletter','Code/Subdivision change'], 
            "Expected columns/headers in observed and expected output to match.")
        self.assertEqual(rs_test_output1, rs_expected_output1, f"Expected and observed outputs do not match:\n{rs_test_output1}.")
        self.assertEqual(rs_test_output2, rs_expected_output2, f"Expected and observed outputs do not match:\n{rs_test_output2}")
#5.)    
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_br).content, "html.parser") #Brazil
        table_html = soup.find("span", {"id": "Changes"})
        br_table = table_to_array(table_html)

        self.assertIsNone(table_html, "Table should be none as no listed changes/updates on wiki.")
        self.assertEqual(br_table, [], "Output from function should be empty array when input param is None.")
#6.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_pt).content, "html.parser") #Portugal
        table_html = soup.find("span", {"id": "Changes"})
        test_table = table_to_array(table_html)

        self.assertIsNone(table_html, "Table should be none as invalid alpha-2 code input.")
        self.assertEqual(test_table, [], "Output from function should be empty array when input param is None.")
#7.)
        with self.assertRaises(TypeError):
           table_to_array(test_alpha2_error_1)
           table_to_array(test_alpha2_error_2)
           table_to_array(test_alpha2_error_3)

    # @unittest.skip("")
    def test_get_updates_wiki_df(self): 
        """ Test function that pulls the updates data from the country's wiki page. """
        test_alpha2_az = "AZ" #Azerbaijan 
        test_alpha2_fi = "FI" #Finland
        test_alpha2_gh = "GH" #Ghana
        test_alpha2_ke = "KE" #Kenya
        test_alpha2_sn = "SN" #Senegal
        test_alpha2_error_1 = "ZZ"
        test_alpha2_error_2 = "abcdef"
        test_alpha2_error_3 = 1234
        test_alpha2_error_4 = False
        expected_output_columns = ["Code/Subdivision Change", "Description of Change", "Date Issued", "Corrected Date Issued", "Edition/Newsletter"]
#1.)
        #get updates dataframe using 2 letter alpha-2 code
        az_updates_df = get_updates_df_wiki(test_alpha2_az) #Azerbaijan
        
        az_expected_output1 = ['Codes: Naxçıvan: AZ-MM → AZ-NX.', 'Correction of one code and four spelling errors. Notification of the rayons belonging to the autonomous republic.', '2002-05-21', '', 
                               'Newsletter I-2 (https://web.archive.org/web/20081218103157/http://www.iso.org/iso/iso_3166-2_newsletter_i-2_en.pdf).']
        az_expected_output2 = ['Subdivisions added: AZ-KAN Kǝngǝrli AZ-NV Naxçıvan (municipality) Subdivisions deleted: AZ-SS Şuşa Codes: AZ-AB Əli Bayramlı → AZ-SR Şirvan AZ-DAV Dəvəçi \
            → AZ-SBN Şabran AZ-XAN Xanlar → AZ-GYG Göygöl.', 'Alphabetical re-ordering, name change of administrative places, first level prefix addition and source list update.', '2011-12-13', 
            '(corrected 2011-12-15)', 'Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf).']

        #removing any whitespace or newlines from expected and test outputs
        az_expected_output1 = [entry.replace(" ", "") for entry in az_expected_output1]
        az_expected_output2 = [entry.replace(" ", "") for entry in az_expected_output2]
        az_updates_df_output1 = [entry.replace(" ", "") for entry in az_updates_df.iloc[0].tolist()]
        az_updates_df_output2 = [entry.replace(" ", "") for entry in az_updates_df.iloc[1].tolist()]

        self.assertIsInstance(az_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(az_updates_df)))
        self.assertEqual(len(az_updates_df), 3, "Expected there to be 3 elements in output dataframe, got {}.".format(len(az_updates_df)))
        self.assertEqual(expected_output_columns, list(az_updates_df.columns), "Columns/headers of dataframe do not match:\n{}".format(list(az_updates_df.columns)))
        self.assertEqual(az_updates_df_output1, az_expected_output1, "Row value for column does not match expected output.")
        self.assertEqual(az_updates_df_output2, az_expected_output2, "Row value for column does not match expected output.")
#2.)
        #get updates dataframe using 2 letter alpha-2 code
        fi_updates_df = get_updates_df_wiki(test_alpha2_fi) #Finland

        fi_expected_output1 = ['Subdivision layout: 6 provinces (see below) → 19 regions.', 'Administrative re-organization, deletion of useless \
                               information and the region names in English and French, source list and source code update.', '2011-12-13', 
                               '(corrected 2011-12-15)', 'Newsletter II-3[1].']
        fi_expected_output2 = ['Name change: Satakunda → Satakunta.', 'Change of spelling of FI-17; Update List Source.', '2022-11-29', '', 
                               'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:FI).']

        #removing any whitespace or newlines from expected and test outputs
        fi_expected_output1 = [entry.replace(" ", "") for entry in fi_expected_output1]
        fi_expected_output2 = [entry.replace(" ", "") for entry in fi_expected_output2]
        fi_updates_df_output1 = [entry.replace(" ", "") for entry in fi_updates_df.iloc[0].tolist()]
        fi_updates_df_output2 = [entry.replace(" ", "") for entry in fi_updates_df.iloc[1].tolist()]

        self.assertIsInstance(fi_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(fi_updates_df)))
        self.assertEqual(len(fi_updates_df), 2, "Expected there to be 2 elements in output dataframe, got {}.".format(len(fi_updates_df)))
        self.assertEqual(expected_output_columns, list(fi_updates_df.columns), "Columns/headers of dataframe do not match:\n{}".format(list(fi_updates_df.columns)))
        self.assertEqual(fi_updates_df_output1, fi_expected_output1, "Row value for column does not match expected output.")
        self.assertEqual(fi_updates_df_output2, fi_expected_output2, "Row value for column does not match expected output.")
#3.)
        #get updates dataframe using 2 letter alpha-2 code
        gh_updates_df = get_updates_df_wiki(test_alpha2_gh) #Ghana

        gh_expected_output1 = ['', 'Deletion of region GH-BA; Addition of regions GH-AF, GH-BE, GH-BO, GH-NE, GH-OT, GH-SV, GH-WN; Update List Source.', '2019-11-22', '', 
                               'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:GH).']
        gh_expected_output2 = ['', 'Update List Source.', '2015-11-27', '', 'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:GH).']
        gh_expected_output3 = ['', 'Update List Source.', '2014-11-03', '', 'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:GH).']

        #removing any whitespace or newlines from expected and test outputs
        gh_expected_output1 = [entry.replace(" ", "") for entry in gh_expected_output1]
        gh_expected_output2 = [entry.replace(" ", "") for entry in gh_expected_output2]
        gh_expected_output3 = [entry.replace(" ", "") for entry in gh_expected_output3]
        gh_updates_df_output1 = [entry.replace(" ", "") for entry in gh_updates_df.iloc[0].tolist()]
        gh_updates_df_output2 = [entry.replace(" ", "") for entry in gh_updates_df.iloc[1].tolist()]
        gh_updates_df_output3 = [entry.replace(" ", "") for entry in gh_updates_df.iloc[2].tolist()]

        self.assertIsInstance(gh_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(gh_updates_df)))
        self.assertEqual(len(gh_updates_df), 3, "Expected there to be 3 elements in output dataframe, got {}.".format(len(gh_updates_df)))
        self.assertEqual(expected_output_columns, list(gh_updates_df.columns), "Columns/headers of dataframe do not match:\n{}".format(list(gh_updates_df.columns)))
        self.assertEqual(gh_updates_df_output1, gh_expected_output1, "Row value for column does not match expected output.")
        self.assertEqual(gh_updates_df_output2, gh_expected_output2, "Row value for column does not match expected output.")
        self.assertEqual(gh_updates_df_output3, gh_expected_output3, "Row value for column does not match expected output.")
#4.)
        #get updates dataframe using 2 letter alpha-2 code
        ke_updates_df = get_updates_df_wiki(test_alpha2_ke) #Kenya

        ke_expected_output1 = ['Codes: Western: KE-900 → KE-800.', 'Second edition of ISO 3166-2 (this change was not announced in a newsletter)[1] (#cite_note-1).', '2007-12-13', '', 
                               'ISO 3166-2:2007 (http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=39718).']
        ke_expected_output2 = ['', 'Update of the list source.', '2010-06-30', '', 'Newsletter II-2 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf).']
        ke_expected_output3 = ['Deleted codes:KE-110, KE-200, KE-300, KE-400, KE-500, KE-600, KE-700, KE-800Added codes:KE-01 through KE-47.', 'Delete provinces; add 47 counties; update List Source.', 
                               '2014-10-30', '', 'Online BrowsingPlatform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:KE).']
       
        #removing any whitespace or newlines from expected and test outputs
        ke_expected_output1 = [entry.replace(" ", "") for entry in ke_expected_output1]
        ke_expected_output2 = [entry.replace(" ", "") for entry in ke_expected_output2]
        ke_expected_output3 = [entry.replace(" ", "") for entry in ke_expected_output3]
        ke_updates_df_output1 = [entry.replace(" ", "") for entry in ke_updates_df.iloc[0].tolist()]
        ke_updates_df_output2 = [entry.replace(" ", "") for entry in ke_updates_df.iloc[1].tolist()] 
        ke_updates_df_output3 = [entry.replace(" ", "") for entry in ke_updates_df.iloc[2].tolist()]

        self.assertIsInstance(ke_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(ke_updates_df)))
        self.assertEqual(len(ke_updates_df), 4, "Expected there to be 4 elements in output dataframe, got {}.".format(len(ke_updates_df)))
        self.assertEqual(expected_output_columns, list(ke_updates_df.columns), "Columns/headers of dataframe do not match:\n{}".format(list(ke_updates_df.columns)))
        self.assertEqual(ke_updates_df_output1, ke_expected_output1, "Row value for column does not match expected output.")
        self.assertEqual(ke_updates_df_output2, ke_expected_output2, "Row value for column does not match expected output.")
        self.assertEqual(ke_updates_df_output3, ke_expected_output3, "Row value for column does not match expected output.")
#5.)
        #get updates dataframe using 2 letter alpha-2 code
        sn_updates_df = get_updates_df_wiki(test_alpha2_sn) #Senegal

        sn_expected_output1 = ['Subdivisions added: SN-MT Matam.', 'Addition of one new region. List source updated.', '2003-09-05', '', 
                               'Newsletter I-5 (https://web.archive.org/web/20081218103244/http://www.iso.org/iso/iso_3166-2_newsletter_i-5_en.pdf).']
        sn_expected_output2 = ['Subdivisions added: SN-KA Kaffrine SN-KE Kédougou SN-SE Sédhiou.', 'Update of the administrative structure and languages and update of the list source.', 
                               '2010-06-30', '', 'Newsletter II-2 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf).']
        
        #removing any whitespace or newlines from expected and test outputs
        sn_expected_output1 = [entry.replace(" ", "") for entry in sn_expected_output1]
        sn_expected_output2 = [entry.replace(" ", "") for entry in sn_expected_output2]
        sn_updates_df_output1 = [entry.replace(" ", "") for entry in sn_updates_df.iloc[0].tolist()]
        sn_updates_df_output2 = [entry.replace(" ", "") for entry in sn_updates_df.iloc[1].tolist()]

        self.assertIsInstance(sn_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(sn_updates_df)))
        self.assertEqual(len(sn_updates_df), 2, "Expected there to be 2 elements in output dataframe, got {}.".format(len(sn_updates_df)))
        self.assertEqual(expected_output_columns, list(sn_updates_df.columns), "Columns/headers of dataframe do not match:\n{}".format(list(sn_updates_df.columns)))
        self.assertEqual(sn_updates_df_output1, sn_expected_output1, "Row value for column does not match expected output.")
        self.assertEqual(sn_updates_df_output2, sn_expected_output2, "Row value for column does not match expected output.")
#6.)    
        with self.assertRaises(requests.exceptions.HTTPError):
            get_updates_df_wiki(test_alpha2_error_1)
            get_updates_df_wiki(test_alpha2_error_2)
#7.)
        with self.assertRaises(TypeError):
            get_updates_df_wiki(test_alpha2_error_3)
            get_updates_df_wiki(test_alpha2_error_4)

    # @unittest.skip("Skipping to save having to go through process of installing Selenium and Chromedriver - tested locally.")
    def test_get_updates_selenium_df(self):
        """ Test function that pulls the updates data from the country's ISO page, using Selenium and Chromedriver. """
        test_alpha2_bs = "BS" #Barbados
        test_alpha2_cm = "CM" #Cameroon
        test_alpha2_mn = "MN" #Mongolia
        test_alpha2_sk = "SK" #Slovakia
        test_alpha2_vu = "VU" #Vanuatu
        test_alpha2_error_1 = "abcdef"
        test_alpha2_error_2 = 1234
        test_alpha2_error_3 = False
        expected_output_columns = ['Code/Subdivision Change', 'Description of Change', 'Date Issued', 'Corrected Date Issued', 'Edition/Newsletter']
#1.)
        bs_updates_df = get_updates_df_selenium(test_alpha2_bs) #Barbados

        bs_expected_output1 = ['', 'Addition of island BS-NP; Addition of Remark; Update List Source.', '2018-11-26', '', 'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:BS).']
        bs_expected_output2 = ['', 'Correction of NL II-2 for toponyms and typographical errors, one deletion and source list update.', '2011-12-13', '', 
                               'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:BS).']

        #removing any whitespace or newlines from expected and test outputs
        bs_expected_output1 = [entry.replace(" ", "") for entry in bs_expected_output1]
        bs_expected_output2 = [entry.replace(" ", "") for entry in bs_expected_output2]
        bs_updates_df_output1 = [entry.replace(" ", "") for entry in bs_updates_df.iloc[0].tolist()]
        bs_updates_df_output2 = [entry.replace(" ", "") for entry in bs_updates_df.iloc[1].tolist()]

        self.assertIsInstance(bs_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(bs_updates_df)))
        self.assertEqual(len(bs_updates_df), 3, "Expected there to be 3 elements in output dataframe, got {}.".format(len(bs_updates_df)))
        self.assertEqual(expected_output_columns, list(bs_updates_df.columns), "Columns/headers of dataframe do not match:\n{}".format(list(bs_updates_df.columns)))
        self.assertEqual(bs_updates_df_output1, bs_expected_output1, "Row value for column does not match expected output.")
        self.assertEqual(bs_updates_df_output2, bs_expected_output2, "Row value for column does not match expected output.")
#2.)
        cm_updates_df = get_updates_df_selenium(test_alpha2_cm) #Cameroon

        cm_expected_output1 = ['', 'Update List Source.', '2015-11-27', '', 'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:CM).']
        cm_expected_output2 = ['', 'Update List Source.', '2014-11-03', '', 'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:CM).']

        #removing any whitespace or newlines from expected and test outputs
        cm_expected_output1 = [entry.replace(" ", "") for entry in cm_expected_output1]
        cm_expected_output2 = [entry.replace(" ", "") for entry in cm_expected_output2]
        cm_updates_df_output1 = [entry.replace(" ", "") for entry in cm_updates_df.iloc[0].tolist()]
        cm_updates_df_output2 = [entry.replace(" ", "") for entry in cm_updates_df.iloc[1].tolist()]

        self.assertIsInstance(cm_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(cm_updates_df)))
        self.assertEqual(len(cm_updates_df), 2, "Expected there to be 2 elements in output dataframe, got {}.".format(len(cm_updates_df)))
        self.assertEqual(expected_output_columns, list(cm_updates_df.columns), "Columns/headers of dataframe do not match:\n{}".format(list(cm_updates_df.columns)))
        self.assertEqual(cm_updates_df_output1, cm_expected_output1, "Row value for column does not match expected output.")
        self.assertEqual(cm_updates_df_output2, cm_expected_output2, "Row value for column does not match expected output.")
#3.)
        mn_updates_df = get_updates_df_selenium(test_alpha2_mn) #Mongolia

        mn_expected_output1 = ['', 'Correction of the romanization system label.', '2018-11-26', '', 'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:MN).']

        #removing any whitespace or newlines from expected and test outputs
        mn_expected_output1 = [entry.replace(" ", "") for entry in mn_expected_output1]
        mn_updates_df_output1 = [entry.replace(" ", "") for entry in mn_updates_df.iloc[0].tolist()]

        self.assertIsInstance(mn_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(mn_updates_df)))
        self.assertEqual(len(mn_updates_df), 1, "Expected there to be 1 element in output dataframe, got {}.".format(len(mn_updates_df)))
        self.assertEqual(expected_output_columns, list(mn_updates_df.columns), "Columns/headers of dataframe do not match:\n{}".format(list(mn_updates_df.columns)))
        self.assertEqual(mn_updates_df_output1, mn_expected_output1, "Row value for column does not match expected output.")
#4.)
        sk_updates_df = get_updates_df_selenium(test_alpha2_sk) #Slovakia

        self.assertIsInstance(sk_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(sk_updates_df)))
        self.assertTrue(sk_updates_df.empty, "Expected output to be an empty dataframe.")
#5.)
        vu_updates_df = get_updates_df_selenium(test_alpha2_vu) #Vanuatu

        self.assertIsInstance(vu_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(vu_updates_df)))
        self.assertTrue(vu_updates_df.empty, "Expected output to be an empty dataframe.")
#6.)
        with self.assertRaises(ValueError):
            get_updates_df_selenium(test_alpha2_error_1)
            get_updates_df_selenium(test_alpha2_error_2)
            get_updates_df_selenium(test_alpha2_error_3)

    # @unittest.skip("")
    def test_get_updates_alpha(self):
        """ Testing main updates function that gets the updates and exports to json/csv, using
            a variety of ISO 3166-1 alpha country code input parameter values. """
        test_alpha_au = "AU" #Australia
        test_alpha_cv = "CV" #Cabo Verde
        test_alpha_id = "IDN" #Indonesia
        test_alpha_pt = "620" #Portugal ({})
        test_alpha_bf_ca_gu_ie_je_str = "BF, CAN, GUM, 372, 832" #Burkina Faso, Canada, Guam, Ireland, Jersey - concat_updates=False
        test_alpha_error_1 = 12345 #should raise type error
        test_alpha_error_2 = False #should raise type error
        test_alpha_error_3 = "XYZ" #should raise value error
        test_alpha_error_4 = "invalid_alpha_code" #should raise value error
#1.) 
        test_alpha_au_updates = get_updates(alpha_codes=test_alpha_au, export_filename=self.export_filename, export_folder=self.export_folder, 
                concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=True)   #Australia
    
        test_au_expected = {
            "Description of Change": "",
            "Code/Subdivision Change": "Update List Source; update Code Source.",
            "Date Issued": "2016-11-15",
            "Edition/Newsletter": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:AU)."
            }
        
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-AU.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-AU.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(list(test_alpha_au_updates), ['AU'], 
            "Expected AU key to be in updates output object:\n{}".format(list(test_alpha_au_updates))) 
        self.assertEqual(len(list(test_alpha_au_updates["AU"])), 3, 
            "Expected there to be 3 output objects in output object, got {}.".format(len(list(test_alpha_au_updates))))
        for row in test_alpha_au_updates["AU"]:
            self.assertEqual(list(row.keys()), self.expected_output_columns, "Columns from output do not match expected.")
            self.assertIsInstance(row, dict, "Ouput object should be of type dict, got {}.".format(type(row)))
        self.assertEqual(test_alpha_au_updates['AU'][0], test_au_expected, f"Expected and observed outputs do not match:\n{test_alpha_au_updates['AU'][0]}.")

        test_au_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "-AU.csv")).fillna("")
        self.assertEqual(list(test_au_iso3166_csv.columns), self.expected_output_columns, 
            "Observed and expected output columns do not match:\n{}.".format(list(test_au_iso3166_csv.columns)))
        self.assertEqual(len(test_au_iso3166_csv), 3, 
            "Expected there to be 3 output objects in csv, got {}.".format(len(list(test_au_iso3166_csv))))
        self.assertEqual(test_au_iso3166_csv.head(1).to_dict(orient='records')[0], test_au_expected, 
            f"Expected and observed outputs do not match:\n{test_au_iso3166_csv.head(1).to_dict(orient='records')[0]}")
#2.)  
        test_alpha_cv_updates = get_updates(test_alpha_cv, export_filename=self.export_filename, export_folder=self.export_folder, 
                concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=True)   #Cabo Verde
        
        test_cv_expected = {
            'Code/Subdivision Change': 'Correction of the Code Source.', 
            'Description of Change': '', 
            'Date Issued': '2020-11-24', 
            'Edition/Newsletter': 'Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:CV).'
            }
        
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-CV.csv")),
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-CV.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(list(test_alpha_cv_updates), ['CV'],
            "Expected CV key to be in updates output object:\n{}.".format(list(test_alpha_cv_updates))) 
        self.assertEqual(len(list(test_alpha_cv_updates["CV"])), 6, 
            "Expected there to be 6 output objects in output object, got {}.".format(len(list(test_alpha_cv_updates))))
        for row in test_alpha_cv_updates["CV"]:
            self.assertEqual(list(row.keys()), self.expected_output_columns, f"Columns from output do not match expected:\n{list(row.keys())}")
            self.assertIsInstance(row, dict, "Ouput object should be of type dict, got {}.".format(type(row)))
        self.assertEqual(test_alpha_cv_updates['CV'][0], test_cv_expected, f"Expected and observed outputs do not match:\n{test_alpha_cv_updates['CV'][0]}")

        test_cv_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "-CV.csv")).fillna("")
        self.assertEqual(list(test_cv_iso3166_csv.columns), self.expected_output_columns, 
            "Observed and expected output columns do not match:\n{}.".format(list(test_cv_iso3166_csv.columns)))
        self.assertEqual(len(test_cv_iso3166_csv), 6, 
            "Expected there to be 6 output objects in csv, got {}.".format(len(list(test_cv_iso3166_csv))))
        self.assertEqual(test_cv_iso3166_csv.head(1).to_dict(orient='records')[0], test_cv_expected,
            f"Expected and observed outputs do not match:\n{test_cv_iso3166_csv.head(1).to_dict(orient='records')[0]}")
#3.)
        test_alpha_id_updates = get_updates(test_alpha_id, export_filename=self.export_filename, export_folder=self.export_folder, 
                export_json=True, export_csv=True, verbose=0, use_selenium=True)    #Indonesia
        
        test_id_expected = {
            "Description of Change": "",
            "Code/Subdivision Change": "Addition of province ID-PD; Update List Source.",
            "Date Issued": "2023-11-23",
            "Edition/Newsletter": "Online Browsing Platform (OBP) - (https://www.iso.org/obp/ui/#iso:code:3166:ID)."
            }

        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-ID.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-ID.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(list(test_alpha_id_updates), ['ID'],
            "Expected ID key to be in updates output object:\n{}.".format(list(test_alpha_id_updates))) 
        self.assertEqual(len(list(test_alpha_id_updates["ID"])), 14, 
            "Expected there to be 14 output objects in updates object, got {}.".format(len(list(test_alpha_id_updates))))
        for row in test_alpha_id_updates["ID"]:
            self.assertEqual(list(row.keys()), self.expected_output_columns, f"Columns from output do not match expected:\n{list(row.keys())}")
            self.assertIsInstance(row, dict, "Ouput object should be of type dict, got {}.".format(type(row)))
        self.assertEqual(test_alpha_id_updates['ID'][0], test_id_expected, f"Expected and observed outputs do not match:\n{test_alpha_id_updates['ID'][0]}")

        test_id_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "-ID.csv")).fillna("")
        self.assertEqual(list(test_id_iso3166_csv.columns), self.expected_output_columns,
            "Observed and expected output columns do not match:\n{}".format(list(test_id_iso3166_csv.columns)))
        self.assertEqual(len(test_id_iso3166_csv), 14, 
            "Expected there to be 14 output objects in csv, got {}.".format(len(list(test_id_iso3166_csv))))
        self.assertEqual(test_id_iso3166_csv.head(1).to_dict(orient='records')[0], test_id_expected,
            f"Expected and observed outputs do not match:\n{test_id_iso3166_csv.head(1).to_dict(orient='records')[0]}")
#4.)
        test_alpha_pt_updates = get_updates(test_alpha_pt, export_filename=self.export_filename, export_folder=self.export_folder, 
                export_json=True, export_csv=True, verbose=0, use_selenium=False)   #Portugal
        
        self.assertFalse(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-PT.csv")),
            "Expected output CSV file to not exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-PT.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(list(test_alpha_pt_updates), ['PT'],
            "Expected PT key to be in updates output object:\n{}.".format(list(test_alpha_pt_updates))) 
        with open(os.path.join(self.export_folder, self.export_filename + "-PT.json")) as output_json:
            test_alpha_pt_updates_json = json.load(output_json)
        self.assertEqual(test_alpha_pt_updates_json, {}, f"Expected and observed outputs do not match:\n{test_alpha_pt_updates_json}")
#5.)
        test_alpha_bf_ca_gu_ie_je_updates = get_updates(test_alpha_bf_ca_gu_ie_je_str, export_filename=self.export_filename, 
                export_folder=self.export_folder, concat_updates=False, export_json=True, export_csv=True, verbose=0, use_selenium=False)   #concat_updates=False, individual output files
        
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-BF.json")),
            "Expected output JSON file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-CA.json")),
            "Expected output JSON file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-GU.json")),
            "Expected output JSON file to not exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-IE.json")),
            "Expected output JSON file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-JE.json")),
            "Expected output JSON file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-BF.csv")),
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-CA.csv")),
            "Expected output CSV file to exist in folder.")
        self.assertFalse(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-GU.csv")),
            "Expected output CSV file to not exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-IE.csv")),
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-JE.csv")),
            "Expected output CSV file to exist in folder.")
        
        self.assertEqual(list(test_alpha_bf_ca_gu_ie_je_updates), ['BF', 'CA', 'GU', 'IE', 'JE'],
            "Expected BF, CA, GU, IE, JE keys to be in updates output object:\n{}".format(list(test_alpha_bf_ca_gu_ie_je_updates))) 
        self.assertEqual(len(list(test_alpha_bf_ca_gu_ie_je_updates["BF"])), 3, 
            "Expected there to be 3 output objects, got {}.".format(len(list(test_alpha_bf_ca_gu_ie_je_updates))))
        self.assertEqual(len(list(test_alpha_bf_ca_gu_ie_je_updates["CA"])), 4, 
            "Expected there to be 4 output objects, got {}.".format(len(list(test_alpha_bf_ca_gu_ie_je_updates))))
        self.assertEqual(len(list(test_alpha_bf_ca_gu_ie_je_updates["GU"])), 0, 
            "Expected there to be 0 output objects, got {}.".format(len(list(test_alpha_bf_ca_gu_ie_je_updates))))
        self.assertEqual(len(list(test_alpha_bf_ca_gu_ie_je_updates["IE"])), 2, 
            "Expected there to be 2 output objects, got {}.".format(len(list(test_alpha_bf_ca_gu_ie_je_updates))))
        self.assertEqual(len(list(test_alpha_bf_ca_gu_ie_je_updates["JE"])), 1, 
            "Expected there to be 1 output object, got {}.".format(len(list(test_alpha_bf_ca_gu_ie_je_updates))))
        for code in test_alpha_cv_updates:
            for row in test_alpha_cv_updates[code]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, f"Columns from output do not match expected:\n{list(row.keys())}")
                self.assertIsInstance(row, dict, "Ouput object row should be of type dict, got {}.".format(type(row)))
#6.)    
        test_alpha_bf_ca_gu_ie_je_updates = get_updates(test_alpha_bf_ca_gu_ie_je_str, export_filename=self.export_filename, 
            export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)    #Burkina Faso, Canada, Guam, Ireland, Jersey - concat_updates=True, one output file

        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-BF,CA,GU,IE,JE.json")), 
            "Output file {} not found in export folder {}.".format(os.path.join(self.export_filename + "-BF,CA,GU,IE,JE.json"), self.export_folder))
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-BF,CA,GU,IE,JE.csv")), 
            "Output file {} not found in export folder {}.".format(os.path.join(self.export_filename + "-BF,CA,GU,IE,JE.csv"), self.export_folder))

        #open exported BF,CA,GU,IE,JE json
        with open(os.path.join(self.export_folder, self.export_filename + "-BF,CA,GU,IE,JE.json")) as output_json:
            test_bf_ca_gu_ie_je_iso3166_json = json.load(output_json)
        self.assertEqual(len(list(test_bf_ca_gu_ie_je_iso3166_json)), 5, 
            "Expected there to be 5 output objects in json, got {}.".format(len(list(test_bf_ca_gu_ie_je_iso3166_json))))
        self.assertEqual(list(test_bf_ca_gu_ie_je_iso3166_json), ["BF", "CA", "GU", "IE", "JE"], 
            "Expected keys of JSON to be BF, CA, GU, IE, JE, got {}.".format(list(test_bf_ca_gu_ie_je_iso3166_json)))
        
        #open exported BF,CA,GU,IE,JE csv
        test_bf_ca_gu_ie_je_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "-BF,CA,GU,IE,JE.csv")).fillna("")
        self.assertEqual(len(test_bf_ca_gu_ie_je_iso3166_csv), 10, 
            "Expected there to be 10 outputs in CSV, got {}.".format(len(test_bf_ca_gu_ie_je_iso3166_csv)))
        self.assertEqual(list(test_bf_ca_gu_ie_je_iso3166_csv["Country Code"].unique()), ["BF", "CA", "IE", "JE"],
            "Expected and observed column values for Country Code column do not match:\n{}".format(test_bf_ca_gu_ie_je_iso3166_csv["Country Code"]))
        self.assertTrue(set(["Country Code"] + self.expected_output_columns) == set(list(test_bf_ca_gu_ie_je_iso3166_csv.columns)),
            "Column names/headers do not match expected:\n{}.".format(set(list(test_bf_ca_gu_ie_je_iso3166_csv.columns))))
#7.)
        with self.assertRaises(TypeError):
            get_updates(test_alpha_error_1, export_filename=self.export_filename, 
                export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0)
            get_updates(test_alpha_error_2, export_filename=self.export_filename, 
                export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0)
#8.)
        with self.assertRaises(ValueError):
            get_updates(test_alpha_error_3, export_filename=self.export_filename, 
                export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0)
            get_updates(test_alpha_error_4, export_filename=self.export_filename, 
                export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0)
            
    @unittest.skip("Skipping as below tests requiring extracting all updates each time.")  
    def test_get_updates_year(self):
        """ Testing main updates function that gets the updates and exports to json/csv, using a variety of year input 
            parameter values. Note, only using updates data from the wiki pages and not ISO due to time constraint of 
            pulling data via Selenium. """
        test_year1 = "2017"
        test_year2 = "2005"
        test_year3 = ">2021"
        test_year4 = "<2003"
        test_year5 = "2005-2007"
        test_year6 = "1999-2002"
        test_year7 = "abcdef"
        test_year8 = 12345
        test_year9 = True
#1.)    
        test_year_2017_updates = get_updates(year=test_year1, export_filename=self.export_filename,  #2017
                export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)
        test_year_2017_expected_keys = ["CN", "CY", "ID", "KP", "NR", "PA", "PK", "QA", "TJ", "UG"]

        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-2017.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-2017.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_year_2017_updates), 10, 
            "Expected 10 updates in output object, got {}.".format(len(test_year_2017_updates)))
        self.assertEqual(list(test_year_2017_updates), test_year_2017_expected_keys, 
            "Expected and observed list of country codes do not match:\n{}.".format(list(test_year_2017_updates)))
        for update in test_year_2017_updates:
            for row in range(0, len(test_year_2017_updates[update])):
                self.assertEqual(datetime.strptime(test_year_2017_updates[update][row]["Date Issued"], '%Y-%m-%d').year, 2017, 
                    "Expected year of updates output to be 2017, got {}.".format(test_year_2017_updates[update][row]["Date Issued"]))

        test_2017_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "-2017.csv")).fillna("")
        self.assertTrue(set(["Country Code"] + self.expected_output_columns) == set(list(test_2017_iso3166_csv.columns)),
            "Column names/headers do not match expected:\n{}.".format(set(list(test_2017_iso3166_csv.columns))))
        self.assertEqual(len(test_2017_iso3166_csv), 10, 
            "Expected there to be 10 output objects in csv, got {}.".format(len(test_2017_iso3166_csv)))
#2.)
        test_year_2005_updates = get_updates(year=test_year2, export_filename=self.export_filename,  #2005
                export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)
        test_year_2005_expected_keys = ["AF", "DJ", "ID", "RU", "SI", "VN"]

        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-2005.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-2005.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_year_2005_updates), 6, 
            "Expected 6 updates in output object, got {}.".format(len(test_year_2005_updates)))
        self.assertEqual(list(test_year_2005_updates), test_year_2005_expected_keys, 
            "Expected and observed list of country codes do not match:\n{}.".format(list(test_year_2005_updates)))
        for update in test_year_2005_updates:
            for row in range(0, len(test_year_2005_updates[update])):
                self.assertEqual(datetime.strptime(test_year_2005_updates[update][row]["Date Issued"], '%Y-%m-%d').year, 2005, 
                    "Expected year of updates output to be 2005, got {}.".format(test_year_2005_updates[update][row]["Date Issued"]))

        test_2005_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "-2005.csv")).fillna("")
        self.assertTrue(set(["Country Code"] + self.expected_output_columns) == set(list(test_2005_iso3166_csv.columns)),
            "Column names/headers do not match expected:\n{}.".format(set(list(test_2005_iso3166_csv.columns))))
        self.assertEqual(len(test_2005_iso3166_csv), 6, 
            "Expected there to be 6 output objects in csv, got {}.".format(len(test_2005_iso3166_csv)))
#3.)
        test_year_gt_2021_updates = get_updates(year=test_year3, export_filename=self.export_filename,  #>2021
                export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)
        test_year_gt_2021_expected_keys = ['CN', 'DZ', 'ET', 'FI', 'FR', 'GB', 'GT', 'HU', 'ID', 'IN', 'IQ', 'IR', 'IS', 'KH', 
                                           'KP', 'KR', 'KZ', 'LT', 'LV', 'ME', 'NP', 'NZ', 'PA', 'PH', 'PL', 'RU', 'SI', 'SS']

        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "_>2021.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "_>2021.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_year_gt_2021_updates), 28, 
            "Expected 28 updates in output object, got {}.".format(len(test_year_gt_2021_updates)))
        self.assertEqual(list(test_year_gt_2021_updates), test_year_gt_2021_expected_keys, 
            "Expected and observed list of country codes do not match:\n{}.".format(list(test_year_gt_2021_updates)))
        for update in test_year_gt_2021_updates:
            for row in range(0, len(test_year_gt_2021_updates[update])):
                self.assertTrue(datetime.strptime(test_year_gt_2021_updates[update][row]["Date Issued"], '%Y-%m-%d').year >= 2021, 
                    "Expected year of updates output to be greater than or equal to 2021, got {}.".format(test_year_gt_2021_updates[update][row]["Date Issued"]))

        test_gt_2021_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "_>2021.csv")).fillna("")
        self.assertTrue(set(["Country Code"] + self.expected_output_columns) == set(list(test_gt_2021_iso3166_csv.columns)),
            "Column names/headers do not match expected:\n{}.".format(set(list(test_gt_2021_iso3166_csv.columns))))
        self.assertEqual(len(test_gt_2021_iso3166_csv), 37, 
            "Expected there to be 37 output objects in csv, got {}.".format(len(test_gt_2021_iso3166_csv)))
#4.)
        test_year_lt_2003_updates = get_updates(year=test_year4, export_filename=self.export_filename,  #<2003
                export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)
        test_year_lt_2003_expected_keys = ['AE', 'AL', 'AO', 'AZ', 'BD', 'BG', 'BI', 'BJ', 'BY', 'CA', 'CD', 'CN', 'CV', 'CZ', \
                                        'DO', 'EC', 'ER', 'ES', 'ET', 'FR', 'GB', 'GE', 'GN', 'GT', 'HR', 'ID', 'IN', 'IR', \
                                            'IT', 'KG', 'KH', 'KP', 'KR', 'KZ', 'LA', 'MA', 'MD', 'MO', 'MU', 'MW', 'NG', \
                                                'NI', 'PH', 'PL', 'PS', 'RO', 'RU', 'SI', 'TJ', 'TL', 'TM', 'TR', 'TW', \
                                                    'UG', 'UZ', 'VA', 'VE', 'VN', 'YE']
        
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "_<2003.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "_<2003.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_year_lt_2003_updates), 59, 
            "Expected 59 updates in output object, got {}.".format(len(test_year_lt_2003_updates)))
        self.assertEqual(list(test_year_lt_2003_updates), test_year_lt_2003_expected_keys, 
            "Expected and observed list of country codes do not match:\n{}.".format(list(test_year_lt_2003_updates)))
        for update in test_year_lt_2003_updates:
            for row in range(0, len(test_year_lt_2003_updates[update])):
                self.assertTrue(datetime.strptime(test_year_lt_2003_updates[update][row]["Date Issued"], '%Y-%m-%d').year < 2003, 
                    "Expected year of updates output to be less than 2003, got {}.".format(test_year_lt_2003_updates[update][row]["Date Issued"]))

        test_lt_2003_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "_<2003.csv")).fillna("")
        self.assertTrue(set(["Country Code"] + self.expected_output_columns) == set(list(test_lt_2003_iso3166_csv.columns)),
            "Column names/headers do not match expected:\n{}.".format(set(list(test_lt_2003_iso3166_csv.columns))))
        self.assertEqual(len(test_lt_2003_iso3166_csv), 79, 
            "Expected there to be 79 output objects in csv, got {}.".format(len(test_lt_2003_iso3166_csv)))
#5.)
        test_year_2005_2007_updates = get_updates(year=test_year5, export_filename=self.export_filename,  #2005-2007
                export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)
        test_year_2005_2007_expected_keys = ['AD', 'AF', 'AG', 'BA', 'BB', 'BG', 'BH', 'BL', 'CI', 'CZ', 'DJ', 'DM', 'DO', 'EG', 'FR', 'GB', \
                                        'GD', 'GE', 'GG', 'GN', 'HT', 'ID', 'IM', 'IR', 'IT', 'JE', 'KE', 'KN', 'KW', 'LB', 'LC', 'LI', \
                                            'LR', 'ME', 'MF', 'MK', 'MT', 'NR', 'PW', 'RS', 'RU', 'RW', 'SB', 'SC', 'SD', 'SG', 'SI', \
                                                'SM', 'TD', 'TO', 'TV', 'UG', 'VC', 'VN', 'YE', 'ZA']

        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "_2005-2007.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "_2005-2007.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_year_2005_2007_updates), 56, 
            "Expected 56 updates in output object, got {}.".format(len(test_year_2005_2007_updates)))
        self.assertEqual(list(test_year_2005_2007_updates), test_year_2005_2007_expected_keys, 
            "Expected and observed list of country codes do not match:\n{}.".format(list(test_year_2005_2007_updates)))
        for update in test_year_2005_2007_updates:
            for row in range(0, len(test_year_2005_2007_updates[update])):
                self.assertTrue((datetime.strptime(test_year_2005_2007_updates[update][row]["Date Issued"], '%Y-%m-%d').year >= 2005) and \
                                (datetime.strptime(test_year_2005_2007_updates[update][row]["Date Issued"], '%Y-%m-%d').year <= 2007), 
                            "Expected year of updates output to be between 2005 and 2007, got {}.".format(test_year_2005_2007_updates[update][row]["Date Issued"]))

        test_year_2005_2007_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "_2005-2007.csv")).fillna("")
        self.assertTrue(set(["Country Code"] + self.expected_output_columns) == set(list(test_year_2005_2007_iso3166_csv.columns)),
            "Column names/headers do not match expected:\n{}.".format(set(list(test_year_2005_2007_iso3166_csv.columns))))
        self.assertEqual(len(test_year_2005_2007_iso3166_csv), 62, 
            "Expected there to be 62 output objects in csv, got {}.".format(len(test_year_2005_2007_iso3166_csv)))
#6.)
        test_year_1999_2002_updates = get_updates(year=test_year6, export_filename=self.export_filename,  #1999-2002
                export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)
        test_year_1999_2002_expected_keys = ['AE', 'AL', 'AO', 'AZ', 'BD', 'BG', 'BI', 'BJ', 'BY', 'CA', 'CD', 'CN', 'CV', 'CZ', 'DO', 'EC', \
                                             'ER', 'ES', 'ET', 'FR', 'GB', 'GE', 'GN', 'GT', 'HR', 'ID', 'IN', 'IR', 'IT', 'KG', 'KH', 'KP', \
                                                'KR', 'KZ', 'LA', 'MA', 'MD', 'MO', 'MU', 'MW', 'NG', 'NI', 'PH', 'PL', 'PS', 'RO', 'RU', 'SI', \
                                                    'TJ', 'TL', 'TM', 'TR', 'TW', 'UG', 'UZ', 'VE', 'VN', 'YE']

        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "_1999-2002.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "_1999-2002.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_year_1999_2002_updates), 58, 
            "Expected 58 updates in output object, got {}.".format(len(test_year_1999_2002_updates)))
        self.assertEqual(list(test_year_1999_2002_updates), test_year_1999_2002_expected_keys, 
            "Expected and observed list of country codes do not match:\n{}.".format(list(test_year_1999_2002_updates)))
        for update in test_year_1999_2002_updates:
            for row in range(0, len(test_year_1999_2002_updates[update])):
                self.assertTrue((datetime.strptime(test_year_1999_2002_updates[update][row]["Date Issued"], '%Y-%m-%d').year >= 1999) and \
                                (datetime.strptime(test_year_1999_2002_updates[update][row]["Date Issued"], '%Y-%m-%d').year <= 2002), 
                            "Expected year of updates output to be between 1999 and 2002, got {}.".format(test_year_1999_2002_updates[update][row]["Date Issued"]))

        test_year_1999_2002_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "_1999-2002.csv")).fillna("")
        self.assertTrue(set(["Country Code"] + self.expected_output_columns) == set(list(test_year_1999_2002_iso3166_csv.columns)),
            "Column names/headers do not match expected:\n{}.".format(set(list(test_year_1999_2002_iso3166_csv.columns))))
        self.assertEqual(len(test_year_1999_2002_iso3166_csv), 78, 
            "Expected there to be 78 output objects in csv, got {}.".format(len(test_year_1999_2002_iso3166_csv)))
#7.)
        with self.assertRaises(ValueError):
            get_updates(year=test_year7, export_filename=self.export_filename,   #abcdef
                export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)
            get_updates(year=test_year8, export_filename=self.export_filename,   #12345
                    export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0)
            get_updates(year=test_year9, export_filename=self.export_filename,   #True
                    export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0)

    # @unittest.skip("")
    def test_get_updates_alpha_year(self):
        """ Testing main updates function that gets the updates and exports to json/csv, using
            a variety of ISO 3166-1 alpha codes and year input parameter values. """
        test_ch_2003 = ("CH", "2003") #Switzerland
        test_md_2008 = ("MD", "2008") #Moldova
        test_ne_2010 = ("NER", "2010") #Niger
        test_sd_tt_2015_2021 = ("SDN,780", "2015-2021") #Sudan, Trinidad and Tabago - using alpha-3 codes
        test_es_gq_kg_sm_2020 = ("ES,GNQ,KGZ,674", "2020") #Spain, Equitorial Guinea, Kyrgyzstan, San Marino
        test_ie_2027 = ("IE", "2027") #Ireland
        test_error1 = ("ABC", "3003")
        test_error2 = ("ABCDEF", "ABC")
#1.) 
        test_alpha_year_ch_2003_updates = get_updates(alpha_codes=test_ch_2003[0], year=test_ch_2003[1],  #Switzerland
                export_filename=self.export_filename, export_folder=self.export_folder, concat_updates=True, export_json=True, \
                    export_csv=False, verbose=0, use_selenium=True)

        self.assertFalse(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-CH_2003.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-CH_2003.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_alpha_year_ch_2003_updates), 1, 
            "Expected 1 update in output object, got {}.".format(len(test_alpha_year_ch_2003_updates)))
        self.assertEqual(list(test_alpha_year_ch_2003_updates), ["CH"], 
            "Expected and observed list of country codes do not match:\n{}.".format(list(test_alpha_year_ch_2003_updates)))
        for update in test_alpha_year_ch_2003_updates:
            for row in range(0, len(test_alpha_year_ch_2003_updates[update])):
                self.assertEqual(datetime.strptime(test_alpha_year_ch_2003_updates[update][row]["Date Issued"], '%Y-%m-%d').year, 2003,
                            "Expected year of updates output to be 2003, got {}.".format(test_alpha_year_ch_2003_updates[update][row]["Date Issued"]))
#2.)
        test_alpha_year_md_2008_updates = get_updates(alpha_codes=test_md_2008[0], year=test_md_2008[1],  #Moldova
                export_filename=self.export_filename, export_folder=self.export_folder, concat_updates=True, export_json=True, \
                    export_csv=False, verbose=0, use_selenium=True)

        self.assertFalse(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-MD_2008.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-MD_2008.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_alpha_year_md_2008_updates), 1, 
            "Expected 1 update in output object, got {}.".format(len(test_alpha_year_md_2008_updates)))
        self.assertEqual(list(test_alpha_year_md_2008_updates), ["MD"], 
            "Expected and observed list of country codes do not match:\n{}.".format(list(test_alpha_year_md_2008_updates)))
        for update in test_alpha_year_md_2008_updates:
            for row in range(0, len(test_alpha_year_md_2008_updates[update])):
                self.assertEqual(datetime.strptime(test_alpha_year_md_2008_updates[update][row]["Date Issued"], '%Y-%m-%d').year, 2008,
                            "Expected year of updates output to be 2008, got {}.".format(test_alpha_year_md_2008_updates[update][row]["Date Issued"]))
#3.) 
        test_alpha_year_ne_2010_updates = get_updates(alpha_codes=test_ne_2010[0], year=test_ne_2010[1],  #Niger
                export_filename=self.export_filename, export_folder=self.export_folder, concat_updates=True, export_json=True, \
                    export_csv=False, verbose=0, use_selenium=True)

        self.assertFalse(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-NE_2010.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-NE_2010.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_alpha_year_ne_2010_updates), 1, 
            "Expected 1 update in output object, got {}.".format(len(test_alpha_year_ne_2010_updates)))
        self.assertEqual(list(test_alpha_year_ne_2010_updates), ["NE"], 
            "Expected and observed list of country codes do not match:\n{}.".format(list(test_alpha_year_ne_2010_updates)))
        for update in test_alpha_year_ne_2010_updates:
            for row in range(0, len(test_alpha_year_ne_2010_updates[update])):
                self.assertEqual(datetime.strptime(test_alpha_year_ne_2010_updates[update][row]["Date Issued"], '%Y-%m-%d').year, 2010,
                            "Expected year of updates output to be 2010, got {}.".format(test_alpha_year_ne_2010_updates[update][row]["Date Issued"]))
#4.)
        test_alpha_year_sd_tt_2015_2021_updates = get_updates(alpha_codes=test_sd_tt_2015_2021[0], year=test_sd_tt_2015_2021[1],  #Sudan, Trinidad and Tabago
                export_filename=self.export_filename, export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=False, verbose=0, use_selenium=True)

        self.assertFalse(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-SD,TT_2015-2021.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-SD,TT_2015-2021.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_alpha_year_sd_tt_2015_2021_updates), 2, 
            "Expected 2 updates in output object, got {}.".format(len(test_alpha_year_sd_tt_2015_2021_updates)))
        self.assertEqual(list(test_alpha_year_sd_tt_2015_2021_updates), ["SD", "TT"], 
            "Expected and observed list of country codes do not match:\n{}.".format(list(test_alpha_year_sd_tt_2015_2021_updates)))
        for update in test_alpha_year_sd_tt_2015_2021_updates:
            for row in range(0, len(test_alpha_year_sd_tt_2015_2021_updates[update])):
                self.assertTrue((datetime.strptime(test_alpha_year_sd_tt_2015_2021_updates[update][row]["Date Issued"], '%Y-%m-%d').year >= 2015) and \
                                (datetime.strptime(test_alpha_year_sd_tt_2015_2021_updates[update][row]["Date Issued"], '%Y-%m-%d').year <= 2021), 
                            "Expected year of updates output to be between 2015 and 2021, got {}.".format(test_alpha_year_sd_tt_2015_2021_updates[update][row]["Date Issued"]))
#5.)
        test_alpha_year_es_gq_kg_sm_2020_updates = get_updates(alpha_codes=test_es_gq_kg_sm_2020[0], year=test_es_gq_kg_sm_2020[1], #Spain, Equitorial Guinea, Kyrgyzstan, San Marino
                export_filename=self.export_filename, export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=False, verbose=0, use_selenium=True)

        self.assertFalse(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-ES,GQ,KG,SM_2020.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-ES,GQ,KG,SM_2020.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_alpha_year_es_gq_kg_sm_2020_updates), 4, 
            "Expected 4 updates in output object, got {}.".format(len(test_alpha_year_es_gq_kg_sm_2020_updates)))
        self.assertEqual(list(test_alpha_year_es_gq_kg_sm_2020_updates), ["ES", "GQ", "KG", "SM"], 
            "Expected and observed list of country codes do not match:\n{}.".format(list(test_alpha_year_es_gq_kg_sm_2020_updates)))
        for update in test_alpha_year_es_gq_kg_sm_2020_updates:
            for row in range(0, len(test_alpha_year_es_gq_kg_sm_2020_updates[update])):
                self.assertEqual(datetime.strptime(test_alpha_year_es_gq_kg_sm_2020_updates[update][row]["Date Issued"], '%Y-%m-%d').year, 2020,
                            "Expected year of updates output to be 2020, got {}.".format(test_alpha_year_es_gq_kg_sm_2020_updates[update][row]["Date Issued"]))
#6.) 
        test_alpha_year_ie_2027_updates = get_updates(alpha_codes=test_ie_2027[0], year=test_ie_2027[1],  #Ireland
                export_filename=self.export_filename, export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=False, verbose=0, use_selenium=True)

        self.assertFalse(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-IE_2027.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-IE_2027.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(list(test_alpha_year_ie_2027_updates), ["IE"], 
            "Expected and observed list of country codes do not match:\n{}.".format(list(test_alpha_year_ie_2027_updates)))
        self.assertEqual(test_alpha_year_ie_2027_updates["IE"], {},
            "Expected output object to be an empty dict, got {}.".format(test_alpha_year_ie_2027_updates["IE"]))
#7.)
        with self.assertRaises(ValueError):
            get_updates(alpha_codes=test_error1[0], year=test_error1[1], 
                    export_filename=self.export_filename, export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=False, verbose=0)
            get_updates(alpha_codes=test_error2[0], year=test_error2[1], 
                    export_filename=self.export_filename, export_folder=self.export_folder, concat_updates=True, export_json=True, export_csv=False, verbose=0)

    def tearDown(self):
        """ Delete imported json from memory. """
        del self.iso3166_json
        shutil.rmtree(self.export_folder)
    
if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)