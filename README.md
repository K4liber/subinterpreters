# Per-interpreter GIL for utilizing multiple cores within a single Python process

## Intro

The repository is a small exercise of how one can use a newly introduced `Python` feature called a `Per-interpreter GIL`[[5]](#b5). `Per-interpreter GIL` allows for utilizing multiple cores within a single Python process.

The feature was accepted as a solution for multi-core `Python` and it is already available<sup>[1](#f1)</sup> through `Python/C API` starting from `Python` version `3.12`. Pythonic interface for the feature will come together with the next `Python` version `3.13` (coming out on October 2024).

If you would like to skip the theoretical aspects and go straight to the practical example, please go right away to the section [Play with a per-interpreter GIL yourself](#playground).

## Technicalities 

#### Units of program execution

`Thread` and `Process` are two fundamental units of execution. Although both are related to how a computer executes tasks, they have different characteristics and serve different roles. It is recommended to understand what is showed on the image below in order to proceed with the article.

![alt text](images/ThreadDiagram.png)  
Figure 1. *Typical relationsip between
threads and processes* [[2]](#b2)

#### What is a thread scheduler?

The `thread scheduler` is a fundamental part of modern operating systems and programming environments that manages the execution of threads in a multi-threaded application. Its primary responsibility is to allocate CPU time to different threads, ensuring fair execution and efficient utilization of system resources. Thread scheduling is crucial for achieving concurrency, responsiveness, and efficient use of hardware. [https://medium.com/@sadigrzazada20/the-thread-scheduler-4c40c6143009]

#### What is a python interpreter?

A `python interpreter` is a computer program that converts python code into machine code.

#### What is GIL?

*The mechanism used by the CPython interpreter to assure that only one thread executes Python bytecode at a time. This simplifies the CPython implementation by making the object model (including critical built-in types such as dict) implicitly safe against concurrent access.*[[2]]https://docs.python.org/3/glossary.html#term-global-interpreter-lock

#### Is GIL only slowing down my multi-threaded programs or is it any useful?

`GIL` simplifies developers lifes. For example, performing the most common operations on a dictionary shared between multiple threads will not result in a race condition or corruption of the data within the dictionary. Moreover, when you are reading or writing from a file or socket the GIL is released allowing multiple threads to run in parallel. The `GIL` is smart, it tries to help, you need to have more trust in `GIL`.

#### What about pure python functions? Is it safe to execute them using multiple threads running at the same time, witihin a single process?

<a name="shared_state"></a>From the perspective of a Python developer who defines a pure function based solely on the absence of explicit shared state manipulation within the function's code, there are still implicit actions performed by the CPython interpreter that can modify shared state.

TODO clean this mess up

For example, `Reference Counts` + `String interning`.

`Reference Counts` is a mechanism that involves such implicit actions. Every object in Python has an associated reference count that the garbage collector uses to determine when its memory can be freed. When you create, copy, or delete any Python object (even locals within pure functions), it affects the reference count. This operation must be protected by the GIL because it changes the global state of the interpreter. Without the GIL, two threads that increment or decrement the reference count of the same object concurrently might corrupt the reference count, leading to memory leaks or premature deallocation.

Nice article about `String interning`: https://medium.com/@bdov_/https-medium-com-bdov-python-objects-part-iii-string-interning-625d3c7319de 

TLTR:

Python tries its best to exclusively intern the strings that are most likely to be reused — identifier strings. Identifier strings include the following:

- Function and class names
- Variable names
- Argument names
- Dictionary keys
- Attribute names

Using shared cached objects in this manner and manipulating their reference counts unsafely can result in serious issues. This example highlights why it's crucial for extension modules, especially those releasing the GIL, to manage the lifecycle and reference counts of Python objects correctly.

```
>>> a = "Michael"
>>> b = "Michael"
>>> id(a), id(b), a is b
(139691346551904, 139691346551904, True)
```

![alt text](images/sharing.png)  
Figure 1. *Demystifying CPython Shared Objects* [[10]](#b10)

To conclude:

*Is it safe to not using GIL for executing pure python functions in multiple threads?*

No. Those functions aren't pure on the level on which the GIL operates. There is still a state shared by multiple threads while exececuting on the python intepreter level.

## Per-interpreter GIL

I would like to take a step back and shortly describe my interest in the `Per-interpreter GIL`.

#### Bulding python objects using data from files

Once I was struggling with a speed of loading the input data for some computation program. Loading was taking several seconds because of loading multipl files with a table format data (excel/csv), laying on the storage.

I tried to use multi-threading and load each file in a seperate thread. 
It gave a solid speed-up of the loading. Unfortunetly, due to GIL existence, all CPU operations were been able to execute on a single core at a given time.

#### Multi-processing as a way to do it

Since there are some CPU operations involved (loading data into memory as `pdtable` objects) 
I have tried to use multi-processing instead. The performance, when it comes to speed, was pretty the same as using multi-threading. The main process needs to spawn itself multiple times and it takes some time. I have experienced a long spawning time while debugging in VSCode, on the regular run it is not that slow.

#### We should not need multiple processes.

But why do we even need to create a seperate process for such a pure function execution? We do not care about synchronization of any data here and we do not need to ensure thread-safe sharing of any explicity defined state. We just want to run a function with a specific input and get the results back to the main thread (the one that starts and runs a `Python` interpreter). Shouldn't it be allowed to run on mutli-cores? I emphasize again, we do not care about any data/state synchronization. As I mentioned [here](#shared_state), it is not possible, due to a shared state implicite created by `Python` intepreter. 

#### Here it comes ... A Per-Interpreter GIL.

After some time, I was reading about new features of `python` version `3.12` and I came across `PEP 684 – A Per-Interpreter GIL`[5]. 
Somebody creates an implementation of the real multi-core behaviour in `Python`! First version of `Python` was released in 1991. Multiple cores processors started to be used on daily basis a bit later (The first commercial multicore processor architecture was Power 4 processor developed by IBM in 2001 [TODO source]). It seems like there is a lot of work to be done 
since the whole architecture of python is not really supportive to the idea. The work already started and is ongoing for a few years with 
multiple PEP's with parts supporting the final implementation.

#### What other programming languages can offer on the multi-core approach? 

`JavaScript`, similary as `Python`, is an interpreted language. One way to achieve concurrency in JavaScript is through the use of `Web Workers`, which are JavaScript scripts that run in the background and can perform tasks independently of the main thread. 

`Web Workers` (first published in 3 April 2009[[8]](#b8)) provide true concurrency for CPU-bound tasks by utilizing multiple cores. Web Workers create separate threads and run within a single process.

Communication between threads in `Python` can be done through shared memory or thread-safe data structures, while `Web Workers` only communicate through message passing, which limits the potential for race conditions and makes state management simpler at the cost of being potentially less efficient for certain kinds of data exchange.

`C#` seems to have (according to my minimal knowledge of `C#`) a pretty solid library for a multi-core utilization called `TPL`. It was released 
together with version 4.0 of the .NET Framework (year 2010).


#### Are there any real-life use cases for a per-Interpreter GIL?  

TODO ... https://peps.python.org/pep-0684/#motivation

Benchmark from the yt video [3] ...

#### Are there any alternatives for utilizing multiple cores within a single Python process?

https://peps.python.org/pep-0684/#rationale

#### What have we learned?

- `Python` PEPs can sometimes be very broad and require a lot of work.
- Initial decisions have a huge impact on the following features of a 
programming language (e.g. GIL).
- The full multi-core potential in `Python` is 
hard to achieve since the initial decision on 
the language behaviour. `GIL` is a simple solution for the thread-safety problems, but 
it is a blocker for utilizing multiple cores.
- `Per-interpreter GIL` seems like a promising 
approach for multi-core utilization. But lets wait for 3.13 and a solid interface, together with 
external modules support.
- `Python` has a lot of cons, but a lot of of people still love it, mostly due to the  great, initial simplicity of writing programs in `Python`. Prototyping with `Python` is easy and fast.

## <a name="playground"></a>Play with a per-interpreter GIL yourself

I have created a simple application with a GUI (using QT) in order to show an example of using `Subinterpreter` as an unit of execution. I strongly encourage you to playaround with the code.

There is already an implemention[1] of a Python interface for `interpreters` C API, but I found it too complex for my case (running a bunch of pure functions) and I have introduced the more briefly implementation.


### Environment preparation
#### Install pyqt

`sudo apt install python3-qtpy`

#### Create Conda env

Firstly, install the `Conda` package manager if you do not have it yet: https://conda.io/projects/conda/en/latest/user-guide/install/index.html.

I am not a huge fan of a `Conda` package manager since it is really slow. Using `mamba`, a re-implementation of `Conda` make the `Conda` environemnts managing acceptable when it comes to timing of creating/updating python environments.

Installing `mamba` in your base conda environment let you reuse it every time you create a new `Conda` environment.

In order to create an environment, type the following commads:  

1. `conda install -c conda-forge mamba`  
2. `mamba env create -f environment.yml --prefix=<path_to_env_dir>`  

### A `Per-interpreter` runner<sup>[2](#f2)</sup>

TODO python example execution intructions ...

### [EXTRA] JS `Web-workers` runner<sup>[2](#f2)</sup>

TODO JS example execution instructions ...

### [EXTRA] C# `TPL` runner

TODO C# example execution intructions ... (ChatGPT helped with the implementation of this simple program)

# Footnotes

<a name="f1"></a>*1. Still me need to wait for python modules to be compatible with `Per-interpreter GIL` approach. For example, `numpy` is not working yet ... TODO make it clear.*  
<a name="f2"></a>*2. Sometimes, on my machine with Ubuntu, CPUs are not fully utilize while using `per-interpreter GIL`. I can only guess that the reason is not good enough context switching, but I didnt make a deeper examination. The same situation we encounter with `Web Workers` and since those two approaches 
share the same thread scheduler on my machine, I am leaning towards blaming a `thread scheduler` for the situation.*

# Bilbiography
<a name="b1"></a>[1] `Python interface for the "intepreters" C API`, https://github.com/jsbueno/extrainterpreters  

<a name="b2"></a>[2] Neil Coffey, `How threads work: more details`, https://www.javamex.com/tutorials/threads/how_threads_work.shtml

<a name="b3"></a>[3] Eric Snow, `A Per-Interpreter GIL: Concurrency and Parallelism with Subinterpreters`, https://www.youtube.com/watch?v=3ywZjnjeAO4  

<a name="b4"></a>[4] Eric Snow, `PEP 554 – Multiple Interpreters in the Stdlib`, https://peps.python.org/pep-0554/  

<a name="b5"></a>[5] Eric Snow, `PEP 684 – A Per-Interpreter GIL`, https://peps.python.org/pep-0684/  

<a name="b6"></a>[6] Microsoft, `TPL`, https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/task-parallel-library-tpl

<a name="b7"></a>[7] wikipedia, `Parallel Extensions`, https://en.wikipedia.org/wiki/Parallel_Extensions

<a name="b8"></a>[8] wikipedia, `Web worker`, https://en.wikipedia.org/wiki/Web_worker

[9] https://medium.com/@bdov_/https-medium-com-bdov-python-objects-part-ii-demystifying-cpython-shared-objects-fce1ec86dd63

[10] https://medium.com/@bdov_/https-medium-com-bdov-python-objects-part-ii-demystifying-cpython-shared-objects-fce1ec86dd63
