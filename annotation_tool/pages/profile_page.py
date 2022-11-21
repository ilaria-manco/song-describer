import logging
import random
from typing import Callable

import sqlalchemy.exc
import streamlit as st
from wonderwords import RandomWord

from annotation_tool.backend.models import User, add_to_db
from annotation_tool.pages.flow_control import USER_ID_KEY

RANDOM_USERNAME = "UP_random_username"

NICKNAME_INPUT = "nickname_input"


def show(callback):
    user_id = st.session_state[USER_ID_KEY]
    if user_id is None:
        logging.error("There is no user-id generated, that should not happen")

    user = User.get_by_id(user_id)
    st.header("You're all set!")

    st.subheader("Your unique user ID 👇")

    st.code(str(user_id), language=None)

    st.write(
        "ℹ️ You'll need it if you come back and want to continue annotating without creating a new user profile."
    )

    subject = "My Song Describer User ID"
    st.write(
        f"""
        Please do not share this with anyone. Save it somewhere safe or [email it to yourself](<mailto:?subject={subject}&body={user_id}>).
        """
    )

    st.write("---")

    random_nickname = _get_random_nickname()
    nickname = st.text_input(
        "Enter your leaderboard nickname (optional):",
        max_chars=32,
        key=NICKNAME_INPUT,
        help="This nickname will be visible to other users in the leaderboard.",
    )
    if nickname and user.nickname != nickname:
        nickname_error = _store_nickname(user_id)
        if nickname_error:
            st.error("This nickname is already taken!")

    user = User.get_by_id(user_id)  # Re-fetch user from database since we changed it
    current_nickname = (
        "You currently don't have a nickname."
        if not user.nickname
        else f"Your nickname is: *{user.nickname}*."
    )
    st.caption(
        " ".join(
            [current_nickname, f"Need inspiration? How about: `{random_nickname}`"]
        )
    )

    _, col1, _ = st.columns([2, 1, 2])
    col1.button(
        "Continue",
        on_click=advance_if_nickname_stored,
        kwargs={"user_id": user_id, "callback": callback},
        type="primary",
    )


def _get_nickname() -> str:
    nickname = st.session_state[NICKNAME_INPUT]
    return nickname.strip()


def _store_nickname(user_id: str) -> bool:
    logging.debug("In _store_nickname")
    nickname = _get_nickname()
    user = User.get_by_id(user_id)
    user.nickname = nickname
    try:
        add_to_db(user)
    except sqlalchemy.exc.IntegrityError:
        return True
    return False


def advance_if_nickname_stored(user_id: str, callback: Callable[[], None]):
    logging.debug("In advance_if_nickname_stored")
    nickname_input = _get_nickname()
    user = User.get_by_id(user_id)
    if not nickname_input or nickname_input == user.nickname:
        logging.debug("Callback! ")
        callback()
    else:
        nickname_error = _store_nickname(user_id)
        if not nickname_error:
            callback()


def _get_random_nickname(cache_to_session_state=False) -> str:
    if cache_to_session_state and RANDOM_USERNAME in st.session_state:
        return st.session_state[RANDOM_USERNAME]
    else:
        word_gen = _get_random_word_generator()
        separator = random.choice(["_", "-", "."])
        random_nickname = separator.join(
            word.title() if round(random.random()) else word.lower()
            for word in [
                word_gen.word(word_max_length=10, include_categories=["adjective"]),
                word_gen.word(word_max_length=10, include_categories=["noun"]),
            ]
        )
        if cache_to_session_state:
            st.session_state[RANDOM_USERNAME] = random_nickname
    return random_nickname


@st.experimental_singleton
def _get_random_word_generator() -> RandomWord:
    return RandomWord()
