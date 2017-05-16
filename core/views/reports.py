# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from core.models import User
from core.views.base import ListView


class HighUserExamination(ListView):
    model = User
    context_object_name = 'users'
    template_name = 'core/reports/high_points.html'
    title = 'Рейтинг преподователей'
high_user_examination_view = HighUserExamination.as_view()
