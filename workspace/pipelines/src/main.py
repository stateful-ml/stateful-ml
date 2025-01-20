import mlflow
from mlflow.pyfunc import load_model
from prefect import flow, task
from sqlalchemy import Connection, create_engine
from sqlalchemy.schema import CreateSchema
from supabase import create_client

from .content import content_etl, content_index
from .users import users_etl
from .config import config
from .shared.data_models import TableManager


@task
def manage_schema(version: str, conn: Connection):
    conn.execute(CreateSchema(version, if_not_exists=True))
    TableManager.set_schema(version)
    TableManager.create_all(conn)


@flow
def etl(embedder_version: str, version: str):
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    supabase_client = create_client(config.supabase_url, config.supabase_key)
    pg_engine = create_engine(
        f"postgresql+psycopg2://{config.vectorstore_connection_string}"
    )
    model = load_model(f"models:/{embedder_version}")

    with pg_engine.connect() as conn:
        manage_schema(version, conn)
        users_etl(supabase_client, conn)
        content_etl(supabase_client, conn, model)
        content_index(conn)

        conn.commit()
