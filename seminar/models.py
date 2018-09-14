# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.conf import settings

from .model_choices.season_choice import season_choice

# Create your models here.


class SeminarGroup(models.Model):
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    season = models.IntegerField(choices=season_choice.choice)

    def __unicode__(self):
        return u"%d - %d %s" % (
            self.start_date.year, self.start_date.year + 1, season_choice.get_verbose_name(self.season)
        )


class Seminar(models.Model):
    seminar_group = models.ForeignKey(SeminarGroup, blank=True, related_name="seminars")
    author = models.CharField(max_length=128, null=True, blank=True)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL)
    upload_time = models.DateTimeField(auto_now_add=True)
    seminar_time = models.DateField()
    title = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)


class SeminarFile(models.Model):
    seminar = models.ForeignKey(Seminar, related_name="seminar_file")
    upload_time = models.DateTimeField(auto_now_add=True)
    path = models.FileField(upload_to=settings.SEMINAR_UPLOAD_PATH)
    download_count = models.IntegerField(default=0)
