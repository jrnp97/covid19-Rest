from django.db import models

# Create your models here.


class GeneralData(models.Model):
    """ Model to save covid data completally """
    province_state = models.CharField(max_length=200, verbose_name='Province/State')
    country_region = models.CharField(max_length=200, verbose_name='Country/Region')
    last_update = models.DateTimeField(verbose_name='Last Update')
    confirmed = models.BigIntegerField()
    deaths = models.BigIntegerField()
    recovered = models.BigIntegerField()
    latitude = models.BigIntegerField(null=True)
    longitude = models.BigIntegerField(null=True)
    report_day = models.DateField()
