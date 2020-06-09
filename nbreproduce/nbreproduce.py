import urllib.request
import shutil
import nbformat
import subprocess

NB_VERSION = 4

def download_notebook_from_url(url: str) -> str:
    # convert GitHub content page URL to raw URL
    if url.startswith('https://github.com'):
        url = url.replace('https://github.com', 'https://raw.githubusercontent.com')
        url = url.replace('/blob', '')
    elif url.startswith('https://raw.githubusercontent.com'):
        pass
    else:
        raise ValueError('URL not valid')
    
    # check ipynb extension
    if url[-6:] != '.ipynb':
        raise ValueError('Not a Jupyter notebook')
    FILE_NAME = url.split('/')[-1]
    with urllib.request.urlopen(url) as response, open(FILE_NAME, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    
    return FILE_NAME


def check_docker_image(notebook):
    # check for notebook existence?
    nb = nbformat.read(notebook, as_version=NB_VERSION)
    # check if docker_image is used previously
    if 'docker_image' not in nb['metadata']:
        print('No linked Docker image found!')
        return False
    return True

def link_docker_notebook(notebook, docker):
    nb = nbformat.read(notebook, as_version=NB_VERSION)
    nb['metadata']['docker_image'] = docker
    nbformat.write(nb, notebook)


def reproduce(notebook, timeout):
    nb = nbformat.read(notebook, as_version=NB_VERSION)
    DOCKER_IMAGE = nb['metadata']['docker_image']
    # check docker link
    print(DOCKER_IMAGE)
    NOTEBOOK_NAME = notebook[:-6]
    pwd = subprocess.run(["pwd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    mount = str(pwd.stdout)[2:-3] + ":/home/jovyan/work"
    # mount the present directory and start up a container
    print('Fetching the docker copy for reproducing results, this may take some time if running the reproduce.py command for the first time')
    container_id = subprocess.run(
        ["docker", "run", "-v", mount, "-d", DOCKER_IMAGE], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    container_id = container_id.stdout.decode("utf-8")[:-1]
    print(f'A docker container is created to execute the notebook, id = {container_id}')
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
    # copy the reproduce notebook back to local machine
    # subprocess.run(
    #     [f"docker exec -it  {container_id} bash -c 'cp {PATH_TO_NOTEBOOK}{NOTEBOOK_NAME}-reproduce.ipynb /home/jovyan/work/notebooks/'"],
    #     shell=True,
    # )
    subprocess.run([f"docker stop {container_id}"], shell=True)
  