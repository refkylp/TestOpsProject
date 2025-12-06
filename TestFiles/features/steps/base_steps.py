from pages.login_page import LoginPage
from utilities.reusable_methods import ReusableMethods

class BaseSteps:
    """Base class for all step definitions"""

    def __init__(self):
        self.login_page = LoginPage()
        self.reusable_methods = ReusableMethods()
