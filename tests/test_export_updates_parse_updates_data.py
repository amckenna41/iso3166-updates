try:
    from iso3166_updates_export.parse_updates_data import *
except:
    from ..iso3166_updates_export.parse_updates_data import *
import unittest
unittest.TestLoader.sortTestMethodsUsing = None

@unittest.skip("")
class ISO3166_Export_Updates_Parse_Updates_Data_Tests(unittest.TestCase):
    """
    Test suite for testing the parse_updates_data module in the ISO 3166
    updates export directory. The module parses the exported tables/objects 
    into the correct format, as well as the optional remarks table data from 
    the ISO page.

    Test Cases
    ==========
    test_parse_remarks_table: 
        testing functionality that parses the remarks table data from ISO page.
    test_parse_updates_table:
        testing functionality that parses the updates table from wiki page. 
    """
    def setUp(self):
        """ Initialise test variables, import json. """
        #turn off tqdm progress bar functionality when running tests
        os.environ["TQDM_DISABLE"] = "1"

    def test_parse_updates_table(self):
        """ Testing functionality that parses the updates table data into valid format. """
#1.)
        test_input_data = [
            ["Change", "Description of Change", "Date Issued", "Source"],
            ["New entry", "Added new subdivision", "2023-01-01", "Official"],
            ["â†’ Change", "Name updated", "2024-02-15", "ISO OBP"],
            ["Correction", "Boundary adjustment", "2022-08-10 (corrected 2023-05-20)", "Gov Report"],
            ["Deletion", "Removed obsolete entry", "2021-12-31", "Official Doc"],
            ["Merge", "Merged two regions", "2020-05-20", "ISO Official"],
            ["Split", "Split one region into two", "2019-07-15", "ISO Update"],
            ["Renaming", "Country renamed", "2018-11-30", "Gov Announcement"],
        ]
        test_expected_output = pd.DataFrame(
            {
                "Change": ["Change", "Correction", "New entry", "Deletion", "Merge", "Split", "Renaming"],
                "Description of Change": ["", "", "Added new subdivision", "Removed obsolete entry", "Merged two regions", "Split one region into two", "Country renamed"],
                "Date Issued": ["2024-02-15", "2022-08-10 2023-05-20", "2023-01-01", "2021-12-31", "2020-05-20", "2019-07-15", "2018-11-30"],
                "Source": [
                    "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:US.",
                    "Gov Report", "Official", "Official Doc", "ISO Official", "ISO Update", "Gov Announcement"
                ]
            }
        )
        #test resultant and expected dataframes are equal
        result = parse_updates_table("US", test_input_data)
        pd.testing.assert_frame_equal(result, test_expected_output)
#2.)
        with self.assertRaises(TypeError):
            parse_updates_table("US", {})
            parse_updates_table("AD", "")
            parse_updates_table("DE", 1.04)

    def test_parse_remarks_table(self):
        """ Testing functionality that parses the remarks table data from ISO page. """
        class MockTag:
            def __init__(self, label_text, value_text):
                self.label_text = label_text
                self.value_text = value_text

            def find(self, class_name):
                class Dummy:
                    def __init__(self, text):
                        self.text = text
                if class_name == "core-view-field-name":
                    return Dummy(self.label_text)
                elif class_name == "core-view-field-value":
                    return Dummy(self.value_text)
                return None

        # Create mocked remark parts
        mock_summary_table = [
            MockTag("Remark Part 1", "This is remark one."),
            MockTag("Remark Part 2", "And here is the second."),
            MockTag("Remark Part 3", "Third part goes here."),
            MockTag("Remark Part 4", "Final remark part."),
        ]

        df_input = pd.DataFrame([
            ["Update", "Initial change", "2023-05-01", "Source"]
        ], columns=["Change", "Description of Change", "Date Issued", "Source"])

        updated_df, remarks = parse_remarks_table(df_input, mock_summary_table)
 #1.)
        self.assertEqual(remarks["part1"], "This is remark one", f"Expected remark part 1 to be in output remarks table:\n{remarks['part1']}.")
        self.assertEqual(remarks["part2"], "And here is the second", f"Expected remark part 2 to be in output remarks table:\n{remarks['part2']}.")
        self.assertEqual(remarks["part3"], "Third part goes here", f"Expected remark part 3 to be in output remarks table:\n{remarks['part3']}.")
        self.assertEqual(remarks["part4"], "Final remark part", f"Expected remark part 4 to be in output remarks table:\n{remarks['part4']}.")
#2.)
        self.assertEqual(["Change", "Description of Change", "Date Issued", "Source"], updated_df.columns, f"Expected and observed list of output columns do not match:\n{updated_df.columns}.")
#3.)
        test_df = pd.DataFrame([
            ["Change", "Some update", "2024-01-01", "ISO"]
        ], columns=["Change", "Description of Change", "Date Issued", "Source"])

        #test resultant and expected dataframes are equal
        result_df, remarks = parse_remarks_table(test_df, None)
        pd.testing.assert_frame_equal(test_df, result_df)
        self.assertIsNone(remarks, "Expected there to be no remarks data output.") 
#4.)        
        with self.assertRaises(TypeError):
            parse_remarks_table([], [])
