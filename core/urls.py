from django.conf.urls import patterns, url

from core.views import examinations, examination, reports
from core.views.management import management_examination_time
from core.views.management import management_examinations

urlpatterns = [
    url(r'^$', examinations.examination_list_view, name='examination_list_view'),

    url(r'^(?P<examination_id>\d+)/$', examination.user_examination_process_view, name='user_examination_answer_view'),
    url(r'^(?P<examination_id>\d+)/(?P<user_examination_question_log_id>\d+)/$', examination.user_examination_process_view, name='user_examination_answer_view'),

    url(r'^textquestion/(?P<user_examination_id>\d+)/(?P<text_question_id>\d+)$', examination.user_text_answer_create_view, name='user_text_answer_create_view'),

    url(r'^view/$', examination.user_examination_list_view, name='user_examination_list_view'),
    url(r'^view/(?P<user_examination_id>\d+)/$', examination.user_examination_detail_view, name='user_examination_detail_view'),

    url(r'^reports/top/$', reports.high_user_examination_view, name='high_user_examination_view'),
    url(r'^reports/average/$', reports.average_points_view, name='average_points_view'),
    url(r'^reports/process/$', reports.user_process_view, name='user_process_view'),

    url(r'^adm/examination/(?P<examination_id>\d+)/questions/(?P<question_id>\d+)/answer/(?P<answer_id>\d+)/delete/$', management_examinations.question_answer_delete_view, name='question_answer_delete_view'),
    url(r'^adm/examination/(?P<examination_id>\d+)/questions/(?P<question_id>\d+)/answer/(?P<answer_id>\d+)/$', management_examinations.question_answer_create_or_update_view, name='question_answer_update_view'),
    url(r'^adm/examination/(?P<examination_id>\d+)/questions/(?P<question_id>\d+)/answer/create/$', management_examinations.question_answer_create_or_update_view, name='question_answer_create_view'),
    url(r'^adm/examination/(?P<examination_id>\d+)/questions/(?P<question_id>\d+)/delete/$', management_examinations.examination_question_delete_view, name='examination_question_delete_view'),
    url(r'^adm/examination/(?P<examination_id>\d+)/questions/(?P<question_id>\d+)/$', management_examinations.examination_question_create_or_update_view, name='examination_question_update_view'),
    url(r'^adm/examination/(?P<examination_id>\d+)/questions/create/$', management_examinations.examination_question_create_or_update_view, name='examination_question_create_view'),
    url(r'^adm/examination/(?P<examination_id>\d+)/questions/$', management_examinations.examination_question_list_view, name='examination_question_list_view'),
    url(r'^adm/examination/(?P<examination_id>\d+)/$', management_examinations.examination_create_or_update_view, name='examination_update_view'),
    url(r'^adm/examination/create/$', management_examinations.examination_create_or_update_view, name='examination_create_view'),
    url(r'^adm/examination/$', management_examinations.examination_list_view, name='adm_examination_list_view'),

    url(r'^adm/examination/(?P<examination_id>\d+)/textquestions/(?P<question_id>\d+)/delete/$',
        management_examinations.examination_text_question_delete_view, name='examination_text_question_delete_view'),
    url(r'^adm/examination/(?P<examination_id>\d+)/textquestions/(?P<question_id>\d+)/$',
        management_examinations.examination_text_question_create_or_update_view, name='examination_text_question_update_view'),
    url(r'^adm/examination/(?P<examination_id>\d+)/textquestions/create/$',
        management_examinations.examination_text_question_create_or_update_view, name='examination_text_question_create_view'),
    url(r'^adm/examination/(?P<examination_id>\d+)/textquestions/$', management_examinations.examination_text_question_list_view,
        name='examination_text_question_list_view'),


    url(r'^adm/users/$', management_examination_time.user_list_view, name='adm_user_list_view'),
    url(r'^adm/users/(?P<user_id>\d+)/$', management_examination_time.user_time_update_view, name='adm_user_time_update_view'),
]
