from __future__ import annotations

from functools import partial

import numpy as np
import polars as pl
from mlflow.pyfunc import PyFuncModel
from prefect import task
from sqlalchemy import Connection, Index
from sqlmodel import Session
from supabase import Client

from .config import config
from .runner import run_etl
from .schemas import Dataset
from .shared.data_models import EMBEDDING_SIZE, Content  # noqa: F401
from .util import by_chunks


def extract(content_bucket: str, client: Client, batch_size: int):
    storage = client.storage.from_(content_bucket)
    for input_batch in by_chunks(storage.list(), batch_size):
        output_batch = []
        metadata = []
        for blob in input_batch:
            _data = storage.download(blob["name"])  # imagine im using it :)
            output_batch.append(np.random.uniform(0, 1, 50))
            metadata.append({"id": blob["name"]})
        yield Dataset(
            np.stack(output_batch, axis=0),
            pl.DataFrame(metadata),
        )


def transform(dataset: Dataset, model: PyFuncModel):
    return Dataset(
        model.predict(dataset.data),
        dataset.metadata,
    )


def upload(dataset: Dataset, conn: Connection):
    with Session(conn) as session:
        # TODO: remove the silly overhead
        for embedding, metadata in zip(
            dataset.data,
            dataset.metadata.iter_rows(named=True),
        ):
            metadata["embedding"] = embedding
            session.add(Content.model_validate(metadata))
        session.commit()


@task
def content_etl(source: Client, destination: Connection, model: PyFuncModel):
    run_etl(
        partial(
            extract,
            content_bucket=config.content_bucket,
            client=source,
            batch_size=100,
        ),
        partial(
            transform,
            model=model,
        ),
        partial(
            upload,
            conn=destination,
        ),
    )


@task
def content_index(conn: Connection):
    Index(
        "ivfflat_index",
        Content.embedding,  # type: ignore
        postgresql_using="ivfflat",
        postgresql_with={"lists": 100},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    ).create(conn)
