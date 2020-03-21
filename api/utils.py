""" Module to define utils """
import os
import time
import hashlib

import requests


def generate_md5_checksum(file_path, chunk_size=4096):
    """
    Util function to generate md5 checksum of files.
    Args:
        file_path: A str describing file path on system.
        chunk_size: A integer describing chunk file bytes when reading.

    Returns:
        A hex value describing file checksum.
    """

    if not os.path.exists(file_path):
        raise ValueError('<file_path> does not exist')
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as file_:
        for chunk in iter(lambda: file_.read(chunk_size), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigist()


def request_with_retry(request_kwargs, max_retries=3):
    """
    Util to do request to server but manage retry system if it is down.
    Args:
        request_kwargs: A dict describing kwargs to pass on requests.request method.
        max_retries: A integer describing max number de retries to do.

    Returns:
        A requests.Response object.
    """
    retried = 0
    while retried < max_retries:
        try:
            response = requests.request(**request_kwargs)
            return response
        except requests.exceptions.Timeout as err:
            time.sleep(30)
            retried += 1
            if retried == max_retries:
                raise err
            continue


def github_api_request(request_kwargs):
    """
    Util to perform github api v3 request.
    Args:
        request_kwargs: A dict describing kwargs to pass on requests.request method.

    Returns:
        A requests.Response object.
    """
    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }
    request_kwargs.update({
        'headers': headers,
        'timeout': 60,
    })
    return request_with_retry(request_kwargs)

