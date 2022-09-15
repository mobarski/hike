# Hike

Hike is a library for automatically generating command line interfaces (CLIs) from Python scripts allowing selection and reordering of steps to run.

**Warning**: this is pre-alpha code - anything can change without a warning.



## Installation

To install Hike with pip, run: `pip install git+https://github.com/mobarski/hike` or  `pip install hike`  (**not yet**)



## Basic Usage

Create the file *example.py*:

```python
import hike

def hello_step10(ctx):
    "say hello"
    print("hello")

def hello_step20(ctx):
    "say world"
    print("world")

if __name__=="__main__":
    hike.run_cli()
```

Then, from the command like, you can run:

```
python example.py hello           # hello world
python example.py hello:20,10     # world hello
python example.py hello:10,10,20  # hello hello world
```

Running the script without any arguments (`python example.py`) will print the help:

```
USAGE: test.py [task1:[:steps]] [task2[:steps]] [--use variants]

steps - comma separated list of step identifiers; leave empty to select
        all the steps; use dash to specify ranges; example: '10,20,30-40,99'

variants - coma separated list of step variants to use; example: 'cpu,windows'


Available tasks: hello

hello steps:
├─ 10 -- say hello
└─ 20 -- say world
```



## Advanced Usage



### Using Hike in scripts

```python
hike.run_steps('hello')             # hello world
hike.run_steps('hello', [20,10])    # world hello
hike.run_steps('hello', [10,10,20]) # hello hello world
```



### Passing information from step to step

```python
def hello_step30(ctx):
    ctx['name'] = 'John'

def hello_step40(ctx):
    name = ctx['name']
    print(f"hello {name}")

hike.run_steps('hello', [30,40]) # hello John
```

The context dictionary can also be passed to the first step as an option to the *run_steps* function:

```python
hike.run_steps('hello', [40], ctx={'name':'Jane'}) # hello Jane
```



### Step variants

```python
def model_step10(ctx): ...
def model_step20_cpu(ctx): ...
def model_step20_gpu_default(ctx): ...
def model_step30_linux(ctx): ...
def model_step30_windows(ctx): ...
def model_step30_macos_default(ctx): ...
def model_step40(ctx): ...
```

```python
hike.run_steps('model', use=['default'])     # steps: 10, 20_gpu, 30_macos, 40
hike.run_steps('model', use=['cpu','linux']) # steps: 10, 20_cpu, 30_linux, 40
hike.run_steps('model') # steps: 10, 40
```

`python example.py model --use cpu,linux`



### Nested tasks

```python
def all_step10(ctx):
	"run all tasks (model, hello)"
	hike.run_steps('model', use=ctx.get('use'))
	hike.run_steps('hello')
```





## Planned features



### Checkpoints and resumptions

TODO



### Parallel execution

TODO



