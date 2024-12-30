import os
import pytest
import requests
from unittest.mock import patch, MagicMock
from typing import Generator, Tuple
import streamlit as st
from src.streamlit.ui import get_backend_host, rating_section, predict
from streamlit.testing.v1 import AppTest


def test_app_run() -> None:
    """Test that the Streamlit app runs without errors.

    Ensures that the Streamlit app defined in `src/streamlit/ui.py` runs without raising any exceptions.
    Additionally, it could verify if the app outputs expected content or components.
    """
    at = AppTest.from_file("src/streamlit/ui.py").run()
    assert not at.exception


@pytest.mark.parametrize(
    "remote_env, expected_host",
    [
        ("", "127.0.0.1"),
        ("True", "backend"),
        ("AnotherValue", "backend"),
    ],
)
def test_get_backend_host(remote_env: str, expected_host: str) -> None:
    """Test the `get_backend_host` function with different environment variable settings.

    Args:
        remote_env (str): The value of the REMOTE environment variable.
        expected_host (str): The expected result of the `get_backend_host` function.

    Ensures that the function returns the correct backend host based on the environment variable.
    """
    with patch.dict(os.environ, {"REMOTE": remote_env}):
        assert get_backend_host() == expected_host


@pytest.fixture(scope="function")
def mock_st() -> Generator[Tuple[MagicMock, MagicMock], None, None]:
    """Fixture to mock Streamlit's `success` and `error` functions.

    Yields:
        Tuple[MagicMock, MagicMock]: Mocked versions of `st.success` and `st.error`.
    """
    with patch.object(st, "success") as mock_success, patch.object(
        st, "error"
    ) as mock_error:
        yield mock_success, mock_error


@patch("requests.post")
def test_predict_happy(
    mock_post: MagicMock, mock_st: Tuple[MagicMock, MagicMock]
) -> None:
    """Test the `predict` function for a successful prediction.

    Args:
        mock_post (MagicMock): Mocked version of `requests.post`.
        mock_st (Tuple[MagicMock, MagicMock]): Mocked versions of `st.success` and `st.error`.

    Verifies that the function displays a success message with the correct happy prediction details.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"prediction": True, "probability": 0.95}
    mock_post.return_value = mock_response

    data = {"city_services": 4, "housing_costs": 5}

    predict(data, predict_button=True)
    mock_st[0].assert_called_once_with("Good news - you are happy! We're 95% sure 😃")


@patch("requests.post")
def test_predict_unhappy(
    mock_post: MagicMock, mock_st: Tuple[MagicMock, MagicMock]
) -> None:
    """Test the `predict` function for a successful prediction.

    Args:
        mock_post (MagicMock): Mocked version of `requests.post`.
        mock_st (Tuple[MagicMock, MagicMock]): Mocked versions of `st.success` and `st.error`.

    Verifies that the function displays a success message with the correct unhappy prediction details.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"prediction": False, "probability": 0.6}
    mock_post.return_value = mock_response

    data = {"city_services": 2, "housing_costs": 1}

    predict(data, predict_button=True)
    mock_st[1].assert_called_with("Oh no, you seem to be unhappy! At least for 60% 😟")


@patch("requests.post")
def test_predict_empty_data(
    mock_post: MagicMock, mock_st: Tuple[MagicMock, MagicMock]
) -> None:
    """Test the `predict` function when the data is empty or malformed."""

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"prediction": True, "probability": 0.9}
    mock_post.return_value = mock_response

    data: dict[str, str] = {}  # Empty data

    predict(data, predict_button=True)

    # Check if error handling occurs or a message is displayed
    mock_st[0].assert_called_with("Good news - you are happy! We're 90% sure 😃")


@patch("requests.post")
def test_predict_failure(
    mock_post: MagicMock, mock_st: Tuple[MagicMock, MagicMock]
) -> None:
    """Test the `predict` function for a failed prediction due to a server error.

    Args:
        mock_post (MagicMock): Mocked version of `requests.post`.
        mock_st (Tuple[MagicMock, MagicMock]): Mocked versions of `st.success` and `st.error`.

    Verifies that the function displays an error message when the prediction service fails.
    Testing additional error types or HTTP codes could further improve robustness.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException(
        "Server Error"
    )
    mock_post.return_value = mock_response

    data = {"key": "value"}
    predict_button = True
    predict(data, predict_button)
    mock_st[1].assert_called_once_with(
        "Failed to connect to the prediction service: Server Error"
    )

    # Additional test for HTTP 404 error
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "404 Client Error: Not Found"
    )
    mock_post.return_value = mock_response
    predict(data, predict_button)
    mock_st[1].assert_called_with(
        "Failed to connect to the prediction service: 404 Client Error: Not Found"
    )


@patch("requests.post")
def test_predict_no_button_pressed(
    mock_post: MagicMock, mock_st: Tuple[MagicMock, MagicMock]
) -> None:
    """Test the `predict` function when the predict button is not pressed.

    Args:
        mock_post (MagicMock): Mocked version of `requests.post`.
        mock_st (Tuple[MagicMock, MagicMock]): Mocked versions of `st.success` and `st.error`.

    Verifies that no prediction occurs and no messages are displayed when the button is not pressed.
    Testing edge cases where `predict_button` is not strictly boolean could add value.
    """
    data = {"key": "value"}
    predict_button = False
    predict(data, predict_button)

    mock_st[0].assert_not_called()
    mock_st[1].assert_not_called()


@pytest.fixture(scope="function")
@patch("src.streamlit.ui.st_star_rating")
def test_rating_section(mock_st_star_rating: MagicMock, mock_st: MagicMock) -> None:
    """Test the `rating_section` function for correct behavior.

    Args:
        mock_st_star_rating (MagicMock): Mocked version of `st_star_rating`.
        mock_st (MagicMock): Mocked versions of `st` components such as `columns` and `write`.

    Verifies that the function displays the rating section correctly and returns the expected rating value.
    Additional test cases could include minimum and maximum star ratings.
    """
    mock_st.columns.return_value = (MagicMock(), MagicMock())
    mock_col_q = mock_st.columns.return_value[0]
    mock_st_star_rating.return_value = 4

    result = rating_section(
        prompt="Test prompt",
        key="test_key",
        text_font_size=18,
        star_rating_size=25,
    )

    mock_col_q.write.assert_called_once_with(
        "<p style='text-align: left; font-size: 18px;'><b>Test prompt</b></p>",
        unsafe_allow_html=True,
    )
    mock_st_star_rating.assert_called_once_with(
        label=None,
        size=25,
        maxValue=5,
        defaultValue=3,
        key="test_key",
        dark_theme=True,
    )

    assert result == 4

    # Additional test for minimum rating
    mock_st_star_rating.return_value = 1
    result = rating_section(
        prompt="Test prompt",
        key="test_key",
        text_font_size=18,
        star_rating_size=25,
    )
    assert result == 1

    # Invalid value, outside the range.
    mock_st_star_rating.return_value = 0
    result = rating_section(
        prompt="Test prompt",
        key="test_key",
        text_font_size=18,
        star_rating_size=25,
    )

    assert result == 0


if __name__ == "__main__":
    pytest.main()
