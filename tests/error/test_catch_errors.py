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

sys.path.append(".")  # noqa # Adds higher directory to python modules path.

from src.puffy.error import catch_errors, StackedException as e


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
