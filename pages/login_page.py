from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.config import ORANGEHRM_URL


class LoginPage:
    USERNAME = (By.XPATH, "//input[@name='username']")
    PASSWORD = (By.XPATH, "//input[@name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[@type='submit']")
    INVALID_LOGIN_MESSAGE = (By.XPATH, "//p[contains(@class,'oxd-alert-content-text')]")

    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open_website(self):
        self.driver.get(ORANGEHRM_URL)

    def verify_title(self):
        assert "OrangeHRM" in self.driver.title, "Title does not contain OrangeHRM"

    def enter_username(self, username):
        element = self.wait.until(EC.visibility_of_element_located(self.USERNAME))
        element.send_keys(username)

    def enter_password(self, password):
        element = self.wait.until(EC.visibility_of_element_located(self.PASSWORD))
        element.send_keys(password)

    def click_login(self):
        element = self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON))
        element.click()

    def login(self, username, password):
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def is_login_successful(self):
        try:
            self.wait.until(EC.url_contains("/dashboard/index"))
            print(f"Login successful - Dashboard URL detected: {self.driver.current_url}")
            return True
        except Exception as exc:
            print("===== LOGIN SUCCESS CHECK FAILED =====")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page Title: {self.driver.title}")
            print(f"Exception: {type(exc).__name__}")
            print(f"Exception Message: {exc}")
            print("======================================")
            return False

    def is_login_failed(self):
        try:
            message = self.wait.until(EC.visibility_of_element_located(self.INVALID_LOGIN_MESSAGE))
            return message.is_displayed()
        except Exception:
            return False
