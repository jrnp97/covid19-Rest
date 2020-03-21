# -*- coding: utf-8 -*-
""" Module to create tasks of project """
import os
import logging
import tempfile
import datetime

import pandas as pd

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile


from api.utils import github_api_request
from api.utils import csv_header2model_field_mapper

from api.models import DataFile
from api.models import GeneralData


LOGGER = logging.getLogger(__file__)


def file_data_importer(data_file_id):
    """
    Tasks to update covid information from file on DataFile instance to GeneralData Model.
    Args:
        data_file_id: A int describing DataFile instance id.

    Returns:
        A bool return if data was imported correct.
    """
    data_file = DataFile.objects.get(id=data_file_id)
    processed = False
    with open(data_file.origin_file.path, 'r') as file_:
        csv_header = file_.readline().replace('\ufeff', '').split(',')
    field_mapping = csv_header2model_field_mapper(csv_header=csv_header)
    process_detail = '[DETAILS]'
    if None in field_mapping.keys():
        process_detail += '\nSome column was not map with field, mapping: {map_}.'.format(map_=field_mapping)
        data_file.processed = processed
        data_file.process_detail = process_detail
        data_file.save(update_fields=['processed', 'process_detail'])
        return False

    df = pd.read_csv(data_file.origin_file.path)
    df.rename(columns=field_mapping, inplace=True)
    date_column_formats = [
        '%m/%d/%y %H:%M',
    ]
    for format_ in date_column_formats:
        try:
            df.last_update = pd.to_datetime(df.last_update, format=format_)
            break
        except ValueError:
            logging.info(msg='Last Update column no support: {form} format.'.format(form=format_))
    else:
        process_detail = 'Last update: {value} not support registre formats: {registred}'.format(
            value=df.last_update[0],
            registred=','.join(date_column_formats)
        )
        data_file.processed = processed
        data_file.process_detail = process_detail
        data_file.save(update_fields=['processed', 'process_detail'])
        return False
    df.to_csv(data_file.origin_file.path, index=False, sep=';')

    report_day_formats = [
        '%m-%d-%Y',
    ]
    filename = os.path.basename(data_file.origin_file.path).split('.')[0].split('_')[0]
    report_day = None
    for date_format in report_day_formats:
        try:
            report_day = datetime.datetime.strptime(filename, date_format)
            break
        except ValueError:
            logging.debug(msg='File name: {name} no with format: {ft}'.format(
                name=filename,
                ft=date_format,
            ))
    if not report_day:
        process_detail += '\nFilename date was not parsed.'
    try:
        total_inserted = GeneralData.objects.from_csv(
            csv_path=data_file.origin_file.path,
            delimiter=';',
            static_mapping={
                'report_day': report_day,
                'data_file_id': data_file_id,
            }
        )
    except IntegrityError as err:
        processed = False
        process_detail += '\nError doing bulk_insert, details\n: {details}.'.format(
            details=err
        )
    else:
        processed = True
        process_detail += '\nTotal inserted: {total}.'.format(total=total_inserted)

    data_file.processed = processed
    data_file.process_detail = process_detail
    data_file.save(update_fields=['processed', 'process_detail'])
    return processed


def file_data_downloader(file_server_data):
    """
    Task to download covid.csv file from server and upload on database.
    Args:
        file_server_data: A dict describing server file data (github api give the follow structure):
        {
            'name': '<string>',
             'path': '<string>',
             'sha': '<hash>',
             'size': <int>,
             'url': '<url>',
             'html_url': '<url>',
             'git_url': '<url>',
             'download_url': '<url>',
             'type': '<string>',
             '_links': {
                 'self': '<url>',
                 'git': '<url>',
                 'html': '<url>',
             }
         }

    Returns:
        A bool indicating if file was imported or not.
    """
    temp_path = os.path.join(tempfile.gettempdir(), file_server_data['name'])
    try:
        DataFile.objects.get(signature=file_server_data['sha'])
    except ObjectDoesNotExist:
        LOGGER.info(msg='Go to save file => {github_path}'.format(github_path=file_server_data['path']))
    else:
        LOGGER.info(msg='Already file found not processed')
        return False

    api_response = github_api_request(request_kwargs={
        'method': 'GET',
        'url': file_server_data['download_url'],
    })
    with open(temp_path, 'wb') as file_:
        file_.write(api_response.content)
    data_file = DataFile(
        signature=file_server_data['sha'],
    )
    data_file.origin_file.save(file_server_data['name'], ContentFile(open(temp_path, 'rb').read()), save=True)
    file_data_importer(data_file_id=data_file.id)
    return False


def covid_data_getter():
    """
    Tasks to Getting Covid daily information from https://github.com/CSSEGISandData/COVID-19 thanks.
    Returns:
        A int describing number of files detected.
    """
    github_base = 'https://api.github.com/repos/CSSEGISandData/COVID-19/contents/'
    data_source_repo_path = [
        '/archived_data/archived_daily_case_updates/',
        '/csse_covid_19_data/csse_covid_19_daily_reports/',
    ]
    files = []
    for repo_path in data_source_repo_path:
        repo_url = github_base + repo_path
        api_response = github_api_request(request_kwargs={
            'method': 'GET',
            'url': repo_url,
        })
        files.extend(api_response.json())
    good_files = 0
    for file_ in files:
        extension = file_['name'].split('.')[-1]
        if extension == 'csv' and file_['type'] == 'file':
            file_data_downloader(file_server_data=file_)
            good_files += 1
    return good_files
