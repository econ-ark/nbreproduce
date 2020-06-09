"""Console script for nbreproduce."""
import argparse
import sys

from .nbreproduce import (
    download_notebook_from_url,
    check_docker_image,
    reproduce,
    link_docker_notebook,
)


def main():
    """Console script for nbreproduce."""
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", help="Path to notebook locally")
    parser.add_argument(
        "--url", help="URL to notebook, currently works only for GitHub"
    )
    parser.add_argument("--docker", help="Name of Docker image on DockerHub")
    parser.add_argument("--timeout", help="indvidual cell timeout limit, default 600s")
    # parser.add_argument('_', nargs='*')
    args = parser.parse_args()
    # print(args)
    if args.url is not None:
        print(f"Downloading Jupyter Notebook from the provided URL: {args.url}")
        notebook = download_notebook_from_url(args.url)
        print("Download successful")
    if args.notebook is not None:
        # sanity check, notebook extension
        if args.notebook[-6:] != ".ipynb":
            raise ValueError("Not a Jupyter notebook")
        if args.notebook[:4] == "http":
            raise ValueError("Use --url flag to pass in a URL to a Jupyter Notebook")
        notebook = args.notebook

    if not check_docker_image(notebook):
        if args.docker is None:
            raise ValueError(
                f'No linked Docker image found in the metadata, link it using "nbreproduce --docker image_name {notebook}" \
                The Docker image should be built using the base Jupyter docker-stacks images, https://jupyter-docker-stacks.readthedocs.io'
            )
        link_docker_notebook(notebook, args.docker)

    # force new docker link
    if args.docker is not None:
        link_docker_notebook(notebook, args.docker)

    reproduce(notebook, args.timeout)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
