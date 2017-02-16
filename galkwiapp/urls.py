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
    url(r'^$', views.HomeView.as_view(), name='home'),

    url(r'^entry/$', views.entry_index, name='entry_index'),
    url(r'^entry/(?P<entry_id>\d+)/$', views.EntryDetailView.as_view(),
        name='entry'),

    url(r'^suggestion/$', views.SuggestionIndexView.as_view(),
        name='suggestion_index'),
    url(r'^suggestion/(?P<rev_id>\d+)/$', views.SuggestionDetailView.as_view(),
        name='suggestion'),
    url(r'^suggestion/add/$', views.SuggestionAddView.as_view(),
        name='suggestion_add'),
    url(r'^suggestion/remove/(?P<entry_id>\d+)/$',
        views.SuggestionRemoveView.as_view(), name='suggestion_remove'),
    url(r'^suggestion/update/(?P<entry_id>\d+)/$',
        views.SuggestionUpdateView.as_view(), name='suggestion_update'),
    url(r'^suggestion/review/(?P<rev_id>\d+)/$', views.suggestion_review,
        name='suggestion_review'),
    url(r'^suggestion/reviewone/$', views.SuggestionReviewOneView.as_view(),
        name='suggestion_review_one'),
    url(r'^suggestion/cancel/(?P<rev_id>\d+)/$',
        views.SuggestionCancelView.as_view(), name='suggestion_cancel'),
    url(r'^suggestion/recentchanges/$',
        views.SuggestionRecentChangesView.as_view(),
        name='suggestion_recentchanges'),

    url(r'^stat/$', views.StatView.as_view(), name='stat'),

    url(r'^accounts/profile/$', views.ProfileView.as_view(), name='profile'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
