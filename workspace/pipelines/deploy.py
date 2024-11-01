import os
import asyncio
import dotenv
import argparse
from prefect import Flow
from prefect.runner.storage import GitRepository
from prefect.docker import DockerImage
from typing import cast, Any, TYPE_CHECKING
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


# TODO: extract into submodule everything that seems out of timeline, like this script
if __name__ == "__main__":  # builds on a local machine
    dotenv.load_dotenv()  # needs to load the prefect server link
    args: Versions = parse_args()
    image_registry = os.environ["IMAGE_REGISTRY_URL"]
    embed_content.deploy(
        name=args.env,
        image=DockerImage(
            name=f"{image_registry}/{args.version}",
            dockerfile="pipelines/Dockerfile",
        ),
        parameters={
            "embedder": args.embedder,
            "version": args.version,
        },
        # tags=[],
        version=args.version,
        work_pool_name="kube-pool",
    )
