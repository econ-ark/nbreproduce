# Reproduce - Notebooks

You can use `nbreproduce` to execute individual Jupyter notebooks locally on your machine inside a docker environment. Jupyter Notebooks can be distributed as individual files/URLs with the name of the docker image it needs to be reproduced consistently.

`nbreproduce` will create a new notebook with the suffix `-reproduce.ipynb` in the current directory. To check the outputs you can open the reproduced notebooks using your favourite notebook frontend, JupyterLab/nteract/VSCode/PyCharm...

## Local Notebooks

You can reproduce local notebooks by linking a docker image which is requried to build the environment.

```
$ nbreproduce --docker DOCKER_IMAGE name_of_notebook.ipynb
```

You wouldn't have to provide the `DOCKER_IMAGE` option after the first run as it is saved inside the notebook metadata (look for the tag name `docker_image`). If you share this notebook users wouldn't need to use `--docker DOCKER_IMAGE` while reproducing the notebook.

To reproduce a notebook which already has a `docker_image` tag in the metadata of the notebook.
```
$ nbreproduce name_of_notebook.ipynb
```


## URL Notebooks

NOTE: This currently only works with GitHub URL links and docker images on DockerHub.

`nbreproduce` can be used in combination with a GitHub link of a Jupyter Notebook with a linked docker image.

To fetch a notebook and run it inside a docker container:
```
$ nbreproduce --docker DOCKER_IMAGE --url LINK_TO_URL
```

As an example to test if everything works locally you can test with a sample notebook hosted at [https://github.com/econ-ark/nbreproduce/blob/master/tests/hello_world.ipynb](https://github.com/econ-ark/nbreproduce/blob/master/tests/hello_world.ipynb).
```
$ nbreproduce --docker jupyter/scipy-notebook:latest --url https://github.com/econ-ark/nbreproduce/blob/master/tests/hello_world.ipynb
```
