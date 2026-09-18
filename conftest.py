import os
from datetime import datetime
from pathlib import Path

import pytest
from pytest_metadata.plugin import metadata_key

from utils.driver_factory import create_driver
from utils.slack_reporter import send_slack_message
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

    # def pytest_terminal_summary(terminalreporter, exitstatus, config):
    #     print("SLACK SUMMARY HOOK STARTED")
    #     passed = len(terminalreporter.stats.get("passed", []))
    #     failed = len(terminalreporter.stats.get("failed", []))
    #     skipped = len(terminalreporter.stats.get("skipped", []))
    #
    #     total = passed + failed + skipped
    #
    #     environment = config.getoption("--env") or "qa"
    #     browser = config.getoption("--browser") or "chrome"
    #
    #     if exitstatus == 0:
    #         overall = "PASSED"
    #     else:
    #         overall = "FAILED"
    #
    #     message = (
    #         "Selenium Python Pytest — Local Test Summary\n\n"
    #         f"Environment: {environment.upper()}\n"
    #         f"Browser: {browser.capitalize()}\n"
    #         "Execution: Local\n\n"
    #         f"Total: {total}\n"
    #         f"Passed: {passed}\n"
    #         f"Failed: {failed}\n"
    #         f"Skipped: {skipped}\n\n"
    #         f"Overall: {overall}"
    #     )
    #
    #     send_slack_message(message)
def pytest_sessionfinish(session, exitstatus):
    terminalreporter = session.config.pluginmanager.get_plugin("terminalreporter")

    if terminalreporter is None:
        print("Slack summary skipped: terminal reporter not available.")
        return

    passed = 0
    failed = 0
    skipped = 0

    for report in terminalreporter.stats.get("passed", []):
        passed += 1

    for report in terminalreporter.stats.get("failed", []):
        failed += 1

    for report in terminalreporter.stats.get("skipped", []):
        skipped += 1

    total = passed + failed + skipped

    environment = session.config.getoption("--env") or "qa"
    browser = session.config.getoption("--browser") or "chrome"
    if os.getenv("JENKINS_HOME"):
        execution_type = "Jenkins"
    elif os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        execution_type = "GitHub Actions"
    else:
        execution_type = "Local"

    if exitstatus == 0:
        overall = "PASSED"
    else:
        overall = "FAILED"

    message = (
        f"Selenium Python Pytest — {execution_type} Test Summary\n\n"
        f"Environment: {environment.upper()}\n"
        f"Browser: {browser.capitalize()}\n"
        f"Execution: {execution_type}\n\n"
        f"Total: {total}\n"
        f"Passed: {passed}\n"
        f"Failed: {failed}\n"
        f"Skipped: {skipped}\n\n"
        f"Overall: {overall}"
    )

    send_slack_message(message)

