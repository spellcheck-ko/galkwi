from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone
from galkwiapp.models import *
from galkwiapp.forms import *


# Create your views here.
def home(request):
        return render(request, 'home.html', {})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            agree = form.cleaned_data['agree']
            if agree:
                ct = ContentType.objects.get_for_model(Revision)
                p = Permission.objects.get(content_type=ct, codename='can_suggest')
                request.user.user_permissions.add(p)
                request.user.save()
                return render(request, 'registration/registration_complete.html')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/registration_form.html', {'form': form})


def profile(request):
    return render(request, 'registration/profile.html')

ENTRIES_PER_PAGE = 25


def entry_index(request):
    data = {}
    if request.method == 'GET':
        form = EntrySearchForm(request.GET)
        if form.is_valid():
            word = form.cleaned_data['word']
            data['word'] = word
            query = Entry.objects.filter(latest__deleted=False).filter(latest__word__word__contains=word)
            query.order_by('word')
            paginator = Paginator(query, ENTRIES_PER_PAGE)
            page = int(request.GET.get('page', '1'))
            try:
                data['page'] = paginator.page(page)
            except InvalidPage:
                raise Http404
            data['form'] = form
        else:
            query = Entry.objects.filter(latest__deleted=False)
            query.order_by('word')
            paginator = Paginator(query, ENTRIES_PER_PAGE)
            page = int(request.GET.get('page', '1'))
            try:
                data['page'] = paginator.page(page)
            except InvalidPage:
                raise Http404

            data['form'] = EntrySearchForm()
    else:
        data['form'] = EntrySearchForm()
    return render(request, 'galkwiapp/entry_index.html', data)


def entry_detail(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    data = {}
    data['entry'] = entry
    data['revisions'] = Revision.objects.filter(entry=entry).filter(Q(status=Revision.STATUS_APPROVED) | Q(status=Revision.STATUS_REPLACED))
    return render(request, 'galkwiapp/entry_detail.html', data)

SUGGESTIONS_PER_PAGE = 25
SUGGESTIONS_PAGE_RANGE = 3


def suggestion_index(request):
    query = Revision.objects.filter(status=Revision.STATUS_VOTING).order_by('-timestamp')
    paginator = Paginator(query, SUGGESTIONS_PER_PAGE)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    data = {}
    try:
        data['page'] = paginator.page(page)
    except InvalidPage:
        raise Http404
    return render(request, 'galkwiapp/suggestion_index.html', data)


@permission_required('galkwiapp.can_suggest')
def suggestion_add(request):
    data = {}
    if request.method == 'POST':
        form = SuggestionEditForm(request.POST)
        if form.is_valid():
            word = form.save(commit=False)
            # TODO: check duplicate
            word.save()
            rev = Revision()
            rev.word = word
            rev.deleted = False
            rev.action = 'ADD'
            rev.timestamp = timezone.now()
            rev.user = request.user
            rev.status = Revision.STATUS_VOTING
            rev.save()
            if '_addanother' in request.POST:
                data['submitted_rev'] = rev
                data['form'] = SuggestionEditForm()
            else:
                return HttpResponseRedirect(rev.get_absolute_url())
    else:
        data['form'] = SuggestionEditForm()
    return render(request, 'galkwiapp/suggestion_add.html', data)


@permission_required('galkwiapp.can_suggest')
def suggestion_remove(request, entry_id):
    data = {}
    entry = get_object_or_404(Entry, pk=entry_id)

    # ensure that this entry is valid
    if entry.latest.deleted:
        return HttpResponseBadRequest(request)
    # ensure there is no other running suggestion on this entry
    existing = Revision.objects.filter(entry=entry, status=Revision.STATUS_VOTING)
    if existing.count() > 0:
        return HttpResponseBadRequest(request)
    if request.method == 'POST':
        data['form'] = form = SuggestionRemoveForm(request.POST)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.entry = entry
            rev.deleted = True
            rev.status = Revision.STATUS_VOTING
            rev.timestamp = timezone.now()
            rev.parent = entry.latest
            rev.user = request.user
            rev.save()
            return HttpResponseRedirect(rev.get_absolute_url())
    else:
        data['form'] = SuggestionRemoveForm()
    data['entry'] = entry
    return render(request, 'galkwiapp/suggestion_remove.html', data)


@permission_required('galkwiapp.can_suggest')
def suggestion_update(request, entry_id):
    data = {}
    entry = get_object_or_404(Entry, pk=entry_id)

    # ensure there is no other suggestion on this entry
    existing = Revision.objects.filter(entry=entry, status=Revision.STATUS_VOTING)
    if existing.count() > 0:
        return HttpResponseBadRequest(request)
    if request.method == 'POST':
        data['form'] = form = SuggestionEditForm(request.POST)
        if form.is_valid():
            word = form.save(commit=False)
            word.save()
            rev = Revision()
            rev.entry = entry
            rev.word = word
            rev.deleted = False
            rev.status = Revision.STATUS_VOTING
            rev.timestamp = timezone.now()
            rev.parent = entry.latest
            rev.user = request.user
            rev.save()
            return HttpResponseRedirect(rev.get_absolute_url())
    else:
        data['form'] = SuggestionEditForm(instance=entry.latest.word)
    data['entry'] = entry
    return render(request, 'galkwiapp/suggestion_update.html', data)


def suggestion_detail(request, rev_id):
    rev = get_object_or_404(Revision, pk=rev_id)
    data = {}
    data['rev'] = rev
    if rev.status == Revision.STATUS_VOTING:
        if request.user.has_perm('galkwiapp.can_review'):
            data['review_form'] = SuggestionReviewForm()
        if request.user == rev.user:
            data['cancel_form'] = SuggestionCancelForm()
    return render(request, 'galkwiapp/suggestion_detail.html', data)


@permission_required('galkwiapp.can_review')
def suggestion_review_one(request):
    revs = Revision.objects.filter(status=Revision.STATUS_VOTING).order_by('timestamp')
    for rev in revs:
        return HttpResponseRedirect(rev.get_absolute_url())
    return render(request, 'galkwiapp/suggestion_review_end.html')


@permission_required('galkwiapp.can_review')
def suggestion_review(request, rev_id):
    if request.method == 'POST':
        rev = get_object_or_404(Revision, pk=rev_id)
        if rev.status != Revision.STATUS_VOTING:
            return HttpResponseBadRequest(request)
        # retrieve previous vote if any
        form = SuggestionReviewForm(request.POST)
        if form.is_valid():
            review = form.cleaned_data['review']
            comment = form.cleaned_data['comment']
            if review == 'APPROVE':
                rev.approve(request.user, comment)
            elif review == 'REJECT':
                rev.reject(request.user, comment)
            if '_reviewone' in request.POST:
                return HttpResponseRedirect(reverse('suggestion_review_one'))
            else:
                return HttpResponseRedirect(rev.get_absolute_url())
        else:
            return HttpResponseBadRequest(request)
    else:
        return HttpResponseBadRequest(request)


@permission_required('galkwiapp.can_suggest')
def suggestion_cancel(request, rev_id):
    if request.method == 'POST':
        rev = get_object_or_404(Revision, pk=rev_id)
        # check if it's my suggestion
        if rev.user != request.user:
            return HttpResponseBadRequest(request)
        if rev.status != Revision.STATUS_VOTING:
            return HttpResponseBadRequest(request)
        form = SuggestionCancelForm(request.POST)
        if form.is_valid():
            rev.cancel()
            return HttpResponseRedirect(rev.get_absolute_url())
        else:
            return HttpResponseBadRequest(request)
    else:
        return HttpResponseBadRequest(request)


def suggestion_recentchanges(request):
    query = Revision.objects.order_by('-timestamp')
    paginator = Paginator(query, SUGGESTIONS_PER_PAGE)
    page = int(request.GET.get('page', '1'))
    data = {}
    try:
        data['page'] = paginator.page(page)
    except InvalidPage:
        raise Http404
    return render(request, 'galkwiapp/suggestion_recentchanges.html', data)


def stat(request):
    return render(request, 'galkwiapp/stat.html')
