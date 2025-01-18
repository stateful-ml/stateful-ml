from __future__ import annotations
import polars as pl
import numpy as np
import mlflow
from mlflow.pyfunc import PyFuncModel, load_model
from functools import partial
from prefect import flow, task
from prefect.blocks.system import Secret
from prefect.logging import get_run_logger, get_logger
from supabase import create_client, Client
from sqlmodel import Session, create_engine
from sqlalchemy import Connection, Index
from sqlalchemy.schema import CreateSchema
from .shared.data_models import EMBEDDING_SIZE, Content, Users, TableManager
from .runner import run_etl
from .schemas import Dataset
from typing import TypeVar, Iterable

T = TypeVar("T")


def by_chunks(x: Iterable[T], n: int) -> Iterable[list[T]]:
    values = []
    for value in x:
        values.append(value)
        if len(values) >= n:
            yield values
            values = []
    yield values


def extract(content_bucket: str, client: Client, batch_size: int):
    storage = client.storage.from_(content_bucket)
    for input_batch in by_chunks(storage.list(), batch_size):
        output_batch = []
        metadata = []
        for blob in input_batch:
            _data = storage.download(blob["name"]) # imagine im using it :)
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
def etl(
    content_bucket: str, source: Client, destination: Connection, model: PyFuncModel
):
    run_etl(
        partial(
            extract,
            content_bucket=content_bucket,
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
def manage_schema(version: str, conn: Connection):
    conn.execute(CreateSchema(version, if_not_exists=True))
    TableManager.set_schema(version)
    TableManager.create_all(conn)


@task
def index(conn: Connection):
    Index(
        "ivfflat_index",
        Content.embedding,  # type: ignore
        postgresql_using="ivfflat",
        postgresql_with={"lists": 100},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    ).create(conn)


@flow
def embed_content(embedder_version: str, version: str):
    print(version)
    mlflow.set_tracking_uri(Secret.load("mlflow-tracking-uri").get())

    supabase_client = create_client(
        Secret.load("supabase-url").get(), Secret.load("supabase-key").get()
    )
    pg_engine = create_engine(
        f"postgresql+psycopg2://{Secret.load('vectorstore-connection-string').get()}"
    )
    content_bucket = Secret.load("content-bucket").get()
    model = load_model(f"models:/{embedder_version}")

    with pg_engine.connect() as conn:
        manage_schema(version, conn)

        etl(content_bucket, supabase_client, conn, model)

        index(conn)

        conn.commit()
