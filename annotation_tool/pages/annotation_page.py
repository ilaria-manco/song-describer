import logging
import string

import streamlit as st

from annotation_tool.backend.config import get_annotation_limit
from annotation_tool.backend.models import (
    Annotation,
    add_to_db,
    get_track_for_annotation,
    SkippedTrack,
    get_user_annotation_count,
)
from annotation_tool.components.custom_audio import get_trimmed_audio_element
from annotation_tool.pages.flow_control import USER_ID_KEY

CAPTION_KEY = "caption_key"
CURRENT_TRACK = "current_track"
FAMILIARITY_KEY = "familiarity_key"
SKIP_CHECKBOX = "skip_checkbox"
TRACK_ISSUE_KEY = "track_issue_key"

FAMILIARITY_OPTIONS = {
    0: "Not familiar at all",
    1: "Quite familiar",
    2: "Very familiar",
}


def show():
    st.header(
        """
        ✏️ Let's get captioning!
        """
    )

    st.markdown(
        """
        In this task, you'll listen to a music track (up to 2 minutes) and write a short description of it.
        """
    )

    st.warning(
        """
        🔊 Before pressing play, please make sure the volume of your headphones or speakers is set to a comfortable level. 
        

        🚩 Note that some tracks may have lyrics with sensitive content. If you don't feel comfortable listening to a track, you can skip it by clicking the button at the bottom of this page.
        """
    )

    user_id = st.session_state[USER_ID_KEY]
    if CURRENT_TRACK not in st.session_state:
        annotation_limit = get_annotation_limit()
        track = get_track_for_annotation(user_id, annotation_limit)
        st.session_state[CURRENT_TRACK] = track
    else:
        track = st.session_state[CURRENT_TRACK]

    if track is None:
        st.info(
            "You listened to all the tracks we have prepared for you today. "
            "Please come back later or choose a different task!"
        )
    else:
        with st.form("annotation", clear_on_submit=True):
            get_trimmed_audio_element(track.audio_url)

            with st.expander("Track info"):
                st.caption(track.attribution)
                st.caption(track.license_text)

            st.subheader("How would you describe this track in **one sentence**?")

            with st.expander(
                label="📋 Instructions",
                expanded=(get_user_annotation_count(user_id) == 0),
            ):
                st.write(
                    """
                    Write one sentence that describes the track you just listened to: 
                    focus on descriptive text which conveys the *overall* content of this track only.
                    * Do:
                        * Write one full sentence
                        * Use at least 8 words
                        * Include things like: genre, mood, instrumentation, ideal listening situation, emotions it evokes, etc.
                    * Don't:
                        * Simply provide a sequence of tags
                        * Use swear words or other offensive language
                        * Refer to other songs or artists you may know
                        * Mention personal events or experiences
                    """
                )
            
            with st.expander(
                label="💬  Need some examples?",
                expanded=False,
            ):
                st.write(
                    """
                    This is what some valid music captions would look like:
                    * *This catchy song features an irresistible guitar-pop jangle, a giddy wordless hook and soft backing vocals*
                    * *This track starts with a man signing with a robotic register, before a rubbery, slightly sinister synth counters*
                    * *Wobbly basslines and EDM-style drops make this track perfect for the dancefloor*
                    * *Slow-paced R&B ballad with elegant vocals and elements of pop music*
                    * *An ambient track that evokes the stillness of a remote nordic island*
                    * *A pop song that employs a worldbeat element through its heavy use of percussion*
                    Note that these are just some examples, they do NOT describe this specific track and are not exhaustive.
                    """
                )

            caption = st.text_area(
                "✍️",
                key=CAPTION_KEY,
                max_chars=512,
            )
            caption_error_container = st.empty()

            st.write("---")

            st.subheader("How familiar are you with this kind of music?")

            st.select_slider(
                "Rate your familiarity:",
                FAMILIARITY_OPTIONS.keys(),
                format_func=lambda i: FAMILIARITY_OPTIONS[i],
                key=FAMILIARITY_KEY,
            )

            st.write("#")

            col1, col2 = st.columns([4.2, 1])

            with col1:
                submitted = st.form_submit_button(
                    "Submit",
                    on_click=submit_annotation,
                    kwargs={
                        "track_id": track.id,
                    },
                    type="primary",
                )

            with col2:
                st.form_submit_button(
                    label="Skip this track", on_click=skip_track, args=[track.id]
                )
            with st.expander("Found an issue with this track?"):
                st.text_input("Report it below", key=TRACK_ISSUE_KEY, max_chars=512)
                st.form_submit_button(
                    "Report issue and skip this track",
                    on_click=skip_track,
                    args=[track.id],
                )

            if submitted:
                logging.debug(f"Submitted the following caption: {caption}")
                if not caption.strip():
                    caption_error_container.error(
                        "Please provide a caption before submitting"
                    )
                elif not _is_caption_long_enough(caption):
                    caption_error_container.warning(
                        "Your caption looks a bit too short, want to try again?"
                    )


def _clear_current_track():
    if CURRENT_TRACK in st.session_state:
        del st.session_state[CURRENT_TRACK]


def _is_caption_long_enough(text: str) -> bool:
    text = text.translate(str.maketrans("", "", string.punctuation))
    return len(text.split()) >= 8


def submit_annotation(track_id):
    caption: str = st.session_state[CAPTION_KEY]
    familiarity: int = st.session_state[FAMILIARITY_KEY]
    track_issue_comments: str = st.session_state[TRACK_ISSUE_KEY]
    user_id = st.session_state[USER_ID_KEY]
    logging.debug(f"on_click {caption=} {familiarity=}")

    if _is_caption_long_enough(caption) and familiarity != -1:
        annotation = Annotation(
            text=caption.strip(),
            track_id=track_id,
            user_id=user_id,
            familiarity=familiarity,
            comments=track_issue_comments,
        )
        add_to_db(annotation)
        st.balloons()
        logging.info(f"Added {annotation}")
        _clear_current_track()

    else:
        logging.debug("Setting session state")
        st.session_state[CAPTION_KEY] = caption
        st.session_state[FAMILIARITY_KEY] = familiarity


def skip_track(track_id):
    track_issue_comments: str = st.session_state[TRACK_ISSUE_KEY]
    user_id = st.session_state[USER_ID_KEY]
    logging.debug(f"{track_issue_comments=}")
    skipped_track = SkippedTrack(
        track_id=track_id,
        user_id=user_id,
        comments=track_issue_comments,
    )
    add_to_db(skipped_track)
    _clear_current_track()
