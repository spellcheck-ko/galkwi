# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from ragendja.urlsauto import urlpatterns
from ragendja.auth.urls import urlpatterns as auth_patterns
#from galkwi.forms import UserRegistrationForm
from django.contrib import admin

admin.autodiscover()

#handler500 = 'ragendja.views.server_error'

import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

urlpatterns = auth_patterns + patterns('',
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
    url(r'^proposal/(?P<proposal_id>\d+)/cancel/$',
        'galkwi.views.proposal_cancel', name='proposal_cancel'),

    url(r'^proposal/recentchanges/$', 'galkwi.views.proposal_recentchanges',
        name='proposal_recentchanges'),

    url(r'^account/profile/$', 'galkwi.views.profile',
        name='profile'),
    url(r'^account/register/$', 'galkwi.views.register',
        name='register'),

    (r'^tasks/count/$', 'galkwi.tasks.count'),

    # # static files
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': ROOT_DIR + '/static/css'}, name='css'),
    url(r'^img/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': ROOT_DIR + '/static/img'}, name='img'),
    url(r'^js/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': ROOT_DIR + '/static/js'}, name='js'),
    url(r'^favicon\.ico$', 'django.views.static.serve',
        {'document_root': ROOT_DIR + '/static', 'path': 'favicon.ico'},
        name='favicon'),
    (r'^(?P<path>robots\.txt)$', 'django.views.static.serve',
     {'document_root': ROOT_DIR + '/static'}),

    # Example:
    # (r'^galkwi/', include('galkwi.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
) + urlpatterns
