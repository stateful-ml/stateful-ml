import os
import dotenv
from supabase import create_client
from prefect.blocks.system import Secret
from pathlib import Path
import uuid

image_dir = Path("images")
assert image_dir.exists() and image_dir.is_dir()

dotenv.load_dotenv()
supabase_client = create_client(
    os.environ["SUPABASE_URL"], Secret.load("supabase-key").get()
)

table_name = Secret.load("content-table").get()
(
    supabase_client.table(table_name)
    .insert(
        [{"id": str(uuid.uuid4())} for _ in range(42)],
        returning="minimal",  # type: ignore
    )
    .execute()
)

bucket_name = Secret.load("content-bucket").get()
supabase_client.storage.create_bucket(
    bucket_name,
    options={"public": True},
)
bucket = supabase_client.storage.from_(bucket_name)
for file in image_dir.glob("*"):
    if file.is_file():
        bucket.upload(file.name, file)
