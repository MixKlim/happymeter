import os

import requests
from streamlit_star_rating import st_star_rating

import streamlit as st


def get_backend_host() -> str:
    """
    Get the backend host URL from the environment variables or use a default value.

    Returns:
        str: The backend host URL.
    """
    return os.getenv("BACKEND_HOST", "127.0.0.1:8080")


def predict(backend_host: str, data: dict, predict_button: bool) -> None:
    """
    Send a prediction request to the backend and display the results in the Streamlit app.

    Args:
        backend_host (str): The URL of the backend server.
        data (dict): The input data for the prediction.
        predict_button (bool): Whether the prediction button was clicked.
    """
    if predict_button:
        response = None
        try:
            # Attempt HTTPS connection
            response = requests.post(f"https://{backend_host}/predict", json=data)
            response.raise_for_status()  # Check if the request was successful
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            try:
                # Fallback to HTTP
                response = requests.post(f"http://{backend_host}/predict", json=data)
                response.raise_for_status()  # Check if the fallback request was successful
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to the prediction service: {e}")

        if response:
            response_dict = response.json()
            prediction = response_dict["prediction"]
            probability = response_dict["probability"]

            if prediction:
                st.success(
                    f"Good news - you are happy! We're {probability:.0%} sure 😃"
                )
            else:
                st.error(
                    f"Oh no, you seem to be unhappy! At least for {probability:.0%} 😟"
                )


def rating_section(
    prompt: str, key: str, text_font_size: int, star_rating_size: int
) -> int:
    """
    Display a rating section with a question prompt and star rating.

    Args:
        prompt (str): The question prompt to display.
        key (str): The unique key for the star rating component.
        text_font_size (int): The font size for the question prompt.
        star_rating_size (int): The size of the star rating component.

    Returns:
        int: The selected star rating value.
    """
    col_q, col_s = st.columns([3, 1])
    with col_q:
        st.write(
            f"<p style='text-align: left; font-size: {text_font_size}px;'><b>{prompt}</b></p>",
            unsafe_allow_html=True,
        )
    with col_s:
        return st_star_rating(
            label=None,
            size=star_rating_size,
            maxValue=5,
            defaultValue=3,
            key=key,
            dark_theme=True,
        )


def main() -> None:
    """
    Main function to run the Streamlit app, gather user input, and display the results.
    """
    # Page configuration
    st.set_page_config("happymeter", page_icon="😊", layout="wide")

    # Constants
    STAR_RATING_SIZE = 25
    TEXT_FONT_SIZE = 18
    CSS_FILE_PATH = "src/static/css/style.css"

    # Apply custom CSS
    if os.path.exists(CSS_FILE_PATH):
        with open(CSS_FILE_PATH) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Title with negative offset
    st.markdown(
        """
        <h1 style="margin-top: -70px; font-size: 30px;">Find out how happy you are with your living situation 😊</h1>
        """,
        unsafe_allow_html=True,
    )

    # Questions and keys for ratings
    questions = [
        "How satisfied are you with the availability of information about the city services?",
        "How satisfied are you with the cost of housing?",
        "How satisfied are you with the overall quality of public schools?",
        "How much do you trust in the local police?",
        "How satisfied are you with the maintenance of streets and sidewalks?",
        "How satisfied are you with the availability of social community events?",
    ]
    keys = [
        "city_services",
        "housing_costs",
        "school_quality",
        "local_policies",
        "maintenance",
        "social_events",
    ]

    # Collect ratings
    ratings = {
        key: rating_section(prompt, key, TEXT_FONT_SIZE, STAR_RATING_SIZE)
        for prompt, key in zip(questions, keys)
    }

    # Submit button centered
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([4, 2, 4])
    with col2:
        predict_button = st.button(label="Submit your ratings")

    # Predict results
    backend_host = get_backend_host()
    predict(backend_host, ratings, predict_button)


if __name__ == "__main__":
    main()
