import argparse
from prefect.docker import DockerImage
from typing import cast
from src.main import embed_content
from pathlib import Path


class Versions(argparse.Namespace):
    env: str
    version: str
    embedder: str


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-registry", required=True)
    parser.add_argument("--image-repo", required=True)
    parser.add_argument("--env", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--embedder", required=True)
    return cast(Versions, parser.parse_known_args())


if __name__ == "__main__":  # builds on a local machine
    args: Versions = parse_args()
    embed_content.deploy(
        name=args.env, # e.g. flow: embed_content, deployment: stg
        image=DockerImage(
            name=f"{args.image_registry}/{args.image_repo}:{args.version}",
            dockerfile=f"{Path(__file__).parent}/Dockerfile",
        ),
        parameters={
            "embedder_version": args.embedder,
            "version": args.version,
        },
        version=args.version,
        work_pool_name="kube-pool",
    )
