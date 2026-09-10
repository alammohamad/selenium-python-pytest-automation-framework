import pytest
import requests

from config.config import API_BASE_URL


@pytest.mark.smoke
@pytest.mark.regression
def test_get_post():
    print(f"API Base URL: {API_BASE_URL}")
    response = requests.get(f"{API_BASE_URL}/posts/1", timeout=15)

    assert response.status_code == 200, "Expected HTTP status code 200"
    assert "userId" in response.text, "Response does not contain userId"
