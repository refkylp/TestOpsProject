import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from utilities.config_reader import ConfigReader
from utilities.driver import Driver

class ReusableMethods:

    @staticmethod
    def get_company(company):
        """Get company from configuration"""
        return ConfigReader.get_property(company)

    @staticmethod
    def get_username(username):
        """Get username from configuration"""
        return ConfigReader.get_property(username)

    @staticmethod
    def get_password(password):
        """Get password from configuration"""
        return ConfigReader.get_property(password)

    def select_company(self, company_dropdown_table, company_dropdown_list, company):
        """Select company from dropdown"""
        ReusableMethods.wait(2)
        company_dropdown_table.click()
        ReusableMethods.wait(2)

        company_value = ReusableMethods.get_company(company)
        for comp in company_dropdown_list:
            if comp.text.lower() == company_value.lower():
                comp.click()
                break

    @staticmethod
    def wait(seconds):
        """Wait for specified seconds"""
        try:
            time.sleep(seconds)
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException, Exception) as e:
            print(f"Exception in wait: {e}")

    @staticmethod
    def navigate_to_url(url):
        """Navigate to the requested URL"""
        url_value = ConfigReader.get_property(url)
        Driver.get_driver().get(url_value)
