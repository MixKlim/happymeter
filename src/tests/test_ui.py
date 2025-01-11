import os
from typing import Any, Dict, Generator, Optional, Tuple
from unittest.mock import MagicMock, patch

import pytest
import requests

import streamlit as st
from src.streamlit.ui import get_backend_host, predict, rating_section
from streamlit.testing.v1 import AppTest


@pytest.fixture(scope="function")
def mock_st() -> Generator[Tuple[MagicMock, MagicMock], None, None]:
    """Provides mocked Streamlit success and error methods.

    Yields:
        Tuple[MagicMock, MagicMock]: Mocked `st.success` and `st.error` methods.
    """
    with (
        patch.object(st, "success") as mock_success,
        patch.object(st, "error") as mock_error,
    ):
        yield mock_success, mock_error


def setup_mock_response(
    mock_post: MagicMock, prediction: bool, probability: float
) -> None:
    """Helper function to set up the mocked response for requests.post.

    Args:
        mock_post (MagicMock): The mocked `requests.post` method.
        prediction (bool): The prediction value to mock.
        probability (float): The probability value to mock.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "prediction": prediction,
        "probability": probability,
    }
    mock_post.return_value = mock_response


# Test cases
def test_app_run() -> None:
    """Tests that the Streamlit application runs without exceptions."""
    at = AppTest.from_file("src/streamlit/ui.py").run()
    assert not at.exception


@pytest.mark.parametrize(
    "env_var_value, expected_output",
    [
        ("backend:5000", "backend:5000"),
        (None, "127.0.0.1:8080"),
    ],
)
def test_get_backend_host(env_var_value: Optional[str], expected_output: str) -> None:
    """
    Test the `get_backend_host` function with various BACKEND_HOST environment variable settings.

    Args:
        env_var_value (Optional[str]): The value to set for the BACKEND_HOST environment variable.
        expected_output (str): The expected output of the function.
    """
    # Backup the current environment variables
    original_env = dict(os.environ)

    # Clear BACKEND_HOST and set the new value if provided
    if env_var_value is not None:
        os.environ["BACKEND_HOST"] = env_var_value
    else:
        os.environ.pop("BACKEND_HOST", None)  # Remove BACKEND_HOST if set

    try:
        # Call the function and assert the result
        assert get_backend_host() == expected_output
    finally:
        # Restore the original environment variables
        os.environ.clear()
        os.environ.update(original_env)


@patch("requests.post")
@pytest.mark.parametrize(
    "data, prediction, probability, expected_message, is_success",
    [
        (
            {"city_services": 4, "housing_costs": 5},
            True,
            0.95,
            "Good news - you are happy! We're 95% sure 😃",
            True,
        ),
        (
            {"city_services": 2, "housing_costs": 1},
            False,
            0.6,
            "Oh no, you seem to be unhappy! At least for 60% 😟",
            False,
        ),
        ({}, True, 0.9, "Good news - you are happy! We're 90% sure 😃", True),
    ],
)
def test_predict(
    mock_post: MagicMock,
    mock_st: Tuple[MagicMock, MagicMock],
    data: Dict[str, Any],
    prediction: bool,
    probability: float,
    expected_message: str,
    is_success: bool,
) -> None:
    """Tests the `predict` function with various scenarios.

    Args:
        mock_post (MagicMock): Mocked `requests.post` method.
        mock_st (Tuple[MagicMock, MagicMock]): Mocked Streamlit methods.
        data (Dict[str, Any]): Input data for the `predict` function.
        prediction (bool): The mocked prediction value.
        probability (float): The mocked probability value.
        expected_message (str): The expected Streamlit message.
        is_success (bool): Whether the message is for success or error.
    """
    setup_mock_response(mock_post, prediction, probability)

    predict(backend_host="backend_host", data=data, predict_button=True)

    if is_success:
        mock_st[0].assert_called_once_with(expected_message)
    else:
        mock_st[1].assert_called_once_with(expected_message)


@patch("requests.post")
def test_predict_http_fallback(
    mock_post: MagicMock, mock_st: Tuple[MagicMock, MagicMock]
) -> None:
    """Tests the predict function when the HTTPS request fails and the fallback to HTTP succeeds.

    Args:
        mock_st: The mocked Streamlit success and error methods.
        mock_post: The mocked requests.post method.
    """

    # Simulate SSL error for the first call (HTTPS request)
    # The second call will return a mocked valid response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"prediction": True, "probability": 0.75}

    # Set the side effect to simulate the SSL error on HTTPS, then return the mocked response for the fallback HTTP
    mock_post.side_effect = [
        requests.exceptions.SSLError("SSL Error"),  # Simulate SSL error on HTTPS
        mock_response,  # Return a valid mocked response for the fallback HTTP request
    ]

    # Run the predict function
    data = {"key": "value"}
    predict(backend_host="backend_host", data=data, predict_button=True)

    # Assert that the success method was called with the correct message
    mock_st[0].assert_called_once_with("Good news - you are happy! We're 75% sure 😃")


@patch("requests.post")
def test_predict_failure(
    mock_post: MagicMock, mock_st: Tuple[MagicMock, MagicMock]
) -> None:
    """Tests the predict function when both HTTPS and HTTP requests fail.

    Args:
        mock_st: The mocked Streamlit success and error methods.
        mock_post: The mocked requests.post method.
    """
    mock_post.side_effect = [
        requests.exceptions.SSLError("SSL Error"),  # Simulate SSL error on HTTPS
        requests.exceptions.ConnectionError(
            "Connection Error"
        ),  # Simulate connection error on HTTP
    ]

    # Run the predict function
    data = {"key": "value"}
    predict(backend_host="backend_host", data=data, predict_button=True)

    # Assert that the error method was called with the correct message
    mock_st[1].assert_called_once_with(
        "Failed to connect to the prediction service: Connection Error"
    )


@patch("requests.post")
def test_predict_no_button_pressed(
    mock_post: MagicMock, mock_st: Tuple[MagicMock, MagicMock]
) -> None:
    """Tests the `predict` function when the prediction button is not pressed.

    Args:
        mock_post (MagicMock): Mocked `requests.post` method.
        mock_st (Tuple[MagicMock, MagicMock]): Mocked Streamlit methods.
    """
    data = {"key": "value"}
    predict(backend_host="test", data=data, predict_button=False)
    mock_st[0].assert_not_called()
    mock_st[1].assert_not_called()


def test_rating_section() -> None:
    """Tests the `rating_section` function for correct Streamlit component behavior."""
    with (
        patch("streamlit.columns") as mock_columns,
        patch("streamlit.write") as mock_write,
        patch("src.streamlit.ui.st_star_rating") as mock_star_rating,
    ):
        mock_col_q = MagicMock()
        mock_col_s = MagicMock()
        mock_columns.return_value = (mock_col_q, mock_col_s)
        mock_star_rating.return_value = 4

        prompt = "How would you rate this?"
        key = "test_key"
        text_font_size = 16
        star_rating_size = 20

        result = rating_section(prompt, key, text_font_size, star_rating_size)

        mock_columns.assert_called_once_with([3, 1])
        mock_write.assert_called_once_with(
            f"<p style='text-align: left; font-size: {text_font_size}px;'><b>{prompt}</b></p>",
            unsafe_allow_html=True,
        )
        mock_star_rating.assert_called_once_with(
            label=None,
            size=star_rating_size,
            maxValue=5,
            defaultValue=3,
            key=key,
            dark_theme=True,
        )

        assert result == 4
