# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import redirect

from core.models import Category, Examination, UserExamination
from core.views.base import CreateOrUpdateView, ListView
from django.core.urlresolvers import reverse_lazy


class CategoryListView(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'core/categories.html'
    title = 'Список категорий'
category_list_view = CategoryListView.as_view()


class CategoryExaminationsListView(ListView):
    model = Examination
    context_object_name = 'examinations'
    template_name = 'core/examinations.html'
    title = 'Список тестирований'

    def get_queryset(self):
        qs = super(CategoryExaminationsListView, self).get_queryset()
        qs = qs.filter(category=self.kwargs['category_id'])
        return qs

    def get_context_data(self, **kwargs):
        context = super(CategoryExaminationsListView, self).get_context_data()
        tested_user_examinations = []
        examinations = context['examinations']

        for examination in context['examinations']:
            if UserExamination.objects.get(examination=examination, user=self.request.user):
                tested_user_examinations.append(UserExamination.objects.get(examination=examination, user=self.request.user))
                examinations = examinations.exclude(id=examination.id)
        context['examinations'] = examinations
        context['tested_user_examinations'] = tested_user_examinations
        return context
category_examinations_list_view = CategoryExaminationsListView.as_view()

