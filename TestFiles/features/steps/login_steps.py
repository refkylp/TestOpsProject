from behave import given, when, then
from utilities.reusable_methods import ReusableMethods
from utilities.driver import Driver

@given('Goes to the given "{url}"')
def step_navigate_to_url(context, url):
    """Navigate to the given URL"""
    ReusableMethods.navigate_to_url(url)
    ReusableMethods.wait(10)

@given('Click the Company button')
def step_click_company_button(context):
    """Click the Company button"""
    element = context.login_page.get_company_select()
    Driver.get_driver().execute_script("arguments[0].click();", element)
    ReusableMethods.wait(10)

@given('Click the Careers button')
def step_click_careers_button(context):
    """Click the Careers button"""
    element = context.login_page.get_careers_select()
    Driver.get_driver().execute_script("arguments[0].click();", element)
    ReusableMethods.wait(10)



# from behave import given, when, then
# from utilities.reusable_methods import ReusableMethods
# from utilities.driver import Driver

# @given('Goes to the given "{url}"')
# def step_navigate_to_url(context, url):
#     """Navigate to the given URL"""
#     ReusableMethods.navigate_to_url(url)
#     ReusableMethods.wait(10)

# @given('Click the Company button')
# def step_click_company_button(context):
#     """Click the Company button"""
#     context.login_page.get_company_select().click()
#     ReusableMethods.wait(10)

# @given('Click the Careers button')
# def step_click_careers_button(context):
#     """Click the Careers button"""
#     context.login_page.get_careers_select().click()
#     ReusableMethods.wait(10)



# @given('Select the correct "{company}", enter the correct "{username}" and "{password}"')
# def step_login_with_correct_credentials(context, company, username, password):
#     """Login with correct credentials"""
#     context.reusable_methods.select_company(
#         context.login_page.get_company_dropdown_table(),
#         context.login_page.get_company_dropdown_list(),
#         company
#     )
#     ReusableMethods.wait(1)
#     context.login_page.get_username_field().send_keys(ReusableMethods.get_username(username))
#     ReusableMethods.wait(1)
#     context.login_page.get_password_field().send_keys(ReusableMethods.get_password(password))
#     ReusableMethods.wait(1)

# @given('Click the Login button')
# def step_click_login_button(context):
#     """Click the login button"""
#     context.login_page.get_login_button().click()

# @given('Click the BEAM SYSTEM ADMINISTRATOR radio button')
# def step_click_beam_admin_radio(context):
#     """Click BEAM System Administrator radio button"""
#     context.login_page.get_beam_system_admin_radio().click()
#     ReusableMethods.wait(1)

# @given('Click the Continue button')
# def step_click_continue_button(context):
#     """Click continue button"""
#     context.login_page.get_continue_button().click()

# @then('Confirm that the text "{text}" is visible')
# def step_confirm_text_visible(context, text):
#     """Confirm that expected text is visible"""
#     ReusableMethods.wait(1)
#     actual_text = context.dashboard_page.get_user_id_text().text
#     assert actual_text.lower() == text.lower(), f"Expected '{text}' but got '{actual_text}'"
#     print("Positive login test success")
#     ReusableMethods.wait(1)
#     Driver.close_driver()

# # Negative login tests
# @given('Select the correct "{company}", enter the correct "{username}" and incorrect "{incorrect_password}"')
# def step_login_with_incorrect_password(context, company, username, incorrect_password):
#     """Login with correct username but incorrect password"""
#     context.reusable_methods.select_company(
#         context.login_page.get_company_dropdown_table(),
#         context.login_page.get_company_dropdown_list(),
#         company
#     )
#     ReusableMethods.wait(1)
#     context.login_page.get_username_field().send_keys(ReusableMethods.get_username(username))
#     ReusableMethods.wait(1)
#     context.login_page.get_password_field().send_keys(ReusableMethods.get_password(incorrect_password))
#     ReusableMethods.wait(1)

# @then('Confirm that incorrect message is "{message}"')
# def step_confirm_incorrect_message(context, message):
#     """Confirm that incorrect login message is displayed"""
#     ReusableMethods.wait(1)
#     actual_message = context.login_page.get_incorrect_message().text
#     assert actual_message.lower() == message.lower(), f"Expected '{message}' but got '{actual_message}'"
#     context.login_page.get_incorrect_message_button().click()
#     ReusableMethods.wait(1)
#     Driver.close_driver()

# @given('Select the correct "{company}", enter the incorrect "{incorrect_username}" and correct "{password}"')
# def step_login_with_incorrect_username(context, company, incorrect_username, password):
#     """Login with incorrect username but correct password"""
#     context.reusable_methods.select_company(
#         context.login_page.get_company_dropdown_table(),
#         context.login_page.get_company_dropdown_list(),
#         company
#     )
#     ReusableMethods.wait(1)
#     context.login_page.get_username_field().send_keys(ReusableMethods.get_username(incorrect_username))
#     ReusableMethods.wait(1)
#     context.login_page.get_password_field().send_keys(ReusableMethods.get_password(password))
#     ReusableMethods.wait(1)

# @given('Select the correct "{company}", enter the incorrect "{incorrect_username}" and "{incorrect_password}"')
# def step_login_with_incorrect_credentials(context, company, incorrect_username, incorrect_password):
#     """Login with incorrect username and password"""
#     context.reusable_methods.select_company(
#         context.login_page.get_company_dropdown_table(),
#         context.login_page.get_company_dropdown_list(),
#         company
#     )
#     ReusableMethods.wait(1)
#     context.login_page.get_username_field().send_keys(ReusableMethods.get_username(incorrect_username))
#     ReusableMethods.wait(1)
#     context.login_page.get_password_field().send_keys(ReusableMethods.get_password(incorrect_password))
#     ReusableMethods.wait(1)

# @given('Select the incorrect "{company}", enter the correct "{username}" and "{password}"')
# def step_login_with_incorrect_company(context, company, username, password):
#     """Login with incorrect company"""
#     ReusableMethods.wait(2)
#     context.login_page.get_company_dropdown_table().click()
#     ReusableMethods.wait(2)

#     companies = context.login_page.get_company_dropdown_list()
#     for comp in companies:
#         if comp.text.lower() == company.lower():
#             comp.click()
#             break

#     ReusableMethods.wait(1)
#     context.login_page.get_username_field().send_keys(ReusableMethods.get_username(username))
#     ReusableMethods.wait(1)
#     context.login_page.get_password_field().send_keys(ReusableMethods.get_password(password))
#     ReusableMethods.wait(1)
