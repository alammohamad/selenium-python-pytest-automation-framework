import pytest

from pages.login_page import LoginPage
from utils.csv_utils import get_login_data

LOGIN_DATA = get_login_data("test_data/data.csv")


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.parametrize(
    "username,password,expected",
    [
        (row["username"], row["password"], row["expected"])
        for row in LOGIN_DATA
    ],
    ids=[f"{row['expected']}-login" for row in LOGIN_DATA],
)
def test_login(driver, username, password, expected):
    print(f"===== RUNNING LOGIN TEST | Browser: {driver.__class__.__name__} =====")

    login_page = LoginPage(driver)
    login_page.open_website()
    login_page.verify_title()
    login_page.login(username, password)

    if expected.lower() == "success":
        assert login_page.is_login_successful(), (
            "Expected login to succeed, but login was not successful."
        )
    elif expected.lower() == "failure":
        assert login_page.is_login_failed(), (
            "Expected login to fail, but login appears to have succeeded."
        )
    else:
        pytest.fail(f"Invalid expected value: {expected}")
