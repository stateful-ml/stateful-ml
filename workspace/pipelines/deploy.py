import os
import asyncio
import dotenv
import argparse
from prefect import Flow
from prefect.runner.storage import GitRepository
from prefect.docker import DockerImage
from typing import cast, Any, TYPE_CHECKING
from src.main import main as src_main


class Versions(argparse.Namespace):
    code: str
    model: str


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model-version", dest="model", required=True)
    parser.add_argument("-c", "--code-version", dest="code", required=True)
    return cast(Versions, parser.parse_args())


# TODO: extract into submodule everything that seems out of timeline, like this script
if __name__ == "__main__":  # builds on a local machine
    dotenv.load_dotenv()  # needs to load the prefect server link
    args = parse_args()
    version = f"{args.code}__{args.model}"
    image_registry = os.environ["IMAGE_REGISTRY_URL"]
    src_main.with_options(name=args.code).deploy(
        name=args.model,
        image=DockerImage(
            name=f"{image_registry}/{version}",
            dockerfile="pipelines/Dockerfile",
        ),
        parameters={
            "model": args.model,
            "version": version,
        },
        tags=["stg"],
        work_pool_name="kube-pool",
    )
