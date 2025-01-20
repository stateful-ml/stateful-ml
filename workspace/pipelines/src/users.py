from __future__ import annotations

from functools import partial

import numpy as np
import polars as pl
from prefect import task
from sqlalchemy import Connection
from sqlmodel import Session
from supabase import Client

from .config import config
from .runner import run_etl
from .schemas import Dataset
from .shared.data_models import EMBEDDING_SIZE, Users
from .util import by_chunks


def extract(client: Client, batch_size: int):
    result = client.table(config.source_users_table).select("id").execute()
    yield from map(pl.DataFrame, by_chunks(result.data, batch_size))


def transform(metadata: pl.DataFrame):
    return Dataset(
        np.zeros((len(metadata), EMBEDDING_SIZE)),
        metadata,
    )


def upload(dataset: Dataset, conn: Connection):
    with Session(conn) as session:
        # TODO: remove the silly overhead
        for embedding, metadata in zip(
            dataset.data,
            dataset.metadata.iter_rows(named=True),
        ):
            metadata["preference"] = embedding
            session.add(Users.model_validate(metadata))
        session.commit()


@task
def users_etl(source: Client, destination: Connection):
    run_etl(
        partial(
            extract,
            client=source,
            batch_size=100,
        ),
        transform,
        partial(
            upload,
            conn=destination,
        ),
    )
