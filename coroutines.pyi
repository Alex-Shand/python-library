from type_aliases import Function
from typing import (Callable, Generator, Iterable, Iterator, List, Optional,
                    Tuple, TypeVar)

T = TypeVar('T')
S = TypeVar('S')

def coroutine(func: Function) -> Function: ...

def start(iterable: Iterator[T], then: Generator[None, T, None]) -> None: ...

def from_file(
        fname: str,
        then: Generator[None, str, None],
        by: Optional[Callable[[str], Iterable[str]]]=...
) -> None: ...

def collect(
        res: List[T],
        side: Optional[Callable[[T], None]]=...
) -> Generator[None, T, None]: ...

def printer(
        wrap: Optional[Callable[[str], str]]=...
) -> Generator[None, str, None]: ...

def to_files(mode: str=...) -> Generator[None, Tuple[str, str], None]: ...

def to_file(fname: str, truncate: bool=...) -> Generator[None, str, None]: ...

def sink() -> Generator[None, T, None]: ...

def cfilter(
        cond: Callable[[T], bool],
        then: Generator[None, T, None]
) -> Generator[None, T, None]: ...

def cmap(
        trans: Callable[[T], S],
        then: Generator[None, S, None]
) -> Generator[None, T, None]: ...

def split_on(
        delim: str,
        then: Generator[None, str, None]
) -> Generator[None, str, None]: ...

def cenumerate(
        then: Generator[None, Tuple[int, T], None]
) -> Generator[None, T, None]: ...
