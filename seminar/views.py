# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urllib
import sys

from itertools import groupby
from operator import itemgetter

from django.shortcuts import render
from django.http.response import FileResponse, HttpResponseNotFound
from django.contrib.auth import authenticate, login, logout

from .models import SeminarFile, SeminarGroup, Seminar
from .model_choices.season_choice import season_choice


# Create your views here.


def get_file_view(request):
    id = request.GET.get('id', None)
    if id is None:
        return HttpResponseNotFound()

    # determine whether user has permission to download private file:
    perm_private = request.user.has_perm('seminar.download_private_file') if request.user is not None else False

    try:
        s_file = SeminarFile.objects.get(id=id)
        if not s_file.seminar.public and not perm_private:
            return HttpResponseNotFound()

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

    login_result = {}

    if request.method == 'POST':
        action = request.POST["action"]
        if action == 'login':
            username = request.POST["username"]
            password = request.POST["password"]

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                login_result["succeed"] = True
            else:
                login_result["succeed"] = False

        if action == 'logout':
            logout(request)

    seminar_groups = SeminarGroup.objects.order_by('-start_date').all()
    this_seminar_group = None
    try:
        this_seminar_group = seminar_groups.latest('start_date') if group is None else seminar_groups.get(id=group)
        seminars = this_seminar_group.seminars.prefetch_related('seminar_file').select_related("uploader").all()
    except (Seminar.DoesNotExist, SeminarGroup.DoesNotExist):
        seminars = []

    # determine whether user has permission to download private file:
    perm_private = request.user.has_perm('seminar.download_private_file') if request.user is not None else False

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
            ] if seminar.public or perm_private else []
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
        "login_result": login_result,
    }

    return render(request, 'seminar.htm', seminar_dict)
