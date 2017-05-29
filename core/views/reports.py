# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db.models import Max
from django.shortcuts import render

from core.models import User, UserExamination
from core.views.base import ListView


class HighUserExamination(ListView):
    model = User
    context_object_name = 'users'
    template_name = 'core/reports/high_points.html'
    title = 'Рейтинг преподователей'
high_user_examination_view = HighUserExamination.as_view()


def average_points_view(request):
    user_examinations = UserExamination.objects.filter(examination__id='4')

    count = user_examinations.count()
    total = 0
    minimum = user_examinations[0].points
    maximum = 0

    for user_examination in user_examinations:
        total += user_examination.points
        if user_examination.points < minimum:
            minimum = user_examination.points
        elif user_examination.points > maximum:
            maximum = user_examination.points

    average = total/count

    users = User.objects.annotate(max_point=Max('user_examinations__points')).order_by('max_point')

    data = [
        ['Максимум', maximum],
        ['Среднее', average],
        ['Минимум', minimum],
    ]

    context = {
        'title': 'Максимальное, минимальное и среднее значение по кол-ву баллов',
        'minimum': minimum,
        'maximum': maximum,
        'average': average,
        'data': json.dumps(data),
        'users': users,
    }

    return render(request, 'core/reports/average_points.html', context)


def user_process_view(request):
    user_examinations = UserExamination.objects.filter(examination__id='4', user=request.user)

    titles = []
    data = []

    for user_examination in user_examinations:
        titles.append(str(user_examination.finished_at.date()))
        data.append(user_examination.points)

    context = {
        'title': 'Не знаю как обозвать его',
        'titles': json.dumps(titles),
        'data': json.dumps(data),
    }

    return render(request, 'core/reports/user_process.html', context)
