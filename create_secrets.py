from prefect.blocks.system import Secret
import dotenv

dotenv.load_dotenv()  # for prefect connection
env = dotenv.dotenv_values("./.env")  # for secrets
for k in [
    "VECTORSTORE_CONNECTION_STRING",
    "CONTENT_BUCKET",
    "SUPABASE_URL",
    "SUPABASE_KEY",
]:
    Secret(
        value=env[k]  # type: ignore : secret init has the wrong type hint
    ).save(name=k.lower().replace("_", "-"))
