from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User, Permission
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone
from django.views.generic import CreateView, FormView, ListView, TemplateView, UpdateView


from galkwiapp.models import *
from galkwiapp.forms import *


class HomeView(TemplateView):
    template_name = 'home.html'


class ProfileView(TemplateView):
    template_name = 'registration/profile.html'

ENTRIES_PER_PAGE = 25


def entry_index(request):
    data = {}
    if request.method == 'GET':
        form = EntrySearchForm(request.GET)
        if form.is_valid():
            word = form.cleaned_data['word']
            data['word'] = word
            query = Entry.objects.filter(latest__deleted=False).filter(latest__word__word__contains=word)
        else:
            query = Entry.objects.filter(latest__deleted=False)
        query.order_by('word')
        paginator = Paginator(query, ENTRIES_PER_PAGE)
        page = int(request.GET.get('page', '1'))
        try:
            data['page'] = paginator.page(page)
        except InvalidPage:
            raise Http404
        data['form'] = form
    else:
        data['form'] = EntrySearchForm()
    return render(request, 'galkwiapp/entry_index.html', data)


def entry_detail(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    data = {}
    data['entry'] = entry
    data['revisions'] = Revision.objects.filter(entry=entry).filter(status=Revision.STATUS_REVIEWING)
    data['history'] = Revision.objects.filter(entry=entry).filter(Q(status=Revision.STATUS_APPROVED) | Q(status=Revision.STATUS_REPLACED))
    return render(request, 'galkwiapp/entry_detail.html', data)

SUGGESTIONS_PER_PAGE = 25
SUGGESTIONS_PAGE_RANGE = 3


class SuggestionIndexView(ListView):
    template_name = 'galkwiapp/suggestion_index.html'
    queryset = Revision.objects.filter(status=Revision.STATUS_REVIEWING).order_by('-timestamp')
    paginate_by = SUGGESTIONS_PER_PAGE


class TermsFormMixin(object):
    def get_context_data(self, **kwargs):
        if 'terms_form' not in kwargs:
            kwargs['terms_form'] = self.get_terms_form()
        return super(TermsFormMixin, self).get_context_data(**kwargs)

    def get_terms_form(self):
        kwargs = {}
        if self.request.method in ('POST', 'PUT'):
            kwargs['data'] = self.request.POST

        return TermsAgreeForm(**kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        terms_form = self.get_terms_form()

        if form.is_valid() and terms_form.is_valid():
            return self.form_valid(form, terms_form)
        else:
            return self.form_invalid(form, terms_form)

    def form_invalid(self, form, terms_form):
        return self.render_to_response(
            self.get_context_data(form=form, terms_form=terms_form)
        )


class SuggestionAddView(PermissionRequiredMixin, TermsFormMixin, CreateView):
    permission_required = 'galkwiapp.can_suggest'
    model = Word
    form_class = SuggestionEditForm
    template_name = 'galkwiapp/suggestion_add.html'

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(SuggestionAddView, self).post(request, *args, **kwargs)

    def form_valid(self, form, terms_form):
        word = form.save(commit=False)
        # check duplicate
        existing = Revision.objects.filter(status__in=(
            Revision.STATUS_APPROVED,
            Revision.STATUS_REVIEWING,
        )).filter(word__word=word.word, word__pos=word.pos)
        if existing.count() > 0:
            return HttpResponseBadRequest(self.request)
        word.save()
        rev = Revision()
        rev.word = word
        rev.deleted = False
        rev.action = 'ADD'
        rev.timestamp = timezone.now()
        rev.user = self.request.user
        rev.status = Revision.STATUS_REVIEWING
        rev.comment = form.cleaned_data['comment']
        rev.save()

        if '_addanother' in self.request.POST:
            return self.render_to_response(
                self.get_context_data(form=SuggestionEditForm(),
                                      terms_form=TermsAgreeForm(),
                                      submitted_rev=rev)
            )
        else:
            return HttpResponseRedirect(rev.get_absolute_url())


class SuggestionRemoveView(PermissionRequiredMixin, TermsFormMixin, FormView):
    permission_required = 'galkwiapp.can_suggest'
    form_class = SuggestionRemoveForm
    template_name = 'galkwiapp/suggestion_remove.html'

    def dispatch(self, request, *args, **kwargs):
        entry = self.get_entry()
        if entry.latest.deleted:
            return HttpResponseBadRequest(request)

        return super(SuggestionRemoveView, self).dispatch(request, *args,
                                                          **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['entry'] = self.get_entry()
        return super(SuggestionRemoveView, self).get_context_data(**kwargs)

    def get_entry(self):
        return get_object_or_404(Entry, pk=self.kwargs['entry_id'])

    def form_valid(self, form, terms_form):
        entry = self.get_entry()
        rev = Revision()
        rev.entry = entry
        rev.deleted = True
        rev.status = Revision.STATUS_REVIEWING
        rev.timestamp = timezone.now()
        rev.parent = entry.latest
        rev.user = self.request.user
        rev.comment = form.cleaned_data['comment']
        rev.save()
        return HttpResponseRedirect(rev.get_absolute_url())


class SuggestionUpdateView(PermissionRequiredMixin, TermsFormMixin, UpdateView):
    permission_required = 'galkwiapp.can_suggest'
    form_class = SuggestionEditForm
    template_name = 'galkwiapp/suggestion_update.html'

    def get_context_data(self, **kwargs):
        kwargs['entry'] = self.get_entry()
        return super(SuggestionUpdateView, self).get_context_data(**kwargs)

    def get_entry(self):
        return get_object_or_404(Entry, pk=self.kwargs['entry_id'])

    def get_object(self):
        return self.get_entry().latest.word

    def form_valid(self, form, terms_form):
        entry = self.get_entry()
        word = form.save(commit=False)
        # check duplicate
        existing = Revision.objects.filter(
                Q(status=Revision.STATUS_APPROVED) | Q(status=Revision.STATUS_REVIEWING)
        ).filter(word__word=word.word, word__pos=word.pos
        ).exclude(entry=entry)
        if existing.count() > 0:
            print('ERROR: duplicate revisions')
            return HttpResponseBadRequest(self.request)
        word.save()
        rev = Revision()
        rev.entry = entry
        rev.word = word
        rev.deleted = False
        rev.timestamp = timezone.now()
        rev.parent = entry.latest
        rev.user = self.request.user
        rev.status = Revision.STATUS_REVIEWING
        rev.comment = form.cleaned_data['comment']
        rev.save()
        return HttpResponseRedirect(rev.get_absolute_url())


def suggestion_detail(request, rev_id):
    rev = get_object_or_404(Revision, pk=rev_id)
    data = {}
    data['rev'] = rev
    if rev.status == Revision.STATUS_REVIEWING:
        if request.user.has_perm('galkwiapp.can_review'):
            data['review_form'] = SuggestionReviewForm()
        if request.user == rev.user:
            data['cancel_form'] = SuggestionCancelForm()
    return render(request, 'galkwiapp/suggestion_detail.html', data)


@permission_required('galkwiapp.can_review')
def suggestion_review_one(request):
    revs = Revision.objects.filter(status=Revision.STATUS_REVIEWING).order_by('timestamp')
    for rev in revs:
        return HttpResponseRedirect(rev.get_absolute_url())
    return render(request, 'galkwiapp/suggestion_review_end.html')


@permission_required('galkwiapp.can_review')
def suggestion_review(request, rev_id):
    if request.method == 'POST':
        rev = get_object_or_404(Revision, pk=rev_id)
        if rev.status != Revision.STATUS_REVIEWING:
            return HttpResponseBadRequest(request)
        form = SuggestionReviewForm(request.POST)
        if form.is_valid():
            review = form.cleaned_data['review']
            comment = form.cleaned_data['comment']
            if review == 'APPROVE':
                rev.approve(request.user, comment)
                # reject other suggestions
                others = Revision.objects.filter(entry=rev.entry, status=Revision.STATUS_REVIEWING)
                for o in others:
                    o.reject(request.user, 'rejected by other suggestion %s' % rev.get_absolute_url())
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
        if rev.status != Revision.STATUS_REVIEWING:
            return HttpResponseBadRequest(request)
        form = SuggestionCancelForm(request.POST)
        if form.is_valid():
            rev.cancel()
            return HttpResponseRedirect(rev.get_absolute_url())
        else:
            return HttpResponseBadRequest(request)
    else:
        return HttpResponseBadRequest(request)


class SuggestionRecentChangesView(ListView):
    template_name = 'galkwiapp/suggestion_recentchanges.html'
    queryset = Revision.objects.filter(status__in=(
        Revision.STATUS_APPROVED, Revision.STATUS_REJECTED,
        Revision.STATUS_REPLACED
    )).order_by('-timestamp')
    paginate_by = SUGGESTIONS_PER_PAGE


class StatView(TemplateView):
    template_name = 'galkwiapp/stat.html'
