from functools import partial

import streamlit as st

from annotation_tool.backend.models import get_leaderboard_counts
from annotation_tool.pages.faqs import FAQS_TEXT
from annotation_tool.pages.flow_control import (
    user_id_exists,
    set_user_id,
    RETURNING_USER_KEY,
)
from annotation_tool.pages.leaderboard import get_leaderboard_dataframe

INPUT_USER_ID_KEY = "input_user_id"


def draw_main_page(callback):
    st.header("Welcome to Song Describer! 👋")

    st.info(
        """
        Song Describer is a tool for crowdsourced collection of **music captions**,
        built by a team of researchers from Queen Mary University of London and
        Universitat Pompeu Fabra Barcelona.
        """
    )

    intro = """
    ###

    🎵 You will be asked to listen to some music and write a new description for it
    (✏️ *Annotation*) or evaluate an existing one (⚖️ *Evaluation*). Each task takes
    only a **few minutes**. You can complete either task as many times as you'd like. 

    ✍️ By contributing to Song Describer, you are helping us release the **first public
    dataset** of music captions. We really appreciate your help!

    ℹ️ We will only collect data you provide by submitting your answers and no other 
    personal information. To find out more about the project and how the data will 
    be used, read our FAQs below.

    """

    informed_consent = """
    ___ 
    📋 This survey is part of a research project being undertaken by Universal Music Group 
    International Limited (part of Universal Music Group), Queen Mary University of 
    London, and Universitat Pompeu Fabra (together the “Research Team”).
    
    By participating in this survey, you acknowledge and agree to the following:

    *	You must be aged 18 or over
    *   You are participating in an academic study, the results of which may or may not be published in an academic journal. 
    *   Your participation is voluntary and you are free to leave at any time
    *	All intellectual property rights which may arise or inure to you as a result of your participation in this survey are hereby assigned jointly, in full and in equal proportion to the members of the Research Team.
    *	By participating in this study, you agree to waive any moral rights of authorship that you may have in the responses that you provide in the survey to the extent permitted by law.
    *	The data collected by this survey is intended to be published and shall be freely available to all. The responses submitted by you shall not be attributable to you and your participation in the survey shall remain confidential.

    """

    returning_user_info = """
    ___
    # Have you been here before?
    """

    st.write(intro)

    with st.expander("❓ FAQs"):
        st.write(FAQS_TEXT)

    st.write(informed_consent)

    _, col3, _ = st.columns([2, 1, 2])
    col3.button(
        "Get started",
        on_click=callback,
        help="By clicking here, you confirm that you agree with the statements above.",
        type="primary",
    )

    st.write(returning_user_info)

    text_input_callback = partial(verify_user_id, callback)
    st.text_input(
        "Insert your unique User ID below and press Enter",
        key=INPUT_USER_ID_KEY,
        on_change=text_input_callback,
        max_chars=36,
        help="This is the 36-character ID generated when you create a new user profile. "
        "It looks like this: '8aa9fd14-1234-f1ec-9f59-9876abc54d32'",
    )

    st.write("---")
    with st.expander("📊 Leaderboard"):
        st.metric(
            label="Contributors so far",
            value=len(get_leaderboard_counts()),
        )
        st.dataframe(get_leaderboard_dataframe())


def verify_user_id(callback):
    input_user_id = st.session_state[INPUT_USER_ID_KEY]
    if user_id_exists(input_user_id):
        st.session_state[RETURNING_USER_KEY] = True
        set_user_id(input_user_id)
        callback()
    else:
        st.error("User ID not found")
