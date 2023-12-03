# Utilizing Multiple Cores in a Single Python Process with Per-interpreter GIL

## Intro

This repository presents a practical exploration of a relatively new feature in Python known as the `Per-interpreter GIL`[[5]](#b5). The `Per-interpreter GIL` enables the utilization of multiple cores within a single Python process.

This feature is accessible through the `Python/C API` starting from Python version 3.12<sup>[1](#f1)</sup>. A Pythonic interface for this feature is anticipated to be released with Python version 3.13 (coming out on October 2024).

Those eager to witness the `Per-interpreter GIL` in action can jump directly to the demo section titled [Play with Per-interpreter GIL yourself](#playground).

## Technicalities 

Before delving into the `Per-interpreter GIL`, it is beneficial to grasp the underlying concepts of threads and processes in the python context.


#### Threads vs. Processes: A Quick Summary*

**For a more detailed explanation, please see the [overview of Threads and Processes](#b2).*

`Threads` and `Processes` are two fundamental units of program execution. While both are integral to how a computer performs tasks, they possess distinct characteristics and fulfill different purposes. 

`Threads`: Lightweight units of execution that share the same memory space within a process, allowing for efficient task parallelism within a single application.

`Processes`: Independent units of execution, each with its own memory space, providing strong isolation but requiring more resources and complexity to communicate between them.

For a visual representation of how threads typically interact with processes, refer to Figure 1 below.

![alt text](images/ThreadDiagram.png)  
Figure 1. *Typical relationsip between
threads and processes* [[2]](#b2)

`Thread scheduler` is a fundamental part of modern operating systems and programming environments that manages the execution of threads in a multi-threaded application. Its primary responsibility is to allocate CPU time to different threads, ensuring fair execution and efficient utilization of system resources. Thread scheduling is crucial for achieving concurrency, responsiveness, and efficient use of hardware[[13]](#b13).

#### What is a python interpreter?

Python is an interpreted language. Interpreted languages do not need to be compiled to run. A program called an interpreter processes Python code at runtime, or "on the fly." For a more in-depth explanation of interpreters, you might find the [Interpreter Wikipedia article](#b14) helpful.

#### What is GIL?

*The mechanism used by the CPython interpreter to assure that only one thread executes Python bytecode at a time. This simplifies the CPython implementation by making the object model (including critical built-in types such as dict) implicitly safe against concurrent access.*[[15]](#b15)

#### Does the GIL Only Slow Down Multi-threaded Programs, or Does It Have Benefits?


While the `GIL` can limit the execution speed of multi-threaded Python programs, it greatly simplifies development. For instance, performing operations on a shared dictionary across multiple threads will not lead to race conditions or data corruption. 

Furthermore, the `GIL` is released during I/O operations, such as reading or writing to a file or socket, which allows threads to run in parallel in these scenarios. The GIL is designed to facilitate multi-threading, and understanding its behavior can help developers write more efficient code.

#### Can We Disable the GIL for Executing Pure Python Functions?


<a name="shared_state"></a>Disabling the GIL to execute a set of pure Python functions across multiple threads might seem safe, especially if those functions do not appear to manipulate shared state explicitly. However, the CPython interpreter performs certain implicit actions that may affect shared state. For example, operations altering `reference counts` and `string interning` are two mechanisms that involve shared state.


#### What are `Reference Counts`?

In Python, every object has an associated `reference count` that the garbage collector utilizes to determine when its memory can be released. Creating, copying, or deleting any Python object impacts the reference count. These operations must be protected by the GIL because they alter the interpreter's global state. Without the GIL, concurrent reference count modifications by two threads on the same object could corrupt the count, leading to memory leaks or premature deallocation.

#### What is `String interning`?

For a comprehensive explanation of `string interning`, please refer to [this article](#b12).

Python optimizes memory usage by interning strings that are likely to be reused, particularly identifier strings. These strings include:

- Function and class names
- Variable names
- Argument names
- Dictionary keys
- Attribute names


Unsafe manipulations of shared cached objects and their reference counts can lead to critical errors. This is why extension modules, especially those that release the GIL, must handle reference counts and the lifecycle of Python objects with care.


```python
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import partial


@dataclass
class Person:
    first_name: str
    last_name: str

    @property
    def last_name_object_address(self) -> str:
        return hex(id(self.last_name))


def get_jackson_sibling(name: str) -> Person:
    return Person(
        first_name=name,
        last_name='Jackson'
    )

tasks = []

with ThreadPoolExecutor(2) as executor:
    for first_name in ['Michael', 'Freddy']:
        task = executor.submit(partial(get_jackson_sibling, first_name))
        tasks.append(task)
    
siblings = [task.result() for task in tasks]

for sibling in siblings:
    print(f'Hello {sibling.first_name}!')

if siblings[0].last_name_object_address == siblings[1].last_name_object_address:
    address = siblings[0].last_name_object_address
    print(f'Same memory address detected: {address}')
```

Output:

```
Hello Michael!
Hello Freddy!
Same memory address detected: 0x7fb1080be9f0
```

As demonstrated, Python sometimes reuses objects for efficiency reasons, such as with string interning, reducing memory usage.

![alt text](images/sharing.png)  
Figure 1. *Demystifying CPython Shared Objects* [[10]](#b10)

#### Conclusion: Is it Safe to Disable the GIL for Pure Python Functions in Multi-threaded Execution?

No, it is not safe. Even if functions appear pure at the code level, they may not be pure in the context of the CPython interpreter, which involves shared state access during execution.

## Per-interpreter GIL

I would like to take a step back and shortly describe my interest in the `Per-interpreter GIL`.

#### Bulding python objects using data from files

Once I was struggling with a speed of loading the input data for some computation program. Loading was taking several seconds because of sequantial loading of multiple files with a table format data (excel/csv), laying on the storage. Using `multi-threading` it gave a solid speed-up. Unfortunetly, due to GIL existence and some CPU oprations involved, I was utilizing only a single core.  

I have tried to use `multi-processing` instead. The performance, when it comes to speed, was pretty the same as using multi-threading. The main process needs to spawn itself multiple times and it takes some time. I have experienced a long spawning time while debugging in VSCode, on the regular run it was not that slow.

#### We should not need multiple processes.

But why do we even need to create a seperate process for such a pure function execution? We do not care about any explicity defined data/state synchronization. Shouldn't it be allowed to run on mutli-cores? As I mentioned [here](#shared_state), it is not possible, due to a shared state implicite created by `Python` intepreter. 

#### Here it comes ... A Per-Interpreter GIL.

While I was reading about new features of `python` version `3.12`, I came across `PEP 684 – A Per-Interpreter GIL`[5]. 
Somebody creates an implementation of the real multi-core behaviour in `Python`! First version of `Python` was released in 1991. Multiple cores processors started to be used on daily basis a bit later (The first commercial multicore processor architecture was POWER4 processor developed by IBM in 2001[[11]](#b11)). The work on a `Per-interpreter GIL` is ongoing for a few years with 
multiple PEP's supporting the final implementation. Curretly (`python 3.12`) we can use `Python/C API` to play around with the new multi-core approach. 

#### What other programming languages can offer on the multi-core approach? 

`JavaScript`, similary as `Python`, is an interpreted language. One way to achieve concurrency in JavaScript is through the use of `Web Workers`, which are JavaScript scripts that run in the background and can perform tasks independently of the main thread. 

`Web Workers` (first published in 3 April 2009[[8]](#b8)) provide true concurrency for CPU-bound tasks by utilizing multiple cores. Web Workers create separate threads and run within a single process.

Communication between threads in `Python` can be done through shared memory or thread-safe data structures, while `Web Workers` only communicate through message passing, which limits the potential for race conditions and makes state management simpler at the cost of being potentially less efficient for certain kinds of data exchange.

`C#` seems to have (according to my minimal knowledge of `C#`) a pretty solid library for a multi-core utilization called `TPL`. It was released 
together with version 4.0 of the .NET Framework (year 2010).


#### Are there any real-life use cases for a Per-Interpreter GIL?  

[Here](https://peps.python.org/pep-0684/#motivation) you can find a motivation behind a Per-interpreter GIL together with benefits coming from it.

There is one use case that comes to my mind: we need to create a server that handles complex requests. We need a single entrypoint for each request. A complex request contains many computation parts that can be parralized. Creating a seperate process for each part and then communicating the results can slow down the performance. In such cases, I guess we can safe some "overhead" time using Per-interpreter GIL.

A promising benchmark was performed and shown by the PEP author Eric Snow on PyCon US 2023[[3]](#b3). I encourage you to watch the full video.

TL;DW

Eric got some results, as he himself desribe them, magical results.

![alt text](images/magic.png)  
Figure 3. *Comparison between clients based on thread, process and Per-interpreter GIL.*

TODO Those results seems to be not possible.

#### Are there any alternatives for utilizing multiple cores within a single Python process?

https://peps.python.org/pep-0684/#rationale

#### What have we learned?

- Python Enhancement Proposals (PEPs) happens to be very broad and require a lot of work.
- Initial decisions have a huge impact on the following features of a 
programming language implementation (e.g. GIL in CPython).
- The full multi-core potential in `Python` is 
hard to achieve since the initial decision on 
the language behaviour. `GIL` is a simple solution for the thread-safety problems, but 
it is a blocker for utilizing multiple cores.
- `Per-interpreter GIL` seems like a promising 
approach for multi-core utilization. But lets wait for 3.13 and a python interface. I hope for the 
external modules support and the more mature implementation based on gathered experiences.
- `Python` has a lot of cons, but a lot of of people still love it, mostly due to the  great, initial simplicity of writing programs in `Python`. Prototyping with `Python` is easy and fast.

## <a name="playground"></a>Play with a Per-interpreter GIL yourself

I have created a simple application with a GUI (using QT) in order to show an example of using `Subinterpreter` as an unit of execution. I strongly encourage you to playaround with the code.

There is already an implemention[[1]](#b1) of a Python interface for `interpreters` C API, but I found it too complex for my case (running a bunch of pure functions) and I have introduced the more briefly implementation.


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

In order to run an example application using `Per-interpreter GIL` type:  

`conda activate <path_to_env_dir>`    
`python main_qt.py`


The application allows to compare python performance using tree different workers:
1. Thread-based
2. Process-based
3. Subinterpreter-based (thread-based with `Per-interpreter GIL`)

The implementation of a subinterpreter-based runner can be found in the [subinterpreters module](runner/subinterpreters.py). One can try more sublime callables than just generating a figonacci sequence by modifying the [callables module](job/callables.py).

### [EXTRA] JS `Web-workers` runner<sup>[2](#f2)</sup>

If you would like to see the JS `Web-workers` performance on the similar task, please type the follwing commands:

`cd js-web-workers`  
`python -m http.server`  

and go to `http://0.0.0.0:8000/` in the browser.

Communication through message passing is very intuitive. Because of that, I like `JS` even more. On top of that, I didnt realise how much JS is better than python when it comes to computations performance. Now I know why my browser is mining crypto on some web-pages. From the parasite perspective, mining is free and pretty efficient at the same time. BTW. I personally think that crypto mining is a waste of energy. Please spent your (or others) resources in more useful way.

### [EXTRA] C# `TPL` runner

If you would like to run the example, please make sure that you have a `.NET` environment installed. Then, type the following commands:

`cd DotNetTPL`  
`dotnet run Program.cs`

My experience in `C#` is so small that a Junior C# developer could point it doesn't really exist. That's why I'd like to tip my hat to ChatGPT as a thank you for helping me create this example. The example is the same performance test as we did with `Python` and `JS`. I use `BlockingCollection` as a communication mechanism between the main thread and workers threads. The implementation seems to much Javaish for me, as so the whole `C#` is. I guess I do not really like it since I do not deeply understand it.


# Footnotes

<a name="f1"></a>*1. Still we need to wait for python extension modules to be compatible with `Per-interpreter GIL` approach. For example, I was not able to import `numpy` in the code running with a subinterpreter. Maybe there is an easy workaround for that, but I didn't spend a lot of time to make it work.*  
<a name="f2"></a>*2. Sometimes, on my machine with Ubuntu, CPUs are not fully utilize while using `Per-interpreter GIL`. I can only guess that the reason is not good enough context switching, but I didnt make a deeper examination. The same situation we encounter with `Web Workers` and since those two approaches 
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

<a name="b9"></a>[9] https://medium.com/@bdov_/https-medium-com-bdov-python-objects-part-ii-demystifying-cpython-shared-objects-fce1ec86dd63

<a name="b10"></a>[10] https://medium.com/@bdov_/https-medium-com-bdov-python-objects-part-ii-demystifying-cpython-shared-objects-fce1ec86dd63

<a name="b11"></a>[11] wikipedia, `POWER4`, https://en.wikipedia.org/wiki/POWER4

<a name="b12"></a> [12] Brennan D Baraban, `String Interning`, https://medium.com/@bdov_/https-medium-com-bdov-python-objects-part-iii-string-interning-625d3c7319de

<a name="b13"></a> [13] Sadigrzazada, `The thread scheduler`, https://medium.com/@sadigrzazada20/the-thread-scheduler-4c40c6143009

<a name="b14"></a> [14] wikipedia, `Interpreter (computing)`, https://en.wikipedia.org/wiki/Interpreter_(computing)

<a name="b15"></a> [15] python.org, `Global Interpreter Lock`, https://docs.python.org/3/glossary.html#term-global-interpreter-lock
