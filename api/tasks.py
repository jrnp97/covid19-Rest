# -*- coding: utf-8 -*-
""" Module to create tasks of project """
import os
import logging
import tempfile

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile


from api.utils import github_api_request
from api.exceptions import AlreadyProcessedFile
from api.models import DataFile


LOGGER = logging.getLogger(__file__)


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
    data_file = DataFile.objects.create(
        origin_file=ContentFile(open(temp_path, 'rb').read()),
        signature=file_server_data['sha'],
    )
    # TODO Import data on model
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
