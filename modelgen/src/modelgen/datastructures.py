""" python function snippet which flattens nested iterables """
# pylint: disable=too-few-public-methods
from typing import Final, Iterable, Iterator, Optional, TypeVar, Union


def flat(*args) -> Iterator:
    """convenience wrapper around flatten"""
    return flatten(args)


def flatten(nested: Iterable) -> Iterator:
    """
    Return the given arbitrarily nested iterables as a flat iterator; for
    example it can flatten a list of lists into a single list

    Parameters:
        nested: An iterable containing nested iterables to flatten

    Yields:
        All non-iterable items and flattened elements

    Warning:
        Inputs containing infinite sequences like generators may cause infinite
        recursion.

    Examples:
        >>> list(flatten([1, [2, [3, "bob"], 5], "alice"]))
        [1, 2, 3, 'bob', 5, 'alice']

    """
    # str and bytes are a special case, without this check we would hit the
    # recursion limit on any string
    if isinstance(nested, (str, bytes)):
        yield nested
        return

    try:
        for item in nested:
            yield from flatten(item)
    except TypeError:
        yield nested


class CoalesceNoDefault:
    """class representing an unspecified default value for the coalesce function"""


__COALESCE_NO_DEFAULT: Final = CoalesceNoDefault()

T = TypeVar("T")
U = TypeVar("U")


def coalesce(
    *args: Optional[T],
    default: Union[U, CoalesceNoDefault] = __COALESCE_NO_DEFAULT,
) -> Union[T, U]:
    """
    return the first item in the argument list that isn't None

    If all items are None and `default` is provided, return the default value.
    If no default is provided and all items are None, raise a ValueError.
    """
    for arg in args:
        if arg is not None:
            return arg
    if not isinstance(default, CoalesceNoDefault):
        return default
    raise ValueError(
        "coalesce() expects at least one non-None argument or a default value"
    )
