import streamlit as st


@st.experimental_singleton
def get_track_tsv_file():
    default_tsv = "data/pilot_tracks.tsv"
    if music_config := st.secrets.get("music"):
        return music_config.get("tsv_file", default_tsv)
    else:
        return default_tsv


@st.experimental_singleton
def get_annotation_limit():
    return _get_limit("annotation", default_limit=5)


@st.experimental_singleton
def get_evaluation_limit():
    return _get_limit("evaluation", default_limit=3)


def _get_limit(key: str, default_limit):
    if music_config := st.secrets.get("limits"):
        return music_config.get(key, default_limit)
    else:
        return default_limit
