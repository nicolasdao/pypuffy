# Copyright (c) 2019-2023, Cloudless Consulting Pty Ltd.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from collections.abc import Iterable
import traceback


class StackedException(Exception):
    def __init__(self, *errors):
        def __flatten(*errors):
            stack = []
            for error in errors:
                if isinstance(error, StackedException):
                    stack.extend(error.stack)
                elif isinstance(error, Exception):
                    stack.append(error)
                elif (
                    isinstance(error, str)
                    or isinstance(error, int)
                    or isinstance(error, float)
                ):
                    stack.append(Exception(error))
                elif isinstance(error, Iterable):
                    stack.extend(__flatten(error))
                else:
                    stack.append(Exception(error))
            return stack

        self.stack = __flatten(*errors)

        ln = len(self.stack)
        head = "Unknown error" if ln == 0 else self.stack[0]
        super().__init__(head)

    def stringify(self):
        if len(self.stack):
            errors = []
            for error in self.stack:
                if hasattr(error, "__traceback__") and error.__traceback__:
                    s = "".join(traceback.format_tb(error.__traceback__))
                    s = "\n" + s if s else ""
                    errors.append(f"error: {str(error)}{s}")
                else:
                    errors.append(f"error: {str(error)}")
            return "\n".join(errors)
        else:
            return ""


def catch_errors(arg):
    if not arg:
        raise Exception("Missing required argument.")

    fn = None
    wrappingError = None

    if callable(arg):
        fn = arg
    elif isinstance(arg, str):
        wrappingError = Exception(arg)
    else:
        raise Exception(
            f'Wrong argument exception. "catch_errors"\'s argument must be a function or a string. Found {type(arg).__name__} instead.'
        )

    def safe_fn_exec(ffn):
        def safe_exec(*args):
            try:
                data = ffn(*args)
                return [None, data]
            except BaseException as error:
                return [
                    StackedException(wrappingError, error)
                    if wrappingError
                    else StackedException(error),
                    None,
                ]

        return safe_exec

    return safe_fn_exec(fn) if fn else safe_fn_exec
