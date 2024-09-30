import streamlit as st
import pandas as pd
import numpy as np
from itertools import product
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from textwrap import wrap
import yaml


#### AUTHENTICATOR ####
def personal_details(authenticator, config):
    try:
        if authenticator.reset_password(st.session_state["username"]):
            st.success("Password modified successfully")
            with open("src/credentials.yaml", "w") as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)
    try:
        if authenticator.update_user_details(st.session_state["username"]):
            st.success("Entries updated successfully")
            with open("src/credentials.yaml", "w") as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)


def sign_up(authenticator, config):
    try:
        (
            email_of_registered_user,
            username_of_registered_user,
            name_of_registered_user,
        ) = authenticator.register_user(pre_authorization=False)
        if email_of_registered_user:
            st.success("User registered successfully")
            with open("src/credentials.yaml", "w") as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)
