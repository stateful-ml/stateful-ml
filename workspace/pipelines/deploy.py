import os
import asyncio
import dotenv
import argparse
from prefect import Flow
from prefect.runner.storage import GitRepository
from prefect.deployments.runner import DeploymentImage
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


async def main():
    dotenv.load_dotenv()  # needs to load the prefect server link
    args = parse_args()
    version = f"{args.code}__{args.model}"
    await src_main.with_options(name=args.code).deploy(
        name=args.model,
        image=DeploymentImage(
            name=f"custom-docker-registry.myminikube/{version}",
            dockerfile="pipelines/Dockerfile",
        ),
        parameters={
            "model": args.model,
            "version": version,
        },
        tags=["stg"],
        work_pool_name="docker-pool",
    )


# TODO: extract into submodule everything that seems out of timeline, like this script
if __name__ == "__main__":  # builds on a local machine
    asyncio.run(main())
