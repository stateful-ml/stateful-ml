import os
import polars as pl
import numpy as np
from functools import partial
from prefect import flow, task
from prefect.deployments.runner import DeploymentImage
from supabase import create_client, Client
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy import Connection, Index
from sqlalchemy.schema import CreateSchema
from shared.data_models import EMBEDDING_SIZE, Content, Users
from runner import run_etl
import dotenv

dotenv.load_dotenv()


def extract(client: Client, batch_size: int):
    batch = []
    metadata = []
    storage = client.storage.from_(os.environ["CONTENT_BUCKET"])
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
def etl(source: Client, destination: Connection):
    run_etl(
        partial(extract, client=source, batch_size=100),
        transform,
        partial(upload, conn=destination),
    )


@task
def manage_schema(conn: Connection):
    version = f"{os.environ['CODE_VERSION']}__{os.environ['MODEL_VERSION']}"
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
def main(model: str):
    print(model)

    supabase_client = create_client(
        os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"]
    )
    pg_engine = create_engine(
        f"postgresql+psycopg2://{os.environ['VECTORSTORE_CONNECTION_STRING']}"
    )
    with pg_engine.connect() as conn:
        manage_schema(conn)

        etl(supabase_client, conn)

        index(conn)

        conn.commit()


if __name__ == "__main__":
    _ = main.with_options(name=os.environ["CODE_VERSION"]).deploy(
        os.environ["MODEL_VERSION"],
        parameters={"model": os.environ["MODEL_VERSION"]},
        tags=["stg"],
        image=DeploymentImage(
            f"{os.environ['CODE_VERSION']}__{os.environ['MODEL_VERSION']}",
            dockerfile="./pipelines.Dockerfile", # should only be run from the root
        ),
        push=False,
    )
