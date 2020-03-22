""" Module to define api no rest views """
import os
import datetime
import mimetypes

from django.http.response import Http404
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from api.models import DataFile
from api.models import GeneralData

from api.serializers import GeneralDataSerializer


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


def download_all_data_on_csv(request):
    """ View to generate data to csv """
    GeneralData.objects.to_csv()


class GeneralDataViewSet(ModelViewSet):
    queryset = GeneralData.objects.order_by('last_update')
    serializer_class = GeneralDataSerializer
    allowed_methods = ['GET']

    @action(detail=False, methods=['GET'])
    def today(self, request):
        """ Action uri to return actual covid information """
        today = datetime.date.today()
        queryset = GeneralData.objects.filter(
            last_update__year=today.year,
            last_update__month=today.month,
            last_update__day=today.day,
        )
        serializer_class = self.get_serializer_class()
        serialzer = serializer_class(queryset, many=True)
        return Response(serialzer.data, status=200)


