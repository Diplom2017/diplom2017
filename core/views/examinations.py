# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from core.models import Examination, UserExamination
from core.views.base import ListView


class ExaminationListView(ListView):
    model = Examination
    context_object_name = 'examinations'
    template_name = 'core/examinations.html'
    title = 'Список доступных тестирований'

    def get_queryset(self):
        qs = super(ExaminationListView, self).get_queryset()
        for examination in qs:
            if UserExamination.objects.filter(examination=examination, user=self.request.user):
                qs = qs.exclude(id=examination.id)
        return qs
examination_list_view = ExaminationListView.as_view()
