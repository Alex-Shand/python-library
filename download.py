"""Functions wrapping urllib.request for common download tasks."""

import re
import os
import time
import urllib.request as r
from urllib.error import URLError
from bs4 import BeautifulSoup

def get_data(url, header=None):
    """Return binary data downloaded from a url."""
    if header is None:
        header = {}
    req = r.Request(url, headers=header)
    data = r.urlopen(req).read()
    return data

def get_html(url):
    """Return html downloaded from a url."""
    data = get_data(url)
    html = data.decode('utf-8')
    return html

def resolve_filename_clash(fname):
    """Ensure the proposed filename doesn't clash with any files already on disk"""

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

def download(url, fname, force=False):
    """Downloads data from the url, returns the filename written to.

    Arguments:
    url -- The url to download
    fname -- The filename to attempt to write to, will be changed
             if it clashes
    force -- If True don't resolve clashes
    """
    data = get_data(url)
    # Resolve filename clashes unless told otherwise
    if not force:
        fname = resolve_filename_clash(fname)
    with open(fname, 'wb') as file:
        file.write(data)
    return fname

def extract_hrefs_from_page(url, tag=None):
    """Extract the hrefs from a page, optionally restricted to a tag."""
    try:
        page = get_html(url)
    except URLError:
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

def download_from_page(url, filter_fun=lambda x: True, targetdir='.', fnamefunc=None):
    """Download links matching a given condition from a url."""

    # Function to extract filename, gets the url of the page the links are
    # extracted from and the url that the file is acutally downloaded from
    def getfname(_, download_url):
        """Take the last part of the download url as the filename"""
        return download_url.split('/')[-1]

    # If a replacement for getfname has been supplied use it
    if fnamefunc is not None:
        getfname = fnamefunc

    # Produce an absolute path
    targetdir = os.path.abspath(targetdir)
    # And recursivly make it if it doesn't exist
    if not os.path.isdir(targetdir):
        os.makedirs(targetdir)

    urls = filter(filter_fun, extract_hrefs_from_page(url))

    for download_url in urls:
        fname = getfname(url, download_url)
        fname = os.path.join(targetdir, fname)
        try:
            download(download_url, fname)
        except URLError:
            return

def download_list(urls, filter_fun=lambda x: True, targetdir='.', fnamefunc=None):
    """Download links matching a given condition from a list of urls."""
    for url in urls:
        time.sleep(30) # Short pause seems to decrease failure rate
        download_from_page(url, filter_fun, targetdir, fnamefunc)

def _main(args):
    """Downloader program using the functions from this module, takes commandline arguments"""

    usage = '''
Usage: download.py file regex
file: File containing urls to download, one per line
regex: Python regular expression to identify the direct link to the desired file in the page source
'''

    if len(args) < 3:
        exit(usage)

    file = args[1]
    regex = re.compile(args[2])

    with open(file) as url_file:
        urls = url_file.read().split()

    download_list(urls, regex)

# If download is run as a program it runs a basic command line downloader
if __name__ == '__main__':
    # Builtin exit shouldn't be used in programs
    from sys import argv, exit # pylint: disable=redefined-builtin
    _main(argv)
