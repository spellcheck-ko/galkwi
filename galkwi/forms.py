# -*- coding: utf-8 -*-
from django import forms
from galkwi.models import *
from django.contrib.auth.models import Permission

class UserRegistrationForm(forms.Form):
    agree = forms.BooleanField(label=u'위 사항에 동의합니다')

class EntrySearchForm(forms.Form):
    word = forms.CharField(label=u'단어')

class ProposalVoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['vote', 'reason']

class ProposalCancelForm(forms.Form):
    pass

class ProposalEditAddForm(forms.ModelForm):
    class Meta:
        model = Proposal
        exclude = ['word_substrings',
                   'action', 'date', 'editor', 'status', 'new_entry',
                   'old_entry', 'status_date']

class ProposalEditRemoveForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['rationale']

class ProposalEditUpdateForm(forms.ModelForm):
    class Meta:
        model = Proposal
        exclude = ['word_substrings',
                   'action', 'date', 'editor', 'status', 'new_entry',
                   'old_entry', 'status_date']
