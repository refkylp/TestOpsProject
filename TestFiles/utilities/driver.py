from selenium import webdriver
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
            browser = ConfigReader.get_property("browser")

            # Selenium 4+ automatically manages drivers (Selenium Manager)
            # No need for webdriver-manager anymore
            if browser == "firefox":
                cls._driver = webdriver.Firefox()
            elif browser == "edge":
                cls._driver = webdriver.Edge()
            elif browser == "safari":
                cls._driver = webdriver.Safari()
            else:  # default chrome
                cls._driver = webdriver.Chrome()

            cls._driver.maximize_window()
            cls._driver.implicitly_wait(15)

        return cls._driver

    @classmethod
    def close_driver(cls):
        """Close and quit the driver"""
        if cls._driver is not None:
            cls._driver.quit()
            cls._driver = None
