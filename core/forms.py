# coding: utf-8
from django import forms


from core.models import Examination, Question, Answer, User


class ExaminationEditForm(forms.ModelForm):

    class Meta:
        model = Examination
        fields = ('name',)


class QuestionEditForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('body', 'sum_points')


class AnswerEditForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ('body', 'points')


class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('next_test_time',)