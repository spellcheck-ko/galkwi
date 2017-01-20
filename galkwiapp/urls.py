"""galkwiapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from galkwiapp import views

urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^entry/$', views.entry_index, name='entry_index'),
    url(r'^entry/(?P<entry_id>\d+)/$', views.entry_detail,
        name='entry'),

    url(r'^proposal/$', views.proposal_index, name='proposal_index'),
    url(r'^proposal/(?P<proposal_id>\d+)/$', views.proposal_detail,
        name='proposal'),
    url(r'^proposal/add/$', views.proposal_add, name='proposal_add'),
    url(r'^proposal/remove/(?P<entry_id>\d+)/$', views.proposal_remove,
        name='proposal_remove'),
    url(r'^proposal/update/(?P<entry_id>\d+)/$', views.proposal_update,
        name='proposal_update'),
    url(r'^proposal/(?P<proposal_id>\d+)/vote/$', views.proposal_vote,
        name='proposal_vote'),
    url(r'^proposal/voteone/$', views.proposal_vote_one,
        name='proposal_vote_one'),
    url(r'^proposal/(?P<proposal_id>\d+)/cancel/$', views.proposal_cancel,
        name='proposal_cancel'),

    url(r'^proposal/recentchanges/$', views.proposal_recentchanges,
        name='proposal_recentchanges'),

    url(r'^stat/$', views.stat, name='stat'),

    url(r'^accounts/profile/$', views.profile, name='profile'),
    url(r'^account/register/$', views.register, name='register'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
