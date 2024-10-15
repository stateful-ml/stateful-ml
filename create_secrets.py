from prefect.blocks.system import Secret
import dotenv
import os

dotenv.load_dotenv()
for k in [
    "VECTORSTORE_CONNECTION_STRING",
    "SUPABASE_KEY",
    "SUPABASE_URL"
]:
    Secret(
        value=os.environ[k]  # type: ignore : secret init has the wrong type hint
    ).save(
        name=k.lower().replace("_", "-"),
        overwrite=True,
    )
