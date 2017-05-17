# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import UpdateView

from core.forms import ExaminationEditForm, QuestionEditForm, AnswerEditForm, UserEditForm
from core.models import User
from core.views.base import CreateOrUpdateView, ListView, ParentListView, ParentCreateOrUpdateView, TitleMixin
from django.core.urlresolvers import reverse_lazy, reverse


class UserListView(ListView):
    model = User
    context_object_name = 'users'
    template_name = 'core/management/user_list.html'
    title = 'Список преподователей'
user_list_view = UserListView.as_view()


class UserTimeUpdateView(UpdateView, TitleMixin):
    model = User
    form_class = UserEditForm
    pk_url_kwarg = 'user_id'
    template_name = 'core/management/user_time_edit.html'
    title = 'Управление датой следующего тестирования'

    def get_success_url(self):
        return reverse('adm_user_list_view')
user_time_update_view = UserTimeUpdateView.as_view()
