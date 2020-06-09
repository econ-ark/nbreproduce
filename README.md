nbreproduce
===========


Reproduce Jupyter Notebooks inside Docker Containers using the `nbreproduce` CLI.


* Free software: BSD license
* Documentation: https://nbreproduce.readthedocs.io. (not up yet, use `$ nbreproduce -h` to get a quick desciption of various flags)


Installation:
-------------

```
$ pip install nbreproduce
```

Features:
--------

* Reproduce a Jupyter Notebook (URL or local file) inside a Docker container for consistent builds across all the devices capable of running docker and Python.

* To test the `hello_world.ipynb` example in this repo.
```
$ nbreproduce https://github.com/MridulS/nbreproduce/tree/master/tests/hello_world.ipynb
```

* `nbreproduce` requires a special metadata tag (`docker_image`) inside in the Jupyter notebook to find the link to docker image on DockerHub. On the first run of `nbreproduce` with a normal Jupyter notebook it will prompt you to add a docker image tag, these docker images are built on top of [Jupyter Docker-Stacks](https://jupyter-docker-stacks.readthedocs.io). The `hello_world.ipynb` example can run with the `scipy-notebook` standard image. Using the `--docker` flag you can point it towards the right docker image. (Currently only DockerHub imgages are supported)
```
$ nbreproduce --docker jupyter/scipy-notebook:latest hello_world.ipynb
```

* The project is in alpha developement mode, so things will break. Don't use this in production. The documentation website doesn't exist yet, use `nbreproduce -h` to get a quick desciption of various flags.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

[Cookiecutter](https://github.com/audreyr/cookiecutter)

[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
