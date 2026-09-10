import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions


# ChromeDriver available on this Windows machine
CHROMEDRIVER_PATH = (
    r"C:\Users\moham\.cache\selenium\chromedriver\win64"
    r"\152.0.7977.82\chromedriver.exe"
)


def create_driver(browser: str):
    browser = browser.lower()
    print(f"WebDriverFactory - Browser: {browser}")

    # =========================
    # CHROME
    # =========================
    if browser == "chrome":
        options = ChromeOptions()

        # Headless mode for Jenkins / GitHub Actions / CI
        if (
            os.getenv("GITHUB_ACTIONS", "").lower() == "true"
            or os.getenv("CI")
            or os.getenv("JENKINS_HOME")
        ):
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        print(f"ChromeDriver: {CHROMEDRIVER_PATH}")

        service = Service(CHROMEDRIVER_PATH)

        return webdriver.Chrome(
            service=service,
            options=options,
        )

    # =========================
    # FIREFOX
    # =========================
    if browser == "firefox":
        options = FirefoxOptions()

        # Headless mode for Jenkins / CI
        if os.getenv("CI") or os.getenv("JENKINS_HOME"):
            options.add_argument("-headless")

        return webdriver.Firefox(options=options)

    # =========================
    # UNSUPPORTED BROWSER
    # =========================
    raise ValueError(f"Unsupported browser: {browser}")
