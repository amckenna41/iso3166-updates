import iso3166_updates
import iso3166
import unittest
unittest.TestLoader.sortTestMethodsUsing = None


class ISO3166_Updates(unittest.TestCase):

    def setUp(self):
        """ """
        #initalise User-agent header for requests library 
        self.user_agent_header = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(__version__,
                                            'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}
        #base URL for ISO3166-2 wiki
        self.wiki_base_url = "https://en.wikipedia.org/wiki/ISO_3166-2:"

    def test_iso3166_updates_metadata(self):
        """ Testing correct iso3166-updates version and metadata. """
        self.assertEqual(iso3166_updates.__version__, "0.0.3, "iso3166-updates version is not correct, got: {}".format(iso3166_updates.__version__))
        self.assertEqual(iso3166_updates.__name__, "iso3166-updates", "iso3166-updates software name is not correct, got: {}".format(iso3166_updates.__name__))
        self.assertEqual(iso3166_updates.__author__, "AJ McKenna, https://github.com/amckenna41", "iso3166-updates author is not correct, got: {}".format(iso3166_updates.__author__))
        self.assertEqual(iso3166_updates.__authorEmail__, "amckenna41@qub.ac.uk", "iso3166-updates author email is not correct, got: {}".format(iso3166_updates.__authorEmail__))
        self.assertEqual(iso3166_updates.__url__, "https://github.com/amckenna41/iso3166-updates", "iso3166-updates repo URL is not correct, got: {}".format(iso3166_updates.__url__))
        self.assertEqual(iso3166_updates.__credits__, ['AJ McKenna'], "iso3166-updates credits is not correct, got: {}".format(iso3166_updates.__credits__))
        self.assertEqual(iso3166_updates.__license__, "MIT", "iso3166-updates license type is not correct, got: {}".format(iso3166_updates.__license__))
        self.assertEqual(iso3166_updates.__maintainer__, "AJ McKenna", "iso3166-updates maintainer is not correct, got: {}".format(iso3166_updates.__license__))

    # @unittest.skip("Skipping to not overload Wiki servers on test suite run.")
    def test_wiki_url(self):
        """ Test each ISO3166-2 wiki URL endpoint to check valid status code 200 is returned. """
        alpha2_codes = list(iso3166.countries_by_alpha2.keys())

        #iterate over each ISO3166 alpha2 code, testing response code using request library
        for code in alpha2_codes:
            request = requests.get(self.wiki_base_url, headers=self.user_agent_header)
            self.assertEqual(request.status_code, 200, "")   
    
    def test_table_to_array(self):
        """ Test func that parses html table into 2D array of headers & rows. """
        test_alpha2_1 = "BA"
        test_alpha2_2 = "EE"
        test_alpha2_3 = "QA"
        test_alpha2_4 = "RW"
        test_alpha2_5 = "TA"
        test_alpha2_6 = "ZA"

        #test alpha2 for countries that have no changes table

        #get html content from wiki of ISO page, convert html content into BS4 object,
        #get Changes Section/Heading from soup, get table element from section
#1.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_1).content, \
            "html.parser").find("span", {"id": "Changes"}).findNext('table')

        ba_table = table_to_array(changesSection)

#2.)
        changesSectionTable = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_2).content, \
            "html.parser").find("span", {"id": "Changes"}).findNext('table')
        
        ee_table = table_to_array(changesSection)

#3.)
        changesSectionTable = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_3).content, \
            "html.parser").find("span", {"id": "Changes"}).findNext('table')
        
        qa_table = table_to_array(changesSectionTable)
        qa_expected_output = ['Newsletter II-3',
                        '2011-12-13 (corrected 2011-12-15)',
                        'Update resulting from the addition of names in administrative languages, and update of the administrative structure and of the list source',
                        'Subdivisions added: QA-ZA Az̧ Za̧`āyin Subdivisions deleted: QA-GH Al Ghuwayrīyah QA-JU Al Jumaylīyah QA-JB Jarīyān al Bāţnah']

        self.assertIsInstance(qa_table, list, '')
        self.assertEqual(len(qa_table), 2, "")
        self.assertListEqual(qa_table[0], ['Newsletter','Date issued','Description of change in newsletter','Code/Subdivision change'], "")
        self.assertEqual(qa_table[1], qa_expected_output, "")
#4.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_4).content, \
            "html.parser").find("span", {"id": "Changes"})
        
        rw_table = table_to_array(changesSection)

    def test_get_updates_df(self):
        """ Test func that converts 2D parsed html table into dataframe. """
        test_alpha2_1 = "AZ"
        test_alpha2_2 = ""
        test_alpha2_3 = ""
        test_alpha2_4 = ""
        test_alpha2_5 = ""
        test_alpha2_6 = ""

#1.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_1).content, \
            "html.parser").find("span", {"id": "Changes"})
        
        az_table = table_to_array(changesSection)
        
        az_updates_df = get_updates_df(az_table)
#2.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_2).content, \
            "html.parser").find("span", {"id": "Changes"})
        
        az_table = table_to_array(changesSection)
        
        az_updates_df = get_updates_df(az_table)
#3.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_3).content, \
            "html.parser").find("span", {"id": "Changes"})
        
        az_table = table_to_array(changesSection)
        
        az_updates_df = get_updates_df(az_table)
#4.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_4).content, \
            "html.parser").find("span", {"id": "Changes"})
        
        az_table = table_to_array(changesSection)
        
        az_updates_df = get_updates_df(az_table)
#5.)
        soup = BeautifulSoup(requests.get(self.wiki_base_url + test_alpha2_5).content, \
            "html.parser").find("span", {"id": "Changes"})
        
        az_table = table_to_array(changesSection)
        
        az_updates_df = get_updates_df(az_table)

# def get_updates_df(iso3166_updates_table):
#     """

#     Parameters
#     ----------
#     :iso3166_updates_table : array
#         2D array of ISO3166-2 updates from Changes section in wiki

#     Returns
#     -------
#     :iso3166_df : pd.DataFrame
#         comverted pandas dataframe of all ISO3166-2 changes for particular country
#         from 2D input array.
#     """
#     #update column names to correct naming conventions
#     cols = correct_columns(iso3166_updates_table[0])

#     #convert 2D array into dataframe    
#     iso3166_df = pd.DataFrame(iso3166_updates_table[1:], columns=cols)

#     #get index and name of Date column in DataFrame, i.e the column that has 'date' in it
#     dateColIndex = [idx for idx, s in enumerate(list(map(lambda x: x.lower(), iso3166_df.columns))) if 'date' in s]
#     dateColName = list(iso3166_df.columns)[dateColIndex[0]]

#     def correct_date(row):
#         """ parse new date from row if changes have been "corrected". """
#         if "corrected" in row:
#             # wordEndIndex = row.index("corrected") + len("corrected")
#             return row[row.index("corrected") + len("corrected"):].strip().replace(')', '')
#         else:
#             return row 

#     def convert_date(row):
#         """ convert string date in rows of df into year from date object. """
#         return datetime.datetime.strptime(row.replace('\n', ''), '%Y-%m-%d').year

#     #parse date column to get corrected & most recent date, if applicable 
#     iso3166_df[dateColName] = iso3166_df[dateColName].apply(correct_date)

#     #only include rows of dataframe where date updated is same as year parameter, drop year col
#     if (year != ""): 
#         iso3166_df['Year'] = iso3166_df[dateColName].apply(convert_date)         #create temp new column to get year of updates from date column 
#         iso3166_df = iso3166_df.drop(iso3166_df[iso3166_df['Year'] != year].index)
#         iso3166_df = iso3166_df.drop('Year', axis=1)
#         export_fname = export_fname + "-" + str(year) #append year onto filename

#     #add below columns if not present so all DF's follow same format
#     if ("Edition/Newsletter" not in iso3166_df):
#         iso3166_df["Edition/Newsletter"] = ""

#     if ("Code/Subdivision change" not in iso3166_df):
#         iso3166_df["Code/Subdivision change"] = ""

#     #reindex/reorder columns in df
#     iso3166_df = iso3166_df.reindex(columns=['Edition/Newsletter', 'Date Issued', 'Description of change in newsletter', 'Code/Subdivision change'])

#     #replace all null/nan with empty string
#     iso3166_df.fillna("", inplace = True)

#     return iso3166_df

    def tearDown(self):
        """  """
        pass

if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)

