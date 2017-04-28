# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from core.models import Examination
from core.views.base import ListView


class ExaminationListView(ListView):
    model = Examination
    context_object_name = 'examinations'
    template_name = 'core/examinations.html'
    title = 'Список тестирований'

    def get_queryset(self):
        qs = super(ExaminationListView, self).get_queryset()
        qs = qs.filter(category=self.kwargs['category_id'])
        return qs

examination_list_view = ExaminationListView.as_view()


