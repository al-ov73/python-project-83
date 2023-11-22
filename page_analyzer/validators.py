import validators
from urllib.parse import urlparse


def validate(url):
    return validators.url(url)


def normilyze(url):
    scheme = urlparse(url).scheme
    hostname = urlparse(url).hostname
    return (scheme + '://' + hostname)
