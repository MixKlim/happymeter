import os
import json
from unittest.mock import patch
from src.streamlit.ui import get_backend_host, predict
from streamlit.testing.v1 import AppTest


def test_backend_host_local() -> None:
    """Test that the backend host is set to localhost when REMOTE is not set."""
    # Clear the environment variable for the test
    os.environ.pop("REMOTE", None)

    assert get_backend_host() == "127.0.0.1"


def test_backend_host_remote() -> None:
    """Test that the backend host is set to backend when REMOTE is set."""
    os.environ["REMOTE"] = "1"  # Simulate remote deployment

    assert get_backend_host() == "backend"

    # Clean up
    os.environ.pop("REMOTE", None)


def test_app_run() -> None:
    """Test that the Streamlit app runs without errors."""
    at = AppTest.from_file("src/streamlit/ui.py").run()
    assert not at.exception


# Test cases
def test_prediction_happy() -> None:
    """Test prediction success scenario."""
    test_data = {"city_services": 4, "housing_costs": 5}
    mock_response = {"prediction": True, "probability": 0.95}

    with patch("requests.post") as mock_post:
        mock_post.return_value.text = json.dumps(mock_response)

        # Simulate button click
        predict(test_data, predict_button=True)

        mock_post.assert_called_once_with(
            f"http://{get_backend_host()}:8080/predict", json=test_data
        )

        # Capture the success message
        with patch("streamlit.success") as mock_success:
            predict(test_data, predict_button=True)
            mock_success.assert_called_once_with(
                "Good news - you are happy! We're 95% sure :grinning:"
            )


def test_prediction_unhappy() -> None:
    """Test prediction failure scenario."""
    test_data = {"city_services": 2, "housing_costs": 1}
    mock_response = {"prediction": False, "probability": 0.60}

    with patch("requests.post") as mock_post:
        mock_post.return_value.text = json.dumps(mock_response)

        # Simulate button click
        predict(test_data, predict_button=True)

        mock_post.assert_called_once_with(
            f"http://{get_backend_host()}:8080/predict", json=test_data
        )

        # Capture the error message
        with patch("streamlit.error") as mock_error:
            predict(test_data, predict_button=True)
            mock_error.assert_called_once_with(
                "Oh no, you seem to be unhappy! At least for 60% :worried:"
            )


def test_predict_button_not_pressed() -> None:
    """Test that nothing happens if the predict button is not pressed."""
    test_data = {"city_services": 3, "housing_costs": 4}

    with patch("requests.post") as mock_post:
        predict(test_data, False)

        # Check that requests.post was not called
        mock_post.assert_not_called()
