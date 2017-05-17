# -*- coding: utf-8 -*-
import datetime
import json

import random
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.db.models import DO_NOTHING

from core.fields import JSONField
from django.forms import model_to_dict


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, verbose_name='Логин пользователя')
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    second_name = models.CharField(max_length=150, verbose_name='Отчество')

    last_test_time = models.DateField(blank=True, null=True, verbose_name='Дата последнего учёта')
    next_test_time = models.DateField(blank=True, null=True, verbose_name='Дата следующего учёта')

    is_staff = models.BooleanField(default=False, verbose_name='Доступ в административную часть')
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __unicode__(self):
        return self.get_full_name()

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = 'пользователя'
        verbose_name_plural = 'Пользователи'

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def get_max_points(self):
        max_points = 0
        for user_examination in self.user_examinations.all():
            if max_points < user_examination.points:
                max_points = user_examination.points
        return max_points


class Examination(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')

    class Meta:
        verbose_name = 'тестирование'
        verbose_name_plural = 'Тестирования'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Question(models.Model):
    examination = models.ForeignKey(Examination, related_name='questions', verbose_name='Тестирование')
    body = models.TextField(verbose_name='Текст')

    def __unicode__(self):
        return self.body

    def __str__(self):
        return self.body

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'Вопросы'


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', verbose_name='Вопрос')
    body = models.TextField(verbose_name='Текст')
    points = models.PositiveSmallIntegerField(verbose_name='Кол-во баллов')

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.body)

    def __str__(self):
        return '[%s] %s' % (self.id, self.body)

    class Meta:
        verbose_name = 'ответ'
        verbose_name_plural = 'Ответы на вопросы'


class UserExamination(models.Model):
    examination = models.ForeignKey(Examination, related_name='user_examinations', verbose_name='Тестирование')
    user = models.ForeignKey(User, related_name='user_examinations', verbose_name='Пользователь')

    points = models.PositiveSmallIntegerField(default=0, verbose_name='Баллы')

    created_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Начат')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='Закончен')

    class Meta:
        verbose_name = 'тестирование пользователя'
        verbose_name_plural = 'Тестирования пользователей'

    def __unicode__(self):
        return '[UserExamination] #%s' % self.id

    def __str__(self):
        return '#%s' % self.id

    def save(self, *args, **kwargs):
        instance = super(UserExamination, self).save(*args, **kwargs)
        if not self.logs.exists() and self.examination.questions.all():
            examination_questions = list(self.examination.questions.all())

            objects_for_bulk = []

            for position, question in enumerate(examination_questions):
                question_answers_data = []
                for answer in question.answers.all():
                    question_answers_data.append(model_to_dict(answer))

                objects_for_bulk.append(UserExaminationQuestionLog(user_examination=self, question=question,
                                                                   question_data=model_to_dict(question),
                                                                   question_answers_data=question_answers_data))

            UserExaminationQuestionLog.objects.bulk_create(objects_for_bulk)
        return instance

    @classmethod
    def get_for_user(cls, user, **kwargs):
        return cls.objects.filter(user=user, **kwargs)

    def finish(self):
        self.finished_at = datetime.datetime.now()
        self.calculate_points(commit=False)
        self.user.last_test_time = datetime.date.today()
        self.save()

    def start(self):
        self.started_at = datetime.datetime.now()
        self.save()

    def calculate_points(self, force=False, commit=True):
        if not force:
            assert self.points == 0

        points = 0

        question_logs = self.logs.all()

        for question_log in question_logs:

            points_user_count = 0
            for answer in question_log.user_examination_answer_logs.all():
                points_user_count += answer.answer.points

            points += points_user_count

        self.points = points

        if commit:
            self.save()

        return self


class UserExaminationQuestionLog(models.Model):
    user_examination = models.ForeignKey(UserExamination, related_name='logs')
    question = models.ForeignKey(Question, on_delete=DO_NOTHING, related_name='logs')

    question_data = JSONField(default={})
    question_answers_data = JSONField(default=[])

    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Лог ответов'
        verbose_name_plural = 'Лог ответов'

    @classmethod
    def get_next_id(cls, user_examination):
        try:
            return cls.objects.filter(
                user_examination=user_examination, user_examination_answer_logs__isnull=True
            ).values_list('id', flat=True)[0]
        except Exception as e:
            return None

    @classmethod
    def get_remains_for_user_examination(cls, user_examination):
        qs = cls.objects.filter(user_examination=user_examination)

        return qs.count() - qs.filter(user_examination_answer_logs__isnull=True).count()


class UserExaminationAnswerLog(models.Model):
    user_examination_question_log = models.ForeignKey(UserExaminationQuestionLog,
                                                      related_name='user_examination_answer_logs')

    answer = models.ForeignKey(Answer, null=True, on_delete=DO_NOTHING)
    answer_data = JSONField()

    class Meta:
        verbose_name = 'Лог ответов на вопросы'
        verbose_name_plural = 'Лог ответов на вопросы'
