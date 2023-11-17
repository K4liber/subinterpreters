# Story behind this repository
...

# Technicalities

`Thread` and `Process` are two fundamental units of execution. Although both are related to how a computer executes tasks, they have different characteristics and serve different roles.

`Subinterpreter` ...

# Play with `subinterpreter` yourself

I have created a simple application with a GUI (using QT) in order to show an example of using `subinterpreter` as an unit of execution. 
I strongly encourage you to playaround with the code. There is already an implemention[1] of a Python interface for `interpreters` C API, but I found it too complex for my case and I have introduced the more briefly implementation ...

## Environment
### Ubuntu

`sudo apt install python3-qtpy`

### Conda env

Firstly, install the `Conda` package manager if you do not have it yet: https://conda.io/projects/conda/en/latest/user-guide/install/index.html.

I am not a huge fan of a `Conda` package manager since it is really slow. Using `mamba`, a re-implementation of `Conda` make the `Conda` environemnts managing acceptable when it comes to timing of creating/updating python environments.

Installing `mamba` in your base conda environment let you reuse it every time you create a new `Conda` environment.

In order to create an environment, type the following commads:  

1. `conda install -c conda-forge mamba`  
2. `mamba env create -f environment.yml --prefix=<path_to_env_dir>`  

## Runner

# Bilbiography
[1] `Python interface for the "intepreters" C API`, https://github.com/jsbueno/extrainterpreters  
[2] https://www.reddit.com/r/Python/comments/16yw7zt/what_are_the_differences_between_python_312/  
[3] Eric Snow, `A Per-Interpreter GIL: Concurrency and Parallelism with Subinterpreters`, https://www.youtube.com/watch?v=3ywZjnjeAO4
