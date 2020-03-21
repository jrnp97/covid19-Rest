from django.urls.conf import path

from api.views import download_csv_file

app_name = 'api'
urlpatterns = [
    path('data_file/<int:data_file_id>', download_csv_file, name='data_file_download')
]
