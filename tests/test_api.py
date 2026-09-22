# import pytest
# import requests
#
# from config.config import API_BASE_URL
#
#
# @pytest.mark.smoke
# @pytest.mark.regression
# def test_get_post():
#     print(f"API Base URL: {API_BASE_URL}")
#     response = requests.get(f"{API_BASE_URL}/posts/1", timeout=15)
#
#     assert response.status_code == 200, "Expected HTTP status code 200"
#     assert "userId" in response.text, "Response does not contain userId"
#
# import pytest
# import requests
# from config.config import API_BASE_URL
#
# @pytest.mark.smoke
# @pytest.mark.regression
# @pytest.mark.parametrize(
#     "testcase_name",
#     ["TC_API_001_Get_Post"],
# )
# def test_get_post(testcase_name):
#     print(f"===== RUNNING API TEST | {testcase_name} =====")
#     print(f"API Base URL: {API_BASE_URL}")
#
#     response = requests.get(
#         f"{API_BASE_URL}/posts/1",
#         timeout=15
#     )
#
#     assert response.status_code == 200, "Expected HTTP status code 200"


import pytest
import requests

from config.config import API_BASE_URL
from utils.csv_utils import get_api_data

API_DATA = get_api_data("test_data/api_data.csv")


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.parametrize(
    "testcase_name,method,endpoint,expected_status",
    [
        (
            row["testcase_name"],
            row["method"],
            row["endpoint"],
            int(row["expected_status"]),
        )
        for row in API_DATA
    ],
    ids=[row["testcase_name"] for row in API_DATA],
)
def test_api_request(testcase_name, method, endpoint, expected_status):
    print(f"===== RUNNING API TEST | {testcase_name} =====")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Method: {method}")
    print(f"Endpoint: {endpoint}")

    response = requests.request(
        method,
        f"{API_BASE_URL}{endpoint}",
        timeout=15
    )

    assert response.status_code == expected_status, (
        f"Expected HTTP status code {expected_status}, "
        f"but received {response.status_code}"
    )