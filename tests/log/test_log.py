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
import json
import re
import os

sys.path.append(".")  # noqa # Adds higher directory to python modules path.

from src.puffy.log import log
from src.puffy.error import catch_errors, StackedException as e


def test_basic_log():
    logs = []

    def print_mock(msg):
        logs.append(msg)

    input_01 = {}
    input_02 = {
        "level": "INFO",
        "message": "Hello world",
        "code": "03030303",
        "data": {"hello": "world"},
    }
    input_03 = {
        "level": "WARN",
        "message": "Hello world",
        "code": "03030303",
        "data": {"hello": "world"},
    }
    input_04 = {
        "level": "WARN",
        "message": "Hello world",
        "code": "03030303",
        "time": 34,
        "data": "hello",
    }
    input_04_out = {
        "level": "WARN",
        "message": "Hello world",
        "code": "03030303",
        "metric": 34,
        "unit": "ms",
        "data": "hello",
    }
    input_05 = {
        "level": "WARN",
        "message": "Hello world",
        "code": "03030303",
        "metric": 34,
        "unit": "seconds",
        "data": {"hello": "world"},
    }
    input_06 = {
        "level": "WARN",
        "message": "Hello world",
        "code": "03030303",
        "metric": 34,
        "unit": "seconds",
        "op_id": "1234",
        "data": {"hello": "world"},
    }
    input_07 = {
        "level": "WARN",
        "message": "Hello world",
        "code": "03030303",
        "metric": 34,
        "unit": "seconds",
        "op_id": "1234",
        "data": {"hello": "world"},
        "hello": "world",
    }
    input_07_out = {
        "level": "WARN",
        "hello": "world",
        "message": "Hello world",
        "code": "03030303",
        "metric": 34,
        "unit": "seconds",
        "op_id": "1234",
        "data": {"hello": "world"},
    }

    log(print_mock=print_mock)
    log(**input_01, print_mock=print_mock)
    log(**input_02, print_mock=print_mock)
    log(**input_03, print_mock=print_mock)
    log(**input_04, print_mock=print_mock)
    log(**input_05, print_mock=print_mock)
    log(**input_06, print_mock=print_mock)
    log(**input_07, print_mock=print_mock)

    # print()
    # print(logs[0])
    # print(json.dumps(input_01))

    assert len(logs) == 8
    assert logs[0] == json.dumps({"level": "INFO"})
    assert logs[1] == json.dumps({"level": "INFO"})
    assert logs[2] == json.dumps(input_02)
    assert logs[3] == json.dumps(input_03)
    assert logs[4] == json.dumps(input_04_out)
    assert logs[5] == json.dumps(input_05)
    assert logs[6] == json.dumps(input_06)
    assert logs[7] == json.dumps(input_07_out)


def test_env_var_log():
    os.environ["LOG_META"] = json.dumps({"api_name": "hello"})

    logs = []

    def print_mock(msg):
        logs.append(msg)

    input_01 = {
        "level": "INFO",
        "message": "Hello world",
        "code": "03030303",
        "data": {"hello": "world"},
    }
    input_01_out = {
        "api_name": "hello",
        "level": "INFO",
        "message": "Hello world",
        "code": "03030303",
        "data": {"hello": "world"},
    }

    log(**input_01, print_mock=print_mock)
    assert len(logs) == 1
    assert logs[0] == json.dumps(input_01_out)

    os.environ["LOG_META"] = ""


def test_incl_errors_log():
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

    err, *_ = fail()

    logs = []

    def print_mock(msg):
        logs.append(msg)

    input_01 = {
        "level": "INFO",
        "message": "Hello world",
        "code": "03030303",
        "data": {"hello": "world"},
        "errors": err,
    }
    input_02 = {
        "level": "INFO",
        "message": "Hello world",
        "code": "03030303",
        "data": {"hello": "world"},
        "errors": "Shit... something broke!!!",
    }
    input_03 = {
        "level": "INFO",
        "message": "Hello world",
        "code": "03030303",
        "data": {"hello": "world"},
        "errors": Exception("Booommmm"),
    }
    input_04 = {
        "level": "INFO",
        "message": "Hello world",
        "code": "03030303",
        "data": {"hello": "world"},
        "errors": [Exception("Booommmm"), "Bim bam boooooommm"],
    }
    input_05 = {
        "level": "INFO",
        "message": "Hello world",
        "code": "03030303",
        "data": {"hello": "world"},
        "errors": [Exception("Booommmm"), "Bim bam boooooommm", err],
    }

    inputs = [input_01, input_02, input_03, input_04, input_05]
    error_messages = [
        ["error: Should fail", "error: Should fail again", "error: Failed again"],
        ["Shit... something broke!!!"],
        ["Booommmm"],
        ["Booommmm", "Bim bam boooooommm"],
        [
            "Booommmm",
            "Bim bam boooooommm",
            "error: Should fail",
            "error: Should fail again",
            "error: Failed again",
        ],
    ]

    log(**input_01, print_mock=print_mock)
    log(**input_02, print_mock=print_mock)
    log(**input_03, print_mock=print_mock)
    log(**input_04, print_mock=print_mock)
    log(**input_05, print_mock=print_mock)

    # print()
    # print(logs[0])
    # print(json.dumps(input_01))

    assert len(logs) == 5

    for i, l in enumerate(logs):
        l_item = json.loads(l)
        original = inputs[i]
        err_msgs = error_messages[i]
        assert original["level"] == l_item["level"]
        assert original["message"] == l_item["message"]
        assert original["code"] == l_item["code"]
        assert original["data"]["hello"] == l_item["data"]["hello"]
        assert original["level"] == l_item["level"]
        assert l_item["errors"]
        assert isinstance(l_item["errors"], str)
        assert len(err_msgs) > 0
        for msg in err_msgs:
            assert re.search(msg, l_item["errors"])
