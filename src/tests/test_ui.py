import os
import pytest
import requests
from unittest.mock import patch, MagicMock
from typing import Generator, Tuple
import streamlit as st
from src.streamlit.ui import get_backend_host, rating_section, predict
from streamlit.testing.v1 import AppTest


# Test the application execution
def test_app_run() -> None:
    """Tests that the Streamlit application runs without exceptions."""
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
    """Tests the `get_backend_host` function with various REMOTE environment values.

    Args:
        remote_env (str): The REMOTE environment variable value.
        expected_host (str): The expected backend host.
    """
    with patch.dict(os.environ, {"REMOTE": remote_env}):
        assert get_backend_host() == expected_host


@pytest.fixture(scope="function")
def mock_st() -> Generator[Tuple[MagicMock, MagicMock], None, None]:
    """Provides mocked Streamlit success and error methods.

    Yields:
        Tuple[MagicMock, MagicMock]: Mocked `st.success` and `st.error` methods.
    """
    with patch.object(st, "success") as mock_success, patch.object(
        st, "error"
    ) as mock_error:
        yield mock_success, mock_error


@patch("requests.post")
def test_predict_happy(
    mock_post: MagicMock, mock_st: Tuple[MagicMock, MagicMock]
) -> None:
    """Tests the `predict` function for a positive prediction.

    Args:
        mock_post (MagicMock): Mocked `requests.post` method.
        mock_st (Tuple[MagicMock, MagicMock]): Mocked Streamlit methods.
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
    """Tests the `predict` function for a negative prediction.

    Args:
        mock_post (MagicMock): Mocked `requests.post` method.
        mock_st (Tuple[MagicMock, MagicMock]): Mocked Streamlit methods.
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
    """Tests the `predict` function with empty input data.

    Args:
        mock_post (MagicMock): Mocked `requests.post` method.
        mock_st (Tuple[MagicMock, MagicMock]): Mocked Streamlit methods.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"prediction": True, "probability": 0.9}
    mock_post.return_value = mock_response

    data: dict[str, str] = {}  # Empty data
    predict(data, predict_button=True)
    mock_st[0].assert_called_with("Good news - you are happy! We're 90% sure 😃")


@patch("requests.post")
def test_predict_failure(
    mock_post: MagicMock, mock_st: Tuple[MagicMock, MagicMock]
) -> None:
    """Tests the `predict` function for a failed prediction service call.

    Args:
        mock_post (MagicMock): Mocked `requests.post` method.
        mock_st (Tuple[MagicMock, MagicMock]): Mocked Streamlit methods.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException(
        "Server Error"
    )
    mock_post.return_value = mock_response

    data = {"key": "value"}
    predict(data, predict_button=True)
    mock_st[1].assert_called_once_with(
        "Failed to connect to the prediction service: Server Error"
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
    predict_button = False
    predict(data, predict_button)
    mock_st[0].assert_not_called()
    mock_st[1].assert_not_called()


def test_rating_section() -> None:
    """Tests the `rating_section` function for correct Streamlit component behavior."""
    with patch("streamlit.columns") as mock_columns, patch(
        "streamlit.write"
    ) as mock_write, patch("src.streamlit.ui.st_star_rating") as mock_star_rating:
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
