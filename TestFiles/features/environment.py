"""
Behave environment configuration
This file contains hooks that run before/after scenarios, features, etc.
"""

from utilities.driver import Driver
from pages.login_page import LoginPage
# from pages.dashboard_page import DashboardPage
from utilities.reusable_methods import ReusableMethods

def before_all(context):
    """Runs once before all tests"""
    pass

def before_feature(context, feature):
    """Runs before each feature"""
    pass

def before_scenario(context, scenario):
    """Runs before each scenario"""
    # Initialize page objects for each scenario
    context.login_page = LoginPage()
    # context.dashboard_page = DashboardPage()
    context.reusable_methods = ReusableMethods()

def after_scenario(context, scenario):
    """Runs after each scenario"""
    # Close driver after each scenario if it's still open
    try:
        Driver.close_driver()
    except Exception as e:
        print(f"Error closing driver: {e}")

def after_feature(context, feature):
    """Runs after each feature"""
    pass

def after_all(context):
    """Runs once after all tests"""
    # Ensure driver is closed
    try:
        Driver.close_driver()
    except Exception as e:
        print(f"Error closing driver in after_all: {e}")
