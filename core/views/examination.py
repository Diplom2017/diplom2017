# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from collections import defaultdict
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms import model_to_dict
from django.shortcuts import redirect, render
from core.views.base import ListView, DetailView, TemplateView

from core.models import (
    UserExamination, UserExaminationQuestionLog, UserExaminationAnswerLog, User, Question, Answer,
    Examination)
from random import random, shuffle


class UserExaminationListView(ListView):
    model = UserExamination
    context_object_name = 'user_examinations'
    template_name = 'core/user_examinations.html'
    title = 'Список пройденных тестирований'

    def get_queryset(self):
        qs = super(UserExaminationListView, self).get_queryset()
        if not self.request.user.is_superuser or not self.request.user.is_staff:
            qs.filter(user=self.request.user)
        return qs
user_examination_list_view = UserExaminationListView.as_view()


class UserExaminationProcessView(TemplateView):
    _user_examination = None
    _user_examination_question_log = None
    _examination = None
    template_name = 'core/examination.html'

    def get_examination(self):
        if not self._examination:
            self._examination = Examination.objects.get(id=self.kwargs['examination_id'])
        return self._examination

    def get_user_examination(self):
        if not self._user_examination:
            examination = self.get_examination()
            if not UserExamination.objects.filter(user=self.request.user, examination=examination, finished_at__isnull=True):
                user_examination = UserExamination.objects.create(user=self.request.user, examination=examination)
            else:
                user_examination = UserExamination.objects.get(user=self.request.user, examination=examination, finished_at__isnull=True)
            self._user_examination = user_examination
        return self._user_examination

    def get_user_examination_question_log(self):
        if not self._user_examination_question_log:
            user_examination_question_log_id = self.kwargs.get('user_examination_question_log_id')
            if not user_examination_question_log_id:
                raise AttributeError('user_examination_question_log_id kwarg not found')
            self._user_examination_question_log = self.get_user_examination().logs.get(id=user_examination_question_log_id)
        return self._user_examination_question_log

    def dispatch(self, request, *args, **kwargs):
        user_examination_question_log_id = kwargs.get('user_examination_question_log_id')

        user_examination = self.get_user_examination()

        if user_examination.started_at is None:
            user_examination.start()

        if user_examination_question_log_id is None:
            next_log_id = UserExaminationQuestionLog.get_next_id(user_examination=user_examination)

            if next_log_id is None:
                user_examination.finish()
                messages.success(request, 'Тестирование %s завершено.' % user_examination.examination.name)
                redirect_to = redirect(reverse('examination_list_view'))
            else:
                redirect_to = redirect(reverse(user_examination_process_view, args=[user_examination.examination_id, next_log_id]))
            return redirect_to

        user_examination_question_log = self.get_user_examination_question_log()
        if user_examination_question_log.user_examination_answer_logs.exists():
            return redirect(reverse(user_examination_process_view, args=[user_examination.examination_id]))

        return super(UserExaminationProcessView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user_examination_question_log = self.get_user_examination_question_log()
        redirect_to = reverse(user_examination_process_view, args=[self.get_examination().id])

        answers_ids = [int(answer_id) for answer_id in request.POST.getlist('answer_id')]

        if len(answers_ids) < 1:
            return redirect(redirect_to)

        question_answers = json.loads(user_examination_question_log.question_answers_data)

        if len(answers_ids) > len(question_answers):
            return redirect(redirect_to)

        for answer_id in answers_ids:
            answer_backuped_data = [
                question_answer for question_answer in question_answers if question_answer['id'] == answer_id
            ][0]

            try:
                answer_obj = Answer.objects.get(id=answer_id)
            except Answer.DoesNotExist:
                answer_obj = None

            UserExaminationAnswerLog.objects.create(
                answer=answer_obj, user_examination_question_log=user_examination_question_log,
                answer_data=answer_backuped_data)

        return redirect(redirect_to)

    def get_title(self):
        user_examination = self.get_user_examination()
        return 'Тестирование %s, осталось вопросов: %s' % (
            user_examination.examination, UserExaminationQuestionLog.get_remains_for_user_examination(user_examination))

    def get_context_data(self, **kwargs):
        context = super(UserExaminationProcessView, self).get_context_data(**kwargs)
        user_examination = self.get_user_examination()
        user_examination_question_log = self.get_user_examination_question_log()
        context.update({
            'user_examination_question_log': user_examination_question_log,
            'user_examination': user_examination,
            'question': json.loads(user_examination_question_log.question_data),
            'answers': json.loads(user_examination_question_log.question_answers_data),
            'input_type': 'checkbox'
        })
        return context
user_examination_process_view = UserExaminationProcessView.as_view()


class UserExaminationDetailView(DetailView):
    model = UserExamination
    pk_url_kwarg = 'user_examination_id'
    context_object_name = 'user_examination'
    template_name = 'core/examination_detail.html'
    _question_log_qs = None
    _answer_log_qs = None

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return super(UserExaminationDetailView, self).get_queryset()
        else:
            return UserExamination.get_for_user(self.request.user)

    def get_answer_log_qs(self):
        if self._answer_log_qs is None:
            self._answer_log_qs = UserExaminationAnswerLog.objects.filter(user_examination_question_log__in=self.get_question_log())
        return self._answer_log_qs

    def get_question_log(self):
        if self._question_log_qs is None:
            self._question_log_qs = UserExaminationQuestionLog.objects.filter(user_examination=self.object)
            for ql_qs in self._question_log_qs:
                ql_qs.question_data = json.loads(ql_qs.question_data)
                ql_qs.question_answers_data = json.loads(ql_qs.question_answers_data)
        return self._question_log_qs

    def get_answer_log_for_question_log(self):
        answer_log_objects = defaultdict(list)
        answer_log_qs = self.get_answer_log_qs()
        for answer_log in answer_log_qs:
            answer_log.answer_data = json.loads(answer_log.answer_data)
            answer_log_objects[answer_log.user_examination_question_log_id].append(answer_log)
        return answer_log_objects

    def get_title(self):
        user_examination = self.get_object()
        return 'Пользователь %s, тестирование %s' % (user_examination.user, user_examination.examination)

    def get_context_data(self, **kwargs):
        context = super(UserExaminationDetailView, self).get_context_data(**kwargs)
        context['question_log'] = self.get_question_log()
        context['answer_log'] = self.get_answer_log_for_question_log()
        return context
user_examination_detail_view = UserExaminationDetailView.as_view()
