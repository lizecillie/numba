import functools
import __builtin__ as builtins

from numba import error
from numba.type_inference.module_type_inference import (register,
                                                        register_inferer,
                                                        register_unbound,
                                                        register_value)


def expect_n_args(node, name, nargs):
    if not isinstance(nargs, tuple):
        nargs = (nargs,)

    if len(node.args) not in nargs:
        expected = " or ".join(map(str, nargs))
        raise error.NumbaError(
            node, "builtin %s expects %s arguments" % (name,
                                                       expected))

def register_with_argchecking(nargs, can_handle_deferred_types=False):
    if not isinstance(nargs, tuple):
        nargs = (nargs,)

    def decorator(func, value=None):
        @functools.wraps(func)
        def infer(context, node, *args):
            expect_n_args(node, name, nargs)

            need_nones = max(nargs) - len(args)
            args += (None,) * need_nones

            return func(context, node, *args)

        if value is None:
            name = infer.__name__.strip("_")
            value = getattr(builtins, name)
        else:
            name = getattr(value, "__name__", "<unknown>")

        register_value(value, infer, pass_in_types=False, pass_in_callnode=True,
                       can_handle_deferred_types=can_handle_deferred_types)

        return func # wrapper

    return decorator
