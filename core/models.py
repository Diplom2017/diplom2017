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
    email = models.EmailField(unique=True, blank=True)
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


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Examination(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    category = models.ForeignKey(Category, related_name='examinations', verbose_name='Категория')
    minutes_to_pass = models.PositiveSmallIntegerField(default=30, verbose_name='Сколько минут дано на тест')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'тестирование'
        verbose_name_plural = 'Тестирования'


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
    is_right = models.BooleanField(default=False, verbose_name='Правильный')

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

    must_finished_at = models.DateTimeField(null=True, blank=True, verbose_name='Обязан закончить до')

    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Начат')
    finished_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name='Закончен')

    class Meta:
        verbose_name = 'тестирование пользователя'
        verbose_name_plural = 'Тестирования пользователей'
        unique_together = ('user', 'examination')

    def __unicode__(self):
        return '[UserExamination] #%s' % self.id

    def __str__(self):
        return '#%s' % self.id

    def save(self, *args, **kwargs):
        instance = super(UserExamination, self).save(*args, **kwargs)
        if not self.logs.exists() and self.examination.questions.all():
            examination_questions = list(self.examination.questions.all())
            random.shuffle(examination_questions)

            objects_for_bulk = []

            for position, question in enumerate(examination_questions):
                question_answers_data = []
                for answer in question.answers.all():
                    question_answers_data.append(model_to_dict(answer))

                objects_for_bulk.append(UserExaminationQuestionLog(
                    position=position, user_examination=self, question=question,
                    question_data=model_to_dict(question), question_answers_data=question_answers_data
                ))

            UserExaminationQuestionLog.objects.bulk_create(objects_for_bulk)
        return instance

    @classmethod
    def get_for_user(cls, user, **kwargs):
        return cls.objects.filter(user=user, **kwargs)

    @classmethod
    def fixed_started(cls):
        for user_examination_id in UserExamination.objects.filter(finished_at__isnull=True).values_list('id', flat=True):
            cls.fixed_started_one(user_examination_id)

    @classmethod
    def fixed_started_one(cls, user_examination_id):
        user_examination = cls.objects.get(id=user_examination_id, finished_at__isnull=True)
        if datetime.datetime.now() > user_examination.must_finished_at:
            user_examination.finish()
            for question in user_examination.examination.questions.all():
                UserExaminationQuestionLog.objects.get_or_create(
                    user_examination=user_examination, question=question,
                    defaults={'question_data': model_to_dict(question)}
                )

    def get_remaining_minutes(self):
        if self.started_at is None:
            return None
        minutes = int((self.must_finished_at - datetime.datetime.now()).total_seconds() / 60)

        if minutes < 0:
            return 0
        return minutes

    def can_view_logs(self, user=None):
        if user and user.is_staff:
            return True

        if self.finished_at is None:
            return False

        deadline_dt = self.finished_at + datetime.timedelta(hours=1)
        return datetime.datetime.now() < deadline_dt

    def finish(self, force=False):
        if not force:
            assert self.finished_at is None
            assert self.points == 0

        self.finished_at = datetime.datetime.now()
        self.calculate_points(commit=False)
        self.save()

    def start(self):
        started_at = datetime.datetime.now()
        must_finished_at = started_at + datetime.timedelta(minutes=self.examination.minutes_to_pass)

        self.started_at = started_at
        self.must_finished_at = must_finished_at
        self.save()

    def calculate_points(self, force=False, commit=True):
        assert self.finished_at

        if not force:
            assert self.points == 0

        points = 0

        question_logs = self.logs.all()

        questions_count = len(question_logs)
        point_for_one_right_answer = float(100) / questions_count

        for question_log in question_logs:

            right_answers_count = question_log.get_right_answers_count()

            right_answers_user_count = 0
            for answer in question_log.user_examination_answer_logs.all():
                right_answers_user_count += answer.is_right

            if right_answers_user_count > 0:
                points += point_for_one_right_answer * float(right_answers_count) / right_answers_user_count

        self.points = points

        if commit:
            self.save()

        return self


class UserExaminationQuestionLog(models.Model):
    user_examination = models.ForeignKey(UserExamination, related_name='logs')
    question = models.ForeignKey(Question, on_delete=DO_NOTHING, related_name='logs')

    position = models.PositiveSmallIntegerField()

    question_data = JSONField(default={})
    question_answers_data = JSONField(default=[])

    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)

    skipped_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['skipped_at', 'position']
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

        return qs.count() - qs.filter(finished_at__isnull=False).count()

    def get_right_answers_count(self):
        return len(
            [qa['is_right'] for qa in json.loads(self.question_answers_data)
             if qa['is_right'] is True]
        )


class UserExaminationAnswerLog(models.Model):
    user_examination_question_log = models.ForeignKey(UserExaminationQuestionLog,
                                                      related_name='user_examination_answer_logs')
    is_right = models.BooleanField()

    answer = models.ForeignKey(Answer, null=True, on_delete=DO_NOTHING)
    answer_data = JSONField()

    class Meta:
        verbose_name = 'Лог ответов на вопросы'
        verbose_name_plural = 'Лог ответов на вопросы'

