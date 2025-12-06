from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utilities.driver import Driver

class BasePage:
    """Base class for all page objects"""

    def __init__(self):
        self.driver = Driver.get_driver()
        self.wait = WebDriverWait(self.driver, 15)

    def find_element(self, locator):
        """Find and return a single element"""
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_elements(self, locator):
        """Find and return multiple elements"""
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def click_element(self, locator):
        """Click on element"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
