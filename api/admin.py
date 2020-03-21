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
    )
    search_fields = (
        'origin_file',
    )
    list_filter = (
        'create_date',
        'processed',
        'normalized',
    )


@register(GeneralData)
class GeneralDataAdmin(admin.ModelAdmin):
    list_display = [f.name for f in GeneralData._meta.fields]
