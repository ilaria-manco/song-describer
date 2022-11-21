from pathlib import Path
from typing import Type

import pandas as pd
from sqlmodel import SQLModel

from annotation_tool.backend.models import (
    get_all,
    User,
    Annotation,
    SkippedTrack,
    Evaluation,
)


def fetch_tables(data_models: list[Type[SQLModel]], out_base_path: Path):
    for data_model in data_models:
        results = get_all(cls=data_model)
        records = [i.dict() for i in results]
        try:
            df = pd.DataFrame.from_records(records, index="id")
        except:
            df = pd.DataFrame.from_records(records)
        df.to_pickle(
            out_base_path / f"{data_model.__tablename__}.pickle",
        )


if __name__ == "__main__":
    output_path = Path("./data_dump")
    output_path.mkdir(exist_ok=True)
    fetch_tables([User, Annotation, SkippedTrack, Evaluation], output_path)
