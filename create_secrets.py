from prefect.blocks.system import Secret
import dotenv

env = dotenv.dotenv_values()
for k in [
    "VECTORSTORE_CONNECTION_STRING",
    "CONTENT_BUCKET",
    "SUPABASE_URL",
    "SUPABASE_KEY",
]:
    Secret(value=env[k]).save(name=k.lower().replace("_", "-"))
