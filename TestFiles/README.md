# Bimser Test Automation Project (Python)

This is a Python port of the original Java Selenium + Cucumber test automation project.

## Project Structure

```
bimserProject-python/
├── features/
│   ├── login.feature
│   ├── dashboard.feature
│   └── steps/
│       ├── base_steps.py
│       ├── login_steps.py
│       └── dashboard_steps.py
├── pages/
│   ├── base_page.py
│   ├── login_page.py
│   └── dashboard_page.py
├── utilities/
│   ├── driver.py
│   ├── config_reader.py
│   └── reusable_methods.py
├── configuration.properties
├── requirements.txt
└── environment.py
```

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

Run all tests:
```bash
behave
```

Run tests with specific tags:
```bash
behave --tags=@positiveLogin
behave --tags=@negativeLogin
behave --tags=@dashboard
```

## Generate Allure Report

```bash
behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results
allure serve reports/allure-results
```
