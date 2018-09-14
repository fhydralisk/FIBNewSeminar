# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urllib
import sys

from itertools import groupby
from operator import itemgetter

from django.shortcuts import render
from django.http.response import FileResponse, HttpResponseNotFound

from .models import SeminarFile, SeminarGroup, Seminar
from .model_choices.season_choice import season_choice

# Create your views here.


def get_file_view(request):
    id = request.GET.get('id', None)
    if id is None:
        return HttpResponseNotFound()

    try:
        s_file = SeminarFile.objects.get(id=id)
        s_file.download_count += 1
        s_file.save()
    except SeminarFile.DoesNotExist:
        return HttpResponseNotFound()
    else:
        response = FileResponse(open(s_file.path.path), content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment;filename="{filename}"'.format(
            filename=urllib.quote(s_file.filename.encode(sys.getdefaultencoding()))
        )
        return response


def seminar_view(request, group=None):
    seminar_groups = SeminarGroup.objects.order_by('-start_date').all()
    this_seminar_group = None
    try:
        this_seminar_group = seminar_groups.latest('start_date') if group is None else seminar_groups.get(id=group)
        seminars = this_seminar_group.seminars.prefetch_related('seminar_file').select_related("uploader").all()
    except (Seminar.DoesNotExist, SeminarGroup.DoesNotExist):
        seminars = []

    seminar_list = [
        {
            "time": seminar.seminar_time,
            "title": seminar.title,
            "author": seminar.author,
            "uploader": seminar.uploader.username,
            "files": [
                {
                    "id": fid.id,
                    "filename": fid.filename,
                }
                for fid in seminar.seminar_file.all()
            ]
        }
        for seminar in seminars
    ]

    seminar_list.sort(key=itemgetter('time'))
    grouped_seminar_list = groupby(seminar_list, itemgetter('time'))
    grouped_seminar_list = [(time, list(group)) for time, group in grouped_seminar_list]

    seminar_dict = {
        "seminar_groups": [
            {
                "id": seminar_group.id,
                "start_year": seminar_group.start_date.year,
                "end_year": seminar_group.start_date.year + 1,
                "season": season_choice.get_verbose_name(seminar_group.season),
            }
            for seminar_group in seminar_groups
        ],
        "this_seminar_group": {
            "id": this_seminar_group.id,
            "start_year": this_seminar_group.start_date.year,
            "end_year": this_seminar_group.start_date.year + 1,
            "season": season_choice.get_verbose_name(this_seminar_group.season),
        } if this_seminar_group is not None else None,
        "seminars": grouped_seminar_list,
    }

    return render(request, 'seminar.htm', seminar_dict)
