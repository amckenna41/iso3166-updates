import os
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException

def create_driver() -> webdriver.Chrome:
    """
    Create instance of Selenium Chromedriver for each country's individual page on the 
    official ISO website. The site requires a session to be created and Javascript to
    be run, therefore the page's data cannot be directly webscraped. For some countries 
    their ISO page contains extra data not on the country's wiki page. 

    Parameters
    ==========
    None

    Returns
    =======
    :driver: selenium.webdriver.chrome.webdriver.WebDriver
        instance of Python Selenium using chromedriver webdriver.
    
    References
    ==========
    [1]: https://chromedriver.chromium.org/getting-started
    [2]: https://www.geeksforgeeks.org/how-to-install-selenium-in-python/
    [3]: https://www.scrapingbee.com/webscraping-questions/selenium/chromedriver-executable-needs-to-be-in-path/
    [4]: https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json
    [5]: https://googlechromelabs.github.io/chrome-for-testing/

    Notes
    =====
    - If Chrome Binary and Chromedriver versions are incompatible, remove chromedriver and reinstall: 
        find / -name chromedriver 2>/dev/null (find chromedriver)
        sudo rm /usr/local/bin/chromedriver (remove)
        chromedriver --version (verify uninstall)
        brew install chromedriver (reinstall)
        chromedriver --version (verify install)
    - If there is a Runtime Error in the function that is calling create_driver(), the error might be in this
        function. For example syntax errors in this function might not be highlighted if a Runtime Error is thrown
        from the calling function.
    - If there is a runtime error with initialising the instance, double check the version of chromedriver & update:
        brew install chromedriver
    - Find where chromedriver is installed:
        which chromedriver
    
    Raises
    ======
    WebDriverException:
        Chromedriver not found at list of paths.
    FileNotFoundError:
        Chrome binary not found at list of possible locations.
    RuntimeError:
        Issue initialising the Chromedriver instance. 
    """
    #list of paths chromedriver might be stored in
    chromedriver_executable_paths = [
        '/usr/local/bin/chromedriver', 
        '/usr/bin/chromedriver', 
        '/usr/lib/chromedriver'
        ]
    chromedriver_executable_path = ""
    chromedriver_path_found = False

    #iterate over potential likely paths for chromedriver executable 
    for path in chromedriver_executable_paths:
        if (os.path.isfile(path)):
            chromedriver_path_found = True
            chromedriver_executable_path = path

    #verify Chromedriver is found on one of the paths, raise exception if not
    if not (chromedriver_path_found):
      raise WebDriverException(f"Chromedriver not found, verify it's installed in one of the paths: {', '.join(chromedriver_executable_paths)}")

    #create instance of Service class and get executable path of chromedriver
    service = Service(executable_path=chromedriver_executable_path)

    #create instance of Options class, add below options to Chromedriver instance
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    # chrome_options.headless = False
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--window-size=1920,1080") 
    chrome_options.add_argument("--disable-popup-blocking")  
    chrome_options.add_argument("--ignore-certificate-errors") 
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    chrome_options.add_experimental_option("useAutomationExtension", False) 

    #list of possible Chrome binary paths
    possible_binary_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",   # macOS
        "/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome", # macOS
        "/usr/bin/google-chrome",                                         # Linux
        "/usr/bin/google-chrome-stable",                                  # Linux
        "/usr/local/bin/google-chrome",                                   # Linux alternative
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",     # Windows
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"  # Windows (32-bit)
    ]

    chrome_binary_path = ""
    
    #iterate through possible Chrome binary paths, raise error if not found via paths
    for path in possible_binary_paths:
        if (os.path.exists(path)):
            chrome_binary_path = path
            break
    else:
        raise FileNotFoundError(f"Chrome binary not found at list of possible locations:\n{', '.join(possible_binary_paths)}.")
    
    #when testing locally need to specify the binary location of Google Chrome: find / -type d -name "*Chrome.app"
    chrome_options.binary_location = chrome_binary_path

    #initialise driver object before try block
    driver = None

    try:
        #create webdriver instance
        driver = webdriver.Chrome(service=service, options=chrome_options)

        #set object to undefined, helps avoid bot detection
        # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
        
        #set random user-agent string for WebDriver to avoid detection, using fake_useragent package
        user_agent_header = UserAgent().random
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent_header}) 

    #raise exception if issue creating chromedriver, always close chromedriver with finally statement
    except Exception as e:
        raise RuntimeError(f"Failed to initialize WebDriver: {e}")

    return driver