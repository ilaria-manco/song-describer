"""The main app for the music caption annotation tool."""
from functools import partial

import streamlit as st

from annotation_tool.pages import (
    annotation_page,
    evaluation_page,
    leaderboard,
    profile_page,
    user_page,
    welcome,
    faqs,
)
from annotation_tool.pages.flow_control import (
    get_active_page,
    init_session_state,
    advance_page,
    sidebar_visible,
    USER_ID_KEY,
)
from annotation_tool.backend.models import get_user_annotation_count

ABOUT_MD = "A tool for crowdsourced collection of music captions."


def set_up_sidebar():
    active_page = get_active_page()
    st.sidebar.title("Song Describer")
    st.sidebar.markdown(ABOUT_MD)
    st.sidebar.header("Choose a task:")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.button(
            "✏️ Annotation",
            disabled=active_page == "Annotation",
            on_click=advance_page,
            args=["Annotation"],
        )
    with col2:
        st.button(
            "🔎 Evaluation",
            disabled=active_page == "Evaluation",
            on_click=advance_page,
            args=["Evaluation"],
        )
    st.sidebar.header("Go to:")
    st.sidebar.button(
        "👤 Profile",
        disabled=active_page == "Profile",
        on_click=advance_page,
        args=["Profile"],
    )
    st.sidebar.button(
        "❓ FAQs",
        disabled=active_page == "FAQs",
        on_click=advance_page,
        args=["FAQs"],
    )
    st.sidebar.button(
        "📊 Leaderboard",
        disabled=active_page == "Leaderboard",
        on_click=advance_page,
        args=["Leaderboard"],
    )

    annotation_count = get_user_annotation_count(st.session_state[USER_ID_KEY])

    track_text = "tracks"
    emoji = "🎉"
    if annotation_count == 1:
        track_text = "track"
    elif annotation_count == 0:
        emoji = ""

    st.sidebar.write("""---""")
    st.sidebar.write(
        """You have annotated {} {} so far {}""".format(
            annotation_count, track_text, emoji
        )
    )

    st.sidebar.write("""---""")
    st.sidebar.info(
        "Do you have any suggestions, feedback or questions for us? Get in touch: [i.manco@qmul.ac.uk](mailto:i.manco@qmul.ac.uk)", icon="📧"
    )


app_pages = {
    "Home": partial(welcome.draw_main_page, advance_page),
    "User Info": partial(user_page.show, advance_page),
    "Profile": partial(profile_page.show, advance_page),
    "Annotation": annotation_page.show,
    "Evaluation": evaluation_page.show,
    "Leaderboard": leaderboard.show,
    "FAQs": faqs.show,
}


def main():
    st.set_page_config(
        page_title="Song Describer",
        menu_items={
            "Get Help": None,
            "Report a bug": None,
            "About": ABOUT_MD,
        },
    )
    init_session_state()

    if sidebar_visible():
        set_up_sidebar()

    # Draw current page
    app_pages[get_active_page()]()


if __name__ == "__main__":
    main()
