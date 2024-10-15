import polars as pl
import numpy as np
from functools import partial
from prefect import flow, task
from prefect.blocks.system import Secret
from supabase import create_client, Client
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy import Connection, Index
from sqlalchemy.schema import CreateSchema
from .shared.data_models import EMBEDDING_SIZE, Content, Users
from .runner import run_etl
import dotenv
import os


def extract(content_bucket: str, client: Client, batch_size: int):
    batch = []
    metadata = []
    storage = client.storage.from_(content_bucket)
    for blob in storage.list():
        data = storage.download(blob["path"])
        batch.append(np.array(data))
        metadata.append((blob["name"],))
        if len(batch) == batch_size:
            yield np.stack(batch, axis=0), pl.DataFrame(metadata, schema=["name"])
            batch = []
            metadata = []


def transform(data: tuple[np.ndarray, pl.DataFrame]):
    arr, df = data
    return np.random.random((arr.shape[0], EMBEDDING_SIZE)), df


def upload(data: tuple[np.ndarray, pl.DataFrame], conn: Connection):
    arr, df = data
    with Session(conn) as session:
        # TODO: remove the silly overhead
        for embedding, metadata in zip(arr, df.iter_rows(named=True)):
            metadata["embedding"] = embedding
            session.add(Content.model_validate(metadata))
        # session.flush()


@task
def etl(content_bucket: str, source: Client, destination: Connection):
    run_etl(
        partial(
            extract,
            content_bucket=content_bucket,
            client=source,
            batch_size=100,
        ),
        transform,
        partial(upload, conn=destination),
    )


@task
def manage_schema(version: str, conn: Connection):
    conn.execute(CreateSchema(version, if_not_exists=True))
    SQLModel.metadata.schema = version
    SQLModel.metadata.create_all(conn)


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
def main(model: str, version: str):
    print(version)

    supabase_client = create_client(
        Secret.load("supabase-url").get(), Secret.load("supabase-key").get()
    )
    pg_engine = create_engine(
        f"postgresql+psycopg2://{Secret.load('vectorstore-connection-string').get()}"
    )
    content_bucket = Secret.load("content-bucket").get()

    with pg_engine.connect() as conn:
        manage_schema(version, conn)

        etl(content_bucket, supabase_client, conn)

        index(conn)

        conn.commit()
