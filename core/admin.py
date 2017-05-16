# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin


from .models import User, Examination, Question, Answer, UserExamination,\
    UserExaminationQuestionLog, UserExaminationAnswerLog


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', )


class ExaminationAdmin(admin.ModelAdmin):
    list_display = ('name',)


class AnswerInline(admin.StackedInline):
    model = Answer


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('body', )

    inlines = [
        AnswerInline
    ]


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('body', )


class UserExaminationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'examination')


class UserExaminationAnswerAdmin(admin.ModelAdmin):
    list_display = ('user_examination', )


class UserExaminationQuestionLogAdmin(admin.ModelAdmin):
    pass


class UserExaminationAnswerLogAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(Examination, ExaminationAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(UserExamination, UserExaminationAdmin)
admin.site.register(UserExaminationQuestionLog, UserExaminationQuestionLogAdmin)
admin.site.register(UserExaminationAnswerLog, UserExaminationAnswerLogAdmin)
