# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from core.models import Examination, UserExamination
from core.views.base import ListView


class ExaminationListView(ListView):
    model = Examination
    context_object_name = 'examinations'
    template_name = 'core/examinations.html'
    title = 'Вы можете пройти учётное тестирование'

    def get_context_data(self, **kwargs):
        context = super(ExaminationListView, self).get_context_data()
        if self.request.user.next_test_time:
            if self.request.user.next_test_time > datetime.date.today():
                context['title'] = 'Следующий учёт можно пройти ' + str(self.request.user.next_test_time)
                context['examinations'] = ''
        else:
            context['examinations'] = ''
            context['title'] = 'Время следующего учёта не установленно'
        return context
examination_list_view = ExaminationListView.as_view()
