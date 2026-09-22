import json
import os
from datetime import datetime
from pathlib import Path

import pytest
from pytest_metadata.plugin import metadata_key

from utils.driver_factory import create_driver
from utils.slack_reporter import send_slack_message
from utils.manager_report import generate_manager_report
from utils.email_reporter import send_email


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


def pytest_sessionfinish(session, exitstatus):
    terminalreporter = session.config.pluginmanager.get_plugin("terminalreporter")

    if terminalreporter is None:
        print("Slack summary skipped: terminal reporter not available.")
        return

    passed = 0
    failed = 0
    skipped = 0

    test_cases = []
    json_test_cases = []

    for report in terminalreporter.stats.get("passed", []):
        if report.when == "call":
            passed += 1

            test_case_name = report.nodeid.split("[")[-1].rstrip("]")

            test_cases.append(f"✅ {test_case_name}")

            json_test_cases.append(
                {
                    "name": test_case_name,
                    "status": "PASSED",
                }
            )

    for report in terminalreporter.stats.get("failed", []):
        if report.when == "call":
            failed += 1

            test_case_name = report.nodeid.split("[")[-1].rstrip("]")

            test_cases.append(f"❌ {test_case_name}")

            json_test_cases.append(
                {
                    "name": test_case_name,
                    "status": "FAILED",
                }
            )

    for report in terminalreporter.stats.get("skipped", []):
        if report.when == "call":
            skipped += 1

            test_case_name = report.nodeid.split("[")[-1].rstrip("]")

            test_cases.append(f"⏭️ {test_case_name}")

            json_test_cases.append(
                {
                    "name": test_case_name,
                    "status": "SKIPPED",
                }
            )

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

    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%I:%M:%S %p")

    # Create data for the manager summary report.
    results_data = {
        "project": "Selenium Python Pytest Automation Framework",
        "environment": environment.upper(),
        "browser": browser.capitalize(),
        "execution_type": execution_type,
        "date": date,
        "time": time,
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "overall": overall,
        "test_cases": json_test_cases,
    }

    results_file = REPORT_DIR / "test-results.json"

    try:
        with results_file.open("w", encoding="utf-8") as file:
            json.dump(results_data, file, indent=4)

        print(f"Test results JSON created: {results_file}")

    except Exception as exc:
        print(f"Unable to create test results JSON: {exc}")

    try:
        generate_manager_report()
    except Exception as exc:
        print(f"Unable to create manager report: {exc}")

    # Send email notification.
    try:
        send_email()
    except Exception as exc:
        print(f"Unable to send email notification: {exc}")

    test_case_text = "\n".join(test_cases)

    message = (
        f"Selenium Python Pytest — {execution_type} Test Summary\n\n"
        f"Environment: {environment.upper()}\n"
        f"Browser: {browser.capitalize()}\n"
        f"Execution: {execution_type}\n"
        f"Date: {date}\n"
        f"Time: {time}\n\n"
        f"Test Cases:\n"
        f"{test_case_text}\n\n"
        f"Total: {total}\n"
        f"Passed: {passed}\n"
        f"Failed: {failed}\n"
        f"Skipped: {skipped}\n\n"
        f"Overall: {overall}\n\n"
        f"Manager Report: http://localhost:8000/manager-summary.html"
    )

    send_slack_message(message)


# import json
# import os
# from datetime import datetime
# from pathlib import Path
#
# import pytest
# from pytest_metadata.plugin import metadata_key
#
# from utils.driver_factory import create_driver
# from utils.slack_reporter import send_slack_message
# from utils.manager_report import generate_manager_report
#
#
# REPORT_DIR = Path("reports")
# SCREENSHOT_DIR = REPORT_DIR / "screenshots"
#
#
# def pytest_addoption(parser):
#     parser.addoption(
#         "--browser",
#         action="store",
#         default="chrome",
#         choices=["chrome", "firefox"],
#         help="Browser to use: chrome or firefox",
#     )
#     parser.addoption(
#         "--env",
#         action="store",
#         default=None,
#         choices=["qa", "prod"],
#         help="Test environment: qa or prod",
#     )
#
#
# def pytest_configure(config):
#     REPORT_DIR.mkdir(exist_ok=True)
#     SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
#
#     # Set TEST_ENV before test collection.
#     cli_env = config.getoption("--env")
#     if cli_env:
#         os.environ["TEST_ENV"] = cli_env
#
#     # Information displayed in the HTML report.
#     browser = config.getoption("--browser")
#     environment = cli_env or "qa"
#
#     config.stash[metadata_key]["Project"] = (
#         "Selenium Python Pytest Automation Framework"
#     )
#     config.stash[metadata_key]["Environment"] = environment.upper()
#     config.stash[metadata_key]["Browser"] = browser.capitalize()
#     config.stash[metadata_key]["Test Suite"] = "UI Regression"
#
#     if os.getenv("JENKINS_HOME"):
#         execution_type = "Jenkins"
#     elif os.getenv("GITHUB_ACTIONS", "").lower() == "true":
#         execution_type = "GitHub Actions"
#     else:
#         execution_type = "Local"
#
#     config.stash[metadata_key]["Execution Type"] = execution_type
#     config.stash[metadata_key]["Execution Date"] = datetime.now().strftime(
#         "%Y-%m-%d"
#     )
#     config.stash[metadata_key]["Execution Time"] = datetime.now().strftime(
#         "%I:%M:%S %p"
#     )
#
#
# @pytest.fixture(scope="function")
# def driver(request):
#     browser = request.config.getoption("--browser")
#
#     web_driver = create_driver(browser)
#
#     print(f"Browser configured: {browser}")
#
#     try:
#         web_driver.maximize_window()
#     except Exception:
#         pass
#
#     yield web_driver
#
#     web_driver.quit()
#
#
# def pytest_runtest_makereport(item, call):
#     if call.when != "call" or not call.excinfo:
#         return
#
#     driver_fixture = item.funcargs.get("driver")
#
#     if driver_fixture is None:
#         return
#
#     try:
#         filename = (
#             f"{item.nodeid.replace('/', '_').replace('::', '_')}_"
#             f"{datetime.now():%Y%m%d_%H%M%S}.png"
#         )
#
#         path = SCREENSHOT_DIR / filename
#
#         driver_fixture.save_screenshot(str(path))
#
#         print(f"Failure screenshot: {path}")
#
#     except Exception as exc:
#         print(f"Unable to capture failure screenshot: {exc}")
#
#
# def pytest_html_report_title(report):
#     report.title = "Selenium Python Pytest Automation Framework"
#
#
# def pytest_sessionfinish(session, exitstatus):
#     terminalreporter = session.config.pluginmanager.get_plugin("terminalreporter")
#
#     if terminalreporter is None:
#         print("Slack summary skipped: terminal reporter not available.")
#         return
#
#     passed = 0
#     failed = 0
#     skipped = 0
#
#     test_cases = []
#     json_test_cases = []
#
#     for report in terminalreporter.stats.get("passed", []):
#         if report.when == "call":
#             passed += 1
#
#             test_case_name = report.nodeid.split("[")[-1].rstrip("]")
#
#             test_cases.append(f"✅ {test_case_name}")
#
#             json_test_cases.append(
#                 {
#                     "name": test_case_name,
#                     "status": "PASSED",
#                 }
#             )
#
#     for report in terminalreporter.stats.get("failed", []):
#         if report.when == "call":
#             failed += 1
#
#             test_case_name = report.nodeid.split("[")[-1].rstrip("]")
#
#             test_cases.append(f"❌ {test_case_name}")
#
#             json_test_cases.append(
#                 {
#                     "name": test_case_name,
#                     "status": "FAILED",
#                 }
#             )
#
#     for report in terminalreporter.stats.get("skipped", []):
#         if report.when == "call":
#             skipped += 1
#
#             test_case_name = report.nodeid.split("[")[-1].rstrip("]")
#
#             test_cases.append(f"⏭️ {test_case_name}")
#
#             json_test_cases.append(
#                 {
#                     "name": test_case_name,
#                     "status": "SKIPPED",
#                 }
#             )
#
#     total = passed + failed + skipped
#
#     environment = session.config.getoption("--env") or "qa"
#     browser = session.config.getoption("--browser") or "chrome"
#
#     if os.getenv("JENKINS_HOME"):
#         execution_type = "Jenkins"
#     elif os.getenv("GITHUB_ACTIONS", "").lower() == "true":
#         execution_type = "GitHub Actions"
#     else:
#         execution_type = "Local"
#
#     if exitstatus == 0:
#         overall = "PASSED"
#     else:
#         overall = "FAILED"
#
#     date = datetime.now().strftime("%Y-%m-%d")
#     time = datetime.now().strftime("%I:%M:%S %p")
#
#     # Create data for the future manager summary report.
#     results_data = {
#         "project": "Selenium Python Pytest Automation Framework",
#         "environment": environment.upper(),
#         "browser": browser.capitalize(),
#         "execution_type": execution_type,
#         "date": date,
#         "time": time,
#         "total": total,
#         "passed": passed,
#         "failed": failed,
#         "skipped": skipped,
#         "overall": overall,
#         "test_cases": json_test_cases,
#     }
#
#     results_file = REPORT_DIR / "test-results.json"
#
#     try:
#         with results_file.open("w", encoding="utf-8") as file:
#             json.dump(results_data, file, indent=4)
#
#         print(f"Test results JSON created: {results_file}")
#
#     except Exception as exc:
#         print(f"Unable to create test results JSON: {exc}")
#
#     try:
#         generate_manager_report()
#     except Exception as exc:
#         print(f"Unable to create manager report: {exc}")
#
#     test_case_text = "\n".join(test_cases)
#
#     message = (
#         f"Selenium Python Pytest — {execution_type} Test Summary\n\n"
#         f"Environment: {environment.upper()}\n"
#         f"Browser: {browser.capitalize()}\n"
#         f"Execution: {execution_type}\n"
#         f"Date: {date}\n"
#         f"Time: {time}\n\n"
#         f"Test Cases:\n"
#         f"{test_case_text}\n\n"
#         f"Total: {total}\n"
#         f"Passed: {passed}\n"
#         f"Failed: {failed}\n"
#         f"Skipped: {skipped}\n\n"
#         f"Overall: {overall}\n\n"
#         f"Manager Report: http://localhost:8000/manager-summary.html"
#     )
#
#     send_slack_message(message)

    # slack report used to show tests/test_api.py::test_api_request[TC_API_001_Get_Post],
    # this code test_case_name = report.nodeid.split("[")[-1].rstrip("]") with return as "TC_API_001_Get_Post"


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
#
# def pytest_sessionfinish(session, exitstatus):
#     terminalreporter = session.config.pluginmanager.get_plugin("terminalreporter")
#
#     if terminalreporter is None:
#         print("Slack summary skipped: terminal reporter not available.")
#         return
#
#     passed = 0
#     failed = 0
#     skipped = 0
#
#     for report in terminalreporter.stats.get("passed", []):
#         passed += 1
#
#     for report in terminalreporter.stats.get("failed", []):
#         failed += 1
#
#     for report in terminalreporter.stats.get("skipped", []):
#         skipped += 1
#
#     total = passed + failed + skipped
#
#     environment = session.config.getoption("--env") or "qa"
#     browser = session.config.getoption("--browser") or "chrome"
#     if os.getenv("JENKINS_HOME"):
#         execution_type = "Jenkins"
#     elif os.getenv("GITHUB_ACTIONS", "").lower() == "true":
#         execution_type = "GitHub Actions"
#     else:
#         execution_type = "Local"
#
#     if exitstatus == 0:
#         overall = "PASSED"
#     else:
#         overall = "FAILED"
#
#     date = datetime.now().strftime("%Y-%m-%d")
#     time = datetime.now().strftime("%I:%M:%S %p")
#     message = (
#         f"Selenium Python Pytest — {execution_type} Test Summary\n\n"
#         f"Environment: {environment.upper()}\n"
#         f"Browser: {browser.capitalize()}\n"
#         f"Execution: {execution_type}\n"
#         f"Date: {date}\n"
#         f"Time: {time}\n\n"
#         f"Total: {total}\n"
#         f"Passed: {passed}\n"
#         f"Failed: {failed}\n"
#         f"Skipped: {skipped}\n\n"
#         f"Overall: {overall}"
#     )
#
#     send_slack_message(message)

# def pytest_sessionfinish(session, exitstatus):
#     terminalreporter = session.config.pluginmanager.get_plugin("terminalreporter")
#
#     if terminalreporter is None:
#         print("Slack summary skipped: terminal reporter not available.")
#         return
#
#     passed = 0
#     failed = 0
#     skipped = 0
#
#     test_cases = []
#
#     for report in terminalreporter.stats.get("passed", []):
#         if report.when == "call":
#             passed += 1
#             test_cases.append(f"✅ {report.nodeid}")
#
#     for report in terminalreporter.stats.get("failed", []):
#         if report.when == "call":
#             failed += 1
#             test_cases.append(f"❌ {report.nodeid}")
#
#     for report in terminalreporter.stats.get("skipped", []):
#         if report.when == "call":
#             skipped += 1
#             test_cases.append(f"⏭️ {report.nodeid}")
#
#     total = passed + failed + skipped
#
#     environment = session.config.getoption("--env") or "qa"
#     browser = session.config.getoption("--browser") or "chrome"
#
#     if os.getenv("JENKINS_HOME"):
#         execution_type = "Jenkins"
#     elif os.getenv("GITHUB_ACTIONS", "").lower() == "true":
#         execution_type = "GitHub Actions"
#     else:
#         execution_type = "Local"
#
#     if exitstatus == 0:
#         overall = "PASSED"
#     else:
#         overall = "FAILED"
#
#     date = datetime.now().strftime("%Y-%m-%d")
#     time = datetime.now().strftime("%I:%M:%S %p")
#
#     test_case_text = "\n".join(test_cases)
#
#     message = (
#         f"Selenium Python Pytest — {execution_type} Test Summary\n\n"
#         f"Environment: {environment.upper()}\n"
#         f"Browser: {browser.capitalize()}\n"
#         f"Execution: {execution_type}\n"
#         f"Date: {date}\n"
#         f"Time: {time}\n\n"
#         f"Test Cases:\n"
#         f"{test_case_text}\n\n"
#         f"Total: {total}\n"
#         f"Passed: {passed}\n"
#         f"Failed: {failed}\n"
#         f"Skipped: {skipped}\n\n"
#         f"Overall: {overall}"
#     )
#
#     send_slack_message(message)
