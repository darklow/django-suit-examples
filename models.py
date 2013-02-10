from datetime import datetime
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models, connections
from pprint import pprint


class Continent(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=256)
    code = models.CharField(max_length=2,
                            help_text='ISO 3166-1 alpha-2 - two character '
                                      'country code')
    independence_day = models.DateField(blank=True, null=True)
    continent = models.ForeignKey(Continent, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Countries"


import urllib2
from django.utils import simplejson
