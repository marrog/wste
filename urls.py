from django.conf.urls.defaults import *
from django.conf import settings
#from django.views.generic import list_detail
from archiwum.models import Lesson
from django.contrib import admin
admin.autodiscover()

#probably unneeded
#lesson_info = {
    #              'queryset': Lesson.objects.all(), 
    #             'template_name': 'archiwum/lessons.html', 
    #            'template_object_name': 'lessons', 
    #           }

urlpatterns = patterns('wste.archiwum.views',

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),
    (r'^archiwum/subjects/add/$', 'add_subject'),
    (r'^archiwum/news/(?P<news_id>\d+)/$', 'news_show'),
    (r'^archiwum/news/(?P<news_id>\d+)/edit/$', 'edit_news'),
    (r'^archiwum/news/my/$', 'my_newses'),
    (r'^archiwum/news/add/$', 'add_news'),
    (r'^archiwum/news/$', 'newses'),
    (r'^archiwum/document/add/$', 'add_document'),
    (r'^users/login/$', 'log_in'),
    (r'^users/logout/$', 'log_out'),
    (r'^users/register/$', 'register_user'),
    (r'^users/groups/$', 'list_groups'),
    (r'^users/list/students/groups/(?P<slug>[\w\-_]+)/?$', 'students_by_group'),
    (r'^users/list/students/semestr/(?P<slug>[\w\-_]+)/?$', 'students_by_semester'),
    (r'^users/list/students/(?P<student_id>\d+)/$', 'student_show'),
    (r'^users/list/students/$', 'list_users'),
    (r'^users/list/instructors/(?P<instructor_id>\d+)/$', 'instructor_show'),
    (r'^users/list/instructors/$', 'list_instructors'),
    (r'^documents/graphs/$', 'graphs'),
    (r'^documents/cat/(?P<slug>[\w\-_]+)/?$', 'documents_by_category'),
    (r'^documents/(?P<document_id>\d+)/$', 'document_show'),
    #(r'^documents/download/(?P<document_id>\d+)/$', 'document_download'), usunieta funkcja widoku
    (r'^documents/search/', 'search_documents'),
    (r'^documents/$', 'documents'),
    (r'^lessons/(?P<lesson_id>\d+)/$', 'lesson_show'),
    # (r'^lessons/$',  list_detail.object_list,  lesson_info), 
    (r'^lessons/$', 'lessons'),
    (r'^info/$', 'info'),
    (r'^info/sendmail/$', 'send_email'),
    (r'^$',  'main_index'), 
)

if settings.DEBUG:
    urlpatterns += patterns('',
                            (r'^statics/(?P<path>.*)$', 'django.views.static.serve',  
                             {'document_root':     settings.MEDIA_ROOT}),
)
