nbreproduce
===========
[![PyPI version](https://badge.fury.io/py/nbreproduce.svg)](https://badge.fury.io/py/nbreproduce)

Reproduce Jupyter Notebooks and projects inside Docker Containers (based on [Jupyter Docker-Stacks](https://jupyter-docker-stacks.readthedocs.io) images) using the `nbreproduce` CLI.


* Free software: BSD license
* Documentation: https://nbreproduce.readthedocs.io. (not up yet, use `$ nbreproduce -h` to get a quick desciption of various flags)


Installation:
-------------

```
$ pip install nbreproduce
```

Features:
--------

- Reproduce a Jupyter Notebook (URL or local file) inside a Docker container for consistent builds across all the devices capable of running docker and Python.

- To test the `hello_world.ipynb` example in this repo.
```
$ nbreproduce --url https://github.com/econ-ark/nbreproduce/blob/master/tests/hello_world.ipynb
```
- The `nbreproduce` will create a new Jupyter notebook ending with `filename-reproduce.ipynb` in the same directory which is a copy of the original notebook but executed inside the docker container environment.

- `nbreproduce` requires a special metadata tag (`docker_image`) inside in the Jupyter notebook to find the link to docker image on DockerHub. On the first run of `nbreproduce` with a normal Jupyter notebook it will prompt you to add a docker image tag, these docker images are built on top of [Jupyter Docker-Stacks](https://jupyter-docker-stacks.readthedocs.io). The `hello_world.ipynb` example can run with the `scipy-notebook` standard image. Using the `--docker` flag you can point it towards the right docker image. (Currently only DockerHub imgags are supported)
```
$ nbreproduce --docker jupyter/scipy-notebook:latest hello_world.ipynb
```

- For a Jupyter notebook which already has the metadata tag (`docker_image`), we can directly execute the notebook, kind of like papermill but inside a standardised docker environemnt :)
```
$ nbreproduce hello_world.ipynb
```

- Reproduce entire folders and projects inside a Docker environment (it works by mounting the current directory to the docker container and running a bash file which has all the required steps to reproduce all the content like figures, builiding latex documents, slides, etc).
```
$ nbreproduce --docker econark/econ-ark-notebook do_all.sh

Executing do_all.sh using the econark/econ-ark-notebook environment inside a docker container.
Executing do_all.sh in the current directory /Users/ms/dev/REMARK/REMARKs/CGMPortfolio
....
....
....
```

- The project is in pre alpha developement mode, so things will break. Don't use this in production. The documentation website doesn't exist yet, use `nbreproduce -h` to get a quick desciption of various flags. Feel free to open up any issue for suggestions or submit a PR to fix bugs/implement new features.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

[Cookiecutter](https://github.com/audreyr/cookiecutter)

[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
