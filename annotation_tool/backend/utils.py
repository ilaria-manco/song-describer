"""Code adapted from https://github.com/MTG/mtg-jamendo-dataset/blob/master/scripts/commons.py"""

import csv

import streamlit


@streamlit.experimental_singleton
def get_country_options_dict():
    with open("data/countries.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        return {row["alpha-2"]: row["name"] for row in reader}


def get_id(value):
    return int(value.split("_")[1])


def read_file(tsv_file):
    tracks = {}

    with open(tsv_file) as fp:
        reader = csv.reader(fp, delimiter="\t")
        next(reader, None)  # skip header
        for row in reader:
            track_id = get_id(row[0])
            tracks[track_id] = {}

    return tracks


def read_lincense_file(txt_file):
    with open(txt_file) as f:
        lines = f.read().splitlines()

    track_paths = [lines[i] for i in range(0, len(lines), 4)]
    attributions = [lines[i].split("from Jamendo")[0] for i in range(1, len(lines), 4)]
    licenses = [lines[i] for i in range(2, len(lines), 4)]

    tracks = {}

    for i, track_path in enumerate(track_paths):
        track_id = int(track_path.split("/")[1].replace(".mp3", ""))
        tracks[track_id] = {
            "attribution": attributions[i],
            "license": licenses[i],
        }

    return tracks


def write_file(tracks, licenses, tsv_file):
    rows = []
    for track_id in tracks:
        row = [
            track_id,
            licenses[track_id]["attribution"],
            licenses[track_id]["license"],
        ]

        rows.append(row)

    with open(tsv_file, "w") as fp:
        writer = csv.writer(fp, delimiter="\t")
        writer.writerow(["TRACK_ID", "ATTRIBUTION", "LICENSE"])
        for row in rows:
            writer.writerow(row)
