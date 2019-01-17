from typing import Any, Optional, Dict, Iterator, Callable, List
from type_aliases import Pathlike

Header = Dict[str, str]

class DownloadError(Exception):
    inner: Exception = ...
    def __init__(self, inner: Exception) -> None: ...

def get_data(url: str, header: Optional[Header] = ...) -> bytes: ...

def get_html(url: str, header: Optional[Header] = ...) -> str: ...

def resolve_filename_clash(fname: str) -> str: ...

def download(
        url: str,
        fname: Pathlike,
        header: Optional[Header] = ...,
        force: bool = ...) -> str: ...

def extract_hrefs_from_page(
        url: str,
        header: Optional[Header] = ...,
        tag: Optional[str] = ...) -> Iterator[str]: ...

def download_from_page(
        url: str,
        filterfun: Optional[Callable[[str], bool]] = ...,
        targetdir: Pathlike = ...,
        fnamefunc: Optional[Callable[[str], str]] = ...,
        header: Optional[Header] = ...) -> None: ...

def download_list(
        urls: List[str],
        filterfun: Optional[Callable[[str], bool]] = ...,
        targetdir: Pathlike = ...,
        fnamefunc: Optional[Callable[[str], str]] = ...,
        header: Optional[Header] = ...) -> None: ...

def main(file: Pathlike, regex: str) -> None: ...
