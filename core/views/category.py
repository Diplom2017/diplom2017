# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import redirect

from core.models import Category
from core.views.base import CreateOrUpdateView, ListView
from django.core.urlresolvers import reverse_lazy


class CategoryListView(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'core/categories.html'
    title = 'Список категорий'

category_list_view = CategoryListView.as_view()

