import json
import os

import requests
from streamlit_star_rating import st_star_rating

import streamlit as st

# Check whether local deployment or not
local_deployment = os.getenv("LOCAL", "True")
if local_deployment == "True":
    backend_host = "localhost"
else:
    backend_host = "backend"

# Custom size options
star_rating_size = 25
text_font_size = 18

# Use custom CSS to set a maximum width
with open("src/static/css/style.css") as f:
    css = f.read()

st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

st.title("Find out how happy you are with your living situation :blush:")

rating_text_1 = "How satisfied are you with the availability of information about the city services?"
st.write(f"<b><span style='font-size: {text_font_size}px;'>{rating_text_1}</span></b>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    pass
with col3:
    pass
with col2:
    rating_1 = st_star_rating(
        label=None,
        size=star_rating_size,
        maxValue=5,
        defaultValue=3,
        key="rating_1",
        customCSS=f"<style>{css}</style>",
        dark_theme=True,
    )

rating_text_2 = "How satisfied are you with the cost of housing?"
st.write(f"<b><span style='font-size: {text_font_size}px;'>{rating_text_2}</span></b>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    pass
with col3:
    pass
with col2:
    rating_2 = st_star_rating(
        label=None,
        size=star_rating_size,
        maxValue=5,
        defaultValue=3,
        key="rating_2",
        dark_theme=True,
    )

rating_text_3 = "How satisfied are you with the overall quality of public schools?"
st.write(f"<b><span style='font-size: {text_font_size}px;'>{rating_text_3}</span></b>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    pass
with col3:
    pass
with col2:
    rating_3 = st_star_rating(
        label=None,
        size=star_rating_size,
        maxValue=5,
        defaultValue=3,
        key="rating_3",
        dark_theme=True,
    )

rating_text_4 = "How much do you trust in the local police?"
st.write(f"<b><span style='font-size: {text_font_size}px;'>{rating_text_4}</span></b>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    pass
with col3:
    pass
with col2:
    rating_4 = st_star_rating(
        label=None,
        size=star_rating_size,
        maxValue=5,
        defaultValue=3,
        key="rating_4",
        dark_theme=True,
    )

rating_text_5 = "How much are you satisfied in the maintenance of streets and sidewalks?"
st.write(f"<b><span style='font-size: {text_font_size}px;'>{rating_text_5}</span></b>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    pass
with col3:
    pass
with col2:
    rating_5 = st_star_rating(
        label=None,
        size=star_rating_size,
        maxValue=5,
        defaultValue=3,
        key="rating_5",
        dark_theme=True,
    )

rating_text_6 = "How much are you satisfied in the availability of social community events?"
st.write(f"<b><span style='font-size: {text_font_size}px;'>{rating_text_6}</span></b>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    pass
with col3:
    pass
with col2:
    rating_6 = st_star_rating(
        label=None,
        size=star_rating_size,
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
    response = requests.post(f"http://{backend_host}:8080/predict", json=data)
    response_dict = json.loads(response.text)
    prediction = response_dict["prediction"]
    probabilty = response_dict["probability"]
    if prediction:
        st.success(f"Good news - you are happy! We're {probabilty:.0%} sure :grinning:")
    else:
        st.error(f"Oh no, you seem to be unhappy! At least for {probabilty:.0%} :worried:")
