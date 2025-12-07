import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utilities.config_reader import ConfigReader
import time

class Driver:
    _driver = None

    def __init__(self):
        """Private constructor - use get_driver() instead"""
        raise Exception("Use get_driver() method to get driver instance")

    @classmethod
    def get_driver(cls):
        """Get or create WebDriver instance"""
        if cls._driver is None:
            # Check if running in Kubernetes (Remote WebDriver mode)
            remote_url = os.getenv("SELENIUM_REMOTE_URL")
            
            if remote_url:
                # Kubernetes mode - Use Remote WebDriver
                print(f"Running in Kubernetes mode")
                print(f"Connecting to Selenium Grid: {remote_url}")
                cls._driver = cls._create_remote_driver(remote_url)
            else:
                # Local mode - Use local WebDriver
                print("Running in Local mode")
                cls._driver = cls._create_local_driver()
            
            # Common configurations
            cls._driver.maximize_window()
            cls._driver.implicitly_wait(15)

        return cls._driver

    @classmethod
    def _create_remote_driver(cls, remote_url):
        """
        Create Remote WebDriver for Kubernetes/Selenium Grid
        """
        # Get browser from config (default: chrome)
        browser = ConfigReader.get_property("browser")
        
        if browser == "firefox":
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            options = FirefoxOptions()
        elif browser == "edge":
            from selenium.webdriver.edge.options import Options as EdgeOptions
            options = EdgeOptions()
        else:  # default chrome
            options = Options()
        
        # Common headless options (required for Kubernetes)
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        
        # Additional stability options for remote execution
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-setuid-sandbox")
        
        try:
            driver = webdriver.Remote(
                command_executor=remote_url,
                options=options
            )
            print(f"✅ Remote {browser.upper()} WebDriver created successfully")
            return driver
        except Exception as e:
            print(f"Failed to create Remote WebDriver: {e}")
            print(f"   Remote URL: {remote_url}")
            print(f"   Browser: {browser}")
            raise

    @classmethod
    def _create_local_driver(cls):
        """
        Create local WebDriver for development/testing
        """
        browser = ConfigReader.get_property("browser")

        # Selenium 4+ automatically manages drivers (Selenium Manager)
        # No need for webdriver-manager anymore
        if browser == "firefox":
            driver = webdriver.Firefox()
        elif browser == "edge":
            driver = webdriver.Edge()
        elif browser == "safari":
            driver = webdriver.Safari()
        else:  # default chrome
            chrome_options = Options()
            
            # Headless mode for local (optional - comment out if you want to see browser)
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            driver = webdriver.Chrome(options=chrome_options)
        
        print(f"Local {browser.upper()} WebDriver created successfully")
        return driver

    @classmethod
    def close_driver(cls):
        """Close and quit the driver"""
        if cls._driver is not None:
            try:
                cls._driver.quit()
                print("WebDriver closed successfully")
            except Exception as e:
                print(f"Error closing driver: {e}")
            finally:
                cls._driver = None