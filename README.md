# PUFFY

A collection of modules with zero-dependencies to help manage common programming tasks.

```
pip install puffy
```

Usage examples:

```python
from puffy.error import catch_errors

# This function will never fail. Instead, the error is safely caught.
@catch_errors
def fail():
    raise Exception("Failed")
    return "yes"

err, resp = fail() # `err` and `resp` are respectively None and Object when the function is successull. Otherwise, they are respectively StackedException and None.
```

```python
from puffy.object import JSON as js

obj = js({ 'hello':'world' })
obj['person']['name'] = 'Nic' # Notice it does not fail.
obj.s('address.line1', 'Magic street') # Sets obj.address.line1 to 'Magic street' and return 'Magic street'
```

# Table of contents

> * [APIs](#apis)
>	- [`error`](#error)
>		- [Basic `error` APIs - Getting in control of your errors](#basic-error-apis---getting-in-control-of-your-errors)
>		- [Nested errors and error stack](#nested-errors-and-error-stack)
>		- [Managing errors in `async/await` corountines](#managing-errors-in-asyncawait-corountines)
>	- [`object`](#object)
>		- [`JSON` API](#json-api)
> * [Dev](#dev)
>	- [CLI commands](#cli-commands)
>	- [Install dependencies with `easypipinstall`](#install-dependencies-with-easypipinstall)
>	- [Linting, formatting and testing](#linting-formatting-and-testing)
>		- [Ignoring `flake8` errors](#ignoring-flake8-errors)
>		- [Skipping tests](#skipping-tests)
>		- [Executing a specific test only](#executing-a-specific-test-only)
>	- [Building and distributing this package](#building-and-distributing-this-package)
> * [FAQ](#faq)
> * [References](#references)
> * [License](#license)

# APIs
## `error`

The `error` module exposes the following APIs:
- `catch_errors`: A higher-order function that returns a function that always return a tuple `(error, response)`. If the `error` is `None`, then the function did not fail. Otherwise, it did and the `error` object can be used to build an error stack.
- `StackedException`: A class that inherits from `Exception`. Use it to stack errors.

### Basic `error` APIs - Getting in control of your errors

```python
from puffy.error import catch_errors

# This function will never fail. Instead, the error is safely caught.
@catch_errors
def fail():
    raise Exception("Failed")
    return "yes"

err, resp = fail() 

print(resp) # None
print(type(err)) # <class 'src.puffy.error.StackedException'> which inherits from Exception
print(str(err)) # Failed
print(len(err.stack)) # 1
print(str(err.stack[0])) # Failed
print(err.stack[0].__traceback__) # <traceback object at 0x7fc69066bf00>

# Use the `strinfigy` method to extract the full error stack details.
print(err.strinfigy()) 
# error: Failed
#   File "blablabla.py", line 72, in safe_exec
#     data = ffn(*args, **named_args)
#   File "blablabla.py", line 28, in fail
#     raise Exception("Failed")
```

### Nested errors and error stack

```python
from puffy.error import catch_errors, StackedException

# This function will never fail. Instead, the error is safely caught.
@catch_errors("Should fail")
def fail():
    err, resp = fail_again()
    if err:
        raise StackedException("As expected, it failed!", err) 
        # StackedException accepts an arbitrary number of inputs of type str or Exception:
        # 	- raise StackedException(err) 
        # 	- raise StackedException('This', 'is', 'a new error') 
    return "yes"

@catch_errors("Should fail again")
def fail_again():
    raise Exception("Failed again")
    return "yes"

err, resp = fail()

print(len(err.stack)) # 4
print(str(err.stack[0])) # Should fail
print(str(err.stack[1])) # As expected, it failed!
print(str(err.stack[2])) # Should fail again
print(str(err.stack[3])) # Failed again

# Use the `strinfigy` method to extract the full error stack details.
print(err.strinfigy()) 
# error: Should fail
#   File "blablabla.py", line 72, in fail
# error: As expected, it failed!
#   File "blablabla.py", line 72, in fail
# error: Should fail again
#   File "blablabla.py", line 72, in fail
# error: Failed again
#   File "blablabla.py", line 72, in safe_exec
#     data = ffn(*args, **named_args)
#   File "blablabla.py", line 28, in fail_again
#     raise Exception("Failed")
```

### Managing errors in `async/await` corountines

```python
from puffy.error import async_catch_errors
import asyncio

# This function will never fail. Instead, the error is safely caught.
@async_catch_errors
async def fail():
    await asyncio.sleep(0.01)
    raise Exception("Failed")
    return "yes"

loop = asyncio.get_event_loop()
err, resp = loop.run_until_complete(fail())

print(resp) # None
print(type(err)) # <class 'src.puffy.error.StackedException'> which inherits from Exception
print(str(err)) # Failed
print(len(err.stack)) # 1
print(str(err.stack[0])) # Failed
print(err.stack[0].__traceback__) # <traceback object at 0x7fc69066bf00>

# Use the `strinfigy` method to extract the full error stack details.
print(err.strinfigy()) 
# error: Failed
#   File "blablabla.py", line 72, in safe_exec
#     data = ffn(*args, **named_args)
#   File "blablabla.py", line 28, in fail
#     raise Exception("Failed")
```

## `object`
### `JSON` API

```python
from puffy.object import JSON as js

obj = js({ 'hello':'world' })
obj['person']['name'] = 'Nic' # Notice it does not fail.
obj.s('address.line1', 'Magic street') # Sets obj.address.line1 to 'Magic street' and return 'Magic street'

print(obj['person']['name']) # Nic
print(obj) # { 'hello':'world', 'person': { 'name': 'Nic' } }
print(obj.g('address.line1')) # Magic street
print(obj) # { 'hello':'world', 'person': { 'name': None }, 'address': { 'line1': 'Magic street' } }
print(obj.g('address.line2')) # Nonce
print(obj) # { 'hello':'world', 'person': { 'name': None }, 'address': { 'line1': 'Magic street', line2: None } }
```

# Dev
## CLI commands

`make` commands:

| Command | Description |
|:--------|:------------|
| `make b` | Builds the package. |
| `make p` | Publish the package to https://pypi.org. |
| `make bp` | Builds the package and then publish it to https://pypi.org. |
| `make bi` | Builds the package and install it locally (`pip install -e .`). |
| `make install` | Install the dependencies defined in the `requirements.txt`. This file contains all the dependencies (i.e., both prod and dev). |
| `make install-prod` | Install the dependencies defined in the `prod-requirements.txt`. This file only contains the production dependencies. |
| `make n` | Starts a Jupyter notebook for this project. |
| `make t` | Formats, lints and then unit tests the project. |
| `make t testpath=<FULLY QUALIFIED TEST PATH>` | Foccuses the unit test on a specific test. For a concrete example, please refer to the [Executing a specific test only](#executing-a-specific-test-only) section. |
| `easyi numpy` | Instals `numpy` and update `setup.cfg`, `prod-requirements.txt` and `requirements.txt`. |
| `easyi flake8 -D` | Instals `flake8` and update `setup.cfg` and `requirements.txt`. |
| `easyu numpy` | Uninstals `numpy` and update `setup.cfg`, `prod-requirements.txt` and `requirements.txt`. |

## Install dependencies with `easypipinstall`

`easypipinstall` adds two new CLI utilities: `easyi` (install) and `easyu` (uninstall).

Examples:
```
easyi numpy
```

This installs `numpy` (via `pip install`) then automatically updates the following files:
- `setup.cfg` (WARNING: this file must already exists):
	```
	[options]
	install_requires = 
		numpy
	```
- `requirements.txt` and `prod-requirements.txt`

```
easyi flake8 black -D
```

This installs `flake8` and `black` (via `pip install`) then automatically updates the following files:
- `setup.cfg` (WARNING: this file must already exists):
	```
	[options.extras_require]
	dev = 
		black
		flake8
	```
- `requirements.txt` only, as those dependencies are installed for development purposes only.

```
easyu flake8
```

This uninstalls `flake8` as well as all its dependencies. Those dependencies are uninstalled only if they are not used by other project dependencies. The `setup.cfg` and `requirements.txt` are automatically updated accordingly.

## Linting, formatting and testing

```
make t
```

This command runs the following three python executables:

```
black ./
flake8 ./
pytest --capture=no --verbose $(testpath)
```

- `black` formats all the `.py` files, while `flake8` lints them. 
- `black` is configured in the `pyproject.toml` file under the `[tool.black]` section.
- `flake8` is configured in the `setup.cfg` file under the `[flake8]` section.
- `pytest` runs all the `.py` files located under the `tests` folder. The meaning of each option is as follow:
	- `--capture=no` allows the `print` function to send outputs to the terminal. 
	- `--verbose` displays each test. Without it, the terminal would only display the count of how many passed and failed.
	- `$(testpath)` references the `testpath` variable. This variable is set to `tests` (i.e., the `tests` folder) by default. This allows to override this default variable with something else (e.g., a specific test to only run that one).

### Ignoring `flake8` errors

This project is pre-configured to ignore certain `flake8` errors. To add or remove `flake8` errors, update the `extend-ignore` property under the `[flake8]` section in the `setup.cfg` file.

### Skipping tests

In your test file, add the `@pytest.mark.skip()` decorator. For example:

```python
import pytest

@pytest.mark.skip()
def test_self_describing_another_test_name():
	# ... your test here
```

### Executing a specific test only

One of the output of the `make t` command is list of all the test that were run (PASSED and FAILED). For example:

```
tests/error/test_catch_errors.py::test_catch_errors_basic PASSED
tests/error/test_catch_errors.py::test_catch_errors_wrapped PASSED
tests/error/test_catch_errors.py::test_catch_errors_nested_errors PASSED
tests/error/test_catch_errors.py::test_catch_errors_StackedException_arbitrary_inputs FAILED
```

To execute a specific test only, add the `testpath` option with the test path. For example, to execute the only FAILED test in the example above, run this command:

```
make t testpath=tests/error/test_catch_errors.py::test_catch_errors_StackedException_arbitrary_inputs
```

## Building and distributing this package

> Tl;dr, Update the version in the `setup.cfg` file, and then run `make bp` to build and publish your package to https://pypi.org.

__IMPORTANT:__ First, make sure you've updated the version in the the `setup.cfg` file. Ideally, you should also tag your git repository `git tag vx.x.x`.

To build your package, run:

```
make b
```

This command is a wrapper around `python3 -m build`.

To build and publish your package to https://pypi.org, run:

```
make p
```

This command is a wrapper around the following commands:

```
python3 -m build; \
twine upload dist/*
```

Those two steps have been bundled in a single command:

```
make bp
```

> __IMPORTANT:__ Don't forget to update the version in the the `setup.cfg` file. Ideally, you should also tag your git repository `git tag vx.x.x`.

To test your package locally before deploying it to https://pypi.org, you can run build and install it locally with this command:

```
make bi
```

This command buils the package and follows with `pip install -e .`.

# FAQ

# References

# License

BSD 3-Clause License

```
Copyright (c) 2019-2023, Cloudless Consulting Pty Ltd
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

