# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.forms.models import ModelForm
from django.forms.models import BaseModelFormSet
from .models import Seminar, SeminarFile, SeminarGroup
from .model_choices.season_choice import season_choice
import calendar
import datetime

# Register your models here.

SPRING_MONTH = (2, 3, 4, 5, 6, 7)
AUTUMN_MONTH = (8, 9, 10, 11, 12, 1)


def get_last_day_of_month(year, month):
    return calendar.monthrange(year, month)[1]


class SeminarFileInline(admin.TabularInline):
    model = SeminarFile
    extra = 1
    fields = ('path', )


class SeminarModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'uploader', 'upload_time')
    list_display_links = ('id', 'title')
    ordering = ('-upload_time', )
    inlines = (SeminarFileInline, )

    fields = ('title', 'author', 'description', 'seminar_time', 'seminar_group')

    def save_model(self, request, obj, form, change):
        # type: (object, Seminar, object, object) -> object
        obj.uploader = request.user
        if obj.seminar_group_id is None:
            sg = SeminarGroup.objects.filter(start_date__lte=obj.seminar_time, end_date__gte=obj.seminar_time).last()
            if sg is None:
                # Create a seminar group
                start_year = obj.seminar_time.year

                if obj.seminar_time.month in SPRING_MONTH:
                    end_year = start_year
                    start_month = SPRING_MONTH[0]
                    end_month = SPRING_MONTH[-1]
                    season = season_choice.SPRING
                else:
                    end_year = start_year + 1
                    start_month = AUTUMN_MONTH[0]
                    end_month = AUTUMN_MONTH[-1]
                    season = season_choice.AUTUMN

                sg = SeminarGroup.objects.create(
                    start_date=datetime.datetime(
                        year=start_year,
                        month=start_month,
                        day=1,
                    ),
                    end_date=datetime.datetime(
                        year=end_year,
                        month=end_month,
                        day=get_last_day_of_month(end_year, end_month)
                    ),
                    season=season,
                )

            obj.seminar_group = sg
        return super(SeminarModelAdmin, self).save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        # type: (object, object, BaseModelFormSet, object) -> object
        if formset.model == SeminarFile:
            instances = formset.save(commit=False)

            for instance in instances:
                instance.filename = instance.path.file.name
                instance.save()
            return instances
        else:
            return formset.save()


admin.site.register(Seminar, SeminarModelAdmin)
admin.site.register([SeminarGroup, ])
