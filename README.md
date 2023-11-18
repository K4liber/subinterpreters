# Per-interpreter GIL as a solution for multi-core Python

The repository is a small exercise of how one can use a newly introduced `Python` feature which is an usage of per-interpreter `GIL`. The feature is an accepted solution for multi-core `Python`. It is already available through Python/C API starting from `Python` version `3.12`. 

If you are interested in the whole story behind this repository, please read the whole document. 
If you value results and your time more than stories, please go to section `Play with a per-interpreter GIL yourself` and see what is currently available.

# Story behind this repository

### Before we start, let's recall some technicalities

`Thread` and `Process` are two fundamental units of execution. Although both are related to how a computer executes tasks, they have different characteristics and serve different roles.

`Subinterpreter` ...

### The GIL is the cause

While I was working on a task in one of the projects I struggle with a speed of loading the input data. 
It was taking several seconds because of loading multiple files with a table format data (excel/csv). 
I tried to use multi-threading and load each file in a seperate thread. 
It gave a solid speed-up of the loading. Unfortunetly, python interpreter uses GIL[TODO link] mechanism (trust me, there are good reason for GIL existence). Thanks to that, only a single thread (main one or a child thread) can be running at a time.

### Multi-processing as a way to do it

Since there are a lot of CPU operations involved (loading data from a storage into memory as `pdtable` objects) 
I have tried to use multi-processing instead. The performance, when it comes to speed, was pretty the same as using multi-threading. This was because the main process needs to spawn itself multiple times and it 
takes some time. I have experienced a long spawning time while debugging in VSCode, on the regular run it is not so slow. But the argument of slow spawning reinforces the need of an another approach for a multi-core `Python`.

### We do not need multiple processes, basta!

But why do we even need to create a seperate process for such a pure function execution? We do not care about synchronization of any data here and we do not need to ensure thread-safe sharing of any state. We just want to run a function with a specific input and get the results back to the main thread (the one that is running the main `Python` interpreter). Shouldn't it be allowed to run on mutli-cores? I emphasize again, we do not care about any data/state synchronization. Probably it should, but for my knowledge, there is no such a thing in python yet ...

### Eureka! A Per-Interpreter GIL.

After some time I was reading about new features of `python` version `3.12` and I came across `PEP 684 – A Per-Interpreter GIL`[5]. 
Somebody, finally, creates an implementation of the real multi-core behaviour in `Python`. First version of `Python` was released in 1991. Even thought multiple cores processors started to be used on daily basis a bit later (The first commercial multicore processor architecture was Power 4 processor developed by IBM in 2001 [TODO source]), it is still a lot of time until such mechanism was introduced. It seems like there is a lot of work to be done 
since the whole architecture of python is not really supportive to the idea. The work already started and is ongoing for a few years with 
multiple PEP's with parts supporting the final implementation.

### What other programming languages can offer on the multi-core approach? 

`JavaScript`, similary as `Python`, is an interpreted language and does not require to compile before execution. One way to achieve concurrency in JavaScript is through the use of web workers, which are JavaScript scripts that run in the background and can perform tasks independently of the main thread. 

`C#` ...
https://www.c-sharpcorner.com/UploadFile/1c8574/thread-safety369/

### Are there any real-life use cases for a per-Interpreter GIL?  

TODO ... https://peps.python.org/pep-0684/#motivation

Benchmark from the yt video [3] ...

### Are there any alternatives for multi-core python?

https://peps.python.org/pep-0684/#rationale

### What have we learned?

- `Python` PEPs can be really heavy and require a lot of work
- Initial decisions have a huge impact on the following features of a 
programming language (GIL again)
- ...

# Play with a per-interpreter GIL yourself

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
[5] Eric Snow, `PEP 684 – A Per-Interpreter GIL`, https://peps.python.org/pep-0684/