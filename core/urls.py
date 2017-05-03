from django.conf.urls import patterns, url

from core.views import category, examinations, examination
from core.views.management import management_examinations

urlpatterns = [
    url(r'^categories/$', category.category_list_view, name='category_list_view'),
    url(r'^categories/(?P<category_id>\d+)/$', examinations.examination_list_view, name='examination_list_view'),

    url(r'^(?P<examination_id>\d+)/$', examination.user_examination_process_view, name='user_examination_answer_view'),
    url(r'^(?P<examination_id>\d+)/(?P<user_examination_question_log_id>\d+)/$', examination.user_examination_process_view, name='user_examination_answer_view'),
    url(r'^view/$', examination.user_examination_list_view, name='user_examination_list_view'),
    url(r'^view/(?P<user_examination_id>\d+)/$', examination.user_examination_detail_view, name='user_examination_detail_view'),

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

]
