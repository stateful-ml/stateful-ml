import argparse
from prefect import flow
from prefect.deployments.runner import DeploymentImage
from prefect.runner.storage import GitRepository


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", type=str)
    parser.add_argument("--model", type=str)
    return parser.parse_args()


args = parse_args()

flow.from_source(
    source=GitRepository(
        url="https://github.com/stateful-ml/stateful-ml.git", branch=args.version
    ),
    entrypoint="pipelines/main.py:main",
).with_options(name=args.version).deploy(args.model)
