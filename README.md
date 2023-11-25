# Per-interpreter GIL for utilizing multiple cores within a single Python process

## Intro

The repository is a small exercise of how one can use a newly introduced `Python` feature which is a `per-interpreter GIL`. 

The feature is an accepted solution for multi-core `Python`. It is already available through `Python/C API` starting from `Python` version `3.12`. 

If you value results and your time more than stories, please go right away to the section [Play with a per-interpreter GIL yourself](#playground) and see an example of `per-interpreter GIL` usage.

## Technicalities 

#### What units of program execution do we have?

`Thread` and `Process` are two fundamental units of execution. Although both are related to how a computer executes tasks, they have different characteristics and serve different roles.

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

`GIL` simplifies developers lifes. For example, performing the most common operations on a dict shared between multiple threads will not result in a race condition or corruption of the data within the dict. Moreover, when you are reading or writing from a file or socket the GIL is released allowing multiple threads to run in parallel. The `GIL` is smart, it tries to help, you need to have more trust in `GIL`.

#### What about pure python functions? Is it safe to execute them using multiple threads running at the same time, witihin a single process?

Even in the context of executing pure functions, which by definition do not modify any shared state or have side effects, multiple threads can still affect the shared state of the Python interpreter, for example, `Reference Counts`. Every object in Python has an associated reference count that the garbage collector uses to determine when its memory can be freed. When you create, copy, or delete any Python object (even locals within pure functions), it affects the reference count. This operation must be protected by the GIL because it changes the global state of the interpreter. Without the GIL, two threads that increment or decrement the reference count of the same object concurrently might corrupt the reference count, leading to memory leaks or premature deallocation.

#### Once again: Is there a way to release the GIL for pure functions using python?

In short, the answer is NO. Those functions aren't pure on the level on which the GIL operates.[[9]](#b9)

```
def f(t):
    x = 16 * sin(t) ** 3
    y = 13 * cos(t) - 5 * cos(2*t) - 2 * cos(3*t) - cos(4*t)
    return (x, y)
```

```
>>> dis.dis(f)
  2           0 LOAD_CONST               1 (16)
              2 LOAD_GLOBAL              0 (sin)
              4 LOAD_FAST                0 (t)
              6 CALL_FUNCTION            1
              8 LOAD_CONST               2 (3)
             10 BINARY_POWER
             12 BINARY_MULTIPLY
             14 STORE_FAST               1 (x)
             ...
```

# Per-interpreter GIL

#### Bulding python objects using data from files

Once I was struggling with a speed of loading the input data for some computation program. Loading was taking several seconds because of loading multipl files with a table format data (excel/csv), laying on the storage.

I tried to use multi-threading and load each file in a seperate thread. 
It gave a solid speed-up of the loading. Unfortunetly, due to GIL existence, all CPU operations were been able to execute on a single core at a given time.

#### Multi-processing as a way to do it

Since there are some CPU operations involved (loading data into memory as `pdtable` objects) 
I have tried to use multi-processing instead. The performance, when it comes to speed, was pretty the same as using multi-threading. This was because the main process needs to spawn itself multiple times and it takes some time. I have experienced a long spawning time while debugging in VSCode, on the regular run it is not so slow.

#### We should not need multiple processes.

But why do we even need to create a seperate process for such a pure function execution? We do not care about synchronization of any data here and we do not need to ensure thread-safe sharing of any state. We just want to run a function with a specific input and get the results back to the main thread (the one that is running the main `Python` interpreter). Shouldn't it be allowed to run on mutli-cores? I emphasize again, we do not care about any data/state synchronization. As I mentioned before, it is not possible, due to a shared state between threads within a single python interpreter run.

### Here it comes ... A Per-Interpreter GIL.

After some time, I was reading about new features of `python` version `3.12` and I came across `PEP 684 – A Per-Interpreter GIL`[5]. 
Somebody, creates an implementation of the real multi-core behaviour in `Python`. First version of `Python` was released in 1991. Multiple cores processors started to be used on daily basis a bit later (The first commercial multicore processor architecture was Power 4 processor developed by IBM in 2001 [TODO source]). It seems like there is a lot of work to be done 
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
the language behaviour. `GIL` is a simple solution for the thead-safety problems, but 
it is a blocker for utilizing multiple cores.
- `per-interpreter GIL` seems like a promising 
approach for multi-core ... But lets wait for 3.13 and a solid interface, together with 
external modules support.
- `Python` has a lot of cons, but a lot of of people still love it, mostly due to the  great, initial simplicity of writing programs in `Python`. Prototyping with `Python` is easy and fast.

# <a name="playground"></a>Play with a per-interpreter GIL yourself

I have created a simple application with a GUI (using QT) in order to show an example of using `Subinterpreter` as an unit of execution. I strongly encourage you to playaround with the code.

There is already an implemention[1] of a Python interface for `interpreters` C API, but I found it too complex for my case (running a bunch of pure functions) and I have introduced the more briefly implementation ...

TODO python example execution intructions ...

TODO JS example execution instructions ...

TODO C# example execution intructions ... (ChatGPT helped with the implementation of this simple program)

Sometimes using `per-interpreter GIL`, CPUs are not fully utilize and I can only guess that the reason is not good enough context switching. The same situation we encounter with `Web Workers` ...


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
<a name="b1"></a>[1] `Python interface for the "intepreters" C API`, https://github.com/jsbueno/extrainterpreters  

<a name="b2"></a>[2] Neil Coffey, `How threads work: more details`, https://www.javamex.com/tutorials/threads/how_threads_work.shtml

<a name="b3"></a>[3] Eric Snow, `A Per-Interpreter GIL: Concurrency and Parallelism with Subinterpreters`, https://www.youtube.com/watch?v=3ywZjnjeAO4  

<a name="b4"></a>[4] Eric Snow, `PEP 554 – Multiple Interpreters in the Stdlib`, https://peps.python.org/pep-0554/  

<a name="b5"></a>[5] Eric Snow, `PEP 684 – A Per-Interpreter GIL`, https://peps.python.org/pep-0684/  

<a name="b6"></a>[6] Microsoft, `TPL`, https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/task-parallel-library-tpl

<a name="b7"></a>[7] wikipedia, `Parallel Extensions`, https://en.wikipedia.org/wiki/Parallel_Extensions

<a name="b8"></a>[8] wikipedia, `Web worker`, https://en.wikipedia.org/wiki/Web_worker

[9] https://stackoverflow.com/a/65141099
