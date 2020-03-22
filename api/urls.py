from django.urls.conf import path
from django.urls.conf import include

from django.views.generic import TemplateView

from rest_framework import routers
from rest_framework.schemas import get_schema_view

from api.views import download_csv_file
from api.views import GeneralDataViewSet


router = routers.DefaultRouter()
router.register(r'data', GeneralDataViewSet,)

schema_view = get_schema_view(
    title='COVID-19 API',
)

app_name = 'api'
urlpatterns = [
    path('v1/', include(router.urls)),
    path('doc/', TemplateView.as_view(
        template_name='api_doc.html'
    ), name='doc'),
    path('', schema_view, name='schema'),
    path('data_file/<int:data_file_id>', download_csv_file, name='data_file_download'),
]
