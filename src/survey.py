import streamlit_survey as ss
import streamlit as st
import datetime
import json
import pickle as pkl


def make_dummy_survey():
    survey = {
        "Interdependency and objectives": [
            {
                "type": "Likert",
                "Text": "I am aware that we depend on each other within my team to be able to deliver",
            }
        ],
        "Agreed rules in the way of working": [
            {
                "type": "Likert",
                "Text": "I feel the rules we use for our way of working within the team are defined and agreed upon by the whole team",
            }
        ],
        "Sense of belonging": [
            {"type": "Likert", "Text": "I do feel I belong to the team"},
            {
                "type": "Likert",
                "Text": "I feel that everyone, myself included, contributes to the care of the ambiance of the team.",
            },
        ],
        "Bond the group": [
            {
                "type": "Likert",
                "Text": "With the other members of the team we share collective time which allows us to be united.",
            },
            {
                "type": "Likert",
                "Text": "I feel I am at ease with the other team members",
            },
        ],
        "Conflict resolution": [
            {
                "type": "Likert",
                "Text": "I have the feeling disagreements/misunderstandings, conflicts are resolved through peaceful dialogue and contribute to the development of empathy within the team",
            }
        ],
        "Safe environment": [
            {"type": "Likert", "Text": "I do feel I am supported"},
            {"type": "Likert", "Text": "I feel I am in a safe environment"},
            {"type": "Likert", "Text": "I feel that I am not judged or evaluated"},
        ],
        "Your comments": [{"type": "Open", "Text": "Do you have any comments?"}],
    }
    return survey


def show_survey(questions_dict, user):
    survey = ss.StreamlitSurvey()
    titles = list(questions_dict.keys())
    number_of_pages = len(titles)
    pages = survey.pages(
        number_of_pages, progress_bar=True, on_submit=lambda: st.success("Submitted!")
    )
    with pages:
        for p in range(number_of_pages):
            if pages.current == p:
                st.write(titles[p])
                questions_list = questions_dict[titles[p]]
                for question in questions_list:
                    if question["type"] == "Likert":
                        survey.select_slider(
                            question["Text"],
                            options=["-3", "-2", "-1", "1", "2", "3"],
                            id=question["Text"],
                        )
                    elif question["type"] == "Open question":
                        survey.text_input(question["Text"], id=question["Text"])
                    elif question["type"] == "Multiple choice":
                        survey.multiselect(
                            question["Text"],
                            options=question["Options"],
                            id=question["Text"],
                        )
        output = json.loads(survey.to_json())
        output.update({"user": user})
        output.update({"datetime": datetime.datetime.now()})
        return output


def add_question():
    question_theme = st.text_input(label="Question theme", key="newtheme")
    question_text = st.text_input(label="Question")
    question_type = st.radio(
        label="Type", options=["Likert", "Open question", "Multiple choice"]
    )
    st.write("Add up to 5 choices (ignored if not Multiple choice question)")
    choices = [""] * 5
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            choices[i] = st.text_input(f"Answer #{i+1}", key=f"answer{i}")
    question = {"type": question_type, "Text": question_text}
    if question_type == "Multiple choice":
        question["Options"] = [x for x in choices if x != ""]
    return question_theme, question


def show_temporary_survey(survey_dict):
    if survey_dict is None or not survey_dict:
        st.write("Empty survey, please add a question.")
    else:
        for theme in survey_dict.keys():
            st.write(f"**{theme}**")
            for questions in survey_dict[theme]:
                if questions["type"] == "Multiple choice":
                    tmp = f"- {questions['Text']}: Multiple choice\n"
                    for choice in questions["Options"]:
                        tmp += f"    - {choice}\n"
                    st.write(tmp)
                else:
                    st.write(f"- {questions['Text']}: {questions['type']}")


def create_survey(survey_dict={}):
    st.header("Create survey")
    with st.form("New question", clear_on_submit=True):
        theme, question = add_question()
        if st.form_submit_button("Confirm question"):
            if theme not in survey_dict:
                survey_dict[theme] = []
            survey_dict[theme].append(question)
    return survey_dict
