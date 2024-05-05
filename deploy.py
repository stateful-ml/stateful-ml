import argparse
from prefect import flow
from prefect.deployments.runner import DeploymentImage


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", type=str)
    parser.add_argument("--model", type=str)
    return parser.parse_args()


args = parse_args()

flow.from_source(
    source=f"https://github.com/stateful-ml/stateful-ml@{args.version}",
    entrypoint=f"pipelines/main.py:{args.version}",
).deploy(
    args.model
)
