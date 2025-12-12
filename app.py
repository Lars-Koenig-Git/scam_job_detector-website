import streamlit as st
import requests

import json

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

st.title('Welcome to Scam Job Detection!')

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
    col_employ, col_country, col_logo = st.columns([1,1,1], gap = 'medium')

    employment_type = col_employ.selectbox(
        'Employment type',
        options=employment_type,
        index=None,
        help='Please insert the type of employment the company offers such as full-time, part-time.',
        placeholder='Insert employment type'
    )

    country_id = col_country.selectbox(
        "Country",
        options=sorted(countries.keys()),
        format_func=lambda code: f"{code} — {countries[code]}",
        index=None,
        help='The input should be the country ID as for example "US" for United States of America',
        placeholder='e.g. "US": "United States of America"',
    )


    company_logo = col_logo.selectbox(
        "Country",
        options=['yes', 'no'],
        index=None,
        help='Please insert whether the company provided a company logo or not with "yes" or "no".',
        placeholder='Has company logo yes/no',
    )


    col_industry, col_function = st.columns([1,1], gap='medium')

    industry = col_industry.selectbox(
        'Industry',
        options=industries,
        index=None,
        help='Please insert the industrial sector of the job offer such as "Information Technology"',
        placeholder='Insert industry of job offer'
    )

    comp_function = col_function.selectbox(
        'Function of the Company',
        options=company_function,
        index=None,
        help='Please insert the functionality of the company as for example Management Consulting.',
        placeholder='Insert function of the company'
    )




if st.button('Predict'):
    # define url for our api on gcloud
    url = 'https://scamjobdetector-946041774253.europe-west1.run.app/predict'

    # Add the input from above to pass as paramters in our prediction model.
    input_values = {
            'location': country_id,
            'industry': industry,
            'function_str': comp_function,
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
    outcome = outcome['fraudulent']
    st.subheader(f'Result of our model:{outcome}')

    if outcome == 1:
        '''
        This job offer is most likely fake.
        '''
    else:
        '''
        This job offer is most likely a correct job offer. However with a probability of X%, the job offer is still fake.
        '''
