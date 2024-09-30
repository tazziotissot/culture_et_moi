import streamlit as st
import pandas as pd
import numpy as np
from itertools import product
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from textwrap import wrap
import yaml


def main_dashboard():
    uploaded_file = st.file_uploader(
        "Choose a file", accept_multiple_files=False, type=["xlsx", "csv"]
    )
    if uploaded_file is not None:
        df = import_data(uploaded_file)
        questions, num_questions = extract_questions(df)
        groups = group_questions(num_questions)
        list_users = extract_users(df)
        df = rescale_columns(df, num_questions)
        st.header("Indice Culture & Moi")
        st.plotly_chart(score_treemap(df, [], num_questions))
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
        col1, col2 = st.columns(2)
        with col1:
            st.header("Questions")
            select_question = st.selectbox("Questions", options=groups)
            plot_questions = st.empty()
            with plot_questions:
                st.plotly_chart(
                    plot_scores_questions(df, select_question, num_questions, groups)
                )
        with col2:
            st.header("People")
            select_user = st.multiselect("Users", options=["All"] + list_users)
            plot_users = st.empty()
            with plot_users:
                st.plotly_chart(plot_scores_users(df, select_user, num_questions))


def import_data(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.name.endswith(".xlsx") or file.name.endswith(".xls"):
        df = pd.read_excel(file)
    return df


def group_questions(num_questions):
    ref = {
        "Interdependency and objectives": [
            "I am aware that we depend on each other within my team to be able to deliver"
        ],
        "Agreed rules in the way of working": [
            "I feel the rules we use for our way of working within the team are defined and agreed upon by the whole team"
        ],
        "Sense of belonging": [
            "I do feel I belong to the team",
            "I feel that everyone, myself included, contributes to the care of the ambiance of the team.",
        ],
        "Bond the group": [
            "With the other members of the team we share collective time which allows us to be united.",
            "I feel I am at ease with the other team members",
        ],
        "Conflict resolution": [
            "I have the feeling disagreements/misunderstandings, conflicts are resolved through peaceful dialogue and contribute to the development of empathy within the team"
        ],
        "Safe environment": [
            "I do feel I am supported",
            "I feel I am in a safe environment",
            "I feel that I am not judged or evaluated",
        ],
    }
    groups = {key: [q for q in ref[key] if q in num_questions] for key in ref}
    return groups


def extract_questions(df):
    questions = df.columns.tolist()[6:]
    num_questions = [col for col in questions if df[col].dtype != "O"]
    return questions, num_questions


def extract_users(df):
    return df["ID"].unique().tolist()


def rescale_columns(df: pd.DataFrame, num_questions: list) -> pd.DataFrame:
    for col in num_questions:
        if df[col].max() > 3 or df[col].min() > 0:
            df[col] = np.where(df[col] > 3, df[col] - 3, df[col] - 4)
    return df


def plot_scores_questions(df, question, num_questions, groups):
    dfx = (
        df[num_questions]
        .stack()
        .reset_index(name="Score")
        .groupby("level_1")["Score"]
        .value_counts()
        .reset_index(name="count")
    )
    dfxtmp = pd.DataFrame(
        list(product(dfx["level_1"].unique(), dfx["Score"].unique())),
        columns=["level_1", "Score"],
    )
    dfx = dfx.merge(dfxtmp, how="right").fillna(0)
    dfx.rename(columns={"level_1": "Question"}, inplace=True)
    # Use question group to select
    subset_questions = groups[question]
    dfx = dfx[dfx["Question"].isin(subset_questions)]
    # dfx = dfx[dfx["Question"].isin(question)]
    dfx["Score"] = pd.Categorical(dfx["Score"], categories=[-3, -2, -1, 1, 2, 3])
    dfx["Question"] = (
        dfx["Question"].str.wrap(30).apply(lambda x: x.replace("\n", "<br>"))
    )
    dfx.sort_values(by="Score", inplace=True)
    colors_scores = [
        "#D73027",  # Rouge foncé
        "#FC8D59",  # Rouge
        "#FEE08B",  # Jaune
        "#D9EF8B",  # Vert clair
        "#91CF60",  # Vert
        "#1A9850",  # Vert foncé
    ]

    fig = px.bar(
        dfx,
        x="Question",
        y="count",
        color="Score",
        color_discrete_sequence=colors_scores,
        category_orders={"Score": [-3, -2, -1, 1, 2, 3]},
        height=400,
    )
    fig.update_layout(
        yaxis_visible=False,
        yaxis_showticklabels=False,
        coloraxis_colorbar=dict(
            tickvals=[-3, -2, -1, 1, 2, 3], ticktext=["-3", "-2", "-1", "1", "2", "3"]
        ),
        xaxis={"tickwidth": 50},
    )
    fig.update_xaxes(title="Question", visible=True, showticklabels=True)
    return fig


def plot_scores_users(df, user, num_questions):
    dfx = df.copy(deep=True)
    dfx.index = dfx["ID"]
    dfmean = (
        dfx[num_questions]
        .stack()
        .reset_index(name="Score")
        .groupby("ID")["Score"]
        .median()
        .reset_index(name="Median score")
    )
    dfx = (
        dfx[num_questions]
        .stack()
        .reset_index(name="Score")
        .groupby("ID")["Score"]
        .value_counts()
        .reset_index(name="count")
    )
    dfxtmp = pd.DataFrame(
        list(product(dfx["ID"].unique(), dfx["Score"].unique())),
        columns=["ID", "Score"],
    )
    dfx = dfx.merge(dfxtmp, how="right").fillna(0)
    if "All" not in user:
        dfx = dfx[dfx["ID"].isin(user)]
        dfmean = dfmean[dfmean["ID"].isin(user)]
    id_order = dfmean.sort_values(by="Median score")["ID"]
    dfx["ID"] = pd.Categorical(
        dfx["ID"], categories=dfx.sort_values(by="ID")["ID"].unique()
    )
    dfx["Score"] = pd.Categorical(dfx["Score"], categories=[-3, -2, -1, 1, 2, 3])
    dfx.sort_values(by="Score", inplace=True)
    colors_scores = [
        "#D73027",  # Rouge foncé
        "#FC8D59",  # Rouge
        "#FEE08B",  # Jaune
        "#D9EF8B",  # Vert clair
        "#91CF60",  # Vert
        "#1A9850",  # Vert foncé
    ]

    fig = px.bar(
        dfx,
        x="ID",
        y="count",
        color="Score",
        color_discrete_sequence=colors_scores,
        category_orders={"Score": [-3, -2, -1, 1, 2, 3], "ID": id_order},
        height=400,
    )
    fig.update_layout(
        yaxis_visible=False,
        yaxis_showticklabels=False,
        coloraxis_colorbar=dict(
            tickvals=[-3, -2, -1, 1, 2, 3], ticktext=["-3", "-2", "-1", "1", "2", "3"]
        ),
        xaxis={"tickwidth": 50},
    )
    fig.update_xaxes(title="ID", visible=True, showticklabels=True, type="category")
    return fig


def plot_scores_top(df, num_questions, top: bool):
    dfx = df[num_questions].mean().reset_index(name="Avg. score")
    dfx["index"] = dfx["index"].str.wrap(30).apply(lambda x: x.replace("\n", "<br>"))
    if top:
        dfx = dfx.sort_values(by="Avg. score", ascending=True).tail(3)
    else:
        dfx = dfx.sort_values(by="Avg. score", ascending=True).head(3)
    colors_scores = [
        "#D73027",  # Rouge foncé
        "#FC8D59",  # Rouge
        "#FEE08B",  # Jaune
        "#D9EF8B",  # Vert clair
        "#91CF60",  # Vert
        "#1A9850",  # Vert foncé
    ]
    fig = px.bar(
        dfx,
        x="index",
        y="Avg. score",
        color="Avg. score",
        color_continuous_scale=colors_scores,
        range_color=[-3, 3],
    )
    fig.update_layout(
        yaxis_visible=False,
        yaxis_showticklabels=False,
        yaxis_range=[-3, 3],
        coloraxis_colorbar=dict(
            tickvals=[-3, -2, -1, 1, 2, 3], ticktext=["-3", "-2", "-1", "1", "2", "3"]
        ),
        xaxis={"tickwidth": 50},
    )
    fig.update_xaxes(title="", visible=True, showticklabels=True)
    return fig


def score_treemap(df, selection, num_questions):
    dfx = df.copy(deep=True)
    dfx.index = dfx["ID"]
    dfx = (
        dfx[num_questions]
        .stack()
        .reset_index(name="Score")
        .groupby("ID")["Score"]
        .mean()
        .reset_index(name="Avg. score")
    )
    dfx["Department"] = ["Department of Mental health"] * 5 + [
        "Department of Informatics"
    ] * 8
    dfx["Team"] = (
        ["Team Culture & Moi"] * 5
        + ["Team Agilopathes"] * 3
        + ["Team Collaboration"] * 5
    )
    colors_scores = [
        "#D73027",  # Rouge foncé
        "#FC8D59",  # Rouge
        "#FEE08B",  # Jaune
        "#D9EF8B",  # Vert clair
        "#91CF60",  # Vert
        "#1A9850",  # Vert foncé
    ]
    fig = px.treemap(
        dfx,
        path=[px.Constant("all"), "Department", "Team", "ID"],
        color="Avg. score",
        color_continuous_scale=colors_scores,
        range_color=[-3, 3],
    )
    return fig
