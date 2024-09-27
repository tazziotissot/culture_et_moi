import streamlit as st
import pandas as pd
import numpy as np
from itertools import product
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from textwrap import wrap


def import_data(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.name.endswith(".xlsx") or file.name.endswith(".xls"):
        df = pd.read_excel(file)
    return df


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


def plot_scores_questions(df, question, num_questions):
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
    dfx = dfx[dfx["Question"].isin(question)]
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
