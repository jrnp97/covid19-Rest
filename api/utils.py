""" Module to define utils """
import os
import time
import logging
import hashlib

import requests
import pandas as pd
from django.utils.text import slugify

from api.exceptions import HeaderNotIdentifier, DateFormatNotIdentifier


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


def csv_header2model_field_mapper(csv_header):
    """
    Util to help to identify csv header to model fields of api.GeneralData.
    Args:
        csv_header: A list with str values of column names of csv file.

    Returns:
        A dict describing GeneralData field = csv header field.
    """
    # TODO Change it for a model to dynamic behavior
    mapping_ = {
        'province_state': [
            slugify('Province/State'),
            slugify('Province_State'),
        ],
        'country_region': [
            slugify('Country/Region'),
            slugify('Country_Region'),
        ],
        'last_update': [
            slugify('Last Update'),
            slugify('Last_Update'),
        ],
        'confirmed': [
            slugify('Confirmed'),
        ],
        'deaths': [
            slugify('Deaths'),
        ],
        'recovered': [
            slugify('Recovered'),
        ],
        'suspected': [
            slugify('Suspected'),
        ],
        'latitude': [
            slugify('Latitude'),
            slugify('Lat'),
        ],
        'longitude': [
            slugify('Longitude'),
            slugify('Long_'),
        ],
        'confn_susp': [
            slugify('ConfnSusp'),
        ]
    }

    def get_field_name(slug_header):
        """ Inner function to get field name of slug column name """
        for field, column_values in mapping_.items():
            if slug_header in column_values:
                return field
    header_mapping = {
        column_name.strip(): get_field_name(slug_header=slugify(column_name.strip())) for column_name in csv_header
    }
    return header_mapping


def clean_jh_csv_file(data_file_id):
    """
    Util receiving a csv DataFile from jh university and clean its columns allowing import it
    on GeneralData table
    Args:
        data_file_id: A int describing DataFile DB ID.

    Returns:
        A pandas.DataFrame object manage DataFile.
    """
    from api.models import DataFile
    data_file = DataFile.objects.get(id=data_file_id)
    delimiter = ','
    if not data_file.header:
        with open(data_file.origin_file.path, 'r') as file_:
            csv_header = file_.readline().replace('\ufeff', '').split(',')
        field_mapping = csv_header2model_field_mapper(csv_header=csv_header)
    else:
        delimiter = ';'
        field_mapping = data_file.header

    field_mapping.pop('null', '')
    if None in field_mapping.keys():
        raise HeaderNotIdentifier('Incomplete headers => {head}'.format(head=field_mapping))

    columns = list(field_mapping.values())
    df = pd.read_csv(data_file.origin_file.path, delimiter=delimiter)
    df.rename(columns=field_mapping, inplace=True)
    df.drop(df.columns.difference(columns), 1, inplace=True)

    # TODO Change for model to more dynamic
    date_column_formats = [
        '%m/%d/%y %H:%M',
        '%Y-%m-%dT%H:%M:%S',
        '%m/%d/%Y %H:%M',
        '%m/%d/%Y %H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%m/%d/%Y %I%p',
    ]
    for format_ in date_column_formats:
        try:
            df.last_update = pd.to_datetime(df.last_update, format=format_)
            break
        except ValueError:
            logging.info(msg='Last Update column no support: {form} format.'.format(form=format_))
    else:
        raise DateFormatNotIdentifier('Last update: {value} not support registre formats.')

    df.to_csv(data_file.origin_file.path, index=False, sep=';')
    return df
