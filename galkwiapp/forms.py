# -*- coding: utf-8 -*-
from django import forms
from django.core import validators
from django.forms.utils import ValidationError
from galkwiapp.models import *
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext_lazy as _


class EntrySearchForm(forms.Form):
    word = forms.CharField(label='단어')


class SuggestionReviewForm(forms.Form):
    REVIEW_CHOICES = (
        ('HOLD', '보류'),
        ('APPROVE', '허용'),
        ('REJECT', '거절'),
    )

    review = forms.ChoiceField(choices=REVIEW_CHOICES,
                               widget=forms.RadioSelect())
    comment = forms.CharField(label='리뷰 이유', required=False)


class SuggestionCancelForm(forms.Form):
    pass


class SuggestionEditForm(forms.ModelForm):
    description = forms.CharField(label='설명', widget=forms.Textarea,
                                  required=False)
    comment = forms.CharField(label='제안 이유', required=False)

    class Meta:
        model = Word
        exclude = []


class SuggestionRemoveForm(forms.ModelForm):
    class Meta:
        model = Revision
        fields = ['review_comment']


class TermsAgreeForm(forms.Form):
    label1 = """
기여한 내용을 MPL/GPL/LGPL 라이선스로 배포하는데 동의합니다. 이 동의는 철회할 수 없습니다.
"""
    label2 = """
저작권 문제가 없는 데이터만 기여했습니다. 저작권 위반에 따른 책임은 기여자에게 있습니다.
"""
    agree1 = forms.BooleanField(label=label1)
    agree2 = forms.BooleanField(label=label2)


error_messages = {
    'required': _('This field is required.'),
    'invalid': _('Enter a valid value.'),
}
