""" Module to define api no rest views """
import os
import mimetypes

from django.http.response import Http404
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from api.models import DataFile


def download_csv_file(request, data_file_id):
    """ View to download DataFile """
    data_file = get_object_or_404(DataFile, id=data_file_id, origin_file__isnull=False)
    if not os.path.exists(data_file.origin_file.path):
        raise Http404
    content_type = mimetypes.guess_type(data_file.origin_file.name)
    response = HttpResponse(
        content_type=content_type,
        status=200,
    )
    response.write(open(data_file.origin_file.path, 'rb').read())
    response['Content-Disposition'] = 'attachment; filename={name}'.format(name=data_file.origin_file.name)
    return response
