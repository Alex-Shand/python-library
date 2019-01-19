"""Download things from the internet."""

import os
from pathlib import Path

import requests

from export import export

@export
def get_data(url, headers=None):
    """Return binary data downloaded from a url.

    Optional Arguments:
    headers -- Dictionary containing request headers.

    Throws:
    requests.exceptions.HTTPError -- If the request fails.
    """

    if headers is None:
        headers = {}

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    yield from resp.iter_content(chunk_size=128)

@export
def get_html(url, headers=None):
    """Return html downloaded from a url.

    Optional Arguments:
    headers -- Dictionary containing request headers.

    Throws:
    requests.exceptions.HTTPError -- If the request fails.
    """

    data = sum(list(get_data(url, headers)), b'')
    html = data.decode('utf-8')
    return html

@export
def resolve_filename_clash(fname):
    """Ensure the proposed filename doesn't clash with any files already on
    disk."""

    fname = str(fname)

    # Start by inserting a one before the extension
    if os.path.isfile(fname):
        name, ext = os.path.splitext(fname)
        fname = '{0}1{1}'.format(name, ext)

    # Increment until the file doesn't clash
    i = 2
    while os.path.isfile(fname):
        name, ext = os.path.splitext(fname)
        # Strips the old number off and appends the new one
        fname = name[:-len(str(i-1))] + str(i) + ext
        i += 1

    return Path(fname)

@export
def download(url, fname, headers=None, force=False):
    """Downloads data from the url, returns the filename written to.

    Required Arguments:
    url -- The url to download.
    fname -- The filename to attempt to write to, will be changed
             if it clashes.

    Optional Arguments:
    headers -- Dictionary containing request headers.
    force -- If True don't resolve clashes.

    Throws:
    requests.exceptions.HTTPError -- If the request fails.
    """

    # Resolve filename clashes unless told otherwise
    if not force:
        fname = resolve_filename_clash(fname)

    with open(str(fname), 'wb') as file:
        for chunk in get_data(url, headers):
            file.write(chunk)

    return Path(fname)
