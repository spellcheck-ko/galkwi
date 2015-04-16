from django.contrib.auth.urls import urlpatterns as auth_patterns
from django.conf.urls import include, url
from django.contrib import admin

import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

urlpatterns = auth_patterns + [
    url(r'^$', 'galkwi.views.index', name='home'),

    url(r'^entry/$', 'galkwi.views.entry_index', name='entry_index'),
    url(r'^entry/(?P<entry_id>\d+)/$', 'galkwi.views.entry_detail',
        name='entry'),

    url(r'^proposal/$', 'galkwi.views.proposal_index',
        name='proposal_index'),
    url(r'^proposal/(?P<proposal_id>\d+)/$',
        'galkwi.views.proposal_detail', name='proposal'),
    url(r'^proposal/add/$', 'galkwi.views.proposal_add',
        name='proposal_add'),
    url(r'^proposal/remove/(?P<entry_id>\d+)/$',
        'galkwi.views.proposal_remove', name='proposal_remove'),
    url(r'^proposal/update/(?P<entry_id>\d+)/$',
        'galkwi.views.proposal_update', name='proposal_update'),
    url(r'^proposal/(?P<proposal_id>\d+)/vote/$',
        'galkwi.views.proposal_vote', name='proposal_vote'),
    url(r'^proposal/voteone/$',
        'galkwi.views.proposal_vote_one', name='proposal_vote_one'),
    url(r'^proposal/(?P<proposal_id>\d+)/cancel/$',
        'galkwi.views.proposal_cancel', name='proposal_cancel'),

    url(r'^proposal/recentchanges/$', 'galkwi.views.proposal_recentchanges',
        name='proposal_recentchanges'),

    url(r'^account/profile/$', 'galkwi.views.profile',
        name='profile'),
    url(r'^account/register/$', 'galkwi.views.register',
        name='register'),

    url(r'^tasks/count/$', 'galkwi.tasks.count'),
    url(r'^tasks/export/$', 'galkwi.tasks.export'),

    # # static files
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': ROOT_DIR + '/static/css'}, name='css'),
    url(r'^img/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': ROOT_DIR + '/static/img'}, name='img'),
    url(r'^js/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': ROOT_DIR + '/static/js'}, name='js'),
    url(r'^favicon\.ico$', 'django.views.static.serve',
        {'document_root': os.path.join(ROOT_DIR, '/static'),
         'path': 'favicon.ico'},
        name='favicon'),
    url(r'^(?P<path>robots\.txt)$', 'django.views.static.serve',
        {'document_root': ROOT_DIR + '/static'}),
    
    url(r'^admin/', include(admin.site.urls)),
]
