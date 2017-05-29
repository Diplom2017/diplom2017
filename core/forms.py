# coding: utf-8
from django import forms


from core.models import Examination, Question, Answer, User, TextQuestion, TextUserAnswer


class ExaminationEditForm(forms.ModelForm):

    class Meta:
        model = Examination
        fields = ('name',)


class QuestionEditForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('body', 'sum_points')


class TextQuestionEditForm(forms.ModelForm):

    class Meta:
        model = TextQuestion
        fields = ('body',)


class AnswerEditForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ('body', 'points')


class TextUserAnswerEditForm(forms.ModelForm):

    class Meta:
        model = TextUserAnswer
        fields = ('body', 'points')


class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('next_test_time',)

        widgets = {
            'next_test_time': forms.DateInput(attrs={'class': 'datetimepicker'}),

        }
