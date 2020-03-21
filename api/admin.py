""" Module to register models to manage on django admin """
from django.contrib import admin
from django.contrib.admin import register

from api.models import DataFile
from api.models import GeneralData


@register(DataFile)
class DataFileAdmin(admin.ModelAdmin):
    list_display = (
        'signature',
        'origin_file',
        'processed',
        'create_date',
        'update_date',
        'download_file',
    )
    search_fields = (
        'origin_file',
    )
    list_filter = (
        'create_date',
        'processed',
        'normalized',
    )

    def re_process_file(self, request, queryset):
        """ Method to sent to retry files """
        from api.tasks import file_data_importer
        for data_file in queryset.filter(processed=False):
            file_data_importer.delay(data_file.id)
        self.message_user(request, 'File send to process successfully...')

    actions = [
        're_process_file',
    ]

@register(GeneralData)
class GeneralDataAdmin(admin.ModelAdmin):
    list_display = [f.name for f in GeneralData._meta.fields]
