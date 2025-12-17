import streamlit as st
import requests
from wordcloud import WordCloud
import json
import matplotlib.pyplot as plt
import numpy as np

# read in column values
with (
    open("data/countries.json", "r", encoding="utf-8") as f1,
    open("data/industry.json", "r", encoding="utf-8") as f2,
    open("data/function.json", "r", encoding="utf-8") as f3,
    open("data/employment_type.json", "r", encoding="utf-8") as f4,
):
    countries = json.load(f1)
    industries = json.load(f2)
    company_function = json.load(f3)
    employment_type = json.load(f4)



#####################################
# BANNER
#####################################

from PIL import Image
from io import BytesIO

# Image URL
banner_url = "scam_job_detector.png"

# Fetch image from URL
# response = requests.get(banner_url)
img = Image.open(banner_url)

# Resize to custom width and height (stretch if necessary)
custom_width = 800
custom_height = 800
img = img.resize((custom_width, custom_height))

# Display the resized/stretched image

left_co, cent_co,last_co = st.columns([1, 6, 1])
with cent_co:
    st.image(img, caption="")

######################################
#Title
######################################

st.title('Welcome to Scam Job Detection!')


######################################
#BODY
######################################

st.markdown(
'''
This website serves to predict whether a particular job is is likely to be fake or real.
''')

st.markdown(
    '''
    #### Please enter the full job posting text, including the title, description, requirements, and benefits.
    '''
)

# Main field to drop job description
job_description = st.text_area(
    '',
    value=None,
    help='Please insert the full job description including the title, job descriptions, requirements, and benefits.',
    label_visibility='visible',
    placeholder='Job description',
    height=200,
)

# Additional fields to increase predictive power
with st.expander("Additional options to increase prediction accuracy"):
    col_employ, col_country = st.columns([1,1], gap = 'medium')

    employment_type = col_employ.selectbox(
        'Employment type',
        options=employment_type,
        index=0,
        help='Please insert the type of employment the company offers such as full-time, part-time.',
        placeholder='Insert employment type'
    )

    country_id = col_country.selectbox(
        "Country",
        options=countries.keys(),
        format_func=lambda code: f"{code} — {countries[code]}",
        index=0,
        help='The input should be the country ID as for example "US" for United States of America',
        placeholder='e.g. "US": "United States of America"',
    )



    col_industry, col_logo = st.columns([1,1], gap='medium')

    industry = col_industry.selectbox(
        'Industry',
        options=industries,
        index=0,
        help='Please insert the industrial sector of the job offer such as "Information Technology"',
        placeholder='Insert industry of job offer'
    )

    company_logo = col_logo.selectbox(
        "Company logo",
        options=[0,1],
        index=0,
        help='Please insert whether the company provided a company logo or not with "yes" or "no".',
        placeholder='Has company logo yes/no',
    )


if st.button('Predict'):

    # 🔄 Spinner while prediction is running
    with st.spinner("Predicting..."):

        # define url for our api on gcloud
        # url = 'https://scamjobdetector-946041774253.europe-west1.run.app/predict'
        url = 'http://127.0.0.1:8000/predict'

        # Add the input from above to pass as parameters in our prediction model
        input_values = {
            'location': country_id,
            'industry': industry,
            'employment_type': employment_type,
            'has_company_logo': company_logo,
            'description': job_description
        }

        # function to call prediction model
        def predict_outcome(params):
            response = requests.get(url, params=params)
            return response.json()

        # get result
        outcome = predict_outcome(input_values)
        outcome_value = outcome['fraudulent']
        outcome_proba = outcome['prob_fraudulent']
        st.session_state["outcome_X_columns"] = outcome["column_names"]
        st.session_state["outcome_X_values"]  = outcome["column_values"]

        st.subheader(f"Result of our model: {outcome_value}")
        st.subheader(f"Probability to be scam: {outcome_proba:.2%}")

        # 🔴 Fake job → red text | 🟢 Genuine job → green text
        if outcome_value == 1:
            st.markdown(
                "<h4 style='color:red;'>🚨 This job offer is most likely fake.</h4>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<h4 style='color:green;'>✅ This job offer is likely genuine.</h4>",
                unsafe_allow_html=True
            )





if st.button('Explain'):
    # 🔄 Spinner while prediction is running
    with st.spinner("Computing cloud of words that drove the prediction..."):

        # Add the input from above to pass as paramters in our prediction model.
        url = "http://127.0.0.1:8000/explain"

        params = {
            "column_names": json.dumps(st.session_state["outcome_X_columns"]),
            "column_values": json.dumps(st.session_state["outcome_X_values"]),
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        outcome = response.json()

        # plotting features
        features = outcome['shap_features_text']
        values = outcome['shap_text_values']
        word_freq = dict(zip(features, np.abs(values)))
        wc = WordCloud(
            width=900,
            height=450,
            background_color="white"
            ).generate_from_frequencies(word_freq)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
        plt.close(fig)

        # Listing columns
        id = np.argmax(np.abs(outcome['shap_values_country']))
        country = outcome['shap_features_country'][id]
        st.text(country)

        # listing whether logo was important
        id = np.argmax(np.abs(outcome['shap_values_binary']))
        logo = outcome['shap_features_binary'][id]


        # Create explanation function for company logo feature

        if company_logo == 0:
            explanation = "Missing company logo increases the likelihood that this job posting is fake."
        else:
            explanation = "The presence of a company logo increases the credibility of the job posting."

        st.text(explanation)
