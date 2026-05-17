try:
    from iso3166_updates_export.parse_updates_data import *
except:
    from ..iso3166_updates_export.parse_updates_data import *
import unittest
unittest.TestLoader.sortTestMethodsUsing = None

# @unittest.skip("Skipping parse_updates_data tests.")
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

    # @unittest.skip("")
    def test_parse_updates_table(self):
        """ Testing functionality that parses the updates table data into valid format. """
#1.)
        test_input_data = test_input_data = [
            ["Change", "Description of Change", "Date Issued", "Source"],
            ["New entry", "Added new subdivision", "2023-01-01", "Official"],
            ["→ Change", "Name updated", "2024-02-15", "ISO OBP"],
            ["Correction", "Boundary adjustment", "2022-08-10 (corrected 2023-05-20)", "Gov Report"],
            ["Deletion", "Removed obsolete entry", "2021-12-31", "Official Doc"],
            ["Merge", "Merged two regions", "2020-05-20", "ISO Official"],
            ["Split", "Split one region into two", "2019-07-15", "ISO Update"],
            ["Renaming", "Country renamed", "2018-11-30", "Gov Announcement"],
        ]
        test_expected_output = pd.DataFrame(
            {
                "Change": ["-> Change", "New entry", "Correction", "Deletion", "Merge", "Split", "Renaming"],
                "Description of Change": ["Name updated", "Added new subdivision", "Boundary adjustment", "Removed obsolete entry", "Merged two regions", "Split one region into two", "Country renamed"],
                "Date Issued": ["2024-02-15", "2023-01-01", "2022-08-10 (corrected 2023-05-20)", "2021-12-31", "2020-05-20", "2019-07-15", "2018-11-30"],
                "Source": [
                    "ISO OBP",
                    "Official", "Gov Report", "Official Doc", "ISO Official", "ISO Update", "Gov Announcement"
                ]
            }
        )
        #test resultant and expected dataframes are equal
        result = parse_updates_table("US", test_input_data)
        pd.testing.assert_frame_equal(result.reset_index(drop=True), test_expected_output.reset_index(drop=True))
#2.)
        with self.assertRaises(TypeError):
            parse_updates_table("US", {})
            parse_updates_table("AD", "")
            parse_updates_table("DE", 1.04)

    # @unittest.skip("")
    def test_parse_remarks_table(self):
        """ Testing functionality that parses the remarks table data from ISO page. """
        class MockTag:
            def __init__(self, label_text, value_text):
                self.label_text = label_text
                self.value_text = value_text

            def find(self, class_=None):
                class Dummy:
                    def __init__(self, text):
                        self.text = text
                if class_ == "core-view-field-name":
                    return Dummy(self.label_text)
                elif class_ == "core-view-field-value":
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
        self.assertEqual(["Change", "Description of Change", "Date Issued", "Source"], list(updated_df.columns), f"Expected and observed list of output columns do not match:\n{updated_df.columns}.")
#3.)
        test_df = pd.DataFrame([
            ["Change", "Some update", "2024-01-01", "ISO"]
        ], columns=["Change", "Description of Change", "Date Issued", "Source"])

        #test resultant and expected dataframes are equal
        result_df, remarks = parse_remarks_table(test_df, None)
        pd.testing.assert_frame_equal(test_df, result_df)
        self.assertEqual(remarks, {}, "Expected there to be no remarks data output.") 
#4.)        
        with self.assertRaises(TypeError):
            parse_remarks_table([], [])

    # @unittest.skip("")
    def test_parse_updates_table_tbd_swap(self):
        """ Testing that when Change is '(TBD).', its value is swapped with Description of Change 
            and Description of Change is cleared. """
#1.)
        test_input_data = [
            ["Change", "Description of Change", "Date Issued", "Source"],
            ["(TBD).", "Name changed to new subdivision name.", "2023-06-01", "Official"],
            ["Normal change.", "Normal description.", "2022-03-10", "Official"],
        ]
        result = parse_updates_table("DE", test_input_data)

        tbd_row = result[result["Change"] == "Name changed to new subdivision name."]
        self.assertEqual(len(tbd_row), 1, "Expected the TBD row to have its Change swapped with Description of Change.")
        self.assertEqual(tbd_row["Description of Change"].iloc[0], "", "Expected Description of Change to be empty after TBD swap.")

        normal_row = result[result["Change"] == "Normal change."]
        self.assertEqual(len(normal_row), 1, "Expected the normal row to be unchanged.")
        self.assertEqual(normal_row["Description of Change"].iloc[0], "Normal description.", "Expected Description of Change to be unchanged for normal row.")

    # @unittest.skip("")
    def test_parse_updates_table_source_normalization(self):
        """ Testing that empty or bare source values are replaced with the OBP URL for the alpha code. """
#1.) Empty source replaced with OBP URL
        test_input_data = [
            ["Change", "Description of Change", "Date Issued", "Source"],
            ["Some change.", "Some description.", "2023-01-01", ""],
        ]
        result = parse_updates_table("FR", test_input_data)
        self.assertEqual(result["Source"].iloc[0], "Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:FR.",
            f"Expected empty source to be replaced with OBP URL for FR:\n{result['Source'].iloc[0]}")
#2.) Non-OBP newsletter source preserved
        test_input_data_newsletter = [
            ["Change", "Description of Change", "Date Issued", "Source"],
            ["Code correction.", "", "2011-12-13", "Newsletter II-3 - https://www.iso.org/files/live/sites/isoorg/files/archive/pdf/en/iso_3166-2_newsletter_ii-3_2011-12-13.pdf."],
        ]
        result_newsletter = parse_updates_table("AZ", test_input_data_newsletter)
        self.assertIn("Newsletter II-3", result_newsletter["Source"].iloc[0],
            f"Expected newsletter source to be preserved:\n{result_newsletter['Source'].iloc[0]}")

    # @unittest.skip("")
    def test_parse_updates_table_missing_optional_columns(self):
        """ Testing that missing optional columns (Change, Source, Description of Change) are 
            added with empty string values when absent from input. """
#1.) Input with only Date Issued column — other columns should be added
        test_input_data = [
            ["Date Issued"],
            ["2023-01-01"],
            ["2022-06-15"],
        ]
        result = parse_updates_table("JP", test_input_data)
        self.assertIn("Change", result.columns, "Expected 'Change' column to be added when absent.")
        self.assertIn("Description of Change", result.columns, "Expected 'Description of Change' column to be added when absent.")
        self.assertIn("Source", result.columns, "Expected 'Source' column to be added when absent.")

    # @unittest.skip("")
    def test_parse_remarks_table_partial_remarks(self):
        """ Testing parse_remarks_table when only a subset of remark parts are present. """
        class MockTag:
            def __init__(self, label_text, value_text):
                self.label_text = label_text
                self.value_text = value_text

            def find(self, class_=None):
                class Dummy:
                    def __init__(self, text):
                        self.text = text
                if class_ == "core-view-field-name":
                    return Dummy(self.label_text)
                elif class_ == "core-view-field-value":
                    return Dummy(self.value_text)
                return None
#1.) Only part1 and part2 present — part3 and part4 should remain empty
        mock_summary_table = [
            MockTag("Remark Part 1", "First remark only."),
            MockTag("Remark Part 2", "Second remark only."),
        ]
        df_input = pd.DataFrame([
            ["Update", "Initial change", "2023-05-01", "Source"]
        ], columns=["Change", "Description of Change", "Date Issued", "Source"])

        _, remarks = parse_remarks_table(df_input, mock_summary_table)
        self.assertEqual(remarks["part1"], "First remark only", f"Expected part1 to be set:\n{remarks['part1']}.")
        self.assertEqual(remarks["part2"], "Second remark only", f"Expected part2 to be set:\n{remarks['part2']}.")
        self.assertEqual(remarks["part3"], "", f"Expected part3 to be empty:\n{remarks['part3']}.")
        self.assertEqual(remarks["part4"], "", f"Expected part4 to be empty:\n{remarks['part4']}.")
#2.) Only part1 present
        mock_summary_table_single = [
            MockTag("Remark Part 1", "Only one remark."),
        ]
        _, remarks_single = parse_remarks_table(df_input, mock_summary_table_single)
        self.assertEqual(remarks_single["part1"], "Only one remark", f"Expected part1 to be set:\n{remarks_single['part1']}.")
        self.assertEqual(remarks_single["part2"], "", f"Expected part2 to be empty:\n{remarks_single['part2']}.")
        self.assertEqual(remarks_single["part3"], "", f"Expected part3 to be empty:\n{remarks_single['part3']}.")
        self.assertEqual(remarks_single["part4"], "", f"Expected part4 to be empty:\n{remarks_single['part4']}.")
