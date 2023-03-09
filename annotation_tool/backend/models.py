import logging
from datetime import date, datetime
from typing import Optional, List, Union, Tuple

import streamlit as st
from sqlalchemy import func, text, not_
from sqlalchemy.orm import aliased
from sqlalchemy_utils import database_exists, create_database
from sqlmodel import Field, SQLModel, Session, create_engine, select, Relationship

from annotation_tool.backend.music import (
    get_track_info,
    Track,
    get_random_track_with_weights,
)


def get_session():
    engine = get_engine()
    return Session(engine)


def add_to_db(obj: SQLModel) -> None:
    with get_session() as session:
        session.add(obj)
        session.commit()
        session.refresh(obj)


def get_all(cls) -> list:
    engine = get_engine()
    with Session(engine) as session:
        results = session.exec(select(cls))  # type: ignore
        return results.all()


class Annotation(SQLModel, table=True):
    __tablename__: str = "annotations"
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    familiarity: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    track_id: str

    user_id: str = Field(foreign_key="users.id")
    user: "User" = Relationship(back_populates="annotations")

    comments: str

    evaluations: List["Evaluation"] = Relationship(back_populates="annotation")

    @classmethod
    def get_annotations_for_evaluation(
        cls, user_id: str, max_evaluations: int
    ) -> Optional["Annotation"]:
        """Select a random row filtered by user id that has fewer evaluations than a
        specified limit.

        Only annotations are selected that
          1) were not done by a specific user identified by user_id
          2) have less than max_evaluations associated entries in the evaluation table
          3) are not already evaluated by the user

        :param user_id: the user id used to filter the annotations
        :param max_evaluations: the limit for the number of evaluations
        :return: An instance of Annotation or None
        """
        engine = get_engine()
        with Session(engine) as session:
            evaluations_incomplete = (
                select(Evaluation.annotation_id)
                .group_by(Evaluation.annotation_id)
                .having(func.count(Evaluation.id) < max_evaluations)
            )
            evaluations_alias = aliased(Evaluation)
            evaluation_by_user = select(Evaluation).where(
                Evaluation.user_id == user_id,
                evaluations_alias.annotation_id == Evaluation.annotation_id,
            )
            evaluations_not_by_user = select(evaluations_alias.annotation_id).where(
                not_(evaluation_by_user.exists()),  # not already evaluated by user
                evaluations_alias.annotation_id.not_in(  # annotation not by user
                    select(cls.id).where(cls.user_id == user_id)
                ),
            )
            annotations_unevaluated_and_not_by_user = select(cls.id).where(
                cls.user_id != user_id, cls.id.not_in(select(Evaluation.annotation_id))
            )
            results = session.exec(
                annotations_unevaluated_and_not_by_user.union(
                    evaluations_incomplete.intersect(evaluations_not_by_user)
                ).limit(1)
            )
            maybe_annotation_id = results.scalar_one_or_none()
            if maybe_annotation_id is not None:
                results = session.exec(select(cls).where(cls.id == maybe_annotation_id))
                return results.one()
            else:
                return None


class Evaluation(SQLModel, table=True):
    __tablename__: str = "evaluations"
    id: Optional[int] = Field(default=None, primary_key=True)
    rating: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    annotation_id: int = Field(foreign_key="annotations.id")
    annotation: Annotation = Relationship(back_populates="evaluations")

    user_id: str = Field(foreign_key="users.id")
    user: "User" = Relationship(back_populates="evaluations")


class SkippedTrack(SQLModel, table=True):
    __tablename__: str = "skippedtracks"
    id: Optional[int] = Field(default=None, primary_key=True)
    track_id: str
    user_id: str = Field(foreign_key="users.id")
    comments: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class User(SQLModel, table=True):
    __tablename__: str = "users"
    id: str = Field(primary_key=True)
    created: datetime = Field(default_factory=datetime.utcnow)
    age_group: Optional[int]
    country: Optional[str]
    english_level: Optional[int]

    music_doing: Optional[int]
    music_writing: Optional[int]
    music_reading: Optional[int]
    nickname: Optional[str] = Field(sa_column_kwargs={"unique": True})

    annotations: list[Annotation] = Relationship(back_populates="user")
    evaluations: list[Evaluation] = Relationship(back_populates="user")

    @classmethod
    def get_by_id(cls, _id) -> Optional["User"]:
        with get_session() as session:
            results = session.exec(select(cls).where(cls.id == _id))
            return results.one_or_none()

    def get_all_seen_track_ids(self):
        annotated = select(Annotation.track_id).where(Annotation.user_id == self.id)
        skipped = select(SkippedTrack.track_id).where(SkippedTrack.user_id == self.id)
        with get_session() as session:
            results = session.exec(annotated.union(skipped))
            return results.scalars().all()

    def get_annotation_count(self):
        annotated_count = select(func.count(Annotation.track_id)).where(
            Annotation.user_id == self.id
        )
        with get_session() as session:
            result = session.exec(annotated_count)
            return result.one()


def get_user_annotation_count(user_id: str) -> int:
    user = User.get_by_id(user_id)
    return user.get_annotation_count()


def get_leaderboard_counts(
    start_date: Union[date, datetime, None] = datetime.min, end_date: Union[date, datetime, None] = datetime.max
):
    annotation_counts = (
        select(Annotation.user_id, User.nickname, func.count(Annotation.id))
        .join(User)
        .filter(Annotation.timestamp >= start_date, Annotation.timestamp <= end_date)
        .group_by(
            Annotation.user_id,
            User.nickname,
        )
    )
    evaluation_counts = (
        select(Evaluation.user_id, User.nickname, func.count(Evaluation.id))
        .join(User)
        .filter(Evaluation.timestamp >= start_date, Evaluation.timestamp <= end_date)
        .group_by(
            Evaluation.user_id,
            User.nickname,
        )
    )
    with get_session() as session:
        annotations_results = session.exec(annotation_counts).all()
        evaluations_results = session.exec(evaluation_counts).all()
    annotation_counts = {user_id: count for user_id, _, count in annotations_results}
    evaluation_counts = {user_id: count for user_id, _, count in evaluations_results}
    annotation_nicknames = {
        user_id: nickname for user_id, nickname, _ in annotations_results
    }
    evaluations_nicknames = {
        user_id: nickname for user_id, nickname, _ in evaluations_results
    }
    all_nicknames = annotation_nicknames | evaluations_nicknames
    results = [
        (
            all_nicknames[_id],
            annotation_counts.get(_id, 0),
            evaluation_counts.get(_id, 0),
        )
        for _id in all_nicknames
    ]
    return results


def get_track_for_annotation(
    user_id: str, annotation_limit: int = 5
) -> Optional[Track]:
    user = User.get_by_id(user_id)
    all_user_seen_tracks = user.get_all_seen_track_ids()
    tracks_above_annotation_limit = get_tracks_at_annotation_limit(annotation_limit)
    return get_random_track_with_weights(
        exclude=set(all_user_seen_tracks + tracks_above_annotation_limit)
    )


def get_tracks_at_annotation_limit(annotation_limit: int) -> list[str]:
    with get_session() as session:
        result = session.exec(
            select(Annotation.track_id)
            .group_by(Annotation.track_id)
            .having(func.count(Annotation.id) >= annotation_limit)
        )
        return result.all()


def get_annotated_track_for_evaluation(
    user_id, max_evaluations=3
) -> Union[Tuple[Track, Annotation], Tuple[None, None]]:
    annotation = Annotation.get_annotations_for_evaluation(user_id, max_evaluations)
    track = get_track_info(annotation.track_id) if annotation else None
    return track, annotation


@st.experimental_singleton
def get_engine():
    logging.info("Creating DB engine")
    engine = create_engine(st.secrets["db"]["url"])
    return engine


def create_tables(db_user=None):
    engine = get_engine()
    if not database_exists(engine.url):
        logging.info("Database does not exist, creating it")
        create_database(engine.url)
    logging.info("Creating tables")
    SQLModel.metadata.create_all(engine)
    if db_user:
        with get_session() as sess:
            sess.execute(
                text(
                    f"""
                GRANT ALL ON SEQUENCE public.annotations_id_seq TO {db_user};
                GRANT ALL ON SEQUENCE public.evaluations_id_seq TO {db_user};
                GRANT ALL ON SEQUENCE public.skippedtracks_id_seq TO {db_user};
                GRANT INSERT, SELECT, UPDATE ON TABLE public.annotations TO {db_user};
                GRANT INSERT, SELECT, UPDATE ON TABLE public.evaluations TO {db_user};
                GRANT INSERT, SELECT, UPDATE ON TABLE public.skippedtracks TO {db_user};
                GRANT INSERT, SELECT, UPDATE ON TABLE public.users TO {db_user};
                """
                )
            )
            sess.commit()


def delete_tables():
    engine = get_engine()
    logging.warning("Deleting tables!")
    SQLModel.metadata.drop_all(engine)
