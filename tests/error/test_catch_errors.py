# Copyright (c) 2019-2023, Cloudless Consulting Pty Ltd.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# - To skip a test, use this decoractor: @pytest.mark.skip() (doc: https://docs.pytest.org/en/latest/how-to/skipping.html)
# - To only run a single test function, in the `makefile`, replace this command:
#
#       pytest --capture=no --verbose tests
#
#   with this:
#
#       pytest --capture=no --verbose tests/somemodule/test_some_test_name.py::test_self_describing_test_name

# import pytest  # uncomment this line to use the 'pytest' decorators
import sys
import re
import asyncio

sys.path.append(".")  # noqa # Adds higher directory to python modules path.

from src.puffy.error import catch_errors, async_catch_errors, StackedException as e


def test_catch_errors_basic():
    @catch_errors
    def fail():
        raise Exception("Failed")
        return "yes"

    err, resp = fail()
    assert err
    assert err.stack
    assert len(err.stack) == 1
    assert str(err.stack[0]) == "Failed"
    assert str(err) == "Failed"


def test_catch_errors_wrapped():
    @catch_errors("Should fail")
    def fail():
        raise Exception("Failed")
        return "yes"

    err, resp = fail()
    assert err
    assert err.stack
    assert len(err.stack) == 2
    assert str(err.stack[0]) == "Should fail"
    assert str(err.stack[1]) == "Failed"


def test_catch_errors_nested_errors():
    @catch_errors("Should fail")
    def fail():
        err, resp = fail_again()
        if err:
            raise e(err)
        return "yes"

    @catch_errors("Should fail again")
    def fail_again():
        raise Exception("Failed again")
        return "yes"

    err, resp = fail()
    assert err
    assert err.stack
    assert len(err.stack) == 3
    assert str(err.stack[0]) == "Should fail"
    assert str(err.stack[1]) == "Should fail again"
    assert str(err.stack[2]) == "Failed again"


def test_catch_errors_StackedException_arbitrary_inputs():
    @catch_errors("Should fail")
    def fail():
        err, resp = fail_again()
        if err:
            raise e("As expected, it failed!", err)
        return "yes"

    @catch_errors("Should fail again")
    def fail_again():
        raise Exception("Failed again")
        return "yes"

    err, resp = fail()
    assert err
    assert err.stack
    assert len(err.stack) == 4
    assert str(err.stack[0]) == "Should fail"
    assert str(err.stack[1]) == "As expected, it failed!"
    assert str(err.stack[2]) == "Should fail again"
    assert str(err.stack[3]) == "Failed again"


def test_catch_errors_arbitrary_inputs():
    @catch_errors("Should fail")
    def fail(name, age=41):
        err, resp = fail_again()
        if err:
            raise e(f"As expected, it failed for {name} (age:{age})", err)
        return "yes"

    @catch_errors("Should fail again")
    def fail_again():
        raise Exception("Failed again")
        return "yes"

    err, resp = fail("Peter", age=32)
    assert err
    assert err.stack
    assert len(err.stack) == 4
    assert str(err.stack[0]) == "Should fail"
    assert str(err.stack[1]) == "As expected, it failed for Peter (age:32)"
    assert str(err.stack[2]) == "Should fail again"
    assert str(err.stack[3]) == "Failed again"


def test_catch_errors_stringify_stack():
    @catch_errors("Should fail")
    def fail(name, age=41):
        err, resp = fail_again()
        if err:
            raise e(f"As expected, it failed for {name} (age:{age})", err)
        return "yes"

    @catch_errors("Should fail again")
    def fail_again():
        raise Exception("Failed again")
        return "yes"

    err, resp = fail("Peter", age=32)
    assert err
    assert err.stack
    stack_details = err.stringify()
    assert stack_details
    error_msgs = re.findall(r"error:\s(.*?)\n", stack_details)
    assert error_msgs
    assert len(error_msgs) == 4
    assert error_msgs[0] == "Should fail"
    assert error_msgs[1] == "As expected, it failed for Peter (age:32)"
    assert error_msgs[2] == "Should fail again"
    assert error_msgs[3] == "Failed again"


def test_catch_errors_basic_async_await():
    @async_catch_errors
    async def fail():
        await asyncio.sleep(0.01)
        raise Exception("Failed")
        return "yes"

    loop = asyncio.get_event_loop()
    err, resp = loop.run_until_complete(fail())
    assert err
    assert err.stack
    assert len(err.stack) == 1
    assert str(err.stack[0]) == "Failed"
    assert str(err) == "Failed"


def test_catch_errors_wrapped_async_await():
    @async_catch_errors("Should fail")
    async def fail():
        await asyncio.sleep(0.01)
        raise Exception("Failed")
        return "yes"

    loop = asyncio.get_event_loop()
    err, resp = loop.run_until_complete(fail())
    assert err
    assert err.stack
    assert len(err.stack) == 2
    assert str(err.stack[0]) == "Should fail"
    assert str(err.stack[1]) == "Failed"


def test_catch_errors_nested_errors_async_await():
    @async_catch_errors("Should fail")
    async def fail():
        err, resp = await fail_again()
        if err:
            raise e(err)
        return "yes"

    @async_catch_errors("Should fail again")
    async def fail_again():
        await asyncio.sleep(0.01)
        raise Exception("Failed again")
        return "yes"

    loop = asyncio.get_event_loop()
    err, resp = loop.run_until_complete(fail())
    assert err
    assert err.stack
    assert len(err.stack) == 3
    assert str(err.stack[0]) == "Should fail"
    assert str(err.stack[1]) == "Should fail again"
    assert str(err.stack[2]) == "Failed again"


def test_catch_errors_StackedException_arbitrary_inputs_async_await():
    @async_catch_errors("Should fail")
    async def fail():
        err, resp = await fail_again()
        if err:
            raise e("As expected, it failed!", err)
        return "yes"

    @async_catch_errors("Should fail again")
    async def fail_again():
        await asyncio.sleep(0.01)
        raise Exception("Failed again")
        return "yes"

    loop = asyncio.get_event_loop()
    err, resp = loop.run_until_complete(fail())
    assert err
    assert err.stack
    assert len(err.stack) == 4
    assert str(err.stack[0]) == "Should fail"
    assert str(err.stack[1]) == "As expected, it failed!"
    assert str(err.stack[2]) == "Should fail again"
    assert str(err.stack[3]) == "Failed again"


def test_catch_errors_arbitrary_inputs_async_await():
    @async_catch_errors("Should fail")
    async def fail(name, age=41):
        err, resp = await fail_again()
        if err:
            raise e(f"As expected, it failed for {name} (age:{age})", err)
        return "yes"

    @async_catch_errors("Should fail again")
    async def fail_again():
        await asyncio.sleep(0.01)
        raise Exception("Failed again")
        return "yes"

    loop = asyncio.get_event_loop()
    err, resp = loop.run_until_complete(fail("Peter", age=32))
    assert err
    assert err.stack
    assert len(err.stack) == 4
    assert str(err.stack[0]) == "Should fail"
    assert str(err.stack[1]) == "As expected, it failed for Peter (age:32)"
    assert str(err.stack[2]) == "Should fail again"
    assert str(err.stack[3]) == "Failed again"


def test_catch_errors_stringify_stack_async_await():
    @async_catch_errors("Should fail")
    async def fail(name, age=41):
        err, resp = await fail_again()
        if err:
            raise e(f"As expected, it failed for {name} (age:{age})", err)
        return "yes"

    @async_catch_errors("Should fail again")
    async def fail_again():
        await asyncio.sleep(0.01)
        raise Exception("Failed again")
        return "yes"

    loop = asyncio.get_event_loop()
    err, resp = loop.run_until_complete(fail("Peter", age=32))
    assert err
    assert err.stack
    stack_details = err.stringify()
    assert stack_details
    error_msgs = re.findall(r"error:\s(.*?)\n", stack_details)
    assert error_msgs
    assert len(error_msgs) == 4
    assert error_msgs[0] == "Should fail"
    assert error_msgs[1] == "As expected, it failed for Peter (age:32)"
    assert error_msgs[2] == "Should fail again"
    assert error_msgs[3] == "Failed again"
