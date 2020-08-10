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


def download_notebook_from_url(url: str) -> str:
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

    return FILE_NAME


def check_docker_image(notebook: str) -> bool:
    # check for notebook existence?
    nb = nbformat.read(notebook, as_version=NB_VERSION)
    # check if docker_image is used previously
    if "docker_image" not in nb["metadata"]:
        print("No linked Docker image found!")
        return False
    return True


def link_docker_notebook(notebook: str, docker: str) -> None:
    nb = nbformat.read(notebook, as_version=NB_VERSION)
    nb["metadata"]["docker_image"] = docker
    nbformat.write(nb, notebook)


def _run_live_env(image: str) -> None:
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
        "Please wait while a notebook server is started up inside the docker container."
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
    # subprocess.run(
    #     [
    #         f'docker run -v {mount} -it --rm {image} bash -c "cd work/; export TERM=dumb; bash {script}"'
    #     ],
    #     shell=True,
    # )
    print(
        "Fetching the docker copy for reproducing results ",
        "this may take some time if running the nbreproduce command for the first time with this image",
    )
    log = client.containers.run(
        image,
        volumes=MOUNT,
        privileged=True,
        command=f'bash -c "cd work/; bash {script}"',
    )
    print(log.decode("utf-8"))
    return None
    # container.exec_run('bash -c "cd work/; bash {script}"')
    # container.stop()


def reproduce(notebook: str, timeout: int) -> None:
    nb = nbformat.read(notebook, as_version=NB_VERSION)
    DOCKER_IMAGE = nb["metadata"]["docker_image"]
    # check docker link
    NOTEBOOK_NAME = notebook[:-6]
    pwd = subprocess.run(["pwd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    mount = str(pwd.stdout)[2:-3] + ":/home/jovyan/work"
    # mount the present directory and start up a container
    print(
        "Fetching the docker copy for reproducing results, this may take some time if running the nbreproduce command for the first time"
    )
    container_id = subprocess.run(
        ["docker", "run", "-v", mount, "-d", DOCKER_IMAGE],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    container_id = container_id.stdout.decode("utf-8")[:-1]
    print(f"A docker container is created to execute the notebook, id = {container_id}")
    PATH_TO_NOTEBOOK = f"/home/jovyan/work/"
    # copy the notebook file to reproduce notebook
    subprocess.run(
        [
            f"docker exec -it  {container_id} bash -c 'cp {PATH_TO_NOTEBOOK}{NOTEBOOK_NAME}.ipynb {PATH_TO_NOTEBOOK}{NOTEBOOK_NAME}-reproduce.ipynb'"
        ],
        shell=True,
    )
    TIMEOUT = timeout
    # execute the reproduce notebook
    subprocess.run(
        [
            f"docker exec -it  {container_id} bash -c 'jupyter nbconvert --ExecutePreprocessor.timeout={TIMEOUT} --to notebook --inplace --execute {PATH_TO_NOTEBOOK}{NOTEBOOK_NAME}-reproduce.ipynb'"
        ],
        shell=True,
    )
    subprocess.run([f"docker stop {container_id}"], shell=True)
