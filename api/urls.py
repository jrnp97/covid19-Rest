from django.urls.conf import path
from django.urls.conf import include

from rest_framework import routers

from api.views import download_csv_file
from api.views import GeneralDataViewSet


router = routers.DefaultRouter()
router.register(r'data', GeneralDataViewSet,)


app_name = 'api'
urlpatterns = [
    path('', include(router.urls)),
    path('data_file/<int:data_file_id>', download_csv_file, name='data_file_download')
]
