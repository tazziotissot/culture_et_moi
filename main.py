import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from src.utils import *
from src.dashboard import *
from src.survey import *
import yaml
from yaml.loader import SafeLoader
import datetime

st.set_page_config(layout="wide", page_title="Culture & Moi")
st.title("Culture & Moi")

with open("src/credentials.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)
stauth.Hasher.hash_passwords(config["credentials"])
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["pre-authorized"],
)


name, authentication_status, username = authenticator.login()
if st.session_state["authentication_status"]:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*!')
    if username in ["mrabeman", "ttissot"]:
        make_survey, launch_survey, dashboard, profile = st.tabs(
            ["Create survey", "Launch survey", "Dashboard", "Profile"]
        )
        with make_survey:
            # st.header("Import survey")
            # survey_dict_pkl = st.file_uploader(
            #     "Choose a file", accept_multiple_files=False, type=["pkl"]
            # )
            # if survey_dict_pkl is None:
            #     survey_dict = {}
            # else:
            #     survey_dict = pkl.load(open(survey_dict_pkl.name, "rb"))
            survey_dict = create_survey()
            show_temporary_survey(survey_dict)
            if st.button("Export survey"):
                st.success(f"Saved at {datetime.datetime.now()}!")
                pkl.dump(
                    survey_dict, open(f"survey_{datetime.datetime.now()}.pkl", "wb")
                )
        with launch_survey:
            st.header("TODO: List existing survey files, and pick the one to launch")
        with dashboard:
            main_dashboard()
        with profile:
            personal_details(authenticator, config)
    else:
        survey, profile = st.tabs(["Survey", "Profile"])
        with survey:
            survey_dict = make_dummy_survey()
            result = show_survey(survey_dict, username)
            st.json(result)
        with profile:
            personal_details(authenticator, config)
elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
    sign_up(authenticator, config)
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")
    sign_up(authenticator, config)
