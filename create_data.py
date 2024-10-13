import supabase
from supabase import create_client, Client
from prefect.blocks.system import Secret
from pathlib import Path

image_dir = Path('images')
assert image_dir.exists() and image_dir.is_dir()

supabase_client = create_client(
    Secret.load("supabase-url").get(), Secret.load("supabase-key").get()
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
