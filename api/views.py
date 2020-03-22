""" Module to define api no rest views """
import os
import io
import datetime
import mimetypes

from django.http.response import Http404
from django.http.response import HttpResponse

from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet
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


class GeneralDataViewSet(ReadOnlyModelViewSet):
    queryset = GeneralData.objects.order_by('last_update')
    serializer_class = GeneralDataSerializer
    allowed_methods = ['GET']
    filterset_fields = [
        'report_day',
        'country_region',
        'province_state',
    ]

    @action(detail=False, methods=['GET'])
    def today(self, request):
        """ EndPoint to return actual covid information """
        today = datetime.date.today()
        queryset = GeneralData.objects.filter(
            last_update__year=today.year,
            last_update__month=today.month,
            last_update__day=today.day,
        )
        status_code = 200
        if queryset.exists():
            serializer_class = self.get_serializer_class()
            data = serializer = serializer_class(queryset, many=True).data
        else:
            status_code = 404
            data = {
                'details': 'Information not sync yet.'
            }
        return Response(data, status=status_code)

    @action(detail=False, methods=['GET'])
    def last(self, request):
        """ Endpoint giving last information update of covid """
        last_date = GeneralData.objects.order_by('-last_update').first().last_update.date()
        queryset = GeneralData.objects.filter(
            last_update__year=last_date.year,
            last_update__month=last_date.month,
            last_update__day=last_date.day,
        )
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        data = {
            'date': last_date,
            'data': serializer.data,
        }
        return Response(data, status=200)

    @action(detail=False, methods=['GET'])
    def csv(self, request):
        """ Endpoint to return a csv with all information collected """
        buffer = io.BytesIO()
        filename = 'all_covid_history_data_{date}.csv'.format(date=datetime.date.today())
        GeneralData.objects.to_csv(buffer)
        response = HttpResponse(
            content_type='text/csv',
            status=200,
        )
        response.write(buffer.getvalue())
        response['Content-Disposition'] = 'attachment; filename={name}'.format(name=filename)
        return response
