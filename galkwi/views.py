# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
#from ragendja.dbutils import get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage
from django.contrib.auth.decorators import permission_required
from datetime import datetime
from galkwi.models import *
from galkwi.forms import *

def index(request):
    context = RequestContext(request)
    return render_to_response('index.html', context)

def register(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            agree = form.cleaned_data['agree']
            if agree:
                request.user.user_permissions = ['galkwi.can_propose']
                request.user.save()
                return render_to_response('registration/registration_complete.html', context)
    else:
        form = UserRegistrationForm()
    context['form'] = form
    return render_to_response('registration/registration_form.html', context)

def profile(request):
    context = RequestContext(request)
    return render_to_response('registration/profile.html', context)

ENTRIES_PER_PAGE = 25

def entry_index(request):
    context = RequestContext(request)
    if request.method == 'GET':
        form = EntrySearchForm(request.GET)
        if form.is_valid():
            word = form.cleaned_data['word']
            context['word'] = word
            query = Entry.all().filter('valid =', True)
            query.filter('word_substrings =', word)
            query.order('word')
            paginator = Paginator(query, ENTRIES_PER_PAGE)
            page = int(request.GET.get('page', '1'))
            try:
                context['page'] = paginator.page(page)
            except InvalidPage:
                raise Http404
        else:
            form = EntrySearchForm()
    else:
        form = EntrySearchForm()
    context['form'] = form
    return render_to_response('entry_index.html', context)

PROPOSALS_PER_PAGE = 25
PROPOSALS_PAGE_RANGE = 3

def proposal_index(request):
    context = RequestContext(request)
    query = Proposal.all()
    query.filter('status =', 'VOTING')
    paginator = Paginator(query, PROPOSALS_PER_PAGE)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        context['page'] = paginator.page(page)
    except InvalidPage:
        raise Http404
    return render_to_response('proposal_index.html', context)

def proposal_add(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = ProposalEditAddForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.action = 'ADD'
            instance.date = datetime.now()
            instance.editor = request.user
            instance.status = 'VOTING'
            instance.rebuild_substrings()
            instance.save()
            return HttpResponseRedirect(instance.get_absolute_url())
    else:
        form = ProposalEditAddForm()
    context['form'] = form
    return render_to_response('proposal_add.html', context)
proposal_add = permission_required('galkwi.can_propose')(proposal_add)

def proposal_remove(request, entry_id):
    context = RequestContext(request)
    entry = Entry.get_by_id(int(entry_id))
    #entry = get_object_or_404(Entry, pk=entry_id)
    # ensure that this entry is valid
    if not entry.valid:
        return HttpResponseBadRequest(request)
    # ensure there is no other running proposal on this entry
    existing = Proposal.all().filter('old_entry=', 'entry').filter('status=', 'VOTING')
    if existing.count() > 0:
        return HttpResponseBadRequest(request)
    if request.method == 'POST':
        form = ProposalEditRemoveForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.action = 'REMOVE'
            instance.old_entry = entry
            instance.date = datetime.now()
            instance.editor = request.user
            instance.status = 'VOTING'
            instance.save()
            return HttpResponseRedirect(instance.get_absolute_url())
    else:
        form = ProposalEditRemoveForm()
    context['entry'] = entry
    context['form'] = form
    return render_to_response('proposal_remove.html', context)
proposal_remove = permission_required('galkwi.can_propose')(proposal_remove)

def proposal_update(request, entry_id):
    context = RequestContext(request)
    entry = Entry.get_by_id(int(entry_id))
    #entry = get_object_or_404(Entry, pk=entry_id)
    # ensure that this entry is valid
    if not entry.valid:
        return HttpResponseBadRequest(request)
    # ensure there is no other proposal on this entry
    existing = Proposal.all().filter('old_entry =', entry).filter('status =', 'VOTING')
    if existing:
        return HttpResponseBadRequest(request)
    if request.method == 'POST':
        form = ProposalEditUpdateForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.action = 'UPDATE'
            instance.old_entry = entry
            instance.date = datetime.now()
            instance.editor = request.user
            instance.status = 'VOTING'
            instance.rebuild_substrings()
            instance.save()
            return HttpResponseRedirect(instance.get_absolute_url())
    else:
        proposal = Proposal()
        proposal.word = entry.word
        proposal.pos = entry.pos
        proposal.stem = entry.stem
        proposal.props = entry.props
        proposal.etym = entry.etym
        proposal.orig = entry.orig
        proposal.comment = entry.comment
        form = ProposalEditUpdateForm(instance=proposal)
    context['entry'] = entry
    context['form'] = form
    return render_to_response('proposal_update.html', context)
proposal_update = permission_required('galkwi.can_propose')(proposal_update)

def proposal_detail(request, proposal_id):
    context = RequestContext(request)
    proposal = Proposal.get_by_id(int(proposal_id))
    #proposal = get_object_or_404(Proposal, pk=proposal_id)
    context['proposal'] = proposal
    votes = Vote.all().filter('proposal =', proposal)
    context['votes'] = votes.fetch(100)
    votes = Vote.all().filter('proposal =', proposal).filter('vote =', 'YES')
    context['votes_yes_count'] = votes.count()
    votes = Vote.all().filter('proposal =', proposal).filter('vote =', 'NO')
    context['votes_no_count'] = votes.count()
    # vote form if possible
    if proposal.status == 'VOTING' and request.user.has_perm('galkwi.can_vote'):
        # retrieve previous vote if any
        vote = Vote.all().filter('proposal =', proposal).filter('reviewer =', request.user).get()
        context['myvote'] = vote
        if vote:
            form = ProposalVoteForm(instance=vote)
        else:
            form = ProposalVoteForm()
        context['vote_form'] = form
        context['cancel_form'] = ProposalCancelForm()
    return render_to_response('proposal_detail.html', context)

def proposal_vote(request, proposal_id):
    if request.method == 'POST':
        context = RequestContext(request)
        #proposal = get_object_or_404(Proposal, pk=proposal_id)
        proposal = Proposal.get_by_id(int(proposal_id))
        if proposal.status != 'VOTING':
            return HttpResponseBadRequest(request)
        # retrieve previous vote if any
        form = ProposalVoteForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)

            # Update the previous vote
            query = Vote.all().filter('proposal =', proposal).filter('reviewer =', request.user)
            prev = query.get()
            if prev:
                prev.vote = instance.vote
                prev.reason = instance.reason
                prev.date = datetime.now()
                prev.save()
            else:
                # Create a new vote
                instance.proposal = proposal
                instance.reviewer = request.user
                instance.date = datetime.now()
                instance.save()
            return HttpResponseRedirect(proposal.get_absolute_url())
        else:
            return HttpResponseBadRequest(request)
    else:
        return HttpResponseBadRequest(request)
proposal_vote = permission_required('galkwi.can_vote')(proposal_vote)

def proposal_cancel(request, proposal_id):
    if request.method == 'POST':
        context = RequestContext(request)
        proposal = Proposal.get_by_id(int(proposal_id))
        #proposal = get_object_or_404(Proposal, pk=proposal_id)
        # check if it's my proposal
        if proposal.editor != request.user:
            return HttpResponseBadRequest(request)
        if proposal.status != 'VOTING':
            return HttpResponseBadRequest(request)
        form = ProposalCancelForm(request.POST)
        if form.is_valid():
            proposal.cancel()
            return HttpResponseRedirect(proposal.get_absolute_url())
        else:
            return HttpResponseBadRequest(request)
    else:
        return HttpResponseBadRequest(request)
proposal_cancel = permission_required('galkwi.can_propose')(proposal_cancel)

def proposal_vote_no(request, proposal_id):
    context = RequestContext(request)
    proposal = get_object_or_404(Proposal, pk=proposal_id)
    return HttpResponseRedirect(proposal.get_absolute_url())
proposal_vote_no = permission_required('galkwi.can_vote')(proposal_vote_no)

def entry_detail(request, entry_id):
    context = RequestContext(request)
    entry = Entry.get_by_id(int(entry_id))
    #entry = get_object_or_404(Entry, pk=entry_id)
    context['entry'] = entry
    context['proposals_voting'] = Proposal.all().filter('old_entry =', entry).filter('status =', 'VOTING')
    context['proposals_new'] = Proposal.all().filter('new_entry =', entry)
    context['proposals_prev'] = Proposal.all().filter('old_entry =', entry).filter('status !=', 'VOTING')
                                                        
    return render_to_response('entry_detail.html', context)

