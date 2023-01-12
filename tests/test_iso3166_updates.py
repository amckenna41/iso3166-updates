import iso3166_updates
import iso3166
import getpass
import requests
import json
import shutil
import os
import pandas as pd
from bs4 import BeautifulSoup
from importlib import metadata
import unittest
unittest.TestLoader.sortTestMethodsUsing = None

class ISO3166_Updates(unittest.TestCase):

    def setUp(self):
        """ Initialise test variables, import json. """
        #initalise User-agent header for requests library 
        self.__version__ = metadata.metadata('iso3166_updates')['version']

        self.user_agent_header = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(self.__version__,
                                            'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}
        
        #base URL for ISO3166-2 wiki
        self.wiki_base_url = "https://en.wikipedia.org/wiki/ISO_3166-2:"
        
        #updates json
        with open("iso3166-updates.json") as input_json:
            self.iso3166_json = json.load(input_json)
        
        #temp filename & dir exports
        self.export_json_filename = "test_iso3166_updates"
        self.export_filename = "test_iso3166"
        self.export_folder = "temp_test_dir"
        
        #create temp dir to store any function outputs
        if not (os.path.isdir(self.export_folder)):
            os.mkdir(self.export_folder)

    def test_iso3166_updates_metadata(self): 
        """ Testing correct iso3166-updates software version and metadata. """
        self.assertEqual(metadata.metadata('iso3166_updates')['version'], "0.0.7", "iso3166-updates version is not correct, got: {}".format(metadata.metadata('iso3166_updates')['version']))
        self.assertEqual(metadata.metadata('iso3166_updates')['name'], "iso3166-updates", "iso3166-updates software name is not correct, got: {}".format(metadata.metadata('iso3166_updates')['name']))
        self.assertEqual(metadata.metadata('iso3166_updates')['author'], "AJ McKenna, https://github.com/amckenna41", "iso3166-updates author is not correct, got: {}".format(metadata.metadata('iso3166_updates')['author']))
        self.assertEqual(metadata.metadata('iso3166_updates')['author-email'], "amckenna41@qub.ac.uk", "iso3166-updates author email is not correct, got: {}".format(metadata.metadata('iso3166_updates')['author-email']))
        self.assertEqual(metadata.metadata('iso3166_updates')['summary'], "A Python package that pulls the latest updates & changes to all ISO3166 listed countries.", 
            "iso3166-updates package summary is not correct, got: {}".format(metadata.metadata('iso3166_updates')['summary']))
        self.assertEqual(metadata.metadata('iso3166_updates')['keywords'], "iso,iso3166,beautifulsoup,python,pypi,countries,country codes,csviso3166-2,iso3166-1,alpha2,alpha3", 
            "iso3166-updates keywords are not correct, got: {}".format(metadata.metadata('iso3166_updates')['keywords']))
        self.assertEqual(metadata.metadata('iso3166_updates')['home-page'], "https://github.com/amckenna41/iso3166-updates", "iso3166-updates home page url is not correct, got: {}".format(metadata.metadata('iso3166_updates')['home-page']))
        self.assertEqual(metadata.metadata('iso3166_updates')['maintainer'], "AJ McKenna", "iso3166-updates maintainer is not correct, got: {}".format(metadata.metadata('iso3166_updates')['maintainer']))
        self.assertEqual(metadata.metadata('iso3166_updates')['license'], "MIT", "iso3166-updates license type is not correct, got: {}".format(metadata.metadata('iso3166_updates')['license']))

    @unittest.skip("Skipping to not overload Wiki servers on test suite run.")
    def test_wiki_url(self):
        """ Test each ISO3166-2 wiki URL endpoint to check valid status code 200 is returned. """
        #get list of alpha2 codes from iso3166 library
        alpha2_codes = list(iso3166.countries_by_alpha2.keys())

        #iterate over each ISO3166 alpha2 code, testing response code using request library
        for code in alpha2_codes:
            request = requests.get(self.wiki_base_url, headers=self.user_agent_header)
            self.assertEqual(request.status_code, 200, 
                "Expected status code 200, got {}".format(request.status_code))   
    
    def test_table_to_array(self):
        """ Test func that parses html table into 2D array of headers & rows. """
        test_alpha2_ba = "BA" #Bosnia
        test_alpha2_eg = "EG" #Egypt
        test_alpha2_qa = "QA" #Qatar
        test_alpha2_rs = "RS" #Serbia
        test_alpha2_td = "TD" #Chad
        test_alpha2_br = "BR" #Brazil, no listed changes/updates
        test_alpha2_1 = "12345"
        test_alpha2_2 = "abcdefg"

        #get html content from wiki of ISO page, convert html content into BS4 object,
        #...get Changes Section/Heading from soup, get table element from section
#1.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_ba).content, "html.parser")
        table_html = soup.find("span", {"id": "Changes"}).findNext('table')
        
        ba_table = iso3166_updates.table_to_array(table_html)
        ba_expected_output1 = ['ISO 3166-2:2007 (http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=39718)', 
            '2007-12-13', 'Second edition of ISO 3166-2 (this change was not announced in a newsletter)[1] (#cite_note-2)', 
            'Subdivisions added: 10 cantons']
        ba_expected_output2 = ['Newsletter II-2 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf)', 
            '2010-06-30', 'Addition of the country code prefix as the first code element, addition of names in administrative languages, \
                update of the administrative structure and of the list source', 'Subdivisions added: BA-BRC Brčko distrikt']

        #removing any whitespace or newlines from expected and test outputs
        ba_expected_output1 = [entry.replace(" ", "") for entry in ba_expected_output1]
        ba_expected_output2 = [entry.replace(" ", "") for entry in ba_expected_output2]
        ba_test_output1 = [entry.replace(" ", "") for entry in ba_table[1]]
        ba_test_output2 = [entry.replace(" ", "") for entry in ba_table[2]]

        self.assertIsInstance(ba_table, list, "Expected output table to be of type list, got {}".format(type(ba_table)))
        self.assertEqual(len(ba_table), 3, "Expected there to be 3 elements in output table, got {}".format(len(ba_table)))
        self.assertListEqual(ba_table[0], ['Edition/Newsletter', 'Date issued', 'Description of change in newsletter', 'Code/Subdivision change'], 
            "Expected columns/headers in observed and expected output to match.")
        self.assertEqual(ba_test_output1, ba_expected_output1, "Expected observed and expected outputs to match.")
        self.assertEqual(ba_test_output2, ba_expected_output2, "Expected observed and expected outputs to match.")
#2.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_eg).content, "html.parser")
        table_html = soup.find("span", {"id": "Changes"}).findNext('table')

        eg_table = iso3166_updates.table_to_array(table_html)
        eg_expected_output1 = ['ISO 3166-2:2007 (http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=39718)', 
            '2007-12-13', 'Second edition of ISO 3166-2 (this change was not announced in a newsletter)[1] (#cite_note-3)', 
            'Subdivision added: EG-LX Al Uqşur']
        eg_expected_output2 = ['Newsletter II-2 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf)', 
            '2010-06-30', 'Update of the administrative structure and of the list source', 'Subdivisions added: EG-SU As Sādis min Uktūbar EG-HU Ḩulwān']

        #removing any whitespace or newlines from expected and test outputs
        eg_expected_output1 = [entry.replace(" ", "") for entry in eg_expected_output1]
        eg_expected_output2 = [entry.replace(" ", "") for entry in eg_expected_output2]
        eg_test_output1 = [entry.replace(" ", "") for entry in eg_table[1]]
        eg_test_output2 = [entry.replace(" ", "") for entry in eg_table[2]]

        self.assertIsInstance(eg_table, list, "Expected output table to be of type list, got {}".format(type(eg_table)))
        self.assertEqual(len(eg_table), 3, "Expected there to be 2 elements in output table, got {}".format(len(eg_table)))
        self.assertListEqual(eg_table[0], ['Edition/Newsletter', 'Date issued', 'Description of change', 'Code/Subdivision change'], 
            "Expected columns/headers in observed and expected output to match.")
        self.assertEqual(eg_test_output1, eg_expected_output1, "Expected observed and expected outputs to match.")
        self.assertEqual(eg_test_output2, eg_expected_output2, "Expected observed and expected outputs to match.")
#3.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_qa).content, "html.parser")
        table_html = soup.find("span", {"id": "Changes"}).findNext('table')

        qa_table = iso3166_updates.table_to_array(table_html)
        qa_expected_output = ['Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf)',
                        '2011-12-13 (corrected 2011-12-15)',
                        'Update resulting from the addition of names in administrative languages, and update of the administrative structure and of the list source',
                        'Subdivisions added: QA-ZA Az̧ Za̧`āyin Subdivisions deleted: QA-GH Al Ghuwayrīyah QA-JU Al Jumaylīyah QA-JB Jarīyān al Bāţnah']

        #removing any whitespace or newlines from expected and test outputs
        qa_expected_output = [entry.replace(" ", "") for entry in qa_expected_output]
        qa_test_output = [entry.replace(" ", "") for entry in qa_table[1]]

        self.assertIsInstance(qa_table, list, "Expected output table to be of type list, got {}".format(type(qa_table)))
        self.assertEqual(len(qa_table), 2, "Expected there to be 2 elements in output table, got {}".format(len(qa_table)))
        self.assertListEqual(qa_table[0], ['Newsletter', 'Date issued', 'Description of change in newsletter', 'Code/Subdivision change'], 
            "Expected columns/headers in observed and expected output to match.")
        self.assertEqual(qa_test_output, qa_expected_output, "Expected observed and expected outputs to match.")
#4.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_rs).content, "html.parser")
        table_html = soup.find("span", {"id": "Changes"}).findNext('table')

        rs_table = iso3166_updates.table_to_array(table_html)
        rs_expected_output1 = ['Newsletter I-8 (https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)', 
            '2007-04-17', 'Addition of a new country (in accordance with ISO 3166-1 Newsletter V-12)', 'Subdivisions added: 1 city, 2 autonomous republics, 29 districts']
        rs_expected_output2 = ['Newsletter II-1 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-1_corrected_2010-02-19.pdf)', 
            '2010-02-03 (corrected 2010-02-19)', 'Addition of the country code prefix as the first code element, administrative update', '']
        
        #removing any whitespace or newlines from expected and test outputs
        rs_expected_output1 = [entry.replace(" ", "") for entry in rs_expected_output1]
        rs_expected_output2 = [entry.replace(" ", "") for entry in rs_expected_output2]
        rs_test_output1 = [entry.replace(" ", "") for entry in rs_table[1]]
        rs_test_output2 = [entry.replace(" ", "") for entry in rs_table[2]]

        self.assertIsInstance(rs_table, list, "Expected output table to be of type list, got {}".format(type(rs_table)))
        self.assertEqual(len(rs_table), 3, "Expected there to be 2 elements in output table, got {}".format(len(rs_table)))
        self.assertListEqual(rs_table[0], ['Newsletter','Date issued','Description of change in newsletter','Code/Subdivision change'], 
            "Expected columns/headers in observed and expected output to match.")
        self.assertEqual(rs_test_output1, rs_expected_output1, "Expected observed and expected outputs to match.")
        self.assertEqual(rs_test_output2, rs_expected_output2, "Expected observed and expected outputs to match.")
#5.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_td).content, "html.parser")
        table_html = soup.find("span", {"id": "Changes"}).findNext('table')

        td_table = iso3166_updates.table_to_array(table_html)
        td_expected_output1 = ['Newsletter I-8 (https://web.archive.org/web/20120330105926/http://www.iso.org/iso/iso_3166-2_newsletter_i-8_en.pdf)', 
            '2007-04-17', 'Modification of the administrative structure', 'Subdivision layout: 14 prefectures (see below) → 18 regions']
        td_expected_output2 = ['Newsletter II-2 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf)', 
            '2010-06-30', 'Update of the administrative structure and languages and update of the list source', 
                'Subdivisions added: TD-BG Bahr el Gazel TD-BO Borkou TD-EN Ennedi TD-SI Sila TD-TI Tibesti Subdivisions deleted: TD-BET Borkou-Ennedi-Tibesti']

        #removing any whitespace or newlines from expected and test outputs
        td_expected_output1 = [entry.replace(" ", "") for entry in td_expected_output1]
        td_expected_output2 = [entry.replace(" ", "") for entry in td_expected_output2]
        td_test_output1 = [entry.replace(" ", "") for entry in td_table[1]]
        td_test_output2 = [entry.replace(" ", "") for entry in td_table[2]]

        self.assertIsInstance(td_table, list, "Expected output table to be of type list, got {}".format(type(td_table)))
        self.assertEqual(len(td_table), 5, "Expected there to be 2 elements in output table, got {}".format(len(td_table)))
        self.assertListEqual(td_table[0], ['Newsletter','Date issued','Description of change in newsletter','Code/Subdivision change'], 
            "Expected columns/headers in observed and expected output to match.")
        self.assertEqual(td_test_output1, td_expected_output1, "Expected observed and expected outputs to match.")
        self.assertEqual(td_test_output2, td_expected_output2, "Expected observed and expected outputs to match.")
#6.)    
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_br).content, "html.parser")
        table_html = soup.find("span", {"id": "Changes"})

        br_table = iso3166_updates.table_to_array(table_html)

        self.assertIsNone(table_html, "Table should be none as no listed changes/updates on wiki.")
        self.assertEqual(br_table, [], "Output from function should be empty array when input param is None.")
#7.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_1).content, "html.parser")
        table_html = soup.find("span", {"id": "Changes"})
        
        test_table = iso3166_updates.table_to_array(table_html)
        self.assertIsNone(table_html, "Table should be none as invalid alpha2 code input.")
        self.assertEqual(test_table, [], "Output from function should be empty array when input param is None.")
#8.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_2).content, "html.parser")
        table_html = soup.find("span", {"id": "Changes"})

        test_table = iso3166_updates.table_to_array(table_html)
        self.assertIsNone(table_html, "Table should be none as invalid alpha2 code input.")
    
    def test_updates_alpha2(self):
        """ Testing main updates function that gets the updates and exports to json/csv. """
        test_alpha2_au = "AU" #Australia
        test_alpha2_cv = "CV" #Cabo Verde
        test_alpha2_id = "ID" #Indonesia
        test_alpha2_pt = "PT" #Portugal ({})
        test_alpha2_bf_ca_gu_ie_je_str = "BF, CA, GU, IE, JE" #concat_updates=False
        test_alpha2_1 = "ABCDEF"
        test_alpha2_2 = 12345
        test_alpha2_3 = False

        #correct column/key names for dict returned from function
        expected_output_columns = ["Date Issued", "Edition/Newsletter", "Description of change in newsletter", "Code/Subdivision change"]
#1.)
        iso3166_updates.get_updates(test_alpha2_au, export_filename=self.export_filename,
            export_json_filename=self.export_json_filename + "-AU", export_folder=self.export_folder, 
                concat_updates=True, export_json=True, export_csv=True)
        
        #change export_json & export_csv
        test_au_expected = {
            "Date Issued": "2016-11-15",
            "Edition/Newsletter": "Online Browsing Platform (OBP)",
            "Description of change in newsletter": "Update List Source; update Code Source",
            "Code/Subdivision change": ""
            }

        with open(os.path.join(self.export_folder, self.export_json_filename + "-AU.json")) as output_json:
            test_au_iso3166_json = json.load(output_json)

        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-AU.csv")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-AU.json")), "")
        self.assertEqual(list(test_au_iso3166_json), ['AU'], "")
        self.assertEqual(len(list(test_au_iso3166_json["AU"])), 3, "Expected there to be 3 output objects in json, got {}.".format(len(list(test_au_iso3166_json))))
        for row in test_au_iso3166_json["AU"]:
            self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
            self.assertIsInstance(row, dict, "Ouput object of json should be of type dict, got {}".format(type(row)))
        self.assertEqual(test_au_iso3166_json['AU'][0], test_au_expected, "Expected observed and expected outputs to match.")

        test_au_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "-AU.csv")).fillna("")
        
        self.assertEqual(list(test_au_iso3166_csv.columns), expected_output_columns, "")
        self.assertEqual(len(test_au_iso3166_csv), 3, "Expected there to be 3 output objects in csv, got {}.".format(len(list(test_au_iso3166_csv))))
        self.assertEqual(test_au_iso3166_csv.head(1).to_dict(orient='records')[0], test_au_expected, "")
#2.)
        iso3166_updates.get_updates(test_alpha2_cv, export_filename=self.export_filename,
            export_json_filename=self.export_json_filename + "-CV", export_folder=self.export_folder, 
                concat_updates=True, export_json=True, export_csv=True)
        
        test_cv_expected = {
            "Date Issued": "2011-12-15",
            "Edition/Newsletter": "Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf)",
            "Description of change in newsletter": "Correction of NL II-2 for toponyms and typographical errors and source list update.",
            "Code/Subdivision change": "Codes: São Lourenço dos Órgãos CV-SL → CV-SO"
            }

        #open exported CV json
        with open(os.path.join(self.export_folder, self.export_json_filename + "-CV.json")) as output_json:
            test_cv_iso3166_json = json.load(output_json)
        
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-CV.csv")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-CV.json")), "")
        self.assertEqual(list(test_cv_iso3166_json), ['CV'], "")
        self.assertEqual(len(list(test_cv_iso3166_json["CV"])), 3, "Expected there to be 3 output objects in json, got {}.".format(len(list(test_cv_iso3166_json))))
        for row in test_cv_iso3166_json["CV"]:
            self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
            self.assertIsInstance(row, dict, "Ouput object of json should be of type dict, got {}".format(type(row)))
        self.assertEqual(test_cv_iso3166_json['CV'][0], test_cv_expected, "Expected observed and expected outputs to match.")

        test_cv_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "-CV.csv")).fillna("")
        
        self.assertEqual(list(test_cv_iso3166_csv.columns), expected_output_columns, "")
        self.assertEqual(len(test_cv_iso3166_csv), 3, "Expected there to be 3 output objects in csv, got {}.".format(len(list(test_cv_iso3166_csv))))
        self.assertEqual(test_cv_iso3166_csv.head(1).to_dict(orient='records')[0], test_cv_expected, "")
#3.)
        iso3166_updates.get_updates(test_alpha2_id, export_filename=self.export_filename,
            export_json_filename=self.export_json_filename + "-ID", export_folder=self.export_folder, 
                export_json=True, export_csv=True)
        
        test_id_expected = {
            "Date Issued": "2022-11-29",
            "Edition/Newsletter": "Online Browsing Platform (OBP)",
            "Description of change in newsletter": "Addition of provinces ID-PE, ID-PS and ID-PT; Update List Source",
            "Code/Subdivision change": ""
            }

        #open exported ID json
        with open(os.path.join(self.export_folder, self.export_json_filename + "-ID.json")) as output_json:
            test_id_iso3166_json = json.load(output_json)
        
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-ID.csv")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-ID.json")), "")
        self.assertEqual(list(test_id_iso3166_json), ['ID'], "")
        self.assertEqual(len(list(test_id_iso3166_json["ID"])), 13, "Expected there to be 13 output objects in json, got {}.".format(len(list(test_id_iso3166_json))))
        for row in test_id_iso3166_json["ID"]:
            self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
            self.assertIsInstance(row, dict, "Ouput object of json should be of type dict, got {}".format(type(row)))
        self.assertEqual(test_id_iso3166_json['ID'][0], test_id_expected, "Expected observed and expected outputs to match.")

        test_id_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "-ID.csv")).fillna("")
        
        self.assertEqual(list(test_id_iso3166_csv.columns), expected_output_columns, "")
        self.assertEqual(len(test_id_iso3166_csv), 13, "Expected there to be 13 output objects in csv, got {}.".format(len(list(test_id_iso3166_csv))))
        self.assertEqual(test_id_iso3166_csv.head(1).to_dict(orient='records')[0], test_id_expected, "")

#4.)
        iso3166_updates.get_updates(test_alpha2_pt, export_filename=self.export_filename,
            export_json_filename=self.export_json_filename + "-PT", export_folder=self.export_folder, 
                export_json=True, export_csv=True)
        
        test_pt_expected = {}

        #open exported PT json
        with open(os.path.join(self.export_folder, self.export_json_filename + "-PT.json")) as output_json:
            test_pt_iso3166_json = json.load(output_json)
        
        self.assertFalse(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-PT.csv")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-PT.json")), "")
        self.assertEqual(list(test_pt_iso3166_json), ['PT'], "")
        self.assertEqual(len(list(test_pt_iso3166_json["PT"])), 0, "Expected there to be 0 output objects in json, got {}.".format(len(list(test_pt_iso3166_json))))
        self.assertEqual(test_pt_iso3166_json['PT'], test_pt_expected, "Expected observed and expected outputs to match.")
#5.) 
        iso3166_updates.get_updates(test_alpha2_bf_ca_gu_ie_je_str, export_filename=self.export_filename,
            export_json_filename=self.export_json_filename, export_folder=self.export_folder, 
                concat_updates=False, export_json=True, export_csv=True)
        
        test_alpha2_bf_ca_gu_ie_je_str_expected = {}
        
        # self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-BF,CA,GU,IE,JE.csv")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-BF.json")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-CA.json")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-GU.json")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-IE.json")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-JE.json")), "")

        #open exported BF json
        with open(os.path.join(self.export_folder, self.export_json_filename + "-BF.json")) as output_json:
                test_bf_iso3166_json = json.load(output_json)
        self.assertEqual(len(list(test_bf_iso3166_json)), 3, "Expected there to be 3 output objects in json, got {}.".format(len(list(test_bf_iso3166_json))))

        #open exported CA json
        with open(os.path.join(self.export_folder, self.export_json_filename + "-CA.json")) as output_json:
                test_ca_iso3166_json = json.load(output_json)
        self.assertEqual(len(list(test_ca_iso3166_json)), 4, "Expected there to be 4 output objects in json, got {}.".format(len(list(test_ca_iso3166_json))))
        
        #open exported GU json
        with open(os.path.join(self.export_folder, self.export_json_filename + "-GU.json")) as output_json:
                test_gu_iso3166_json = json.load(output_json)
        self.assertEqual(len(list(test_gu_iso3166_json)), 0, "Expected there to be 0 output objects in json, got {}.".format(len(list(test_gu_iso3166_json))))

        #open exported IE json
        with open(os.path.join(self.export_folder, self.export_json_filename + "-IE.json")) as output_json:
                test_ie_iso3166_json = json.load(output_json)
        self.assertEqual(len(list(test_ie_iso3166_json)), 2, "Expected there to be 2 output objects in json, got {}.".format(len(list(test_ie_iso3166_json))))

        #open exported JE json
        with open(os.path.join(self.export_folder, self.export_json_filename + "-JE.json")) as output_json:
                test_je_iso3166_json = json.load(output_json)
        self.assertEqual(len(list(test_je_iso3166_json)), 1, "Expected there to be 1 output objects in json, got {}.".format(len(list(test_je_iso3166_json))))
#6.)    
        iso3166_updates.get_updates(test_alpha2_1, export_filename=self.export_filename,
            export_json_filename=self.export_json_filename, export_folder=self.export_folder, 
                concat_updates=True, export_json=True, export_csv=True)
#7.)
        with self.assertRaises(TypeError):
            iso3166_updates.get_updates(test_alpha2_2, export_filename=self.export_filename,
                export_json_filename=self.export_json_filename, export_folder=self.export_folder, 
                    concat_updates=True, export_json=True, export_csv=True)
#8.)
        with self.assertRaises(TypeError):
            iso3166_updates.get_updates(test_alpha2_3, export_filename=self.export_filename,
                export_json_filename=self.export_json_filename, export_folder=self.export_folder, 
                    concat_updates=True, export_json=True, export_csv=True)

    def test_updates(self):
        """ Testing main updates function that gets the updates and exports to json/csv. """
        test_alpha2_au = "AU" #Australia
        test_alpha2_cv = "CV" #Cabo Verde
        test_alpha2_id = "ID" #Indonesia
        test_alpha2_pt = "PT" #Portugal ({})
        test_alpha2_bf_ca_gu_ie_je_str = "BF, CA, GU, IE, JE" #concat_updates=False
        test_alpha2_1 = "ABCDEF"
        test_alpha2_2 = 12345
        test_alpha2_3 = False

        #correct column/key names for dict returned from function
        expected_output_columns = ["Date Issued", "Edition/Newsletter", "Description of change in newsletter", "Code/Subdivision change"]
#1.)
        iso3166_updates.get_updates(test_alpha2_au, export_filename=self.export_filename,
            export_json_filename=self.export_json_filename + "-AU", export_folder=self.export_folder, 
                concat_updates=True, export_json=True, export_csv=True)
        
        #change export_json & export_csv
        test_au_expected = {
            "Date Issued": "2016-11-15",
            "Edition/Newsletter": "Online Browsing Platform (OBP)",
            "Description of change in newsletter": "Update List Source; update Code Source",
            "Code/Subdivision change": ""
            }

        #open exported AU json
        with open(os.path.join(self.export_folder, self.export_json_filename + "-AU.json")) as output_json:
            test_au_iso3166_json = json.load(output_json)

        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-AU.csv")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-AU.json")), "")
        self.assertEqual(list(test_au_iso3166_json), ['AU'], "")
        self.assertEqual(len(list(test_au_iso3166_json["AU"])), 3, "Expected there to be 3 output objects in json, got {}.".format(len(list(test_au_iso3166_json))))
        for row in test_au_iso3166_json["AU"]:
            self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
            self.assertIsInstance(row, dict, "Ouput object of json should be of type dict, got {}".format(type(row)))
        self.assertEqual(test_au_iso3166_json['AU'][0], test_au_expected, "Expected observed and expected outputs to match.")

        test_au_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "-AU.csv")).fillna("")
        
        self.assertEqual(list(test_au_iso3166_csv.columns), expected_output_columns, "")
        self.assertEqual(len(test_au_iso3166_csv), 3, "Expected there to be 3 output objects in csv, got {}.".format(len(list(test_au_iso3166_csv))))
        self.assertEqual(test_au_iso3166_csv.head(1).to_dict(orient='records')[0], test_au_expected, "")
#2.)
        iso3166_updates.get_updates(test_alpha2_cv, export_filename=self.export_filename,
            export_json_filename=self.export_json_filename + "-CV", export_folder=self.export_folder, 
                concat_updates=True, export_json=True, export_csv=True)
        
        test_cv_expected = {
            "Date Issued": "2011-12-15",
            "Edition/Newsletter": "Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf)",
            "Description of change in newsletter": "Correction of NL II-2 for toponyms and typographical errors and source list update.",
            "Code/Subdivision change": "Codes: São Lourenço dos Órgãos CV-SL → CV-SO"
            }

        #open exported CV json
        with open(os.path.join(self.export_folder, self.export_json_filename + "-CV.json")) as output_json:
            test_cv_iso3166_json = json.load(output_json)
        
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-CV.csv")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-CV.json")), "")
        self.assertEqual(list(test_cv_iso3166_json), ['CV'], "")
        self.assertEqual(len(list(test_cv_iso3166_json["CV"])), 3, "Expected there to be 3 output objects in json, got {}.".format(len(list(test_cv_iso3166_json))))
        for row in test_cv_iso3166_json["CV"]:
            self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
            self.assertIsInstance(row, dict, "Ouput object of json should be of type dict, got {}".format(type(row)))
        self.assertEqual(test_cv_iso3166_json['CV'][0], test_cv_expected, "Expected observed and expected outputs to match.")

        test_cv_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "-CV.csv")).fillna("")
        
        self.assertEqual(list(test_cv_iso3166_csv.columns), expected_output_columns, "")
        self.assertEqual(len(test_cv_iso3166_csv), 3, "Expected there to be 3 output objects in csv, got {}.".format(len(list(test_cv_iso3166_csv))))
        self.assertEqual(test_cv_iso3166_csv.head(1).to_dict(orient='records')[0], test_cv_expected, "")
#3.)
        iso3166_updates.get_updates(test_alpha2_id, export_filename=self.export_filename,
            export_json_filename=self.export_json_filename + "-ID", export_folder=self.export_folder, 
                export_json=True, export_csv=True)
        
        test_id_expected = {
            "Date Issued": "2022-11-29",
            "Edition/Newsletter": "Online Browsing Platform (OBP)",
            "Description of change in newsletter": "Addition of provinces ID-PE, ID-PS and ID-PT; Update List Source",
            "Code/Subdivision change": ""
            }

        #open exported ID json
        with open(os.path.join(self.export_folder, self.export_json_filename + "-ID.json")) as output_json:
            test_id_iso3166_json = json.load(output_json)
        
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-ID.csv")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-ID.json")), "")
        self.assertEqual(list(test_id_iso3166_json), ['ID'], "")
        self.assertEqual(len(list(test_id_iso3166_json["ID"])), 13, "Expected there to be 13 output objects in json, got {}.".format(len(list(test_id_iso3166_json))))
        for row in test_id_iso3166_json["ID"]:
            self.assertEqual(list(row.keys()), expected_output_columns, "Columns from output do not match expected.")
            self.assertIsInstance(row, dict, "Ouput object of json should be of type dict, got {}".format(type(row)))
        self.assertEqual(test_id_iso3166_json['ID'][0], test_id_expected, "Expected observed and expected outputs to match.")

        test_id_iso3166_csv = pd.read_csv(os.path.join(self.export_folder, self.export_filename + "-ID.csv")).fillna("")
        
        self.assertEqual(list(test_id_iso3166_csv.columns), expected_output_columns, "")
        self.assertEqual(len(test_id_iso3166_csv), 13, "Expected there to be 13 output objects in csv, got {}.".format(len(list(test_id_iso3166_csv))))
        self.assertEqual(test_id_iso3166_csv.head(1).to_dict(orient='records')[0], test_id_expected, "")

#4.)
        iso3166_updates.get_updates(test_alpha2_pt, export_filename=self.export_filename,
            export_json_filename=self.export_json_filename + "-PT", export_folder=self.export_folder, 
                export_json=True, export_csv=True)
        
        test_pt_expected = {}

        #open exported PT json
        with open(os.path.join(self.export_folder, self.export_json_filename + "-PT.json")) as output_json:
            test_pt_iso3166_json = json.load(output_json)
        
        self.assertFalse(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-PT.csv")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-PT.json")), "")
        self.assertEqual(list(test_pt_iso3166_json), ['PT'], "")
        self.assertEqual(len(list(test_pt_iso3166_json["PT"])), 0, "Expected there to be 0 output objects in json, got {}.".format(len(list(test_pt_iso3166_json))))
        self.assertEqual(test_pt_iso3166_json['PT'], test_pt_expected, "Expected observed and expected outputs to match.")
#5.) 
        iso3166_updates.get_updates(test_alpha2_bf_ca_gu_ie_je_str, export_filename=self.export_filename,
            export_json_filename=self.export_json_filename, export_folder=self.export_folder, 
                concat_updates=False, export_json=True, export_csv=True)
        
        test_alpha2_bf_ca_gu_ie_je_str_expected = {}
        
        # self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_filename + "-BF,CA,GU,IE,JE.csv")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-BF.json")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-CA.json")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-GU.json")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-IE.json")), "")
        self.assertTrue(os.path.isfile(os.path.join(self.export_folder, self.export_json_filename + "-JE.json")), "")

        with open(os.path.join(self.export_folder, self.export_json_filename + "-BF.json")) as output_json:
                test_bf_iso3166_json = json.load(output_json)
        self.assertEqual(len(list(test_bf_iso3166_json)), 3, "Expected there to be 3 output objects in json, got {}.".format(len(list(test_bf_iso3166_json))))
        
        with open(os.path.join(self.export_folder, self.export_json_filename + "-CA.json")) as output_json:
                test_ca_iso3166_json = json.load(output_json)
        self.assertEqual(len(list(test_ca_iso3166_json)), 4, "Expected there to be 4 output objects in json, got {}.".format(len(list(test_ca_iso3166_json))))
        
        with open(os.path.join(self.export_folder, self.export_json_filename + "-GU.json")) as output_json:
                test_gu_iso3166_json = json.load(output_json)
        self.assertEqual(len(list(test_gu_iso3166_json)), 0, "Expected there to be 0 output objects in json, got {}.".format(len(list(test_gu_iso3166_json))))
        
        with open(os.path.join(self.export_folder, self.export_json_filename + "-IE.json")) as output_json:
                test_ie_iso3166_json = json.load(output_json)
        self.assertEqual(len(list(test_ie_iso3166_json)), 2, "Expected there to be 2 output objects in json, got {}.".format(len(list(test_ie_iso3166_json))))
        
        with open(os.path.join(self.export_folder, self.export_json_filename + "-JE.json")) as output_json:
                test_je_iso3166_json = json.load(output_json)
        self.assertEqual(len(list(test_je_iso3166_json)), 1, "Expected there to be 1 output objects in json, got {}.".format(len(list(test_je_iso3166_json))))
#6.)    
        iso3166_updates.get_updates(test_alpha2_1, export_filename=self.export_filename,
            export_json_filename=self.export_json_filename, export_folder=self.export_folder, 
                concat_updates=True, export_json=True, export_csv=True)
#7.)
        with self.assertRaises(TypeError):
            iso3166_updates.get_updates(test_alpha2_2, export_filename=self.export_filename,
                export_json_filename=self.export_json_filename, export_folder=self.export_folder, 
                    concat_updates=True, export_json=True, export_csv=True)
#8.)
        with self.assertRaises(TypeError):
            iso3166_updates.get_updates(test_alpha2_3, export_filename=self.export_filename,
                export_json_filename=self.export_json_filename, export_folder=self.export_folder, 
                    concat_updates=True, export_json=True, export_csv=True)
                    
    def test_get_updates_df(self):
        """ Test func that converts 2D parsed html table into dataframe. """
        test_alpha2_az = "AZ" #Azerbaijan
        test_alpha2_fi = "FI" #Finland
        test_alpha2_gh = "GH" #Ghana
        test_alpha2_ke = "KE" #Kenya
        test_alpha2_sn = "SN" #Senegal
        test_alpha2_1 = ""

        #correct column/key names for dict returned from function
        expected_output_columns = ["Date Issued", "Edition/Newsletter", "Description of change in newsletter", "Code/Subdivision change"]
#1.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_az).content, "html.parser")
        table_html = soup.find("span", {"id": "Changes"}).findNext('table')

        #get html table and updates dataframe  
        az_table = iso3166_updates.table_to_array(table_html)        
        az_updates_df = iso3166_updates.get_updates_df(az_table)

        az_expected_output1 = ['2002-05-21', 'Newsletter I-2 (https://web.archive.org/web/20081218103157/http://www.iso.org/iso/iso_3166-2_newsletter_i-2_en.pdf)', 
            'Correction of one code and four spelling errors. Notification of the rayons belonging to the autonomous republic', 'Codes: Naxçıvan: AZ-MM → AZ-NX']
        az_expected_output2 = ['2011-12-15', 'Newsletter II-3 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf)', 
            'Alphabetical re-ordering, name change of administrative places, first level prefix addition and source list update', 
                'Subdivisions added: AZ-KAN Kǝngǝrli AZ-NV Naxçıvan (municipality) Subdivisions deleted: AZ-SS Şuşa Codes: AZ-AB Əli \
                Bayramlı → AZ-SR Şirvan AZ-DAV Dəvəçi → AZ-SBN Şabran AZ-XAN Xanlar → AZ-GYG Göygöl']

        #removing any whitespace or newlines from expected and test outputs
        az_expected_output1 = [entry.replace(" ", "") for entry in az_expected_output1]
        az_expected_output2 = [entry.replace(" ", "") for entry in az_expected_output2]
        az_updates_df_output1 = [entry.replace(" ", "") for entry in az_updates_df.iloc[0].tolist()]
        az_updates_df_output2 = [entry.replace(" ", "") for entry in az_updates_df.iloc[1].tolist()]
        
        self.assertIsInstance(az_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(az_updates_df)))
        self.assertEqual(len(az_updates_df), 2, "Expected there to be 2 elements in output table, got {}".format(len(az_updates_df)))
        self.assertEqual(expected_output_columns, list(az_updates_df.columns), "Columns/Headers of dataframe do not match.")
        self.assertEqual(az_updates_df_output1, az_expected_output1, "Row value for column does not match expected output.")
        self.assertEqual(az_updates_df_output2, az_expected_output2, "Row value for column does not match expected output.")
#2.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_fi).content, "html.parser")
        table_html = soup.find("span", {"id": "Changes"}).findNext('table')

        #get html table and updates dataframe  
        fi_table = iso3166_updates.table_to_array(table_html)
        fi_updates_df = iso3166_updates.get_updates_df(fi_table)

        fi_expected_output1 = ['2011-12-15', 'Newsletter II-3[1]', 'Administrative re-organization, \
            deletion of useless information and the region names in English and French, source list \
                and source code update.', 'Subdivision layout: 6 provinces (see below) → 19 regions']
        fi_expected_output2 = ['2022-11-29', 'ISO Online Browsing Platform (OBP) \
            (https://www.iso.org/obp/ui/#iso:code:3166:FI)', 'Change of spelling of FI-17; Update List Source', 
                'Name change: Satakunda → Satakunta']

        #removing any whitespace or newlines from expected and test outputs
        fi_expected_output1 = [entry.replace(" ", "") for entry in fi_expected_output1]
        fi_expected_output2 = [entry.replace(" ", "") for entry in fi_expected_output2]
        fi_updates_df_output1 = [entry.replace(" ", "") for entry in fi_updates_df.iloc[0].tolist()]
        fi_updates_df_output2 = [entry.replace(" ", "") for entry in fi_updates_df.iloc[1].tolist()]

        self.assertIsInstance(fi_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(fi_updates_df)))
        self.assertEqual(len(fi_updates_df), 2, "Expected there to be 2 elements in output table, got {}".format(len(fi_updates_df)))
        self.assertEqual(expected_output_columns, list(fi_updates_df.columns), "Columns/Headers of dataframe do not match.")
        self.assertEqual(fi_updates_df_output1, fi_expected_output1, "Row value for column does not match expected output.")
        self.assertEqual(fi_updates_df_output2, fi_expected_output2, "Row value for column does not match expected output.")
#3.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_gh).content, "html.parser")
        table_html = soup.find("span", {"id": "Changes"}).findNext('table')

        #get html table and updates dataframe  
        gh_table = iso3166_updates.table_to_array(table_html)        
        gh_updates_df = iso3166_updates.get_updates_df(gh_table)

        gh_expected_output1 = ['2019-11-22', '', 'Deletion of region GH-BA; Addition of regions \
            GH-AF, GH-BE, GH-BO, GH-NE, GH-OT, GH-SV, GH-WN; Update List Source', '']
        gh_expected_output2 = ['2015-11-27', '', 'Update List Source', '']
        gh_expected_output3 = ['2014-11-03', '', 'Update List Source', '']

        #removing any whitespace or newlines from expected and test outputs
        gh_expected_output1 = [entry.replace(" ", "") for entry in gh_expected_output1]
        gh_expected_output2 = [entry.replace(" ", "") for entry in gh_expected_output2]
        gh_expected_output3 = [entry.replace(" ", "") for entry in gh_expected_output3]
        gh_updates_df_output1 = [entry.replace(" ", "") for entry in gh_updates_df.iloc[0].tolist()]
        gh_updates_df_output2 = [entry.replace(" ", "") for entry in gh_updates_df.iloc[1].tolist()]
        gh_updates_df_output3 = [entry.replace(" ", "") for entry in gh_updates_df.iloc[2].tolist()]

        self.assertIsInstance(gh_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(gh_updates_df)))
        self.assertEqual(len(gh_updates_df), 3, "Expected there to be 3 elements in output table, got {}".format(len(gh_updates_df)))
        self.assertEqual(expected_output_columns, list(gh_updates_df.columns), "Columns/Headers of dataframe do not match.")
        self.assertEqual(gh_updates_df_output1, gh_expected_output1, "Row value for column does not match expected output.")
        self.assertEqual(gh_updates_df_output2, gh_expected_output2, "Row value for column does not match expected output.")
        self.assertEqual(gh_updates_df_output3, gh_expected_output3, "Row value for column does not match expected output.")
#4.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_ke).content, "html.parser")
        table_html = soup.find("span", {"id": "Changes"}).findNext('table')

        #get html table and updates dataframe  
        ke_table = iso3166_updates.table_to_array(table_html)
        ke_updates_df = iso3166_updates.get_updates_df(ke_table)

        ke_expected_output1 = ['2007-12-13', 'ISO 3166-2:2007 (http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=39718)', \
            'Second edition of ISO 3166-2 (this change was not announced in a newsletter)[1] (#cite_note-1)', 'Codes: Western: KE-900 → KE-800']
        ke_expected_output2 = ['2010-06-30', 'Newsletter II-2 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf)', \
            'Update of the list source', '']
        ke_expected_output3 = ['2014-10-30', 'Online BrowsingPlatform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:KE)', 'Delete provinces; add 47 counties; \
            update List Source', 'Deleted codes:KE-110, KE-200, KE-300, KE-400, KE-500, KE-600, KE-700, KE-800Added codes:KE-01 through KE-47']
       
        #removing any whitespace or newlines from expected and test outputs
        ke_expected_output1 = [entry.replace(" ", "") for entry in ke_expected_output1]
        ke_expected_output2 = [entry.replace(" ", "") for entry in ke_expected_output2]
        ke_expected_output3 = [entry.replace(" ", "") for entry in ke_expected_output3]
        ke_updates_df_output1 = [entry.replace(" ", "") for entry in ke_updates_df.iloc[0].tolist()]
        ke_updates_df_output2 = [entry.replace(" ", "") for entry in ke_updates_df.iloc[1].tolist()]
        ke_updates_df_output3 = [entry.replace(" ", "") for entry in ke_updates_df.iloc[2].tolist()]
        
        self.assertIsInstance(ke_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(ke_updates_df)))
        self.assertEqual(len(ke_updates_df), 4, "Expected there to be 4 elements in output table, got {}".format(len(ke_updates_df)))
        self.assertEqual(expected_output_columns, list(ke_updates_df.columns), "Columns/Headers of dataframe do not match.")
        self.assertEqual(ke_updates_df_output1, ke_expected_output1, "Row value for column does not match expected output.")
        self.assertEqual(ke_updates_df_output2, ke_expected_output2, "Row value for column does not match expected output.")
        self.assertEqual(ke_updates_df_output3, ke_expected_output3, "Row value for column does not match expected output.")
#5.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_sn).content, "html.parser")
        table_html = soup.find("span", {"id": "Changes"}).findNext('table')

        #get html table and updates dataframe  
        sn_table = iso3166_updates.table_to_array(table_html)
        sn_updates_df = iso3166_updates.get_updates_df(sn_table)

        sn_expected_output1 = ['2003-09-05', 'Newsletter I-5 (https://web.archive.org/web/20081218103244/http://www.iso.org/iso/iso_3166-2_newsletter_i-5_en.pdf)', \
            'Addition of one new region. List source updated', 'Subdivisions added: SN-MT Matam']
        sn_expected_output2 = ['2010-06-30', 'Newsletter II-2 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf)', \
            'Update of the administrative structure and languages and update of the list source', 'Subdivisions added: SN-KA Kaffrine SN-KE Kédougou SN-SE Sédhiou']
        
        #removing any whitespace or newlines from expected and test outputs
        sn_expected_output1 = [entry.replace(" ", "") for entry in sn_expected_output1]
        sn_expected_output2 = [entry.replace(" ", "") for entry in sn_expected_output2]
        sn_updates_df_output1 = [entry.replace(" ", "") for entry in sn_updates_df.iloc[0].tolist()]
        sn_updates_df_output2 = [entry.replace(" ", "") for entry in sn_updates_df.iloc[1].tolist()]

        self.assertIsInstance(sn_updates_df, pd.DataFrame, "Ouput of function should be a dataframe, got {}.".format(type(sn_updates_df)))
        self.assertEqual(len(sn_updates_df), 2, "Expected there to be 2 elements in output table, got {}".format(len(sn_updates_df)))
        self.assertEqual(expected_output_columns, list(sn_updates_df.columns), "Columns/Headers of dataframe do not match.")
        self.assertEqual(sn_updates_df_output1, sn_expected_output1, "Row value for column does not match expected output.")
        self.assertEqual(sn_updates_df_output2, sn_expected_output2, "Row value for column does not match expected output.")



    def test_iso3166_alpha2_json(self):
        """ Testing all ISO3166-2 updates created in JSON generated from software package. """
        alpha2_codes = list(iso3166.countries_by_alpha2.keys())

        #iterate over each ISO3166 alpha2 code, testing alpha2 code is in updates json
        for code in alpha2_codes:
            self.assertIn(code, list(self.iso3166_json.keys()), "")

        test_alpha2_bg = "BG" #Bulgaria
        test_alpha2_cn = "CN" #China
        test_alpha2_cy = "CY" #Cyprus
        test_alpha2_ec = "EC" #Ecuador
        test_alpha2_pm = "PM" #Saint Pierre and Miquelon
        test_alpha2_pn = "PN" #Pitcairn Islands
        test_alpha2_abc = "abc"

        #output keys/columns for each entry in json
        expected_output_columns = ["Date Issued", "Edition/Newsletter", "Description of change in newsletter", "Code/Subdivision change"]
#1.)       
        bg_expected_output1 = {'Date Issued': '2018-11-26', 'Edition/Newsletter': 'Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:BG)', 
            'Description of change in newsletter': 'Correction of the romanization system label', 'Code/Subdivision change': ''}
        bg_expected_output2 = {'Date Issued': '2018-04-20', 'Edition/Newsletter': 'Online Browsing Platform (OBP) (https://www.iso.org/obp/ui/#iso:code:3166:BG)', 
            'Description of change in newsletter': 'Change of subdivision category from region to district in eng and fra; update List Source', 'Code/Subdivision change': ''}

        self.assertIsInstance(self.iso3166_json[test_alpha2_bg], list, "Expected output to be of type list, got {}".format(type(self.iso3166_json[test_alpha2_bg])))
        self.assertEqual(len(self.iso3166_json[test_alpha2_bg]), 7, "Expected there to be 7 elements in output row, got {}".format(len(self.iso3166_json[test_alpha2_bg])))
        for row in range(0, len(self.iso3166_json[test_alpha2_bg])):
            self.assertEqual(list(self.iso3166_json[test_alpha2_bg][row].keys()), expected_output_columns, "Columns from output do not match expected.")
        self.assertEqual(self.iso3166_json[test_alpha2_bg][0], bg_expected_output1, "Row in updates json does not match expected output.")
        self.assertEqual(self.iso3166_json[test_alpha2_bg][1], bg_expected_output2, "Row in updates json does not match expected output.")
#2.)
        cn_expected_output1 = {'Date Issued': '2021-11-25', 'Edition/Newsletter': 'Online Browsing Platform (OBP)', 
            'Description of change in newsletter': 'Change of spelling of CN-NX; Update List Source', 'Code/Subdivision change': ''}
        cn_expected_output2 = {'Date Issued': '2019-11-22', 'Edition/Newsletter': 'Online Browsing Platform (OBP)', 'Description of change in newsletter': 
            'Change language from mon to zho for CN-NM', 'Code/Subdivision change': ''}

        self.assertIsInstance(self.iso3166_json[test_alpha2_cn], list, "Expected output to be of type list, got {}".format(type(self.iso3166_json[test_alpha2_cn])))
        self.assertEqual(len(self.iso3166_json[test_alpha2_cn]), 6, "Expected there to be 6 elements in output row, got {}".format(len(self.iso3166_json[test_alpha2_cn])))
        for row in range(0, len(self.iso3166_json[test_alpha2_cn])):
            self.assertEqual(list(self.iso3166_json[test_alpha2_cn][row].keys()), expected_output_columns, "Columns from output do not match expected.")        
        self.assertEqual(self.iso3166_json[test_alpha2_cn][0], cn_expected_output1, "Row in updates json does not match expected output.")
        self.assertEqual(self.iso3166_json[test_alpha2_cn][1], cn_expected_output2, "Row in updates json does not match expected output.")
#3.)
        cy_expected_output1 = {'Date Issued': '2018-11-26', 'Edition/Newsletter': 'Online Browsing Platform (OBP)', 
            'Description of change in newsletter': 'Correction of the romanization system label', 'Code/Subdivision change': ''}
        cy_expected_output2 = {'Date Issued': '2018-04-20', 'Edition/Newsletter': 'Online Browsing Platform (OBP)', 
            'Description of change in newsletter': 'Update Code Source; update List Source', 'Code/Subdivision change': ''}

        self.assertIsInstance(self.iso3166_json[test_alpha2_cy], list, "Expected output to be of type list, got {}".format(type(self.iso3166_json[test_alpha2_cy])))
        self.assertEqual(len(self.iso3166_json[test_alpha2_cy]), 5, "Expected there to be 5 elements in output row, got {}".format(len(self.iso3166_json[test_alpha2_cy])))
        for row in range(0, len(self.iso3166_json[test_alpha2_cy])):
            self.assertEqual(list(self.iso3166_json[test_alpha2_cy][row].keys()), expected_output_columns, "Columns from output do not match expected.")
        self.assertEqual(self.iso3166_json[test_alpha2_cy][0], cy_expected_output1, "Row in updates json does not match expected output.")
        self.assertEqual(self.iso3166_json[test_alpha2_cy][1], cy_expected_output2, "Row in updates json does not match expected output.")
#4.)
        ec_expected_output1 = {'Date Issued': '2010-06-30', 'Edition/Newsletter': 
            'Newsletter II-2 (https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-2_2010-06-30.pdf)', 
                'Description of change in newsletter': 'Update of the administrative structure and of the list source', 'Code/Subdivision change': 
                    'Subdivisions added: EC-SE Santa Elena EC-SD Santo Domingo de los Tsáchilas'}
        ec_expected_output2 = {'Date Issued': '2002-12-10', 'Edition/Newsletter': 
            'Newsletter I-4 (https://web.archive.org/web/20081218103210/http://www.iso.org/iso/iso_3166-2_newsletter_i-4_en.pdf)', 
                'Description of change in newsletter': 'Addition of one province', 'Code/Subdivision change': 'Subdivisions added: EC-D Orellana'}

        self.assertIsInstance(self.iso3166_json[test_alpha2_ec], list, "Expected output to be of type list, got {}".format(type(self.iso3166_json[test_alpha2_ec])))
        self.assertEqual(len(self.iso3166_json[test_alpha2_ec]), 2, "Expected there to be 2 elements in output row, got {}".format(len(self.iso3166_json[test_alpha2_ec])))
        for row in range(0, len(self.iso3166_json[test_alpha2_ec])):
            self.assertEqual(list(self.iso3166_json[test_alpha2_ec][row].keys()), expected_output_columns, "Columns from output do not match expected.")
        self.assertEqual(self.iso3166_json[test_alpha2_ec][0], ec_expected_output1, "Row in updates json does not match expected output.")
        self.assertEqual(self.iso3166_json[test_alpha2_ec][1], ec_expected_output2, "Row in updates json does not match expected output.")
#5.)
        self.assertEqual(self.iso3166_json[test_alpha2_pm], {}, "Expected output to be of type dict, got {}".format(type(self.iso3166_json[test_alpha2_pm])))
#6.)
        self.assertEqual(self.iso3166_json[test_alpha2_pn], {}, "Expected output to be of type list, got {}".format(type(self.iso3166_json[test_alpha2_pn])))
#7.)
        with self.assertRaises(KeyError):
            self.iso3166_json[test_alpha2_abc]
            self.iso3166_json[12345]
            self.iso3166_json[False]
#8.)   
        for alpha2 in list(self.iso3166_json.keys()): #Testing no entries have an empty Edition/Newsletter field
            for row in range(0, len(self.iso3166_json[alpha2])):
                self.assertNotEqual(self.iso3166_json[alpha2][row]["Edition/Newsletter"], "", 
                    "For all entries in json the Edition/Newsletter column should not be empty, {}".format(self.iso3166_json[alpha2][row]))

    def tearDown(self):
        """ Delete imported json from memory. """
        del self.iso3166_json
        shutil.rmtree(self.export_folder)
    
if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)