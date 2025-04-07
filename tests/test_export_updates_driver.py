try:
    from iso3166_updates_export.driver import create_driver
except:
    from ..iso3166_updates_export.driver import create_driver
from selenium.common.exceptions import WebDriverException
from unittest.mock import MagicMock, patch
import unittest
unittest.TestLoader.sortTestMethodsUsing = None

class ISO3166_Export_Updates_Driver_Tests(unittest.TestCase):
    """
    Test suite for testing the driver module script that initialises the Selenium 
    Chromedriver instance, required to parse data from the ISO pages. 
    
    Test Cases
    ==========
    test_driver_initialization_success: 
        testing driver is initialised from create_driver() function. 
    test_chromedriver_not_found:
        test exception is raised when error finding chromedriver instance.
    test_chrome_binary_not_found:
        test exception is raised when Google Chrome binary isn't found. 
    test_driver_initialization_failure:
        test exception is raised if error during initialisation of driver object.
    test_user_agent_set:
        testing user agent has updated in chromedriver initialisation.
    test_driver_cleanup_on_failure:
        testing driver session is properly closed.
    test_chrome_options_applied:
        testing chrome options are applied on Chromedriver initialisation. 
    """
    @patch("os.path.isfile")
    @patch("os.path.exists")
    @patch("selenium.webdriver.Chrome")
    def test_driver_initialization_success(self, mock_chrome, mock_path_exists, mock_isfile):
        """ Test that the driver is initialised on function call. """
        #create mock object
        mock_isfile.side_effect = lambda path: path == "/usr/local/bin/chromedriver"
        mock_driver_instance = MagicMock()
        mock_chrome.return_value = mock_driver_instance

        #create driver 
        driver = create_driver()

        mock_chrome.assert_called_once()
        self.assertEqual(driver, mock_driver_instance, "Chromedriver instance wasn't initialised correctly.")

    @patch("os.path.isfile")
    def test_chromedriver_not_found(self, mock_isfile):
        """ Test error raised when chromedriver not found. """
        mock_isfile.return_value = False

        with self.assertRaises(WebDriverException) as context:
            create_driver()

        self.assertIn("Chromedriver not found", str(context.exception), "WebDriverException not raised when Chromedriver not found.")

    @patch("os.path.isfile")
    @patch("os.path.exists")
    def test_chrome_binary_not_found(self, mock_path_exists, mock_isfile):
        """ Test error raised when Google Chrome binary not found. """
        mock_isfile.return_value = True
        mock_path_exists.return_value = False

        with self.assertRaises(FileNotFoundError) as context:
            create_driver()

        self.assertIn("Chrome binary not found", str(context.exception), "FileNotFounnd error not raised when Google Chrome binary wasn't found.")

    @patch("os.path.isfile")
    @patch("os.path.exists")
    @patch("selenium.webdriver.Chrome")
    def test_driver_initialization_failure(self, mock_chrome, mock_path_exists, mock_isfile):
        """ Test RuntimeError raised when issue initialising Chromedriver instance. """
        mock_isfile.side_effect = lambda path: path == "/usr/local/bin/chromedriver"
        # mock_path_exists.side_effect = lambda path: path == "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        mock_chrome.side_effect = RuntimeError("Failed to initialize WebDriver")

        with self.assertRaises(RuntimeError) as context:
            create_driver()

        self.assertIn("Failed to initialize WebDriver", str(context.exception), "RuntimeError not raised when issue initialising Chromedriver instance.")

    @patch("os.path.isfile")
    @patch("os.path.exists")
    @patch("selenium.webdriver.Chrome")
    def test_user_agent_set(self, mock_chrome, mock_path_exists, mock_isfile):
        """ Testing user agent is updated on chromedriver initialisation. """
        mock_isfile.side_effect = lambda path: path == "/usr/local/bin/chromedriver"
        # mock_path_exists.side_effect = lambda path: path == "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        mock_driver_instance = MagicMock()
        mock_chrome.return_value = mock_driver_instance

        create_driver()

        mock_driver_instance.execute_cdp_cmd.assert_called_with(
            "Network.setUserAgentOverride",
            {"userAgent": unittest.mock.ANY}
        )

    # @patch("os.path.isfile")
    # @patch("os.path.exists")
    # @patch("selenium.webdriver.Chrome")
    # def test_driver_cleanup_on_failure(self, mock_chrome, mock_path_exists, mock_isfile):
    #     """ """
    #     mock_isfile.side_effect = lambda path: path == "/usr/local/bin/chromedriver"
    #     mock_path_exists.side_effect = lambda path: path == "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    #     mock_chrome.side_effect = Exception("Some failure")

    #     with self.assertRaises(RuntimeError):
    #         create_driver()

    @patch("os.path.isfile")
    @patch("os.path.exists")
    @patch("selenium.webdriver.Chrome")
    def test_chrome_options_applied(self, mock_chrome, mock_path_exists, mock_isfile):
        """ Testing chrome options are applied to Chromedriver on initialisation. """
        mock_isfile.side_effect = lambda path: path == "/usr/local/bin/chromedriver"
        # mock_path_exists.side_effect = lambda path: path == "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        mock_driver_instance = MagicMock()
        mock_chrome.return_value = mock_driver_instance

        with patch("selenium.webdriver.ChromeOptions") as mock_options:
            options_instance = mock_options.return_value
            create_driver()

            expected_options = [
                "--headless",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "start-maximized",
                "--window-size=1920,1080",
                "--disable-popup-blocking",
                "--ignore-certificate-errors",
                '--disable-blink-features=AutomationControlled'
            ]
            for option in expected_options:
                options_instance.add_argument.assert_any_call(option)

if __name__ == '__main__':
    #run all unit tests
    unittest.main(verbosity=2)