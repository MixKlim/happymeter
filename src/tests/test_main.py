import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from typing import Dict, Generator
from src.app.main import app, get_database_url
from src.app.database import HappyPrediction


client = TestClient(app=app)


@pytest.fixture
def mock_env() -> Generator[None, None, None]:
    """Fixture to mock environment variables for tests."""
    with patch.dict(os.environ, {}, clear=True):
        yield


@pytest.fixture
def mock_model() -> Generator[AsyncMock, None, None]:
    """Fixture to mock the model object.

    Yields:
        AsyncMock: A mock object simulating the model with an async `predict_happiness` method.
    """
    with patch("src.app.main.model", new_callable=AsyncMock) as mock_model:
        # Ensure predict_happiness is an async method
        mock_model.predict_happiness = AsyncMock()
        yield mock_model


@pytest.fixture
def mock_read_from_db() -> Generator[AsyncMock, None, None]:
    """Fixture to mock read_from_db for a successful database read.

    This fixture mocks the `read_from_db` function to return a sample list
    of rows representing database content for use in testing the /measurements
    endpoint.

    Yields:
        AsyncMock: Mocked `read_from_db` function.
    """
    with patch(
        "src.app.main.read_from_db",
        return_value=[
            HappyPrediction(
                city_services=5,
                housing_costs=4,
                school_quality=3,
                local_policies=2,
                maintenance=1,
                social_events=4,
                prediction=85,
                probability=0.92,
            )
        ],
    ) as mock:
        yield mock


# Test cases
@pytest.mark.parametrize(
    "remote_env, expected_url",
    [
        (
            "",  # SQLite when REMOTE is not set
            f"sqlite:///{Path(__file__).resolve().parent.parent.absolute() / 'database' / 'predictions.db'}",
        ),
        (
            "true",  # PostgreSQL when REMOTE is set
            "postgresql://test_user:test_password@postgres/test_db",
        ),
    ],
)
def test_get_database_url(mock_env: None, remote_env: str, expected_url: str) -> None:
    """
    Parametrized test for getting the correct database URL based on the REMOTE environment variable.

    Args:
        mock_env (None): Mocked environment.
        remote_env (str): Value to set for the REMOTE environment variable.
        expected_url (str): The expected URL to be returned by get_database_url.
    """
    # Mock environment variables based on the parameterized test case
    if remote_env == "":
        os.environ["REMOTE"] = ""
    else:
        os.environ["REMOTE"] = "true"
        os.environ["POSTGRES_USER"] = "test_user"
        os.environ["POSTGRES_PASSWORD"] = "test_password"
        os.environ["POSTGRES_DB"] = "test_db"

    # Call the function
    result = get_database_url()

    # Assert that the returned URL matches the expected URL
    assert result == expected_url, f"Expected {expected_url}, but got {result}"


def test_root() -> None:
    """Tests the root endpoint.

    Asserts:
        - The response status code is 200.
    """
    response = client.get("/")
    assert (
        response.status_code == 200
    ), "Expected status code 200 for a successful response"


def test_predict_happiness_success(mock_model: AsyncMock) -> None:
    """Tests that the prediction endpoint returns the expected response on success.

    Args:
        mock_model (AsyncMock): The mocked model object with `predict_happiness`.

    Asserts:
        - The response status code is 200.
        - The response JSON matches the expected prediction and probability.
        - The `predict_happiness` method was called with the correct arguments.
    """
    # Arrange
    mock_model.predict_happiness.return_value = (1, 0.85)
    test_data = {
        "city_services": 4,
        "housing_costs": 3,
        "school_quality": 5,
        "local_policies": 4,
        "maintenance": 3,
        "social_events": 4,
    }

    # Act
    response = client.post("/predict", json=test_data)

    # Assert
    assert (
        response.status_code == 200
    ), "Expected status code 200 for a successful response"
    assert response.json() == {"prediction": 1, "probability": 0.85}
    mock_model.predict_happiness.assert_awaited_once_with(
        test_data["city_services"],
        test_data["housing_costs"],
        test_data["school_quality"],
        test_data["local_policies"],
        test_data["maintenance"],
        test_data["social_events"],
    )


def test_predict_happiness_unexpected_error(mock_model: AsyncMock) -> None:
    """Tests that the prediction endpoint handles unexpected errors gracefully.

    Args:
        mock_model (AsyncMock): The mocked model object with `predict_happiness`.

    Asserts:
        - The response status code is 500.
        - The response JSON contains the correct error detail.
    """
    # Arrange
    mock_model.predict_happiness.side_effect = Exception("Unexpected error")
    test_data: Dict[str, int] = {}

    # Act
    response = client.post("/predict", json=test_data)

    # Assert
    assert (
        response.status_code == 500
    ), "Expected status code 500 for a failure response"
    assert response.json() == {"detail": "ERR_UNEXPECTED"}


def test_predict_happiness_invalid_input() -> None:
    """Tests that the prediction endpoint returns a 422 error on invalid input.

    Asserts:
        - The response status code is 422.
    """
    # Arrange
    invalid_data = {
        "city_services": "invalid"
    }  # Missing required fields and invalid data

    # Act
    response = client.post("/predict", json=invalid_data)

    # Assert
    assert response.status_code == 422, "Expected status code 422 for an invalid input"


@patch("src.app.main.logger")
def test_read_measurements(
    mock_logger: AsyncMock, mock_read_from_db: AsyncMock
) -> None:
    """
    Tests the `read_measurements` endpoint.

    Args:
        mock_logger (AsyncMock): Mocked logger.
        mock_read_from_db (MagicMock): Mock for the read_from_db function.
    """

    # Act
    response = client.get("/measurements")

    # Assert
    assert (
        response.status_code == 200
    ), "Expected status code 200 for a successful response"

    html_content = response.text

    # Verify HTML content
    assert (
        "<h1>Saved Measurements</h1>" in html_content
    ), "HTML content should include the header"
    assert "<td>1</td>" in html_content, "HTML content should include ID"
    assert "<td>5</td>" in html_content, "HTML content should include data"
    assert "<td>0.92</td>" in html_content, "HTML content should include probability"

    # Verify db mock was called
    mock_read_from_db.assert_called_once()

    # Verify the logger logs a success message
    mock_logger.info.assert_called_once_with("Measurement rows rendered successfully!")
