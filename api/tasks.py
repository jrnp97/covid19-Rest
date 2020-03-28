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

from api.exceptions import HeaderNotIdentifier
from api.exceptions import DateFormatNotIdentifier
from covid_19 import celery_app as app

from api.utils import clean_jh_csv_file
from api.utils import github_api_request

from api.models import DataFile
from api.models import GeneralData


LOGGER = logging.getLogger(__file__)


@app.task(bind=True)
def file_data_importer(self, data_file_id):
    """
    Tasks to update covid information from file on DataFile instance to GeneralData Model.
    Args:
        self: A celery.Task object.
        data_file_id: A int describing DataFile instance id.

    Returns:
        A bool return if data was imported correct.
    """
    data_file = DataFile.objects.get(id=data_file_id)
    data_file.process_id = self.request.id
    data_file.save(update_fields=['process_id'])
    processed = False
    try:
        df = clean_jh_csv_file(data_file_id=data_file_id)
    except HeaderNotIdentifier as err:
        data_file.processed = processed
        data_file.process_detail = 'Some column was not map with field, details: {error}.'.format(error=err)
        data_file.save(update_fields=['processed', 'process_detail'])
        return False
    except DateFormatNotIdentifier as err:
        data_file.processed = processed
        data_file.process_detail = 'Some Date column format was not identify, details: {error}.'.format(error=err)
        data_file.save(update_fields=['processed', 'process_detail'])
        return False

    data_file.header = {name: name for name in df.columns}
    data_file.save(update_fields=['header'])
    process_detail = '[DETAILS]'

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


@app.task
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
        data_file = DataFile.objects.get(signature=file_server_data['sha'])
    except ObjectDoesNotExist:
        LOGGER.info(msg='Go to save file => {github_path}'.format(github_path=file_server_data['path']))
    else:
        if data_file.processed:
            LOGGER.info(msg='Already file found not processed')
            return False
        else:
            file_data_importer.delay(data_file_id=data_file.id)
            return True

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
    file_data_importer.delay(data_file_id=data_file.id)
    return True


@app.task
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
            file_data_downloader.apply_async(
                kwargs={
                    'file_server_data': file_,
                }
            )
            good_files += 1
    return good_files
