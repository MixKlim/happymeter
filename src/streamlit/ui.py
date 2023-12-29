import json

import requests
from streamlit_star_rating import st_star_rating

import streamlit as st

st.title("Find out how happy you are with your living situation :blush:")

rating_1 = st_star_rating(
    "How satisfied are you with the availability of information about the city services?",
    maxValue=5,
    defaultValue=3,
    key="rating_1",
    dark_theme=True,
    customCSS="..\\css\\style.css",
)
rating_2 = st_star_rating(
    "How satisfied are you with the cost of housing?", maxValue=5, defaultValue=3, key="rating_2", dark_theme=True
)
rating_3 = st_star_rating(
    "How satisfied are you with the overall quality of public schools?",
    maxValue=5,
    defaultValue=3,
    key="rating_3",
    dark_theme=True,
)
rating_4 = st_star_rating(
    "How much do you trust in the local police?", maxValue=5, defaultValue=3, key="rating_4", dark_theme=True
)
rating_5 = st_star_rating(
    "How much are you satisfied in the maintenance of streets and sidewalks?",
    maxValue=5,
    defaultValue=3,
    key="rating_5",
    dark_theme=True,
)
rating_6 = st_star_rating(
    "How much are you satisfied in the availability of social community events?",
    maxValue=5,
    defaultValue=3,
    key="rating_6",
    dark_theme=True,
)

data = {
    "city_services": rating_1,
    "housing_costs": rating_2,
    "school_quality": rating_3,
    "local_policies": rating_4,
    "maintenance": rating_5,
    "social_events": rating_6,
}

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    pass
with col2:
    pass
with col4:
    pass
with col5:
    pass
with col3:
    predict_button = st.button(label="Submit your ratings")

if predict_button:
    response = requests.post("http://127.0.0.1:8080/predict", json=data)
    response_dict = json.loads(response.text)
    prediction = response_dict["prediction"]
    probabilty = response_dict["probability"]
    if prediction:
        st.success(f"You are happy! We're {probabilty:.0%} sure!")
    else:
        st.error(f"You seem to be unhappy! At least for {probabilty:.0%}...")
