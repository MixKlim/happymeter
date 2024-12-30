import os
import requests
import streamlit as st
from streamlit_star_rating import st_star_rating


def get_backend_host() -> str:
    """Check whether local deployment or not."""
    remote_deployment = os.getenv("REMOTE", "")
    return "backend" if bool(remote_deployment) else "127.0.0.1"


def predict(data: dict, predict_button: bool) -> None:
    """Display proper message based on model prediction."""
    if predict_button:
        try:
            response = requests.post(
                f"http://{get_backend_host()}:8080/predict", json=data
            )
            response.raise_for_status()
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
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to the prediction service: {e}")


def rating_section(
    prompt: str, key: str, text_font_size: int, star_rating_size: int
) -> int:
    """Reusable component for a rating section with question and stars on the same line."""

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
    st.markdown("<br>", unsafe_allow_html=True)  # Small spacer
    col1, col2, col3 = st.columns([4, 2, 4])
    with col2:
        predict_button = st.button(label="Submit your ratings")

    # Predict results
    predict(ratings, predict_button)


if __name__ == "__main__":
    main()
