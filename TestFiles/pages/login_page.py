from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    """Page Object Model for Login Page"""

    # Locators
    COMPANY_SELECT= (By.XPATH, "/html/body/nav/div[2]/div/ul[1]/li[6]/a")
    CAREERS_SELECT= (By.XPATH, "//*[@id='navbarNavDropdown']/ul[1]/li[6]/div/div[2]/a[2]")
    # COMPANY_DROPDOWN_TABLE = (By.ID, "cbCompany_B-1Img")
    # COMPANY_DROPDOWN_LIST = (By.XPATH, "//tr[@class='dxeListBoxItemRow']")
    # USERNAME = (By.ID, "teUser_I")
    # PASSWORD = (By.ID, "PV_I")
    # LOGIN_BUTTON = (By.ID, "btn_CD")
    # BEAM_SYSTEM_ADMIN_RADIO = (By.ID, "xppcProcurationList_xrblProcurationList_RB0_I_D")
    # CONTINUE_BUTTON = (By.ID, "xppcProcurationList_xbtnContinue_CD")
    # INCORRECT_MESSAGE = (By.XPATH, "//span[@id='xmmMessage']")
    # INCORRECT_MESSAGE_BUTTON = (By.ID, "MessageBox1_xpcMsgBox_xbtnOK_CD")

    def __init__(self):
        super().__init__()

    def get_company_select(self):
        """Get company select element"""
        return self.find_element(self.COMPANY_SELECT)
    
    def get_careers_select(self):
        """Get careers select element"""
        return self.find_element(self.CAREERS_SELECT)

    # def get_company_dropdown_table(self):
    #     """Get company dropdown table element"""
    #     return self.find_element(self.COMPANY_DROPDOWN_TABLE)

    # def get_company_dropdown_list(self):
    #     """Get company dropdown list elements"""
    #     return self.find_elements(self.COMPANY_DROPDOWN_LIST)

    # def get_username_field(self):
    #     """Get username field element"""
    #     return self.find_element(self.USERNAME)

    # def get_password_field(self):
    #     """Get password field element"""
    #     return self.find_element(self.PASSWORD)

    # def get_login_button(self):
    #     """Get login button element"""
    #     return self.find_element(self.LOGIN_BUTTON)

    # def get_beam_system_admin_radio(self):
    #     """Get BEAM System Administrator radio button element"""
    #     return self.find_element(self.BEAM_SYSTEM_ADMIN_RADIO)

    # def get_continue_button(self):
    #     """Get continue button element"""
    #     return self.find_element(self.CONTINUE_BUTTON)

    # def get_incorrect_message(self):
    #     """Get incorrect message element"""
    #     return self.find_element(self.INCORRECT_MESSAGE)

    # def get_incorrect_message_button(self):
    #     """Get incorrect message button element"""
    #     return self.find_element(self.INCORRECT_MESSAGE_BUTTON)
