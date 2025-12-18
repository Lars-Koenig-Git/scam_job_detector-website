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

st.title('Welcome to Scam Job Detector!')


######################################
#BODY
######################################

st.markdown(
'''
This website serves to predict whether a particular job is is likely to be fake or real.
''')

st.markdown(
    '''
----------------------------------------------
    '''
)

st.markdown(
    '''
Please enter the full job posting text, including the title, description, requirements, and benefits.
    '''
)

# Main field to drop job description
job_description = st.text_area(
    '',
    value=None,
    help='Please insert the full job description including the title, job descriptions, requirements, and benefits.',
    label_visibility='visible',
    placeholder='Job description',
    height=300,
)

# Additional fields to increase predictive power
with st.expander("Additional options to increase prediction accuracy",expanded=True):
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
        url = ' https://scamjobdetector-946041774253.europe-west1.run.app/predict'

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
        st.session_state['outcome_value'] = outcome['fraudulent']

        outcome_proba = outcome['prob_fraudulent']

        st.session_state["outcome_X_columns"] = outcome["column_names"]
        st.session_state["outcome_X_values"]  = outcome["column_values"]

        st.subheader(f"Result of our model: {outcome_value}")
        # st.subheader(f"Probability to be scam: {outcome_proba:.2%}")

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
        url = " https://scamjobdetector-946041774253.europe-west1.run.app/explain"

        params = {
            "column_names": json.dumps(st.session_state["outcome_X_columns"]),
            "column_values": json.dumps(st.session_state["outcome_X_values"]),
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        outcome = response.json()
        outcome_value = st.session_state["outcome_value"]



        if outcome_value == 1:
            st.markdown('''The cloud of words below shows what our ML model has identified in your job description as key indicators for the job being fake.

                    
                        ''')
            # plotting features
            features = outcome['text_contributions_words_fake']
            values = outcome['text_contributions_contribution_fake']
            word_freq = dict(zip(features, np.abs(values)))
            wc = WordCloud(
                width=900,
                height=450,
                background_color="white",
                colormap="Reds"
                ).generate_from_frequencies(word_freq)

            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
            plt.close(fig)
        else:
            # plotting features
            features = outcome['text_contributions_words_real']
            values = outcome['text_contributions_contribution_real']
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
        with st.expander('## Technical explanation'):
            for item in outcome['non_text_contributions']:
                st.text(item)

        # https://www.linkedin.com/pulse/fake-job-listings-9-red-flags-how-spot-them-andersontruckingservice-5cegc/
        # st.link_button("Get additional information on how to identify scam job offers", "https://www.linkedin.com/pulse/fake-job-listings-9-red-flags-how-spot-them-andersontruckingservice-5cegc/")
        # st.markdown('<a href="https://www.linkedin.com/pulse/fake-job-listings-9-red-flags-how-spot-them-andersontruckingservice-5cegc/" target="_blank">Get additional information on how to identify scam job offers</a>', unsafe_allow_html=True)

        # id = np.argmax(np.abs(outcome['shap_values_country']))
        # country = outcome['shap_features_country'][id]
        # st.text(country)

        # # listing whether logo was important
        # id = np.argmax(np.abs(outcome['shap_values_binary']))
        # logo = outcome['shap_features_binary'][id]


        # Create explanation function for company logo feature

        # if company_logo == 0:
        #     explanation = "Missing company logo increases the likelihood that this job posting is fake."
        # else:
        #     explanation = "The presence of a company logo increases the credibility of the job posting."

        # st.text(explanation)
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import streamlit.components.v1 as components

def fetch_preview(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
    }
    r = requests.get(url, headers=headers, timeout=12, allow_redirects=True)

    # LinkedIn often blocks scraping with a "999" response
    if r.status_code in (401, 403, 999):
        raise RuntimeError(f"Blocked by site (HTTP {r.status_code}).")

    soup = BeautifulSoup(r.text, "html.parser")

    def meta(prop: str):
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        return tag.get("content", "").strip() if tag else ""

    title = meta("og:title") or (soup.title.string.strip() if soup.title else url)
    desc  = meta("og:description") or meta("description")
    image = meta("og:image") or meta("twitter:image")
    site  = meta("og:site_name") or urlparse(url).netloc

    # Optional extras (may be empty depending on the page)
    author = meta("author") or meta("article:author")
    return {"url": url, "title": title, "desc": desc, "image": image, "site": site, "author": author}

def render_card(p: dict):
    img_html = f"<img src='{p['image']}' class='lp-img'/>" if p["image"] else ""
    author_html = f"<div class='lp-meta'>Written by<br><span class='lp-author'>{p['author']}</span></div>" if p["author"] else ""

    html = f"""
    <div class="lp-wrap">
      <a class="lp-link" href="{p['url']}" target="_blank" rel="noopener noreferrer">
        <div class="lp-top">
          <div class="lp-site">{p['site']}</div>
          <div class="lp-title">{p['title']}</div>
          <div class="lp-desc">{p['desc']}</div>
        </div>
        <div class="lp-bottom">
          {author_html}
          <div class="lp-thumb">{img_html}</div>
        </div>
      </a>
    </div>

    <style>
      .lp-wrap {{
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 14px;
        overflow: hidden;
        background: rgba(255,255,255,0.02);
      }}
      .lp-link {{
        display:block;
        padding: 18px 18px 14px 18px;
        text-decoration:none;
        color: inherit;
      }}
      .lp-site {{
        font-size: 14px;
        opacity: 0.85;
        margin-bottom: 10px;
      }}
      .lp-title {{
        font-size: 26px;
        font-weight: 700;
        line-height: 1.15;
        margin-bottom: 10px;
        color: #4ea1ff;
      }}
      .lp-desc {{
        font-size: 16px;
        opacity: 0.92;
        line-height: 1.5;
        margin-bottom: 16px;
        max-height: 4.6em;
        overflow: hidden;
      }}
      .lp-bottom {{
        display:flex;
        gap: 16px;
        align-items:flex-start;
        justify-content: space-between;
      }}
      .lp-meta {{
        font-size: 16px;
        opacity: 0.9;
        white-space: nowrap;
      }}
      .lp-author {{
        display:inline-block;
        margin-top: 6px;
        font-size: 22px;
        font-weight: 500;
        white-space: normal;
      }}
      .lp-thumb {{
        width: 220px;
        min-width: 220px;
      }}
      .lp-img {{
        width: 100%;
        border-radius: 12px;
        display:block;
        object-fit: cover;
      }}
    </style>
    """
    components.html(html, height=360)

st.title("Additional information for identifying fake job postings.")


url = st.text_input(
    "URL",
    "https://www.linkedin.com/pulse/fake-job-listings-9-red-flags-how-spot-them-andersontruckingservice-5cegc/",
)

if url:
    try:
        preview = fetch_preview(url)
        render_card(preview)
    except Exception as e:
        st.warning(f"Preview not available: {e}")
        st.markdown(f"[Open link]({url})")
