import logging
from typing import Optional
from uuid import uuid4

import streamlit as st

from annotation_tool.backend.models import User

USER_ID_KEY = "user_id"
ACTIVE_PAGE_KEY = "active_page"
RETURNING_USER_KEY = "returning_user"


def init_session_state():
    if ACTIVE_PAGE_KEY not in st.session_state:
        st.session_state[ACTIVE_PAGE_KEY] = "Home"
        if _check_query_parameter_user_id() is not None:
            st.session_state[RETURNING_USER_KEY] = True
            advance_page()
    if RETURNING_USER_KEY not in st.session_state:
        st.session_state[RETURNING_USER_KEY] = False


def advance_page(requested_page: Optional[str] = None):
    logging.debug(
        f"Current Page: {st.session_state[ACTIVE_PAGE_KEY]}, {requested_page=}"
    )
    ensure_user_id()
    if st.session_state[ACTIVE_PAGE_KEY] == "Home":
        if st.session_state[RETURNING_USER_KEY]:
            st.session_state[ACTIVE_PAGE_KEY] = "Annotation"
        else:
            st.session_state[ACTIVE_PAGE_KEY] = "User Info"
    elif st.session_state[ACTIVE_PAGE_KEY] == "User Info":
        st.session_state[ACTIVE_PAGE_KEY] = "Profile"
    elif st.session_state[ACTIVE_PAGE_KEY] == "Profile":
        st.session_state[ACTIVE_PAGE_KEY] = "Annotation"
        st.session_state[RETURNING_USER_KEY] = True
    if requested_page:
        st.session_state[ACTIVE_PAGE_KEY] = requested_page


def get_active_page() -> str:
    return st.session_state[ACTIVE_PAGE_KEY]


def sidebar_visible():
    active_page = get_active_page()
    return active_page not in {"Home", "User Info", "Profile"}


# TODO: maybe add user object to st.session_state to be accesses from individual pages


def ensure_user_id():
    if USER_ID_KEY not in st.session_state:
        logging.debug("No user_id in session state, setting or generating...")
        user_id = _get_user_id()
        set_user_id(user_id)
    elif _check_query_parameter_user_id() is None:
        set_user_id(st.session_state[USER_ID_KEY])


def user_id_exists(user_id: str) -> bool:
    user = User.get_by_id(user_id)
    return user is not None


def _get_user_id() -> str:
    """Get the user id from the query parameters or generate a new one.

    Check if user id present in query parameters. if yes: verify and return valid id
    If not in query parameters or not valid generate and return a new (unique) UUID

    :return: str of a UUID
    """
    qp_user_id = _check_query_parameter_user_id()
    if qp_user_id:
        logging.debug("Setting user id from query params")
        user_id = qp_user_id
    else:
        logging.debug("Generating a new user id!")
        user_id = uuid4()

    return str(user_id)


def _check_query_parameter_user_id() -> Optional[str]:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    query_params = st.experimental_get_query_params()
    logging.info(f"{query_params=}")
    qp_user_id = query_params.get(USER_ID_KEY)
    if qp_user_id and user_id_exists(qp_user_id[0]):
        return qp_user_id[0]  # query parameters are a list: take the first item
    else:
        return None


def set_user_id(user_id: str):
    st.session_state[USER_ID_KEY] = user_id
    query_params = st.experimental_get_query_params()
    query_params[USER_ID_KEY] = user_id
    st.experimental_set_query_params(**query_params)
