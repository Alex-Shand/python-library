"""Coroutine utility functions."""

from functools import wraps
from typing import (cast, Callable, Generator, Iterable, Iterator, List,
                    Optional, Tuple, TypeVar)

from export import export
from type_aliases import Function

T = TypeVar('T') # pylint: disable=invalid-name
S = TypeVar('S') # pylint: disable=invalid-name

# From: http://www.dabeaz.com/coroutines/index.html
@export
def coroutine(func: Function) -> Function:
    """Prime the given function as a coroutine."""
    @wraps(func)
    def _coroutine(*args, **kwargs): # type: ignore # pylint: disable=missing-docstring
        cr = func(*args, **kwargs) # pylint: disable=invalid-name
        cr.send(None)
        return cr
    return cast(Function, _coroutine)

## Start ##

@export
def start(iterable: Iterator[T], then: Generator[None, T, None]) -> None:
    """Send an iterable to a coroutine.

    Required Arguments:
    iterable -- Iterable to convert.
    then -- Coroutine to send each item to.
    """

    for item in iterable:
        then.send(item)

@export
def from_file( # pylint: disable=invalid-name
        fname: str,
        then: Generator[None, str, None],
        by: Optional[Callable[[str], Iterable[str]]] = None
) -> None:
    """Send file data to a coroutine.

    Required Arguments:
    fname -- Name of the file to read.
    then -- Coroutine to send each chunk to.

    Optional Arguments:
    by -- If provided it will be passed the text of the file and should return
          an iterable, defaults to splitlines().
    """

    if by is None:
        by = lambda x: x.splitlines()
    with open(fname) as file:
        stream = by(file.read())
    for obj in stream:
        then.send(obj)

## End ##

@export
@coroutine
def collect(
        res: List[T],
        side: Optional[Callable[[T], None]] = None
) -> Generator[None, T, None]:
    """Convert a coroutine into a list.

    Required Arguments:
    res -- After the pipeline finishes res will contain the list constructed.

    Optional Arguments:
    side -- If present side will be passed each item recived from the pipeline,
    its return value is ignored.
    """

    res = []
    if side is None:
        side = lambda x: None
    while True:
        item = (yield)
        side(item)
        res.append(item)

@export
@coroutine
def printer(
        wrap: Optional[Callable[[str], str]] = None
) -> Generator[None, str, None]:
    """Print the 'return values' of a coroutine.

    Optional Arguments:
    wrap -- If present the result of calling this function with each item is
            printed.
    """

    if wrap is None:
        wrap = lambda x: x
    while True:
        print(wrap((yield)))

@export
@coroutine
def to_files(mode: str = 'w') -> Generator[None, Tuple[str, str], None]:
    """Write each item sent from a coroutine to a file.

    Expects the sending coroutine to send a tuple (filename, data).
    """

    while True:
        fname, data = (yield)
        with open(fname, mode) as file:
            file.write(str(data))

@export
@coroutine
def to_file(fname: str, truncate: bool = False) -> Generator[None, str, None]:
    """Append each item from a coroutine to a file.

    Required Arguments:
    fname -- File name to write to.

    Optional Arguments:
    truncate -- If True the file will be truncated before the first write,
                defaults to False.
    """

    if truncate:
        with open(fname, 'w'):
            pass
    while True:
        text = str((yield))
        with open(fname, 'a') as file:
            file.write(text)

@export
@coroutine
def sink() -> Generator[None, T, None]:
    """Do nothing with a coroutine."""
    while True:
        (yield)

## Middle ##

@export
@coroutine
def cfilter(
        cond: Callable[[T], bool],
        then: Generator[None, T, None]
) -> Generator[None, T, None]:
    """Coroutine equivalent of builtin filter."""
    while True:
        item = (yield)
        if cond(item):
            then.send(item)

@export
@coroutine
def cmap(
        trans: Callable[[T], S],
        then: Generator[None, S, None]
) -> Generator[None, T, None]:
    """Coroutine equivalent of builtin map."""
    while True:
        item = (yield)
        then.send(trans(item))

@export
@coroutine
def split_on(
        delim: str,
        then: Generator[None, str, None]
) -> Generator[None, str, None]:
    """Split an incoming string on a delimiter."""
    while True:
        to_split = (yield)
        items = to_split.split(delim)
        for item in items:
            then.send(item)

@export
@coroutine
def cenumerate(
        then: Generator[None, Tuple[int, T], None]
) -> Generator[None, T, None]:
    """Coroutine equivalent of builtin enumerate."""
    i = 0
    while True:
        item = (yield)
        then.send((i, item))
        i += 1
