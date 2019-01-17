"""Functions wrapping urllib.request for common download tasks."""

import re
import os
import time
import urllib.request as request
from urllib.error import URLError
from http.client import IncompleteRead
from argparse import ArgumentParser

from bs4 import BeautifulSoup

class DownloadError(Exception):
    """Wrapper for the various things urlopen might throw."""
    def __init__(self, inner):
        self.inner = inner
    def __repr__(self):
        return repr(inner)
    
def get_data(url, header=None):
    """Return binary data downloaded from a url.

    Throws:
    DownloadError -- If download fails for any reason.
    """

    if header is None:
        header = {}
    req = request.Request(url, headers=header)
    try:
        data = request.urlopen(req).read()
    except (URLError, IncompleteRead) as e:
        raise DownloadError(e)
    return data

def get_html(url, header=None):
    """Return html downloaded from a url.

    Throws:
    DownloadError -- If download fails for any reason.
    """

    data = get_data(url, header)
    html = data.decode('utf-8')
    return html

def resolve_filename_clash(fname):
    """Ensure the proposed filename doesn't clash with any files already on
    disk."""

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

    return fname

def download(url, fname, header=None, force=False):
    """Downloads data from the url, returns the filename written to.

    Required Arguments:
    url -- The url to download.
    fname -- The filename to attempt to write to, will be changed
             if it clashes.

    Optional Arguments:
    force -- If True don't resolve clashes.

    Throws:
    DownloadError -- If download fails for any reason.
    """

    data = get_data(url, header=header)
    resp = urlopen(url)
    # Resolve filename clashes unless told otherwise
    if not force:
        fname = resolve_filename_clash(fname)
    with open(fname, 'wb') as file:
        for chunk in iter(lambda: resp.read(16 * 1024), ''):
            if not chunk:
                break
            file.write(data)
    return fname

def extract_hrefs_from_page(url, header=None, tag=None):
    """Return a generator containing all hrefs from a page, optionally
    restricted to a tag.

    Required Arguments:
    url -- The url of the web page to search.

    Optional Arguments:
    tag -- Restrict the search to this tag.
    """

    try:
        page = get_html(url, header=header)
    except DownloadError:
        # Returns an empty generator
        return
        # This is unreachable but still required to get an empty generator out
        yield # pylint: disable=unreachable
    soup = BeautifulSoup(page, 'lxml')
    if tag is None:
        hrefs = soup(href=True)
    else:
        hrefs = soup(tag, href=True)

    yield from map(lambda x: x['href'], hrefs)

def download_from_page(url, filterfun=None, targetdir='.', fnamefunc=None, header=None):
    """Download all links from a page.

    Required Arguments:
    url -- Source page

    Optional Arguments:
    filterfun -- Only download links where filterfun(link) == True
    targetdir -- Files go here
    fnamefunc -- Recieves url and the link currently being downloaded. Return
                 value will be used as the filename for the download.
    """

    # Set default functions as required
    if fnamefunc is None:
        fnamefunc = lambda _, url: url.split('/')[-1]
    if filterfun is None:
        filterfun = lambda _: True

    # Produce an absolute path
    targetdir = os.path.abspath(targetdir)
    # And recursivly make it if it doesn't exist
    if not os.path.isdir(targetdir):
        os.makedirs(targetdir)

    urls = filter(filterfun, extract_hrefs_from_page(url))

    for download_url in urls:
        fname = fnamefunc(url, download_url)
        fname = os.path.join(targetdir, fname)
        try:
            download(download_url, fname, header=header)
        except URLError:
            return

def download_list(urls, filterfun=None, targetdir='.', fnamefunc=None, header=None):
    """Download links matching a given condition from a list of urls.

    Required Arguments:
    urls -- Source pages

    Optional Arguments:
    filterfun -- Only download links where filterfun(link) == True
    targetdir -- Files go here
    fnamefunc -- Recieves url and the link currently being downloaded. Return
                 value will be used as the filename for the download.
    """

    for url in urls:
        time.sleep(30) # Short pause seems to decrease failure rate
        download_from_page(url, filterfun, targetdir, fnamefunc, header=header)

def main(file, regex):
    """Main."""

    regex = re.compile(regex)

    with open(file) as url_file:
        urls = url_file.read().split()

    download_list(urls, regex)

# If download is run as a program it runs a basic command line downloader
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('file',
                        help='File containing source urls to download from, one'
                        'per line')
    parser.add_argument('-r', '--regex', default='.*',
                        help='Python regular expression to identify the correct'
                        ' link(s) in the page, defaults to ".*"')
    main(**(vars(parser.parse_args())))
