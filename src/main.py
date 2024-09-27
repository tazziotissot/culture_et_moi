import streamlit as st
import pandas as pd
from utils import *

st.set_page_config(layout="wide", page_title="Culture & Moi")
st.title("Culture & Moi")

uploaded_file = st.file_uploader(
    "Choose a file", accept_multiple_files=False, type=["xlsx", "csv"]
)
if uploaded_file is not None:
    df = import_data(uploaded_file)
    questions, num_questions = extract_questions(df)
    list_users = extract_users(df)
    df = rescale_columns(df, num_questions)
    col1, col2 = st.columns(2)
    with col1:
        st.header("Questions")
        select_question = st.multiselect("Questions", options=num_questions)
        plot_questions = st.empty()
        with plot_questions:
            st.plotly_chart(plot_scores_questions(df, select_question, num_questions))
    with col2:
        st.header("People")
        select_user = st.multiselect("Users", options=["All"] + list_users)
        plot_users = st.empty()
        with plot_users:
            st.plotly_chart(plot_scores_users(df, select_user, num_questions))
    col3, col4 = st.columns(2)
    with col3:
        st.header("Top 3 areas to develop")
        plot_flop3 = st.empty()
        with plot_flop3:
            st.plotly_chart(plot_scores_top(df, num_questions, False))
    with col4:
        st.header("Top 3 strengths")
        plot_top3 = st.empty()
        with plot_top3:
            st.plotly_chart(plot_scores_top(df, num_questions, True))
    st.header("Indice Culture & Moi")
    st.plotly_chart(score_treemap(df, [], num_questions))
