""" Module to define API DB Models """
import hashlib
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.postgres.fields import JSONField

from api.exceptions import AlreadyProcessedFile


class DataFile(models.Model):
    """ DB Table to track imported files """
    origin_file = models.FileField(upload_to='covid_data')
    signature = models.TextField(unique=True)
    create_date = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    normalized = models.BooleanField(default=False)
    process_detail = models.TextField(null=True)
    headers = JSONField(default=dict)

    def generate_checksum(self):
        """
        Function to generate file checksum.
        Returns:
            A hex str describing file checksum.
        """
        from api.utils import generate_md5_checksum
        return generate_md5_checksum(self.origin_file.path)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """ Override to generate file checksum """
        if not self.signature:
            self.signature = self.generate_checksum()
        try:
            DataFile.objects.get(signature=self.signature)
        except ObjectDoesNotExist:
            super().save(
                force_insert=force_insert,
                force_update=force_update,
                using=using,
                update_fields=update_fields,
            )
        else:
            raise AlreadyProcessedFile


class GeneralData(models.Model):
    """ Model to save COVID data completely """
    province_state = models.CharField(max_length=200, verbose_name='Province/State')
    country_region = models.CharField(max_length=200, verbose_name='Country/Region')
    last_update = models.DateTimeField(verbose_name='Last Update')
    confirmed = models.BigIntegerField()
    deaths = models.BigIntegerField()
    recovered = models.BigIntegerField()
    Suspected = models.BigIntegerField(null=True, blank=True)
    latitude = models.BigIntegerField(null=True, blank=True)
    longitude = models.BigIntegerField(null=True, blank=True)
    report_day = models.DateField()

    def __str__(self):
        return '{0} - {1}'.format(self.country_region, self.province_state)
