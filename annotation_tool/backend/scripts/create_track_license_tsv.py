from utils import read_file, read_lincense_file, write_file

PILOT = True

SPLIT_O_TEST_TSV = "data/autotagging-test.tsv"
AUDIO_LICENSES_FILE = "data/audio_licenses.txt"

PILOT_TRACK_IDS = [
    786782,
    356447,
    10565,
    11842,
    998030,
    1208084,
    1149726,
    49421,
    1288813,
    497844,
    1408979,
    844690,
    1079319,
    381459,
    1354434,
    1410638,
    1063336,
    936445,
    692953,
    1128085,
]


if __name__ == '__main__':
    if PILOT:
        tsv_output = "data/pilot_tracks.tsv"
        tracks = PILOT_TRACK_IDS
    else:
        tsv_output = "data/split_0_test_tracks.tsv"
        tracks = read_file(SPLIT_O_TEST_TSV)
    licenses = read_lincense_file(AUDIO_LICENSES_FILE)

    write_file(tracks, licenses, tsv_output)
