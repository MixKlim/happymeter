import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from typing import Dict, Generator
from src.app.main import app


client = TestClient(app=app)


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


def test_root() -> None:
    """Tests the root endpoint.

    Asserts:
        - The response status code is 200.
    """
    response = client.get("/")
    assert response.status_code == 200


# Test cases
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
    assert response.status_code == 200
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
    assert response.status_code == 500
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
    assert response.status_code == 422
