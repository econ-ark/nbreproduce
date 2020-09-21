import urllib.request
import shutil
import nbformat
import os
import docker
import signal
import time
import socket

NB_VERSION = 4
client = docker.from_env()
PWD = os.getcwd()
MOUNT = {PWD: {"bind": "/home/jovyan/work", "mode": "rw"}}

# https://stackoverflow.com/a/31464349/4892738
class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


# https://stackoverflow.com/a/52872579/4892738
def _is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def _random_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _pull_image(image: str) -> None:
    tags = [j for l in client.images.list() for j in l.tags]
    if image in tags:
        pass
    else:
        print(f"Fetching {image}, this may take some time.")
        client.images.pull(image)
    print(f"Executing the script inside {image} container.")
    return None


def _download_notebook_from_url(url: str) -> str:
    print(f"Downloading Jupyter Notebook from the provided URL: {url}.")
    # convert GitHub content page URL to raw URL
    if url.startswith("https://github.com"):
        url = url.replace("https://github.com", "https://raw.githubusercontent.com")
        url = url.replace("/blob", "")
    elif url.startswith("https://raw.githubusercontent.com"):
        pass
    else:
        raise ValueError(
            "URL not valid. Only GitHub and GitHub raw links are supported for now."
        )

    # check ipynb extension
    if url[-6:] != ".ipynb":
        raise ValueError("URL doesn't point to a Jupyter notebook.")
    FILE_NAME = url.split("/")[-1]
    with urllib.request.urlopen(url) as response, open(FILE_NAME, "wb") as out_file:
        shutil.copyfileobj(response, out_file)

    print("Download successful.")
    return FILE_NAME


def _link_docker_notebook(notebook: str, image: str) -> str:
    nb = nbformat.read(notebook, as_version=NB_VERSION)
    nb["metadata"]["docker_image"] = image
    nbformat.write(nb, notebook)
    return image


def _run_live_env(image: str, port: int) -> None:
    """ Start up a Jupyter instance on the local machine using the docker environment.

    Parameters
    -----------
    image: str
        Docker image (example: jupyter/scipy-notebook)
    
    port: int
        Port to local machine to bind the docker container. To open up the Jupyter instance
        go to localhost:port/?token=token_from_the_output
    """
    _pull_image(image)
    container = client.containers.run(
        image,
        volumes=MOUNT,
        ports={"8888/tcp": int(port)},
        detach=True,
        command="start.sh jupyter lab",
    )
    killer = GracefulKiller()
    print(
        f"Please wait while a notebook server is started up inside the {image} container on the port {port}. \
          To access the Jupyter instance go to localhost:{port}/?token=token_from_the_output."
    )
    time.sleep(10)
    for e in container.logs().decode("utf-8").split("\n"):
        print(e)
    while not killer.kill_now:
        time.sleep(1)
    print("\n", "Jupyter notebook instance is stopped!")
    container.stop()
    container.remove()
    return None


def reproduce_script(script: str, image: str, inplace: bool, output_dir: str) -> None:
    """ Execute a bash script inside the docker container.

    Parameters
    -----------
    script: str
        bash script name, if none provided execute reproduce.sh

    image: str
        Docker image (example: jupyter/scipy-notebook)
    
    inplace: bool
        If True, the script is executed in the current directory.
        If False, everything in the current folder is copied to a new folder (output_dir)
        and the bash script is executed in that folder.
    
    output_dir: str
        Name of the output directory, if none provided an output directory 'reproduce_output'
        will be created in the current directory.
    """
    _check_windows_EOL(script)
    print(
        f"Executing {script} in the current directory {PWD} using the {image} docker image."
    )
    _pull_image(image)
    container_id = client.containers.run(
        image, volumes=MOUNT, detach=True, user="root",
    )
    print(
        f"A docker container is created to execute the notebook, id = {container_id.short_id}"
    )
    if inplace:
        _, log = container_id.exec_run(
            cmd=f'bash -c "cd work/; bash {script}"', tty=True, stdin=True, stream=True
        )
        for chunk in log:
            print(chunk.decode("utf-8"))
    else:
        # TODO output_dir
        # copy eveything into output_dir and execute inside it.
        _, log = container_id.exec_run(
            cmd=f'bash -c "cp cd work/; bash {script}"',
            tty=True,
            stdin=True,
            stream=True,
        )

    container_id.stop()
    return None

def _check_windows_EOL(script):
    import platform
    # Convert the bash script EOL to UNIX compatible
    if platform.system() == 'Windows':
        print('Windows machine detected, converting the {script} EOL to UNIX style.')
        WINDOWS_LINE_ENDING = b'\r\n'
        UNIX_LINE_ENDING = b'\n'
        with open(script, 'rb') as open_file:
            content = open_file.read()
        content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
        with open(script, 'wb') as open_file:
            open_file.write(content)


def reproduce(
    notebook: str, image: str, timeout: int = 600, inplace: bool = False
) -> None:
    """ Execute the given notebook inside a docker container using the image.

    This creates a copy of notebook with the suffix *-reproduce.ipynb.

    Parameters
    -----------

    notebook: str
        Name of the notebook.
        
    image: str
        Docker image (example: jupyter/scipy-notebook)

    timeout: int
        timeout for individual cells in the notebook (default 600s)

    inplace: bool (default = False)
        False if notebook should be copied and reproduced as a seprate notebook
        with the -reproduce.ipynb suffix, True if notebook is reproduced using the
        base notebook.
    """
    # Should notebooks take in PATH object instead of str?
    nb = nbformat.read(notebook, as_version=NB_VERSION)
    if "docker_image" in nb["metadata"]:
        image = nb["metadata"]["docker_image"]
    else:
        image = _link_docker_notebook(notebook, image)
    # check docker link
    NOTEBOOK_NAME = notebook[:-6]
    print(
        f"Executing {notebook} using the {image} environment inside a docker container."
    )
    # mount the present directory and start up a container
    _pull_image(image)
    container_id = client.containers.run(
        image, volumes=MOUNT, detach=True, user="root",
    )
    print(
        f"A docker container is created to execute the notebook, id = {container_id.short_id}"
    )
    PATH_TO_NOTEBOOK = f"/home/jovyan/work/"
    if not inplace:
        # copy the notebook file to reproduce notebook
        REPRODUCED_NOTEBOOK = f"{PATH_TO_NOTEBOOK}{NOTEBOOK_NAME}-reproduce.ipynb"
        _, log = container_id.exec_run(
            cmd=f"cp {PATH_TO_NOTEBOOK}{NOTEBOOK_NAME}.ipynb {REPRODUCED_NOTEBOOK}",
            tty=True,
            stdin=True,
            stream=True,
        )
        for chunk in log:
            print(chunk.decode("utf-8"))
    else:
        REPRODUCED_NOTEBOOK = f"{PATH_TO_NOTEBOOK}{NOTEBOOK_NAME}.ipynb"

    TIMEOUT = timeout
    # execute the reproduce notebook
    _, log = container_id.exec_run(
        cmd=f"jupyter nbconvert --ExecutePreprocessor.timeout={TIMEOUT} --to notebook --inplace --execute {REPRODUCED_NOTEBOOK}",
        tty=True,
        stdin=True,
        stream=True,
    )
    for chunk in log:
        print(chunk.decode("utf-8"))
    print(
        f"Reproduced {NOTEBOOK_NAME}.ipynb in the {image} environment, check {REPRODUCED_NOTEBOOK[18:]} for the reproduced output."
    )
    container_id.stop()
    return None
