# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from core.models import Examination, UserExamination
from core.views.base import ListView


class ExaminationListView(ListView):
    model = Examination
    context_object_name = 'examinations'
    template_name = 'core/examinations.html'
    title = 'Список доступных тестирований'
examination_list_view = ExaminationListView.as_view()
