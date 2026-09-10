import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def create_driver(browser: str):
    browser = browser.lower()
    print(f"WebDriverFactory - Browser: {browser}")

    if browser == "chrome":
        options = ChromeOptions()
        if os.getenv("GITHUB_ACTIONS", "").lower() == "true" or os.getenv("CI") or os.getenv("JENKINS_HOME"):
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(options=options)

    if browser == "firefox":
        options = FirefoxOptions()
        if os.getenv("CI") or os.getenv("JENKINS_HOME"):
            options.add_argument("-headless")
        return webdriver.Firefox(options=options)

    raise ValueError(f"Unsupported browser: {browser}")
