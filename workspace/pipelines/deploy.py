import os
import dotenv
import argparse
from prefect.docker import DockerImage
from typing import cast
from src.main import embed_content


class Versions(argparse.Namespace):
    env: str
    version: str
    embedder: str


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("env", required=True)
    parser.add_argument("version", required=True)
    parser.add_argument("embedder", required=True)
    return cast(Versions, parser.parse_args())


if __name__ == "__main__":  # builds on a local machine
    dotenv.load_dotenv()  # needs to load the prefect server link
    args: Versions = parse_args()
    image_registry = os.environ["IMAGE_REGISTRY_URL"]
    embed_content.deploy(
        name=args.env, # e.g. flow: embed_content, deployment: stg
        image=DockerImage(
            name=f"{image_registry}/{args.version}",
            dockerfile="pipelines/Dockerfile",
        ),
        parameters={
            "embedder_version": args.embedder,
            "version": args.version,
        },
        version=args.version,
        work_pool_name="kube-pool",
    )
