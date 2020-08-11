import urllib.request
import shutil
import nbformat
import subprocess
import os
import docker
import signal
import time

NB_VERSION = 4
client = docker.from_env()
PWD = os.getcwd()
MOUNT = {PWD: {"bind": "/home/jovyan/work", "mode": "rw"}}


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


def _pull_image(image: str) -> None:
    tags = [j for l in client.images.list() for j in l.tags] 
    if image in tags:
        pass
    else:        
        print(f'Fetching {image}, this may take some time.')
        client.images.pull(image)
    print(f'Executing the script inside {image} container.')

def _download_notebook_from_url(url: str) -> str:
    print(f"Downloading Jupyter Notebook from the provided URL: {url}.")
    # convert GitHub content page URL to raw URL
    if url.startswith("https://github.com"):
        url = url.replace("https://github.com", "https://raw.githubusercontent.com")
        url = url.replace("/blob", "")
    elif url.startswith("https://raw.githubusercontent.com"):
        pass
    else:
        raise ValueError("URL not valid")

    # check ipynb extension
    if url[-6:] != ".ipynb":
        raise ValueError("Not a Jupyter notebook")
    FILE_NAME = url.split("/")[-1]
    with urllib.request.urlopen(url) as response, open(FILE_NAME, "wb") as out_file:
        shutil.copyfileobj(response, out_file)

    print("Download successful.")
    return FILE_NAME


def check_docker_image(notebook: str) -> bool:
    # check for notebook existence?
    nb = nbformat.read(notebook, as_version=NB_VERSION)
    # check if docker_image is used previously
    if "docker_image" not in nb["metadata"]:
        print("No linked Docker image found!")
        return False
    return True


def _link_docker_notebook(notebook: str, image: str) -> None:
    nb = nbformat.read(notebook, as_version=NB_VERSION)
    nb["metadata"]["docker_image"] = image
    nbformat.write(nb, notebook)

def _run_live_env(image: str) -> None:
    _pull_image(image)
    container = client.containers.run(
        image,
        volumes=MOUNT,
        ports={"8888/tcp": 8888},
        detach=True,
        command="start.sh jupyter lab",
    )
    killer = GracefulKiller()
    log_set = dict()
    print(
        "Please wait while a notebook server is started up inside the {image} container."
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


def reproduce_script(script: str, image: str) -> None:
    print(
        f"Executing {script} in the current directory {PWD} using the {image} docker image."
    )
    _pull_image(image)
    log = client.containers.run(
        image,
        volumes=MOUNT,
        user="root",
        command=f'bash -c "cd work/; bash {script}"',
    )
    print(log.decode("utf-8"))
    return None


def reproduce(notebook: str, timeout: int, image: str) -> None:
    nb = nbformat.read(notebook, as_version=NB_VERSION)
    if 'docker_image' in nb["metadata"]:
        image = nb["metadata"]["docker_image"]
    else:
        image = _link_docker_notebook(notebook, image)
    # check docker link
    NOTEBOOK_NAME = notebook[:-6]
    print(
        f"Executing {notebook} using the {image} environment inside a docker container."
    )
    # pwd = subprocess.run(["pwd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # mount = str(pwd.stdout)[2:-3] + ":/home/jovyan/work"
    # mount the present directory and start up a container
    _pull_image(image)
    container_id = client.containers.run(
        image,
        volumes=MOUNT,
        detach=True,
        user="root",
    )
    # container_id = subprocess.run(
    #     ["docker", "run", "-v", mount, "-d", DOCKER_IMAGE],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE,
    # )
    # container_id = container_id.stdout.decode("utf-8")[:-1]
    print(f"A docker container is created to execute the notebook, id = {container_id.short_id}")
    PATH_TO_NOTEBOOK = f"/home/jovyan/work/"
    # copy the notebook file to reproduce notebook
    container_id.exec_run(
        cmd=f'cp {PATH_TO_NOTEBOOK}{NOTEBOOK_NAME}.ipynb {PATH_TO_NOTEBOOK}{NOTEBOOK_NAME}-reproduce.ipynb',
        tty=True)
    # subprocess.run(
    #     [
    #         f"docker exec -it  {container_id} bash -c 'cp {PATH_TO_NOTEBOOK}{NOTEBOOK_NAME}.ipynb {PATH_TO_NOTEBOOK}{NOTEBOOK_NAME}-reproduce.ipynb'"
    #     ],
    #     shell=True,
    # )
    TIMEOUT = timeout
    # execute the reproduce notebook
    # subprocess.run(
    #     [
    #         f"docker exec -it  {container_id} bash -c 'jupyter nbconvert --ExecutePreprocessor.timeout={TIMEOUT} --to notebook --inplace --execute {PATH_TO_NOTEBOOK}{NOTEBOOK_NAME}-reproduce.ipynb'"
    #     ],
    #     shell=True,
    # )
    container_id.exec_run(
        cmd=f'jupyter nbconvert --ExecutePreprocessor.timeout={TIMEOUT} --to notebook --inplace --execute {PATH_TO_NOTEBOOK}{NOTEBOOK_NAME}-reproduce.ipynb',
        tty=True,
        stdin=True)
    # subprocess.run([f"docker stop {container_id}"], shell=True)
    print(f'Reproduced {NOTEBOOK_NAME}, check {NOTEBOOK_NAME}-reproduce.ipynb for the reproduced output in the {image} environment.')
    container_id.stop()
