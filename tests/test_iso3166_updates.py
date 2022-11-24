import iso3166_updates
import unittest
unittest.TestLoader.sortTestMethodsUsing = None


class ISO3166_Updates(unittest.TestCase):

    def setUp(self):
        """ """

    def test_iso3166_updates_metadata(self):
        """ Testing correct iso3166-updates version and metadata. """
        self.assertEqual(iso3166_updates.__version__, "0.0.2", "iso3166-updates version is not correct, got: {}".format(iso3166_updates.__version__))
        self.assertEqual(iso3166_updates.__name__, "iso3166-updates", "iso3166-updates software name is not correct, got: {}".format(iso3166_updates.__name__))
        self.assertEqual(iso3166_updates.__author__, "AJ McKenna, https://github.com/amckenna41", "iso3166-updates author is not correct, got: {}".format(iso3166_updates.__author__))
        self.assertEqual(iso3166_updates.__authorEmail__, "amckenna41@qub.ac.uk", "iso3166-updates author email is not correct, got: {}".format(iso3166_updates.__authorEmail__))
        self.assertEqual(iso3166_updates.__url__, "https://github.com/amckenna41/iso3166-updates", "iso3166-updates repo URL is not correct, got: {}".format(iso3166_updates.__url__))
        self.assertEqual(iso3166_updates.__credits__, ['AJ McKenna'], "iso3166-updates credits is not correct, got: {}".format(iso3166_updates.__credits__))
        self.assertEqual(iso3166_updates.__license__, "MIT", "iso3166-updates license type is not correct, got: {}".format(iso3166_updates.__license__))
        self.assertEqual(iso3166_updates.__maintainer__, "AJ McKenna", "iso3166-updates maintainer is not correct, got: {}".format(iso3166_updates.__license__))

    def tearDown(self):
        """  """

if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)

