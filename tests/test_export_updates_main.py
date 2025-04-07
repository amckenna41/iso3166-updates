try:
    from iso3166_updates_export.main import *
except:
    from ..iso3166_updates_export.main import *
import shutil
import pandas as pd
import os
from datetime import datetime
import unittest
unittest.TestLoader.sortTestMethodsUsing = None

class ISO3166_Export_Updates_Main_Tests(unittest.TestCase):
    """
    Test suite for testing the main entry module for exporting the updates data. 
    The module has the get_iso3166_updates function that executes the full pipeline 
    for exporting the data. The function can accept a range of parameters including 
    individual or a list of alpha codes and years

    Test Cases
    ==========
    test_get_iso3166_updates_alpha:
        testing the main entry function for the full export updates pipeline,
        using a variety of alpha country codes.
    test_get_iso3166_updates_year:
        testing the main entry function for the full export updates pipeline,
        using a variety of years.
    test_get_iso3166_updates_alpha_year:
        testing the main entry function for the full export updates pipeline,
        using a variety of alpha country codes and years.
    test_alpha_codes_range:
        testing the main entry function for the full export updates pipeline,
        using a range of alpha codes via the alpha_codes_range parameter.
    test_save_each_iteration:
        testing the main entry function for the full export updates pipeline,
        and the parameter that saves each export's data per iteration.
    """
    def setUp(self):
        """ Initialise test variables, import json. """
        #temp filename & dir exports
        self.test_export_filename = "test_iso3166_updates"
        self.test_export_folder = os.path.join("tests", "temp_test_dir")
        
        #output columns from various functions
        self.expected_output_columns = ["Change", "Description of Change", "Date Issued", "Source"]

        #create temp dir to store any function outputs
        if not (os.path.isdir(self.test_export_folder)):
            os.mkdir(self.test_export_folder)

        #turn off tqdm progress bar functionality when running tests
        os.environ["TQDM_DISABLE"] = "1"

    @unittest.skip("")
    def test_get_iso3166_updates_alpha(self):
        """ Testing main updates function that gets the updates and exports to json/csv, using
            a variety of ISO 3166-1 alpha country code input parameter values. """
        test_alpha_au = "AU" #Australia
        test_alpha_cv = "CV" #Cabo Verde
        test_alpha_id_io = "IDN,IOT " #Indonesia, British Indian Ocean Territory
        test_alpha_sk = "703" #Slovakia ({})
        test_alpha_bf_ca_gu_ie_je = "BF, CAN, GUM, 372, 832" #Burkina Faso, Canada, Guam, Ireland, Jersey - concat_updates=False
        test_alpha_error_1 = 12345 #should raise type error
        test_alpha_error_2 = False #should raise type error
        test_alpha_error_3 = ["HU,MV,ZA"] #should raise Type error
        test_alpha_error_4 = "XYZ" #should raise value error
        test_alpha_error_5 = "AD,DE,PP" #should raise value error
        test_alpha_error_6 = "invalid_alpha_code" #should raise value error
#1.) 
        test_alpha_au_updates = get_iso3166_updates(alpha_codes=test_alpha_au, export_filename=self.test_export_filename, export_folder=self.test_export_folder, 
                concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=True)   #Australia
        test_au_expected = {"AU": [{'Change': 'Update List Source; update Code Source.', 'Description of Change': '', 'Date Issued': '2016-11-15', 
            'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AU.'}, 
            {'Change': 'Update List Source.', 'Description of Change': '', 'Date Issued': '2015-11-27', 
            'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AU.'}, 
            {'Change': 'Codes: New South Wales: AU-NS -> AU-NSW. Queensland: AU-QL -> AU-QLD. Tasmania: AU-TS -> AU-TAS. Victoria: AU-VI -> AU-VIC. Australian Capital Territory: AU-CT -> AU-ACT.', 
            'Description of Change': 'Change of subdivision code in accordance with Australian Standard AS 4212-1994.', 'Date Issued': '2004-03-08', 
            'Source': 'Newsletter I-6 - https://web.archive.org/web/20081218103224/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf.'}]}
        # use_selenium=False - Output when just using Wiki page data
        # test_au_expected = [{'Change': 'Update List Source; update Code Source.', 'Description of Change': '', 'Date Issued': '2016-11-15', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AU.'}, 
        #     {'Change': 'Update List Source.', 'Description of Change': '', 'Date Issued': '2015-11-27', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AU.'}, 
        #     {'Change': 'Codes: New South Wales: AU-NS -> AU-NSW Queensland: AU-QL -> AU-QLD Tasmania: AU-TS -> AU-TAS Victoria: AU-VI -> AU-VIC Australian Capital Territory: AU-CT -> AU-ACT.', 
        #     'Description of Change': 'Change of subdivision code in accordance with Australian Standard AS 4212-1994.', 'Date Issued': '2004-03-08', 
        #     'Source': 'Newsletter I-6 - https://web.archive.org/web/20081218103224/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf.'}]       #use_selenium=False

        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_AU.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_AU.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(list(test_alpha_au_updates), ['AU'], 
            f"Expected AU key to be in updates output object:\n{list(test_alpha_au_updates)}.") 
        self.assertEqual(len(list(test_alpha_au_updates["AU"])), 3,
            f"Expected there to be 3 output objects in output object, got {len(list(test_alpha_au_updates))}.")
        for row in test_alpha_au_updates["AU"]:
            self.assertEqual(list(row.keys()), self.expected_output_columns, f"Columns from output do not match expected:\n{list(row.keys()),}")
            self.assertIsInstance(row, dict, f"Ouput object should be of type dict, got {type(row)}.")        
        self.assertEqual(test_alpha_au_updates, test_au_expected, f"Expected and observed outputs do not match:\n{test_alpha_au_updates}.")

        test_au_iso3166_csv = pd.read_csv(os.path.join(self.test_export_folder, self.test_export_filename + "_AU.csv")).fillna("")
        self.assertEqual(list(test_au_iso3166_csv.columns), self.expected_output_columns, 
            f"Observed and expected output columns do not match:\n{list(test_au_iso3166_csv.columns)}.")
        self.assertEqual(len(test_au_iso3166_csv), 3, 
            f"Expected there to be 3 output objects in csv, got {len(test_au_iso3166_csv)}.")
        self.assertEqual(test_au_iso3166_csv.to_dict(orient='records'), test_au_expected["AU"], 
            f"Expected and observed outputs do not match:\n{test_au_iso3166_csv.to_dict(orient='records')}")
#2.)  
        test_alpha_cv_updates = get_iso3166_updates(test_alpha_cv, export_filename=self.test_export_filename, export_folder=self.test_export_folder, 
                concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=True)   #Cabo Verde
        test_cv_expected = {'CV': [{'Change': 'Correction of the Code Source.', 'Description of Change': '', 'Date Issued': '2020-11-24', 
            'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CV.'}, 
            {'Change': 'Modification of the French remark.', 'Description of Change': '', 'Date Issued': '2014-03-03', 
            'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CV.'}, 
            {'Change': 'UN notification of name change for both short and full names.', 'Description of Change': '', 'Date Issued': '2013-11-26', 
            'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CV.'}, 
            {'Change': 'Codes: São Lourenço dos Órgãos CV-SL -> CV-SO.', 'Description of Change': 'Correction of NL II-2 for toponyms and typographical errors and source list update.', 
            'Date Issued': '2011-12-13 (corrected 2011-12-15)', 'Source': 'Newsletter II-3 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf.'}, 
            {'Change': 'Subdivisions added: CV-RB Ribeira Brava. CV-RS Ribeira Grande de Santiago. CV-CF Santa Catarina do Fogo. CV-SL São Lourenço dos Órgãos. CV-SS São Salvador do Mundo. CV-TS Tarrafal de São Nicolau. Subdivisions deleted: CV-SN São Nicolau. Codes: CV-CS Calheta de São Miguel -> CV-SM São Miguel.', 
            'Description of Change': 'Addition of the country code prefix as the first code element, update of the administrative structure and of the list source.', 'Date Issued': '2010-06-30', 
            'Source': 'Newsletter II-2 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf.'}, 
            {'Change': 'Subdivisions added: CV-CS Calheta de São Miguel. CV-MO Mosteiros. CV-SF São Filipe.', 'Description of Change': 'Subdivision layout partially revised: Three new municipalities. New reference for list source.', 
        'Date Issued': '2002-05-21', 'Source': 'Newsletter I-2 - https://web.archive.org/web/20120131102127/http://www.iso.org/iso/iso_3166-2_newsletter_i-2_en.pdf.'}]}
        # use_selenium=False - Output when just using Wiki page data
        # test_cv_expected = [{'Change': 'Codes: São Lourenço dos Órgãos CV-SL -> CV-SO.', 'Description of Change': 'Correction of NL II-2 for toponyms and typographical errors and source list update.', 'Date Issued': '2011-12-13 (corrected 2011-12-15)', 
        #     'Source': 'Newsletter II-3 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf.'}, {'Change': 'Subdivisions added: CV-RB Ribeira Brava CV-RS Ribeira Grande de Santiago CV-CF Santa Catarina do Fogo CV-SL São Lourenço dos \
        #     Órgãos CV-SS São Salvador do Mundo CV-TS Tarrafal de São Nicolau Subdivisions deleted: CV-SN São Nicolau Codes: CV-CS Calheta de São Miguel -> CV-SM São Miguel.', 'Description of Change': 'Addition of the country code prefix as the first code element, update of the administrative \
        #     structure and of the list source.', 'Date Issued': '2010-06-30', 'Source': 'Newsletter II-2 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf.'}, {'Change': 'Subdivisions added: CV-CS Calheta de São Miguel CV-MO Mosteiros CV-SF São Filipe.', 
        #     'Description of Change': 'Subdivision layout partially revised: Three new municipalities. New reference for list source.', 'Date Issued': '2002-05-21', 'Source': 'Newsletter I-2 - https://web.archive.org/web/20120131102127/http://www.iso.org/iso/iso_3166-2_newsletter_i-2_en.pdf.'}]} #use_selenium=False

        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_CV.csv")),
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_CV.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(list(test_alpha_cv_updates), ['CV'],
            f"Expected CV key to be in updates output object:\n{list(test_alpha_cv_updates)}.") 
        self.assertEqual(len(list(test_alpha_cv_updates["CV"])), 6, 
            f"Expected there to be 6 output objects in output object, got {len(list(test_alpha_cv_updates['CV']))}.")
        for row in test_alpha_cv_updates["CV"]:
            self.assertEqual(list(row.keys()), self.expected_output_columns, f"Columns from output do not match expected:\n{list(row.keys())}")
            self.assertIsInstance(row, dict, f"Ouput object should be of type dict, got {type(row)}.")
        self.assertEqual(test_alpha_cv_updates, test_cv_expected, f"Expected and observed outputs do not match:\n{test_alpha_cv_updates}.")

        test_cv_iso3166_csv = pd.read_csv(os.path.join(self.test_export_folder, self.test_export_filename + "_CV.csv")).fillna("")
        self.assertEqual(list(test_cv_iso3166_csv.columns), self.expected_output_columns, 
            f"Observed and expected output columns do not match:\n{list(test_cv_iso3166_csv.columns)}.")
        self.assertEqual(len(test_cv_iso3166_csv), 6, 
            f"Expected there to be 6 output objects in csv, got {len(test_cv_iso3166_csv)}.")
        self.assertEqual(test_cv_iso3166_csv.to_dict(orient='records'), test_cv_expected["CV"],
            f"Expected and observed outputs do not match:\n{test_cv_iso3166_csv.to_dict(orient='records')}")
#3.)
        test_alpha_id_io_updates = get_iso3166_updates(test_alpha_id_io, export_filename=self.test_export_filename, export_folder=self.test_export_folder, 
                export_json=True, export_csv=True, verbose=0, use_selenium=True)    #Indonesia, British Indian Ocean Territory
        test_id_io_expected = {'ID': [{'Change': 'Addition of province ID-PD; Update List Source.', 'Description of Change': '', 'Date Issued': '2023-11-23', 
            'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:ID.'}, 
            {'Change': 'Addition of provinces ID-PE, ID-PS and ID-PT; Update List Source.', 'Description of Change': '', 'Date Issued': '2022-11-29', 
            'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:ID.'}, 
            {'Change': 'Correction of the Code Source.', 'Description of Change': '', 'Date Issued': '2020-11-24', 
            'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:ID.'}, 
            {'Change': 'Change of spelling of category name in eng/fra from special district to capital district (ID-JK); change of category name from autonomous province to province for ID-AC; deletion of category autonomous province (eng) / province autonome (fra) / nanggroe (ind); update List Source.', 
            'Description of Change': '', 'Date Issued': '2017-11-23', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:ID.'}, 
            {'Change': 'Addition of local variation of ID-JK, ID-YO; change of spelling of ID-BB, update list source.', 'Description of Change': '', 
            'Date Issued': '2016-11-15', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:ID.'}, 
            {'Change': 'Update List Source.', 'Description of Change': '', 'Date Issued': '2015-11-27', 
            'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:ID.'}, 
            {'Change': 'Add province ID-KU; change code for Papua formerly ID-IJ; update List Source.', 'Description of Change': '', 
            'Date Issued': '2014-10-30', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:ID.'}, 
            {'Change': 'Codes: Maluku (geographical unit) ID-MA -> ID-ML.', 'Description of Change': 'Removal of duplicate code.', 
            'Date Issued': '2011-12-13 (corrected 2011-12-15)', 'Source': 'Newsletter II-3 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf.'}, 
            {'Change': 'Subdivisions added: ID-PB Papua Barat.', 'Description of Change': 'Addition of the country code prefix as the first code element, alphabetical re-ordering, administrative update.', 
            'Date Issued': '2010-02-03 (corrected 2010-02-19)', 'Source': 'Newsletter II-1 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-1_corrected_2010-02-19.pdf.'}, 
            {'Change': 'Subdivisions added: ID-SR Sulawesi Barat.', 'Description of Change': "Addition of a new province 'Sulawesi Barat'.", 'Date Issued': '2005-09-13', 
            'Source': 'Newsletter I-7 - https://web.archive.org/web/20081218103217/http://www.iso.org/iso/iso_3166-2_newsletter_i-7_en.pdf.'}, 
            {'Change': 'Subdivisions added: ID-KR Kepulauan Riau.', 'Description of Change': "Move 'Aceh' to a new category of 'autonomous province'. Addition of a new province 'Kepulauan Riau'.", 
            'Date Issued': '2004-03-08', 'Source': 'Newsletter I-6 - https://web.archive.org/web/20120112041245/http://www.iso.org/iso/iso_3166-2_newsletter_i-6_en.pdf.'}, 
            {'Change': 'Change of name of one geographical unit.', 'Description of Change': '', 'Date Issued': '2002-12-10', 
            'Source': 'Newsletter I-4 - https://web.archive.org/web/20081218103210/http://www.iso.org/iso/iso_3166-2_newsletter_i-4_en.pdf.'}, 
            {'Change': 'Subdivisions added: ID-BB Bangka Belitung. ID-BT Banten. ID-GO Gorontalo. ID-MU Maluku Utara. Subdivisions deleted: ID-TT Timor Timur (see ISO 3166-2:TL). Codes: (to correct duplicate use). ID-IJ Irian Jaya (province) -> ID-PA Papua.', 
            'Description of Change': 'Addition of four new provinces and deletion of one (ID-TT). Inclusion of one alternative name form and one changed province name (ID-PA, formerly ID-IJ).', 'Date Issued': '2002-05-21', 
            'Source': 'Newsletter I-2 - https://web.archive.org/web/20120131102127/http://www.iso.org/iso/iso_3166-2_newsletter_i-2_en.pdf.'}],
            'IO': [{'Change': 'Modification of remark part 2. (Remark part 2: No subdivisions relevant for this standard).', 'Description of Change': '', 'Date Issued': '2018-11-26', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:IO.'}]}
        # test_id_expected = [{}] #use_selenium=False

        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_ID,IO.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_ID,IO.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(list(test_alpha_id_io_updates), ['ID', 'IO'],
            f"Expected ID and IO keys to be in updates output object:\n{list(test_alpha_id_io_updates)}.") 
        self.assertEqual(len(list(test_alpha_id_io_updates["ID"])), 13, 
            f"Expected there to be 13 output objects in updates object, got {len(list(test_alpha_id_io_updates['ID']))}.")
        self.assertEqual(len(list(test_alpha_id_io_updates["IO"])), 1, 
            f"Expected there to be 1 output object in updates object, got {len(list(test_alpha_id_io_updates['IO']))}.")
        self.assertEqual(test_alpha_id_io_updates, test_id_io_expected, f"Expected and observed outputs do not match:\n{test_alpha_id_io_updates}")

        test_id_io_iso3166_csv = pd.read_csv(os.path.join(self.test_export_folder, self.test_export_filename + "_ID,IO.csv")).fillna("")
        self.assertEqual(list(test_id_io_iso3166_csv.columns), ["Country Code"] + self.expected_output_columns,
            f"Observed and expected output columns do not match:\n{list(test_id_io_iso3166_csv.columns)}")
        self.assertEqual(len(test_id_io_iso3166_csv), 14, 
            f"Expected there to be 14 output objects in csv, got {len(list(test_id_io_iso3166_csv))}.")
        # self.assertEqual(test_id_io_iso3166_csv.to_dict(orient='records'), test_id_io_expected,
        #     f"Expected and observed outputs do not match:\n{test_id_io_iso3166_csv.to_dict(orient='records')}")
#4.)
        test_alpha_sk_updates = get_iso3166_updates(test_alpha_sk, export_filename=self.test_export_filename, export_folder=self.test_export_folder, 
                export_json=True, export_csv=True, verbose=0, use_selenium=True)   #Slovakia
        test_sk_expected = {"SK": []}

        self.assertFalse(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_SK.csv")),
            "Expected output CSV file to not exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_SK.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(list(test_alpha_sk_updates), ['SK'],
            f"Expected SK key to be in updates output object:\n{list(test_alpha_sk_updates)}.") 
        with open(os.path.join(self.test_export_folder, self.test_export_filename + "_SK.json")) as output_json:
            test_alpha_sk_updates_json = json.load(output_json)
        self.assertEqual(test_alpha_sk_updates_json, test_sk_expected, f"Expected and observed outputs do not match:\n{test_alpha_sk_updates_json}")
#5.)
        test_alpha_bf_ca_gu_ie_je_updates = get_iso3166_updates(test_alpha_bf_ca_gu_ie_je, export_filename=self.test_export_filename, 
                export_folder=self.test_export_folder, concat_updates=False, export_json=True, export_csv=True, verbose=0, use_selenium=True)  #concat_updates=False, individual output files
        
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_BF.json")),
            "Expected output JSON file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_CA.json")),
            "Expected output JSON file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_GU.json")),
            "Expected output JSON file to not exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_IE.json")),
            "Expected output JSON file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_JE.json")),
            "Expected output JSON file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_BF.csv")),
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_CA.csv")),
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_GU.csv")),
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_IE.csv")),
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_JE.csv")),
            "Expected output CSV file to exist in folder.")
        
        self.assertEqual(list(test_alpha_bf_ca_gu_ie_je_updates), ['BF', 'CA', 'GU', 'IE', 'JE'],
            f"Expected BF, CA, GU, IE, JE keys to be in updates output object:\n{list(test_alpha_bf_ca_gu_ie_je_updates)}") 
        self.assertEqual(len(list(test_alpha_bf_ca_gu_ie_je_updates["BF"])), 3, 
            f"Expected there to be 3 output objects, got {len(list(test_alpha_bf_ca_gu_ie_je_updates['BF']))}.")
        self.assertEqual(len(list(test_alpha_bf_ca_gu_ie_je_updates["CA"])), 4, 
            f"Expected there to be 4 output objects, got {len(list(test_alpha_bf_ca_gu_ie_je_updates['CA']))}.")
        self.assertEqual(len(list(test_alpha_bf_ca_gu_ie_je_updates["GU"])), 1, 
            f"Expected there to be 1 output object, got {len(list(test_alpha_bf_ca_gu_ie_je_updates['GU']))}.")
        self.assertEqual(len(list(test_alpha_bf_ca_gu_ie_je_updates["IE"])), 4, 
            f"Expected there to be 4 output objects, got {len(list(test_alpha_bf_ca_gu_ie_je_updates['IE']))}.")
        self.assertEqual(len(list(test_alpha_bf_ca_gu_ie_je_updates["JE"])), 3, 
            f"Expected there to be 3 output object, got {len(list(test_alpha_bf_ca_gu_ie_je_updates['JE']))}.")
        for code in test_alpha_bf_ca_gu_ie_je_updates:
            for row in test_alpha_bf_ca_gu_ie_je_updates[code]:
                self.assertEqual(list(row.keys()), self.expected_output_columns, f"Columns from output do not match expected:\n{list(row.keys())}")
                self.assertIsInstance(row, dict, f"Ouput object row should be of type dict, got {type(row)}.")
#6.)    
        test_alpha_bf_ca_gu_ie_je_updates = get_iso3166_updates(test_alpha_bf_ca_gu_ie_je, export_filename=self.test_export_filename, 
            export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)  #Burkina Faso, Canada, Guam, Ireland, Jersey - concat_updates=True, one output file

        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_BF,CA,GU,IE,JE.json")), 
            f"Output file {os.path.join(self.test_export_filename + '-BF,CA,GU,IE,JE.json')} not found in export folder {self.test_export_folder}.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_BF,CA,GU,IE,JE.csv")), 
            f"Output file {os.path.join(self.test_export_filename + '-BF,CA,GU,IE,JE.csv')} not found in export folder {self.test_export_folder}.")

        #open exported BF,CA,GU,IE,JE json
        with open(os.path.join(self.test_export_folder, self.test_export_filename + "_BF,CA,GU,IE,JE.json")) as output_json:
            test_bf_ca_gu_ie_je_iso3166_json = json.load(output_json)
        self.assertEqual(len(list(test_bf_ca_gu_ie_je_iso3166_json)), 5, 
            f"Expected there to be 5 output objects in json, got {len(list(test_bf_ca_gu_ie_je_iso3166_json))}.")
        self.assertEqual(list(test_bf_ca_gu_ie_je_iso3166_json), ["BF", "CA", "GU", "IE", "JE"], 
            f"Expected keys of JSON to be BF, CA, GU, IE, JE, got {list(test_bf_ca_gu_ie_je_iso3166_json)}.")
        
        #open exported BF,CA,GU,IE,JE csv
        test_bf_ca_gu_ie_je_iso3166_csv = pd.read_csv(os.path.join(self.test_export_folder, self.test_export_filename + "_BF,CA,GU,IE,JE.csv")).fillna("")
        self.assertEqual(len(test_bf_ca_gu_ie_je_iso3166_csv), 10, 
            f"Expected there to be 10 outputs in CSV, got {len(test_bf_ca_gu_ie_je_iso3166_csv)}.")
        self.assertEqual(list(test_bf_ca_gu_ie_je_iso3166_csv["Country Code"].unique()), ["BF", "CA", "IE", "JE"],
            f"Expected and observed column values for Country Code column do not match:\n{test_bf_ca_gu_ie_je_iso3166_csv['Country Code']}.")
        self.assertTrue(set(["Country Code"] + self.expected_output_columns) == set(list(test_bf_ca_gu_ie_je_iso3166_csv.columns)),
            f"Column names/headers do not match expected:\n{set(list(test_bf_ca_gu_ie_je_iso3166_csv.columns))}.")
#7.)
        with self.assertRaises(TypeError):
            get_iso3166_updates(test_alpha_error_1)
            get_iso3166_updates(test_alpha_error_2)
            get_iso3166_updates(test_alpha_error_3)
#8.)
        with self.assertRaises(ValueError):
            get_iso3166_updates(test_alpha_error_4)
            get_iso3166_updates(test_alpha_error_5)
            get_iso3166_updates(test_alpha_error_6)

    @unittest.skip("Skipping as below tests requiring extracting all updates each time.")   
    def test_get_iso3166_updates_year(self):
        """ Testing main updates function that gets the updates and exports to json/csv, using a variety of year input 
            parameter values. Note, only using updates data from the wiki pages and not ISO due to time constraint of 
            pulling data via Selenium. """
        test_year1 = "2005,2017"
        test_year3 = ">2021"
        test_year4 = "<2003"
        test_year5 = "2005-2007"
        test_year6 = "1999-2002"
        test_year7 = "<>2004,2018"
        test_year8 = "abcdef"
        test_year9 = "2020-2024><"
        test_year10 = ">>2009"
        test_year11 = ["2009, 2012, 2014"]
        test_year12 = 12345
        test_year13 = True
#1.)    
        test_year_2005_2017_updates = get_iso3166_updates(year=test_year1, export_filename=self.test_export_filename,  #2005,2017
                export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)
        test_year_2005_2017_expected_keys = ['AF', 'CN', 'CY', 'DJ', 'ID', 'KP', 'NR', 'PA', 'PK', 'QA', 'RU', 'SI', 'TJ', 'UG', 'VN']

        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_2005,2017.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_2005,2017.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_year_2005_2017_updates), 15, 
            f"Expected 15 updates in output object, got {len(test_year_2005_2017_updates)}.")
        self.assertEqual(list(test_year_2005_2017_updates), test_year_2005_2017_expected_keys, 
            f"Expected and observed list of country codes do not match:\n{list(test_year_2005_2017_updates)}.")
        for update in test_year_2005_2017_updates:
            for row in range(0, len(test_year_2005_2017_updates[update])):
                self.assertTrue(
                    (datetime.strptime(test_year_2005_2017_updates[update][row]["Date Issued"], '%Y-%m-%d').year == 2005 or
                    datetime.strptime(test_year_2005_2017_updates[update][row]["Date Issued"], '%Y-%m-%d').year == 2017),
                    f"Expected year of updates output to be 2005 or 2017, got {test_year_2005_2017_updates[update][row]['Date Issued']}.")

        test_2005_2017_iso3166_csv = pd.read_csv(os.path.join(self.test_export_folder, self.test_export_filename + "_2005,2017.csv")).fillna("")
        self.assertTrue(set(["Country Code"] + self.expected_output_columns) == set(list(test_2005_2017_iso3166_csv.columns)),
            f"Column names/headers do not match expected:\n{set(list(test_2005_2017_iso3166_csv.columns))}.")
        self.assertEqual(len(test_2005_2017_iso3166_csv), 16, 
            f"Expected there to be 16 output objects in csv, got {len(test_2005_2017_iso3166_csv)}.")
#2.)
        test_year_gt_2021_updates = get_iso3166_updates(year=test_year3, export_filename=self.test_export_filename,  #>2021
                export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)
        test_year_gt_2021_expected_keys = ['CN', 'DZ', 'ET', 'FI', 'FR', 'GB', 'GT', 'HU', 'ID', 'IN', 'IQ', 'IR', 'IS', 'KH', 'KP',
                                           'KR', 'KZ', 'LT', 'LV', 'ME', 'NP', 'NZ', 'PA', 'PH', 'PL', 'RU', 'SI', 'SS', 'VE']

        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_>2021.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_>2021.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_year_gt_2021_updates), 29, 
            f"Expected 29 updates in output object, got {len(test_year_gt_2021_updates)}.")
        self.assertEqual(list(test_year_gt_2021_updates), test_year_gt_2021_expected_keys, 
            f"Expected and observed list of country codes do not match:\n{list(test_year_gt_2021_updates)}.")
        for update in test_year_gt_2021_updates:
            for row in range(0, len(test_year_gt_2021_updates[update])):
                self.assertTrue(datetime.strptime(test_year_gt_2021_updates[update][row]["Date Issued"], '%Y-%m-%d').year >= 2021, 
                    f"Expected year of updates output to be greater than or equal to 2021, got {test_year_gt_2021_updates[update][row]['Date Issued']}.")

        test_gt_2021_iso3166_csv = pd.read_csv(os.path.join(self.test_export_folder, self.test_export_filename + "_>2021.csv")).fillna("")
        self.assertTrue(set(["Country Code"] + self.expected_output_columns) == set(list(test_gt_2021_iso3166_csv.columns)),
            f"Column names/headers do not match expected:\n{set(list(test_gt_2021_iso3166_csv.columns))}.")
        self.assertEqual(len(test_gt_2021_iso3166_csv), 39, 
            f"Expected there to be 39 output objects in csv, got {len(test_gt_2021_iso3166_csv)}.")
#3.)
        test_year_lt_2003_updates = get_iso3166_updates(year=test_year4, export_filename=self.test_export_filename,  #<2003
                export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)
        test_year_lt_2003_expected_keys = ['AE', 'AL', 'AO', 'AZ', 'BD', 'BG', 'BI', 'BJ', 'BY', 'CA', 'CD', 'CN', 'CV', 'CZ', 
                                           'DO', 'EC', 'ER', 'ES', 'ET', 'FR', 'GB', 'GE', 'GN', 'GT', 'HR', 'ID', 'IN', 'IR', 
                                           'IT', 'KG', 'KH', 'KP', 'KR', 'KZ', 'LA', 'MA', 'MD', 'MO', 'MU', 'MW', 'NG', 'NI', 
                                           'PH', 'PL', 'PS', 'RO', 'RU', 'SI', 'TJ', 'TL', 'TM', 'TR', 'TW', 'UG', 'UZ', 'VA', 
                                           'VE', 'VN', 'YE']
        
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_<2003.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_<2003.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_year_lt_2003_updates), 59, 
            f"Expected 59 updates in output object, got {len(test_year_lt_2003_updates)}.")
        self.assertEqual(list(test_year_lt_2003_updates), test_year_lt_2003_expected_keys, 
            f"Expected and observed list of country codes do not match:\n{list(test_year_lt_2003_updates)}.")
        for update in test_year_lt_2003_updates:
            for row in range(0, len(test_year_lt_2003_updates[update])):
                self.assertTrue(datetime.strptime(test_year_lt_2003_updates[update][row]["Date Issued"], '%Y-%m-%d').year < 2003, 
                    f"Expected year of updates output to be less than 2003, got {test_year_lt_2003_updates[update][row]['Date Issued']}.")

        test_lt_2003_iso3166_csv = pd.read_csv(os.path.join(self.test_export_folder, self.test_export_filename + "_<2003.csv")).fillna("")
        self.assertTrue(set(["Country Code"] + self.expected_output_columns) == set(list(test_lt_2003_iso3166_csv.columns)),
            f"Column names/headers do not match expected:\n{set(list(test_lt_2003_iso3166_csv.columns))}.")
        self.assertEqual(len(test_lt_2003_iso3166_csv), 79, 
            f"Expected there to be 79 output objects in csv, got {len(test_lt_2003_iso3166_csv)}.")
#4.)
        test_year_2005_2007_updates = get_iso3166_updates(year=test_year5, export_filename=self.test_export_filename,  #2005-2007
                export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)
        test_year_2005_2007_expected_keys = ['AD', 'AF', 'AG', 'BA', 'BB', 'BG', 'BH', 'BL', 'CI', 'CZ', 'DJ', 'DM', 'DO', 'EG', 'FR', 'GB', 
                                            'GD', 'GE', 'GG', 'GN', 'HT', 'ID', 'IM', 'IR', 'IT', 'JE', 'KE', 'KN', 'KW', 'LB', 'LC', 'LI', 
                                            'LR', 'ME', 'MF', 'MK', 'MT', 'NR', 'PW', 'RS', 'RU', 'RW', 'SB', 'SC', 'SD', 'SG', 'SI', 'SM', 
                                            'TD', 'TO', 'TV', 'UG', 'VC', 'VN', 'YE', 'ZA']

        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_2005-2007.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_2005-2007.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_year_2005_2007_updates), 56, 
            f"Expected 56 updates in output object, got {len(test_year_2005_2007_updates)}.")
        self.assertEqual(list(test_year_2005_2007_updates), test_year_2005_2007_expected_keys, 
            f"Expected and observed list of country codes do not match:\n{list(test_year_2005_2007_updates)}.")
        for update in test_year_2005_2007_updates:
            for row in range(0, len(test_year_2005_2007_updates[update])):
                self.assertTrue((datetime.strptime(test_year_2005_2007_updates[update][row]["Date Issued"], '%Y-%m-%d').year >= 2005) and \
                                (datetime.strptime(test_year_2005_2007_updates[update][row]["Date Issued"], '%Y-%m-%d').year <= 2007), 
                            f"Expected year of updates output to be between 2005 and 2007, got {test_year_2005_2007_updates[update][row]['Date Issued']}.")

        test_year_2005_2007_iso3166_csv = pd.read_csv(os.path.join(self.test_export_folder, self.test_export_filename + "_2005-2007.csv")).fillna("")
        self.assertTrue(set(["Country Code"] + self.expected_output_columns) == set(list(test_year_2005_2007_iso3166_csv.columns)),
            f"Column names/headers do not match expected:\n{set(list(test_year_2005_2007_iso3166_csv.columns))}.")
        self.assertEqual(len(test_year_2005_2007_iso3166_csv), 62, 
            f"Expected there to be 62 output objects in csv, got {len(test_year_2005_2007_iso3166_csv)}.")
#5.)
        test_year_1999_2002_updates = get_iso3166_updates(year=test_year6, export_filename=self.test_export_filename,  #1999-2002
                export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)
        test_year_1999_2002_expected_keys = ['AE', 'AL', 'AO', 'AZ', 'BD', 'BG', 'BI', 'BJ', 'BY', 'CA', 'CD', 'CN', 'CV', 'CZ', 'DO', 'EC', 
                                             'ER', 'ES', 'ET', 'FR', 'GB', 'GE', 'GN', 'GT', 'HR', 'ID', 'IN', 'IR', 'IT', 'KG', 'KH', 'KP', 
                                             'KR', 'KZ', 'LA', 'MA', 'MD', 'MO', 'MU', 'MW', 'NG', 'NI', 'PH', 'PL', 'PS', 'RO', 'RU', 'SI', 
                                             'TJ', 'TL', 'TM', 'TR', 'TW', 'UG', 'UZ', 'VE', 'VN', 'YE']

        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_1999-2002.csv")), 
            "Expected output CSV file to exist in folder.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_1999-2002.json")),
            "Expected output JSON file to exist in folder.")
        self.assertEqual(len(test_year_1999_2002_updates), 58, 
            f"Expected 58 updates in output object, got {len(test_year_1999_2002_updates)}.")
        self.assertEqual(list(test_year_1999_2002_updates), test_year_1999_2002_expected_keys, 
            f"Expected and observed list of country codes do not match:\n{list(test_year_1999_2002_updates)}.")
        for update in test_year_1999_2002_updates:
            for row in range(0, len(test_year_1999_2002_updates[update])):
                self.assertTrue((datetime.strptime(test_year_1999_2002_updates[update][row]["Date Issued"], '%Y-%m-%d').year >= 1999) and \
                                (datetime.strptime(test_year_1999_2002_updates[update][row]["Date Issued"], '%Y-%m-%d').year <= 2002), 
                            f"Expected year of updates output to be between 1999 and 2002, got {test_year_1999_2002_updates[update][row]['Date Issued']}.")

        test_year_1999_2002_iso3166_csv = pd.read_csv(os.path.join(self.test_export_folder, self.test_export_filename + "_1999-2002.csv")).fillna("")
        self.assertTrue(set(["Country Code"] + self.expected_output_columns) == set(list(test_year_1999_2002_iso3166_csv.columns)),
            f"Column names/headers do not match expected:\n{set(list(test_year_1999_2002_iso3166_csv.columns))}.")
        self.assertEqual(len(test_year_1999_2002_iso3166_csv), 78, 
            f"Expected there to be 78 output objects in csv, got {len(test_year_1999_2002_iso3166_csv)}.")
#6.)
        test_year_not_equal_2004_2018_updates = get_iso3166_updates(year=test_year7, export_filename=self.test_export_filename,  #<>2004,2018
                export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False)
        test_year_not_equal_2004_2018_expected_keys = ['AD', 'AE', 'AF', 'AG', 'AL', 'AO', 'AR', 'AT', 'AU', 'AW', 'AZ', 'BA', 'BB', 'BD', 'BE', 'BF', 
                                                       'BG', 'BH', 'BI', 'BJ', 'BL', 'BN', 'BO', 'BQ', 'BS', 'BT', 'BW', 'BY', 'CA', 'CD', 'CF', 'CG', 
                                                       'CH', 'CI', 'CL', 'CN', 'CO', 'CU', 'CV', 'CW', 'CY', 'CZ', 'DJ', 'DM', 'DO', 'DZ', 'EC', 'EE', 
                                                       'EG', 'ER', 'ES', 'ET', 'FI', 'FM', 'FR', 'GB', 'GD', 'GE', 'GG', 'GH', 'GL', 'GM', 'GN', 'GQ', 
                                                       'GR', 'GT', 'GW', 'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IM', 'IN', 'IQ', 'IR', 'IS', 'IT', 'JE', 
                                                       'JO', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KP', 'KR', 'KW', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK', 
                                                       'LR', 'LS', 'LT', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MF', 'MH', 'MK', 'MM', 'MO', 'MT', 'MU', 
                                                       'MV', 'MW', 'MY', 'NA', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NZ', 'OM', 'PA', 'PE', 'PG', 'PH', 
                                                       'PK', 'PL', 'PS', 'PW', 'QA', 'RO', 'RS', 'RU', 'RW', 'SA', 'SB', 'SC', 'SD', 'SE', 'SG', 'SH', 
                                                       'SI', 'SL', 'SM', 'SN', 'SS', 'ST', 'SX', 'TD', 'TJ', 'TL', 'TM', 'TN', 'TO', 'TR', 'TT', 'TV', 
                                                       'TW', 'TZ', 'UG', 'UZ', 'VA', 'VC', 'VE', 'VN', 'YE', 'ZA', 'ZM']

        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_<>2004,2018.csv")), 
            f"Expected output CSV file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_<>2004,2018.csv')}")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_<>2004,2018.json")),
            f"Expected output JSON file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_<>2004,2018.json')}")
        self.assertEqual(len(test_year_not_equal_2004_2018_updates), 171, 
            f"Expected 171 updates in output object, got {len(test_year_not_equal_2004_2018_updates)}.")
        self.assertEqual(list(test_year_not_equal_2004_2018_updates), test_year_not_equal_2004_2018_expected_keys, 
            f"Expected and observed list of country codes do not match:\n{list(test_year_not_equal_2004_2018_updates)}.")
        for update in test_year_not_equal_2004_2018_updates:
            for row in range(0, len(test_year_not_equal_2004_2018_updates[update])):
                #convert year in Date Issued column to string of year, remove "corrected" date if applicable
                if ("corrected" in test_year_not_equal_2004_2018_updates[update][row]["Date Issued"]):
                    current_updates_year = str(datetime.strptime(re.sub("[(].*[)]", "", test_year_not_equal_2004_2018_updates[update][row]["Date Issued"]).replace(' ', "").
                                                    replace(".", '').replace('\n', ''), '%Y-%m-%d').year)
                else:
                    current_updates_year = str(datetime.strptime(test_year_not_equal_2004_2018_updates[update][row]["Date Issued"].replace('\n', ''), '%Y-%m-%d').year)
                self.assertTrue((current_updates_year != 2004 and current_updates_year != 2018), 
                            f"Expected year of updates output to not include 2004 and 2018 publication years, got {test_year_not_equal_2004_2018_updates[update][row]['Date Issued']}.")

        test_year_not_equal_2004_2018_iso3166_csv = pd.read_csv(os.path.join(self.test_export_folder, self.test_export_filename + "_<>2004,2018.csv")).fillna("")
        self.assertTrue(set(["Country Code"] + self.expected_output_columns) == set(list(test_year_not_equal_2004_2018_iso3166_csv.columns)),
            f"Column names/headers do not match expected:\n{set(list(test_year_not_equal_2004_2018_iso3166_csv.columns))}.")
        self.assertEqual(len(test_year_not_equal_2004_2018_iso3166_csv), 522, 
            f"Expected there to be 522 output objects in csv, got {len(test_year_not_equal_2004_2018_iso3166_csv)}.")
#7.)
        with self.assertRaises(ValueError):
            get_iso3166_updates(year=test_year8) #abcdef
            get_iso3166_updates(year=test_year9) #2020-2024><
            get_iso3166_updates(year=test_year10) #>>2009 
#8.)
        with self.assertRaises(TypeError):
            get_iso3166_updates(year=test_year11) #["2009, 2012, 2014"]
            get_iso3166_updates(year=test_year12) #12345
            get_iso3166_updates(year=test_year13) #True

    @unittest.skip("")
    def test_get_iso3166_updates_alpha_year(self):
        """ Testing main updates function that gets the updates and exports to json/csv, using
            a variety of ISO 3166-1 alpha codes and year input parameter values. """
        test_ch_2003 = ("CH", "2003") #Switzerland
        test_md_2008 = ("MD", "2008") #Moldova
        test_ne_om_2010 = ("NER,OMN", "2010") #Niger, Oman
        test_sd_tt_2015_2021 = ("SDN,780", "2015-2021") #Sudan, Trinidad and Tabago - using alpha-3 codes
        test_ie_2027 = ("IE", "2027") #Ireland
        test_error1 = ("ABC", "3003")
        test_error2 = ("ABCDEF", "ABC")
        test_error3 = ("FR", "199999")
        test_error4 = (123, "2007")
        test_error5 = ("MO", False)
        test_error6 = (["PL,PW,QA"], "2012")
#1.) 
        test_alpha_year_ch_2003_updates = get_iso3166_updates(alpha_codes=test_ch_2003[0], year=test_ch_2003[1],  #Switzerland
                export_filename=self.test_export_filename, export_folder=self.test_export_folder, concat_updates=True, export_json=True, \
                    export_csv=False, verbose=0, use_selenium=True)
        ch_2003_expected_updates = {'CH': [{'Change': 'Spelling correction of CH-AI and CH-AR. New list source.', 'Description of Change': '', 
            'Date Issued': '2003-09-05', 'Source': 'Newsletter I-5 - https://web.archive.org/web/20081218103244/http://www.iso.org/iso/iso_3166-2_newsletter_i-5_en.pdf.'}]}

        self.assertFalse(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_CH_2003.csv")), 
            f"Expected output CSV file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_CH_2003.csv')}.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_CH_2003.json")),
            f"Expected output JSON file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_CH_2003.json')}.")
        self.assertEqual(test_alpha_year_ch_2003_updates, ch_2003_expected_updates, 
            f"Expected and observed updates data outputs do not match:\n{test_alpha_year_ch_2003_updates}")
#2.)
        test_alpha_year_md_2008_updates = get_iso3166_updates(alpha_codes=test_md_2008[0], year=test_md_2008[1],  #Moldova
                export_filename=self.test_export_filename, export_folder=self.test_export_folder, concat_updates=True, export_json=True, \
                    export_csv=False, verbose=0, use_selenium=True)
        md_2008_expected_updates = {'MD': [{'Change': 'Correction of administrative language from Romanian (ro, ron) to Moldavian (mo, mol).', 
            'Description of Change': '', 'Date Issued': '2008-09-09', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:MD.'}, 
            {'Change': 'Change of short name.', 'Description of Change': '', 'Date Issued': '2008-04-08', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:MD.'}]}

        self.assertFalse(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_MD_2008.csv")), 
            f"Expected output CSV file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_MD_2008.csv')}.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_MD_2008.json")),
            f"Expected output JSON file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_MD_2008.json')}.")
        self.assertEqual(test_alpha_year_md_2008_updates, md_2008_expected_updates, 
            f"Expected and observed updates data outputs do not match:\n{test_alpha_year_md_2008_updates}")
#3.) 
        test_alpha_year_ne_om_2010_updates = get_iso3166_updates(alpha_codes=test_ne_om_2010[0], year=test_ne_om_2010[1],  #Niger, Oman
                export_filename=self.test_export_filename, export_folder=self.test_export_folder, concat_updates=True, export_json=True, \
                    export_csv=False, verbose=0, use_selenium=True)
        ne_om_2010_expected_updates = {'NE': [], 'OM': [{'Change': 'Subdivisions added: OM-BU Al Buraymī. Codes: OM-JA Al Janūbīyah -> OM-ZU Z̧ufār.', 
            'Description of Change': 'Update of the administrative structure and of the list source.', 'Date Issued': '2010-06-30', 
            'Source': 'Newsletter II-2 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf.'}]}

        self.assertFalse(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_NE,OM_2010.csv")), 
            f"Expected output CSV file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_NE,OM_2010.csv')}.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_NE,OM_2010.json")),
            f"Expected output JSON file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_NE,OM_2010.json')}.")
        self.assertEqual(test_alpha_year_ne_om_2010_updates, ne_om_2010_expected_updates, 
            f"Expected and observed updates data outputs do not match:\n{test_alpha_year_ne_om_2010_updates}")
#4.)
        test_alpha_year_sd_tt_2015_2021_updates = get_iso3166_updates(alpha_codes=test_sd_tt_2015_2021[0], year=test_sd_tt_2015_2021[1],  #Sudan, Trinidad and Tabago
                export_filename=self.test_export_filename, export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=False, verbose=0, use_selenium=True)
        sd_tt_2015_2021_expected_updates =  {'SD': [{'Change': 'Spelling changes: SD-DC Wasaţ Dārfūr Zālinjay -> Wasaţ Dārfūr. SD-KN Shiamāl Kurdufān -> Shamāl Kurdufān.', 
            'Description of Change': 'Typographical correction of subdivision name of SD-KN, SD-DC; Addition of local variation of SD-DC.', 'Date Issued': '2020-11-24', 
            'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:SD.'},         
            {'Change': 'Correction of the romanization system label.', 'Description of Change': '', 'Date Issued': '2018-11-26', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:SD.'}, 
            {'Change': 'Subdivision added: SD-GK Gharb Kurdufān (ar), West Kordofan (en). Spelling changes: SD-DC Zalingei -> Wasaţ Dārfūr Zālinjay. SD-DN ? -> Shamāl Dārfūr. SD-KN Shamāl Kurdufān -> Shiamāl Kurdufān. SD-NO ? -> Ash Shamālīyah. SD-NR An Nīl -> Nahr an Nīl.', 
            'Description of Change': 'Additions of state SD-GK; change spelling of SD-NR, SD-NO, SD-DN, SD-KN, SD-DC; update List Source.', 'Date Issued': '2015-11-27', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:SD.'}], 
            'TT': [{'Change': 'Change of category name from municipality to borough for TT-ARI, TT-CHA, TT-PTF; Change of subdivision category name from municipality to city for TT-POS, TT-SFO; Update List Source.', 
            'Description of Change': '', 'Date Issued': '2020-11-24', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:TT.'}, 
            {'Change': 'Deletion of regions TT-ETO, TT-RCM, TT-WTO; addition of region TT-MRC; addition of one ward TT-TOB; update List Source.', 'Description of Change': '', 'Date Issued': '2015-11-27', 
            'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:TT.'}]}
        
        self.assertFalse(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_SD,TT_2015-2021.csv")), 
            f"Expected output CSV file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_SD,TT_2015-2021.csv')}.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_SD,TT_2015-2021.json")),
            f"Expected output JSON file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_SD,TT_2015-2021.json')}.")
        self.assertEqual(test_alpha_year_sd_tt_2015_2021_updates, sd_tt_2015_2021_expected_updates, 
            f"Expected and observed updates data outputs do not match:\n{test_alpha_year_sd_tt_2015_2021_updates}")
#6.) 
        test_alpha_year_ie_2027_updates = get_iso3166_updates(alpha_codes=test_ie_2027[0], year=test_ie_2027[1],  #Ireland
                export_filename=self.test_export_filename, export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=False, verbose=0, use_selenium=True)
        ie_2027_expected_updates = {"IE": []}

        self.assertFalse(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_IE_2027.csv")), 
            f"Expected output CSV file to not exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_IE_2027.csv')}.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_IE_2027.json")),
            f"Expected output JSON file to not exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_IE_2027.json')}.")
        self.assertEqual(test_alpha_year_ie_2027_updates, ie_2027_expected_updates, 
            f"Expected and observed updates data outputs do not match:\n{test_alpha_year_ie_2027_updates}")
#7.)
        with self.assertRaises(ValueError):
            get_iso3166_updates(alpha_codes=test_error1[0], year=test_error1[1])
            get_iso3166_updates(alpha_codes=test_error2[0], year=test_error2[1])
            get_iso3166_updates(alpha_codes=test_error3[0], year=test_error3[1])
#8.)
        with self.assertRaises(TypeError):
            get_iso3166_updates(alpha_codes=test_error4[0], year=test_error4[1])
            get_iso3166_updates(alpha_codes=test_error5[0], year=test_error5[1])
            get_iso3166_updates(alpha_codes=test_error6[0], year=test_error6[1])

    @unittest.skip("Skipping to not overload test runner.")
    def test_alpha_codes_range(self):
        """ Testing parameter in get script that gets the updates for a range of alpha codes, alpbetically. """
        test_alpha_codes_range_ad_az = "AD-AZ" #Andorra-Azerbaijan
        test_alpha_codes_range_ci_cv = "CI-CV" #Ivory Coast-Cabo Verde
        test_alpha_codes_range_nr_mn = "NR-MN" #Mongolia-Norway 
        test_alpha_codes_range_zw = "Zw"  #Zimbabwe
        test_alpha_codes_range_error1 = "AA-DD" 
        test_alpha_codes_range_error2 = "zz"
        test_alpha_codes_range_error3 = "NAA-QA"
#1.)
        test_alpha_codes_range_ad_az_updates = get_iso3166_updates(alpha_codes_range=test_alpha_codes_range_ad_az, export_filename=self.test_export_filename,  #Andorra-Azerbaijan
            export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=False, verbose=0, use_selenium=False)
        test_alpha_codes_range_ad_az_updates_expected_ad = [{'Change': 'Update List Source.', 'Description of Change': '', 'Date Issued': '2015-11-27', 
            'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD.'}, {'Change': 'Update List Source.', 'Description of Change': '', 
            'Date Issued': '2014-11-03', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AD.'}, {'Change': 'Subdivisions added: 7 parishes.', 
            'Description of Change': 'Addition of the administrative subdivisions and of their code elements.', 'Date Issued': '2007-04-17', 
            'Source': 'Newsletter I-8 - https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf.'}]
        test_alpha_codes_range_ad_az_updates_expected_at = [{'Change': 'Change of subdivision category from federal Länder to state; update List Source.', 'Description of Change': '', 
            'Date Issued': '2015-11-27', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AT.'}, {'Change': 'Update List Source.', 
            'Description of Change': '', 'Date Issued': '2014-11-03', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AT.'}]

        self.assertEqual(list(test_alpha_codes_range_ad_az_updates), ['AD','AE','AF','AG','AI','AL','AM','AO','AQ','AR','AS','AT','AU','AW','AX','AZ'], 
            f"Expected and observed list of alpha codes do not match:\n{list(test_alpha_codes_range_ad_az)}")
        self.assertEqual(test_alpha_codes_range_ad_az_updates["AD"], test_alpha_codes_range_ad_az_updates_expected_ad, 
            f"Expected updates output for AD does not match observed:\n{test_alpha_codes_range_ad_az_updates['AD']}")
        self.assertEqual(test_alpha_codes_range_ad_az_updates["AT"], test_alpha_codes_range_ad_az_updates_expected_at, 
            f"Expected updates output for AT does not match observed:\n{test_alpha_codes_range_ad_az_updates['AT']}")
#2.)
        test_alpha_codes_range_ci_cv_updates = get_iso3166_updates(alpha_codes_range=test_alpha_codes_range_ci_cv, export_filename=self.test_export_filename,  #Ivory Coast-Cabo Verde
            export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=False, verbose=0, use_selenium=False)
        test_alpha_codes_range_ci_cv_updates_expected_cl = [{'Change': 'Subdivisions added: CL-NB Ñuble.', 'Description of Change': 'Addition of region CL-NB; Update List Source.', 'Date Issued': '2018-11-26', 
            'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CL.'}, {'Change': 'Spelling changes: CL-AI, CL-AR.', 'Description of Change': 
            'Change of spelling of CL-AR, CL-AI; addition of local variation of CL-AI, CL-LI; update list source.', 'Date Issued': '2016-11-15', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CL.'}, 
            {'Change': 'Spelling changes: CL-AI, CL-BI.', 'Description of Change': 'Change spelling of CL-AI and CL-BI; update List Source.', 'Date Issued': '2014-10-29', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CL.'}, 
            {'Change': 'Subdivisions added: CL-AP Arica y Parinacota. CL-LR Los Ríos.', 'Description of Change': 'Update of the administrative structure and of the list source.', 'Date Issued': '2010-06-30', 
            'Source': 'Newsletter II-2 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf.'}]
        test_alpha_codes_range_ci_cv_updates_expected_cu = [{'Change': 'Update List Source.', 'Description of Change': '', 'Date Issued': '2015-11-27', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CU.'}, 
            {'Change': 'Add 2 provinces CU-15 and CU-16; delete CU-02; change name of CU-03; update List Source.', 'Description of Change': '', 'Date Issued': '2014-10-29', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:CU.'}]
        
        self.assertEqual(list(test_alpha_codes_range_ci_cv_updates), ['CI','CK','CL','CM','CN','CO','CR','CU','CV'], 
            f"Expected and observed list of alpha codes do not match:\n{list(test_alpha_codes_range_ci_cv)}")
        self.assertEqual(test_alpha_codes_range_ci_cv_updates["CL"], test_alpha_codes_range_ci_cv_updates_expected_cl, 
            f"Expected updates output for CL does not match observed:\n{test_alpha_codes_range_ci_cv_updates['CL']}")
        self.assertEqual(test_alpha_codes_range_ci_cv_updates["CU"], test_alpha_codes_range_ci_cv_updates_expected_cu, 
            f"Expected updates output for CU does not match observed:\n{test_alpha_codes_range_ci_cv_updates['CU']}")
#3.)
        test_alpha_codes_range_nr_mn_updates = get_iso3166_updates(alpha_codes_range=test_alpha_codes_range_nr_mn, export_filename=self.test_export_filename,  #Mongolia-Norway
            export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=False, verbose=0, use_selenium=False)
        test_alpha_codes_range_nr_mn_updates_expected_mu = [{'Change': 'Deleted: MU-BR (Beau Bassin-Rose Hill), MU-CU (Curepipe), MU-PU (Port Louis), MU-QB (Quatre Bornes), MU-VP (Vacoas-Phoenix).', 
            'Description of Change': 'Deletion of city MU-BR, MU-CU, MU-PU, MU-QB, MU-VP; Update List Source; Correction of the Code Source.', 'Date Issued': '2020-11-24', 
            'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:MU.'}, {'Change': 'Codes: (to correct duplicate use). Port Louis (city): MU-PL -> MU-PU.', 
            'Description of Change': 'Error correction: Duplicate use of one code element corrected. Subdivision categories in header re-sorted.', 'Date Issued': '2002-12-10', 
            'Source': 'Newsletter I-4 - https://web.archive.org/web/20081218103210/http://www.iso.org/iso/iso_3166-2_newsletter_i-4_en.pdf.'}]
        test_alpha_codes_range_nr_mn_updates_expected_na =  [{'Change': 'Change of subdivision name of NA-KA; Change of local variation of NA-KA; Addition of local variation of NA-KA; Update List Source.', 
            'Description of Change': '', 'Date Issued': '2020-11-24', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:NA.'}, 
            {'Change': 'Addition of local variation of NA-KA; update list source.', 'Description of Change': '', 'Date Issued': '2016-11-15', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:NA.'}, 
            {'Change': 'Delete 1 region NA-OK; add two regions NA-KE and NA-KW; change subdivision name of NA-CA.', 'Description of Change': '', 'Date Issued': '2014-11-03', 'Source': 'Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:NA.'}]

        self.assertEqual(list(test_alpha_codes_range_nr_mn_updates), ['MN','MO','MP','MQ','MR','MS','MT','MU','MV','MW','MX','MY','MZ','NA','NC','NE','NF','NG','NI','NL','NO','NP','NR'], 
            f"Expected and observed list of alpha codes do not match:\n{list(test_alpha_codes_range_nr_mn)}")
        self.assertEqual(test_alpha_codes_range_nr_mn_updates["MU"], test_alpha_codes_range_nr_mn_updates_expected_mu, 
            f"Expected updates output for MU does not match observed:\n{test_alpha_codes_range_nr_mn_updates['MU']}")
        self.assertEqual(test_alpha_codes_range_nr_mn_updates["NA"], test_alpha_codes_range_nr_mn_updates_expected_na, 
            f"Expected updates output for NA does not match observed:\n{test_alpha_codes_range_nr_mn_updates['NA']}")
#4.)
        test_alpha_codes_range_zw_updates = get_iso3166_updates(alpha_codes_range=test_alpha_codes_range_zw, export_filename=self.test_export_filename,  #Zimbabwe
            export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=False, verbose=0, use_selenium=False)
        test_alpha_codes_range_za_updates_expected_zw = []

        self.assertEqual(list(test_alpha_codes_range_zw_updates), ['ZW'], 
            f"Expected and observed list of alpha codes do not match:\n{list(test_alpha_codes_range_nr_mn)}")
        self.assertEqual(test_alpha_codes_range_zw_updates["ZW"], test_alpha_codes_range_za_updates_expected_zw, 
            f"Expected updates output for ZW does not match observed:\n{test_alpha_codes_range_zw_updates['ZW']}")
#5.)
        with self.assertRaises(ValueError):
            get_iso3166_updates(alpha_codes_range=test_alpha_codes_range_error1) #AA-DD
            get_iso3166_updates(alpha_codes_range=test_alpha_codes_range_error2) #ZZ
            get_iso3166_updates(alpha_codes_range=test_alpha_codes_range_error3) #NAA-QA

    @unittest.skip("")
    def test_save_each_iteration(self):
        """ Testing parameter that saves each exports data per iteration rather than in the end in bulk. """
        test_alpha_codes_range_kn_kw = "KN,KP,KR,KW" #St Kitts-Kuwait
        test_alpha_codes_range_pa_pg = "PA-PG" #Panama-Papa New Guinea
#1.)
        test_alpha_codes_range_kn_kw_updates = get_iso3166_updates(alpha_codes=test_alpha_codes_range_kn_kw, export_filename=self.test_export_filename, 
            export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=True, verbose=0, use_selenium=False, save_each_iteration=True)
        
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_KN.json")), 
            f"Expected output JSON file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_KN.json')}.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_KP.json")), 
            f"Expected output JSON file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_KP.json')}.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_KR.json")), 
            f"Expected output JSON file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_KR.json')}.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_KW.json")), 
            f"Expected output JSON file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_KW.json')}.")
#2.)
        test_alpha_codes_range_pa_pg_updates = get_iso3166_updates(alpha_codes_range=test_alpha_codes_range_pa_pg, export_filename=self.test_export_filename, 
            export_folder=self.test_export_folder, concat_updates=True, export_json=True, export_csv=False, verbose=0, use_selenium=False, save_each_iteration=True)        

        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_PA.json")), 
            f"Expected output JSON file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_PA.json')}.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_PE.json")), 
            f"Expected output JSON file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_PE.json')}.")
        self.assertTrue(os.path.isfile(os.path.join(self.test_export_folder, self.test_export_filename + "_PG.json")), 
            f"Expected output JSON file to exist in folder: {os.path.join(self.test_export_folder, self.test_export_filename + '_PG.json')}.")
        
    def tearDown(self):
        """ Delete any exported test files/directories. """
        shutil.rmtree(self.test_export_folder)

if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)