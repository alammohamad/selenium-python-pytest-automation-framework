import os

DEFAULT_ENV = "qa"

ENVIRONMENT = os.getenv("TEST_ENV", DEFAULT_ENV).lower()

if ENVIRONMENT not in {"qa", "prod"}:
    raise ValueError(f"Unsupported TEST_ENV: {ENVIRONMENT}. Use qa or prod.")

# The Java project currently uses the same application URL for QA and PROD.
# Keep these separate so they can be changed later without changing tests.
ENV_URLS = {
    "qa": "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login",
    "prod": "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login",
}

ORANGEHRM_URL = ENV_URLS[ENVIRONMENT]
API_BASE_URL = "https://jsonplaceholder.typicode.com"
