import os
import dotenv
import argparse
from prefect import flow, Flow
from prefect.runner.storage import GitRepository
from prefect.deployments.runner import DeploymentImage
from typing import cast, Any


class Args(argparse.Namespace):
    code: str
    model: str


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--code-version", dest="code")
    parser.add_argument("-m", "--model-version", dest="model")
    return cast(Args, parser.parse_args())


# TODO: extract into submodule everything that seems out of timeline, like this script
if __name__ == "__main__":  # builds on a local machine
    dotenv.load_dotenv()  # needs to load the prefect server link
    args = parse_args()
    flow: Any  # this one is a mess
    _ = (
        flow.from_source(
            GitRepository(
                "https://github.com/stateful-ml/stateful-ml.git",
                branch=args.code,
            ),
            entrypoint="pipelines/src/main.py:main",
        )
        .with_options(name=args.code)
        .deploy(
            args.model,
            parameters={
                "model": args.model,
                "version": f"{args.code}__{args.model}",
            },
            tags=["stg"],
            work_pool_name="docker-pool",
        )
    )
