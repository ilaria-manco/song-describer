import streamlit as st

from annotation_tool.backend.config import get_evaluation_limit
from annotation_tool.backend.models import (
    get_annotated_track_for_evaluation,
    Evaluation,
    Annotation,
    add_to_db,
)
from annotation_tool.components.custom_audio import get_trimmed_audio_element
from annotation_tool.pages.flow_control import USER_ID_KEY

RATING_KEY = "rating"
ACCEPTED_KEY = "accepted"
CURRENT_EVALUATION_TRACK = "current_evaluation_track"


def show():
    st.header("⚖️ Evaluation")
    st.write(
        """
        In this task, you'll first be shown a piece of text and asked whether it is a valid caption.
        """
    )
    st.info(
        """
        A caption is valid if it's a comprehensible and grammatically correct 
        English sentence describing a piece of music.
        """, icon="ℹ️"
    )
    st.write(
        """
        If the caption is valid, you'll then be asked to listen to a music track and rate how well 
        the caption describes it. 
        """
    )

    if CURRENT_EVALUATION_TRACK not in st.session_state:
        evaluation_limit = get_evaluation_limit()
        track, annotation = get_annotated_track_for_evaluation(
            st.session_state[USER_ID_KEY],
            evaluation_limit,
        )
        st.session_state[CURRENT_EVALUATION_TRACK] = (track, annotation)
    else:
        track, annotation = st.session_state[CURRENT_EVALUATION_TRACK]

    if annotation is None:
        st.write("There are currently no captions to review. Please, come back later.")
    else:
        st.subheader("Is the caption below valid?")
        with st.expander("Caption", expanded=True):
            st.text(annotation.text)

        _, col2, col3, _ = st.columns([3, 1, 1, 3])
        with col3:
            st.button(
                label="No 🚫",
                on_click=submit_evaluation,
                kwargs={
                    "annotation": annotation,
                    "accepted": False,
                },
            )
        with col2:
            accepted = st.button(
                label="Yes ✅",
            )
        if accepted:
            with st.form("rating_form", clear_on_submit=True):
                st.subheader("How well does it describe this track?")

                get_trimmed_audio_element(track.audio_url)
                with st.expander("Track info"):
                    st.caption(track.attribution)
                    st.caption(track.license_text)

                st.select_slider(
                    label="Rate the caption from 1 to 5",
                    options=range(1, 6),
                    format_func=lambda i: "⭐" * i,
                    key=RATING_KEY,
                )

                _, col2, _ = st.columns([2.1, 1, 2])
                with col2:
                    st.form_submit_button(
                        label="Submit",
                        on_click=submit_evaluation,
                        kwargs={
                            "annotation": annotation,
                            "accepted": True,
                        },
                        type="primary",
                    )


def _clear_current_evaluation_track():
    if CURRENT_EVALUATION_TRACK in st.session_state:
        del st.session_state[CURRENT_EVALUATION_TRACK]


def submit_evaluation(annotation: Annotation, accepted: bool):
    user_id = st.session_state[USER_ID_KEY]
    if not accepted:
        rating = 0
    else:
        rating = st.session_state[RATING_KEY]
    evaluation = Evaluation(rating=rating, annotation_id=annotation.id, user_id=user_id)
    add_to_db(evaluation)
    _clear_current_evaluation_track()
