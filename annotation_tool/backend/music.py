from dataclasses import dataclass
from typing import Optional

import pandas as pd
import streamlit as st

from annotation_tool.backend.config import get_track_tsv_file


@dataclass(frozen=True)
class Track:
    """Class for bundling information of a Creative Commons track."""

    id: str
    audio_url: str
    attribution: str
    license_text: str


@st.experimental_memo
def load_track_tsv(tsv_file=None) -> pd.DataFrame:
    if tsv_file is None:
        tsv_file = get_track_tsv_file()
    return pd.read_csv(tsv_file, delimiter="\t", converters={"TRACK_ID": str})


@st.experimental_memo
def load_jamendo_stats_tsv(tsv_file="data/jamendo_stats.tsv") -> pd.DataFrame:
    df = pd.read_csv(tsv_file, delimiter="\t", converters={"track": str})
    return df.set_index("track")


def get_random_track(exclude=None) -> Optional[Track]:
    if exclude is None:
        exclude = []
    tracks = load_track_tsv()
    tracks: pd.DataFrame = tracks[~tracks["TRACK_ID"].isin(exclude)]
    if not tracks.empty:
        track_id, attribution, license_text = tracks.sample().values[0]
        return Track(str(track_id), audio_url(track_id), attribution, license_text)
    else:
        return None


def get_random_track_with_weights(exclude=None) -> Optional[Track]:
    if exclude is None:
        exclude = []
    tracks = load_track_tsv()
    tracks = tracks.set_index("TRACK_ID")
    tracks: pd.DataFrame = tracks.drop(exclude)
    play_counts = load_jamendo_stats_tsv()["rate_listened_total"]
    if not tracks.empty:
        results = tracks.sample(weights=play_counts)
        attribution, license_text = results.values[0]
        track_id = results.index[0]
        return Track(str(track_id), audio_url(track_id), attribution, license_text)
    else:
        return None


def get_track_info(track_id) -> Track:
    tracks = load_track_tsv()
    entry = tracks[tracks["TRACK_ID"] == track_id]
    track_id, attribution, license_text = entry.values[0]
    return Track(track_id, audio_url(track_id), attribution, license_text)


def audio_url(audio_id):
    return f"https://mp3d.jamendo.com/?trackid={audio_id}&format=mp32#t=0,120"


if __name__ == "__main__":
    get_random_track_with_weights()
