# Selenium Python + Pytest Automation Framework

This project is a Python/Pytest equivalent of the Selenium Java + TestNG framework used as its source blueprint.

## Stack

- Python
- Selenium WebDriver
- Pytest
- Pytest HTML
- Requests for API testing
- Page Object Model
- CSV-driven test data
- Smoke and regression markers
- QA / PROD environment selection
- Chrome and Firefox
- GitHub Actions

## Project structure

```text
selenium-python-pytest-automation-framework/
├── pages/
│   └── login_page.py
├── tests/
│   ├── test_ui.py
│   └── test_api.py
├── utils/
│   ├── driver_factory.py
│   └── csv_utils.py
├── config/
│   └── config.py
├── test_data/
│   └── data.csv
├── reports/
├── .github/workflows/qa-tests.yml
├── conftest.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Windows setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run tests

### Chrome, all smoke + regression tests
```powershell
pytest --browser chrome --env qa
```

### Firefox
```powershell
pytest --browser firefox --env qa
```

### QA regression only
```powershell
pytest -m regression --browser chrome --env qa
```

### PROD smoke only
```powershell
pytest -m smoke --browser chrome --env prod
```

### API only
```powershell
pytest tests/test_api.py
```

### HTML report
```powershell
pytest --browser chrome --env qa --html=reports/pytest-report.html --self-contained-html
```

## Important environment note

The source Java project currently uses the same OrangeHRM URL for QA and PROD. The Python project preserves that behavior while keeping QA and PROD as separate configuration entries so real environment URLs can be added later without changing test code.

## Java → Pytest mapping

| Java/TestNG | Python/Pytest |
|---|---|
| `@BeforeMethod` | `@pytest.fixture` |
| `@AfterMethod` | fixture teardown after `yield` |
| `@DataProvider` | `@pytest.mark.parametrize` |
| TestNG groups | `@pytest.mark.smoke` / `@pytest.mark.regression` |
| `Assert.assertTrue` | Python `assert` |
| `WebDriverFactory` | `utils/driver_factory.py` |
| `LoginPage` | `pages/login_page.py` |
| `CSVUtils` | `utils/csv_utils.py` |
| TestNG listener | Pytest hooks/fixtures |
| Surefire HTML reports | `pytest-html` |
| GitHub Slack notification test |
