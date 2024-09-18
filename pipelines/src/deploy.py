import os
import dotenv
import argparse
from prefect import flow
from prefect.runner.storage import GitRepository
from prefect.deployments.runner import DeploymentImage
from typing import cast, Any
from main import main


class Args(argparse.Namespace):
    model: str


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model-version", dest="model", required=True)
    return cast(Args, parser.parse_args())


# TODO: extract into submodule everything that seems out of timeline, like this script
if __name__ == "__main__":  # builds on a local machine
    dotenv.load_dotenv()  # needs to load the prefect server link
    args = parse_args()
    _ = main.with_options(name=os.environ["CODE_VERSION"]).deploy(
        name=args.model,
        image=DeploymentImage(
            name=f"{os.environ['CODE_VERSION']}__{args.model}",
            dockerfile="pipelines.Dockerfile",
        ),
        parameters={
            "model": args.model,
            "version": f"{os.environ['CODE_VERSION']}__{args.model}",
        },
        tags=["stg"],
        work_pool_name="docker-pool",
    )
