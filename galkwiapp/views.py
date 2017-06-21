from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import (CreateView, DetailView, FormView, ListView,
                                  TemplateView, UpdateView)

from galkwiapp.models import Entry, Revision, Word
from galkwiapp.forms import (EntrySearchForm, SuggestionEditForm,
                             SuggestionRemoveForm, SuggestionReviewForm,
                             SuggestionCancelForm, TermsAgreeForm)


SUGGESTIONS_PER_PAGE = 25
SUGGESTIONS_PAGE_RANGE = 3
ENTRIES_PER_PAGE = 25


class HomeView(TemplateView):
    template_name = 'home.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/profile.html'


class EntryIndexView(ListView):
    paginate_by = ENTRIES_PER_PAGE
    template_name = 'galkwiapp/entry_index.html'

    def dispatch(self, request, *args, **kwargs):
        self.form = self.get_form()
        return super(EntryIndexView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Entry.objects.filter(latest__deleted=False)
        word = self.form.get_word()
        if word is not None:
            queryset = queryset.filter(latest__word__word__contains=word)

        return queryset.order_by('latest__word__word')

    def get_form(self):
        return EntrySearchForm(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = {}

        if 'word' in self.request.GET:
            kwargs['data'] = self.request.GET

        return kwargs

    def get_context_data(self, **kwargs):
        kwargs['form'] = self.form

        word = self.form.get_word()
        if word is not None:
            kwargs['word'] = word

        return super(EntryIndexView, self).get_context_data(**kwargs)


class EntryDetailView(DetailView):
    model = Entry
    pk_url_kwarg = 'entry_id'
    template_name = 'galkwiapp/entry_detail.html'

    def get_context_data(self, **kwargs):
        kwargs['revisions'] = self.object.revision_set.filter(status=Revision.STATUS_REVIEWING)
        kwargs['history'] = self.object.revision_set.filter(status__in=(Revision.STATUS_APPROVED, Revision.STATUS_REPLACED))
        return super(EntryDetailView, self).get_context_data(**kwargs)


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

        # check for duplicate records
        dups = Revision.objects.filter(status__in=(
            Revision.STATUS_APPROVED,
            Revision.STATUS_REVIEWING,
        ), word__word=word.word, word__pos=word.pos)

        if dups.exists():
            rev = dups.get()
            return self.render_to_response(
                self.get_context_data(form=SuggestionEditForm(),
                                      terms_form=TermsAgreeForm(),
                                      duplicated_rev=rev)
            )

        try:
            with transaction.atomic():
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
        except IntegrityError:
            return HttpResponseBadRequest(self.request)

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

        # check for duplicate recordds
        dups = Revision.objects.filter(status__in=(
            Revision.STATUS_APPROVED,
            Revision.STATUS_REVIEWING
        ), word__word=word.word, word__pos=word.pos).exclude(entry=entry)

        if dups.exists():
            rev = dups.get()
            return self.render_to_response(
                self.get_context_data(form=SuggestionEditForm(),
                                      terms_form=TermsAgreeForm(),
                                      duplicated_rev=rev)
            )

        try:
            with transaction.atomic():
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
        except IntegrityError:
            return HttpResponseBadRequest(self.request)

        return HttpResponseRedirect(rev.get_absolute_url())


class SuggestionDetailView(DetailView):
    model = Revision
    pk_url_kwarg = 'rev_id'
    template_name = 'galkwiapp/suggestion_detail.html'

    def get_context_data(self, **kwargs):
        kwargs['rev'] = self.object

        if self.object.status == Revision.STATUS_REVIEWING:
            if self.request.user.has_perm('galkwiapp.can_review'):
                kwargs['review_form'] = SuggestionReviewForm()
            if self.request.user == self.object.user:
                kwargs['cancel_form'] = SuggestionCancelForm()

        return super(SuggestionDetailView, self).get_context_data(**kwargs)


class SuggestionReviewOneView(PermissionRequiredMixin, TemplateView):
    permission_required = 'galkwiapp.can_review'
    template_name = 'galkwiapp/suggestion_review_end.html'

    def get(self, request, *args, **kwargs):
        revs = Revision.objects.filter(status=Revision.STATUS_REVIEWING).order_by('timestamp')
        for rev in revs:
            return HttpResponseRedirect(rev.get_absolute_url())
        return super(SuggestionReviewOneView, self).get(request, *args, **kwargs)


class SuggestionReviewView(PermissionRequiredMixin, FormView):
    permission_required = 'galkwiapp.can_suggest'
    form_class = SuggestionReviewForm
    http_method_names = [m for m in FormView.http_method_names if m != 'get']

    def post(self, request, *args, **kwargs):
        self.rev = get_object_or_404(Revision, pk=self.kwargs['rev_id'])

        if self.rev.status != Revision.STATUS_REVIEWING:
            return HttpResponseBadRequest(request)

        return super(SuggestionReviewView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        review = form.cleaned_data['review']
        comment = form.cleaned_data['comment']

        if review == 'APPROVE':
            self.rev.approve(self.request.user, comment)
            # reject other suggestions
            others = Revision.objects.filter(entry=self.rev.entry,
                                             status=Revision.STATUS_REVIEWING)
            for o in others:
                o.reject(self.request.user,
                         'rejected by other suggestion %s' % self.rev.get_absolute_url())
        elif review == 'REJECT':
            self.rev.reject(self.request.user, comment)

        if '_reviewone' in self.request.POST:
            return HttpResponseRedirect(reverse('suggestion_review_one'))
        else:
            return HttpResponseRedirect(self.rev.get_absolute_url())


class SuggestionCancelView(PermissionRequiredMixin, FormView):
    permission_required = 'galkwiapp.can_suggest'
    form_class = SuggestionCancelForm
    http_method_names = [m for m in FormView.http_method_names if m != 'get']

    def post(self, request, *args, **kwargs):
        self.rev = get_object_or_404(Revision, pk=self.kwargs['rev_id'])

        if self.rev.user != request.user:
            return HttpResponseBadRequest(request)
        if self.rev.status != Revision.STATUS_REVIEWING:
            return HttpResponseBadRequest(request)

        return super(SuggestionCancelView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.rev.cancel()
        return HttpResponseRedirect(self.rev.get_absolute_url())


class SuggestionRecentChangesView(ListView):
    template_name = 'galkwiapp/suggestion_recentchanges.html'
    queryset = Revision.objects.filter(status__in=(
        Revision.STATUS_APPROVED, Revision.STATUS_REJECTED,
        Revision.STATUS_REPLACED
    )).order_by('-timestamp')
    paginate_by = SUGGESTIONS_PER_PAGE


class StatView(TemplateView):
    template_name = 'galkwiapp/stat.html'

    def get_context_data(self, **kwargs):
        all_words = Entry.objects.filter(latest__deleted=False)

        kwargs['words_total'] = all_words.count()
        kwargs['words_by_license'] = licenses = []
        q = all_words.values('latest__license').annotate(Count('id'));
        for d in q:
            licenses.append((d['latest__license'], d['id__count']))
        return super(StatView, self).get_context_data(**kwargs)
