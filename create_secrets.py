from prefect.blocks.system import Secret
import dotenv
import os

dotenv.load_dotenv()
for k in [
    "VECTORSTORE_CONNECTION_STRING",
    "SUPABASE_KEY",
    "SUPABASE_URL",
    "CONTENT_BUCKET",
    "MLFLOW_TRACKING_URI"
]:
    Secret(
        value=os.environ[k]  # type: ignore : secret init has the wrong type hint
    ).save(
        name=k.lower().replace("_", "-"),
        overwrite=True,
    )
