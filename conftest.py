import os
from datetime import datetime
from pathlib import Path

import pytest
from pytest_metadata.plugin import metadata_key

from utils.driver_factory import create_driver

REPORT_DIR = Path("reports")
SCREENSHOT_DIR = REPORT_DIR / "screenshots"


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        choices=["chrome", "firefox"],
        help="Browser to use: chrome or firefox",
    )
    parser.addoption(
        "--env",
        action="store",
        default=None,
        choices=["qa", "prod"],
        help="Test environment: qa or prod",
    )


def pytest_configure(config):
    REPORT_DIR.mkdir(exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Set TEST_ENV before test collection.
    cli_env = config.getoption("--env")
    if cli_env:
        os.environ["TEST_ENV"] = cli_env

    # Information displayed in the HTML report.
    browser = config.getoption("--browser")
    environment = cli_env or "qa"

    config.stash[metadata_key]["Project"] = (
        "Selenium Python Pytest Automation Framework"
    )
    config.stash[metadata_key]["Environment"] = environment.upper()
    config.stash[metadata_key]["Browser"] = browser.capitalize()
    config.stash[metadata_key]["Test Suite"] = "UI Regression"
    if os.getenv("JENKINS_HOME"):
        execution_type = "Jenkins"
    elif os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        execution_type = "GitHub Actions"
    else:
        execution_type = "Local"

    config.stash[metadata_key]["Execution Type"] = execution_type
    config.stash[metadata_key]["Execution Date"] = datetime.now().strftime(
        "%Y-%m-%d"
    )
    config.stash[metadata_key]["Execution Time"] = datetime.now().strftime(
        "%I:%M:%S %p"
    )


@pytest.fixture(scope="function")
def driver(request):
    browser = request.config.getoption("--browser")

    web_driver = create_driver(browser)

    print(f"Browser configured: {browser}")

    try:
        web_driver.maximize_window()
    except Exception:
        pass

    yield web_driver

    web_driver.quit()


def pytest_runtest_makereport(item, call):
    if call.when != "call" or not call.excinfo:
        return

    driver_fixture = item.funcargs.get("driver")

    if driver_fixture is None:
        return

    try:
        filename = (
            f"{item.nodeid.replace('/', '_').replace('::', '_')}_"
            f"{datetime.now():%Y%m%d_%H%M%S}.png"
        )

        path = SCREENSHOT_DIR / filename

        driver_fixture.save_screenshot(str(path))

        print(f"Failure screenshot: {path}")

    except Exception as exc:
        print(f"Unable to capture failure screenshot: {exc}")

def pytest_html_report_title(report):
    report.title = "Selenium Python Pytest Automation Framework"

