from __future__ import annotations
import polars as pl
import numpy as np
from mlflow.pyfunc import PyFuncModel, load_model
from functools import partial
from prefect import flow, task
from prefect.blocks.system import Secret
from supabase import create_client, Client
from sqlmodel import Session, create_engine
from sqlalchemy import Connection, Index
from sqlalchemy.schema import CreateSchema
from .shared.data_models import EMBEDDING_SIZE, Content, Users, TableManager
from .runner import run_etl
from .schemas import Dataset


def extract(content_bucket: str, client: Client, batch_size: int):
    batch = []
    metadata = []
    storage = client.storage.from_(content_bucket)
    for blob in storage.list():
        data = storage.download(blob["name"])
        batch.append(np.array(data))
        metadata.append((blob["name"],))
        if len(batch) == batch_size:
            yield Dataset(
                np.stack(batch, axis=0),
                pl.DataFrame(metadata, schema=["name"]),
            )
            batch = []
            metadata = []


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
