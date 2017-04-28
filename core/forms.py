# coding: utf-8
from django import forms


from core.models import Examination, Question, Answer


class ExaminationEditForm(forms.ModelForm):

    class Meta:
        model = Examination
        fields = ('name', 'minutes_to_pass', 'category')


class QuestionEditForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('body',)


class AnswerEditForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ('body', 'is_right')


class ExaminationSearchForm(forms.Form):
    pass
