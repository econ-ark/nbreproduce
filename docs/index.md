# Welcome to nbreproduce

[![PyPI version](https://badge.fury.io/py/nbreproduce.svg)](https://badge.fury.io/py/nbreproduce)

Reproduce Jupyter Notebooks and projects inside Docker Containers (based on [Jupyter Docker-Stacks](https://jupyter-docker-stacks.readthedocs.io) images) using the `nbreproduce` CLI.


## Installation

`nbreproduce` uses docker to execute notebooks and scripts in a containerised environment.

Before installing `nbreproduce` install Docker using the instructions at [Docker Desktop](https://www.docker.com/products/docker-desktop).

Once you have successfully installed docker you can install `nbreproduce` using pip.

```
$ pip install nbreproduce
```

To check if you have installed `nbreproduce` properly you can execute the `hello-world-notebook` test.

```
$ nbreproduce --url https://github.com/econ-ark/nbreproduce/blob/master/tests/hello_world.ipynb
```
This will download a minimal example notebook `hello_world.ipynb` and save the a copy `hello_world-reproduce.ipynb` which is executed inside a docker container environment. To check the output, open up `hello_world-reproduce.ipynb` in a Jupyter Notebook/Lab instance or another notebook serving frontend like VSCode/PyCharm/nteract.
