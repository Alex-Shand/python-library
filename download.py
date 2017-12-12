"""Functions wrapping urllib.request for common download tasks."""

import re
import os
import time
import urllib.request as r
from urllib.error import URLError
from bs4 import BeautifulSoup

# TODO: Add optional header
def get_data(url):
    """Returns binary data downloaded from the url."""
    req = r.Request(url)
    data = r.urlopen(req).read()
    return data

def get_html(url):
    """Returns html downloaded from the url."""
    data = get_data(url)
    html = data.decode('utf-8')
    return html

def get_download_url(html, regex):
    """Extracts the download url from the given html using a regex, returns None if it fails."""
    match = regex.search(html)
    if match:
        return match.group(1)

def resolve_filename_clash(fname):
    """Ensures the proposed filename doesn't clash with any files already on disk"""

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

def filter_urls(urls, downloadlog):
    """Removes urls known to have been downloaded previously"""
    try:
        with open(downloadlog) as log:
            downloaded = set(log.read().split())

        urls = set(urls) - downloaded
    except FileNotFoundError:
        pass

    return urls

def download(url, fname):
    """Downloads data from the url, returns the filename written to.

    Arguments:
    url -- The url to download
    fname -- The filename to attempt to write to, will be changed
             if it clashes
    """
    data = get_data(url)
    fname = resolve_filename_clash(fname)
    with open(fname, 'wb') as file:
        file.write(data)
    return fname

# TODO: There's probably some kind of logging library that does this better
def logurl(log, url, kind=''):
    """Writes the url to the specified log file optionally prepending a type"""
    if kind:
        kind += ': '
    with open(log, 'a') as logfile:
        logfile.write('{0}{1}\n'.format(kind, url))

def extract_links_from_page(url):
    try:
        page = get_html(url)
    except URLError:
        return

# TODO: Regex is a really bad idea here
# TODO: Get rid of some of the arguments
def download_from_page(url, regex, targetdir=None, fnamefunc=None,
                       fnametarget=False, faillog='0FAILS', succlog='0DOWNLOADED'):
    """Downloads media specified by the regex from the given url"""

    def getfname(url, ext):
        """Default file name extraction function"""
        return url.split('/')[-1].split('.')[0] + ext

    # If a replacement for getfname has been supplied use it
    if fnamefunc:
        getfname = fnamefunc

    # If a target directory has been supplied
    if targetdir is not None:
        targetdir = os.path.abspath(targetdir)
        # Put the fail and success logs in the target directiory
        faillog = os.path.join(targetdir, faillog)
        succlog = os.path.join(targetdir, succlog)
        # And recursivly make it if it doesn't exist
        if not os.path.isdir(targetdir):
            os.makedirs(targetdir)

    print('Retrieving html...', end='', flush=True)
    try:
        html = get_html(url)
        print('done\nExtracting direct url...', end='', flush=True)
    except URLError:
        print('failed\n', flush=True)
        logurl(faillog, url, 'HTML') # Log an error at the html stage
        return

    # getdownloadurl returns None on failure
    download_url = get_download_url(html, regex)
    if not download_url:
        print('failed\n', flush=True)
        logurl(faillog, url, 'REGEX') # Log an error in the regex
        return
    print('done\nDownloading...', end='', flush=True)

    # Empty string if the url doesn't contain a '.'
    ext = os.path.splitext(download_url)[1]
    if fnametarget:
        fname = getfname(download_url, ext)
    else:
        fname = getfname(url, ext)

    # If a target directory has been supplied join it to the filename
    if targetdir:
        fname = os.path.join(targetdir, fname)

    # Same as gethtml
    try:
        download(download_url, fname)
        print('done\n', flush=True)
    except URLError:
        print('failed\n', flush=True)
        # Log a download error including both urls
        logurl(faillog, '{0}|{1}'.format(url, download_url), 'DOWNLOAD')
        return
    # Log a successful download
    logurl(succlog, url)

def download_list(urls, regex, targetdir=None, fnamefunc=None, fnametarget=False,
                  faillog='0FAILS', succlog='0DOWNLOADED'):
    """Download a list of urls."""

    # Remove urls known to be downloaded
    filter_urls(urls, succlog)

    length = len(urls)
    for i, url in enumerate(urls):
        time.sleep(30) # Short pause seems to decrease failure rate
        print('{0}/{1}'.format(i+1, length), flush=True)
        download_from_page(url, regex, targetdir, fnamefunc, fnametarget, faillog,
                           succlog)

# If download is run as a program it runs a basic command line downloader
if __name__ == '__main__':

    # Builtin exit shouldn't be used in programs
    from sys import argv, exit # pylint: disable=redefined-builtin

    USAGE = '''
Usage: download.py file regex
file: File containing urls to download, one per line
regex: Python regular expression to identify the direct link to the desired file in the page source
'''

    if len(argv) < 3:
        exit(USAGE)

    FILE = argv[1]
    REGEX = re.compile(argv[2])

    with open(FILE) as f:
        URLS = f.read().split()

    download_list(URLS, REGEX)
