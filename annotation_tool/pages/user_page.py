import logging
from typing import Optional, Callable

import streamlit as st

from annotation_tool.backend.utils import get_country_options_dict
from annotation_tool.backend.models import User, add_to_db
from annotation_tool.pages.flow_control import USER_ID_KEY

MUSIC_READING_INPUT = "music_reading_input"
MUSIC_WRITING_INPUT = "music_writing_input"
MUSIC_DOING_INPUT = "music_doing_input"
AGE_GROUP_INPUT = "age_group_input"
ENGLISH_INPUT = "english_input"
COUNTRY_INPUT = "country_input"

AGREEMENT_OPTIONS = {
    0: "Completely Disagree",
    1: "Strongly Disagree",
    2: "Disagree",
    3: "Neither Agree nor Disagree",
    4: "Agree",
    5: "Strongly Agree",
    6: "Completely Agree",
}

AGE_GROUPS = {
    -1: "",
    0: "18-24",
    1: "25-34",
    2: "35-44",
    3: "45-54",
    4: "55-64",
    5: "65+",
}

ENGLISH_OPTIONS = {
    0: "Yes",
    1: "More or less",
    2: "No",
}


def show(callback):
    user_id = st.session_state[USER_ID_KEY]
    if user_id is None:
        logging.error("There is no user-id generated, that should not happen")

    st.header("👤 Before we start...")

    user = User.get_by_id(user_id)
    logging.info(f"User: {user}")

    with st.form("user_info"):
        # TODO: streamline default options and get rid of redundant code

        st.radio(
            "Are you comfortable writing in English?",
            ENGLISH_OPTIONS.keys(),
            format_func=lambda i: ENGLISH_OPTIONS[i],
            index=list(ENGLISH_OPTIONS.keys()).index(user.english_level)
            if user is not None
            else 0,
            key=ENGLISH_INPUT,
        )
        st.write("---")

        st.selectbox(
            "How old are you?",
            AGE_GROUPS.keys(),
            format_func=lambda i: AGE_GROUPS[i],
            # a bit ugly, maybe we make index and value to be the same in AGE_GROUPS?
            index=list(AGE_GROUPS.keys()).index(user.age_group)
            if user is not None
            else 0,
            key=AGE_GROUP_INPUT,
        )
        country_options = {"": ""} | get_country_options_dict()

        st.selectbox(
            "Where do you live?",
            country_options.keys(),
            format_func=country_options.get,
            key=COUNTRY_INPUT,
        )
        st.write("---")

        st.subheader("How much do you agree or disagree with the following statements?")

        st.select_slider(
            "1. I spend a lot of my free time doing music-related activities",
            AGREEMENT_OPTIONS.keys(),
            format_func=lambda i: AGREEMENT_OPTIONS[i],
            value=user.music_doing if user is not None else 3,
            key=MUSIC_DOING_INPUT,
        )
        st.markdown("#")

        st.select_slider(
            "2. I enjoy writing about music, for example on blogs or social media",
            AGREEMENT_OPTIONS.keys(),
            format_func=lambda i: AGREEMENT_OPTIONS[i],
            value=user.music_writing if user is not None else 3,
            key=MUSIC_WRITING_INPUT,
        )
        st.markdown("#")

        st.select_slider(
            "3. I often read or search the internet for things related to music",
            AGREEMENT_OPTIONS.keys(),
            format_func=lambda i: AGREEMENT_OPTIONS[i],
            value=user.music_reading if user is not None else 3,
            key=MUSIC_READING_INPUT,
        )

        st.markdown("#")

        _, col_middle, _ = st.columns([2, 1, 2])
        col_middle.form_submit_button(
            "Submit",
            on_click=submit_user_form,
            args=[
                callback,
                user,
                user_id,
            ],
            type="primary",
        )


def submit_user_form(
    done_callback: Callable[[], None],
    user: Optional[User],
    user_id: str,
):
    country: int = st.session_state[COUNTRY_INPUT]
    english_level: int = st.session_state[ENGLISH_INPUT]
    age_group: int = st.session_state[AGE_GROUP_INPUT]
    music_doing: int = st.session_state[MUSIC_DOING_INPUT]
    music_writing: int = st.session_state[MUSIC_WRITING_INPUT]
    music_reading: int = st.session_state[MUSIC_READING_INPUT]

    logging.debug(f"{age_group=} {music_doing=} {music_writing=} {music_reading=}")
    if age_group >= 0 and country != "":
        if user is None:
            user = User(
                id=user_id,
                age_group=age_group,
                music_doing=music_doing,
                music_writing=music_writing,
                music_reading=music_reading,
                english_level=english_level,
                country=country,
            )
        else:
            user.age_group = age_group
            user.music_doing = music_doing
            user.music_writing = music_writing
            user.music_reading = music_reading
            user.english_level = english_level

        add_to_db(user)
        done_callback()
    else:
        st.error("Please fill in all missing fields!")
