from typing import TypeVar, Any, Union, Callable

from pathlib import Path

Function = TypeVar('Function', bound=Callable[..., Any])
Pathlike = Union[str, Path]
