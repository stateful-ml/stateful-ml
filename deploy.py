import argparse
from prefect import flow, deploy
from prefect.deployments.runner import DeploymentImage
from prefect.runner.storage import GitRepository


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", type=str)
    parser.add_argument("--model", type=str)
    return parser.parse_args()


args = parse_args()

deployment = flow.from_source(
    source=GitRepository(
        url="https://github.com/stateful-ml/stateful-ml.git", branch=args.version
    ),
    entrypoint="pipelines/main.py:main",
).to_deployment(args.model, parameters={"model": args.model})
deployment.flow_name = args.version

deploy(deployment, image=DeploymentImage(f"{args.version}__{args.model}"), push=False)
