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

from src.puffy.object import JSON, dotProps


def test_query_keys():
    obj = JSON()

    assert not obj["hello"]["world"]
    obj["hello"]["world"] = "cool"
    assert obj["hello"]
    assert obj["hello"]["world"]
    assert obj["hello"]["world"] == "cool"


def test_query_JSON_dot_keys():
    obj = JSON(
        {"hello": {"default": "world", "address": ["no", 1, "street"]}, "name": "Nic"}
    )

    assert obj.s("person.name", "Peter") == "Peter"
    assert obj.g("hello.default") == "world"
    assert obj.g("person.name") == "Peter"
    assert not obj.g("hello.something.else")
    assert obj.g("name") == "Nic"
    assert obj.g("hello.address")
    assert isinstance(obj.g("hello.address"), list)
    assert len(obj.g("hello.address")) == 3
    assert obj.g("hello.address")[0] == "no"
    assert obj.g("hello.address.line1") is None
    assert isinstance(obj.g("hello.address"), dict)


def test_query_dot_keys():
    obj = {"hello": {"default": "world"}, "name": "Nic"}

    assert dotProps(obj, "hello.default") == "world"
    assert not dotProps(obj, "hello.something.else")
    assert dotProps(obj, "name") == "Nic"
