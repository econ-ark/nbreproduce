"""Console script for nbreproduce."""
import argparse
import sys
from pathlib import Path

from .nbreproduce import (
    _download_notebook_from_url,
    reproduce,
    _link_docker_notebook,
    reproduce_script,
    _run_live_env,
    _is_port_in_use,
    _random_port,
)


def main():
    """Console script for nbreproduce."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "notebook",
        help="Path to notebook/script locally",
        default="reproduce.sh",
        nargs="?",
    )
    parser.add_argument(
        "--url",
        help="URL to notebook, currently works only for GitHub",
        dest="url",
        action="store_true",
    )
    parser.add_argument(
        "--docker",
        help="Name of Docker image on DockerHub",
        default="econark/econ-ark-notebook:latest",
    )
    parser.add_argument(
        "--live",
        help="Run nbreproduce in live mode, it exposes a jupyter server instance running inside the docker container on port 8888",
        dest="live",
        action="store_true",
    )
    parser.add_argument(
        "--timeout", dest="timeout", help="indvidual cell timeout limit, default 600s"
    )
    parser.add_argument(
        "--port",
        dest="port",
        help="port number on the local machine to bind with the docker container.",
        default=8888,
    )
    parser.add_argument(
        "--inplace",
        dest="inplace",
        help="Flag to reproduce notebooks and projects inplace.",
        action="store_true",
    )
    parser.add_argument(
        "--output",
        dest="output_dir",
        help="Output directory to store the reproduced project after executing the bash script",
        default="reproduce_output",
    )
    # Check if give port or default (8888) already in use, if yes assign a random open port.
    args = parser.parse_args()
    if _is_port_in_use(args.port):
        args.port = _random_port()

    # Check if .dockerimage file exits either in root directory or reproduce/ dir
    docker_image_file_root = Path('.dockerimage')
    docker_image_file_dir = Path('reproduce/.dockerimage')
    if docker_image_file_root.is_file():
        with open(docker_image_file_root) as f:
            args.docker = f.readline().strip()
    elif docker_image_file_dir.is_file():
        with open(docker_image_file_dir) as f:
            args.docker = f.readline().strip()

    if args.live:
        print(
            f"Running in live interactive mode using the {args.docker} docker image on port {args.port}"
        )
        _run_live_env(args.docker, args.port)
        return 0
    if args.url:
        notebook = _download_notebook_from_url(args.notebook)
        reproduce(
            notebook, args.docker, args.timeout, args.inplace,
        )
        return 0
    elif args.notebook is not None:
        # sanity check, notebook extension or bash script
        if args.notebook[-6:] != ".ipynb" and args.notebook[-3:] != ".sh":
            raise ValueError("Not a Jupyter notebook or a bash script.")
        if args.notebook[:4] == "http":
            raise ValueError("Use --url flag to pass in a URL to a Jupyter Notebook.")
        notebook = args.notebook

    if notebook[-3:] == ".sh":
        if args.docker is None:
            raise ValueError("Please provide a docker image to execute the script.")
        reproduce_script(notebook, args.docker, True, args.output_dir)
        return 0

    reproduce(
        notebook, args.docker, args.timeout, args.inplace,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
