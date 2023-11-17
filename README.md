# Subinterpreters

The repository is a small exercise of how one can use a newly introduced 
unit of execution called `Subinterpreter`. If you are interested in the whole story behind this repository, please read the whole document. 
If you value results and your time more than stories, please go to section `Play with a Subinterpreter yourself`.

# Story behind this repository

### All the evil of GIL

While I was working on a task in one of the projects I struggle with a speed of loading the input data. 
It was taking several seconds because of loading multiple files with a table format data (excel/csv). 
I tried to use multi-threading and load each file in a seperate thread. 
It gave a solid speed-up of the loading. Unfortunetly (I know, there are good reasons for that), python interpreter uses GIL[TODO link] mechanism and because of that, only a single thread (main one or a child one) can be running at a time.

### Multi-processing as a way to do it

Since there are a lot of CPU operations involved (loading data from a storage into memory as `pdtable` objects) 
I have tried to use multi-processing as well. The performance, when it comes to speed, was pretty the same as using multi-threading. The reason was that the main process needs to spawn itself multiple times and it 
takes some time (btw. I have experienced a long spawning time while debugging in VSCode, on the regular run it is not so slow).

### We do not need multiple processes, basta!

But why do we even need to create a seperate process for such a pure function execution? We do not care about synchronization of any data here. We just want to run a function with a specific input and get the results back to the main thread (the one that is running an original python interpreter). Shouldn't it be allowed if we agree with a non-synchornization requirement? Probably it should, but there is no 
such a thing in python yet ...

### Eureka! Subinterpreter.

After some time I was reading about new features of `python` version `3.12` and I came across `PEP 554 – Multiple Interpreters in the Stdlib`[4]. 
Somebody, finally, creates an implementation of ... First version of `Python` was released in 1991. I know, that multiple cores processors started to be used on daily basis a bit later (The first commercial multicore processor architecture was Power 4 processor developed by IBM in 2001 [TODO source]), but still it took a lot of time to be introduced.  
If it took so much time (minimum several years) maybe it was not so crucial? Maybe it is not usable at all and it is only a fun fact 
and an exercise? We will come back to this, but first lets find out ...  

### ... what solutions other languages can offer on this topic? 

Green threads https://en.wikipedia.org/wiki/Green_thread

`JavaScript`, similary as `Python`, is an interpreted language and doesn't require to compile before execution. One way to achieve concurrency in JavaScript is through the use of web workers, which are JavaScript scripts that run in the background and can perform tasks independently of the main thread. 

https://www.c-sharpcorner.com/UploadFile/1c8574/thread-safety369/

### Can a Python subinterpreter be useful in some way?  

TODO ...


# Technicalities

`Thread` and `Process` are two fundamental units of execution. Although both are related to how a computer executes tasks, they have different characteristics and serve different roles.

`Subinterpreter` ...

# Play with a `Subinterpreter` yourself

I have created a simple application with a GUI (using QT) in order to show an example of using `Subinterpreter` as an unit of execution. 
I strongly encourage you to playaround with the code. There is already an implemention[1] of a Python interface for `interpreters` C API, but I found it too complex for my case (running a bunch of pure functions) and I have introduced the more briefly implementation ...

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
[4] Eric Snow, `PEP 554 – Multiple Interpreters in the Stdlib`, https://peps.python.org/pep-0554/  
