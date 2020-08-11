# Reproduce - Bash Projects

`nbreproduce` can also be used to reproduced whole projects which has an entry bash script. (Just like a make file)

The only requirement is to have an entry bash script which contains all the required steps to reproduce the project.
An example bash script could be something like:
``` 
# clean data
python clean_data.py

# generate figure
python generate_figures.py

# build latex paper
pdflatex latex/paper.tex 
```

`nbreproduce` mounts the current directory inside a docker container created using the docker image name provided.

To reproduce a project with a docker image and bash script:
```
$ nbreproduce --docker DOCKER_IMAGE name_of_bash_script.sh
```

`nbreproduce` by default looks for a bash script with the name `reproduce.sh`. If the bash script is `reproduce.sh` then just providing the name of the docker image is enough to execute `nbreproduce` in the current directory.
```
$ nbreproduce --docker DOCKER_IMAGE 
```

By default the docker image points to `econark/econ-ark-notebook:latest` which builds on top of `jupyter/scipy-notebook` by adding `latex` and `econ-ark`.

## Example

As an example, we will look at a replication of the paper Cocco, Gomes, & Maenhout (2005), "Consumption and Portfolio Choice Over the Life Cycle". The code is available at [https://github.com/econ-ark/REMARK/tree/master/REMARKs/CGMPortfolio](https://github.com/econ-ark/REMARK/tree/master/REMARKs/CGMPortfolio).

To reproduce the contents of this paper we can use `nbreproduce` to run the code inside a docker environment and get consistent results.
```
# Clone the repository from GitHub
$ git clone https://github.com/econ-ark/REMARK

# navigate to CGMPortfolio
$ cd REMARKS/CGMPortfolio

# check if reproduce.sh already exists in the current directory
$ ls
...
...
...
reproduce.sh
...
...


# Use nbreproduce to reproduce the content in this repository.
$ nbreproduce
Executing reproduce.sh in the current directory /Users/ms/dev/REMARK/REMARKs/CGMPortfolio using the econark/econ-ark-notebook:latest docker image.
Executing the script inside econark/econ-ark-notebook:latest container.
Using matplotlib backend: agg
1. Solve the model and display its policy functions
2. Simulate the lives of a few agents to show the implied income and stockholding processes.
3. Run a larger simulation to display the age conditional means of variables of interest.
4. Solve and compare policy functions with those obtained from CGM's Fortran 90 code
5. Present more detailed figures on discrepancies for the last periods of life.
6. Use HARK to compare the limiting MPC to the theoretical result obtained when there is no income risk and no riskless asset.
7. Turn off all shocks and check if consumption converges to its analytical perfect foresight solution

```

We didn't provide a docker image name in the  `nbreproduce` command as we want to create the docker container using the default (`econark/econ-ark-notebook:latest`) image. We could have provided a different image and a different bash script:
```
$ nbreproduce --docker econark/econ-ark-notebook:0.10.7 custom_reproduce_script.sh
```