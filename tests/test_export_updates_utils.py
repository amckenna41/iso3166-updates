try:
    from iso3166_updates_export.utils import *
except:
    from ..iso3166_updates_export.utils  import *
import json
import re
from datetime import datetime
import os 
import platform
import shutil
import pandas as pd
import requests
from fake_useragent import UserAgent
import unittest
unittest.TestLoader.sortTestMethodsUsing = None

class ISO3166_Export_Updates_Utils_Tests(unittest.TestCase):
    """
    Test suite for testing the utils module in the ISO 3166 updates export directory. 
    The module contains various utility and auxillary functions used throughout the 
    export process. 

    Test Cases
    ==========
    test_convert_to_alpha2:
        testing function that converts any alpha codes to its alpha-2 counterpart. 
    test_validate_year:
        testing function that validates and corrects any input year/years. 
    test_filter_year:
        testing function that filters out/in rows of the updates export dataframe 
        based on input year parameter.
    test_get_alpha_codes_list:
        testing function that validates and returns the list of alpha country codes
        to export. 
    test_correct_columns:
        testing function that corrects and aligns the column names for the export
        dataframe.
    test_table_to_array:
        testing function that converts a 2D html table from wiki pages into array/list.
    test_parse_date:
        testing function that parses publication date from a string.
    test_get_year:
        testing function that parses the publication year from the date. 
    test_extract_corrected_date:
        testing function that extracts the corrected publication date from date.
    test_remove_corrected_date:
        testing function that removes the corrected publication date from date.
    test_remove_doublespacing:
        testing function that removes double spacing from rows in dataframe.
    test_export_updates:
        testing the functionality for exporting the exported updates data to the JSON and CSV.
    test_remove_duplicates:
        testing the functionality that removes duplicate objects from the dataframe export. 
    """
    def setUp(self):
        """ Initialise test variables, import json. """
        #importing all test updates data from JSON, open iso3166-updates json file and load it into class variable, loading in a JSON is different in Windows & Unix/Linux systems
        if (platform.system() != "Windows"):
            with open(os.path.join("tests", "test-iso3166-updates.json")) as input_json:
                self.iso3166_data = json.load(input_json)
        else:
            with open(os.path.join("tests", "test-iso3166-updates.json"), encoding="utf-8") as input_json:
                self.iso3166_data = json.loads(input_json.read())

        #normalize JSON data for conversion into dataframe, some functions require data to be dataframe
        flat_data = []
        for country_code, changes in self.iso3166_data.items():
            for change in changes:
                flat_data.append({
                    "Country Code": country_code,
                    "Change": change.get("Change", ""),
                    "Description of Change": change.get("Description of Change", ""),
                    "Date Issued": change.get("Date Issued", ""),
                    "Source": change.get("Source", ""),
                })

        #convert to DataFrame
        self.iso3166_df = pd.DataFrame(flat_data)

        #create temp test dir for storing any test class outputs
        self.test_export_folder = os.path.join("tests", "temp_test_dir")
        if not(os.path.isdir(self.test_export_folder)):
            os.makedirs(self.test_export_folder)

    # @unittest.skip("")
    def test_convert_to_alpha2(self):
        """ Testing function that converts country codes into their alpha-2 counterpart. """
        test_alpha_br = "BR" #Brazil
        test_alpha_cz = "CZE" #Czechia 
        test_alpha_er = "ERI" #Eritrea
        test_alpha_fj = "242" #Fiji
        test_alpha_mk = "807" #North Macedonia
        test_alpha_error1 = "abc"
        test_alpha_error2 = "z"
        test_alpha_error3 = "000"
        test_alpha_error4 = ["BY,CO,FJ"]
        test_alpha_error5 = 12345
        test_alpha_error6 = False
#1.)
        self.assertEqual(convert_to_alpha2(test_alpha_br), "BR", f"Expected alpha-2 country code to be BR, got {convert_to_alpha2(test_alpha_br)}.")
#2.)
        self.assertEqual(convert_to_alpha2(test_alpha_cz), "CZ", f"Expected alpha-2 country code to be CZ, got {convert_to_alpha2(test_alpha_cz)}.")
#3.)
        self.assertEqual(convert_to_alpha2(test_alpha_er), "ER", f"Expected alpha-2 country code to be ER, got {convert_to_alpha2(test_alpha_er)}.")
#4.)
        self.assertEqual(convert_to_alpha2(test_alpha_fj), "FJ", f"Expected alpha-2 country code to be FJ, got {convert_to_alpha2(test_alpha_fj)}.")
#5.)
        self.assertEqual(convert_to_alpha2(test_alpha_mk), "MK", f"Expected alpha-2 country code to be MK, got {convert_to_alpha2(test_alpha_mk)}.")
#6.)
        with self.assertRaises(ValueError):
            convert_to_alpha2(test_alpha_error1)
            convert_to_alpha2(test_alpha_error2)
            convert_to_alpha2(test_alpha_error3)
#7.)
        with self.assertRaises(TypeError):
            convert_to_alpha2(test_alpha_error4)
            convert_to_alpha2(test_alpha_error5)
            convert_to_alpha2(test_alpha_error6)
    
    # @unittest.skip("")
    def test_validate_year(self):
        """ Testing function that validates and corrects any input year/years. """
        test_year_2002 = "2002"
        test_year_2020 = "2020"
        test_year_2002_2005_2024 = "2002,2005,2024"
        test_year_gt_2006 = ">2006"
        test_year_lt_2000 = "<2000"
        test_year_bw_2012_2017 = "2012-2017"
        test_year_not_2001 = "<>2001"
        test_year_error1 = ">2009,<2019"
        test_year_error2 = "2009,2010,12345"
        test_year_error3 = "ABC"
        test_year_error4 = ["2001,2002,2003"]
        test_year_error5 = False
        test_year_error6 = 10.5
#1.)    
        test_year_2002_output = validate_year(test_year_2002)
        self.assertEqual(test_year_2002_output, (["2002"], False, False, False, False), f"Output of validate_year function does not match expected:\n{test_year_2002_output}.")
#2.)
        test_year_2020_output = validate_year(test_year_2020)
        self.assertEqual(test_year_2020_output, (["2020"], False, False, False, False), f"Output of validate_year function does not match expected:\n{test_year_2020_output}.")
#3.)
        test_year_2002_2005_2024_output = validate_year(test_year_2002_2005_2024)
        self.assertEqual(test_year_2002_2005_2024_output, (["2002", "2005", "2024"], False, False, False, False), f"Output of validate_year function does not match expected:\n{test_year_2002_2005_2024_output}.")
#4.)
        test_year_gt_2006_output = validate_year(test_year_gt_2006)
        self.assertEqual(test_year_gt_2006_output, (["2006"], False, True, False, False), f"Output of validate_year function does not match expected:\n{test_year_gt_2006_output}.")
#5.)
        test_year_lt_2000_output = validate_year(test_year_lt_2000)
        self.assertEqual(test_year_lt_2000_output, (["2000"], False, False, True, False), f"Output of validate_year function does not match expected:\n{test_year_lt_2000_output}.")
#6.)
        test_year_bw_2012_2017_output = validate_year(test_year_bw_2012_2017)
        self.assertEqual(test_year_bw_2012_2017_output, (["2012", "2017"], True, False, False, False), f"Output of validate_year function does not match expected:\n{test_year_bw_2012_2017_output}.")
#7.)
        test_year_not_2001_output = validate_year(test_year_not_2001)
        self.assertEqual(test_year_not_2001_output, (["2001"], False, False, False, True), f"Output of validate_year function does not match expected:\n{test_year_not_2001_output}.")
#8.)
        with self.assertRaises(ValueError):
            validate_year(test_year_error1)
            validate_year(test_year_error2)
            validate_year(test_year_error3)
#9.)
        with self.assertRaises(TypeError):
            validate_year(test_year_error4)
            validate_year(test_year_error5)
            validate_year(test_year_error6)

    # @unittest.skip("")
    def test_filter_year(self):
        """ Testing function that filters out/in rows of the updates export dataframe based on input year parameter. """
        test_filter_year_2010 = "2010"
        test_filter_year_2004_2007_2008 = "2004,2007,2008"
        test_filter_year_gt_2009 = ">2009"
        test_filter_year_lt_2001 = "<2001"
        test_filter_year_2010_2015 = "2010-2015"
        test_year_error1 = set("2004,2007,2008")
        test_year_error2 = False
        test_year_error3 = 1.35
#1.)    
        test_filter_year_2010_filtered_output = filter_year(self.iso3166_df, test_filter_year_2010)

        for index, row in test_filter_year_2010_filtered_output.iterrows():
            current_year = datetime.strptime(re.sub(r"\(.*\)", "", row["Date Issued"]).strip(), "%Y-%m-%d").year
            self.assertNotEqual(current_year, test_filter_year_2010, f"Current publiction date/year for row should not be 2010: {row}.")
#2.)
        test_filter_year_2004_2007_2008_filtered_output = filter_year(self.iso3166_df, test_filter_year_2004_2007_2008)
        for index, row in test_filter_year_2004_2007_2008_filtered_output.iterrows():
            current_year = datetime.strptime(re.sub(r"\(.*\)", "", row["Date Issued"]).strip(), "%Y-%m-%d").year
            self.assertNotEqual(current_year, test_filter_year_2004_2007_2008, f"Current publiction date/year for row should not be 2004, 2007 or 2008: {row}.")
#3.)
        test_filter_year_gt_2009_filtered_output = filter_year(self.iso3166_df, test_filter_year_gt_2009)
        for index, row in test_filter_year_gt_2009_filtered_output.iterrows():
            current_year = datetime.strptime(re.sub(r"\(.*\)", "", row["Date Issued"]).strip(), "%Y-%m-%d").year
            self.assertTrue(current_year>=2009, f"Current publiction date/year for row should not be less than 2009: {row}.")
#4.)
        test_filter_year_lt_2001_filtered_output = filter_year(self.iso3166_df, test_filter_year_lt_2001)
        for index, row in test_filter_year_lt_2001_filtered_output.iterrows():
            current_year = datetime.strptime(re.sub(r"\(.*\)", "", row["Date Issued"]).strip(), "%Y-%m-%d").year
            self.assertTrue(current_year<2001, f"Current publiction date/year for row should not be more than or equal to 2001: {row}.")
#5.)
        test_filter_year_2010_2015_filtered_output = filter_year(self.iso3166_df, test_filter_year_2010_2015)
        for index, row in test_filter_year_2010_2015_filtered_output.iterrows():
            current_year = datetime.strptime(re.sub(r"\(.*\)", "", row["Date Issued"]).strip(), "%Y-%m-%d").year
            self.assertTrue((current_year>=2010 and current_year<=2015), f"Current publiction date/year for row should be between 2010 and 2015 inclusive: {row}.")
#6.)
        with self.assertRaises(TypeError):
            filter_year(test_year_error1)
            filter_year(test_year_error2)
            filter_year(test_year_error3)

    # @unittest.skip("")
    def test_get_alpha_codes_list(self):
        """ Testing function that validates and returns the list of alpha country codes to export. """
        test_alpha_codes_1 = ["FR", "BGD", "GE", "ESP", "174"]
        test_alpha_codes_2 = "KHM,kna,408,422"
        test_alpha_codes_3 = "438,lux,ma,mdg"
        test_alpha_codes_4 = "TR"
        test_alpha_codes_range_1 = "AD-DJ"
        test_alpha_codes_range_2 = "NAM-PLW"
        test_alpha_codes_range_3 = "ZW-VU"
        test_alpha_codes_range_4 = "WLF-740"
#1.)
        test_alpha_codes_ouput_1, _ = get_alpha_codes_list(test_alpha_codes_1)   #["FR", "BGD", "GE", "ESP", "174"]
        self.assertEqual(test_alpha_codes_ouput_1, ['BD', 'ES', 'FR', 'GE', 'KM'], f"Expected and observed alpha codes do not match:\n{test_alpha_codes_ouput_1}.")
#2.)
        test_alpha_codes_ouput_2, _ = get_alpha_codes_list(test_alpha_codes_2)   #KHM,kna,408,422
        self.assertEqual(test_alpha_codes_ouput_2, ['KH', 'KN', 'KP', 'LB'], f"Expected and observed alpha codes do not match:\n{test_alpha_codes_ouput_2}.")
#3.)
        test_alpha_codes_ouput_3, _ = get_alpha_codes_list(test_alpha_codes_3)   #438,lux,ma,mdg
        self.assertEqual(test_alpha_codes_ouput_3, ['LI', 'LU', 'MA', 'MG'], f"Expected and observed alpha codes do not match:\n{test_alpha_codes_ouput_3}.")
#4.)
        test_alpha_codes_ouput_4, _ = get_alpha_codes_list(test_alpha_codes_4)   #TR
        self.assertEqual(test_alpha_codes_ouput_4, ['TR'], f"Expected and observed alpha codes do not match:\n{test_alpha_codes_ouput_4}.")
#5.)
        test_alpha_codes_range_ouput_1 = get_alpha_codes_list(alpha_codes_range=test_alpha_codes_range_1)   #AD-DJ 
        test_alpha_codes_range_output_list_1 = ['AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AW', 'AX', 'AZ', 'BA', 
            'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BL', 'BM', 'BN', 'BO', 'BQ', 'BR', 'BS', 'BT', 'BV', 'BW', 'BY', 'BZ', 'CA', 'CC', 'CD', 
            'CF', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN', 'CO', 'CR', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ', 'DE', 'DJ']
        self.assertEqual(test_alpha_codes_range_ouput_1, (test_alpha_codes_range_output_list_1, test_alpha_codes_range_1), f"Expected and observed range of alpha codes do not match:\n{test_alpha_codes_range_ouput_1}.")
#6.)
        test_alpha_codes_range_ouput_2 = get_alpha_codes_list(alpha_codes_range=test_alpha_codes_range_2)   #NAM-PLW
        test_alpha_codes_range_output_list_2 = ['NA', 'NC', 'NE', 'NF', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG', 'PH', 'PK', 'PL', 'PM', 'PN', 'PR', 'PS', 'PT', 'PW']
        self.assertEqual(test_alpha_codes_range_ouput_2, (test_alpha_codes_range_output_list_2, 'NA-PW'), f"Expected and observed range of alpha codes do not match:\n{test_alpha_codes_range_ouput_2}.")
#7.)
        test_alpha_codes_range_ouput_3 = get_alpha_codes_list(alpha_codes_range=test_alpha_codes_range_3)   #ZW-VU
        test_alpha_codes_range_output_list_3 = ['VU', 'WF', 'WS', 'YE', 'YT', 'ZA', 'ZM', 'ZW']
        self.assertEqual(test_alpha_codes_range_ouput_3, (test_alpha_codes_range_output_list_3, 'VU-ZW'), f"Expected and observed range of alpha codes do not match:\n{test_alpha_codes_range_ouput_3}.")
#8.)
        test_alpha_codes_range_ouput_4 = get_alpha_codes_list(alpha_codes_range=test_alpha_codes_range_4)   #WLF-740
        test_alpha_codes_range_output_list_4 = ['SR', 'SS', 'ST', 'SV', 'SX', 'SY', 'SZ', 'TC', 'TD', 'TF', 'TG', 'TH', 'TJ', 'TK', 'TL', 'TM', 'TN', 'TO', 'TR', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 
            'UM', 'US', 'UY', 'UZ', 'VA', 'VC', 'VE', 'VG', 'VI', 'VN', 'VU', 'WF']
        self.assertEqual(test_alpha_codes_range_ouput_4, (test_alpha_codes_range_output_list_4, "SR-WF"), f"Expected and observed range of alpha codes do not match:\n{test_alpha_codes_range_ouput_4}.")
#9.)
        with self.assertRaises(ValueError):
            get_alpha_codes_list("ABC")
            get_alpha_codes_list("123")
            get_alpha_codes_list(alpha_codes_range="DEE-000")
#10.)
        with self.assertRaises(TypeError):
            get_alpha_codes_list(123)
            get_alpha_codes_list(False)
            get_alpha_codes_list(alpha_codes_range=["DE-FR"])

    # @unittest.skip("")
    def test_correct_columns(self):
        """ Testing function that corrects and aligns the column names for the export dataframe. """
        test_columns_1 = ["Changes", "Edition/Newsletter", "Newsletter", "Edition"]
        test_columns_2 = ["Publication", "Date of Change", "Date Issued", "Description of Change"]
        test_columns_3 = ["Effective date", "Short description of change (en)", "Short description of change", "Changes made"]
        test_columns_4 = ["Change", "Description of Change", "Date Issued", "Source"]
        test_columns_5 = []
#1.)
        test_columns_output_1 = correct_columns(test_columns_1)
        self.assertEqual(test_columns_output_1, ["Change", "Source", "Source", "Source"], 
            f"Expected and observed corrected columns does not match:\n{test_columns_output_1}.")
#2.)
        test_columns_output_2 = correct_columns(test_columns_2)
        self.assertEqual(test_columns_output_2, ["Source", "Date Issued", "Date Issued", "Description of Change"], 
            f"Expected and observed corrected columns does not match:\n{test_columns_output_2}.")
#3.)
        test_columns_output_3 = correct_columns(test_columns_3)
        self.assertEqual(test_columns_output_3, ["Date Issued", "Description of Change", "Description of Change", "Change"], 
            f"Expected and observed corrected columns does not match:\n{test_columns_output_3}.")
#4.)
        test_columns_output_4 = correct_columns(test_columns_4)
        self.assertEqual(test_columns_output_4, test_columns_4, 
            f"Expected and observed corrected columns does not match:\n{test_columns_output_4}.")
#5.)
        test_columns_output_5 = correct_columns(test_columns_5)
        self.assertEqual(test_columns_output_5, [], 
            f"Expected output of correct columns to be an empty array:\n{test_columns_output_5}.")
#6.)    
        with self.assertRaises(TypeError):
            correct_columns("Changes", "Edition/Newsletter", "Newsletter", "Edition")
            correct_columns(False)
            correct_columns(10.2)
    
    # @unittest.skip("")
    def test_table_to_array(self):
        """ Testing function that converts a 2D html table from wiki pages into array/list. """
        test_alpha2_ba = "BA" #Bosnia
        test_alpha2_eg = "EG" #Egypt
        test_alpha2_qa = "QA" #Qatar
        test_alpha2_rs = "RS" #Serbia
        test_alpha2_br = "BR" #Brazil, no listed changes/updates
        test_alpha2_pt = "PT" #Portugal, no listed changes/updates
        test_alpha2_error_1 = 12345 #should raise type error
        test_alpha2_error_2 = "abcdefg" #should raise type error
        test_alpha2_error_3 = False #should raise type error
        wiki_base_url = "https://en.wikipedia.org/wiki/ISO_3166-2:"
        user_agent = UserAgent()
        user_agent_header = user_agent.random
        #get html content from wiki of ISO page, convert html content into BS4 object,
        #...get Changes Section/Heading from soup, get table element from section
#1.)    
        soup = BeautifulSoup(requests.get(wiki_base_url + test_alpha2_ba, headers={"User-Agent": user_agent_header}, timeout=10).content, "html.parser") #Bosnia & Hez
        table_html = soup.find("h2", {"id": "Changes"}).find_next('table')   #gets the 1st Changes table, 2nd one isnt parsed
        ba_table = table_to_array(table_html, soup)

        ba_expected_output1 = ['ISO 3166-2:2007 - http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=39718.', 
            '2007-12-13.', "Second edition of ISO 3166-2 (this change was not announced in a newsletter) - 'Statoid Newsletter January 2008' - http://www.statoids.com/n0801.html.", 
            'Subdivisions added: 10 cantons.']
        ba_expected_output2 = ['Newsletter II-2 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf.', 
            '2010-06-30.', 'Addition of the country code prefix as the first code element, addition of names in administrative languages, \
                update of the administrative structure and of the list source.', 'Subdivisions added: BA-BRC Brčko Distrikt.']
        
        #removing any whitespace or newlines from expected and test outputs
        ba_expected_output1 = [entry.replace(" ", "") for entry in ba_expected_output1]
        ba_expected_output2 = [entry.replace(" ", "") for entry in ba_expected_output2]
        ba_test_output1 = [entry.replace(" ", "") for entry in ba_table[1]]
        ba_test_output2 = [entry.replace(" ", "") for entry in ba_table[2]]

        self.assertIsInstance(ba_table, list, f"Expected output table to be of type list, got {type(ba_table)}.")
        self.assertEqual(len(ba_table), 3, f"Expected there to be 3 elements in output table, got {len(ba_table)}.")
        self.assertListEqual(ba_table[0], ['Edition/Newsletter', 'Date issued', 'Description of change in newsletter', 'Code/Subdivision change'], 
            f"Expected columns/headers in observed and expected output to match:\n{ba_table[0]}.")
        self.assertEqual(ba_test_output1, ba_expected_output1, f"Expected and observed outputs do not match:\n{ba_test_output1}.")
        self.assertEqual(ba_test_output2, ba_expected_output2, f"Expected and observed outputs do not match:\n{ba_expected_output2}.")
#2.)
        soup = BeautifulSoup(requests.get(wiki_base_url + test_alpha2_eg, headers={"User-Agent": user_agent_header}, timeout=10).content, "html.parser") #Egypt
        table_html = soup.find("h2", {"id": "Changes"}).find_next('table')
        eg_table = table_to_array(table_html, soup)

        eg_expected_output1 = ['ISO 3166-2:2007 - http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=39718.', 
            '2007-12-13.', "Second edition of ISO 3166-2 (this change was not announced in a newsletter) - 'Statoid Newsletter January 2008' - http://www.statoids.com/n0801.html.", 
            'Subdivision added: EG-LX Al Uqşur.']
        eg_expected_output2 = ['Newsletter II-2 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf.', 
            '2010-06-30.', 'Update of the administrative structure and of the list source.', 'Subdivisions added: EG-SU As Sādis min Uktūbar. EG-HU Ḩulwān.']

        #removing any whitespace or newlines from expected and test outputs
        eg_expected_output1 = [entry.replace(" ", "") for entry in eg_expected_output1]
        eg_expected_output2 = [entry.replace(" ", "") for entry in eg_expected_output2]
        eg_test_output1 = [entry.replace(" ", "") for entry in eg_table[1]]
        eg_test_output2 = [entry.replace(" ", "") for entry in eg_table[2]]

        self.assertIsInstance(eg_table, list, f"Expected output table to be of type list, got {type(eg_table)}.")
        self.assertEqual(len(eg_table), 3, f"Expected there to be 2 elements in output table, got {len(eg_table)}.")
        self.assertListEqual(eg_table[0], ['Edition/Newsletter', 'Date issued', 'Description of change', 'Code/Subdivision change'], 
            f"Expected columns/headers in observed and expected output to match:\n{eg_table[0]}.")
        self.assertEqual(eg_test_output1, eg_expected_output1, f"Expected and observed outputs do not match:\n{eg_test_output1}.")
        self.assertEqual(eg_test_output2, eg_expected_output2, f"Expected and observed outputs do not match:\n{eg_test_output2}")
#3.)
        soup = BeautifulSoup(requests.get(wiki_base_url + test_alpha2_qa, headers={"User-Agent": user_agent_header}, timeout=10).content, "html.parser") #Qatar
        table_html = soup.find("h2", {"id": "Changes"}).find_next('table')
        qa_table = table_to_array(table_html, soup)

        qa_expected_output = ['Newsletter II-3 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf.',
                        '2011-12-13 (corrected. 2011-12-15).',
                        'Update resulting from the addition of names in administrative languages, and update of the administrative structure and of the list source.',
                        'Subdivisions added: QA-ZA Az̧ Za̧`āyin. Subdivisions deleted: QA-GH Al Ghuwayrīyah. QA-JU Al Jumaylīyah. QA-JB Jarīyān al Bāţnah.']

        #removing any whitespace or newlines from expected and test outputs
        qa_expected_output = [entry.replace(" ", "") for entry in qa_expected_output]
        qa_test_output = [entry.replace(" ", "") for entry in qa_table[1]]

        self.assertIsInstance(qa_table, list, f"Expected output table to be of type list, got {type(qa_table)}.")
        self.assertEqual(len(qa_table), 2, f"Expected there to be 2 elements in output table, got {len(qa_table)}.")
        self.assertListEqual(qa_table[0], ['Newsletter', 'Date issued', 'Description of change in newsletter', 'Code/Subdivision change'], 
            f"Expected columns/headers in observed and expected output to match:\n{qa_table[0]}.")
        self.assertEqual(qa_test_output, qa_expected_output, f"Expected and observed outputs do not match:\n{qa_test_output}")
#4.)
        soup = BeautifulSoup(requests.get(wiki_base_url + test_alpha2_rs, headers={"User-Agent": user_agent_header}, timeout=10).content, "html.parser") #Serbia
        table_html = soup.find("h2", {"id": "Changes"}).find_next('table')
        rs_table = table_to_array(table_html, soup)

        rs_expected_output1 = ['Newsletter I-8 - https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf.', 
            '2007-04-17.', 'Addition of a new country (in accordance with ISO 3166-1 Newsletter V-12).', 'Subdivisions added: 1 city, 2 autonomous republics, 29 districts.']
        rs_expected_output2 = ['Newsletter II-1 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-1_corrected_2010-02-19.pdf.', 
            '2010-02-03  (corrected. 2010-02-19).', 'Addition of the country code prefix as the first code element, administrative update.', '']
        
        #removing any whitespace or newlines from expected and test outputs
        rs_expected_output1 = [entry.replace(" ", "") for entry in rs_expected_output1]
        rs_expected_output2 = [entry.replace(" ", "") for entry in rs_expected_output2]
        rs_test_output1 = [entry.replace(" ", "") for entry in rs_table[1]]
        rs_test_output2 = [entry.replace(" ", "") for entry in rs_table[2]]

        self.assertIsInstance(rs_table, list, f"Expected output table to be of type list, got {type(rs_table)}.")
        self.assertEqual(len(rs_table), 3, f"Expected there to be 2 elements in output table, got {len(rs_table)}.")
        self.assertListEqual(rs_table[0], ['Newsletter', 'Date issued', 'Description of change in newsletter', 'Code/Subdivision change'], 
            f"Expected columns/headers in observed and expected output to match:\n{rs_table[0]}.")
        self.assertEqual(rs_test_output1, rs_expected_output1, f"Expected and observed outputs do not match:\n{rs_test_output1}.")
        self.assertEqual(rs_test_output2, rs_expected_output2, f"Expected and observed outputs do not match:\n{rs_test_output2}")
#5.)    
        soup = BeautifulSoup(requests.get(wiki_base_url + test_alpha2_br, headers={"User-Agent": user_agent_header}, timeout=10).content, "html.parser") #Brazil
        table_html = soup.find("span", {"id": "Changes"})
        br_table = table_to_array(table_html, soup)

        self.assertIsNone(table_html, "Table should be none as no listed changes/updates on wiki.")
        self.assertEqual(br_table, [], "Output from function should be empty array when input param is None.")
#6.)
        soup = BeautifulSoup(requests.get(wiki_base_url + test_alpha2_pt, headers={"User-Agent": user_agent_header}, timeout=10).content, "html.parser") #Portugal
        table_html = soup.find("span", {"id": "Changes"})
        test_table = table_to_array(table_html, soup)

        self.assertIsNone(table_html, "Table should be none as invalid alpha-2 code input.")
        self.assertEqual(test_table, [], "Output from function should be empty array when input param is None.")
#7.)
        with self.assertRaises(TypeError):
           table_to_array(test_alpha2_error_1, soup)
           table_to_array(test_alpha2_error_2, soup)
           table_to_array(test_alpha2_error_3, soup)

    # @unittest.skip("")
    def test_parse_date(self):
        """ Testing auxillary conversion function that converts a string date into YYYY-MM-DD format. """
        test_parse_date_1 = "2024-25-12"
        test_parse_date_2 = "14/02/1999"
        test_parse_date_3 = "29/1/2000"
        test_parse_date_4 = "05-05-2012"
        test_parse_date_5 = "15th January 2009"
        test_parse_date_6 = "23rd May 2024"
#1.)
        test_parse_date_output_1 = parse_date(test_parse_date_1)
        self.assertEqual(test_parse_date_output_1, "2024-12-25", 
            "Expected and observed output date format is not correct:\n{test_parse_date_output_1}.")
#2.)
        test_parse_date_output_2 = parse_date(test_parse_date_2)
        self.assertEqual(test_parse_date_output_2, "1999-02-14", 
            "Expected and observed output date format is not correct:\n{test_parse_date_output_2}.")
#3.)
        test_parse_date_output_3 = parse_date(test_parse_date_3)
        self.assertEqual(test_parse_date_output_3, "2000-01-29", 
            "Expected and observed output date format is not correct:\n{test_parse_date_output_3}.")
#4.)
        test_parse_date_output_4 = parse_date(test_parse_date_4)
        self.assertEqual(test_parse_date_output_4, "2012-05-05", 
            "Expected and observed output date format is not correct:\n{test_parse_date_output_4}.")
#5.)
        test_parse_date_output_5 = parse_date(test_parse_date_5)
        self.assertEqual(test_parse_date_output_5, "2009-01-15", 
            "Expected and observed output date format is not correct:\n{test_parse_date_output_5}.")
#6.)
        test_parse_date_output_6 = parse_date(test_parse_date_6)
        self.assertEqual(test_parse_date_output_6, "2024-05-23", 
            "Expected and observed output date format is not correct:\n{test_parse_date_output_6}.")
#7.)
        with self.assertRaises(ValueError):
            parse_date("20012-01-12")
            parse_date("99/16/04")
            parse_date("2001-2001-2001")
            parse_date("37th Shittember 2025")

    # @unittest.skip("")
    def test_get_year(self):
        """ Testing auxillary function that parses the year format from the Date Issued column. """
        test_get_year_1 = "2012-01-01"
        test_get_year_2 = "2008-12-21"
        test_get_year_3 = "2020-03-30"
        test_get_year_4 = "2021-05-16 (corrected 2022-06-16)"
        test_get_year_5 = "2023-11-20 (corrected 2024-11-22)"
#1.)
        test_get_year_output_1 = get_year(test_get_year_1) #2012-01-01
        self.assertEqual(test_get_year_output_1, 2012, 
            f"Expected year output of function to be 2012, got {test_get_year_output_1}.")
#2.)
        test_get_year_output_2 = get_year(test_get_year_2) #2008-12-21
        self.assertEqual(test_get_year_output_2, 2008, 
            f"Expected year output of function to be 2008, got {test_get_year_output_2}.")
#3.)
        test_get_year_output_3 = get_year(test_get_year_3) #2020-03-30
        self.assertEqual(test_get_year_output_3, 2020, 
            f"Expected year output of function to be 2020, got {test_get_year_output_3}.")
#4.)
        test_get_year_output_4 = get_year(test_get_year_4) #2021-05-16 (corrected 2022-06-16)
        self.assertEqual(test_get_year_output_4, 2021, 
            f"Expected year output of function to be 2021, got {test_get_year_output_4}.")
#5.)
        test_get_year_output_5 = get_year(test_get_year_5) #2023-11-20 (corrected 2024-11-22)
        self.assertEqual(test_get_year_output_5, 2023, 
            f"Expected year output of function to be 2023, got {test_get_year_output_5}.")

    # @unittest.skip("")
    def test_extract_corrected_date(self):
        """ Testing auxillary function that extracts the 'corrected' date from the Date Issued column. """
        test_extract_corrected_date_1 = "2011-02-02 (corrected 2011-02-09)"
        test_extract_corrected_date_2 = "2010-01-08 (corrected 2010-02-09)"
        test_extract_corrected_date_3 = "2020-03-30 (corrected 2025-06-17)"
        test_extract_corrected_date_4 = "2022-06-19"
        test_extract_corrected_date_5 = "1999-07-11"
        test_extract_corrected_date_6 = ""
#1.)
        test_extract_corrected_date_output_1 = extract_corrected_date(test_extract_corrected_date_1) #2011-02-02 (corrected 2011-02-09)
        self.assertEqual(test_extract_corrected_date_output_1, "(corrected 2011-02-09)", 
            f"Expected correct date of function to be 2011-02-09, got {test_extract_corrected_date_output_1}.")
#2.)
        test_extract_corrected_date_output_2 = extract_corrected_date(test_extract_corrected_date_2) #2010-01-08 (corrected 2010-02-09)
        self.assertEqual(test_extract_corrected_date_output_2, "(corrected 2010-02-09)", 
            f"Expected corrected date of function to be 2010-02-09, got {test_extract_corrected_date_output_2}.")
#3.)
        test_extract_corrected_date_output_3 = extract_corrected_date(test_extract_corrected_date_3) #2020-03-30 (corrected 2025-06-17)
        self.assertEqual(test_extract_corrected_date_output_3, "(corrected 2025-06-17)", 
            f"Expected corrected date of function to be 2025-06-17, got {test_extract_corrected_date_output_3}.")
#4.)
        test_extract_corrected_date_output_4 = extract_corrected_date(test_extract_corrected_date_4) #2022-06-19
        self.assertEqual(test_extract_corrected_date_output_4, "",  
            f"Expected corrected date of function to be an empty string, got {test_extract_corrected_date_output_4}.")
#5.)
        test_extract_corrected_date_output_5 = extract_corrected_date(test_extract_corrected_date_5) #1999-07-11
        self.assertEqual(test_extract_corrected_date_output_5, "", 
            f"Expected corrected date of function to be an empty string, got {test_extract_corrected_date_output_5}.")
#6.)
        test_extract_corrected_date_output_6 = extract_corrected_date(test_extract_corrected_date_6) #""
        self.assertEqual(test_extract_corrected_date_output_6, "", 
            f"Expected corrected date of function to be an empty string, got {test_extract_corrected_date_output_6}.")

    # @unittest.skip("")
    def test_remove_corrected_date(self):
        """ Testing auxillary function that removes the 'corrected' date from the Date Issued column. """
        test_remove_corrected_date_1 = "2013-04-11 (corrected 2013-06-12)"
        test_remove_corrected_date_2 = "2015-07-12 (corrected 2015-08-12)"
        test_remove_corrected_date_3 = "2005-02-18 (corrected 2005-09-18)"
        test_remove_corrected_date_4 = "2000-04-21 (corrected 2000-04-23)"
        test_remove_corrected_date_5 = "2012-06-22"
        test_remove_corrected_date_6 = "2015-09-24"
#1.)
        test_remove_corrected_date_output_1 = remove_corrected_date(test_remove_corrected_date_1)
        self.assertEqual(test_remove_corrected_date_output_1, "2013-04-11", 
            f"Expected output of function to be 2013-04-11, got {test_remove_corrected_date_output_1}.")
#2.)
        test_remove_corrected_date_output_2 = remove_corrected_date(test_remove_corrected_date_2)
        self.assertEqual(test_remove_corrected_date_output_2, "2015-07-12",
            f"Expected output of function to be 2015-07-12, got {test_remove_corrected_date_output_2}.")
#3.)
        test_remove_corrected_date_output_3 = remove_corrected_date(test_remove_corrected_date_3)
        self.assertEqual(test_remove_corrected_date_output_3, "2005-02-18",
            f"Expected output of function to be 2005-02-18, got {test_remove_corrected_date_output_3}.")
#4.)
        test_remove_corrected_date_output_4 = remove_corrected_date(test_remove_corrected_date_4)
        self.assertEqual(test_remove_corrected_date_output_4, "2000-04-21",
            f"Expected output of function to be 2000-04-21, got {test_remove_corrected_date_output_4}.")
#5.)
        test_remove_corrected_date_output_5 = remove_corrected_date(test_remove_corrected_date_5)
        self.assertEqual(test_remove_corrected_date_output_5, test_remove_corrected_date_5,
            f"Expected output of function to be 2012-06-22, got {test_remove_corrected_date_output_5}.")
#6.)
        test_remove_corrected_date_output_6 = remove_corrected_date(test_remove_corrected_date_6)
        self.assertEqual(test_remove_corrected_date_output_6, test_remove_corrected_date_6,
            f"Expected output of function to be 2015-09-24, got {test_remove_corrected_date_output_6}.")

    # @unittest.skip("")
    def test_remove_doublespacing(self):
        """ Testing auxillary function that removes any double spacing from column/string. """
        test_remove_doublespacing_1 = "double  spacing"
        test_remove_doublespacing_2 = "hello  there  blah  "
        test_remove_doublespacing_3 = " help  im double  spaced"
        test_remove_doublespacing_4 = "help im not double spaced woohoo"
        test_remove_doublespacing_5 = ""
#1.)
        test_remove_double_spacing_output_1 = remove_corrected_date(test_remove_doublespacing_1)
        self.assertEqual(test_remove_double_spacing_output_1, "double spacing",
            f"Expected output of function to have all double spacing removed, got {test_remove_double_spacing_output_1}.")
#2.)
        test_remove_double_spacing_output_2 = remove_corrected_date(test_remove_doublespacing_2)
        self.assertEqual(test_remove_double_spacing_output_2, "hello there blah",
            f"Expected output of function to have all double spacing removed, got {test_remove_double_spacing_output_2}.")
#3.)
        test_remove_double_spacing_output_3 = remove_corrected_date(test_remove_doublespacing_3)
        self.assertEqual(test_remove_double_spacing_output_3, "help im double spaced",
            f"Expected output of function to have all double spacing removed, got {test_remove_double_spacing_output_3}.")
#4.)
        test_remove_double_spacing_output_4 = remove_corrected_date(test_remove_doublespacing_4)
        self.assertEqual(test_remove_double_spacing_output_4, "help im not double spaced woohoo",
            f"Expected output of function to have all double spacing removed, got {test_remove_double_spacing_output_4}.")
#5.)
        test_remove_double_spacing_output_5 = remove_corrected_date(test_remove_doublespacing_5)
        self.assertEqual(test_remove_double_spacing_output_5, "",
            f"Expected output of function to have all double spacing removed, got {test_remove_double_spacing_output_5}.")

    # @unittest.skip("")
    def test_export_updates(self):
        """ Testing functionality for exporting the exported updates data to the JSON and CSV. """
#1.)    
        export_updates({"AD": self.iso3166_data["AD"]}, export_folder=self.test_export_folder, export_filename="test-iso3166-export-1", export_json=True, export_csv=True)
        
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, "test-iso3166-export-1.json")), "Expected JSON export file to be in test folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, "test-iso3166-export-1.csv")), "Expected CSV export file to be in test folder.")

        with open(os.path.join(self.test_export_folder, "test-iso3166-export-1.json")) as output_json:
            test_export_updates_ad_json = json.load(output_json)
        ad_expected_json = {'AD': [{'Change': 'Update List Source.', 'Description of Change': '', 'Date Issued': '2015-11-27', 
                'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD.'}, 
                {'Change': 'Update List Source.', 'Description of Change': '', 'Date Issued': '2014-11-03', 
                 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD.'}, 
                 {'Change': 'Subdivisions added: 7 parishes.', 'Description of Change': 'Addition of the administrative subdivisions and of their code elements.', 
                  'Date Issued': '2007-04-17', 'Source': 'Newsletter I-8 - https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf.'}]}

        self.assertEqual(test_export_updates_ad_json, ad_expected_json, f"Observed and expected output dicts do not match:\n{test_export_updates_ad_json}")
#2.)
        test_export_updates_co_ec_fi = {"CO": self.iso3166_data["CO"], "EC": self.iso3166_data["EC"], "FI": self.iso3166_data["FI"]}
        export_updates(test_export_updates_co_ec_fi, export_folder=self.test_export_folder, export_filename="test-iso3166-export-2", export_json=True, export_csv=True)

        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, "test-iso3166-export-2.json")), "Expected JSON export file to be in test folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, "test-iso3166-export-2.csv")), "Expected CSV export file to be in test folder.")

        with open(os.path.join(self.test_export_folder, "test-iso3166-export-2.json")) as output_json:
            test_export_updates_co_ec_fi_json = json.load(output_json)
        co_ec_fi_expected_json = {'CO': [{'Change': 'Addition of local variation of CO-DC, CO-SAP, CO-VAC; update list source.', 'Description of Change': '', 'Date Issued': '2016-11-15', 
                'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CO.'}, 
                {'Change': 'Change of name of CO-DC.', 'Description of Change': '', 'Date Issued': '2004-03-08', 
                'Source': 'Newsletter I-6 - https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf.'}], 
                'EC': [{'Change': 'Change of spelling of EC-S, EC-Z; update List Source.', 'Description of Change': '', 'Date Issued': '2017-11-23', 
                'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:EC.'}, 
                {'Change': 'Subdivisions added: EC-SE Santa Elena. EC-SD Santo Domingo de los Tsáchilas.', 
                'Description of Change': 'Update of the administrative structure and of the list source.', 'Date Issued': '2010-06-30', 
                'Source': 'Newsletter II-2 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf.'}, 
                {'Change': 'Subdivisions added: EC-D Orellana.', 'Description of Change': 'Addition of one province.', 'Date Issued': '2002-12-10', 
                'Source': 'Newsletter I-4 - https://web.archive.org/web/20081218103210/http://www.iso.org/iso/iso_3166-2_newsletter_i-4_en.pdf.'}], 
                'FI': [{'Change': 'Name change: Satakunda -> Satakunta.', 'Description of Change': 'Change of spelling of FI-17; Update List Source.', 
                'Date Issued': '2022-11-29', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:FI.'}, 
                {'Change': 'Update Code Source.', 'Description of Change': '', 'Date Issued': '2016-11-15', 
                'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:FI.'}, 
                {'Change': 'Subdivision layout: 6 provinces -> 19 regions.', 
                'Description of Change': 'Administrative re-organization, deletion of useless information and the region names in English and French, source list and source code update.', 
                'Date Issued': '2011-12-13 (corrected 2011-12-15)', 'Source': "Newsletter II-3 - 'Changes in the list of subdivision names and code elements' - http://www.iso.org/iso/iso_3166-2_newsletter_ii-3_2011-12-13.pdf."}]}

        self.assertEqual(test_export_updates_co_ec_fi_json, co_ec_fi_expected_json, f"Observed and expected output dicts do not match:\n{test_export_updates_co_ec_fi_json}")
#3.)
        export_updates({"SK": self.iso3166_data["SK"]}, export_folder=self.test_export_folder, export_filename="test-iso3166-export-3", export_json=True, export_csv=True)
        
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, "test-iso3166-export-3.json")), "Expected JSON export file to be in test folder.")
        self.assertFalse(os.path.isfile(os.path.join(self.test_export_folder, "test-iso3166-export-3.csv")), "Expected CSV export file to be in test folder.")

        with open(os.path.join(self.test_export_folder, "test-iso3166-export-3.json")) as output_json:
            test_export_updates_sk_json = json.load(output_json)

        self.assertEqual(test_export_updates_sk_json, {"SK": []}, f"Observed and expected output dicts do not match:\n{test_export_updates_sk_json}")

    # @unittest.skip("")
    def test_remove_duplicates(self):
        """ Testing the functionality that removes duplicate objects from the dataframe export. """
#1.) Simple Duplicate (should remove the first entry and keep the corrected one)
        df_test_1 = pd.DataFrame([
            {
                "Change": "Addition of the country code prefix as the first code element.",
                "Description of Change": "",
                "Date Issued": "2010-02-19",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:IE."
            },
            {
                "Change": "Addition of the country code prefix as the first code element.",
                "Description of Change": "",
                "Date Issued": "2010-02-03 (corrected 2010-02-19)",
                "Source": "Newsletter II-1 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-1_corrected_2010-02-19.pdf."
            }
        ])

        result = remove_duplicates(df_test_1)
        self.assertEqual(len(result), 1, f"Expected one object in output, got {len(result)}.")
        self.assertTrue("corrected" in result.iloc[0]["Date Issued"], "Expected 'corrected' to be in Date Issued attribute.")
#2.) No Duplicates (output should be same as input)
        df_test_2 = pd.DataFrame([
            {
                "Change": "New subdivision added.",
                "Description of Change": "A new administrative division has been introduced.",
                "Date Issued": "2021-08-15",
                "Source": "Newsletter VI-5 - https://www.iso.org/newsletter_2021-08-15.pdf."
            },
            {
                "Change": "Subdivision name update.",
                "Description of Change": "Updated the name of a region.",
                "Date Issued": "2020-06-30",
                "Source": "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:US."
            }
        ])

        result = remove_duplicates(df_test_2)
        self.assertEqual(len(result), len(df_test_2), "Expected the object to be the same length, no duplicates found.")
#3.) Multiple Duplicates with Corrected Dates (should keep the more complete versions)
        df_test_3 = pd.DataFrame([
            {
                "Change": "Code reassigned.",
                "Description of Change": "",
                "Date Issued": "2015-04-10",
                "Source": "Online Browsing Platform (OBP)."
            },
            {
                "Change": "Code reassigned.",
                "Description of Change": "",
                "Date Issued": "2015-03-20 (corrected 2015-04-10)",
                "Source": "Newsletter III-2 - https://www.iso.org/newsletter_2015-04-10.pdf."
            },
            {
                "Change": "Minor subdivision adjustment.",
                "Description of Change": "Updated borders.",
                "Date Issued": "2018-12-01",
                "Source": "Online Browsing Platform (OBP)."
            }
        ])

        result = remove_duplicates(df_test_3)
        self.assertEqual(len(result), 2, f"Expected two objects in output, got {len(result)}.")
        self.assertTrue("corrected" in result.iloc[0]["Date Issued"], "Expected 'corrected' to be in Date Issued attribute.")
#4.) Duplicate Without Corrected Date (should keep the one with more details, such as Desc of Change value)
        df_test_4 = pd.DataFrame([
            {
                "Change": "Territory name change.",
                "Description of Change": "",
                "Date Issued": "2013-07-01",
                "Source": ""
            },
            {
                "Change": "Territory name change.",
                "Description of Change": "Region renamed for administrative reasons.",
                "Date Issued": "2013-07-01",
                "Source": "Newsletter IV-3 - https://www.iso.org/newsletter_2013-07-01.pdf."
            }
        ])

        result = remove_duplicates(df_test_4)
        self.assertEqual(len(result), 1, f"Expected one object in output, got {len(result)}.")
        # self.assertEqual(result.iloc[0]["Description of Change"], "Region renamed for administrative reasons.", 
            # "Expected output result to contain the object with a Desc of Change value.")
#5.) Identical Entries (only one should remain)
        df_test_5 = pd.DataFrame([
            {
                "Change": "Added new province.",
                "Description of Change": "Created a new administrative region.",
                "Date Issued": "2022-09-15",
                "Source": "Newsletter VII-8 - https://www.iso.org/newsletter_2022-09-15.pdf."
            },
            {
                "Change": "Added new province.",
                "Description of Change": "Created a new administrative region.",
                "Date Issued": "2022-09-15",
                "Source": "Newsletter VII-8 - https://www.iso.org/newsletter_2022-09-15.pdf."
            }
        ])

        result = remove_duplicates(df_test_5)
        self.assertEqual(len(result), 1, f"Expected one object in output, got {len(result)}.")

    def tearDown(self):
        """ Delete test directory. """
        shutil.rmtree(self.test_export_folder)