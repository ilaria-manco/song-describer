import pandas as pd
import streamlit as st

from annotation_tool.backend.models import get_leaderboard_counts

ANNOTATION_SCORE_FACTOR = 5
EVALUATION_SCORE_FACTOR = 1


def show():
    st.header("📊 Leaderboard")

    st.dataframe(get_leaderboard_dataframe(), use_container_width=True)

    prize_info = """
    ### Competition 🏆

    If you contribute to Song Describer, you'll also have a chance to win one of our prizes!

    As a way to say thank you for your time and effort, we are offering gift vouchers
    to the 3 users with the highest overall score.

    The vouchers can be spent on the [Abbey Road Studios](https://shop.abbeyroad.com/) online store and their
    value is:
    * 🥇 1st place: £100
    * 🥈 2nd place: £60
    * 🥉 3rd place: £40 

    The competition opens on 23/11/2022 and ends on 31/01/2023 AOE.

    #### How do I enter the competition?
    All users contributing to Song Describer while the competition is running will automatically be considered
    participants. 
    
    #### How are contributions evaluated?
    You will be awarded points every time you complete an annotation or evaluation. 
    The overall contribution score is computed as follows:
    * 5 points for every annotation
    * 1 point for every evaluation

    If you'd like to save your progress and come back to Song Describer later on, you can log back onto 
    your profile by providing your unique user ID. If you're unable to provide your user ID, you will 
    not be able to recover your profile and you'll lose your progress.

    If you'd like to publicly track your progress on the leaderboard, you can also choose a nickname
    when you create your profile. 

    #### How do I claim my prize?
    If you're one of the top 3 ranked contributors on our leaderboard when the competition ends, you 
    can claim your prize by emailing your unique user ID to [i.manco@qmul.ac.uk](mailto:i.manco@qmul.ac.uk) 
    by 31/02/2023. Please note, if you cannot provide your user ID, we will not be able to verify your
    contributions and you won't be able to claim your prize.

    We will check that your contributions adhere to the annotation guidelines outlined on this platform
    and we reserve the right to refuse to award the prize if we find, at our sole discretion, that the 
    guidelines were not followed.
    """

    st.write(prize_info)


def get_leaderboard_dataframe():
    data = get_leaderboard_counts()
    captions_written_column = "Annotations"
    captions_evaluated_column = "Evaluations"
    name_column = "Nickname"
    score_column = "Score"
    df = pd.DataFrame(
        data,
        columns=[name_column, captions_written_column, captions_evaluated_column],
    )
    df[score_column] = (
        ANNOTATION_SCORE_FACTOR * df[captions_written_column]
        + EVALUATION_SCORE_FACTOR * df[captions_evaluated_column]
    )
    df[name_column] = df[name_column].fillna("Anonymous user")
    sorted_df = df.sort_values(score_column, ascending=False, ignore_index=True)
    sorted_df.index += 1  # index start at 1 not zero for nicer leaderboard
    return sorted_df


if __name__ == "__main__":
    show()
