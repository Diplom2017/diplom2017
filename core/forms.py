# coding: utf-8
from django import forms


from core.models import Examination, Question, Answer


class ExaminationEditForm(forms.ModelForm):

    class Meta:
        model = Examination
        fields = ('name',)


class QuestionEditForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('body',)


class AnswerEditForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ('body', 'points')
